from models.model_cart import Cart


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