-- init.sql
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_number VARCHAR(50) NOT NULL,
    service_id INTEGER REFERENCES services(id),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    estimated_wait_time FLOAT NOT NULL,
    queue_position INTEGER NOT NULL
);