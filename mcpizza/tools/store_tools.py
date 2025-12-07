"""
MCP tool handlers for store operations
"""
from mcp.types import TextContent
from mcpizza.models.params import StoreSearchParams, StoreInfoParams
from mcpizza.services import store_service
from mcpizza.logger import interaction_logger


async def handle_find_stores(params: StoreSearchParams) -> list[TextContent]:
    """Find nearby Domino's stores"""
    try:
        stores = store_service.find_stores(params.query)

        if not stores:
            return [TextContent(
                type="text",
                text=f"No stores found near '{params.query}'"
            )]

        result = f"🍕 Found {len(stores)} store(s) near '{params.query}':\n\n"
        for store in stores:
            status = "✅ OPEN" if store['is_open'] else "❌ CLOSED"
            result += f"**Store #{store['id']}** {status}\n"
            result += f"  📍 {store['address']}\n"
            result += f"  📞 {store['phone']}\n\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error finding stores: {str(e)}"
        )]


async def handle_get_store_info(params: StoreInfoParams) -> list[TextContent]:
    """Get detailed store information"""
    try:
        info = store_service.get_store_info(params.store_id)

        result = f"🏪 Store #{info['id']} Details:\n\n"
        result += f"📍 Address: {info['address']}\n"
        result += f"📞 Phone: {info['phone']}\n"
        result += f"🕐 Hours: {info['hours']}\n"
        result += f"Status: {'✅ OPEN' if info['is_open'] else '❌ CLOSED'}\n"
        result += f"Delivery: {'✅ Available' if info['is_delivery_store'] else '❌ Carryout only'}\n"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error getting store info: {str(e)}"
        )]
