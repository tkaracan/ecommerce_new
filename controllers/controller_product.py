import jwt
from flask import request, current_app
from flask_restx import Resource, Namespace, fields
from models.models import db
from models.model_customer import Customer
from models.model_product import Product
from service.service_product import ProductService
from service.service_token import CustomerService

ns_product = Namespace('product', description='Product operations')


product_model = ns_product.model('Product', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True)
})

product_detail_model = ns_product.model('ProductDetail', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'description': fields.String()
})

add_product_model = ns_product.model('AddProduct', {
    'name': fields.String(required=True),
    'price': fields.Float(required=True),
    'description': fields.String(required=False)
})


@ns_product.route('/view_all')
class ProductResource(Resource):
    @ns_product.doc(responses={
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized access'
    })
    def get(self):
        """
        Retrieve all products
        """
        product_list = ProductService.get_all_products()

        return product_list



@ns_product.route('/<int:product_id>')
@ns_product.doc(params={'product_id': 'The product ID'})
class ProductDetailResource(Resource):
    @ns_product.doc(responses={200: 'OK', 404: 'Not Found'})
    def get(self, product_id):
        """
        Retrieve a product by its ID
        """
        product = Product.query.filter_by(id=product_id).first()

        if not product:
            ns_product.abort(404, "Product not found")

        return product


@ns_product.route('/')
class AddProductResource(Resource):
    @ns_product.doc('add_product', responses={
        201: 'Product added successfully',
        401: 'Unauthorized access'
    })
    @ns_product.expect(add_product_model)
    def post(self):
        token = request.headers.get('Authorization')
        if token is None:
            return {'message': 'You need to sign in to add productt my bruh'}, 401

        customer_service = CustomerService()
        customer = customer_service.validate_token(token)
        if customer is None:
            return {'message': 'No Customer like that!'}, 401

        if not customer.is_admin:
            return {'message': "You can't add products here, go away, become admin first!"}
        else:
            data = request.get_json()
            name = data.get('name')
            price = data.get('price')
            description = data.get('description')

            product_service = ProductService()
            response = product_service.add_product(name, price, description)

            return response
