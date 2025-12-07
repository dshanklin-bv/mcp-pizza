"""
Payment processing and order placement services
"""
from typing import Dict, Any
from mcpizza.api.client import api_client
from mcpizza.services.order_service import get_current_order


def place_order(payment_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Place a real order with payment.

    ⚠️ WARNING: This charges a real credit card!

    Args:
        payment_info: Dictionary with card_number, card_expiry, card_cvv, card_zip

    Returns:
        Order placement result with status and details
    """
    current_order = get_current_order()

    if current_order is None:
        return {
            'success': False,
            'error': 'No active order. Create an order first.'
        }

    result = {'success': False, 'steps': []}

    # Step 1: Price the order (validate and get totals)
    try:
        result['steps'].append('Validating and pricing order...')

        # Update order data with customer info
        current_order.data.update(
            StoreID=current_order.store.id,
            Email=current_order.customer.email,
            FirstName=current_order.customer.first_name,
            LastName=current_order.customer.last_name,
            Phone=current_order.customer.phone
        )

        # Call pricing API
        price_data = api_client.price_order(current_order.data)

        if price_data.get('Status') == -1:
            result['error'] = f"Pricing failed: {price_data}"
            return result

        # Update order with pricing info
        for key, value in price_data.get('Order', {}).items():
            if value or not isinstance(value, list):
                current_order.data[key] = value

        amounts = current_order.data.get('Amounts', {})
        result['steps'].append(f"Order validated - Subtotal: ${amounts.get('Customer', 0):.2f}")
        result['pricing'] = amounts

    except Exception as price_error:
        result['error'] = f"Pricing failed: {str(price_error)}"
        return result

    # Step 2: Add payment information
    result['steps'].append('Adding payment information...')

    current_order.data['Payments'] = [{
        'Type': 'CreditCard',
        'Number': payment_info.get('card_number'),
        'Expiration': payment_info.get('card_expiry'),
        'Amount': current_order.data['Amounts'].get('Customer', 0),
        'CardType': 'AMEX' if payment_info.get('card_number', '').startswith('3') else 'Visa',
        'SecurityCode': payment_info.get('card_cvv'),
        'PostalCode': payment_info.get('card_zip')
    }]

    result['steps'].append('Payment added')

    # Step 3: Place the order
    try:
        result['steps'].append('Submitting order to Domino\'s...')

        response = api_client.place_order(current_order.data)

        # Check if order was actually successful
        if response.get('Status') == -1:
            result['success'] = False
            result['rejected'] = True
            result['status'] = response.get('Status')
            result['status_items'] = response.get('Order', {}).get('StatusItems', [])
            result['error'] = 'ORDER REJECTED BY DOMINO\'S'
        else:
            result['success'] = True
            result['order_id'] = response.get('Order', {}).get('OrderID')
            result['status'] = response.get('Status')
            result['estimated_wait_minutes'] = response.get('Order', {}).get('EstimatedWaitMinutes')
            result['steps'].append('ORDER PLACED SUCCESSFULLY!')

    except Exception as place_error:
        result['error'] = f"ORDER FAILED: {str(place_error)}"
        result['possible_causes'] = [
            'Invalid payment information',
            'Store not accepting online orders',
            'Invalid items in order',
            'API limitations',
            'CAPTCHA verification required'
        ]

    return result
