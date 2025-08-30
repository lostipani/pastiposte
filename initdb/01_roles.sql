-- Create roles for the app (safe to re-run)
DO
$do$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_writer') THEN
    CREATE ROLE app_writer LOGIN PASSWORD 'writer_password_change_me';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_reader') THEN
    CREATE ROLE app_reader LOGIN PASSWORD 'reader_password_change_me';
  END IF;
END
$do$;

-- Allow both roles to connect and use the public schema
GRANT CONNECT ON DATABASE db_orders TO app_writer, app_reader;
GRANT USAGE ON SCHEMA public TO app_writer, app_reader;

-- Default privileges note:
-- These affect ONLY objects created *by the role that runs this file* (POSTGRES_USER) in this DB/schema.
-- Keep explicit GRANTs in 02_schema.sql for the tables you create there.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT, UPDATE, DELETE ON TABLES TO app_writer;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_writer;

