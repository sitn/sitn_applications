import subprocess
import os

from django.core.management.base import BaseCommand

from .utils import get_pg_dump_path

class Command(BaseCommand):
    """
    Prepares local db for testing
    """

    # Schemas that need to be restored before
    dependent_schemas = ['edition', 'main_prepub', 'mensuration']

    def __init__(self):
        super().__init__()
        self.pg_binaries_path = get_pg_dump_path()

    def handle(self, *args, **options):
        """
        Entry point of the script when called by Django manage.py
        """
        # DROP existing test DB
        db_name = os.environ['PGDATABASE']
        cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", 'postgres',
                '-c',
                f'DROP DATABASE IF EXISTS "test_{db_name}"'
            ]
        print(" ".join(cmd))
        subprocess.check_call(cmd)

        # rename local DB to test_
        cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", 'postgres',
                '-c',
                f'ALTER DATABASE "{db_name}" RENAME TO "test_{db_name}"'
            ]
        print(" ".join(cmd))
        subprocess.check_call(cmd)

        # dump the test_ DB
        dump_success = True
        try:
            cmd = [
                f"{self.pg_binaries_path}pg_dump.exe",
                "-d", f"test_{db_name}",
                "--create",
                "--format=C",
                f"--file=db/test_{db_name}.backup"
            ]
            print(" ".join(cmd))
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError as e:
            dump_success = False
            print(e.stderr)

        finally:
            # rename the test_ DB to its original name
            cmd = [
                    f'{self.pg_binaries_path}psql.exe',
                    "-d", 'postgres',
                    '-c',
                    f'ALTER DATABASE "test_{db_name}" RENAME TO "{db_name}"'
                ]
            print(" ".join(cmd))
            subprocess.check_call(cmd)

        # Restore the test_ DB
        if dump_success:
            cmd = [
                f"{self.pg_binaries_path}pg_restore.exe",
                "-d", "postgres",
                "--create",
                "--format=C",
                f"db/test_{db_name}.backup"
            ]
            print(" ".join(cmd))
            subprocess.check_call(cmd)
