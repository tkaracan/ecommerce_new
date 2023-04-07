from flask import Flask, jsonify, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt

#create a new instance of the flask class. create a flask object
app = Flask(__name__)
#put configuration to the app. -----------here: /// means file in the current directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbtrl4.sqlite3'
#surpress trivial warnings in terminal
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#for login auth token
app.config['SECRET_KEY'] = 'tugrul'

#instantiate (create) flask sql alchemy object
db = SQLAlchemy(app)

#db.init_app(app) #-- this is the same, but with multiple py files

#now create MODELS like roles
#from each class you need to inherit from Model

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False, unique = True)
    password = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default = False)
    #this will create a psudo column on Order. ASK ABOUT THIS!!!!!!!!!!!!!!
    orders = db.relationship('Order', backref='customer')

#this is for order-product relationship
order_product = db.Table('order_product',
                         db.Column('order_id', db.Integer, db.ForeignKey('order.id'), primary_key=True),
                         db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
                         )

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    order_date = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)
    #ForeignKey means this column is coming from another table. name of the table should be lowercase of the class name
    customer_id =db.Column(db.Integer,db.ForeignKey('customer.id'), nullable=False)
    #when you want to know products on the order. Ask more about this!!!!!!!!!!!!!!!!
    products = db.relationship('Product', secondary=order_product)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False, unique = True) #(50) --> max 50 character str
    description = db.Column(db.String(140))  # (50) --> max 50 character str
    price = db.Column(db.Integer, nullable=False) #nullable = true means you cant leave it blank

db.create_all()


@app.route("/user", methods=["GET"])
def user_view():
    customers = Customer.query.all()
    customer_list = []
    for customer in customers:
        customer_dict = {
            'id': customer.id,
            'username': customer.username,
            'is_admin': customer.is_admin,
            'order_count': len(customer.orders)
        }
        customer_list.append(customer_dict)

        # if customer.is_admin == True:
        #      customer_list[-1]["tugrul dedi ki:"]=('memeleeer')


    return jsonify(customer_list)


@app.route("/user", methods=["POST"])
def create_user():
    # Parse the JSON payload from the request
    data = request.get_json()
    # Get the values for the new customer from the payload
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False) # Optional, default to False if not provided
    # Create a new Customer object
    new_customer = Customer(username=username, password=password, is_admin=is_admin)
    # Add the new customer to the database
    db.session.add(new_customer)
    db.session.commit()
    # Return a JSON representation of the new customer with a 201 (Created) status code
    return jsonify({
        'id': new_customer.id,
        'username': new_customer.username,
        'is_admin': new_customer.is_admin,
        'order_count': 0 # New customers have no orders yet
    }), 201





@app.route("/product", methods=["GET"])
def product_view():
    products = Product.query.all()
    product_list = []
    for product in products:
        customer_dict = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description' : product.description

        }
        product_list.append(customer_dict)

    return jsonify(product_list)

@app.route("/product", methods=["POST"])
def add_product():
    # Parse the JSON payload from the request
    data = request.get_json()

    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    new_product = Product(name=name, price=price, description=description)

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        'id': new_product.id,
        'name': new_product.name,
        'description': new_product.description,
        'price': new_product.price
    }), 201

@app.route('/login')
def login():
    auth = request.authorization
    if auth and auth.password == 'abc':
        token = jwt.encode({'user': auth.username, 'exp' : datetime.utcnow()+timedelta(minutes=1)}, app.config['SECRET_KEY'])

        #return jsonify({'token': token.decode('UTF-8')})
        return token

    return make_response('Olmadi anam', 401, {'WWW-Authenticate' : 'Basic realm = "Login Required"'})

if __name__ == "__main__":
    app.run(debug=True)








