from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()





class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    bought = db.Column(db.Boolean, nullable=False, default=False)
    price = db.Column(db.Integer, default=1)
    def __repr__(self):
        return f'<Cart {self.id}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_summary = db.Column(db.String)
    total_price = db.Column(db.Integer)

    def __repr__(self):
        return f'<Order {self.id}>'




class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # (50) --> max 50 character str
    description = db.Column(db.String(140))  # (50) --> max 50 character str
    price = db.Column(db.Integer, nullable=False)  # nullable = true means you cant leave it blank

    def __repr__(self):
        return f'<Product {self.name}>'
