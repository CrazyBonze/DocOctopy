"""Test fixture with Google style docstring patterns from napoleon examples.

This file contains various Google style docstring patterns that should be
validated by our rules. Based on:
https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
"""

# Module level variables
module_level_variable1 = 12345
module_level_variable2 = 98765
"""int: Module level variable documented inline."""


def function_with_types_in_docstring(param1, param2):
    """Example function with types documented in the docstring.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: The return value. True for success, False otherwise.
    """
    return True


def function_with_pep484_type_annotations(param1: int, param2: str) -> bool:
    """Example function with PEP 484 type annotations.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.
    """
    return True


def module_level_function(param1, param2=None, *args, **kwargs):
    """This is an example of a module level function.

    Args:
        param1 (int): The first parameter.
        param2 (:obj:`str`, optional): The second parameter. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        AttributeError: The ``Raises`` section is a list of all exceptions.
        ValueError: If `param2` is equal to `param1`.
    """
    if param1 == param2:
        raise ValueError("param1 may not be equal to param2")
    return True


def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns`` section.

    Args:
        n (int): The upper limit of the range to generate, from 0 to `n` - 1.

    Yields:
        int: The next number in the range of 0 to `n` - 1.
    """
    for i in range(n):
        yield i


class ExampleError(Exception):
    """Exceptions are documented in the same way as classes.

    Args:
        msg (str): Human readable string describing the exception.
        code (:obj:`int`, optional): Error code.

    Attributes:
        msg (str): Human readable string describing the exception.
        code (int): Exception error code.
    """

    def __init__(self, msg, code):
        self.msg = msg
        self.code = code


class ExampleClass:
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.
    """

    def __init__(self, param1, param2, param3):
        """Example of docstring on the __init__ method.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`.
            param3 (:obj:`list` of :obj:`str`): Description of `param3`.
        """
        self.attr1 = param1
        self.attr2 = param2
        self.attr3 = param3

    @property
    def readonly_property(self):
        """str: Properties should be documented in their getter method."""
        return "readonly_property"

    def example_method(self, param1, param2):
        """Class methods are similar to regular functions.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.
        """
        return True


# Functions with various issues for testing rules
def missing_docstring_function(param1, param2):
    """Missing docstring - should trigger DG101."""
    return param1 + param2


def malformed_args_section(param1, param2):
    """Function with malformed args section.

    Args:
        param1: Missing type annotation
        param2 (str): Properly formatted parameter
        param3: Extra parameter not in function signature
    """
    return param1 + param2


def missing_returns_section(param1: int, param2: int) -> int:
    """Function with return annotation but missing Returns section.

    Args:
        param1: First parameter
        param2: Second parameter
    """
    return param1 + param2


def missing_raises_section():
    """Function that raises exceptions but doesn't document them.

    Returns:
        str: Some return value
    """
    raise ValueError("This should be documented")


def summary_without_period():
    """Summary line without period

    Args:
        param: A parameter

    Returns:
        str: Return value
    """
    return "test"


def no_blank_line_after_summary():
    """Summary line
    Args:
        param: A parameter

    Returns:
        str: Return value
    """
    return "test"


def inconsistent_indentation():
    """Function with inconsistent docstring indentation.

    Args:
        param1: First parameter
    param2: Second parameter with wrong indentation
        param3: Third parameter

    Returns:
        str: Return value
    """
    return "test"


def args_section_lowercase_description(param1, param2):
    """Function with lowercase descriptions in Args section.

    Args:
        param1: the first parameter
        param2: the second parameter

    Returns:
        str: return value
    """
    return "test"


def returns_section_lowercase_description():
    """Function with lowercase description in Returns section.

    Returns:
        str: return value
    """
    return "test"


def raises_section_lowercase_description():
    """Function with lowercase description in Raises section.

    Raises:
        ValueError: if something goes wrong
    """
    raise ValueError("test")
