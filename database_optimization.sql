-- 🚀 CRITICAL DATABASE OPTIMIZATION
-- Run these SQL commands in your Supabase SQL editor
-- These indexes will improve query performance by 10-100x

-- 1. CRITICAL: DataPoint table indexes (most important)
-- This will dramatically speed up experiment queries and dashboard metrics

-- Index for metric-based queries (used in experiments)
CREATE INDEX IF NOT EXISTS idx_datapoints_metric_date 
ON data_points (metric_name, date DESC);

-- Index for date range queries (used in dashboard)
CREATE INDEX IF NOT EXISTS idx_datapoints_date_range 
ON data_points (date DESC) 
WHERE date >= CURRENT_DATE - INTERVAL '1 year';

-- Index for user-specific queries (if you add user_id later)
-- CREATE INDEX IF NOT EXISTS idx_datapoints_user_metric 
-- ON data_points (user_id, metric_name, date DESC);

-- Index for recent metrics queries (dashboard recent metrics)
CREATE INDEX IF NOT EXISTS idx_datapoints_recent 
ON data_points (date DESC) 
WHERE date >= CURRENT_DATE - INTERVAL '30 days';

-- Composite index for experiment stats calculation
CREATE INDEX IF NOT EXISTS idx_datapoints_experiment_stats 
ON data_points (metric_name, date, value) 
WHERE date >= CURRENT_DATE - INTERVAL '90 days';

-- 2. Graph table indexes
-- Index for non-temporary graphs (used in dashboard)
CREATE INDEX IF NOT EXISTS idx_graphs_not_temporary 
ON graphs (is_temporary) 
WHERE is_temporary = false;

-- Index for graph creation date (used in ordering)
CREATE INDEX IF NOT EXISTS idx_graphs_created_at 
ON graphs (created_at DESC);

-- 3. Experiment table indexes
-- Index for experiment ordering (used in experiments page)
CREATE INDEX IF NOT EXISTS idx_experiments_created_at 
ON experiments (created_at DESC);

-- Index for experiment status queries
CREATE INDEX IF NOT EXISTS idx_experiments_dates 
ON experiments (start_date, end_date) 
WHERE start_date IS NOT NULL;

-- 4. User table indexes (if you have user-specific data)
-- Index for user tokens (Oura, Fitbit)
-- CREATE INDEX IF NOT EXISTS idx_user_tokens 
-- ON "user" (oura_api_token, fitbit_access_token) 
-- WHERE oura_api_token IS NOT NULL OR fitbit_access_token IS NOT NULL;

-- 5. ANALYZE tables to update statistics
-- This helps PostgreSQL choose the best query plans
ANALYZE data_points;
ANALYZE graphs;
ANALYZE experiments;
ANALYZE "user";

-- 6. Check index usage (run this after creating indexes)
-- This will show you which indexes are being used
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- 7. Performance monitoring query
-- Run this to check query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM data_points 
WHERE metric_name = 'average_heart_rate' 
AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC 
LIMIT 100;

