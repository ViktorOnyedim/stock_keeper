from flask import Blueprint, request, render_template, session, url_for, redirect, jsonify

from app.extensions import db
from app.models.models import User, Category, Product, Transaction
from app.models.data import items
from sqlalchemy.exc import IntegrityError

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
            print("error: user already exists")
            return render_template("auth/register.html", error="User already exists")
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect(url_for('app.dashboard'))
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

        # user = User.query.filter_by(username=username).first()
        print("*******HELLO********")
        # print(session["created_at"])
        return render_template("stock/dashboard.html", username=session["username"])
    return redirect(url_for('app.index'))


### Categories endpoint
@bp.get("/categories/")
def get_categories():
    if "username" in session:
        categories = db.session.execute(db.select(Category)).scalars().all()

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
        return redirect(url_for('app.index'))
        

@bp.post("/categories/")
def create_category():
    if "username" in session:
        name = request.form["name"]
        description = request.form["description"]
        existing_category = db.session.execute(db.select(Category).filter_by(name=name)).scalar()

        if existing_category:
            return f"Category with name '{name}' already exists."

        new_category = Category(name=name, description=description)

        try:
            db.session.add(new_category)
            db.session.commit()
            return redirect(url_for("app.get_categories"))
        except IntegrityError:
            db.session.rollback()
            return "Failed to add category due to a unique constraint violation."

        # categories =
        # return jsonify({
        #     "id": new_category.id,
        #     "name": new_category.name,
        #     "description": new_category.description
        # }), 201
        
    return redirect(url_for("app.register"))

# /categories/{categoryId} Get and update specific category
@bp.route("/categories/<int:id>", methods=["GET", "PUT", "DELETE"])
def category(id):
    return render_template("stock/category.html", id=id)


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

        print(products_list)
        # products_json = jsonify(products_list)
        return render_template("stock/products.html", products=products_list)
    else:
        return redirect(url_for("app.login"))

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

@bp.post("/transactions/<string:product_id>")
def add_transaction(id):
    type = request.form["type"]
    quantity = int(request.form["quantity"])
    purpose = request.form["purpose"]

    product = db.get_or_404(Product, product_id)

    if type.lower() == 'out' and product.quantity < quantity:
        return redirect(url_for('app.transactions'))

    new_transaction = Transaction(type=type, quantity=quantity, purpose=purpose)

    return render_template("stock/transaction.html", id=id)

