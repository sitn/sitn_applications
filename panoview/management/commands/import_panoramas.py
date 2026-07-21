"""
Populates the panoview database from mobile-mapping panorama capture folders
(gps-imu_*.txt + adjacent image folders), replacing the old workflow that wrote
a static STAC catalog to disk (see generate_panoramas_stac.py).

Input layout expected, same as before:

    <input-dir>/gps-imu_<SITE>_<VERSION>_LV95_LN02_PANO-RPH_PANO_DEG_ADJ.txt
    <input-dir>/<VERSION>/<image files...>

Each txt row is: <image name> <E> <N> <Z> <Omega/roll> <Phi/pitch> <Kappa/heading>
in LV95 (EPSG:2056) coordinates with LN02 heights, roll/pitch/heading in degrees.
These coordinates are stored as-is (SRID 2056); WGS84 conversion for STAC output
happens on the fly when serving the data (see panoview/stac.py).
"""
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError

from panoview.models import PanoramaItem, Sequence

TXT_PATTERN = "gps-imu_*_LV95_LN02_PANO-RPH_PANO_DEG_ADJ.txt"
TXT_NAME_RE = re.compile(r"^gps-imu_(?P<site>[^_]+)_(?P<version>[^_]+)_LV95_LN02_PANO-RPH_PANO_DEG_ADJ\.txt$")
IMAGE_NAME_RE = re.compile(r"^(?P<stem>.+)_(?P<date>\d{6})_(?P<index>\d+)$")

ITEM_UPDATE_FIELDS = [
    "sequence", "rank", "geom", "captured_at", "azimuth", "pitch", "roll",
    "image_name", "image_width", "image_height",
]


class Command(BaseCommand):
    help = "Import mobile-mapping panorama sequences (gps-imu_*.txt + images) into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-dir", type=Path, default=Path(settings.BASE_DIR) / "images_pano",
            help="Folder containing the gps-imu_*.txt files and their VXX image subfolders",
        )
        parser.add_argument("--pattern", default=TXT_PATTERN, help="Glob pattern used to find gps-imu txt files")
        parser.add_argument(
            "--all", action="store_true", dest="include_all",
            help="Include every txt row even when the image file is missing on disk "
                 "(by default only rows with an existing image are imported)",
        )
        parser.add_argument(
            "--purge", action="store_true",
            help="Delete pictures previously imported for a sequence that are no longer present in its txt file",
        )

    def handle(self, *args, **options):
        input_dir = options["input_dir"]
        if not input_dir.is_dir():
            raise CommandError(f"Input directory not found: {input_dir}")

        sequences = self._find_sequences(input_dir, options["pattern"])
        if not sequences:
            raise CommandError(f"No gps-imu txt file found in {input_dir} matching {options['pattern']!r}")

        default_date = datetime.now(timezone.utc)

        for seq in sequences:
            self._import_sequence(seq, options["include_all"], options["purge"], default_date)

    def _find_sequences(self, input_dir, pattern):
        sequences = []
        for txt_path in sorted(input_dir.glob(pattern)):
            m = TXT_NAME_RE.match(txt_path.name)
            if not m:
                self.stderr.write(f"Skipping {txt_path.name}: does not match expected naming convention")
                continue
            site, version = m.group("site"), m.group("version")
            images_dir = input_dir / version
            if not images_dir.is_dir():
                self.stderr.write(f"Skipping {txt_path.name}: adjacent folder {images_dir} not found")
                continue
            sequences.append({"txt_path": txt_path, "site": site, "version": version, "images_dir": images_dir})
        return sequences

    def _read_rows(self, txt_path):
        rows = []
        with open(txt_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                name, e, n, z, roll, pitch, heading = line.split()
                rows.append({
                    "name": name,
                    "easting": float(e),
                    "northing": float(n),
                    "height": float(z),
                    "roll": float(roll),
                    "pitch": float(pitch),
                    "heading": float(heading) % 360,
                })
        return rows

    def _image_size(self, path):
        if Image is None or not path.is_file():
            return None
        try:
            with Image.open(path) as img:
                return img.width, img.height
        except OSError:
            return None

    def _parse_capture_date(self, image_stem):
        m = IMAGE_NAME_RE.match(image_stem)
        if not m:
            return None
        try:
            return datetime.strptime(m.group("date"), "%y%m%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _import_sequence(self, seq, include_all, purge, default_date):
        seq_id = f"{seq['site']}_{seq['version']}"
        rows = self._read_rows(seq["txt_path"])
        if not include_all:
            rows = [r for r in rows if (seq["images_dir"] / r["name"]).is_file()]
        if not rows:
            self.stderr.write(f"Skipping sequence {seq_id}: no matching image found in {seq['images_dir']}")
            return

        sequence, _ = Sequence.objects.update_or_create(
            id=seq_id,
            defaults={
                "site": seq["site"],
                "version": seq["version"],
                "title": seq_id,
                "description": f"SITN mobile-mapping panorama sequence {seq['site']}/{seq['version']}",
            },
        )

        items = []
        for rank, row in enumerate(rows):
            item_id = Path(row["name"]).stem
            image_path = seq["images_dir"] / row["name"]
            capture_date = self._parse_capture_date(item_id) or default_date
            size = self._image_size(image_path)

            items.append(PanoramaItem(
                id=item_id,
                sequence=sequence,
                rank=rank,
                geom=Point(row["easting"], row["northing"], row["height"], srid=2056),
                captured_at=capture_date + timedelta(seconds=rank),
                azimuth=row["heading"],
                pitch=row["pitch"],
                roll=row["roll"],
                image_name=row["name"],
                image_width=size[0] if size else None,
                image_height=size[1] if size else None,
            ))

        PanoramaItem.objects.bulk_create(
            items,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=ITEM_UPDATE_FIELDS,
        )

        if purge:
            imported_ids = [item.id for item in items]
            deleted, _ = PanoramaItem.objects.filter(sequence=sequence).exclude(id__in=imported_ids).delete()
            if deleted:
                self.stdout.write(f"Sequence {seq_id}: purged {deleted} stale picture(s)")

        self.stdout.write(self.style.SUCCESS(f"Sequence {seq_id}: {len(items)} pictures imported"))
