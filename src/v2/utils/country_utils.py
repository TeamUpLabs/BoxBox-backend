from typing import Optional

def get_country_code(country_name: str) -> Optional[str]:
    """
    Get ISO 3166-1 alpha-2 country code in uppercase for a given country name
    
    Args:
        country_name (str): The name of the country
        
    Returns:
        Optional[str]: Uppercase country code if found, None otherwise
    """
    country_code_mapping = {
        'Australia': 'AU',
        'Austria': 'AT',
        'Azerbaijan': 'AZ',
        'Bahrain': 'BH',
        'Belgium': 'BE',
        'Brazil': 'BR',
        'Canada': 'CA',
        'China': 'CN',
        'France': 'FR',
        'Germany': 'DE',
        'Hungary': 'HU',
        'Italy': 'IT',
        'Japan': 'JP',
        'Mexico': 'MX',
        'Monaco': 'MC',
        'Netherlands': 'NL',
        'Qatar': 'QA',
        'Saudi Arabia': 'SA',
        'Singapore': 'SG',
        'Spain': 'ES',
        'United Arab Emirates': 'AE',
        'United Kingdom': 'GB',
        'United States': 'US',
        'Portugal': 'PT',
        'Russia': 'RU',
        'Turkey': 'TR',
        'Vietnam': 'VN'
    }
    return country_code_mapping.get(country_name, None)
