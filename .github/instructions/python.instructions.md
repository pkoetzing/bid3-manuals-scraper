---
description: 'Python coding conventions and guidelines'
applyTo: '**/*.py'
---

# Python Coding Conventions

## Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Use the `typing` module for type annotations (e.g., `list[str]`, `dict[str, int]`).
- Break down complex functions into smaller, more manageable functions.

## General Instructions

- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.

## Code Style and Formatting

- Follow the **PEP 8** style guide for Python.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Ensure lines do not exceed 79 characters.
- Place function and class docstrings immediately after the `def` or `class` keyword.
- Use blank lines to separate functions, classes, and code blocks where appropriate.
- Use hanging indentation for line continuations;
- avoid placing a single closing brace, bracket, or parenthesis
  on a separate line.
- Use **Single quotes** for strings.
- Use **Double quotes** for docstrings.

## Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.

## Example of Proper Documentation

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.

    Parameters:
    radius (float): The radius of the circle.

    Returns:
    float: The area of the circle, calculated as π * radius^2.
    """
    import math
    return math.pi * radius ** 2
```

## Logging Guidelines
- Use the `logging` module for all logging purposes.
- Configure logging to:
  - Write **info messages** to the console.
  - Write **debug messages** to a file.
- Use the following logging format and date format:
  - `format='%(asctime)s:%(levelname)s:%(message)s'`
  - `datefmt='%Y-%m-%d %H:%M:%S'`

## File Handling
- Use the `pathlib` module for file and directory operations.

## Pandas Best Practices
- When working with timeseries data always convert the timestamp
  column to a DatetimeIndex and use it as the DataFrame’s index;
  do not leave timestamps in a separate column or separate list
  and do not separate timestamps from the values
- Avoid using `inplace=True` with pandas operations.
- Prefer method chaining for cleaner and more readable pandas code.
