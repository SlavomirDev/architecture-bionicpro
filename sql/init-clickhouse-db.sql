CREATE DATABASE IF NOT EXISTS olap_db;

CREATE TABLE IF NOT EXISTS olap_db.customer_telemetry_mart
(
    mart_id UInt32,
    customer_id UInt32,
    username String,
    email String,
    customer_role String,
    report_date Date,

    total_usage_minutes UInt32,
    avg_daily_usage_minutes Float32,
    total_movements UInt32,
    avg_success_rate Float32,
    avg_response_time_ms Float32,
    total_errors UInt32,
    avg_battery_level Float32,
    avg_signal_quality Float32,

    registration_date Date,
    product_type String,
    total_orders UInt32,
    total_order_amount Decimal64(2),

    usage_efficiency_score Float32,
    movement_accuracy_score Float32,

    last_updated DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(report_date)
ORDER BY (customer_id, report_date, customer_role);

CREATE TABLE IF NOT EXISTS olap_db.daily_telemetry_summary
(
    summary_date Date,
    customer_role String,
    total_customers UInt32,
    total_usage_hours Float32,
    avg_success_rate Float32,
    avg_response_time_ms Float32,
    total_errors UInt32,
    avg_battery_level Float32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(summary_date)
ORDER BY (summary_date, customer_role);