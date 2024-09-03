from app.extensions import db
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey, String
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(25), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # def __init__(self, name, email, password, is_admin=False):
    #     self.email = email
    #     self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    #     self.name = name
    #     self.created_on = datetime.now()
    #     self.is_admin = is_admin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f"<User {self.name}>"

# class User(UserMixin, db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(1000))
#     email: Mapped[str] = mapped_column(unique=True, nullable=False)
#     password: Mapped[str] = mapped_column(String(100), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

#     def __init__(self, name, email, password, is_admin=False):
#         self.email = email
#         self.password = bcrypt.generate_password_hash(password).decode('utf-8')
#         self.name = name
#         self.created_on = datetime.now()
#         self.is_admin = is_admin
        
#     def __repr__(self):
#         return f"<User {self.name}>"
    
class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    items: Mapped[List["Item"]] = relationship("Item", back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"

class Item(db.Model):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="items")

    name: Mapped[str] = mapped_column(unique=True, nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    quantity_in_stock: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
class Transactions(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(nullable=True)
    quantity_in: Mapped[int] = mapped_column()
    quantity_out: Mapped[int] = mapped_column()
    balance: Mapped[int] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))