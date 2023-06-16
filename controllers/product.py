import jwt
from flask import request, current_app
from flask_restx import Resource, Namespace, fields
from MODELS import Product, db, Customer

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

    # @ns_product.marshal_list_with(product_model)
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
@ns_product.doc(params={'product_id': 'The product ID'})
class ProductDetailResource(Resource):
    @ns_product.doc(responses={200: 'OK', 404: 'Not Found'})
    # @ns_product.marshal_with(product_detail_model)
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

        if not token:
            return {'message': 'No token provided'}, 401
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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
