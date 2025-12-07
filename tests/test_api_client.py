"""
Test API client
"""
import pytest
from unittest.mock import Mock, patch
from mcpizza.api.client import DominosAPIClient
from mcpizza.api import endpoints


def test_api_client_initialization():
    """Test API client initializes correctly"""
    client = DominosAPIClient()
    assert client.base_url == endpoints.BASE_URL
    assert 'Content-Type' in client.headers
    assert client.headers['Content-Type'] == 'application/json'


@patch('mcpizza.api.client.requests.get')
def test_get_store_info(mock_get):
    """Test get_store_info makes correct API call"""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {'StoreID': '8022', 'IsOpen': True}
    mock_get.return_value = mock_response

    # Call API
    client = DominosAPIClient()
    result = client.get_store_info("8022")

    # Verify
    assert result['StoreID'] == '8022'
    assert result['IsOpen'] is True
    mock_get.assert_called_once()


@patch('mcpizza.api.client.requests.get')
def test_get_store_menu(mock_get):
    """Test get_store_menu makes correct API call"""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {'Products': {}, 'Coupons': {}}
    mock_get.return_value = mock_response

    # Call API
    client = DominosAPIClient()
    result = client.get_store_menu("8022")

    # Verify
    assert 'Products' in result
    assert 'Coupons' in result
    mock_get.assert_called_once()


@patch('mcpizza.api.client.requests.post')
def test_price_order(mock_post):
    """Test price_order makes correct API call"""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {'Status': 1, 'Order': {'Amounts': {'Customer': 11.90}}}
    mock_post.return_value = mock_response

    # Call API
    client = DominosAPIClient()
    order_data = {'Products': [], 'Coupons': []}
    result = client.price_order(order_data)

    # Verify
    assert result['Status'] == 1
    assert 'Order' in result
    mock_post.assert_called_once()


@patch('mcpizza.api.client.requests.post')
def test_place_order(mock_post):
    """Test place_order makes correct API call"""
    # Mock response
    mock_response = Mock()
    mock_response.json.return_value = {'Status': 1, 'Order': {'OrderID': '12345'}}
    mock_post.return_value = mock_response

    # Call API
    client = DominosAPIClient()
    order_data = {'Products': [], 'Coupons': [], 'Payments': []}
    result = client.place_order(order_data)

    # Verify
    assert result['Status'] == 1
    assert result['Order']['OrderID'] == '12345'
    mock_post.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
