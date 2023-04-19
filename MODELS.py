from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    ######BU OLMADAN LOGIN CALISMADI, NEDENINI OGREN
    def __repr__(self):
        return f'<Customer {self.username}>'

    # this will create a pseudo column on Order. ASK ABOUT THIS!!!!!!!!!!!!!!
    orders = db.relationship('Order', backref='customer')


# this is for order-product relationship
order_product = db.Table('order_product',
                         db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                         )


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # ForeignKey means this column is coming from another table. name of the table should be lowercase of the class name
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    # when you want to know products on the order. Ask more about this!!!!!!!!!!!!!!!!
    products = db.relationship('Product', secondary=order_product)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # (50) --> max 50 character str
    description = db.Column(db.String(140))  # (50) --> max 50 character str
    price = db.Column(db.Integer, nullable=False)  # nullable = true means you cant leave it blank
