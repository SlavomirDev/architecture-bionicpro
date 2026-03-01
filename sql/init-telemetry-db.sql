CREATE TABLE IF NOT EXISTS telemetry_data (
    telemetry_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    session_date DATE NOT NULL,
    usage_minutes INTEGER DEFAULT 0,
    movement_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    battery_level INTEGER DEFAULT 100,
    signal_quality DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

\copy telemetry_data FROM '/tmp/telemetry_data.csv' WITH (FORMAT CSV, HEADER true);

CREATE TABLE IF NOT EXISTS movement_logs (
    log_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    movement_type VARCHAR(50),
    success_rate DECIMAL(5,2),
    response_time_ms INTEGER,
    session_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

\copy movement_logs FROM '/tmp/movement_logs.csv' WITH (FORMAT CSV, HEADER true);