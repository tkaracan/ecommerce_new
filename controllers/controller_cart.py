import jwt
from flask import request, current_app
from flask_restx import Resource, Namespace, fields
from models.models import db
from models.model_customer import Customer
from models.model_cart import Cart
from models.model_product import Product
from service.service_cart import CartService
from service.service_token import CustomerService

ns_cart = Namespace('cart', description='Cart operations')


add_cart_model = ns_cart.model('AddToCart', {
    'product_id': fields.Integer(required=True),
    'quantity': fields.Integer(required=True)
})


cart_model = ns_cart.model('Cart', {
    'name': fields.Integer(description='Product ID'),
    'count': fields.Integer(description='Quantity'),
    'price': fields.Float(description='Price')
})


@ns_cart.route('/add_to_cart')
class AddToCartResource(Resource):
    @ns_cart.doc('add_to_cart', responses={
        201: 'Cart updated successfully',
        401: 'Unauthorized access'
    })
    @ns_cart.expect(add_cart_model)
    def post(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to buy stuff dude'}, 401
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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
        @ns_cart.doc('view_cart', responses={
            200: 'Cart fetched successfully',
            401: 'Unauthorized access'
        })
        def get(self):
            token = request.headers.get('Authorization')
            if token is None:
                return {'message': 'You need to sign in to see your Cart my bruh'}, 401
            customer_service = CustomerService()

            customer = customer_service.validate_token(token)
            if customer is None:
                return {'message': 'You need to sign in to see your Cart bruh'}, 401

            cart_service = CartService()
            cart_items = cart_service.get_cart_items(customer.id)

            return {"customer_id": customer.id, 'cart_items': cart_items}

# @ns_cart.route('/view_cart')
# class CartViewResource(Resource):
#     @ns_cart.doc('view_cart', responses={
#         200: 'Cart fetched successfully',
#         401: 'Unauthorized access'
#     })
#     def get(self):
#         def token_check(token):
#             if not token:
#                 return {'message': 'You need to sign in to see your Cart bruh'}, 401
#             try:
#                 decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
#             except jwt.InvalidTokenError:
#                 return {'message': 'Invalid token'}, 401
#
#             username = decoded_token.get('customer')
#             customer = Customer.query.filter_by(username=username).first()
#             return customer
#
#
#         customer = token_check(request.headers.get('Authorization'))
#
#
#         try:
#             customer_id = customer.id
#         except:
#             return customer
#
#         carts = Cart.query.filter_by(customer_id=customer_id).all()
#
#         cart_list = []
#         for cart in carts:
#             cart_dict = {
#                 'name': cart.product_id,
#                 'count': cart.quantity,
#                 'price': cart.price,
#             }
#             cart_list.append(cart_dict)
#
#         return {"customer_id": customer_id, 'cart_items': cart_list}


