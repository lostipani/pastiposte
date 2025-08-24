-- Runs automatically on first DB startup
CREATE ROLE app_writer LOGIN PASSWORD 'writer_password_change_me';
CREATE ROLE app_reader LOGIN PASSWORD 'reader_password_change_me';

GRANT CONNECT ON DATABASE db_orders TO app_writer, app_reader;
GRANT USAGE ON SCHEMA public TO app_writer, app_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT INSERT, UPDATE, DELETE ON TABLES TO app_writer;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO app_writer;

