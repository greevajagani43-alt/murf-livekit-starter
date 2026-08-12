-- ============================================
-- KIRANA STORE DATABASE
-- ============================================

CREATE DATABASE kirana_store;


-- ============================================
-- Connect to the database
-- PostgreSQL / psql:
-- \c kirana_store
-- ============================================


-- ============================================
-- PRODUCTS TABLE
-- ============================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    size VARCHAR(50) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    icon VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    qty INTEGER NOT NULL DEFAULT 0
);


-- ============================================
-- 50 TYPICAL KIRANA STORE PRODUCTS
-- ============================================

INSERT INTO products
    (name, size, price, icon, category, qty)
VALUES

-- =========================
-- ATT A & FLOUR
-- =========================

('Aashirvaad Atta', '5 kg', 295.00, 'Wheat', 'Atta & Flour', 18),
('Fortune Chakki Fresh Atta', '5 kg', 285.00, 'Wheat', 'Atta & Flour', 15),
('Besan', '500 g', 75.00, 'Wheat', 'Atta & Flour', 22),
('Maida', '500 g', 35.00, 'Wheat', 'Atta & Flour', 20),
('Sooji / Rava', '500 g', 40.00, 'Wheat', 'Atta & Flour', 25),

-- =========================
-- RICE & DAL
-- =========================

('India Gate Basmati Rice', '5 kg', 650.00, 'Wheat', 'Rice & Dal', 10),
('Daawat Basmati Rice', '5 kg', 620.00, 'Wheat', 'Rice & Dal', 12),
('Sona Masoori Rice', '5 kg', 350.00, 'Wheat', 'Rice & Dal', 14),
('Toor Dal', '1 kg', 180.00, 'Wheat', 'Rice & Dal', 25),
('Moong Dal', '1 kg', 145.00, 'Wheat', 'Rice & Dal', 20),
('Masoor Dal', '1 kg', 110.00, 'Wheat', 'Rice & Dal', 18),
('Chana Dal', '1 kg', 95.00, 'Wheat', 'Rice & Dal', 22),

-- =========================
-- OIL & GHEE
-- =========================

('Fortune Sunflower Oil', '1 L', 145.00, 'Droplets', 'Oil & Ghee', 30),
('Fortune Groundnut Oil', '1 L', 175.00, 'Droplets', 'Oil & Ghee', 24),
('Fortune Mustard Oil', '1 L', 160.00, 'Droplets', 'Oil & Ghee', 20),
('Amul Ghee', '1 L', 650.00, 'Milk', 'Oil & Ghee', 12),
('Patanjali Cow Ghee', '500 ml', 350.00, 'Milk', 'Oil & Ghee', 14),

-- =========================
-- SPICES
-- =========================

('MDH Chana Masala', '100 g', 45.00, 'Sprout', 'Spices', 25),
('MDH Garam Masala', '100 g', 55.00, 'Sprout', 'Spices', 28),
('Everest Turmeric Powder', '100 g', 35.00, 'Sprout', 'Spices', 30),
('Everest Red Chilli Powder', '100 g', 40.00, 'Flame', 'Spices', 32),
('Everest Coriander Powder', '100 g', 38.00, 'Sprout', 'Spices', 25),
('Tata Salt', '1 kg', 28.00, 'Waves', 'Spices', 40),

-- =========================
-- SUGAR & TEA
-- =========================

('Tata Tea Premium', '500 g', 280.00, 'Coffee', 'Tea & Coffee', 18),
('Red Label Tea', '500 g', 270.00, 'Coffee', 'Tea & Coffee', 16),
('Bru Instant Coffee', '100 g', 180.00, 'Coffee', 'Tea & Coffee', 14),
('Nescafe Classic', '100 g', 320.00, 'Coffee', 'Tea & Coffee', 12),
('Madhur Sugar', '1 kg', 48.00, 'Candy', 'Sugar & Sweeteners', 35),

-- =========================
-- BISCUITS & SNACKS
-- =========================

('Parle-G Biscuits', '800 g', 100.00, 'Cookie', 'Biscuits & Snacks', 30),
('Britannia Good Day', '200 g', 40.00, 'Cookie', 'Biscuits & Snacks', 28),
('Britannia Marie Gold', '250 g', 40.00, 'Cookie', 'Biscuits & Snacks', 30),
('Hide & Seek', '120 g', 40.00, 'Cookie', 'Biscuits & Snacks', 24),
('Lays Magic Masala', '52 g', 20.00, 'Cookie', 'Biscuits & Snacks', 45),
('Kurkure Masala Munch', '90 g', 20.00, 'Cookie', 'Biscuits & Snacks', 40),
('Haldiram Aloo Bhujia', '200 g', 70.00, 'Cookie', 'Biscuits & Snacks', 20),

-- =========================
-- DAIRY
-- =========================

('Amul Taaza Milk', '1 L', 65.00, 'Milk', 'Dairy', 25),
('Amul Butter', '100 g', 60.00, 'Milk', 'Dairy', 18),
('Amul Cheese Slices', '200 g', 140.00, 'Milk', 'Dairy', 15),
('Amul Curd', '400 g', 40.00, 'Milk', 'Dairy', 20),

-- =========================
-- BEVERAGES
-- =========================

('Coca-Cola', '750 ml', 45.00, 'GlassWater', 'Beverages', 25),
('Thums Up', '750 ml', 45.00, 'GlassWater', 'Beverages', 22),
('Sprite', '750 ml', 45.00, 'GlassWater', 'Beverages', 20),
('Real Mixed Fruit Juice', '1 L', 130.00, 'GlassWater', 'Beverages', 12),
('Frooti Mango Drink', '1 L', 70.00, 'GlassWater', 'Beverages', 18),

-- =========================
-- PERSONAL CARE
-- =========================

('Dove Bathing Soap', '100 g', 55.00, 'Bath', 'Personal Care', 30),
('Lux Soap', '100 g', 38.00, 'Bath', 'Personal Care', 35),
('Colgate Strong Teeth', '200 g', 110.00, 'Smile', 'Personal Care', 22),
('Clinic Plus Shampoo', '340 ml', 210.00, 'Droplets', 'Personal Care', 15),
('Parachute Coconut Oil', '200 ml', 95.00, 'Droplets', 'Personal Care', 20),

-- =========================
-- HOUSEHOLD
-- =========================

('Surf Excel Matic', '2 kg', 390.00, 'Sparkles', 'Household', 12),
('Vim Dishwash Bar', '200 g', 25.00, 'Sparkles', 'Household', 30),
('Harpic Toilet Cleaner', '500 ml', 110.00, 'SprayCan', 'Household', 18),
('Dettol Liquid', '250 ml', 95.00, 'ShieldCheck', 'Household', 16);