import subprocess
import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    """
    Prepares local db for unmanaged models
    """
    def __init__(self):
        super().__init__()
        self.pg_binaries_path = ""
        self.backup_env = {
            "PGDATABASE": os.environ["PGDATABASE"],
            "PGUSER": os.environ["PGUSER"],
            "PGHOST": os.environ["PGHOST"],
            "PGPORT": os.environ["PGPORT"],
            "PGPASSWORD": os.environ["PGPASSWORD"],
            "PGSCHEMA": os.environ["PGSCHEMA"]
        }

    def is_pg_dump_on_path(self):
        """
        Checks if pg_dump in PATH, if not, asks for binaries path.
        """
        try:
            result = subprocess.check_call(["pg_dump", "--version"])
            print("pg_dump was successfully found, version:", result.stdout.decode().strip())
        except FileNotFoundError:
            print("👀 pg_dump not found in PATH!")
            input_path = Path(input("Provide pg_dump folder path:\n"))
            if not Path.is_dir(Path(input_path)):
                print(f"Error, {input_path} is not a folder")
                exit(1)
            self.pg_binaries_path = f"{input_path.as_posix()}/"

    def set_remote_pg_host(self):
        """
        Sets env so psql commands will be executed on remote
        """
        os.environ["PGDATABASE"] = os.environ["DEV_REMOTE_PGDATABASE"]
        os.environ["PGUSER"] = os.environ["DEV_REMOTE_PGUSER"]
        os.environ["PGHOST"] = os.environ["DEV_REMOTE_PGHOST"]
        os.environ["PGPORT"] = os.environ["DEV_REMOTE_PGPORT"]
        os.environ["PGPASSWORD"] = os.environ["DEV_REMOTE_PGPASSWORD"]
        os.environ["PGSCHEMA"] = os.environ["DEV_REMOTE_PGSCHEMA"]

    def reset_env(self):
        """
        resets env as it was before running script
        """
        for key in self.backup_env:
            os.environ[key] = self.backup_env[key]

    def dump_tables(self, unmanaged_tables):
        self.set_remote_pg_host()
        print(f'🔽 Dumping from {os.environ["PGHOST"]}...')
        pg_dump_args = "--format=C --clean"
        for schema in unmanaged_tables:
            table_list = f' -t {schema}.'.join(unmanaged_tables[schema])
            cmd = f"\"{self.pg_binaries_path}pg_dump.exe\" -t {schema}.{table_list} {pg_dump_args} --file=db/{schema}.backup"
            print(cmd)
            subprocess.check_call(cmd)
        self.reset_env()

    def restore_tables(self, unmanaged_tables):
        print(f'🔼 Restoring to {os.environ["PGHOST"]}...')
        for schema in unmanaged_tables:
            create_schema_cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-U", os.environ["PGUSER"],
                "-d", os.environ["PGDATABASE"],
                '-c',
                f"\"CREATE SCHEMA IF NOT EXISTS {schema};\""
            ]
            print(create_schema_cmd)
            subprocess.check_call(" ".join(create_schema_cmd))
            pg_restore_cmd = [
                f'"{self.pg_binaries_path}pg_restore.exe"',
                "--dbname",
                os.environ['PGDATABASE'],
                "--clean",
                "--format=C",
                f"db/{schema}.backup"
            ]
            print(pg_restore_cmd)
            subprocess.check_call(" ".join(pg_restore_cmd))

    def handle(self, *args, **options):
        """
        Entry point of the script when called by Django manage.py
        """
        self.is_pg_dump_on_path()
        unmanaged_tables = {}
        models = apps.get_models()
        for model in models:
            if not model._meta.managed:
                # typicall model._meta.db_table is 'schema_name"."table_name'
                schema_name, table_name = model._meta.db_table.replace('"','').split(".")
                if not schema_name in unmanaged_tables:
                    unmanaged_tables[schema_name] = []
                unmanaged_tables[schema_name].append(table_name)

        #self.dump_tables(unmanaged_tables)
        self.restore_tables(unmanaged_tables)
