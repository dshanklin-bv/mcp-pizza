#!/usr/bin/env python3
"""
Autonomous MCP Pizza Testing with Ollama
Tests all MCP functionality except actual order placement
"""

import asyncio
import json
import subprocess
import sys
from typing import Optional

try:
    import ollama
except ImportError:
    print("Installing ollama package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    import ollama


class MCPTester:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.mcp_process = None
        self.conversation_history = []

    async def start_mcp_server(self):
        """Start the MCP server"""
        print("🚀 Starting MCP server...")
        self.mcp_process = await asyncio.create_subprocess_exec(
            "uv", "--directory", "/Users/dshanklinbv/repos/mcp-pizza",
            "run", "mcpizza",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Wait a bit for server to initialize
        await asyncio.sleep(2)
        print("✅ MCP server started")

    async def send_mcp_request(self, method: str, params: dict = None):
        """Send a JSON-RPC request to the MCP server"""
        if not self.mcp_process:
            raise RuntimeError("MCP server not started")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }

        request_json = json.dumps(request) + "\n"
        self.mcp_process.stdin.write(request_json.encode())
        await self.mcp_process.stdin.drain()

        # Read response
        response_line = await self.mcp_process.stdout.readline()
        if response_line:
            return json.loads(response_line.decode())
        return None

    async def list_tools(self):
        """Get list of available MCP tools"""
        print("\n📋 Listing available tools...")
        response = await self.send_mcp_request("tools/list")

        if response and "result" in response:
            tools = response["result"].get("tools", [])
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            return tools
        return []

    async def call_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool"""
        print(f"\n🔧 Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")

        response = await self.send_mcp_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        if response:
            if "result" in response:
                result = response["result"]
                print(f"✅ Success!")
                if "content" in result:
                    for content_item in result["content"]:
                        if content_item.get("type") == "text":
                            print(f"\n{content_item.get('text', '')}")
                return result
            elif "error" in response:
                print(f"❌ Error: {response['error']}")
                return {"error": response["error"]}
        return None

    async def run_test_sequence(self):
        """Run autonomous test sequence"""
        print("\n" + "="*60)
        print("🍕 STARTING AUTONOMOUS MCP PIZZA TESTING")
        print("="*60)

        try:
            # Start server
            await self.start_mcp_server()

            # Initialize MCP
            init_response = await self.send_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp-tester",
                    "version": "1.0.0"
                }
            })
            print(f"✅ MCP initialized: {init_response}")

            # List available tools
            tools = await self.list_tools()

            # Test 1: Find stores
            print("\n" + "="*60)
            print("TEST 1: Find pizza stores near 76102")
            print("="*60)
            result1 = await self.call_tool("find_stores", {"query": "76102"})

            # Test 2: Get store info (use store from previous result)
            print("\n" + "="*60)
            print("TEST 2: Get store information for store 6982")
            print("="*60)
            result2 = await self.call_tool("get_store_info", {"store_id": "6982"})

            # Test 3: Search menu for deals
            print("\n" + "="*60)
            print("TEST 3: Search menu for deals")
            print("="*60)
            result3 = await self.call_tool("search_menu", {
                "store_id": "6982",
                "query": "deal"
            })

            # Test 4: Get full menu
            print("\n" + "="*60)
            print("TEST 4: Get full menu (first 50 items)")
            print("="*60)
            result4 = await self.call_tool("get_menu", {"store_id": "6982"})

            # Test 5: Create test order
            print("\n" + "="*60)
            print("TEST 5: Create a test order")
            print("="*60)
            result5 = await self.call_tool("create_order", {
                "store_id": "6982",
                "customer_name": "Test User",
                "customer_email": "test@example.com",
                "customer_phone": "555-0123",
                "delivery_address": "123 Test St",
                "delivery_city": "Fort Worth",
                "delivery_state": "TX",
                "delivery_zip": "76102",
                "order_type": "Delivery"
            })

            # Test 6: View order
            print("\n" + "="*60)
            print("TEST 6: View current order")
            print("="*60)
            result6 = await self.call_tool("view_order", {})

            # Test 7: Clear order
            print("\n" + "="*60)
            print("TEST 7: Clear order")
            print("="*60)
            result7 = await self.call_tool("clear_order", {})

            # Summary
            print("\n" + "="*60)
            print("📊 TEST SUMMARY")
            print("="*60)

            tests = [
                ("Find stores", result1),
                ("Get store info", result2),
                ("Search menu", result3),
                ("Get full menu", result4),
                ("Create order", result5),
                ("View order", result6),
                ("Clear order", result7)
            ]

            for test_name, result in tests:
                if result and "error" not in result:
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
                    if result and "error" in result:
                        print(f"   Error: {result['error']}")

        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Cleanup
            if self.mcp_process:
                self.mcp_process.terminate()
                await self.mcp_process.wait()
                print("\n🛑 MCP server stopped")


async def main():
    tester = MCPTester()
    await tester.run_test_sequence()


if __name__ == "__main__":
    asyncio.run(main())
