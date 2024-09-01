from flask import Blueprint, render_template, redirect, request, url_for
from app.extensions import db

bp = Blueprint("auth", __name__)

@bp.route('/login/')
def login():
    return render_template("auth/login.html")

@bp.route('/register/', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        print(email, password)
        return redirect(url_for("main.index"))
    else:
        return render_template("auth/register.html")


@bp.route('/logout/')
def logout():
    return render_template("auth/logout.html")