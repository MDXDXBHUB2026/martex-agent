-- MARTEX operator database (Postgres, see infra/docker-compose.yml) registered in Zetaris.
-- Run each statement separately in Zetaris SQL Workspace.
-- Replace <MARTEX_DB_PASSWORD> with the value from your local .env. Never commit the real value.
-- Note: DESCRIBE BY text must use only letters, digits, _ . - , (spaces are rejected).

CREATE DATASOURCE MARTEX_OPS DESCRIBE BY "MARTEX_operator_database" OPTIONS (jdbcdriver "org.postgresql.Driver", jdbcurl "jdbc:postgresql://martex-db:5432/martex", username "martex", fetchsize "1000", password "<MARTEX_DB_PASSWORD>");

REGISTER DATASOURCE TABLES FROM MARTEX_OPS;

-- Verify (expect: Mina Jabal Ali | AEJEA | 12.5 | 15.5)
SELECT port_name, unlocode, channel_depth_m, max_vessel_draft_m FROM MARTEX_OPS.port_index WHERE unlocode = 'AEJEA';
