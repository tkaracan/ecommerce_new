
from models.models import db

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