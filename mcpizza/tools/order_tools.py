"""
MCP tool handlers for order operations
"""
from mcp.types import TextContent
from mcpizza.models.params import CreateOrderParams, AddItemParams, AddPizzaParams
from mcpizza.services import order_service, payment_service
from mcpizza.logger import interaction_logger


async def handle_create_order(params: CreateOrderParams) -> list[TextContent]:
    """Create a new order"""
    try:
        result = order_service.create_order(
            params.store_id,
            params.customer_name,
            params.customer_email,
            params.customer_phone,
            params.delivery_address,
            params.delivery_city,
            params.delivery_state,
            params.delivery_zip,
            params.order_type
        )

        interaction_logger.log_state_change("order_created", None, result)

        text = "✅ Order Created!\n\n"
        text += f"Customer: {params.customer_name}\n"
        text += f"Store: #{params.store_id}\n"
        text += f"Type: {params.order_type}\n\n"
        text += "📝 Next steps:\n"
        text += "1. Add items with add_item_to_order or add_pizza_with_toppings\n"
        text += "2. View order with view_order\n"
        text += "3. Place order with place_order"

        return [TextContent(type="text", text=text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error creating order: {str(e)}"
        )]


async def handle_add_item_to_order(params: AddItemParams) -> list[TextContent]:
    """Add item to order"""
    try:
        result = order_service.add_item_to_order(
            params.item_code,
            params.quantity,
            params.options
        )

        interaction_logger.log_state_change("item_added", None, params.item_code)

        return [TextContent(
            type="text",
            text=f"✅ {result['message']}"
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error adding item: {str(e)}"
        )]


async def handle_add_pizza_with_toppings(params: AddPizzaParams) -> list[TextContent]:
    """Add customized pizza with toppings"""
    try:
        result = order_service.add_pizza_with_toppings(
            params.coupon_code,
            params.size,
            params.crust,
            params.toppings
        )

        interaction_logger.log_state_change("pizza_added", None, result)

        return [TextContent(
            type="text",
            text=f"✅ {result['message']}"
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error adding pizza: {str(e)}"
        )]


async def handle_view_order() -> list[TextContent]:
    """View current order"""
    try:
        order = order_service.view_order()

        result = "📋 CURRENT ORDER:\n\n"
        result += f"Store: #{order['store_id']}\n"
        result += f"Customer: {order['customer']['name']}\n"
        result += f"Service: {order['service_method']}\n\n"

        result += "🎉 Coupons:\n"
        if order['coupons']:
            for coupon in order['coupons']:
                result += f"  - {coupon.get('Code', 'N/A')}\n"
        else:
            result += "  (none)\n"

        result += "\n🍕 Products:\n"
        if order['products']:
            for product in order['products']:
                result += f"  - {product.get('Code', 'N/A')}\n"
                if product.get('Options'):
                    result += f"    Toppings: {', '.join(product['Options'].keys())}\n"
        else:
            result += "  (none)\n"

        result += "\n💰 Pricing:\n"
        amounts = order['amounts']
        if amounts:
            result += f"  Total: ${amounts.get('Customer', 0):.2f}\n"
        else:
            result += "  (not priced yet - will be calculated at checkout)\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error viewing order: {str(e)}"
        )]


async def handle_clear_order() -> list[TextContent]:
    """Clear current order"""
    try:
        result = order_service.clear_order()

        interaction_logger.log_state_change("order_cleared", "active", None)

        return [TextContent(
            type="text",
            text=f"✅ {result['message']}"
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error clearing order: {str(e)}"
        )]


async def handle_place_order(payment_info: dict) -> list[TextContent]:
    """Place a real order with payment"""
    try:
        result = payment_service.place_order(payment_info)

        text = "🚀 ATTEMPTING TO PLACE REAL ORDER...\n\n"

        # Add steps
        for step in result.get('steps', []):
            text += f"📊 {step}\n"

        text += "\n"

        if result['success']:
            text += "✅ ORDER PLACED SUCCESSFULLY!\n\n"
            text += f"Order ID: {result.get('order_id', 'Unknown')}\n"
            text += f"Status: {result.get('status', 'Unknown')}\n"
            text += f"Estimated Wait: {result.get('estimated_wait_minutes', 'Unknown')} minutes\n\n"
            text += "🍕 Your pizza is on the way! Check your email for confirmation.\n"
        else:
            if result.get('rejected'):
                text += "❌ ORDER REJECTED BY DOMINO'S\n\n"
                text += f"Status: {result.get('status')}\n"
                status_items = result.get('status_items', [])
                if status_items:
                    text += "Issues:\n"
                    for item in status_items:
                        text += f"  - {item.get('Code', 'Unknown')}: {item.get('PulseText', '')}\n"
                text += "\nThe order was not placed. Please check the issues above.\n"
            else:
                text += f"❌ {result.get('error', 'Unknown error')}\n\n"
                if result.get('possible_causes'):
                    text += "Possible causes:\n"
                    for cause in result['possible_causes']:
                        text += f"  - {cause}\n"

        return [TextContent(type="text", text=text)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error placing order: {str(e)}"
        )]
