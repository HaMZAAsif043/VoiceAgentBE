import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfc_api.settings')
django.setup()

from menu.models import Menu

def seed_menu():
    smash_burger_items = [
        # BEEF SMASH BURGERS
        {"name": "Classic New York Beef Smash", "cost": 999},
        {"name": "London BBQ Beef Smash", "cost": 899},
        {"name": "Texas Flamin Hot Beef Smash", "cost": 899},
        {"name": "Paris Truffle Beef Smash", "cost": 899},

        # CHICKEN BURGERS
        {"name": "Bangkok Chipotle Chicken", "cost": 749},
        {"name": "Cairo Honey Mustard Chicken", "cost": 749},
        {"name": "Cheesy Mexico Chicken", "cost": 849},
        {"name": "Vegas Parm Chicken", "cost": 849},

        # PLAIN & MASALA FRIES
        {"name": "Plain Fries", "cost": 249},
        {"name": "Masala Fries", "cost": 249},

        # WINGS
        {"name": "Plain Wings (6 PCS)", "cost": 399},
        {"name": "Masala Wings (6 PCS)", "cost": 399},
        {"name": "BBQ Wings (6 PCS)", "cost": 499},
        {"name": "Cheese Wings (6 PCS)", "cost": 499},

        # NEW YORK FRIES
        {"name": "New York Fries - Classic", "cost": 749},
        {"name": "Bangkok Fries", "cost": 699},
        {"name": "Disco Fries", "cost": 699},
        {"name": "Lahori Fries", "cost": 599},

        # DRINKS
        {"name": "Mint Margarita", "cost": 399},
        {"name": "Fresh Lemonade", "cost": 199},
        {"name": "Iced Milo", "cost": 499},

        # SOFT DRINK
        {"name": "Soft Drink - Cola", "cost": 149},
        {"name": "Soft Drink - White Soda", "cost": 149},
        {"name": "Soft Drink - Cola Zero", "cost": 149},
        {"name": "Soft Drink - White Soda Zero", "cost": 149},
        {"name": "Soft Drink - Orange Soda", "cost": 149},

        # MEALS (Add-ons for burgers)
        {"name": "Meal Upgrade (Fries + Soda)", "cost": 249},
        {"name": "Meal Upgrade (Fries + Mint Margarita)", "cost": 249},
        {"name": "Meal Upgrade (Fries + Fizzs Drinks)", "cost": 449},

        # ADD-ONS
        {"name": "Extra Beef Patty (110g)", "cost": 249},
        {"name": "Extra Crispy Chicken Fillet", "cost": 199},
        {"name": "Extra Grilled Fillet", "cost": 199},
        {"name": "Extra Crumbed Fillet", "cost": 199},
        {"name": "Extra Cheese Slice", "cost": 99},
    ]

    print("Seeding Smash Burger Menu...")
    for item in smash_burger_items:
        # We append these to the existing menu
        obj, created = Menu.objects.get_or_create(
            name=item['name'],
            defaults={'cost': item['cost']}
        )
        if created:
            print(f"Added: {item['name']} - {item['cost']} PKR")
        else:
            if obj.cost != item['cost']:
                obj.cost = item['cost']
                obj.save()
                print(f"Updated: {item['name']} - {item['cost']} PKR")
            else:
                print(f"Skipped (exists): {item['name']}")

    print("Smash Burger menu seeding completed.")

if __name__ == "__main__":
    seed_menu()
