"""
MCP tool handlers for ordering guidance
"""
from mcp.types import TextContent
from mcpizza.services import guidance_service


async def handle_get_ordering_guidance(store_id: str, user_request: str) -> list[TextContent]:
    """Get AI-powered ordering guidance"""
    try:
        guidance = guidance_service.get_ordering_guidance(store_id, user_request)

        result = "🎯 ORDERING GUIDANCE\n"
        result += f"User wants: {guidance['user_request']}\n\n"
        result += "📊 ANALYSIS & RECOMMENDATIONS:\n\n"

        # Show strategies
        for strategy in guidance['strategies']:
            result += f"## {strategy['title']}\n\n"
            for deal in strategy['deals']:
                result += f"- Code **{deal['code']}**: {deal['name']}"
                if 'price' in deal and deal['price'] != 999.99:
                    result += f" (${deal['price']})"
                result += "\n"
            result += "\n"

        # Show recommendation
        if guidance['recommended_code']:
            result += "## 🎯 RECOMMENDED ACTION\n\n"
            result += f"Best coupon code for your request: **{guidance['recommended_code']}**\n\n"
            result += "### How to Order:\n"
            result += "1. Use create_order to start your order\n"
            result += f"2. Use add_pizza_with_toppings with the recommended coupon code:\n"
            result += f"   - coupon_code: {guidance['recommended_code']}\n"
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
