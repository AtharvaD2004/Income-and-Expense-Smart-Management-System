from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

TRANSACTION_TYPES = ["income", "expense", "investment"]

CATEGORIES = {
    "income":     ["Salary", "Freelance", "Business", "Other"],
    "expense":    ["Food", "Transport", "Shopping", "Bills", "Health", "Education", "Entertainment", "Other"],
    "investment": ["Stocks", "Real Estate", "Education", "Other"]
}

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password   = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship("Transaction", backref="user", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email, "created_at": self.created_at.isoformat()}

class Transaction(db.Model):
    __tablename__ = "transactions"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    amount      = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(100), nullable=False)
    type        = db.Column(db.String(20), nullable=False)
    date        = db.Column(db.Date, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "description": self.description,
            "amount": self.amount, "category": self.category,
            "type": self.type, "date": self.date.isoformat(),
            "created_at": self.created_at.isoformat()
        }
