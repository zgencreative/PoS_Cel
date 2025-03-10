from flask import Flask, render_template, url_for, redirect, request
from models import db, Menu, Submenu, Category, Product

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



# def get_cat():
#     categories = Category.query.all()

#     # Hitung total produk dari semua kategori
#     total_all_products = Product.query.count()

#     result = [
#         {
#             "id": 0,  # ID 0 atau None untuk kategori "All"
#             "name": "All",
#             "image_url": "logo-all-cat.svg",  # Bisa pakai default image atau None
#             "total_products": total_all_products,
#             "created_at": None,
#             "updated_at": None,
#         }
#     ]

#     for category in categories:
#         result.append({
#             "id": category.id,
#             "name": category.name,
#             "image_url": category.image_url,
#             "total_products": len(category.products),
#             "created_at": category.created_at,
#             "updated_at": category.updated_at,
#         })

#     return result

# def get_prod():
#     products = Product.query.all()
#     result = []

#     for product in products:
#         result.append({
#             "id": product.id,
#             "name": product.name,
#             "image_url": product.image_url,
#             "price": product.price,
#             "created_at": product.created_at,
#             "updated_at": product.updated_at,
#         })
    
#     return result


@app.route("/", methods=["GET"])
def index():
    menu = get_menus()
    data = get_data()
    return render_template("index.html", menu=menu, data=data)

@app.route("/stock-management", methods=['GET'])
def stock():
    menu = get_menus()
    return render_template("stock.html", menu=menu)


if __name__ == '__main__':
    app.run(port=9000, debug=True)