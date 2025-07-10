"""Sample Python file for demonstration."""

from __future__ import annotations

from typing import Any


def hello_world() -> None:
    """Print hello world."""
    print("Hello, World!")


def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def unused_function() -> None:
    """This function is not used."""
    pass


class BadClass:
    """A class with issues."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def method_with_issues(self) -> Any:
        x = self.value
        y = 10
        return x + y


if __name__ == "__main__":
    hello_world()
    result = add_numbers(5, 3)
    print(f"Result: {result}")
