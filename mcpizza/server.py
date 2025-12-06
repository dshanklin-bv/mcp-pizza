#!/usr/bin/env python3
"""
MCPizza MCP Server
AI-Powered Pizza Ordering with Model Context Protocol
"""

import json
import asyncio
from typing import Any, Optional
from pydantic import BaseModel, Field

try:
    from pizzapi import Store, Address, Customer, Order
    from pizzapi.menu import Menu
except ImportError:
    print("Warning: pizzapi not installed. Run: uv pip install pizzapi")
    Store = None
    Address = None
    Customer = None
    Order = None
    Menu = None

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from mcpizza.logger import interaction_logger

# Global state for current order
current_order: Optional[Any] = None
current_store: Optional[Any] = None
current_customer: Optional[Any] = None

# Initialize MCP server
app = Server("mcpizza")


class StoreSearchParams(BaseModel):
    """Parameters for finding stores"""
    query: str = Field(description="Address or zip code to search for stores")


class StoreInfoParams(BaseModel):
    """Parameters for getting store information"""
    store_id: str = Field(description="Store ID to get information for")


class MenuSearchParams(BaseModel):
    """Parameters for searching menu items"""
    store_id: str = Field(description="Store ID to search menu for")
    query: Optional[str] = Field(default=None, description="Search query (optional)")
    category: Optional[str] = Field(default=None, description="Category filter (e.g., 'Pizza', 'Wings', 'Sides')")


class CreateOrderParams(BaseModel):
    """Parameters for creating an order"""
    store_id: str = Field(description="Store ID to order from")
    customer_name: str = Field(description="Customer first and last name")
    customer_email: str = Field(description="Customer email address")
    customer_phone: str = Field(description="Customer phone number")
    delivery_address: str = Field(description="Delivery street address")
    delivery_city: str = Field(description="Delivery city")
    delivery_state: str = Field(description="Delivery state (2-letter code)")
    delivery_zip: str = Field(description="Delivery zip code")
    order_type: str = Field(default="Delivery", description="Order type: 'Delivery' or 'Carryout'")


class AddItemParams(BaseModel):
    """Parameters for adding an item to order"""
    item_code: str = Field(description="Menu item code")
    quantity: int = Field(default=1, description="Quantity to add")
    options: Optional[dict] = Field(default=None, description="Item customization options")


