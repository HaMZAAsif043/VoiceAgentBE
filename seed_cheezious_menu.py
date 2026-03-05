import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfc_api.settings')
django.setup()

from menu.models import Menu

def seed_menu():
    cheezious_items = [
        # Pizzas
        {"name": "Chicken Mushroom Pizza (Medium)", "cost": 1390},
        {"name": "Behari Kebab Pizza (Medium)", "cost": 1390},
        {"name": "Chicken Pepperoni Pizza (Medium)", "cost": 1390},
        {"name": "Crown Crust Pizza (Medium)", "cost": 1450},
        {"name": "Chicken Tikka Pizza (Small)", "cost": 690},
        {"name": "Chicken Fajita Pizza (Regular)", "cost": 1350},
        {"name": "Chicken Supreme Pizza (Large)", "cost": 1850},
        
        # Burgers
        {"name": "Bazinga Supreme Burger", "cost": 690},
        {"name": "Bazinga Burger", "cost": 560},
        {"name": "Reggy Burger", "cost": 390},
        {"name": "Chicken Spice Burger", "cost": 330},
        
        # Starters & Sides
        {"name": "Spin Rolls", "cost": 590},
        {"name": "Cheezy Sticks", "cost": 630},
        {"name": "Oven Baked Wings (6pcs)", "cost": 600},
        {"name": "Flaming Wings (6pcs)", "cost": 650},
        {"name": "Calzone Chunks (4pcs)", "cost": 1150},
        {"name": "Arabic Rolls", "cost": 690},
        {"name": "Behari Rolls", "cost": 690},
        {"name": "HotShots", "cost": 390},
        
        # Sandwiches & Platters
        {"name": "Special Roasted Platter", "cost": 1200},
        {"name": "Mexican Sandwich", "cost": 920},
        {"name": "Pizza Stacker", "cost": 920},
        {"name": "Euro Sandwich", "cost": 920},
        
        # Pasta
        {"name": "Fettuccine Alfredo Pasta", "cost": 850}, # Estimated
        {"name": "Crunchy Chicken Pasta", "cost": 800},   # Estimated
    ]

    print("Seeding Cheezious Pakistan Menu...")
    for item in cheezious_items:
        # Check if item already exists to avoid duplicates
        obj, created = Menu.objects.get_or_create(
            name=item['name'],
            defaults={'cost': item['cost']}
        )
        if created:
            print(f"Added: {item['name']} - {item['cost']} PKR")
        else:
            # Update price if it exists but is different
            if obj.cost != item['cost']:
                obj.cost = item['cost']
                obj.save()
                print(f"Updated: {item['name']} - {item['cost']} PKR")
            else:
                print(f"Skipped (exists): {item['name']}")

    print("Menu seeding completed.")

if __name__ == "__main__":
    seed_menu()
