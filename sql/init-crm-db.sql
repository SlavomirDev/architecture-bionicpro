CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    registration_date DATE DEFAULT CURRENT_DATE,
    role VARCHAR(50) DEFAULT 'user'
);

\copy customers FROM '/tmp/crm_customers.csv' WITH (FORMAT CSV, HEADER true);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE DEFAULT CURRENT_DATE,
    product_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    total_amount DECIMAL(10,2)
);

\copy orders FROM '/tmp/crm_orders.csv' WITH (FORMAT CSV, HEADER true);