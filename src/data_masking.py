"""
Data masking utilities for protecting sensitive client information.
"""
import re
import hashlib
from typing import Dict, Any, List, Union, Set

# Define sensitive field patterns
ACCOUNT_NUMBER_PATTERN = re.compile(r'ACC\d+')
CLIENT_ID_PATTERN = re.compile(r'C\d+')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Fields that should be masked in any object
SENSITIVE_FIELDS = {
    'account_number', 
    'client_id',
    'email',
    'recipient_email'
}

# Fields that should be partially masked (show only last 4 chars)
PARTIAL_MASK_FIELDS = {
    'client_name'
}

def hash_value(value: str) -> str:
    """Create a deterministic hash of a value for consistent masking."""
    if not value:
        return value
    
    # Create a deterministic hash that's consistent for the same input
    hashed = hashlib.md5(value.encode()).hexdigest()
    return hashed[:8]  # Use first 8 chars of hash

def mask_account_number(account_number: str) -> str:
    """Mask an account number, showing only last 4 digits."""
    if not account_number:
        return account_number
    
    if len(account_number) <= 4:
        return "****"
    
    masked = "X" * (len(account_number) - 4) + account_number[-4:]
    return masked

def mask_email(email: str) -> str:
    """Mask an email address."""
    if not email or '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    if len(username) <= 2:
        masked_username = "**"
    else:
        masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

def mask_client_name(name: str) -> str:
    """Partially mask a client name, showing only first initial and last name."""
    if not name or ' ' not in name:
        return name
    
    parts = name.split()
    if len(parts) == 1:
        return f"{parts[0][0]}***"
    
    # For names with multiple parts, keep first initial and last name
    first_initial = parts[0][0]
    last_name = parts[-1]
    return f"{first_initial}. {last_name}"

def mask_sensitive_data(data: Any, masked_fields: Set[str] = None) -> Any:
    """
    Recursively mask sensitive data in a nested structure.
    
    Args:
        data: The data structure to mask (dict, list, or primitive)
        masked_fields: Set of field names that have already been masked
                      (used for recursive calls)
    
    Returns:
        A copy of the data with sensitive information masked
    """
    if masked_fields is None:
        masked_fields = set()
    
    # Handle different data types
    if isinstance(data, dict):
        return mask_dict(data, masked_fields)
    elif isinstance(data, list):
        return [mask_sensitive_data(item, masked_fields) for item in data]
    elif isinstance(data, str):
        # Check if this string looks like an account number or other sensitive pattern
        if ACCOUNT_NUMBER_PATTERN.fullmatch(data):
            return mask_account_number(data)
        elif CLIENT_ID_PATTERN.fullmatch(data):
            return hash_value(data)
        elif EMAIL_PATTERN.fullmatch(data):
            return mask_email(data)
        return data
    else:
        # Return primitives unchanged
        return data

def mask_dict(data_dict: Dict[str, Any], masked_fields: Set[str]) -> Dict[str, Any]:
    """Mask sensitive fields in a dictionary."""
    result = {}
    
    for key, value in data_dict.items():
        # Check if this is a sensitive field
        if key in SENSITIVE_FIELDS:
            if key == 'account_number':
                result[key] = mask_account_number(value)
            elif key == 'email' or key == 'recipient_email':
                result[key] = mask_email(value)
            else:
                result[key] = hash_value(value)
            masked_fields.add(key)
        elif key in PARTIAL_MASK_FIELDS:
            if key == 'client_name':
                result[key] = mask_client_name(value)
            masked_fields.add(key)
        else:
            # Recursively process nested structures
            result[key] = mask_sensitive_data(value, masked_fields)
    
    return result
