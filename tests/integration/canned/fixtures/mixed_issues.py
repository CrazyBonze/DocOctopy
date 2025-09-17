"""Scenario 3: Mixed issues - missing params, wrong sections, etc."""


def complex_function(data, limit=None, sort_key=None, reverse=False):
    """Process complex data with various options.

    Args:
        data: The input data to process

    Returns:
        Processed data
    """
    if limit:
        data = data[:limit]
    if sort_key:
        data = sorted(data, key=sort_key, reverse=reverse)
    return data


def calculate_statistics(numbers):
    """Calculate basic statistics.

    Args:
        numbers: List of numbers

    Returns:
        Dictionary with mean, median, and mode
    """
    if not numbers:
        return {}

    mean = sum(numbers) / len(numbers)
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    median = (
        sorted_nums[n // 2]
        if n % 2 == 1
        else (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
    )

    return {"mean": mean, "median": median}


class DatabaseConnection:
    """Database connection manager."""

    def __init__(self, host, port, username, password):
        """Initialize database connection.

        Args:
            host: Database host
            port: Database port
            username: Username
            password: Password
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def connect(self):
        """Establish database connection."""
        # Connection logic here
        pass

    def execute_query(self, query, params=None):
        """Execute SQL query.

        Args:
            query: SQL query string

        Returns:
            Query results
        """
        # Query execution logic
        pass


def parse_config_file(file_path):
    """Parse configuration file.

    Args:
        file_path: Path to config file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    import json

    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in config file: {file_path}")
