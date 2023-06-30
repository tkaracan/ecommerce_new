from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from models.models import db


from config.config import GlobalConfig

from controllers.controller_customer import ns_customer
from controllers.controller_product import ns_product
from controllers.controller_cart import ns_cart
from controllers.controller_order import ns_order

global_config = GlobalConfig()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = global_config.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = global_config.JWT_SECRET_KEY


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


cors_origin_url = f"http://{global_config.CORS_IP}:{global_config.CORS_PORT}"
cors = CORS(app, origins=[cors_origin_url])

with app.app_context():
    db.create_all()





if __name__ == "__main__":
    app.run(debug=True)
