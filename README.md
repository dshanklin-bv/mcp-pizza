# 🍕 MCPizza - Enhanced

An educational MCP (Model Context Protocol) server demonstrating AI-powered pizza ordering with Domino's API integration.

> **⚠️ Important**: This project is for **educational purposes only**. While it integrates with Domino's real API, actual order placement is blocked by CAPTCHA requirements. See [Limitations](#limitations) for details.

## Credits

This project is based on [GrahamMcBain/mcpizza](https://github.com/GrahamMcBain/mcpizza), with significant enhancements:

### Original Project
- **Author**: Graham McBain
- **Purpose**: Educational MCP protocol demonstration
- **Design**: Safe-mode ordering without real placement

### Our Enhancements
- ✅ **Real API Integration** - Actually calls Domino's pricing and validation APIs
- ✅ **Pizza Customization** - `add_pizza_with_toppings` tool for proper coupon + topping configuration
- ✅ **Interaction Logging** - Complete 2-way logging system for all MCP interactions
- ✅ **Coupon Discovery** - `get_coupons` and `get_ordering_guidance` tools
- ✅ **Enhanced Error Handling** - Detailed error reporting and validation
- ✅ **Comprehensive Documentation** - WORKFLOW.md with step-by-step instructions

## What This Project Demonstrates

1. **MCP Protocol Integration** - Full implementation of Model Context Protocol
2. **Real-world API Interaction** - Integration with Domino's unofficial API
3. **Complex Tool Orchestration** - 12 tools working together for multi-step workflows
4. **State Management** - Order state management across tool calls
5. **Error Handling** - Graceful handling of API validation and errors

## Features

### Store & Menu Tools
- 📍 `find_stores` - Find nearby Domino's by address or zip
- 🏪 `get_store_info` - Detailed store information and hours
- 📋 `get_menu` - Complete menu with categories
- 🔍 `search_menu` - Search for specific items
- 🎉 `get_coupons` - Discover available deals and coupons

### Ordering Tools
- 📝 `create_order` - Initialize a new order
- 🍕 `add_pizza_with_toppings` - Add customized pizzas with toppings (NEW!)
- ➕ `add_item_to_order` - Add any menu item
- 👁️ `view_order` - Preview order details and pricing
- 🗑️ `clear_order` - Clear current order
- 💳 `place_order` - Attempt to place order (blocked by CAPTCHA)

### Guidance Tools
- 🎯 `get_ordering_guidance` - AI-powered deal recommendations (NEW!)

## Installation

### Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/dshanklin-bv/mcp-pizza.git
cd mcp-pizza

# Install dependencies
uv pip install -e .
```

### Claude Desktop Integration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

## Usage

See [WORKFLOW.md](WORKFLOW.md) for complete ordering workflow documentation.

### Basic Example

```
1. Find stores: "find pizza stores near 76104"
2. Get coupons: "what deals are available at store 8022?"
3. Get guidance: "I want a deep dish sausage and pepperoni pizza"
4. Create order: Create order with your details
5. Add pizza: Use add_pizza_with_toppings with coupon code
6. View order: Review pricing and details
7. (Optional) Place order: Will be blocked by CAPTCHA
```

## Architecture

The codebase follows a clean, modular architecture with separation of concerns:

```
mcp-pizza/
├── mcpizza/
│   ├── server.py          # Main MCP server (303 lines, down from 1308!)
│   ├── logger.py          # Interaction logging system
│   ├── __main__.py        # Entry point
│   │
│   ├── models/            # Pydantic parameter models
│   │   └── params.py      # Tool parameter definitions
│   │
│   ├── services/          # Business logic layer
│   │   ├── store_service.py     # Store lookup & menu browsing
│   │   ├── order_service.py     # Order creation & management
│   │   ├── payment_service.py   # Payment processing
│   │   └── guidance_service.py  # AI ordering guidance
│   │
│   ├── tools/             # MCP tool handlers
│   │   ├── store_tools.py       # Store-related tools
│   │   ├── menu_tools.py        # Menu-related tools
│   │   ├── order_tools.py       # Order-related tools
│   │   └── guidance_tools.py    # Guidance tools
│   │
│   ├── api/               # Domino's API client
│   │   ├── endpoints.py         # API endpoint constants
│   │   └── client.py            # HTTP client wrapper
│   │
│   └── utils/             # Utilities
│       └── mock_order.py        # Mock order object creation
│
├── tests/                 # Comprehensive test suite (18 tests)
│   ├── test_models.py     # Model validation tests
│   ├── test_utils.py      # Utility function tests
│   ├── test_api_client.py # API client tests
│   └── test_services.py   # Service layer tests
│
├── examples/              # Example scripts
│   └── test_mcp_with_ollama.py  # Autonomous testing
│
├── logs/                  # Interaction logs (gitignored)
├── WORKFLOW.md            # Complete workflow documentation
└── README.md              # This file
```

### Benefits of This Architecture

1. **Maintainability**: Each module has a single responsibility
2. **Testability**: Services and utilities are easily unit tested
3. **Readability**: Clear separation between MCP layer, business logic, and API calls
4. **Scalability**: Easy to add new tools or services
5. **Reusability**: Services can be reused outside of MCP context

## Logging

All MCP interactions are automatically logged to `logs/interactions_YYYYMMDD.log`:

- Tool calls with full arguments
- Tool responses with previews
- State changes (order creation, items added)
- Errors with context

Log format is JSON for easy parsing and analysis.

## Limitations

### CAPTCHA Requirement
Domino's API requires CAPTCHA verification for order placement. Our system successfully:
- ✅ Validates pizza configurations
- ✅ Prices orders correctly (e.g., $11.90 for medium 2-topping)
- ✅ Accepts payment structure
- ❌ **Cannot submit final order** (blocked by `recaptchaVerificationRequired`)

This is an intentional fraud prevention measure by Domino's and **cannot be bypassed** without violating their terms of service.

### What Works
- Store lookup and menu browsing
- Coupon discovery and deal analysis
- Order validation and pricing
- Complete order preparation
- All MCP protocol features

### What Doesn't Work
- Final order submission (CAPTCHA required)
- Real payment processing

## Development

### Testing

```bash
# Run autonomous test suite (tests all tools except order placement)
python test_mcp_with_ollama.py
```

### Contributing

This is an educational project demonstrating MCP protocol integration. Contributions that enhance the educational value are welcome!

## Technical Details

- **MCP SDK**: Official Model Context Protocol SDK
- **API Library**: pizzapi (unofficial Domino's API wrapper)
- **Order Structure**: Mock order object with real API calls
- **Validation**: Multi-step validation (structure → pricing → placement)

## Disclaimer

⚠️ **Educational Use Only**

This project is for learning about:
- Model Context Protocol implementation
- Real-world API integration
- Multi-tool orchestration
- State management in AI assistants

**Do not use for actual pizza ordering.** Use Domino's official website or mobile app instead.

## License

MIT License

Based on [GrahamMcBain/mcpizza](https://github.com/GrahamMcBain/mcpizza) (MIT License)

## Acknowledgments

- **Graham McBain** - Original mcpizza project and MCP implementation
- **pizzapi contributors** - Unofficial Domino's API wrapper
- **Anthropic** - Model Context Protocol specification

---

Built with Claude Code 🤖
