import subprocess
import os

from django.core.management.base import BaseCommand
from django.apps import apps

from .utils import get_pg_dump_path

class Command(BaseCommand):
    """
    Prepares local db for unmanaged models
    """

    # Schemas that need to be restored before
    dependent_schemas = ['edition', 'main_prepub', 'general', 'mensuration']

    def __init__(self):
        super().__init__()
        self.pg_binaries_path = get_pg_dump_path()

    def get_remote_pg_env(self):
        """
        Sets env so psql commands will be executed on remote
        """
        temp_env = os.environ.copy()
        temp_env["PGDATABASE"] = os.environ["DEV_REMOTE_PGDATABASE"]
        temp_env["PGUSER"] = os.environ["DEV_REMOTE_PGUSER"]
        temp_env["PGHOST"] = os.environ["DEV_REMOTE_PGHOST"]
        temp_env["PGPORT"] = os.environ["DEV_REMOTE_PGPORT"]
        temp_env["PGPASSWORD"] = os.environ["DEV_REMOTE_PGPASSWORD"]
        return temp_env

    def dump_schemas(self, schemas):
        print(f'🔽 Dumping from {os.environ["DEV_REMOTE_PGHOST"]}...')
        for schema in schemas:
            cmd = [
                f"{self.pg_binaries_path}pg_dump.exe",
                "--schema-only",
                "--no-privileges",
                "--no-owner",
                "-n", schema,
                "--format=c",
                f"--file=db/{schema}.backup"
            ]
            print(cmd)
            temp_env = self.get_remote_pg_env()
            subprocess.check_call(cmd, env=temp_env)

    def dump_tables(self, unmanaged_tables):
        print(f'🔽 Dumping from {os.environ["DEV_REMOTE_PGHOST"]}...')
        for schema in unmanaged_tables:
            table_list = f'|'.join(unmanaged_tables[schema])
            cmd = [
                f"{self.pg_binaries_path}pg_dump.exe",
                "-t", f"{schema}.({table_list})",
                "--no-privileges",
                "--no-owner",
                "--format=c",
                f"--file=db/{schema}.backup"
            ]
            print(cmd)
            temp_env = self.get_remote_pg_env()
            subprocess.check_call(cmd, env=temp_env)

    def restore_schemas(self, unmanaged_tables):
        temp_env = os.environ.copy()
        temp_env['PGOPTIONS'] = '--client-min-messages=warning'
        print(f'🔼 Restoring to {os.environ["PGHOST"]}...')
        for schema in unmanaged_tables:
            create_schema_cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", os.environ["PGDATABASE"],
                "-c",
                f"\"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};\""
            ]
            print(create_schema_cmd)
            subprocess.check_call(" ".join(create_schema_cmd), env=temp_env)

            pg_restore_cmd = [
                f'"{self.pg_binaries_path}pg_restore.exe"',
                "--dbname",
                os.environ['PGDATABASE'],
                "--no-owner",
                "--clean",
                "--if-exists",
                "--format=c",
                f"db/{schema}.backup"
            ]
            print(pg_restore_cmd)
            subprocess.check_call(" ".join(pg_restore_cmd))

    def restore_tables(self, unmanaged_tables):
        print(f'🔼 Restoring to {os.environ["PGHOST"]}...')
        for schema in unmanaged_tables:
            exists = "--if-exists --clean"
            if schema in self.dependent_schemas:
                exists = "--data-only"
            pg_restore_cmd = [
                f'"{self.pg_binaries_path}pg_restore.exe"',
                "--dbname",
                os.environ['PGDATABASE'],
                "--no-owner",
                exists,
                "--format=c",
                f"db/{schema}.backup"
            ]
            print(pg_restore_cmd)
            subprocess.check_call(" ".join(pg_restore_cmd))

    def handle(self, *args, **options):
        """
        Entry point of the script when called by Django manage.py
        """
        unmanaged_tables = {}
        models = apps.get_models()
        for model in models:
            if not model._meta.managed:
                # typicall model._meta.db_table is 'schema_name"."table_name'
                schema_name, table_name = model._meta.db_table.replace('"','').split(".")
                if not schema_name in unmanaged_tables:
                    unmanaged_tables[schema_name] = []
                unmanaged_tables[schema_name].append(table_name)
        self.dump_schemas(self.dependent_schemas)
        self.restore_schemas(self.dependent_schemas)
        self.dump_schemas(unmanaged_tables)
        self.restore_schemas(unmanaged_tables)
        self.dump_tables(unmanaged_tables)
        self.restore_tables(unmanaged_tables)
