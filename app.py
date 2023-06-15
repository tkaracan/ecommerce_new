from flask import Flask, request,json
from flask_restx import Api, Resource, fields, mask

from flask_cors import CORS
from MODELS import Customer, Product, db, Cart, Order
import jwt

from controllers.customer import ns_customer

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
cors = CORS(app, origins=["http://localhost:5000"])
custom_mask = mask.Mask('*,!field_to_exclude', skip=True)
with app.app_context():
    db.create_all()


ns_product = api.namespace('product', description='Product operations')
ns_cart = api.namespace('cart', description='Cart operations')
ns_order = api.namespace('order', description='Order operations')

# Define models for Swagger documentation
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})







product_model = api.model('Product', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True)
})

product_detail_model = api.model('ProductDetail', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'description': fields.String()
})

add_product_model = api.model('AddProduct', {
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'description': fields.String(required=False)
})

add_cart_model = api.model('AddToCart', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True)
})

order_confirm_model = api.model('OrderConfirmation', {
    'Do_U_Confirm? Y/N': fields.String(required=True, description='Confirm the order')
})
cart_model = api.model('Cart', {
    'name': fields.Integer(description='Product ID'),
    'count': fields.Integer(description='Quantity'),
    'price': fields.Float(description='Price')
})

order_list_model = api.model('OrderList', {
    'Begin': fields.Integer(description='Start number'),
    'End': fields.Integer(description='End number')
})

order_response_model = api.model('OrderResponse', {
    'customer_id': fields.Integer(description='Customer ID'),
    'Previous orders': fields.List(fields.Nested(api.model('Order', {
        'Date': fields.String(description='Order date'),
        'Order_Details': fields.String(description='Order summary'),
        'price': fields.String(description='Total price')
    })), description='List of previous orders')
})







@api.route('/login')
class LoginResource(Resource):
    @api.doc('login', responses={
        200: 'Login successful',
        400: 'Missing username or password',
        401: 'Wrong password or username'
    })
    @api.expect(login_model)
    def post(self):
        data = request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return {'message': 'Missing username or password'}, 400

        customer = Customer.query.filter_by(username=username).first()
        if not customer or customer.password != password:
            return {'message': 'Wrong Password or Username'}, 401

        token = jwt.encode({'customer': username}, app.config['SECRET_KEY'], algorithm='HS256')
        return {'token': token}








@ns_product.route('/view_all')
class ProductResource(Resource):
    @api.doc(responses={
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized access'
    })

    @ns_product.marshal_list_with(product_model)
    def get(self):
        """
        Retrieve all products
        """
        products = Product.query.all()
        product_list = []
        for product in products:
            product_dict = {
                'id': product.id,
                'name': product.name,
                'price': product.price
            }
            product_list.append(product_dict)

        return product_list



@ns_product.route('/<int:product_id>')
@api.doc(params={'product_id': 'The product ID'})
class ProductDetailResource(Resource):
    @api.doc(responses={200: 'OK', 404: 'Not Found'})
    @api.marshal_with(product_detail_model)
    def get(self, product_id):
        """
        Retrieve a product by its ID
        """
        product = Product.query.filter_by(id=product_id).first()

        if not product:
            api.abort(404, "Product not found")

        return product


@ns_product.route('/')
class AddProductResource(Resource):
    @api.doc('add_product', responses={
        201: 'Product added successfully',
        401: 'Unauthorized access'
    })
    @api.expect(add_product_model)
    def post(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'No token provided'}, 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        username = decoded_token.get('customer')
        customer = Customer.query.filter_by(username=username).first()

        if not customer:
            return {'message': 'Invalid user'}, 401
        if customer.is_admin == False:
            return ("You cant add products here, go away")
        else:
            try:
                data = request.get_json()
                name = data.get('name')
                price = data.get('price')
                description = data.get('description')
                new_product = Product(name=name, price=price, description=description)

                db.session.add(new_product)
                db.session.commit()
            except:
                return {"message": "we already have that lan"}

        return {
            'id': new_product.id,
            'name': new_product.name,
            'description': new_product.description,
            'price': new_product.price
        }, 201


