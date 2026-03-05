import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kfc_api.settings')
django.setup()

from menu.models import Menu

def seed_menu():
    burger_menu_items = [
        # Burgers
        {"name": "OG Burger", "cost": 800},
        {"name": "OG Burger (Double)", "cost": 1090},
        {"name": "Jammy Jack", "cost": 800},
        {"name": "Jammy Jack (Double)", "cost": 1090},
        {"name": "Shroomster", "cost": 800},
        {"name": "Shroomster (Double)", "cost": 1090},
        {"name": "Mini TOT (Beef)", "cost": 1590},
        {"name": "Mini TOT (Chicken)", "cost": 1590},
        {"name": "Mini TOT (Heart-Heart)", "cost": 1590},

        # Shapack Sandos (Chicken Sandwiches)
        # {"name": "Dijon Don Sando", "cost": 990},
        # {"name": "Jojo Sando", "cost": 990},
        {"name": "Chitotley Sando", "cost": 1190},
        {"name": "Bacon Drip Sando", "cost": 1190},

        # Fries Selection
        {"name": "Fries (Plain / Masala)", "cost": 240},
        {"name": "Loaded Fries", "cost": 390},
        {"name": "Curly Fries", "cost": 390},
        {"name": "Waffle Fries", "cost": 390},
        {"name": "Potato Wedges", "cost": 390},
        {"name": "Long Bois Fries (Japanese-style)", "cost": 490},

        # Appetizers
        {"name": "Buffalo Wings", "cost": 690},
        {"name": "Classic Wings", "cost": 690},
        {"name": "Thai Sweet Chilli Wings", "cost": 690},
        {"name": "Chicken Tenders", "cost": 540},
        {"name": "Tender Platter", "cost": 1490},

        # Add-Ons Menu
        {"name": "Add-On: Jalapeño", "cost": 50},
        {"name": "Add-On: Mushroom", "cost": 50},
        {"name": "Add-On: Cheese Slice", "cost": 50},
        {"name": "Add-On: Pickle", "cost": 50},
        {"name": "Add-On: Lettuce", "cost": 50},
        {"name": "Add-On: Chicken Fillet", "cost": 290},
        {"name": "Add-On: Patty & Cheese", "cost": 290},
        {"name": "Add-On: Bacon Jam", "cost": 290},
        {"name": "Add-On: Onion Marmalade", "cost": 290},
        {"name": "Add-On: Turkey Bacon", "cost": 290},

        # Signature Sips
        {"name": "Blue Voltage", "cost": 350},
        {"name": "Sunset Passion", "cost": 350},
        {"name": "Kiwi Drift", "cost": 350},
        {"name": "Apple Volt", "cost": 350},
        {"name": "Berry Spritz", "cost": 350},

        # Regular Drinks
        {"name": "Coke", "cost": 150},
        {"name": "Sprite", "cost": 150},
        {"name": "Fanta", "cost": 150},
        {"name": "Diet Coke", "cost": 150},
        {"name": "Diet Sprite", "cost": 150},
        {"name": "Water", "cost": 50},

        # Desserts
        {"name": "Lotus Bar (Small)", "cost": 1090},
        {"name": "Lotus Bar (Large)", "cost": 1390},
        {"name": "Fudge Bar (Small)", "cost": 990},
        {"name": "Fudge Bar (Large)", "cost": 1890},

        # Special Shakes
        {"name": "Lotus Shake", "cost": 790},
        {"name": "Oreo Shake", "cost": 790},
        {"name": "Strawberry Berry Cheesecake Shake", "cost": 790},
        {"name": "Nutella Brownie Shake", "cost": 790},
        {"name": "Peanut Butter Shake", "cost": 790},
        {"name": "Hazelnut Frappe", "cost": 790},

        # Make It a Meal
        {"name": "Meal 01 (Fries + Regular Drink)", "cost": 290},
        {"name": "Meal 02 (Fries + Signature Sip)", "cost": 490},

        # Dips & Sauces
        {"name": "Dijon Sauce", "cost": 99},
        {"name": "Creamy Aioli", "cost": 99},
        {"name": "Jalapeño Sauce", "cost": 99},
        {"name": "Gangsta Sauce", "cost": 99},
        {"name": "Chipotle Sauce", "cost": 99},
    ]

    print("Clearing existing menu items...")
    Menu.objects.all().delete()

    print("Seeding New Burger Menu...")
    for item in burger_menu_items:
        # Check if item already exists (though we cleared them, good for robustness)
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