class AddPizzaParams(BaseModel):
    """Parameters for adding a customized pizza"""
    coupon_code: str = Field(description="Coupon code (e.g., '9204')")
    size: str = Field(default="12", description="Pizza size: 10, 12, 14, 16")
    crust: str = Field(default="NPAN", description="Crust type: NPAN (pan), HAND (hand tossed), THIN, etc.")
    toppings: list[str] = Field(description="List of topping codes (e.g., ['P', 'S'] for pepperoni and sausage)")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available pizza ordering tools"""
    interaction_logger.log_tool_list_request()
    return [
        Tool(
            name="find_stores",
            description="Find nearby Domino's stores by address or zip code. Returns store IDs, addresses, and phone numbers.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Address or zip code to search for stores"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_store_info",
            description="Get detailed information about a specific Domino's store including hours and services.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to get information for"
                    }
                },
                "required": ["store_id"]
            }
        ),
        Tool(
            name="get_menu",
            description="Get the full menu for a specific store. Returns all available items organized by category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to get menu for"
                    }
                },
                "required": ["store_id"]
            }
        ),
        Tool(
            name="search_menu",
            description="Search for specific menu items at a store. Can filter by category and search term.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to search menu for"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category filter: Pizza, Wings, Sides, Drinks, Desserts, etc."
                    }
                },
                "required": ["store_id"]
            }
        ),
        Tool(
            name="create_order",
            description="Create a new order for delivery or carryout. Required before adding items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {"type": "string", "description": "Store ID"},
                    "customer_name": {"type": "string", "description": "Customer full name"},
                    "customer_email": {"type": "string", "description": "Customer email"},
                    "customer_phone": {"type": "string", "description": "Customer phone number"},
                    "delivery_address": {"type": "string", "description": "Street address"},
                    "delivery_city": {"type": "string", "description": "City"},
                    "delivery_state": {"type": "string", "description": "State (2-letter code)"},
                    "delivery_zip": {"type": "string", "description": "Zip code"},
                    "order_type": {"type": "string", "description": "Delivery or Carryout", "default": "Delivery"}
                },
                "required": ["store_id", "customer_name", "customer_email", "customer_phone",
                           "delivery_address", "delivery_city", "delivery_state", "delivery_zip"]
            }
        ),
        Tool(
            name="add_item_to_order",
            description="Add a menu item to the current order. Must create an order first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_code": {
                        "type": "string",
                        "description": "Menu item code from the menu"
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity to add",
                        "default": 1
                    },
                    "options": {
                        "type": "object",
                        "description": "Item customization options"
                    }
                },
                "required": ["item_code"]
            }
        ),
        Tool(
            name="add_pizza_with_toppings",
            description="Add a customized pizza with toppings using a coupon code. Handles proper product + topping configuration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "coupon_code": {
                        "type": "string",
                        "description": "Coupon code (e.g., '9204')"
                    },
                    "size": {
                        "type": "string",
                        "description": "Pizza size code: 10, 12, 14, or 16",
                        "default": "12"
                    },
                    "crust": {
                        "type": "string",
                        "description": "Crust code: NPAN (pan), HAND (hand tossed), THIN, BROOKLYN, etc.",
                        "default": "NPAN"
                    },
                    "toppings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Topping codes: P (pepperoni), S (sausage), M (mushrooms), O (onions), etc."
                    }
                },
                "required": ["coupon_code", "toppings"]
            }
        ),
        Tool(
            name="view_order",
            description="View the current order including all items, prices, and totals.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="clear_order",
            description="Clear the current order and start over.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_coupons",
            description="Get available coupons and deals for a store. Returns coupon codes, descriptions, and prices.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to get coupons for"
                    }
                },
                "required": ["store_id"]
            }
        ),
        Tool(
            name="get_ordering_guidance",
            description="Get AI guidance on how to build the best order based on user preferences. Analyzes deals, suggests optimal pizza counts, and provides ordering strategy.",
            inputSchema={
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "Store ID to analyze deals for"
                    },
                    "user_request": {
                        "type": "string",
                        "description": "What the user wants (e.g., 'deep dish sausage and pepperoni', '2 large pizzas for a party')"
                    }
                },
                "required": ["store_id", "user_request"]
            }
        ),
        Tool(
            name="place_order",
            description="⚠️ PLACES A REAL ORDER with real payment! Submit the current order to Domino's. Requires payment information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "card_number": {
                        "type": "string",
                        "description": "Credit card number"
                    },
                    "card_expiry": {
                        "type": "string",
                        "description": "Card expiry (MM/YY)"
                    },
                    "card_cvv": {
                        "type": "string",
                        "description": "Card CVV"
                    },
                    "card_zip": {
                        "type": "string",
                        "description": "Billing zip code"
                    }
                },
                "required": ["card_number", "card_expiry", "card_cvv", "card_zip"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for pizza ordering"""

    # Log incoming tool call
    interaction_logger.log_tool_call(name, arguments)

    try:
        result = None

        if name == "find_stores":
            params = StoreSearchParams(**arguments)
            result = await find_stores(params.query)

        elif name == "get_store_info":
            params = StoreInfoParams(**arguments)
            result = await get_store_info(params.store_id)

        elif name == "get_menu":
            store_id = arguments.get("store_id")
            result = await get_menu(store_id)

        elif name == "search_menu":
            params = MenuSearchParams(**arguments)
            result = await search_menu(params.store_id, params.query, params.category)

        elif name == "create_order":
            params = CreateOrderParams(**arguments)
            result = await create_order(params)

        elif name == "add_item_to_order":
            params = AddItemParams(**arguments)
            result = await add_item_to_order(params)

        elif name == "add_pizza_with_toppings":
            params = AddPizzaParams(**arguments)
            result = await add_pizza_with_toppings(params)

        elif name == "view_order":
            result = await view_order()

        elif name == "clear_order":
            result = await clear_order()

        elif name == "get_coupons":
            store_id = arguments.get("store_id")
            result = await get_coupons(store_id)

        elif name == "get_ordering_guidance":
            store_id = arguments.get("store_id")
            user_request = arguments.get("user_request")
            result = await get_ordering_guidance(store_id, user_request)

        elif name == "place_order":
            result = await place_order(arguments)

        else:
            result = [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Log successful response
        interaction_logger.log_tool_response(name, True, result)
        return result

    except Exception as e:
        error_msg = str(e)
        result = [TextContent(type="text", text=f"Error: {error_msg}")]
        # Log error response
        interaction_logger.log_tool_response(name, False, None, error=error_msg)
        return result


async def find_stores(query: str) -> list[TextContent]:
    """Find stores by address or zip code"""
    try:
        if Address is None:
            return [TextContent(
                type="text",
                text="Error: pizzapi not installed. Run: uv pip install pizzapi"
            )]

        # Create address object
        # If query looks like a zip code (5 digits), use it as zip
        if query.strip().isdigit() and len(query.strip()) == 5:
            address = Address('', '', '', query.strip())
        else:
            # Try to parse as full address - this might still fail
            # For best results, users should provide: "street, city, state zip"
            parts = [p.strip() for p in query.split(',')]
            if len(parts) >= 2:
                street = parts[0]
                city = parts[1]
                region = parts[2] if len(parts) > 2 else ''
                zip_code = parts[3] if len(parts) > 3 else ''
                address = Address(street, city, region, zip_code)
            else:
                # Fallback: treat as city name
                address = Address('', query.strip(), '')

        # Find nearby stores
        stores = address.closest_store()

        if not stores:
            return [TextContent(
                type="text",
                text=f"No stores found near: {query}"
            )]

        # Format store information
        result = f"Found stores near {query}:\n\n"

        # Handle both single store and list of stores
        store_list = [stores] if not isinstance(stores, list) else stores

        for i, store in enumerate(store_list[:5], 1):  # Limit to top 5
            store_id = store.data.get('StoreID', 'Unknown')
            address_desc = store.data.get('AddressDescription', 'N/A').strip()
            phone = store.data.get('Phone', 'N/A')
            is_open = store.data.get('IsOpen', False)
            status = "🟢 Open" if is_open else "🔴 Closed"

            result += f"{i}. Store #{store_id} {status}\n"
            result += f"   Address: {address_desc}\n"
            result += f"   Phone: {phone}\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error finding stores: {str(e)}"
        )]


