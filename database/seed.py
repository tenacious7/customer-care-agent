from database.connection import engine
from database.models import Base, Customer, Product, Order


def seed_database():

    # Create tables
    Base.metadata.create_all(engine)

    # Create database session
    from sqlalchemy.orm import Session

    with Session(engine) as session:

        # Customers
        customer1 = Customer(
            name="Brijesh",
            email="brijesh@example.com",
            phone="9876543210"
        )

        customer2 = Customer(
            name="Rahul",
            email="rahul@example.com",
            phone="9876543211"
        )

        customer3 = Customer(
            name="Ankit",
            email="ankit@example.com",
            phone="9876543212"
        )

        # Products
        watch1 = Product(
            name="Classic Black Watch",
            description="Classic black stainless steel watch",
            price=2999,
            stock=15
        )

        watch2 = Product(
            name="Silver Watch",
            description="Minimal silver stainless steel watch",
            price=3499,
            stock=8
        )

        watch3 = Product(
            name="Sport Watch",
            description="Sport watch with silicone strap",
            price=2499,
            stock=20
        )

        session.add_all([
            customer1,
            customer2,
            customer3,
            watch1,
            watch2,
            watch3
        ])

        session.flush()

        # Orders
        order1 = Order(
            order_number="ORD1001",
            customer_id=customer1.id,
            product_id=watch1.id,
            status="SHIPPED",
            estimated_delivery="2026-09-12"
        )

        order2 = Order(
            order_number="ORD1002",
            customer_id=customer2.id,
            product_id=watch2.id,
            status="DELIVERED",
            estimated_delivery="2026-09-08"
        )

        order3 = Order(
            order_number="ORD1003",
            customer_id=customer3.id,
            product_id=watch3.id,
            status="OUT_FOR_DELIVERY",
            estimated_delivery="2026-09-10"
        )

        session.add_all([
            order1,
            order2,
            order3
        ])

        session.commit()

        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_database()