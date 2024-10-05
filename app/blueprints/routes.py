from flask import Blueprint, request, render_template, session, url_for, redirect, jsonify

from app.extensions import db
from app.models.models import User, Category, Product, Transaction
from app.models.data import items
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

bp = Blueprint("app", __name__)


@bp.route("/")
def index():
    if "username" in session:
        return redirect(url_for("app.dashboard"))
    return render_template("stock/index.html")


@bp.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Collect info from the form
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["username"] = username
            return redirect(url_for("app.dashboard"))
        else:
            print("user does not exist")
            return render_template("auth/login.html")
    return render_template("auth/login.html")

@bp.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Collect info from the form
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("auth/register.html", error="User already exists!")
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            print(new_user.username)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect(url_for('app.login'))
    else:
        return render_template("auth/register.html")


@bp.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('app.index'))

### Dashboard endpoint
@bp.route('/dashboard/')
def dashboard():
    if "username" in session:
        total_products = db.session.execute(db.select(db.func.count(Product.id))).scalar()
        total_categories = db.session.execute(db.select(db.func.count(Category.id))).scalar()
        transactions = []
        # transactions = db.session.execute(db.select(Transaction).order_by(Transaction.transaction_date.desc())).scalars().all()
        # transactions = db.session.query(Transaction).order_by(db.desc(Transaction.transaction_date)).limit(5).all()

        return render_template("stock/dashboard.html", username=session["username"], transactions=transactions, total_products=total_products, total_categories=total_categories)
    return redirect(url_for('app.index'))




### Categories endpoint
@bp.get("/categories/")
def get_categories():
    if "username" in session:
        user = db.session.execute(db.select(User).filter_by(username=session["username"])).scalar_one_or_none()

        if not user:
            return jsonify({"error": "User not found."}), 404
        
        categories = db.session.execute(db.select(Category).filter_by(user_id=user.id)).scalars().all()

        categories_list = [{
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "products": category.products,
            "products_length": len(category.products)
        } for category in categories]

        # categories_json = jsonify(categories_list)
        
        return render_template("stock/categories.html", categories=categories_list)
    else:
        return redirect(url_for('app.register'))
        

@bp.post("/categories/")
def create_category():
    if "username" in session:

        user = db.session.execute(db.select(User).filter_by(username=session["username"])).scalar_one_or_none()
        if not user:
            return jsonify({"error": "User not found."}), 404
        if request.content_type == "application/json":
            data = request.get_json()
            print("Received JSON data;", data)
            name = data.get("category_name")
            description = data.get("category_description")
        else:
            print("Received form data")
            name = request.form.get("category-name")
            description = request.form.get("category-description")

        print(f"Attempting to create category: {name}, {description}")

       
        if not name or not description:
            print("Missing name or description")
            return jsonify({"error": "Category name and description are required."})
        
        # Check if category already exists
        existing_category = db.session.execute(db.select(Category).filter_by(user_id=user.id, name=name.lower())).scalar_one_or_none()

        if existing_category:
            jsonify({"error": f"Category with name '{name}' already exists for this user."}), 400

        new_category = Category(user_id=user.id, name=name, description=description)

        try:
            db.session.add(new_category)
            db.session.commit()
        
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError: {str(e)}")
            return jsonify({"error": "Failed to add category due to a unique constraint violation."}), 500
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error: {str(e)}")
            return jsonify({"error": "An unexpected error occurred."}), 500
        return redirect(url_for("app.get_categories"))
    return redirect(url_for("app.register"))

@bp.delete("/categories/<string:category_id>")
def delete_category(category_id):
    try:
        category = db.session.execute(db.select(Category).filter_by(id=category_id)).scalar_one_or_none()

        if category:
            db.session.delete(category)
            db.session.commit()
            return jsonify({"message": f"Category {category} deleted successfully!"}), 200
        else:
            return jsonify({"error": "Category not found"}, 404)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500  

@bp.get("/products/")
def get_products():
    if "username" in session:
        products = db.session.execute(db.select(Product)).scalars()
        categories = db.session.execute(db.select(Category)).scalars()

        products_list = [{
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "quantity": product.quantity,
            "category": product.category
        } for product in products]

        
        # products_json = jsonify(products_list)
        return render_template("stock/products.html", products=products_list, categories=categories)
    else:
        return redirect(url_for("app.login"))

# transactions = db.session.execute(db.select(Transaction).order_by(Transaction.transaction_date.desc())).scalars().all()
# products = db.session.execute(db.select(Product)).scalars().all()

@bp.post("/products/")
def create_product():
    if "username" in session:
        name = request.form["name"]
        quantity = request.form["quantity"]
        description = request.form["description"]

        category_name = request.form["category"]
        category = db.session.execute(db.select(Category).filter_by(name=category_name)).scalar()
        
        if not category:
            raise ValueError("Categories does not exist")

        existing_products = db.session.execute(db.select(Product).filter_by(name=name)).scalar()

        if existing_products:
            return f"The product name '{name}' already exists"
    
        new_product = Product(name=name, quantity=int(quantity), category_id=category.id, description=description)

        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for("app.get_products"))
        except IntegrityError:
            db.session.rollback()
            return "Failed to add product due to a unique constraint violation."


@bp.delete("/products/<string:product_id>")
def delete_product(product_id):
    try:
        product = db.session.execute(db.select(Product).filter_by(id=product_id)).scalar_one_or_none()

        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"message": "Product deleted successfully!"}), 200
        else:
            return jsonify({"error": "Product not found"}, 404)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500      
      

# Stock transactions Endpoints
@bp.get("/transactions/")
def transactions():
    transactions = db.session.execute(db.select(Transaction).order_by(Transaction.transaction_date.desc())).scalars().all()
    products = db.session.execute(db.select(Product)).scalars().all()
    return render_template("stock/transactions.html", transactions=transactions, products=products)

# @bp.post("/transactions/")
# def add_transaction():
#     product_id = request.form['product_id']
#     type = request.form["type"]
#     quantity = int(request.form["quantity"])
#     purpose = request.form["purpose"]

#     product = db.get_or_404(Product, product_id)

#     if type.lower() == 'out' and product.quantity < quantity:
#         return redirect(url_for('app.transactions'))

#     new_transaction = Transaction(type=type, quantity=quantity, purpose=purpose)

#     return render_template("stock/transaction.html", product_id=product_id)


@bp.post("/transactions/")
def add_transaction():

    data = request.get_json()
    product = db.get_or_404(Product, data['product_id'])

    if data['type'].lower() == 'out' and product.quantity < data['quantity']:
        return jsonify({"message": "Insufficient stock"}), 400
    print(product)

    new_transaction = Transaction(
        product_id=data['product_id'],
        type=data['type'],
        quantity=data['quantity'],
        purpose=data.get('purpose', ''),
        transaction_date=datetime.fromisoformat(data['transaction_date'])
    )
    print(new_transaction)

    if data['type'].lower() == 'in':
        product.quantity += data['quantity']
    else:
        product.quantity -= data['quantity']

    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({
        'id': new_transaction.id,
        'product_id': new_transaction.product_id,
        'type': new_transaction.type,
        'quantity': new_transaction.quantity,
        'purpose': new_transaction.purpose,
        'transaction_date': new_transaction.transaction_date.isoformat()
    }), 201
