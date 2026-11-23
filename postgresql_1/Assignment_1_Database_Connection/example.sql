-- VERIFIED SELECT; existing database already provisioned. No CREATE DATABASE executed.
BEGIN READ ONLY;
SELECT 1 AS connection_check, current_database() AS database_name, current_schema() AS schema_name, current_setting('server_version_num') AS server_version_num;
ROLLBACK;
