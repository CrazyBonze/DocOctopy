"""Scenario 2: Malformed Google-style docstrings."""


def calculate_area(length, width):
    """Calculate area of rectangle
    Args:
        length: length of rectangle
        width: width of rectangle
    Returns:
        area
    """
    return length * width


def process_data(data, limit=None):
    """Process data
    Args:
        data: data to process
    """
    if limit:
        return data[:limit]
    return data


class DataProcessor:
    """DataProcessor class"""

    def __init__(self, config):
        """Initialize processor
        Args:
            config: configuration object
        """
        self.config = config

    def process(self, items):
        """Process items
        Args:
            items: list of items
        Returns:
            processed items
        """
        return [item for item in items if item]


def validate_input(value, min_val=0, max_val=100):
    """Validate input value
    Args:
        value: value to validate
        min_val: minimum value
        max_val: maximum value
    Returns:
        True if valid
    """
    return min_val <= value <= max_val
