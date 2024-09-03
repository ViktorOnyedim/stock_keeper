from flask import Blueprint, request, render_template, session, url_for, redirect

from app.extensions import db
from app.models.models import User
from app.extensions import SECRET_KEY

bp = Blueprint("app", __name__)

bp.secret_key = SECRET_KEY


@bp.route("/")
def index():
    if "username" in session:
        return redirect(url_for("stock/dashboard"))
    return render_template("stock/index.html")

@bp.route('/dashboard/')
def dashboard():
    return render_template("stock/dashboard.html")

@bp.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Collect info from the form
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.checkpassword(password):
            session["username"] = username
            redirect(url_for("dashboard"))
        else: 
            return render_template("auth/login.html")
    return render_template("auth/login.html")

@bp.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Collect info from the form
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template("auth/register.html", error="User already here")
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect(url_for('dashboard'))
    else:
        return render_template("auth/register.html")


@bp.route('/logout/')
def logout():
    return render_template("auth/logout.html")


@bp.route("/categories/", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        if "username" in session:
            return f"Logged in as {session['username']}"
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