@ns_cart.route('/add_to_cart')
class AddToCartResource(Resource):
    @api.doc('add_to_cart', responses={
        201: 'Cart updated successfully',
        401: 'Unauthorized access'
    })
    @api.expect(add_cart_model)
    def post(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to buy stuff dude'}, 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        username = decoded_token.get('customer')
        print(username)
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {'message': 'Invalid user'}, 401
        customer_id = customer.id

        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if quantity == 0:
            print("success")

        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return {'message': 'we dont have it. come tomorrow!'}, 401
        previous_order = Cart.query.filter_by(id=product_id).filter_by(customer_id=customer_id).first()

        if previous_order:
            if quantity == 0:
                db.session.delete(previous_order)
                db.session.commit()
                return {
                    'Message': 'Product deleted. Its gone.',
                }, 201

            previous_order.price = product.price * quantity
            previous_order.quantity = quantity
            return {
                'Message': 'Product details updated Mr. Adams',
                'customer_id': customer.id,
                'Product_Id': previous_order.product_id,
                'Product_Name': product.name,
                'Quantity': previous_order.quantity,
                'price': previous_order.price
            }, 201

        else:
            price = product.price * quantity

        cart = Cart(customer_id=customer_id, product_id=product_id, quantity=quantity, price=price)

        db.session.add(cart)
        db.session.commit()

        return {
            'customer_id': customer.id,
            'Product_Id': cart.product_id,
            'Product_Name': product.name,
            'Quantity': cart.quantity,
            'price': cart.price
        }, 201

@ns_cart.route('/view_cart')
class CartViewResource(Resource):
    @api.doc('view_cart', responses={
        200: 'Cart fetched successfully',
        401: 'Unauthorized access'
    })
    def get(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to see your Cart bruh'}, 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        username = decoded_token.get('customer')
        customer = Customer.query.filter_by(username=username).first()
        customer_id = customer.id

        carts = Cart.query.filter_by(customer_id=customer_id).all()

        cart_list = []
        for cart in carts:
            cart_dict = {
                'name': cart.product_id,
                'count': cart.quantity,
                'price': cart.price,
            }
            cart_list.append(cart_dict)

        return {"customer_id": customer_id, 'cart_items': cart_list}

@ns_order.route('/give_order')
class OrderResource(Resource):
    @api.doc('create_order', responses={
        201: 'Order succeeded',
        401: 'Unauthorized access'
    })
    # @api.expect(order_confirm_model)
    def get(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to buy sheet'}, 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        username = decoded_token.get('customer')

        customer = Customer.query.filter_by(username=username).first()
        customer_id = customer.id
        if not customer:
            return {'message': 'Invalid user'}, 401

        carts = Cart.query.filter_by(customer_id=customer_id).all()
        if not carts:
            return {'message': 'go buy some stuff first, empty here!'}, 401

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

        # data = request.get_json()
        # confirm = data.get('Do_U_Confirm? Y/N')  # Changed 'product' to 'products'
        # if confirm != "Y":
        #     return {'message': 'DENIED! buy it later then...'}, 401


        order = Order(customer_id=customer_id, order_summary=json.dumps(cart_list), total_price=total_price)

        db.session.add(order)
        db.session.commit()

        for cart in carts:
            db.session.delete(cart)
            db.session.commit()

        print(cart_list)

        return {
            'Message': 'Order Succeeded!',
            'customer_id': customer.id,
            'Order_Details': cart_list,
            'Total': total_price,
        }, 201


@ns_order.route('/order_history')
class OrderResource(Resource):
    @api.doc('list_orders', responses={
        200: 'List of orders',
        401: 'Unauthorized access'
    })
    @api.expect(order_list_model)
    #@api.marshal_list_with(order_list_model)
    def post(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to see your Cart bruh'}, 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

        username = decoded_token.get('customer')
        customer = Customer.query.filter_by(username=username).first()
        customer_id = customer.id
        print(customer_id)

        data = request.get_json()
        start = data.get('Begin')
        end = data.get('End')





        orders = Order.query.filter_by(customer_id=customer_id).all()
        if not orders:
            return {'message': 'go buy some stuff first, empty here!'}, 401


        order_list = []
        if end == 0:
            for order in orders[start:]:
                order_dict = {
                    'Date': str(order.order_date),
                    'Order_Details': str(order.order_summary),
                    'price': str(order.total_price)
                }
                order_list.append(order_dict)
        else:
            for order in orders[start:end]:
                order_dict = {
                    'Date': str(order.order_date),
                    'Order_Details': str(order.order_summary),
                    'price': str(order.total_price)
                }
                order_list.append(order_dict)




        return {"customer_id": customer_id,
                'Previous orders': order_list}


if __name__ == "__main__":
    app.run(debug=True)
