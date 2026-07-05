"""
calculator_engine.py
Core math evaluation logic for the Scientific Calculator.

Uses a restricted namespace (only `math` functions + safe builtins) so we
never call raw eval() on arbitrary user input with full Python access.
"""

import math
import re


class CalculationError(Exception):
    """Raised when an expression is invalid or unsafe."""
    pass


# Whitelist of names allowed inside the expression.
_ALLOWED_NAMES = {
    # constants
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    # trig
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    # logs / exponents
    "log": math.log,      # log(x, base=e) -> supports log(x, base)
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,
    "sqrt": math.sqrt,
    "cbrt": lambda x: x ** (1 / 3),
    "pow": math.pow,
    # misc
    "factorial": math.factorial,
    "abs": abs,
    "round": round,
    "degrees": math.degrees,
    "radians": math.radians,
    "gcd": math.gcd,
    "floor": math.floor,
    "ceil": math.ceil,
}

# Only allow digits, operators, parentheses, letters (for func names), dot, comma, spaces
_SAFE_PATTERN = re.compile(r"^[0-9a-zA-Z_+\-*/().,\s%^]*$")


def _preprocess(expression: str) -> str:
    """Normalize common calculator notation into valid Python syntax."""
    expr = expression.strip()
    expr = expr.replace("^", "**")     # caret -> power
    expr = expr.replace("×", "*").replace("÷", "/")
    return expr


def evaluate(expression: str) -> float:
    """
    Safely evaluate a math expression string and return the numeric result.
    Raises CalculationError on invalid/unsafe input.
    """
    if not expression or not expression.strip():
        raise CalculationError("Empty expression.")

    expr = _preprocess(expression)

    if not _SAFE_PATTERN.match(expr):
        raise CalculationError("Expression contains disallowed characters.")

    try:
        # No builtins available at all; only our whitelisted names.
        result = eval(expr, {"__builtins__": {}}, _ALLOWED_NAMES)
    except ZeroDivisionError:
        raise CalculationError("Division by zero.")
    except (SyntaxError, NameError, TypeError, ValueError) as exc:
        raise CalculationError(f"Invalid expression: {exc}")

    if isinstance(result, complex):
        raise CalculationError("Result is complex; not supported.")

    return result


def format_result(result: float) -> str:
    """Pretty-print a numeric result, trimming floating point noise."""
    if isinstance(result, float):
        if result.is_integer():
            return str(int(result))
        return f"{result:.10g}"
    return str(result)


if __name__ == "__main__":
    # Quick manual test harness — run `python calculator_engine.py`
    tests = [
        "2 + 3 * 4",
        "sqrt(16)",
        "sin(pi/2)",
        "log(100, 10)",
        "2^10",
        "factorial(5)",
        "1/0",
        "__import__('os')",
    ]
    for t in tests:
        try:
            print(f"{t:25s} -> {format_result(evaluate(t))}")
        except CalculationError as e:
            print(f"{t:25s} -> ERROR: {e}")
