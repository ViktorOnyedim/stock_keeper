from flask import Blueprint, request, render_template, session, url_for, redirect

from app.extensions import db
from app.models.models import User

bp = Blueprint("app", __name__)


@bp.route("/")
def index():
    if "username" in session:
        return redirect(url_for("stock/dashboard"))
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


@bp.route('/dashboard/')
def dashboard():
    if "username" in session:
        return render_template("stock/dashboard.html", username=session["username"])
    return redirect(url_for('app.index'))


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

