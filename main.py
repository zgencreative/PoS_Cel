from flask import Flask, render_template, url_for, redirect, request, jsonify
from models import db, Menu, Submenu, Category, Product, OrderHistory, Invoice, Customer
import datetime

app = Flask(__name__)

# Ganti dengan informasi PostgreSQL-mu
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/pos_celevo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Fungsi untuk mendapatkan data menu beserta submenunya
def get_menus():
    menus = Menu.query.all()  # Ambil semua data dari tabel menus
    result = []
    current_path = request.path  # Ambil URL halaman saat ini

    for menu in menus:
        is_active = menu.url_path == current_path  # Cocokkan dengan URL
        result.append({
            "id": menu.id,
            "name": menu.name,
            "image_url": menu.image_url,
            "hover_image_url": menu.hover_image_url,
            "url_path": menu.url_path,  # Pastikan dikirim ke frontend
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "active": is_active,  # Tambahkan status aktif
            "submenus": [
                {
                    "id": submenu.id,
                    "name": submenu.name,
                    "image_url": submenu.image_url,
                    "created_at": submenu.created_at,
                    "updated_at": submenu.updated_at
                }
                for submenu in menu.submenus  # Mengambil submenus yang terkait dengan menu ini
            ]
        })

    return result

def get_data():
    # Ambil semua kategori dari database
    categories = Category.query.all()

    # Hitung total produk dari semua kategori
    total_all_products = Product.query.count()

    # Format data kategori, termasuk kategori "All"
    category_list = [
        {
            "id": 0,  # ID untuk kategori "All"
            "name": "All",
            "image_url": "logo-all-cat.svg",  # Default image untuk "All"
            "hover_image_url": "logo-all-cat-pink.svg",
            "total_products": total_all_products,
            "created_at": None,
            "updated_at": None,
        }
    ]

    # Dictionary untuk menyimpan produk per kategori
    product_dict = {0: []}  # Produk untuk kategori "All"

    for category in categories:
        category_list.append({
            "id": category.id,
            "name": category.name,
            "image_url": category.image_url,
            "hover_image_url": category.hover_image_url,
            "total_products": len(category.products),
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        })

        # Simpan produk berdasarkan kategori
        product_dict[category.id] = []
        for product in category.products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "image_url": product.image_url,
                "price": product.price,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            }
            product_dict[category.id].append(product_data)
            product_dict[0].append(product_data)  # Tambahkan ke kategori "All"

    return {"categories": category_list, "products": product_dict}

# API untuk menampilkan daftar Order History dengan filter tanggal & waktu
@app.route("/orders/<int:invoice_id>", methods=["GET"])
def get_orders(invoice_id):
    # Menjalankan query untuk mengambil data berdasarkan invoice_id
    orders = db.session.query(
        OrderHistory.id.label("order_id"),
        OrderHistory.created_at.label("order_date"),
        OrderHistory.customer_id.label("customer_id"),
        db.func.sum(OrderHistory.price * OrderHistory.quantity).label("total_payment"),
        Invoice.payment_status.label("payment_status"),
        Invoice.id.label("invoice_id"),
        OrderHistory.product_id.label("product_id"),
        db.func.sum(OrderHistory.quantity).label("total_quantity"),
        Product.name.label("product_name"),
        Product.price.label("product_price")
    ).join(Invoice, OrderHistory.invoice_id == Invoice.id, isouter=True)\
     .join(Product, OrderHistory.product_id == Product.id, isouter=True)\
     .join(Customer, OrderHistory.customer_id == Customer.id, isouter=True)\
     .filter(OrderHistory.invoice_id == invoice_id)\
     .group_by(OrderHistory.id, Invoice.id, OrderHistory.product_id, Product.name, Customer.name, Product.price).all()

    # Memastikan query menghasilkan hasil
    if not orders:
        return jsonify({"error": "Orders not found for this invoice"}), 404

    # Memproses hasil query menjadi response yang diinginkan
    result = []
    for order in orders:
        result.append({
            "order_id": order.order_id,
            "order_date": order.order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_payment": float(order.total_payment) if order.total_payment else 0.00,
            "invoice_id": order.invoice_id if order.invoice_id else None,
            "product_id": order.product_id,
            "product_name": order.product_name,
            "product_price": float(order.product_price),  # Harga produk
            "total_quantity": order.total_quantity
        })

    return jsonify(result)

