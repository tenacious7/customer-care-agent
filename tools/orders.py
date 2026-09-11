from sqlalchemy.orm import Session

from database.connection import engine
from database.models import Order, Product


def get_order(order_number: str):

    with Session(engine) as session:

        result = (
            session.query(Order, Product)
            .join(Product, Order.product_id == Product.id)
            .filter(Order.order_number == order_number)
            .first()
        )

        if not result:
            return None

        order, product = result

        return {
            "order_number": order.order_number,
            "product": product.name,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
        }

def get_product(product_name: str):

    with Session(engine) as session:

        product = (
            session.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .first()
        )

        if not product:
            return None

        return {
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
        }