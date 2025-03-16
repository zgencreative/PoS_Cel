from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, literal
from datetime import datetime

db = SQLAlchemy()

# ENUM untuk status order dan pembayaran
ORDER_STATUS = ('pending', 'confirm', 'return', 'canceled')
PAYMENT_STATUS = ('unpaid', 'paid', 'failed', 'refunded')
PAYMENT_METHODS = ('credit_card', 'e-wallet', 'cash')

class Customer(db.Model):
    __tablename__ = "customer"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    poin = db.Column(db.Integer, nullable=False, server_default="0")
    member_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())

    # Relasi ke Order History
    orders = db.relationship("OrderHistory", back_populates="customer")

    # Relasi ke Invoice
    invoices = db.relationship("Invoice", back_populates="customer")

# Model Invoice
class Invoice(db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)  # Relasi ke customer
    total_price = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), nullable=False, server_default="unpaid")
    order_status = db.Column(db.Enum('pending', 'confirm', 'return', 'canceled', name="order_status_enum"), nullable=False, server_default=literal("pending"))
    issued_at = db.Column(db.TIMESTAMP, server_default=func.now())
    due_date = db.Column(db.TIMESTAMP, nullable=True)

    # Relasi ke Customer
    customer = db.relationship("Customer", back_populates="invoices")

    # Relasi ke Order History
    orders = db.relationship("OrderHistory", back_populates="invoice")

# Tabel Order History
class OrderHistory(db.Model):
    __tablename__ = "order_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"), nullable=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relasi ke Invoice
    invoice = db.relationship("Invoice", back_populates="orders")

    # Relasi ke Customer
    customer = db.relationship("Customer", back_populates="orders")

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url_path = db.Column(db.String(255), unique=True, nullable=False)  # Tambahkan ini
    image_url = db.Column(db.String(255))
    hover_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submenus = db.relationship('Submenu', backref='menu', cascade="all, delete")

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    image_url = db.Column(db.String(255))
    hover_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='category', cascade="all, delete")

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Submenu(db.Model):
    __tablename__ = 'submenus'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