async def get_store_info(store_id: str) -> list[TextContent]:
    """Get detailed store information"""
    try:
        if Store is None:
            return [TextContent(
                type="text",
                text="Error: pizzapi not installed"
            )]

        # Get store data from API first
        import requests
        store_url = f"https://order.dominos.com/power/store/{store_id}"
        response = requests.get(store_url)
        store_data = response.json()

        result = f"Store #{store_id} Information:\n\n"
        result += f"Address: {store_data.get('AddressDescription', 'N/A')}\n"
        result += f"Phone: {store_data.get('Phone', 'N/A')}\n"
        result += f"Hours: {store_data.get('HoursDescription', 'N/A')}\n"
        result += f"Status: {'🟢 Open' if store_data.get('IsOpen') else '🔴 Closed'}\n"
        result += f"Online Ordering: {'✅' if store_data.get('IsOnlineNow') else '❌'}\n"
        result += f"Delivery: {'✅' if store_data.get('AllowDeliveryOrders') else '❌'}\n"
        result += f"Carryout: {'✅' if store_data.get('AllowCarryoutOrders') else '❌'}\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting store info: {str(e)}"
        )]


async def get_menu(store_id: str) -> list[TextContent]:
    """Get full menu for a store"""
    try:
        if Store is None:
            return [TextContent(type="text", text="Error: pizzapi not installed")]

        # Get store data from API first
        import requests
        store_url = f"https://order.dominos.com/power/store/{store_id}"
        response = requests.get(store_url)
        store_data = response.json()

        store = Store(store_data)

        # Try to get menu, but pizzapi has bugs with menu parsing
        try:
            menu = store.get_menu()
            result = f"Menu for Store #{store_id}:\n\n"

            # Get menu categories
            if hasattr(menu, 'products'):
                products = menu.products
            else:
                products = {}
        except Exception as menu_error:
            # Fallback: get raw menu data directly from API
            menu_url = f"https://order.dominos.com/power/store/{store_id}/menu?lang=en&structured=true"
            menu_response = requests.get(menu_url)
            menu_data = menu_response.json()

            result = f"Menu for Store #{store_id}:\n\n"
            products = menu_data.get('Products', {})

        if products:
            categories = {}

            for code, product in products.items():
                # Handle both dict and object-based products
                if isinstance(product, dict):
                    category = product.get('Name', 'Other')
                    name = product.get('Name', code)
                else:
                    category = getattr(product, 'category', 'Other')
                    name = getattr(product, 'name', code)

                if category not in categories:
                    categories[category] = []

                categories[category].append(f"{code}: {name}")

            for category, items in sorted(categories.items()):
                result += f"## {category}\n"
                for item in items[:10]:  # Limit items per category
                    result += f"  - {item}\n"
                result += "\n"
        else:
            result += "Menu format not recognized\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting menu: {str(e)}"
        )]


