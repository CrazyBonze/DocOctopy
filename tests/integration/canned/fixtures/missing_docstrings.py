"""Scenario 1: Missing docstrings for functions and classes."""


def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number.

    Args:
        n (int): The position in the Fibonacci sequence to calculate.

    Returns:
        int: The nth Fibonacci number.
    """

    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


def process_user_data(user_id, include_metadata=False):
    """Process user data.

    Args:
        user_id (str): The unique identifier of the user.
        include_metadata (bool): Whether to include metadata in the response.

    Returns:
        dict: A dictionary containing user information, including their name and email address. If `include_metadata` is True, it also includes additional details such as account creation date and last login time.
    """

    # Process user data
    pass


class UserManager:
    """Implementation of a UserManager class to manage user data.

    Args:
        users (list): A list of dictionaries containing user information. Each dictionary has keys 'name', 'email', and 'age'.

    Methods:
        add_user(user_dict): Adds a new user to the users list.
        delete_user(user_id): Deletes a user from the users list based on their ID.
        update_user(user_id, updated_info): Updates information for a specific user in the users list.
    """

    def __init__(self, database_url):
        self.db_url = database_url

    def create_user(self, username, email):
        # Create new user
        pass

    def get_user(self, user_id):
        # Get user by ID
        pass


def validate_email(email):
    """Validates whether an email address is valid.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """

    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
