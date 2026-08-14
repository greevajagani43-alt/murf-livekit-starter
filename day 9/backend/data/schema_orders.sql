-- Orders table for Ratan Kirana Store
-- Stores orders placed during voice calls with delivery scheduling

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_date DATE NOT NULL,
    delivery_slot TEXT DEFAULT 'morning',  -- morning, afternoon, evening
    items TEXT NOT NULL,  -- JSON array of {product_name, qty, price}
    total_amount REAL NOT NULL,
    status TEXT DEFAULT 'confirmed',  -- confirmed, out_for_delivery, delivered, cancelled
    payment_status TEXT DEFAULT 'pending',  -- pending, paid, cod
    payment_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_confirmed INTEGER DEFAULT 0,  -- 0=not called, 1=confirmed, 2=rescheduled, 3=no_answer
    delivery_confirmation_notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_delivery_date ON orders(delivery_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);