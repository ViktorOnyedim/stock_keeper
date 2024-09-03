import os
from flask import Flask
from .extensions import db, migrate
from .blueprints import routes
from dotenv import load_dotenv


app = Flask(__name__)

# Set secret key for session management
load_dotenv()
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

# Register Blueprints
app.register_blueprint(routes.bp)

if __name__ in "__main__":
    # Create database
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)