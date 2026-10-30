# AGENTS.md

## Database

An app's tables are always created in a PostgreSQL schema of its own, never in `public`.

- Every model declares its schema in `Meta.db_table`, including `ManyToManyField` join tables (`db_table=` on the field):

  ```python
  class Meta:
      db_table = 'my_app\".\"my_table'
  ```

- The initial migration creates the schema before the tables, without failing if it already exists:

  ```python
  operations = [
      migrations.RunSQL('CREATE SCHEMA IF NOT EXISTS my_app;', reverse_sql=migrations.RunSQL.noop),
      ...
  ]
  ```

- Do not rely on the connection's `search_path` (`PGSCHEMA,ppe,public`): without an explicit schema, tables land in the first existing schema, which varies from one database to another.
