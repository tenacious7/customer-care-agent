from typing import TypedDict


class CustomerState(TypedDict):
    message: str
    intent: str
    order_number: str
    response: str
    product_name: str
    active_product: dict
