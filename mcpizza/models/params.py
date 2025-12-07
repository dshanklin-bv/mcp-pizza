"""
Pydantic models for MCP tool parameters
"""
from typing import Optional
from pydantic import BaseModel, Field


class StoreSearchParams(BaseModel):
    """Parameters for finding stores"""
    query: str = Field(description="Address or zip code to search for stores")


class StoreInfoParams(BaseModel):
    """Parameters for getting store information"""
    store_id: str = Field(description="Store ID to get information for")


class MenuSearchParams(BaseModel):
    """Parameters for searching menu items"""
    store_id: str = Field(description="Store ID to search menu for")
    query: Optional[str] = Field(default=None, description="Search query (optional)")
    category: Optional[str] = Field(default=None, description="Category filter (e.g., 'Pizza', 'Wings', 'Sides')")


class CreateOrderParams(BaseModel):
    """Parameters for creating an order"""
    store_id: str = Field(description="Store ID to order from")
    customer_name: str = Field(description="Customer first and last name")
    customer_email: str = Field(description="Customer email address")
    customer_phone: str = Field(description="Customer phone number")
    delivery_address: str = Field(description="Delivery street address")
    delivery_city: str = Field(description="Delivery city")
    delivery_state: str = Field(description="Delivery state (2-letter code)")
    delivery_zip: str = Field(description="Delivery zip code")
    order_type: str = Field(default="Delivery", description="Order type: 'Delivery' or 'Carryout'")


class AddItemParams(BaseModel):
    """Parameters for adding an item to order"""
    item_code: str = Field(description="Menu item code")
    quantity: int = Field(default=1, description="Quantity to add")
    options: Optional[dict] = Field(default=None, description="Item customization options")


class AddPizzaParams(BaseModel):
    """Parameters for adding a customized pizza"""
    coupon_code: str = Field(description="Coupon code (e.g., '9204')")
    size: str = Field(default="12", description="Pizza size: 10, 12, 14, 16")
    crust: str = Field(default="NPAN", description="Crust type: NPAN (pan), HAND (hand tossed), THIN, etc.")
    toppings: list[str] = Field(description="List of topping codes (e.g., ['P', 'S'] for pepperoni and sausage)")
