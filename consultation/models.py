import os

from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import FileExtensionValidator
from django.urls import reverse
from django.utils import timezone
from django_prose_editor.fields import ProseEditorField

RICH_TEXT_EXTENSIONS = {
    "Bold": True,
    "Italic": True,
    "Underline": True,
    "Heading": {"levels": [2, 3, 4]},
    "BulletList": True,
    "OrderedList": True,
    "ListItem": True,
    "Blockquote": True,
    "HorizontalRule": True,
    "Link": {"enableTarget": True},
    "HardBreak": True,
    "History": True,
}

DOCUMENT_EXTENSIONS = ["pdf", "doc", "docx", "odt", "xls", "xlsx", "ods", "zip", "jpg", "jpeg", "png"]
DOCUMENT_ICONS = {
    "pdf": "bi-file-earmark-pdf",
    "doc": "bi-file-earmark-word", "docx": "bi-file-earmark-word", "odt": "bi-file-earmark-word",
    "xls": "bi-file-earmark-excel", "xlsx": "bi-file-earmark-excel", "ods": "bi-file-earmark-excel",
    "zip": "bi-file-earmark-zip",
    "jpg": "bi-file-earmark-image", "jpeg": "bi-file-earmark-image", "png": "bi-file-earmark-image",
}
PROPOSAL_FILE_EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "gif", "webp"]
BANNER_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]


def rich_text_field(verbose_name, **kwargs):
    """Rich text edited in the admin, sanitized on save to the allowed extensions."""
    return ProseEditorField(verbose_name, extensions=RICH_TEXT_EXTENSIONS, sanitize=True, blank=True, **kwargs)


