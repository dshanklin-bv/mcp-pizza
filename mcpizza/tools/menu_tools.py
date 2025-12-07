"""
MCP tool handlers for menu operations
"""
from mcp.types import TextContent
from mcpizza.models.params import StoreInfoParams, MenuSearchParams
from mcpizza.services import store_service, guidance_service


async def handle_get_menu(params: StoreInfoParams) -> list[TextContent]:
    """Get full menu for a store"""
    try:
        menu = store_service.get_menu(params.store_id)

        result = f"📋 Menu for Store #{params.store_id}:\n\n"

        for category, items in menu.items():
            result += f"## {category}\n"
            for item in items[:10]:  # Limit items per category
                result += f"- **{item['name']}** ({item['code']})\n"
                if item['description']:
                    result += f"  {item['description']}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting menu: {str(e)}"
        )]


async def handle_search_menu(params: MenuSearchParams) -> list[TextContent]:
    """Search menu items"""
    try:
        items = store_service.search_menu(
            params.store_id,
            params.query,
            params.category
        )

        if not items:
            return [TextContent(
                type="text",
                text="No matching items found"
            )]

        result = f"🔍 Found {len(items)} item(s):\n\n"
        for item in items[:20]:  # Limit results
            result += f"**{item['name']}** ({item['code']})\n"
            result += f"  Category: {item['category']}\n"
            if item['description']:
                result += f"  {item['description']}\n"
            result += "\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error searching menu: {str(e)}"
        )]


async def handle_get_coupons(params: StoreInfoParams) -> list[TextContent]:
    """Get available coupons"""
    try:
        coupons = store_service.get_coupons(params.store_id)

        if not coupons:
            return [TextContent(
                type="text",
                text=f"No coupons found for store #{params.store_id}"
            )]

        result = f"🎉 Available Deals & Coupons for Store #{params.store_id}:\n\n"

        for coupon in coupons[:20]:  # Limit to 20
            result += f"**Code: {coupon['code']}**\n"
            result += f"  {coupon['name']}\n"

            if coupon['price'] != 999.99:
                result += f"  💰 Price: ${coupon['price']}\n"
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
