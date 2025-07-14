"""Sample Python file for demonstration with intentional quality issues."""

import os
import sys
from typing import Any
import json
import datetime


def hello_world() -> None:
    """Print hello world."""
    print("Hello, World!")


def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def VeryLongFunctionNameThatViolatesNamingConventionsAndExceedsRecommendedLength(param1, param2, param3):
    """Function with naming and parameter issues."""
    veryLongVariableNameThatAlsoViolatesConventions = param1 + param2 + param3
    anotherProblematicVariable = veryLongVariableNameThatAlsoViolatesConventions * 2
    yetAnotherVariable = anotherProblematicVariable / 3
    return yetAnotherVariable


def unused_function() -> None:
    """This function is not used."""
    pass


def function_with_too_many_branches(x):
    if x > 10:
        if x > 20:
            if x > 30:
                if x > 40:
                    if x > 50:
                        return "very high"
                    else:
                        return "high"
                else:
                    return "medium high"
            else:
                return "medium"
        else:
            return "low medium"
    else:
        return "low"


class BadClass:
    """A class with issues."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def method_with_issues(self) -> Any:
        x = self.value
        y = 10
        z = 20
        unused_var = 42
        return x + y


class anotherBadClass:
    def methodWithoutDocstring(self):
        return "no docstring"
    
    def method_with_missing_return_type(self, param_without_type):
        result = param_without_type * 2
        return result


def function_with_line_too_long():
    """This function has a line that is way too long and exceeds the recommended line length limit."""
    very_long_variable_name = "This is a very long string that when combined with other code elements will definitely exceed the line length limit of 88 characters and trigger a formatting issue"
    return very_long_variable_name


if __name__ == "__main__":
    hello_world()
    result = add_numbers(5, 3)
    print(f"Result: {result}")
    
    # More problematic code
    bad_instance = BadClass("test")
    bad_result = bad_instance.method_with_issues()
    
    another_bad = anotherBadClass()
    another_result = another_bad.methodWithoutDocstring()