async def search_menu(store_id: str, query: Optional[str] = None,
                     category: Optional[str] = None) -> list[TextContent]:
    """Search menu items"""
    try:
        if Store is None:
            return [TextContent(type="text", text="Error: pizzapi not installed")]

        # Get store data from API first
        import requests
        store_url = f"https://order.dominos.com/power/store/{store_id}"
        response = requests.get(store_url)
        store_data = response.json()

        store = Store(store_data)

        # Try to get menu, but pizzapi has bugs with menu parsing
        try:
            menu = store.get_menu()
            products = menu.products if hasattr(menu, 'products') else {}
        except Exception:
            # Fallback: get raw menu data directly from API
            menu_url = f"https://order.dominos.com/power/store/{store_id}/menu?lang=en&structured=true"
            menu_response = requests.get(menu_url)
            menu_data = menu_response.json()
            products = menu_data.get('Products', {})

        results = []

        for code, product in products.items():
            # Handle both dict and object-based products
            if isinstance(product, dict):
                product_name = product.get('Name', code).lower()
                product_category = product.get('Tags', {}).get('Specialty', '')
            else:
                product_name = getattr(product, 'name', code).lower()
                product_category = getattr(product, 'category', '')

            # Filter by category if specified
            if category and category.lower() not in product_category.lower():
                continue

            # Filter by query if specified
            if query and query.lower() not in product_name:
                continue

            # Format the result
            if isinstance(product, dict):
                results.append(f"{code}: {product.get('Name', code)}")
            else:
                results.append(f"{code}: {getattr(product, 'name', code)} ({product_category})")

        if not results:
            return [TextContent(
                type="text",
                text=f"No items found matching: {query or 'all'} in category: {category or 'all'}"
            )]

        result_text = f"Found {len(results)} items:\n\n"
        result_text += "\n".join(results[:20])  # Limit to 20 results

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching menu: {str(e)}"
        )]


async def create_order(params: CreateOrderParams) -> list[TextContent]:
    """Create a new order"""
    global current_order, current_store, current_customer

    try:
        if Store is None or Customer is None or Order is None:
            return [TextContent(type="text", text="Error: pizzapi not installed")]

        # Create customer
        first_name, *last_name_parts = params.customer_name.split()
        last_name = " ".join(last_name_parts) if last_name_parts else ""

        customer = Customer(
            first_name,
            last_name,
            params.customer_email,
            params.customer_phone
        )

        # Create address object
        address = Address(
            params.delivery_address,
            params.delivery_city,
            params.delivery_state,
            params.delivery_zip
        )

        # Get store by finding closest one to the address
        # This ensures we have a properly initialized Store object
        all_stores = address.closest_store()

        # closest_store() can return a single store or a list
        if isinstance(all_stores, list):
            # Find the requested store in the list
            store = next((s for s in all_stores if s.id == params.store_id), all_stores[0])
        else:
            store = all_stores

        # Create order - wrap in try/except to catch menu parsing bugs
        try:
            order = Order(store, customer, address)
        except Exception as order_error:
            # If Order() fails due to menu parsing bug, create a mock order object
            # that has the essential attributes but skips menu loading
            import types
            order = types.SimpleNamespace()
            order.store = store
            order.customer = customer
            order.address = address
            order.data = {
                'Address': {
                    'Street': address.street,
                    'City': address.city,
                    'Region': address.region,
                    'PostalCode': address.zip,
                    'Type': 'House'
                },
                'Coupons': [],
                'CustomerID': '',
                'Extension': '',
                'OrderChannel': 'OLO',
                'OrderID': '',
                'NoCombine': True,
                'OrderMethod': 'Web',
                'OrderTaker': None,
                'Payments': [],
                'Products': [],
                'Market': '',
                'Currency': '',
                'ServiceMethod': params.order_type,
                'Tags': {},
                'Version': '1.0',
                'SourceOrganizationURI': 'order.dominos.com',
                'LanguageCode': 'en',
                'Partners': {},
                'NewUser': True,
                'metaData': {},
                'Amounts': {},
                'BusinessDate': '',
                'EstimatedWaitMinutes': '',
                'PriceOrderTime': '',
                'AmoundsBreakdown': {}
            }
            # Add a menu attribute that won't error
            order.menu = None

            # Add methods that the mock order needs
            def add_coupon(coupon_code):
                """Add coupon to order"""
                order.data['Coupons'].append({
                    'Code': coupon_code,
                    'Qty': 1,
                    'ID': len(order.data['Coupons']) + 1
                })

            def add_product(product_code, options=None):
                """Add product with toppings to order"""
                order.data['Products'].append({
                    'Code': product_code,
                    'Qty': 1,
                    'ID': len(order.data['Products']) + 1,
                    'isNew': True,
                    'Options': options or {}
                })

            def add_item(item_code, options=None):
                """Add item to mock order - handles both products and coupons"""
                # If it's a 4-digit code, it's likely a coupon
                # If it's longer with letters, it's likely a product code
                if item_code.isdigit() and len(item_code) == 4:
                    add_coupon(item_code)
                else:
                    add_product(item_code, options)

            order.add_coupon = add_coupon
            order.add_product = add_product

            def place():
                """Place order - makes real API call to Domino's"""
                import requests

                # Update order data with customer info
                order.data.update(
                    StoreID=store.id,
                    Email=customer.email,
                    FirstName=customer.first_name,
                    LastName=customer.last_name,
                    Phone=customer.phone
                )

                # Validate required fields
                for key in ('Products', 'StoreID', 'Address'):
                    if key not in order.data or not order.data[key]:
                        raise Exception(f'order has invalid value for key "{key}"')

                # Make the API call
                headers = {
                    'Referer': 'https://order.dominos.com/en/pages/order/',
                    'Content-Type': 'application/json'
                }

                url = 'https://order.dominos.com/power/place-order'
                r = requests.post(url=url, headers=headers, json={'Order': order.data})
                r.raise_for_status()
                return r.json()

            order.add_item = add_item
            order.place = place

        # Store globally
        old_order = current_order
        current_order = order
        current_store = store
        current_customer = customer

        # Log state change
        interaction_logger.log_state_change(
            "order_created",
            old_order,
            {
                "store_id": params.store_id,
                "customer": params.customer_name,
                "order_type": params.order_type
            }
        )

        return [TextContent(
            type="text",
            text=f"✅ Order created for {params.customer_name}\n"
                 f"Store: #{params.store_id}\n"
                 f"Type: {params.order_type}\n"
                 f"Address: {params.delivery_address}, {params.delivery_city}, {params.delivery_state} {params.delivery_zip}\n\n"
                 f"You can now add items with add_item_to_order."
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error creating order: {str(e)}"
        )]


