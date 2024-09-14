from app.extensions import db
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String, Integer, DateTime
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin
import uuid
from datetime import timedelta

class User(db.Model):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
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

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    products: Mapped[List["Product"]] = relationship(back_populates="category")
    
    def __repr__(self):
        return f"<Category {self.name}>"

class Product(db.Model):

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id: Mapped[str] = mapped_column(ForeignKey("category.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=True) # Change the nullable later
    description: Mapped[Optional[str]] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category: Mapped["Category"] = relationship(back_populates="products")
    transactions: Mapped[List["Transaction"]] = relationship(back_populates="product")


    def __repr__(self):
        return f"<Product {self.name}>"
class Transaction(db.Model):
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(ForeignKey("product.id"), nullable=False)
    
    type: Mapped[str] = mapped_column(String(3), nullable=False) # 'in' or 'out'
    purpose: Mapped[Optional[str]] = mapped_column(String(255))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    product: Mapped["Product"] = relationship(back_populates="transactions")