class Consultation(models.Model):
    title = models.CharField("titre", max_length=200)
    slug = models.SlugField("identifiant URL", unique=True)
    about = rich_text_field("à propos")
    banner = models.FileField(
        "image bannière", upload_to="consultation/banners/", blank=True,
        validators=[FileExtensionValidator(BANNER_EXTENSIONS)])
    measures_html = models.TextField(
        "bloc HTML des mesures", blank=True,
        help_text="HTML brut (par exemple un iframe) affiché en haut de la page des mesures, "
                  "sur toute la largeur et sur 400px de hauteur au maximum.")
    measures_position = models.PositiveIntegerField(
        "ordre de la section Mesures", null=True, blank=True,
        help_text="Même numérotation que l'ordre des chapitres : la section Mesures s'affiche après les chapitres "
                  "dont l'ordre est inférieur ou égal à cette valeur. Vide = après tous les chapitres.")
    is_published = models.BooleanField("publiée", default=False)
    opens_on = models.DateField("ouverture de la participation", null=True, blank=True)
    closes_on = models.DateField("clôture de la participation", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultation\".\"consultation'
        ordering = ["-opens_on", "title"]
        verbose_name = "consultation"
        verbose_name_plural = "consultations"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("consultation:detail", args=[self.slug])

    def sections(self, chapters):
        """``chapters`` (ordered by position) with None where the measures section goes."""
        sections = list(chapters)
        index = len(sections)
        if self.measures_position is not None:
            index = next((i for i, c in enumerate(sections) if c.position > self.measures_position), index)
        sections.insert(index, None)
        return sections

    @property
    def is_open(self):
        """Whether feedback and questionnaire responses are accepted today."""
        today = timezone.localdate()
        return (self.opens_on is None or self.opens_on <= today) and (self.closes_on is None or today <= self.closes_on)


class Chapter(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField("titre", max_length=200)
    position = models.PositiveIntegerField("ordre", default=0)
    intro = rich_text_field("introduction")

    class Meta:
        db_table = 'consultation\".\"chapter'
        ordering = ["position", "id"]
        verbose_name = "chapitre"
        verbose_name_plural = "chapitres"

    def __str__(self):
        return f"{self.consultation} – {self.title}"


class ChapterDocument(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField("titre", max_length=200)
    file = models.FileField(
        "fichier", upload_to="consultation/documents/",
        validators=[FileExtensionValidator(DOCUMENT_EXTENSIONS)])
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"chapter_document'
        ordering = ["position", "id"]
        verbose_name = "document"
        verbose_name_plural = "documents"

    def __str__(self):
        return self.title

    @property
    def extension(self):
        return os.path.splitext(self.file.name)[1].lstrip(".").upper()

    @property
    def icon(self):
        """Bootstrap Icons class matching the file type."""
        return DOCUMENT_ICONS.get(self.extension.lower(), "bi-file-earmark")


class Questionnaire(models.Model):
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name="questionnaire",
                                   verbose_name="chapitre")
    title = models.CharField("titre", max_length=200)
    description = rich_text_field("description")

    class Meta:
        db_table = 'consultation\".\"questionnaire'
        verbose_name = "questionnaire"
        verbose_name_plural = "questionnaires"

    def __str__(self):
        return self.title


class Question(models.Model):
    """Question types mirror Decidim's questionnaires (file uploads excepted)."""
    SHORT_RESPONSE = "short_response"
    LONG_RESPONSE = "long_response"
    SINGLE_OPTION = "single_option"
    MULTIPLE_OPTION = "multiple_option"
    SORTING = "sorting"
    MATRIX_SINGLE = "matrix_single"
    MATRIX_MULTIPLE = "matrix_multiple"
    TITLE_AND_DESCRIPTION = "title_and_description"
    SEPARATOR = "separator"
    TYPES = [
        (SHORT_RESPONSE, "Réponse courte"),
        (LONG_RESPONSE, "Réponse longue"),
        (SINGLE_OPTION, "Choix unique"),
        (MULTIPLE_OPTION, "Choix multiple"),
        (SORTING, "Classement"),
        (MATRIX_SINGLE, "Matrice (choix unique par ligne)"),
        (MATRIX_MULTIPLE, "Matrice (choix multiple par ligne)"),
        (TITLE_AND_DESCRIPTION, "Titre et description"),
        (SEPARATOR, "Séparateur"),
    ]
    OPTION_TYPES = {SINGLE_OPTION, MULTIPLE_OPTION, SORTING, MATRIX_SINGLE, MATRIX_MULTIPLE}
    MATRIX_TYPES = {MATRIX_SINGLE, MATRIX_MULTIPLE}
    DISPLAY_ONLY_TYPES = {TITLE_AND_DESCRIPTION, SEPARATOR}

    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name="questions")
    position = models.PositiveIntegerField("ordre", default=0)
    question_type = models.CharField("type", max_length=30, choices=TYPES, default=SHORT_RESPONSE)
    body = models.CharField("question", max_length=500, blank=True)
    description = rich_text_field("description")
    mandatory = models.BooleanField("obligatoire", default=False)
    max_choices = models.PositiveSmallIntegerField(
        "nombre maximum de choix", null=True, blank=True,
        help_text="Choix multiple et matrice à choix multiple ; vide = illimité.")
    max_characters = models.PositiveIntegerField(
        "nombre maximum de caractères", null=True, blank=True,
        help_text="Réponses courtes et longues ; vide = illimité.")

    class Meta:
        db_table = 'consultation\".\"question'
        ordering = ["position", "id"]
        verbose_name = "question"
        verbose_name_plural = "questions"

    def __str__(self):
        return self.body or self.get_question_type_display()

    @property
    def is_display_only(self):
        return self.question_type in self.DISPLAY_ONLY_TYPES

    @property
    def has_options(self):
        return self.question_type in self.OPTION_TYPES

    @property
    def is_matrix(self):
        return self.question_type in self.MATRIX_TYPES


class ResponseOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    body = models.CharField("option", max_length=300)
    free_text = models.BooleanField("texte libre", default=False,
                                    help_text="Ajoute un champ « précisez » lorsque cette option est choisie.")
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"response_option'
        ordering = ["position", "id"]
        verbose_name = "option de réponse"
        verbose_name_plural = "options de réponse"

    def __str__(self):
        return self.body


class MatrixRow(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="matrix_rows")
    body = models.CharField("ligne", max_length=300)
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"matrix_row'
        ordering = ["position", "id"]
        verbose_name = "ligne de matrice"
        verbose_name_plural = "lignes de matrice"

    def __str__(self):
        return self.body


class QuestionnaireResponse(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="consultation_responses", verbose_name="participant")
    created_at = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        db_table = 'consultation\".\"questionnaire_response'
        ordering = ["-created_at"]
        verbose_name = "réponse au questionnaire"
        verbose_name_plural = "réponses aux questionnaires"
        constraints = [
            models.UniqueConstraint(fields=["questionnaire", "user"], name="consultation_one_response_per_user"),
        ]

    def __str__(self):
        return f"{self.questionnaire} – {self.user}"


class Answer(models.Model):
    """
    One answer per question. ``choices`` holds the selected options as dicts:
    ``{"option": id, "text": str}`` (choice), plus ``"position"`` (sorting) or ``"row"`` (matrix).
    """
    response = models.ForeignKey(QuestionnaireResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    text = models.TextField(blank=True)
    choices = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'consultation\".\"answer'
        ordering = ["question__position", "question_id"]
        verbose_name = "réponse"
        verbose_name_plural = "réponses"

    def __str__(self):
        return f"{self.question}: {self.display()}"

    def display(self):
        """Readable answer, used by the admin and CSV export."""
        if not self.question.has_options:
            return self.text
        options = {o.id: o.body for o in self.question.options.all()}
        rows = {r.id: r.body for r in self.question.matrix_rows.all()}
        parts = []
        for choice in sorted(self.choices, key=lambda c: (c.get("row") or 0, c.get("position") or 0)):
            label = options.get(choice.get("option"), "?")
            if choice.get("text"):
                label = f"{label} ({choice['text']})"
            if "row" in choice:
                label = f"{rows.get(choice['row'], '?')} : {label}"
            elif "position" in choice:
                label = f"{choice['position']}. {label}"
            parts.append(label)
        return " ; ".join(parts)


class TaxonomyGroup(models.Model):
    name = models.CharField("nom", max_length=100, unique=True)
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"taxonomy_group'
        ordering = ["position", "name"]
        verbose_name = "groupe de taxonomies"
        verbose_name_plural = "groupes de taxonomies"

    def __str__(self):
        return self.name


class Taxonomy(models.Model):
    group = models.ForeignKey(TaxonomyGroup, on_delete=models.CASCADE, related_name="taxonomies",
                              verbose_name="groupe")
    name = models.CharField("nom", max_length=100)
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"taxonomy'
        ordering = ["group__position", "group__name", "position", "name"]
        verbose_name = "taxonomie"
        verbose_name_plural = "taxonomies"
        constraints = [
            models.UniqueConstraint(fields=["group", "name"], name="consultation_unique_taxonomy_per_group"),
        ]

    def __str__(self):
        return f"{self.group} : {self.name}"


class Proposal(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="proposals")
    reference = models.CharField("référence", max_length=30, blank=True, help_text="Ex. : C1, I15")
    title = models.CharField("titre", max_length=300)
    summary = rich_text_field("résumé")
    file = models.FileField(
        "document (PDF ou image)", upload_to="consultation/proposals/", blank=True,
        validators=[FileExtensionValidator(PROPOSAL_FILE_EXTENSIONS)])
    geom = models.GeometryField("géométrie", srid=settings.DEFAULT_SRID, null=True, blank=True)
    taxonomies = models.ManyToManyField(Taxonomy, blank=True, related_name="proposals", verbose_name="taxonomies",
                                        db_table='consultation\".\"proposal_taxonomies')
    position = models.PositiveIntegerField("ordre", default=0)

    class Meta:
        db_table = 'consultation\".\"proposal'
        ordering = ["position", "reference", "id"]
        verbose_name = "mesure"
        verbose_name_plural = "mesures"

    def __str__(self):
        return f"{self.reference} · {self.title}" if self.reference else self.title

    def get_absolute_url(self):
        return reverse("consultation:proposal", args=[self.consultation.slug, self.pk])

    @property
    def file_is_pdf(self):
        return bool(self.file) and self.file.name.lower().endswith(".pdf")


class Feedback(models.Model):
    """Private opinion on a proposal: visible to its author only (and to staff in the admin)."""
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name="consultation_feedbacks", verbose_name="participant")
    body = models.TextField("avis")
    location = models.PointField("localisation", srid=settings.DEFAULT_SRID, null=True, blank=True)
    created_at = models.DateTimeField("date", auto_now_add=True)

    class Meta:
        db_table = 'consultation\".\"feedback'
        ordering = ["-created_at"]
        verbose_name = "avis"
        verbose_name_plural = "avis"

    def __str__(self):
        return f"{self.proposal} – {self.user}"