async def add_item_to_order(params: AddItemParams) -> list[TextContent]:
    """Add item to current order"""
    global current_order

    try:
        if current_order is None:
            return [TextContent(
                type="text",
                text="❌ No active order. Create an order first with create_order."
            )]

        # Get current item count
        current_items = len(current_order.data.get('Products', []))

        # Add item to order
        current_order.add_item(params.item_code)

        # Log state change
        interaction_logger.log_state_change(
            "item_added",
            current_items,
            current_items + 1
        )

        return [TextContent(
            type="text",
            text=f"✅ Added {params.quantity}x {params.item_code} to order\n"
                 f"Use view_order to see the current order."
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error adding item: {str(e)}"
        )]


async def add_pizza_with_toppings(params: AddPizzaParams) -> list[TextContent]:
    """Add a customized pizza with toppings using a coupon"""
    global current_order

    try:
        if current_order is None:
            return [TextContent(
                type="text",
                text="❌ No active order. Create an order first with create_order."
            )]

        # Add the coupon
        current_order.add_coupon(params.coupon_code)

        # Build the pizza product code: P + size + I + crust
        # Example: P12IPAZA = Pizza, 12 inch, I (build your own), NPAN crust (becomes PAZA in code)
        crust_map = {
            "NPAN": "PAZA",  # Pan crust
            "HAND": "HAND",  # Hand tossed
            "THIN": "THIN",  # Thin crust
            "BROOKLYN": "BK",  # Brooklyn
        }
        crust_code = crust_map.get(params.crust, "PAZA")
        product_code = f"P{params.size}I{crust_code}"

        # Build topping options
        # Toppings format: {"X": {"1/1": "1"}} means whole pizza, single portion
        topping_options = {}
        for topping in params.toppings:
            topping_options[topping] = {"1/1": "1"}  # Whole pizza, normal amount

        # Add the pizza product
        current_order.add_product(product_code, topping_options)

        # Log state change
        interaction_logger.log_state_change(
            "pizza_added",
            len(current_order.data.get('Products', [])) - 1,
            len(current_order.data.get('Products', []))
        )

        topping_names = {
            "P": "Pepperoni",
            "S": "Sausage",
            "M": "Mushrooms",
            "O": "Onions",
            "B": "Beef",
            "K": "Bacon",
            "H": "Ham"
        }
        toppings_str = ", ".join([topping_names.get(t, t) for t in params.toppings])

        return [TextContent(
            type="text",
            text=f"✅ Added pizza to order:\n"
                 f"   Coupon: {params.coupon_code}\n"
                 f"   Size: {params.size}\"\n"
                 f"   Crust: {params.crust}\n"
                 f"   Toppings: {toppings_str}\n\n"
                 f"Use view_order to see the complete order."
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error adding pizza: {str(e)}"
        )]


