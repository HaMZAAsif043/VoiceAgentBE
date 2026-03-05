import os
import django
import random
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfc_api.settings')
django.setup()

from menu.models import Menu, Order

def seed_orders():
    # Get some menu items to create orders
    menu_items = list(Menu.objects.all())
    if not menu_items:
        print("No menu items found. Please run seed_cheezious_menu.py first.")
        return

    demo_customers = [
        {
            "name": "Ahmed Raza",
            "phone": "+923001234567",
            "address": "House 123, Street 4, F-10, Islamabad",
            "landmark": "Near Silver Oaks"
        },
        {
            "name": "Sara Khan",
            "phone": "+923219876543",
            "address": "Apartment 5B, Askari 11, Lahore",
            "landmark": "Near Gate 1"
        },
        {
            "name": "Zubair Ali",
            "phone": "+923335554443",
            "address": "Sector G-13/2, Street 15, Islamabad",
            "landmark": "Opposite Grocery Store"
        }
    ]

    print("Seeding Demo Orders...")
    for customer in demo_customers:
        # Pick 1-3 random items
        num_items = random.randint(1, 3)
        selected_items = random.sample(menu_items, num_items)
        
        order_items = []
        total_price = 0
        
        for item in selected_items:
            qty = random.randint(1, 2)
            order_items.append({
                "id": item.id,
                "name": item.name,
                "quantity": qty,
                "price": item.cost
            })
            total_price += item.cost * qty
            
        # Create the order
        order = Order.objects.create(
            customer_name=customer['name'],
            phone_number=customer['phone'],
            address=customer['address'],
            landmark=customer['landmark'],
            items=order_items,
            total_price=total_price
        )
        print(f"Created Order #{order.id} for {customer['name']} - Total: {total_price} PKR")

    print("Demo orders seeding completed.")

if __name__ == "__main__":
    seed_orders()
