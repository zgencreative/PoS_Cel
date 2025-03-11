import psycopg2

# Koneksi ke PostgreSQL
conn = psycopg2.connect(
    host="localhost",      # Ganti dengan host PostgreSQL Anda
    user="postgres",       # Ganti dengan username PostgreSQL Anda
    password="root",   # Ganti dengan password PostgreSQL Anda
    dbname="pos_celevo"    # Pastikan database sudah ada atau buat secara manual
)

cursor = conn.cursor()

# Membuat tabel menus
create_menus_table = """
CREATE TABLE IF NOT EXISTS menus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(255), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Membuat tabel categories
create_categories_table = """
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Membuat tabel products
create_products_table = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);
"""

# Membuat tabel submenus
create_submenus_table = """
CREATE TABLE IF NOT EXISTS submenus (
    id SERIAL PRIMARY KEY,
    menu_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
);
"""

# Query untuk membuat tabel order_history
create_order_table = """
CREATE TABLE IF NOT EXISTS order_history (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    invoice_id INT NULL REFERENCES invoice(id) ON DELETE SET NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Query untuk membuat tabel invoice
create_invoice_table = """
CREATE TABLE IF NOT EXISTS invoice (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    total_price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL DEFAULT 'unpaid',
    order_status VARCHAR(50) NOT NULL DEFAULT 'pending'
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NULL
);
"""

create_customer_table = """
CREATE TABLE IF NOT EXISTS customer (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(50) NOT NULL,
    member_id VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Eksekusi query
cursor.execute(create_customer_table)
# cursor.execute(create_order_table)
# cursor.execute(create_products_table)
# cursor.execute(create_submenus_table)

# Commit perubahan
conn.commit()

print("Tabel berhasil dibuat!")

# Tutup koneksi
cursor.close()
conn.close()
