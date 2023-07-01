
from flask import request, current_app
from flask_restx import Resource, Namespace, fields

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
        if token is None:
            return {'message': 'You need to sign in to see your Cart my bruh'}, 401
        customer_service = CustomerService()
        customer = customer_service.validate_token(token)
        if customer is None:
            return {'message': 'No Customer like that!'}, 401

        customer_id = customer.id

        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        # if quantity == 0:
        #     print("success")

        cart_service = CartService()
        response = cart_service.add_to_cart(customer_id, product_id, quantity)

        return response

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
                return {'message': 'No Customer like that!'}, 401

            cart_service = CartService()
            cart_items = cart_service.get_cart_items(customer.id)

            return {"customer_id": customer.id, 'cart_items': cart_items}