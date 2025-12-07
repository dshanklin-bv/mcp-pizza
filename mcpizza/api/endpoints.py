"""
Domino's API endpoint constants
"""

BASE_URL = "https://order.dominos.com"

# Store endpoints
STORE_INFO = "{base}/power/store/{store_id}"
STORE_MENU = "{base}/power/store/{store_id}/menu?lang=en&structured=true"

# Order endpoints
PRICE_ORDER = "{base}/power/price-order"
PLACE_ORDER = "{base}/power/place-order"
