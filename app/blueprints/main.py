from flask import Blueprint, request, render_template

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("stock/index.html")

@bp.route("/categories/", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        return "<h1>Add Categories</h1>"
    else:
        return render_template("stock/categories.html")


# @bp.route("/categories/", methods=["GET", "POST"])

@bp.route("/items", methods=["GET", "POST"])
def items():
    if request.method == "POST":
        return "<h1>Add Item</h1>"
    else:
        return render_template("stock/items.html")

@bp.route("/transactions/")
def transactions():
    return "<h1>Transaction History</h1>"
