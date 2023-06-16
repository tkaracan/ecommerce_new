from flask import Flask, request
from flask_restx import Api, Resource, fields, mask

from flask_cors import CORS
from MODELS import Customer, Product, db, Cart, Order
import jwt

from controllers.customer import ns_customer
from controllers.product import ns_product
from controllers.cart import ns_cart
from controllers.order import ns_order

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataCAN.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'tugrul'
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

db.init_app(app)



api = Api(app, version='1.0', title='Noodle Store API', description='A Noodle Store API', doc='/swagger/', authorizations=authorizations, security='apikey')
api.add_namespace(ns_customer)
api.add_namespace(ns_product)
api.add_namespace(ns_cart)
api.add_namespace(ns_order)

cors = CORS(app, origins=["http://localhost:5000"])
custom_mask = mask.Mask('*,!field_to_exclude', skip=True)
with app.app_context():
    db.create_all()





if __name__ == "__main__":
    app.run(debug=True)
