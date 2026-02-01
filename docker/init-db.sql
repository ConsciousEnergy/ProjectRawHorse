-- PostgreSQL initialization script for Project RawHorse
-- This script runs on first database creation

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For faster indexing

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rawhorse TO prh;

-- Create schema (tables will be created by SQLAlchemy)
-- This ensures proper ownership

-- Create read-only user for analytics (optional)
-- CREATE USER prh_readonly WITH PASSWORD 'readonly_password';
-- GRANT CONNECT ON DATABASE rawhorse TO prh_readonly;
-- GRANT USAGE ON SCHEMA public TO prh_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO prh_readonly;

-- Performance tuning for container environment
-- These are applied at session level; for persistence, modify postgresql.conf
-- ALTER SYSTEM SET shared_buffers = '256MB';
-- ALTER SYSTEM SET work_mem = '16MB';
-- ALTER SYSTEM SET maintenance_work_mem = '128MB';
-- ALTER SYSTEM SET effective_cache_size = '512MB';

-- Logging configuration
-- ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log slow queries
-- ALTER SYSTEM SET log_statement = 'ddl';  -- Log DDL statements
