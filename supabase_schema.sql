-- Supabase Schema for HAMMER-API IMEI Processing System
-- Run this SQL in your Supabase SQL Editor to create tables

-- Main orders table
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    order_id TEXT UNIQUE NOT NULL,
    service_name TEXT,
    service_id TEXT,
    imei TEXT NOT NULL,
    imei2 TEXT,
    credits DECIMAL(10, 4),
    status TEXT,
    carrier TEXT,
    simlock TEXT,
    model TEXT,
    fmi TEXT,
    order_date TIMESTAMPTZ,
    result_code TEXT,
    result_code_display TEXT,
    notes TEXT,
    raw_response TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_orders_imei ON orders(imei);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at DESC);

-- Import history table
CREATE TABLE IF NOT EXISTS import_history (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT,
    rows_imported INTEGER,
    rows_skipped INTEGER,
    import_date TIMESTAMPTZ DEFAULT NOW()
);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at on orders table
DROP TRIGGER IF EXISTS update_orders_updated_at ON orders;
CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Important for Supabase
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE import_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies - Allow all operations with service role key (used by backend)
-- This allows your backend to read/write, but not public users
CREATE POLICY "Enable all access for service role" ON orders
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable all access for service role on import_history" ON import_history
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Optional: Create a read-only view for public access (if needed)
-- CREATE VIEW public_orders AS
-- SELECT id, order_id, imei, status, carrier, model, order_date, created_at
-- FROM orders;

-- Comments for documentation
COMMENT ON TABLE orders IS 'IMEI orders from GSM Fusion API with results';
COMMENT ON COLUMN orders.order_id IS 'Unique order ID from GSM Fusion API';
COMMENT ON COLUMN orders.imei IS '15-digit IMEI number';
COMMENT ON COLUMN orders.imei2 IS 'Secondary IMEI for dual-SIM devices';
COMMENT ON COLUMN orders.status IS 'Order status: Pending/Completed/Rejected/In Process';
COMMENT ON COLUMN orders.result_code IS 'Raw CODE response with HTML tags (for record keeping)';
COMMENT ON COLUMN orders.result_code_display IS 'Cleaned CODE for display (HTML removed)';
COMMENT ON COLUMN orders.raw_response IS 'Full JSON response from API';

-- Grant necessary permissions (if using service role)
-- GRANT ALL ON orders TO service_role;
-- GRANT ALL ON import_history TO service_role;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;
