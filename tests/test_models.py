"""
Test Pydantic models
"""
import pytest
from pydantic import ValidationError
from mcpizza.models.params import (
    StoreSearchParams,
    StoreInfoParams,
    MenuSearchParams,
    CreateOrderParams,
    AddItemParams,
    AddPizzaParams
)


def test_store_search_params():
    """Test StoreSearchParams validation"""
    params = StoreSearchParams(query="76104")
    assert params.query == "76104"

    # Test validation error
    with pytest.raises(ValidationError):
        StoreSearchParams()


def test_store_info_params():
    """Test StoreInfoParams validation"""
    params = StoreInfoParams(store_id="8022")
    assert params.store_id == "8022"


def test_menu_search_params():
    """Test MenuSearchParams validation"""
    params = MenuSearchParams(store_id="8022", query="pizza", category="Pizza")
    assert params.store_id == "8022"
    assert params.query == "pizza"
    assert params.category == "Pizza"

    # Test optional fields
    params = MenuSearchParams(store_id="8022")
    assert params.query is None
    assert params.category is None


def test_create_order_params():
    """Test CreateOrderParams validation"""
    params = CreateOrderParams(
        store_id="8022",
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="5555551234",
        delivery_address="123 Main St",
        delivery_city="Fort Worth",
        delivery_state="TX",
        delivery_zip="76102"
    )
    assert params.store_id == "8022"
    assert params.customer_name == "John Doe"
    assert params.order_type == "Delivery"  # Default value


def test_add_item_params():
    """Test AddItemParams validation"""
    params = AddItemParams(item_code="9204", quantity=2)
    assert params.item_code == "9204"
    assert params.quantity == 2
    assert params.options is None


def test_add_pizza_params():
    """Test AddPizzaParams validation"""
    params = AddPizzaParams(
        coupon_code="9204",
        size="12",
        crust="NPAN",
        toppings=["P", "S"]
    )
    assert params.coupon_code == "9204"
    assert params.size == "12"
    assert params.crust == "NPAN"
    assert params.toppings == ["P", "S"]

    # Test defaults
    params = AddPizzaParams(coupon_code="9204", toppings=["P"])
    assert params.size == "12"
    assert params.crust == "NPAN"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