async def view_order() -> list[TextContent]:
    """View current order details"""
    global current_order

    try:
        if current_order is None:
            return [TextContent(
                type="text",
                text="No active order. Create an order first with create_order."
            )]

        # Get order details
        result = "🛒 Current Order:\n\n"
        result += f"📍 Store: #{current_order.store.id}\n"
        result += f"👤 Customer: {current_order.customer.first_name} {current_order.customer.last_name}\n"
        result += f"📦 Type: {current_order.data.get('ServiceMethod', 'Unknown')}\n\n"

        if hasattr(current_order, 'data'):
            order_data = current_order.data

            # Show coupons
            if 'Coupons' in order_data and order_data['Coupons']:
                result += "Coupons:\n"
                for coupon in order_data['Coupons']:
                    code = coupon.get('Code', 'Unknown')
                    qty = coupon.get('Qty', 1)
                    result += f"  - {qty}x Coupon Code: {code}\n"

                    # Try to identify the coupon
                    if code == '9204':
                        result += f"    (Medium 2-Topping Handmade Pan Pizza - $10.99)\n"

                result += f"\nTotal Coupons: {len(order_data['Coupons'])}\n"

            # Show items
            if 'Products' in order_data and order_data['Products']:
                result += "\nProducts:\n"
                for product in order_data['Products']:
                    code = product.get('Code', 'Unknown')
                    qty = product.get('Qty', 1)
                    result += f"  - {qty}x Product Code: {code}\n"

                result += f"\nTotal Products: {len(order_data['Products'])}\n"

            if (not order_data.get('Coupons') and not order_data.get('Products')):
                result += "No items added yet.\n"

            result += "\n"

            # Show pricing if available
            if 'Amounts' in order_data and order_data['Amounts']:
                amounts = order_data['Amounts']
                if amounts:
                    result += f"Subtotal: ${amounts.get('Customer', 0):.2f}\n"
                    result += f"Tax: ${amounts.get('Tax', 0):.2f}\n"
                    result += f"Delivery: ${amounts.get('Delivery', 0):.2f}\n"
                    result += f"Total: ${amounts.get('Payment', 0):.2f}\n"
            else:
                result += "💡 Pricing will be calculated when order is validated.\n"
        else:
            result += "Order is empty\n"

        result += "\n💡 Ready to place this order! Use the Domino's API to submit it."

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error viewing order: {str(e)}"
        )]


async def clear_order() -> list[TextContent]:
    """Clear the current order"""
    global current_order, current_store, current_customer

    old_order = current_order
    current_order = None
    current_store = None
    current_customer = None

    # Log state change
    interaction_logger.log_state_change(
        "order_cleared",
        old_order,
        None
    )

    return [TextContent(
        type="text",
        text="✅ Order cleared. Create a new order with create_order."
    )]


async def get_coupons(store_id: str) -> list[TextContent]:
    """Get available coupons and deals for a store"""
    try:
        import requests

        # Get menu with coupons from API
        menu_url = f"https://order.dominos.com/power/store/{store_id}/menu?lang=en&structured=true"
        response = requests.get(menu_url)
        menu_data = response.json()

        coupons = menu_data.get('Coupons', {})

        if not coupons:
            return [TextContent(
                type="text",
                text=f"No coupons found for store #{store_id}"
            )]

        result = f"🎉 Available Deals & Coupons for Store #{store_id}:\n\n"

        # Sort by price to show best deals first
        sorted_coupons = sorted(
            coupons.items(),
            key=lambda x: float(x[1].get('Price', 999)) if x[1].get('Price') else 999
        )

        for code, coupon in sorted_coupons[:20]:  # Limit to 20 coupons
            name = coupon.get('Name', 'Unknown')
            price = coupon.get('Price')

            result += f"**Code: {code}**\n"
            result += f"  {name}\n"

            if price:
                result += f"  💰 Price: ${price}\n"
            else:
                result += f"  💰 Price: Varies (% off or minimum purchase)\n"

            result += "\n"

        result += "\n💡 Tip: Use these coupon codes when adding items to your order!"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting coupons: {str(e)}"
        )]


