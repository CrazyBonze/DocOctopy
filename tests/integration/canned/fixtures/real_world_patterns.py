"""Scenario 4: Real-world patterns from actual projects."""


def find_files(directory, pattern="*.py", recursive=True):
    """Find files matching pattern in directory.

    Args:
        directory: Directory to search
        pattern: File pattern to match
        recursive: Whether to search recursively

    Returns:
        List of matching file paths
    """
    import glob
    import os

    if recursive:
        return glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    else:
        return glob.glob(os.path.join(directory, pattern))


class Logger:
    """Simple logging utility."""

    def __init__(self, name, level="INFO"):
        """Initialize logger.

        Args:
            name: Logger name
            level: Log level
        """
        self.name = name
        self.level = level

    def info(self, message):
        """Log info message."""
        print(f"[INFO] {self.name}: {message}")

    def error(self, message):
        """Log error message."""
        print(f"[ERROR] {self.name}: {message}")


def retry_on_failure(func, max_attempts=3, delay=1):
    """Retry function on failure.

    Args:
        func: Function to retry
        max_attempts: Maximum retry attempts
        delay: Delay between attempts

    Returns:
        Function result
    """
    import time

    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay)


def format_bytes(bytes_value):
    """Format bytes in human readable format.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


class Cache:
    """Simple in-memory cache."""

    def __init__(self, max_size=1000):
        """Initialize cache.

        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self.cache = {}

    def get(self, key):
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        return self.cache.get(key)

    def set(self, key, value):
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[key] = value
