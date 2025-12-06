#!/usr/bin/env python3
"""
MCPizza Demo - No Real API Calls
Demonstrates the MCPizza functionality without placing real orders
"""

import asyncio
from typing import Any


class MockStore:
    """Mock Domino's store for demo purposes"""

    def __init__(self, store_id: str):
        self.id = store_id
        self.phone = "(555) 123-4567"
        self.address = "123 Pizza St, Anytown, ST 12345"

    def __str__(self):
        return self.address

    def get_menu(self):
        return MockMenu()


class MockMenu:
    """Mock menu for demo purposes"""

    def __init__(self):
        self.products = {
            "14SCREEN": MockProduct("Large (14\") Hand Tossed Pizza", "Pizza"),
            "P14IPAZA": MockProduct("Large (14\") Pan Pizza", "Pizza"),
            "W08PBNW": MockProduct("Hot Buffalo Wings", "Wings"),
            "W08PHOTW": MockProduct("Hot Wings", "Wings"),
            "B8PCSCB": MockProduct("Stuffed Cheesy Bread", "Sides"),
            "MARBRWNE": MockProduct("Marbled Cookie Brownie", "Desserts"),
            "20BCOKE": MockProduct("Coca-Cola (20oz)", "Drinks"),
        }


class MockProduct:
    """Mock menu product"""

    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category


class MockAddress:
    """Mock address for store lookup"""

    def __init__(self, query: str):
        self.query = query

    def closest_store(self):
        """Return mock stores"""
        return [
            MockStore("4336"),
            MockStore("4337"),
            MockStore("4338")
        ]


class MockCustomer:
    """Mock customer"""

    def __init__(self, first_name: str, last_name: str, email: str, phone: str, address: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.address = address


class MockOrder:
    """Mock order for demo"""

    def __init__(self, store: MockStore, customer: MockCustomer, address: str):
        self.store = store
        self.customer = customer
        self.address = address
        self.data = {
            "Products": [],
            "Amounts": {
                "Customer": 0.0,
                "Tax": 0.0,
                "Delivery": 3.99,
                "Payment": 3.99
            }
        }
        self.items = []

    def add_item(self, item_code: str):
        """Add item to order"""
        # Mock pricing
        prices = {
            "14SCREEN": 12.99,
            "P14IPAZA": 13.99,
            "W08PBNW": 8.99,
            "W08PHOTW": 8.99,
            "B8PCSCB": 6.99,
            "MARBRWNE": 5.99,
            "20BCOKE": 2.49
        }

        price = prices.get(item_code, 9.99)

        product = {
            "Code": item_code,
            "Name": f"Item {item_code}",
            "Qty": 1,
            "Price": price
        }

        self.data["Products"].append(product)
        self.items.append(item_code)

        # Update totals
        subtotal = sum(p["Price"] for p in self.data["Products"])
        tax = subtotal * 0.08  # 8% tax
        total = subtotal + tax + self.data["Amounts"]["Delivery"]

        self.data["Amounts"]["Customer"] = subtotal
        self.data["Amounts"]["Tax"] = tax
        self.data["Amounts"]["Payment"] = total


async def demo_find_stores():
    """Demo: Find stores"""
    print("\n" + "=" * 60)
    print("🔍 DEMO: Finding Stores")
    print("=" * 60)

    address = MockAddress("90210")
    stores = address.closest_store()

    print(f"\nFound {len(stores)} stores near 90210:\n")
    for i, store in enumerate(stores, 1):
        print(f"{i}. Store #{store.id}")
        print(f"   Address: {store}")
        print(f"   Phone: {store.phone}\n")


async def demo_browse_menu():
    """Demo: Browse menu"""
    print("\n" + "=" * 60)
    print("📋 DEMO: Browsing Menu")
    print("=" * 60)

    store = MockStore("4336")
    menu = store.get_menu()

    print(f"\nMenu for Store #{store.id}:\n")

    categories = {}
    for code, product in menu.products.items():
        if product.category not in categories:
            categories[product.category] = []
        categories[product.category].append(f"{code}: {product.name}")

    for category, items in sorted(categories.items()):
        print(f"## {category}")
        for item in items:
            print(f"  - {item}")
        print()


async def demo_create_order():
    """Demo: Create and manage an order"""
    print("\n" + "=" * 60)
    print("🛒 DEMO: Creating and Managing Order")
    print("=" * 60)

    # Create customer
    customer = MockCustomer(
        "John",
        "Doe",
        "john.doe@example.com",
        "555-123-4567",
        "123 Main St"
    )

    print("\n✅ Customer created:")
    print(f"   Name: {customer.first_name} {customer.last_name}")
    print(f"   Email: {customer.email}")
    print(f"   Phone: {customer.phone}")
    print(f"   Address: {customer.address}")

    # Create order
    store = MockStore("4336")
    order = MockOrder(store, customer, customer.address)

    print(f"\n✅ Order created for Store #{store.id}")
    print(f"   Type: Delivery")
    print(f"   Address: {order.address}")

    # Add items
    print("\n📦 Adding items to order...")

    items_to_add = [
        ("14SCREEN", "Large Hand Tossed Pizza"),
        ("W08PBNW", "Hot Buffalo Wings"),
        ("20BCOKE", "Coca-Cola")
    ]

    for item_code, item_name in items_to_add:
        order.add_item(item_code)
        print(f"   ✅ Added: {item_name}")

    # Display order
    print("\n🛒 Current Order:")
    print(f"\n   Items:")
    for product in order.data["Products"]:
        print(f"   - {product['Qty']}x {product['Name']} (${product['Price']:.2f})")

    amounts = order.data["Amounts"]
    print(f"\n   Subtotal: ${amounts['Customer']:.2f}")
    print(f"   Tax: ${amounts['Tax']:.2f}")
    print(f"   Delivery: ${amounts['Delivery']:.2f}")
    print(f"   Total: ${amounts['Payment']:.2f}")

    print("\n   ⚠️  This is a PREVIEW ONLY")
    print("   ⚠️  Real order placement is DISABLED for safety")


async def demo_menu_search():
    """Demo: Search menu items"""
    print("\n" + "=" * 60)
    print("🔎 DEMO: Searching Menu")
    print("=" * 60)

    store = MockStore("4336")
    menu = store.get_menu()

    # Search for pizza
    print("\nSearching for 'Pizza':")
    pizza_items = [
        f"{code}: {product.name}"
        for code, product in menu.products.items()
        if product.category == "Pizza"
    ]
    for item in pizza_items:
        print(f"  - {item}")

    # Search for wings
    print("\nSearching for 'Wings':")
    wing_items = [
        f"{code}: {product.name}"
        for code, product in menu.products.items()
        if product.category == "Wings"
    ]
    for item in wing_items:
        print(f"  - {item}")


async def main():
    """Run all demos"""
    print("\n" + "🍕" * 30)
    print(" " * 20 + "MCPizza Demo")
    print(" " * 10 + "AI-Powered Pizza Ordering with MCP")
    print("🍕" * 30)

    print("\n⚠️  EDUCATIONAL DEMO ONLY")
    print("⚠️  No real API calls or orders will be placed")
    print("⚠️  This demonstrates the MCPizza functionality safely")

    await demo_find_stores()
    await demo_browse_menu()
    await demo_menu_search()
    await demo_create_order()

    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("\nTo use MCPizza with Claude:")
    print("1. Install dependencies: uv pip install pizzapi requests pydantic mcp")
    print("2. Add MCPizza to your Claude Desktop config")
    print("3. Ask Claude to help you order pizza!")
    print("\n⚠️  Remember: Real orders require explicit confirmation")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