async def get_ordering_guidance(store_id: str, user_request: str) -> list[TextContent]:
    """Provide AI guidance on building the best order"""
    try:
        import requests

        # Get menu with coupons from API
        menu_url = f"https://order.dominos.com/power/store/{store_id}/menu?lang=en&structured=true"
        response = requests.get(menu_url)
        menu_data = response.json()

        coupons = menu_data.get('Coupons', {})

        # Analyze the user request
        request_lower = user_request.lower()

        result = f"🎯 ORDERING GUIDANCE\n"
        result += f"User wants: {user_request}\n\n"

        result += "📊 ANALYSIS & RECOMMENDATIONS:\n\n"

        # Analyze deal structure
        result += "## Deal Analysis\n\n"

        # Find multi-pizza deals
        multi_pizza_deals = []
        single_pizza_deals = []
        percentage_deals = []

        for code, coupon in coupons.items():
            name = coupon.get('Name', '').lower()
            price = coupon.get('Price')

            if '2 or more' in name or 'two or more' in name:
                multi_pizza_deals.append((code, coupon.get('Name'), price))
            elif 'medium' in name and price and 'pizza' in name:
                single_pizza_deals.append(('medium', code, coupon.get('Name'), price))
            elif 'large' in name and price and 'pizza' in name:
                single_pizza_deals.append(('large', code, coupon.get('Name'), price))
            elif '%' in name or 'percent' in name:
                percentage_deals.append((code, coupon.get('Name')))

        # Strategy recommendations
        result += "### Best Value Strategies:\n\n"

        if multi_pizza_deals:
            result += "**🎉 Multi-Pizza Deals (Best for 2+ pizzas):**\n"
            for code, name, price in sorted(multi_pizza_deals, key=lambda x: float(x[2]) if x[2] else 999)[:3]:
                result += f"- Code {code}: {name}"
                if price:
                    result += f" (${price} each)"
                result += "\n"
            result += "\n"

        if single_pizza_deals:
            result += "**🍕 Single Pizza Deals:**\n"
            # Group by size
            mediums = [d for d in single_pizza_deals if d[0] == 'medium']
            larges = [d for d in single_pizza_deals if d[0] == 'large']

            if mediums:
                best_medium = min(mediums, key=lambda x: float(x[3]) if x[3] else 999)
                result += f"- Best Medium: Code {best_medium[1]} - ${best_medium[3]}\n"

            if larges:
                best_large = min(larges, key=lambda x: float(x[3]) if x[3] else 999)
                result += f"- Best Large: Code {best_large[1]} - ${best_large[3]}\n"

            result += "\n"

        if percentage_deals:
            result += "**💰 Percentage Discounts:**\n"
            for code, name in percentage_deals[:2]:
                result += f"- Code {code}: {name}\n"
            result += "\n"

        # Specific recommendation based on request
        result += "## Recommended Approach:\n\n"

        # Parse quantity from request
        has_multiple = any(word in request_lower for word in ['2', 'two', 'three', '3', 'four', '4', 'party', 'group', 'family'])

        if has_multiple and multi_pizza_deals:
            best_deal = min(multi_pizza_deals, key=lambda x: float(x[2]) if x[2] else 999)
            result += f"✅ Since you need multiple pizzas, use **Code {best_deal[0]}**\n"
            result += f"   {best_deal[1]}\n"
            if best_deal[2]:
                result += f"   ${best_deal[2]} per pizza\n"
            result += "\n"
        else:
            # Single pizza recommendation
            size_pref = 'medium' if 'medium' in request_lower else 'large' if 'large' in request_lower else 'medium'
            matching_deals = [d for d in single_pizza_deals if d[0] == size_pref]

            if matching_deals:
                best_deal = min(matching_deals, key=lambda x: float(x[3]) if x[3] else 999)
                result += f"✅ For one {size_pref} pizza, use **Code {best_deal[1]}**\n"
                result += f"   {best_deal[2]}\n"
                result += f"   ${best_deal[3]}\n\n"

        # Toppings guidance
        if 'topping' in request_lower or 'sausage' in request_lower or 'pepperoni' in request_lower:
            result += "## Topping Strategy:\n\n"
            result += "- Look for '2-topping' or '3-topping' deals for custom pizzas\n"
            result += "- Specialty pizzas have fixed toppings but may save money\n"
            result += "- Deep dish may require specific crust selection when building\n\n"

        # Order building steps
        result += "## Next Steps:\n\n"
        result += "1. Create an order with customer details (create_order)\n"
        result += "2. Use add_pizza_with_toppings with the recommended coupon code:\n"
        result += "   - coupon_code: (recommended code from above)\n"
        result += "   - size: 12 (for medium) or 14 (for large)\n"
        result += "   - crust: NPAN (pan/deep dish), HAND (hand tossed), THIN, etc.\n"
        result += "   - toppings: ['P', 'S'] for pepperoni and sausage\n"
        result += "3. View order to verify (view_order)\n"
        result += "4. Place order with payment (place_order)\n\n"

        result += "💡 Pro Tips:\n"
        result += "- Multi-pizza deals almost always beat single pizza pricing!\n"
        result += "- Use add_pizza_with_toppings (not add_item_to_order) for custom pizzas\n"
        result += "- Deep dish = NPAN crust code"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting ordering guidance: {str(e)}"
        )]


