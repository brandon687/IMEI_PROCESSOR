-- Add columns for parsed IMEI data (if they don't exist)
-- Run this in Supabase SQL Editor to add missing columns

-- Add serial_number column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS serial_number TEXT;

-- Add meid column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS meid TEXT;

-- Add gsma_status column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS gsma_status TEXT;

-- Add purchase_date column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS purchase_date TEXT;

-- Add applecare column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS applecare TEXT;

-- Add tether_policy column
ALTER TABLE orders ADD COLUMN IF NOT EXISTS tether_policy TEXT;

-- Add comments
COMMENT ON COLUMN orders.serial_number IS 'Device serial number (parsed from CODE)';
COMMENT ON COLUMN orders.meid IS 'MEID number (parsed from CODE)';
COMMENT ON COLUMN orders.gsma_status IS 'GSMA blacklist status (parsed from CODE)';
COMMENT ON COLUMN orders.purchase_date IS 'Estimated purchase date (parsed from CODE)';
COMMENT ON COLUMN orders.applecare IS 'AppleCare eligibility (parsed from CODE)';
COMMENT ON COLUMN orders.tether_policy IS 'Next tether policy ID (parsed from CODE)';
