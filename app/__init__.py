from flask import Flask
from .blueprints import main
from .blueprints import auth
from .extensions import db

app = Flask(__name__)

app.register_blueprint(main.bp)
app.register_blueprint(auth.bp)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

db.init_app(app)

# Create database
with app.app_context():
    db.create_all()