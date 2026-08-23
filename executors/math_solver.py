"""
Nebula v9 — Mathematics, Algebra, Calculus, and Number Theory Executors
"""
import math
from typing import Tuple


def _me_is_prime(e) -> Tuple[bool, str]:
    q = e.get("query", "") or e.get("raw", "")
    nums = [int(s) for s in q.split() if s.isdigit()]
    if not nums:
        return False, "Specify a number to check"
    n = nums[0]
    if n < 2:
        return True, f"{n} is not prime"
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return True, f"{n} is not prime (divisible by {i})"
    return True, f"{n} is prime!"


def _me_fibonacci(e) -> Tuple[bool, str]:
    q = e.get("query", "") or e.get("raw", "")
    nums = [int(s) for s in q.split() if s.isdigit()]
    if not nums:
        return False, "Specify the term N"
    n = nums[0]
    if n > 1000:
        return False, "Number too large"
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return True, f"Fibonacci({n}) = {a}"


def _me_solve(e) -> Tuple[bool, str]:
    q = e.get("query", "") or e.get("raw", "")
    if not q:
        return False, "Specify equation to solve"
    try:
        import sympy as sp
        expr_str = q.replace("^", "**").replace("=", "-").strip()
        x = sp.Symbol("x")
        expr = sp.sympify(expr_str)
        solutions = sp.solve(expr, x)
        sols = ", ".join(str(s) for s in solutions)
        return True, f"Solutions for {q}: x = {sols}"
    except Exception:
        try:
            # Fallback simple arithmetic evaluation
            clean = q.replace("^", "**")
            result = eval(clean, {"__builtins__": {}}, {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "abs": abs
            })
            return True, f"{q} = {result}"
        except Exception as ex:
            return False, f"Could not solve: {ex}"
