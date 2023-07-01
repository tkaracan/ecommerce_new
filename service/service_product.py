from models.model_product import Product
from models.models import db


class ProductService:
    @staticmethod
    def get_all_products():
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


    def add_product(self, name, price, description):
        try:
            new_product = Product(name=name, price=price, description=description)
            db.session.add(new_product)
            db.session.commit()
        except:
            return {"message": "product not added"}

        return {
            'id': new_product.id,
            'name': new_product.name,
            'description': new_product.description,
            'price': new_product.price
        }, 201