import jwt
from flask import request, current_app,json
from flask_restx import Resource, Namespace, fields
from MODELS import Product, db, Customer, Order,Cart

ns_order = Namespace('order', description='Order operations')


order_list_model = ns_order.model('OrderList', {
    'Begin': fields.Integer(description='Start number'),
    'End': fields.Integer(description='End number')
})

order_response_model = ns_order.model('OrderResponse', {
    'customer_id': fields.Integer(description='Customer ID'),
    'Previous orders': fields.List(fields.Nested(ns_order.model('Order', {
        'Date': fields.String(description='Order date'),
        'Order_Details': fields.String(description='Order summary'),
        'price': fields.String(description='Total price')
    })), description='List of previous orders')
})

@ns_order.route('/give_order')
class OrderResource(Resource):
    @ns_order.doc('create_order', responses={
        201: 'Order succeeded',
        401: 'Unauthorized access'
    })
    # @api.expect(order_confirm_model)
    def get(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to buy sheet'}, 401
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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
    @ns_order.doc('list_orders', responses={
        200: 'List of orders',
        401: 'Unauthorized access'
    })
    @ns_order.expect(order_list_model)
    #@api.marshal_list_with(order_list_model)
    def post(self):
        token = request.headers.get('Authorization')

        if not token:
            return {'message': 'You need to sign in to see your Cart bruh'}, 401
        try:
            decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
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

