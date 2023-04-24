from flask import Flask, jsonify, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from MODELS import Customer, Product, db, Cart, Order


import jwt

# create a new instance of the flask class. create a flask object
app = Flask(__name__)
# put configuration to the app. -----------here: /// means file in the current directory
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dataCAN.sqlite3'
# surpress trivial warnings in terminal
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# for login auth token
app.config['SECRET_KEY'] = 'tugrul'

db.init_app(app)

# db.init_app(app) #-- this is the same, but with multiple py files

# now create MODELS like roles
# from each class you need to inherit from Model
with app.app_context():
    db.create_all()


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

    return jsonify(customer_list)


@app.route("/user", methods=["POST"])
def create_user():
    # Parse the JSON payload from the request
    data = request.get_json()
    # Get the values for the new customer from the payload
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)  # Optional, default to False if not provided
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
        'order_count': 0  # New customers have no orders yet
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

    username = decoded_token.get('customer')  # bu neden str?
    customer = Customer.query.filter_by(username=username).first()

    if not customer:
        return jsonify({'message': 'Invalid user'}), 401
    if customer.is_admin == False:
        return ("You cant add products here, go away")
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


@app.route("/cart", methods=["POST"])
def add_to_cart():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'You need to sign in to buy stuff dude'}), 401
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('customer')
    print(username)
    customer = Customer.query.filter_by(username=username).first()
    customer_id = customer.id
    if not customer:
        return jsonify({'message': 'Invalid user'}), 401

    data = request.get_json()
    product_id = data.get('product_id')  # Changed 'product' to 'products'
    quantity = data.get('quantity')

    if quantity == 0:
        print("success")

    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({'message': 'we dont have it. come tomorrow!'}), 401
    previous_order = Cart.query.filter_by(id=product_id).filter_by(customer_id=customer_id).first()

    if previous_order:
        if quantity == 0:
            db.session.delete(previous_order)
            db.session.commit()
            return jsonify({
                'Message': 'Product deleted.Its gone.',
            }), 201

        previous_order.price = product.price * quantity
        previous_order.quantity = quantity
        return jsonify({
            'Message': 'Product details updated Mr. Adams',
            'customer_id': customer.id,
            'Product_Id': previous_order.product_id,
            'Product_Name': product.name,
            'Quantity': previous_order.quantity,
            'price': previous_order.price
        }), 201


    else:
        price = product.price * quantity

    cart = Cart(customer_id=customer_id, product_id=product_id, quantity=quantity, price=price)
    # existing_order = Order.query.filter_by(customer_id=customer_id).first()

    db.session.add(cart)
    db.session.commit()

    return jsonify({
        'customer_id': customer.id,
        'Product_Id': cart.product_id,
        'Product_Name': product.name,
        'Quantity': cart.quantity,
        'price': cart.price
    }), 201


@app.route("/cart", methods=["GET"])
def cart_view():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'You need to sign in to see your Cart bruh'}), 401
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('customer')
    print(username)
    customer = Customer.query.filter_by(username=username).first()
    customer_id = customer.id

    # carts = Cart.query.all()
    carts = Cart.query.filter_by(customer_id=customer_id).all()

    cart_list = []
    for cart in carts:
        cart_dict = {

            'name': cart.product_id,
            'count': cart.quantity,
            'price': cart.price,

        }
        cart_list.append(cart_dict)

    return jsonify({"customer_id": customer_id, 'cart_items': cart_list})


@app.route("/order", methods=["POST"])
def order_give():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'You need to sign in to see your Cart bruh'}), 401
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('customer')

    customer = Customer.query.filter_by(username=username).first()
    customer_id = customer.id
    if not customer:
        return jsonify({'message': 'Invalid user'}), 401

    carts = Cart.query.filter_by(customer_id=customer_id).all()
    if not carts:
        return jsonify({'message': 'go buy some stuff first, empty here!'}), 401

    cart_list = []
    total_price = 0
    for cart in carts:
        cart_dict = {

            'name': cart.product_id,
            'count': cart.quantity,
            'price': cart.price,

        }
        total_price = total_price + cart_dict['price']
        cart_list.append(cart_dict)

    print(total_price)

    data = request.get_json()
    confirm = data.get('Do_U_Confirm? Y/N')  # Changed 'product' to 'products'
    if confirm != "Y":
        return jsonify({'message': 'DENIED! buy it later then...'}), 401

    order = Order(customer_id=customer_id, order_summary=cart_list, total_price=total_price)

    db.session.add(order)
    db.session.commit()

    for cart in carts:
        db.session.delete(cart)
        db.session.commit()

    return jsonify({
        'Message': 'Order Succeeded!',
        'customer_id': customer.id,
        'Order_Details': cart_list,
        'Total': total_price,

    }), 201

    return jsonify({"customer_id": customer_id, 'cart_items': cart_list})

@app.route("/order", methods=["GET"])
def order_view():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({'message': 'You need to sign in to see your Cart bruh'}), 401
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401

    username = decoded_token.get('customer')
    print(username)
    customer = Customer.query.filter_by(username=username).first()
    customer_id = customer.id

    # carts = Cart.query.all()
    orders = Order.query.filter_by(customer_id=customer_id).all()

    order_list = []
    for order in orders:
        order_dict = {

            'Date': order.order_date,
            'Order_Details': order.order_summary,
            'price': order.total_price,

        }
        order_list.append(order_dict)

    return jsonify({"customer_id": customer_id, 'Previous orders': order_list})


if __name__ == "__main__":
    app.run(debug=True)
