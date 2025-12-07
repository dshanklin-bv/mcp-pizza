"""
Test utility functions
"""
import pytest
from mcpizza.utils.mock_order import create_mock_order
from types import SimpleNamespace


def test_create_mock_order():
    """Test mock order creation"""
    # Create mock objects
    store = SimpleNamespace(id="8022")
    customer = SimpleNamespace(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="5555551234"
    )
    address = SimpleNamespace(
        street="123 Main St",
        city="Fort Worth",
        region="TX",
        zip="76102"
    )

    # Create mock order
    order = create_mock_order(store, customer, address, "Delivery")

    # Verify attributes
    assert order.store == store
    assert order.customer == customer
    assert order.address == address
    assert order.data['ServiceMethod'] == "Delivery"
    assert order.data['Coupons'] == []
    assert order.data['Products'] == []

    # Verify methods exist
    assert callable(order.add_coupon)
    assert callable(order.add_product)


def test_mock_order_add_coupon():
    """Test adding coupons to mock order"""
    store = SimpleNamespace(id="8022")
    customer = SimpleNamespace(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="5555551234"
    )
    address = SimpleNamespace(
        street="123 Main St",
        city="Fort Worth",
        region="TX",
        zip="76102"
    )

    order = create_mock_order(store, customer, address, "Delivery")

    # Add coupon
    order.add_coupon("9204")

    # Verify coupon was added
    assert len(order.data['Coupons']) == 1
    assert order.data['Coupons'][0]['Code'] == "9204"
    assert order.data['Coupons'][0]['Qty'] == 1


def test_mock_order_add_product():
    """Test adding products to mock order"""
    store = SimpleNamespace(id="8022")
    customer = SimpleNamespace(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="5555551234"
    )
    address = SimpleNamespace(
        street="123 Main St",
        city="Fort Worth",
        region="TX",
        zip="76102"
    )

    order = create_mock_order(store, customer, address, "Delivery")

    # Add product with toppings
    toppings = {"P": {"1/1": "1"}, "S": {"1/1": "1"}}
    order.add_product("P12IPAZA", toppings)

    # Verify product was added
    assert len(order.data['Products']) == 1
    assert order.data['Products'][0]['Code'] == "P12IPAZA"
    assert order.data['Products'][0]['Qty'] == 1
    assert order.data['Products'][0]['Options'] == toppings


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
