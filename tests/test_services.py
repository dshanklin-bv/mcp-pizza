"""
Test service functions
"""
import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from types import SimpleNamespace

# Mock pizzapi module before importing services
sys.modules['pizzapi'] = MagicMock()

from mcpizza.services import order_service
from mcpizza.utils.mock_order import create_mock_order


@patch('mcpizza.services.order_service.Address')
@patch('mcpizza.services.order_service.Customer')
def test_create_order(mock_customer, mock_address):
    """Test order creation"""
    # Mock pizzapi objects
    mock_address_instance = Mock()
    mock_address_instance.closest_store.return_value = Mock(id="8022")
    mock_address.return_value = mock_address_instance

    mock_customer_instance = Mock()
    mock_customer_instance.first_name = "John"
    mock_customer_instance.last_name = "Doe"
    mock_customer.return_value = mock_customer_instance

    # Create order
    result = order_service.create_order(
        store_id="8022",
        customer_name="John Doe",
        customer_email="john@example.com",
        customer_phone="5555551234",
        delivery_address="123 Main St",
        delivery_city="Fort Worth",
        delivery_state="TX",
        delivery_zip="76102",
        order_type="Delivery"
    )

    # Verify
    assert result['success'] is True
    assert 'John Doe' in result['message']
    assert order_service.current_order is not None


def test_add_pizza_with_toppings():
    """Test adding pizza with toppings"""
    # Setup mock order
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

    order_service.current_order = create_mock_order(store, customer, address, "Delivery")

    # Add pizza
    result = order_service.add_pizza_with_toppings(
        coupon_code="9204",
        size="12",
        crust="NPAN",
        toppings=["P", "S"]
    )

    # Verify
    assert result['success'] is True
    assert order_service.current_order.data['Coupons'][0]['Code'] == "9204"
    assert len(order_service.current_order.data['Products']) == 1
    assert order_service.current_order.data['Products'][0]['Code'] == "P12IPAZA"


def test_view_order():
    """Test viewing order"""
    # Setup mock order
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

    order_service.current_order = create_mock_order(store, customer, address, "Delivery")
    order_service.current_order.add_coupon("9204")

    # View order
    result = order_service.view_order()

    # Verify
    assert result['store_id'] == "8022"
    assert result['customer']['name'] == "John Doe"
    assert len(result['coupons']) == 1


def test_clear_order():
    """Test clearing order"""
    # Setup mock order
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

    order_service.current_order = create_mock_order(store, customer, address, "Delivery")

    # Clear order
    result = order_service.clear_order()

    # Verify
    assert result['success'] is True
    assert order_service.current_order is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
