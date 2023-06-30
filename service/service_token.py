import jwt
from flask import current_app

from models.model_customer import Customer


class CustomerService:
    def validate_token(self, token):
        if not token:
            return None

        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return None

        username = decoded_token.get('customer')
        customer = Customer.query.filter_by(username=username).first()
        return customer
