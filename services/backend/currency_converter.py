"""
Currency conversion service using exchange rates.
Supports 6 major currencies: USD, EUR, GBP, JPY, CNY, CAD
"""

import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
from logger import get_logger

log = get_logger(__name__)

# Cache for exchange rates
_exchange_rates_cache: Optional[Dict[str, float]] = None
_cache_timestamp: Optional[datetime] = None
_cache_duration = timedelta(hours=1)  # Refresh rates every hour

# Major currencies we support (limited to 6)
SUPPORTED_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'CAD']

def get_exchange_rates(base_currency: str = 'USD') -> Dict[str, float]:
    """
    Get exchange rates with USD as base currency.
    Uses a free exchange rate API with caching.
    """
    global _exchange_rates_cache, _cache_timestamp

    # Check if we have a valid cache
    if _exchange_rates_cache and _cache_timestamp:
        if datetime.now() - _cache_timestamp < _cache_duration:
            log.debug("Using cached exchange rates")
            return _exchange_rates_cache

    # Try to fetch from API
    try:
        # Using exchangerate-api.io (free tier, no API key needed for basic use)
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        log.info(f"Fetching exchange rates from API with base currency: {base_currency}")

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()
        rates = data.get('rates', {})

        # Update cache
        _exchange_rates_cache = rates
        _cache_timestamp = datetime.now()

        log.info(f"Successfully fetched {len(rates)} exchange rates")
        return rates

    except Exception as e:
        log.error(f"Failed to fetch exchange rates: {e}")

        # Fallback to hardcoded rates if API fails
        log.warning("Using fallback exchange rates")
        return get_fallback_rates()

def get_fallback_rates() -> Dict[str, float]:
    """
    Fallback exchange rates (approximate, relative to USD).
    These are rough estimates and should only be used if API fails.
    Limited to 6 major currencies.
    """
    return {
        'USD': 1.0,
        'EUR': 0.92,
        'GBP': 0.79,
        'JPY': 149.50,
        'CNY': 7.24,
        'CAD': 1.36,
    }

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert an amount from one currency to another.

    Args:
        amount: The amount to convert
        from_currency: Source currency code (e.g., 'EUR')
        to_currency: Target currency code (e.g., 'USD')

    Returns:
        Converted amount in target currency
    """
    if from_currency == to_currency:
        return amount

    # Normalize currency codes
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    log.debug(f"Converting {amount} from {from_currency} to {to_currency}")

    # Get exchange rates with USD as base
    rates = get_exchange_rates('USD')

    # Convert to USD first (if not already USD)
    if from_currency != 'USD':
        if from_currency not in rates:
            log.error(f"Unsupported currency: {from_currency}")
            raise ValueError(f"Unsupported currency: {from_currency}")
        amount_in_usd = amount / rates[from_currency]
    else:
        amount_in_usd = amount

    # Convert from USD to target currency
    if to_currency != 'USD':
        if to_currency not in rates:
            log.error(f"Unsupported currency: {to_currency}")
            raise ValueError(f"Unsupported currency: {to_currency}")
        converted_amount = amount_in_usd * rates[to_currency]
    else:
        converted_amount = amount_in_usd

    log.debug(f"Converted result: {converted_amount} {to_currency}")
    return converted_amount

def get_supported_currencies() -> list[str]:
    """Return list of supported currency codes."""
    return SUPPORTED_CURRENCIES