import re

# Country codes with their phone number rules
COUNTRY_PHONE_RULES = {
    '+91':  {'name': 'India',          'length': 10, 'pattern': r'^[6-9]\d{9}$'},
    '+1':   {'name': 'USA/Canada',     'length': 10, 'pattern': r'^\d{10}$'},
    '+44':  {'name': 'UK',             'length': 10, 'pattern': r'^\d{10}$'},
    '+61':  {'name': 'Australia',      'length': 9,  'pattern': r'^\d{9}$'},
    '+971': {'name': 'UAE',            'length': 9,  'pattern': r'^[0-9]{9}$'},
    '+966': {'name': 'Saudi Arabia',   'length': 9,  'pattern': r'^[0-9]{9}$'},
    '+974': {'name': 'Qatar',          'length': 8,  'pattern': r'^\d{8}$'},
    '+65':  {'name': 'Singapore',      'length': 8,  'pattern': r'^[689]\d{7}$'},
    '+60':  {'name': 'Malaysia',       'length': 9,  'pattern': r'^\d{9,10}$'},
    '+49':  {'name': 'Germany',        'length': 10, 'pattern': r'^\d{10,11}$'},
    '+33':  {'name': 'France',         'length': 9,  'pattern': r'^\d{9}$'},
    '+81':  {'name': 'Japan',          'length': 10, 'pattern': r'^\d{10}$'},
    '+86':  {'name': 'China',          'length': 11, 'pattern': r'^\d{11}$'},
    '+971': {'name': 'UAE',            'length': 9,  'pattern': r'^\d{9}$'},
    '+92':  {'name': 'Pakistan',       'length': 10, 'pattern': r'^[0-9]{10}$'},
    '+880': {'name': 'Bangladesh',     'length': 10, 'pattern': r'^[0-9]{10}$'},
    '+94':  {'name': 'Sri Lanka',      'length': 9,  'pattern': r'^[0-9]{9}$'},
    '+977': {'name': 'Nepal',          'length': 10, 'pattern': r'^[0-9]{10}$'},
}

VALID_COUNTRY_CODES = list(COUNTRY_PHONE_RULES.keys())


def validate_phone_number(country_code, phone_number):
    """
    Validates phone number based on country code rules.
    Returns (is_valid, error_message)
    """
    # Check country code is valid
    if country_code not in COUNTRY_PHONE_RULES:
        return False, f"Unsupported country code '{country_code}'."

    # Remove any spaces or dashes from phone number
    phone_number = re.sub(r'[\s\-\(\)]', '', phone_number)

    # Check it's all digits
    if not phone_number.isdigit():
        return False, "Phone number must contain digits only."

    # Get rules for this country
    rules = COUNTRY_PHONE_RULES[country_code]
    pattern = rules['pattern']

    # Validate against pattern
    if not re.match(pattern, phone_number):
        country_name = rules['name']
        expected_length = rules['length']
        return False, f"Invalid phone number for {country_name}. Expected {expected_length} digits."

    return True, None


def get_valid_country_codes():
    """Returns list of valid country codes with country names."""
    return [
        {"code": code, "country": rules['name']}
        for code, rules in COUNTRY_PHONE_RULES.items()
    ]