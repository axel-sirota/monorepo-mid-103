-- Runs once when Postgres initialises the data volume.
-- Creates one database per consuming service so they don't share schemas.

CREATE DATABASE users_db;
CREATE DATABASE notifications_db;
CREATE DATABASE mlflow_db;

-- Grant the bootstrap user full access to each.
GRANT ALL PRIVILEGES ON DATABASE users_db TO monorepo;
GRANT ALL PRIVILEGES ON DATABASE notifications_db TO monorepo;
GRANT ALL PRIVILEGES ON DATABASE mlflow_db TO monorepo;
