"""
AI-powered ordering guidance service
"""
from typing import Dict, Any, List, Tuple
from mcpizza.services.store_service import get_coupons


def get_ordering_guidance(store_id: str, user_request: str) -> Dict[str, Any]:
    """
    Provide AI guidance on building the best order.

    Args:
        store_id: Store ID
        user_request: User's description of what they want

    Returns:
        Ordering guidance with recommendations
    """
    # Get all available coupons
    coupons = get_coupons(store_id)

    # Analyze the user request
    request_lower = user_request.lower()

    # Categorize deals
    multi_pizza_deals = []
    single_pizza_deals = []
    percentage_deals = []

    for coupon in coupons:
        name = coupon['name'].lower()
        code = coupon['code']
        price = coupon['price']

        if '2 or more' in name or 'two or more' in name:
            multi_pizza_deals.append((code, coupon['name'], price))
        elif 'medium' in name and price != 999.99 and 'pizza' in name:
            single_pizza_deals.append(('medium', code, coupon['name'], price))
        elif 'large' in name and price != 999.99 and 'pizza' in name:
            single_pizza_deals.append(('large', code, coupon['name'], price))
        elif '%' in name or 'percent' in name:
            percentage_deals.append((code, coupon['name']))

    # Build recommendations
    strategies = []
    recommended_code = None

    if multi_pizza_deals:
        strategies.append({
            'type': 'multi_pizza',
            'title': 'Multi-Pizza Deals (Best for 2+ pizzas)',
            'deals': [
                {
                    'code': code,
                    'name': name,
                    'price': price
                }
                for code, name, price in sorted(multi_pizza_deals, key=lambda x: x[2])[:3]
            ]
        })

    if single_pizza_deals:
        strategies.append({
            'type': 'single_pizza',
            'title': 'Single Pizza Deals',
            'deals': [
                {
                    'size': size,
                    'code': code,
                    'name': name,
                    'price': price
                }
                for size, code, name, price in sorted(single_pizza_deals, key=lambda x: x[3])[:3]
            ]
        })

    # Determine recommended coupon based on user request
    if 'deep dish' in request_lower or 'pan' in request_lower:
        # Look for medium 2-topping deal (usually code 9204 for pan)
        for size, code, name, price in single_pizza_deals:
            if 'medium' in name.lower() and '2' in name and 'topping' in name.lower():
                recommended_code = code
                break
    else:
        # Default to best multi-pizza deal if available
        if multi_pizza_deals:
            recommended_code = multi_pizza_deals[0][0]
        elif single_pizza_deals:
            recommended_code = single_pizza_deals[0][1]

    return {
        'user_request': user_request,
        'strategies': strategies,
        'recommended_code': recommended_code,
        'total_coupons_available': len(coupons)
    }
