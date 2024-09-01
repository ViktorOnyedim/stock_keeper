from app.extensions import db
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey, Integer, String
from datetime import datetime, timezone

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(1000))
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User {self.name}>"
    
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
    category: Mapped["Category"] = relationship("Category", back_populates="itemssou")

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