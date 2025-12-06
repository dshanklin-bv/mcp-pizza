"""Run MCPizza MCP server"""
from mcpizza.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
