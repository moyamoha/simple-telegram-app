def is_str_digit_like(s: str) -> bool:
    """Check if the string represents a digit (including negative numbers)."""
    if s.startswith('-') or s.startswith('+'):
        return s[1:].isdigit()
    return s.isdigit()