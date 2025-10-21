-- Supabase Database Schema for Fitbit Integration
-- Run these SQL commands in your Supabase SQL editor

-- 1. Create user_tokens table for storing OAuth tokens
CREATE TABLE IF NOT EXISTS user_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider TEXT NOT NULL, -- 'fitbit', 'oura', etc.
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP WITH TIME ZONE,
    provider_user_id TEXT, -- Fitbit user ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one token per provider per user
    UNIQUE(user_id, provider)
);

-- 2. Create metrics table for storing health data
CREATE TABLE IF NOT EXISTS metrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- 'fitbit_steps', 'fitbit_heart_rate', etc.
    value DECIMAL NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Index for efficient queries
    INDEX idx_metrics_user_type_timestamp (user_id, type, timestamp)
);

-- 3. Create RLS (Row Level Security) policies
ALTER TABLE user_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own tokens
CREATE POLICY "Users can access own tokens" ON user_tokens
    FOR ALL USING (auth.uid() = user_id);

-- Policy: Users can only access their own metrics
CREATE POLICY "Users can access own metrics" ON metrics
    FOR ALL USING (auth.uid() = user_id);

-- 4. Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at column
CREATE TRIGGER update_user_tokens_updated_at 
    BEFORE UPDATE ON user_tokens 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_tokens_user_provider ON user_tokens(user_id, provider);
CREATE INDEX IF NOT EXISTS idx_metrics_user_type ON metrics(user_id, type);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);

-- 6. Create a view for easy metric queries
CREATE OR REPLACE VIEW user_metrics_summary AS
SELECT 
    user_id,
    type,
    COUNT(*) as record_count,
    MIN(timestamp) as first_record,
    MAX(timestamp) as last_record,
    AVG(value) as average_value,
    MAX(value) as max_value,
    MIN(value) as min_value
FROM metrics
GROUP BY user_id, type;

-- 7. Grant permissions
GRANT ALL ON user_tokens TO authenticated;
GRANT ALL ON metrics TO authenticated;
GRANT SELECT ON user_metrics_summary TO authenticated;

-- 8. Insert sample data (optional - for testing)
-- INSERT INTO metrics (user_id, type, value, timestamp) VALUES
-- ('your-user-id-here', 'fitbit_steps', 8500, NOW() - INTERVAL '1 day'),
-- ('your-user-id-here', 'fitbit_steps', 9200, NOW());

