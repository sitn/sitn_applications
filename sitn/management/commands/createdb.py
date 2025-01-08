import subprocess
import os

from django.core.management.base import BaseCommand

from .utils import get_pg_dump_path

class Command(BaseCommand):
    """
    Prepares local db for unmanaged models
    """

    def __init__(self):
        super().__init__()
        self.pg_binaries_path = get_pg_dump_path()

    def handle(self, *args, **options):
        """
        Entry point of the script when called by Django manage.py
        """
        db_name = os.environ['PGDATABASE']
        schema_name = os.environ['PGSCHEMA']
        if os.environ['PGHOST'] != 'localhost':
            is_sure = input(f"⚠⚠⚠ You'll delete {db_name} on {os.environ['PGHOST']} are you sure? Type yes or no:")
            if is_sure != 'yes':
                exit(0)
        cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", 'postgres',
                '-c',
                f'DROP DATABASE IF EXISTS {db_name}'
            ]
        print(" ".join(cmd))
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            # probably db is in use in pgAdmin so let's force quit sessions
            terminate_cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", 'postgres',
                '-c',
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{db_name}' and state='idle';"
            ]
            print("Closing existing connections")
            subprocess.check_call(terminate_cmd)
            print("Trying to drop exisiting DB")
            subprocess.check_call(cmd)

        cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", 'postgres',
                '-c',
                f'"CREATE DATABASE {db_name}"'
            ]
        print(" ".join(cmd))
        subprocess.check_call(" ".join(cmd))

        sql = f"""CREATE schema {schema_name};
            CREATE EXTENSION unaccent;
            CREATE EXTENSION postgis;
            CREATE EXTENSION pg_trgm;
            CREATE EXTENSION \\"uuid-ossp\\";
            CREATE EXTENSION hstore;
            """
        cmd = [
                f'{self.pg_binaries_path}psql.exe',
                "-d", db_name,
                '-c',
                f'"{sql}"'
        ]
        print(" ".join(cmd))
        subprocess.check_call(" ".join(cmd))
