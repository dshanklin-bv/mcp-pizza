"""
HTTP client wrapper for Domino's API
"""
import requests
from typing import Any, Dict
from mcpizza.api import endpoints


class DominosAPIClient:
    """Client for interacting with Domino's API"""

    def __init__(self):
        self.base_url = endpoints.BASE_URL
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'MCPizza/1.0'
        }

    def get_store_info(self, store_id: str) -> Dict[str, Any]:
        """Get detailed information about a store"""
        url = endpoints.STORE_INFO.format(base=self.base_url, store_id=store_id)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_store_menu(self, store_id: str) -> Dict[str, Any]:
        """Get full menu for a store including coupons"""
        url = endpoints.STORE_MENU.format(base=self.base_url, store_id=store_id)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def price_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and price an order"""
        url = endpoints.PRICE_ORDER.format(base=self.base_url)
        response = requests.post(
            url=url,
            headers=self.headers,
            json={'Order': order_data}
        )
        response.raise_for_status()
        return response.json()

    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit an order for placement"""
        url = endpoints.PLACE_ORDER.format(base=self.base_url)
        response = requests.post(
            url=url,
            headers=self.headers,
            json={'Order': order_data}
        )
        response.raise_for_status()
        return response.json()


# Global client instance
api_client = DominosAPIClient()
