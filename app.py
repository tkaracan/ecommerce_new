from flask import Flask, jsonify, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from MODELS import Customer, Product, db, Order

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
db.init_app(app)

#db.init_app(app) #-- this is the same, but with multiple py files

#now create MODELS like roles
#from each class you need to inherit from Model
#db.create_all()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    if not username or not password:
        return jsonify({'message': 'Missing username or password'}), 400

    customer = Customer.query.filter_by(username=username).first()
    if not customer or customer.password != password:
        return jsonify({'message': 'Wrong Password or Username'}), 401

    token = jwt.encode({'customer': username}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})





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
        #      customer_list[-1]["tugrul dedi ki:"]=('deneme')


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


        }
        product_list.append(customer_dict)

    return jsonify(product_list)

@app.route("/product/<product_id>", methods=["GET"])
def product_detail(product_id):
    product = Product.query.filter_by(id=product_id).first()

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify({
        'id': product.id,
        'name': product.name,
        'price': product.price,
        'description': product.description
    })
@app.route("/product", methods=["POST"])
def add_product():


    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'No token provided'}), 401

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('customer')
    customer = Customer.query.filter_by(username=username).first()


    if not customer:
        return jsonify({'message': 'Invalid user'}), 401
    if customer.is_admin == False:
        return("You cant add products here, go away")
    else:

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










if __name__ == "__main__":
    app.run(debug=True)








