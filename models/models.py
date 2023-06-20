from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()







class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    order_summary = db.Column(db.String)
    total_price = db.Column(db.Integer)

    def __repr__(self):
        return f'<Order {self.id}>'