async def place_order(payment_info: dict) -> list[TextContent]:
    """⚠️ PLACE A REAL ORDER - This charges a real credit card!"""
    global current_order

    try:
        if current_order is None:
            return [TextContent(
                type="text",
                text="❌ No active order. Create an order first."
            )]

        import requests

        result_text = "🚀 ATTEMPTING TO PLACE REAL ORDER...\n\n"

        # Step 1: Price the order (validate and get totals)
        try:
            result_text += "📊 Step 1: Validating and pricing order...\n"

            # Update order data with customer info
            current_order.data.update(
                StoreID=current_order.store.id,
                Email=current_order.customer.email,
                FirstName=current_order.customer.first_name,
                LastName=current_order.customer.last_name,
                Phone=current_order.customer.phone
            )

            headers = {
                'Referer': 'https://order.dominos.com/en/pages/order/',
                'Content-Type': 'application/json'
            }

            price_url = 'https://order.dominos.com/power/price-order'
            price_response = requests.post(
                url=price_url,
                headers=headers,
                json={'Order': current_order.data}
            )
            price_response.raise_for_status()
            price_data = price_response.json()

            if price_data.get('Status') == -1:
                result_text += f"❌ Pricing failed: {price_data}\n"
                return [TextContent(type="text", text=result_text)]

            # Update order with pricing info
            for key, value in price_data.get('Order', {}).items():
                if value or not isinstance(value, list):
                    current_order.data[key] = value

            result_text += "✅ Order validated and priced\n"
            amounts = current_order.data.get('Amounts', {})
            result_text += f"   Subtotal: ${amounts.get('Customer', 0):.2f}\n\n"

        except Exception as price_error:
            result_text += f"❌ Pricing failed: {str(price_error)}\n"
            return [TextContent(type="text", text=result_text)]

        # Step 2: Add payment information
        result_text += "💳 Step 2: Adding payment information...\n"

        current_order.data['Payments'] = [{
            'Type': 'CreditCard',
            'Number': payment_info.get('card_number'),
            'Expiration': payment_info.get('card_expiry'),
            'Amount': current_order.data['Amounts'].get('Customer', 0),
            'CardType': 'AMEX' if payment_info.get('card_number', '').startswith('3') else 'Visa',
            'SecurityCode': payment_info.get('card_cvv'),
            'PostalCode': payment_info.get('card_zip')
        }]

        result_text += "✅ Payment added\n\n"

        # Step 3: Place the order
        try:
            result_text += "🍕 Step 3: Submitting order to Domino's...\n"

            place_url = 'https://order.dominos.com/power/place-order'
            place_response = requests.post(
                url=place_url,
                headers=headers,
                json={'Order': current_order.data}
            )
            place_response.raise_for_status()
            response = place_response.json()

            # Check if order was actually successful
            if response.get('Status') == -1:
                result_text += "❌ ORDER REJECTED BY DOMINO'S\n\n"
                result_text += f"Status: {response.get('Status')}\n"
                status_items = response.get('Order', {}).get('StatusItems', [])
                if status_items:
                    result_text += "Issues:\n"
                    for item in status_items:
                        result_text += f"  - {item.get('Code', 'Unknown')}: {item.get('PulseText', '')}\n"
                result_text += "\nThe order was not placed. Please check the issues above.\n"
            else:
                result_text += "✅ ORDER PLACED SUCCESSFULLY!\n\n"
                result_text += f"Order ID: {response.get('Order', {}).get('OrderID', 'Unknown')}\n"
                result_text += f"Status: {response.get('Status', 'Unknown')}\n"
                result_text += f"Estimated Wait: {response.get('Order', {}).get('EstimatedWaitMinutes', 'Unknown')} minutes\n\n"
                result_text += "🍕 Your pizza is on the way! Check your email for confirmation.\n"

            return [TextContent(type="text", text=result_text)]

        except Exception as place_error:
            result_text += f"❌ ORDER FAILED: {str(place_error)}\n\n"
            result_text += "This could be due to:\n"
            result_text += "- Invalid payment information\n"
            result_text += "- Store not accepting online orders\n"
            result_text += "- Invalid items in order\n"
            result_text += "- API limitations\n"

            return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error placing order: {str(e)}"
        )]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
