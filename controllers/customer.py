import jwt
from flask import request, current_app
from flask_restx import Resource, Namespace, fields

from models.models import db
from models.customer import Customer

ns_customer = Namespace('customer', description='Customer operations')


# Define models for Swagger documentation
login_model = ns_customer.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})


customer_model = ns_customer.model('Customer', {
    'id': fields.Integer,
    'username': fields.String,
    'is_admin': fields.Boolean,
    'order_count': fields.Integer
})
new_customer_model = ns_customer.model('NewCustomer', {
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'is_admin': fields.Boolean(required=False, default=False)
})






@ns_customer.route('/login')
class LoginResource(Resource):
    @ns_customer.doc('login', responses={
        200: 'Login successful',
        400: 'Missing username or password',
        401: 'Wrong password or username'
    })
    @ns_customer.expect(login_model)
    def post(self):
        data = request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return {'message': 'Missing username or password'}, 400

        customer = Customer.query.filter_by(username=username).first()
        if not customer or customer.password != password:
            return {'message': 'Wrong Password or Username'}, 401

        token = jwt.encode({'customer': username}, current_app.config['SECRET_KEY'], algorithm='HS256')
        return {'token': token}

@ns_customer.route('/user')
class CustomerResource(Resource):
    @ns_customer.doc(responses={
        200: 'Success',
        400: 'Bad Request',
        401: 'Unauthorized access'
    })
    # @ns_customer.marshal_list_with(customer_model)
    def get(self):
        """
        Get a list of all customers
        """

        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'No token provided'}, 401
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401

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

        return customer_list




@ns_customer.route('/')
class CustomerResource(Resource):
    # ... The existing get method ...

    @ns_customer.doc(responses={
        201: 'Created',
        400: 'Bad Request',
        401: 'Unauthorized access'
    })
    @ns_customer.expect(new_customer_model, validate=True)
    # @ns_customer.marshal_with(customer_model, code=201)
    def post(self):
        """
        Create a new customer
        """
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        is_admin = data.get('is_admin', False)

        new_customer = Customer(username=username, password=password, is_admin=is_admin)
        db.session.add(new_customer)
        db.session.commit()

        return {
            'id': new_customer.id,
            'username': new_customer.username,
            'is_admin': new_customer.is_admin,
            'order_count': 0
        }, 201