def get_invoice(start_date=None, end_date=None, start_time=None, end_time=None):
    # Mendapatkan tanggal sekarang dan mengatur default start_date dan end_date
    date_now = datetime.datetime.now()
    formatted_date = date_now.strftime("%Y-%m-%d")
    # Jika start_date atau end_date None, atur ke default formatted_date
    start_date = start_date or formatted_date
    end_date = end_date or formatted_date

    # Jika start_time atau end_time None, atur ke default 00:00:00 dan 23:59:59
    start_time = start_time or "00:00:00"
    end_time = end_time or "23:59:59"

    # Konversi string ke format datetime
    start_datetime = datetime.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")

    # Ambil invoice berdasarkan rentang tanggal
    invoices = Invoice.query.filter(
        Invoice.issued_at.between(start_datetime, end_datetime)
    ).all()

    if not invoices:
        return jsonify({"error": "Invoice not found"}), 404

    data = {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "result": []
    }

    # Loop untuk mengambil detail setiap invoice dan nama customer
    for invoice in invoices:
        # Ambil nama customer berdasarkan customer_id dari invoice
        customer = Customer.query.filter(Customer.id == invoice.customer_id).first()

        if not customer:
            return jsonify({"error": f"Customer not found for invoice {invoice.id}"}), 404

        # Buat detail invoice
        invoice_detail = {
            "invoice_id": invoice.id,
            "customer_id": invoice.customer_id,
            "customer_name": customer.name,  # Menambahkan nama customer
            "total_price": '{:,.0f}'.format(float(invoice.total_price)).replace(',', '.'),
            "payment_method": invoice.payment_method,
            "payment_status": invoice.payment_status,
            "order_status": invoice.order_status,
            "issued_at": invoice.issued_at.strftime("%d/%m/%Y - %H.%M"),
            "due_date": invoice.due_date.strftime("%d/%m/%Y - %H.%M") if invoice.due_date else None,
        }

        data['result'].append(invoice_detail)

    return data

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        data = request.json

        # Insert Customer
        new_customer = Customer(
            name=data['customer_name'],
            contact = data.get('customer_contact', ""),
            member_id=data.get('member_id', "")  # Opsional
        )
        db.session.add(new_customer)
        db.session.flush()  # Dapatkan customer_id sebelum commit

        # Insert Invoice
        new_invoice = Invoice(
            customer_id=new_customer.id,
            total_price=data['total_price'],
            payment_method=data['payment_method'],
            payment_status=data['payment_status'],
            order_status='pending',
            due_date=data.get('due_date', None)
        )
        db.session.add(new_invoice)
        db.session.flush()  # Dapatkan invoice_id sebelum commit

        # Insert Order History (Multiple Orders)
        orders = []
        for item in data['orders']:
            orders.append(OrderHistory(
                customer_id=new_customer.id,
                invoice_id=new_invoice.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price=item['price']
            ))
        db.session.add_all(orders)

        db.session.commit()

        return jsonify({"message": "Order berhasil dibuat!", "invoice_id": new_invoice.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@app.route("/", methods=["GET"])
def index():
    menu = get_menus()
    data = get_data()
    return render_template("index.html", menu=menu, data=data)

@app.route("/stock-management", methods=['GET'])
def stock():
    menu = get_menus()
    return render_template("stock.html", menu=menu)

@app.route("/order-history", methods=['GET'])
def order():
    menu = get_menus()
    history = get_invoice()
    return render_template("order.html", menu=menu, history=history)


if __name__ == '__main__':
    app.run(port=9000, debug=True)