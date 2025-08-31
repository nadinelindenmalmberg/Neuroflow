-- Create experiments table in Supabase
CREATE TABLE IF NOT EXISTS experiments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    period VARCHAR(50) NOT NULL,
    start_date DATE,
    end_date DATE,
    driver VARCHAR(200),
    metric_of_interest VARCHAR(100) NOT NULL,
    benchmark VARCHAR(100) NOT NULL,
    icon VARCHAR(50),
    icon_color VARCHAR(7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add comment to table
COMMENT ON TABLE experiments IS 'Stores user experiments with their configuration and metadata'; 