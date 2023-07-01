from models.model_cart import Cart
from models.model_product import Product
from models.models import db


class CartService:
    def get_cart_items(self, customer_id):
        carts = Cart.query.filter_by(customer_id=customer_id).all()

        cart_list = []
        for cart in carts:
            cart_dict = {
                'name': cart.product_id,
                'count': cart.quantity,
                'price': cart.price,
            }
            cart_list.append(cart_dict)

        return cart_list

    def add_to_cart(self, customer_id, product_id, quantity):
        product = Product.query.filter_by(id=product_id).first()
        if not product:
            return {'message': 'we dont have it. come tomorrow!'}, 401

        cart = Cart.query.filter_by(product_id=product_id, customer_id=customer_id).first()
        if cart:
            if quantity == 0:
                db.session.delete(cart)
                db.session.commit()
                return {
                    'Message': 'Product deleted. It has been removed from your cart.',
                }, 201

            cart.price = product.price * quantity
            cart.quantity = quantity
            return {
                'Message': 'Product details updated.',
                'customer_id': customer_id,
                'Product_Id': cart.product_id,
                'Product_Name': product.name,
                'Quantity': cart.quantity,
                'price': cart.price
            }, 201
        else:
            price = product.price * quantity
            cart = Cart(customer_id=customer_id, product_id=product_id, quantity=quantity, price=price)
            db.session.add(cart)
            db.session.commit()

            return {
                'customer_id': customer_id,
                'Product_Id': cart.product_id,
                'Product_Name': product.name,
                'Quantity': cart.quantity,
                'price': cart.price
            }, 201