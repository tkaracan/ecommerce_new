from models.models import db

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    bought = db.Column(db.Boolean, nullable=False, default=False)
    price = db.Column(db.Integer, default=1)
    def __repr__(self):
        return f'<Cart {self.id}>'
