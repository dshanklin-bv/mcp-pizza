# 🍕 MCPizza

AI-Powered Pizza Ordering with Model Context Protocol

⚠️ **For educational purposes only. Real order placement is disabled by default for safety.**

## Features

- 📍 **Store Locator** - Find the nearest Domino's stores by address or zip code
- 📋 **Menu Browsing** - Search and browse complete menu categories
- 🛒 **Order Management** - Add items to cart, customize options, and calculate totals
- 👤 **Customer Info** - Handle delivery addresses and contact information
- 🔒 **Safe Preview** - Prepare and review orders without placing them
- 🤖 **MCP Integration** - Full Model Context Protocol support

## Built With

- **Python 3.9+** - Modern Python with full async support
- **Model Context Protocol** - Standardized AI assistant integration
- **Domino's API** - Unofficial API for pizza ordering (pizzapi)
- **Pydantic** - Data validation and serialization

## Quick Start

```bash
# Install uv package manager (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup environment
cd mcp-pizza
uv venv && source .venv/bin/activate

# Install dependencies
uv pip install pizzapi requests pydantic mcp

# Run demo
python mcpizza/demo_no_real_api.py
```

## MCP Server Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "pizza": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/mcp-pizza",
        "run",
        "mcpizza"
      ]
    }
  }
}
```

## Available Tools

### Store Locator
- `find_stores` - Find nearby Domino's locations by address or zip code
- `get_store_info` - Get detailed information about a specific store

### Menu Management
- `get_menu` - Get the full menu for a store
- `search_menu` - Search for specific items in the menu
- `get_item_details` - Get detailed information about a menu item

### Order Management
- `create_order` - Create a new order for delivery or carryout
- `add_item_to_order` - Add a menu item to the current order
- `view_order` - View current order details and pricing
- `clear_order` - Clear the current order

### Safety Features
- Order preview only (no actual order placement by default)
- Explicit confirmation required for any real orders
- Clear warnings about educational use

## Disclaimer

This project is for educational purposes only. Use responsibly and in accordance with Domino's terms of service. Real order placement functionality is disabled by default.

## License

MIT License - Use responsibly!
