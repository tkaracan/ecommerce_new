from models.models import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)  # (50) --> max 50 character str
    description = db.Column(db.String(140))  # (50) --> max 50 character str
    price = db.Column(db.Integer, nullable=False)  # nullable = true means you cant leave it blank

    def __repr__(self):
        return f'<Product {self.name}>'