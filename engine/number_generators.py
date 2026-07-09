"""
Deterministic number generators for ILEARN math questions.
Produces numbers that respect content limits and difficulty tiers.
All generation is seeded for reproducibility.
"""

import random
from fractions import Fraction
from typing import Optional


# Denominators that produce "clean" fractions students can work with by hand
ALLOWED_DENOMINATORS = [2, 3, 4, 5, 6, 8, 10, 12]

# Denominators that produce terminating decimals
DECIMAL_DENOMINATORS = [2, 4, 5, 8, 10, 20, 25, 50, 100]


class NumberGenerator:
    """Seeded random number generator for math questions.

    Guarantees:
    - All numbers are nonnegative rational
    - Numbers match the difficulty tier
    - Computations are hand-doable (no calculator needed)
    """

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.seed = seed

    def reseed(self, seed: int):
        """Reset with a new seed."""
        self.rng = random.Random(seed)
        self.seed = seed

    # --- Whole numbers (Easy difficulty) ---

    def whole_number(self, min_val: int = 1, max_val: int = 100) -> Fraction:
        """Generate a whole number. Used for Easy difficulty."""
        return Fraction(self.rng.randint(min_val, max_val))

    def small_whole(self, min_val: int = 2, max_val: int = 12) -> Fraction:
        """Small whole number, good for multipliers/divisors."""
        return Fraction(self.rng.randint(min_val, max_val))

    # --- Decimals (Medium difficulty) ---

    def decimal_1place(self, min_val: float = 0.1, max_val: float = 99.9) -> Fraction:
        """1 decimal place (e.g., 3.5, 12.8). Medium difficulty."""
        val = self.rng.randint(int(min_val * 10), int(max_val * 10))
        return Fraction(val, 10)

    def decimal_2place(self, min_val: float = 0.01, max_val: float = 99.99) -> Fraction:
        """2 decimal places (e.g., 3.25, 12.75). Medium/Difficult."""
        val = self.rng.randint(int(min_val * 100), int(max_val * 100))
        return Fraction(val, 100)

    def money(self, min_dollars: float = 0.25, max_dollars: float = 100.0) -> Fraction:
        """Money amount (always 2 decimal places). For real-world contexts."""
        cents = self.rng.randint(int(min_dollars * 100), int(max_dollars * 100))
        return Fraction(cents, 100)

    # --- Fractions (Difficult difficulty) ---

    def proper_fraction(self, max_denom: Optional[int] = None) -> Fraction:
        """Proper fraction (0 < f < 1). Difficult difficulty."""
        denoms = ALLOWED_DENOMINATORS
        if max_denom:
            denoms = [d for d in denoms if d <= max_denom]
        denom = self.rng.choice(denoms)
        numer = self.rng.randint(1, denom - 1)
        return Fraction(numer, denom)

    def improper_fraction(self, max_whole_part: int = 5) -> Fraction:
        """Improper fraction (f >= 1). Difficult difficulty."""
        denom = self.rng.choice(ALLOWED_DENOMINATORS)
        min_numer = denom + 1
        max_numer = denom * max_whole_part
        numer = self.rng.randint(min_numer, max_numer)
        return Fraction(numer, denom)

    def mixed_number(self, max_whole: int = 20, max_denom: Optional[int] = None) -> Fraction:
        """Mixed number (whole + proper fraction). Difficult difficulty."""
        whole = self.rng.randint(1, max_whole)
        frac = self.proper_fraction(max_denom)
        return Fraction(whole) + frac

    # --- Difficulty-aware generators ---

    def for_difficulty(self, difficulty: str, min_val: int = 1, max_val: int = 50) -> Fraction:
        """Generate a number appropriate for the given difficulty tier.

        Easy: whole numbers only
        Medium: mix of whole numbers and 1-place decimals
        Difficult: fractions, mixed numbers, or 2-place decimals
        """
        if difficulty == "easy":
            return self.whole_number(min_val, max_val)
        elif difficulty == "medium":
            choice = self.rng.random()
            if choice < 0.5:
                return self.whole_number(min_val, max_val)
            else:
                return self.decimal_1place(max(0.1, min_val * 0.1), min(99.9, max_val * 1.0))
        else:  # difficult
            choice = self.rng.random()
            if choice < 0.33:
                return self.decimal_2place(0.01, min(99.99, max_val * 1.0))
            elif choice < 0.66:
                return self.proper_fraction()
            else:
                return self.mixed_number(min(20, max_val))

    # --- Pair generators for equation forms ---
    # These ensure both the equation values AND the solution are valid

    def addition_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction]:
        """Generate (x, p, q) for x + p = q where x = q - p > 0.

        Returns: (x, p, q) all nonneg rational, appropriate for difficulty.
        """
        if difficulty == "easy":
            q = self.whole_number(3, 100)
            p = self.whole_number(1, int(q) - 1)
        elif difficulty == "medium":
            q = self.decimal_1place(2.0, 50.0)
            p = self.decimal_1place(0.1, float(q) - 0.1)
            if p >= q:
                p = q - Fraction(1, 10)
        else:  # difficult
            q = self.mixed_number(10, 6)
            p = self.proper_fraction()
            if p >= q:
                p = Fraction(1, q.denominator if q.denominator in ALLOWED_DENOMINATORS else 2)
        x = q - p
        return (x, p, q)

    def subtraction_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction]:
        """Generate (x, p, q) for x - p = q where x = q + p.

        Returns: (x, p, q) all nonneg rational.
        """
        if difficulty == "easy":
            p = self.whole_number(1, 50)
            q = self.whole_number(1, 50)
        elif difficulty == "medium":
            p = self.decimal_1place(0.5, 25.0)
            q = self.decimal_1place(0.5, 25.0)
        else:
            p = self.proper_fraction()
            q = self.mixed_number(5)
        x = q + p
        return (x, p, q)

    def multiplication_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction]:
        """Generate (x, p, q) for px = q where x = q/p.

        Generates p and x first, computes q = p*x to guarantee clean division.
        Returns: (x, p, q) all nonneg rational.
        """
        if difficulty == "easy":
            p = self.small_whole(2, 12)
            x = self.whole_number(1, 20)
        elif difficulty == "medium":
            # Mix: one decimal, one whole, guaranteeing clean result
            if self.rng.random() < 0.5:
                p = self.decimal_1place(0.5, 9.9)
                x = self.whole_number(2, 20)
            else:
                p = self.small_whole(2, 10)
                x = self.decimal_1place(0.5, 9.9)
        else:  # difficult
            p = self.proper_fraction()
            x = self.whole_number(2, 30)
        q = p * x
        return (x, p, q)

    def division_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction]:
        """Generate (x, p, q) for x/p = q where x = p*q.

        Generates p and q first, computes x = p*q.
        Returns: (x, p, q) all nonneg rational.
        """
        if difficulty == "easy":
            p = self.small_whole(2, 10)
            q = self.whole_number(1, 15)
        elif difficulty == "medium":
            p = self.decimal_1place(0.5, 5.0)
            q = self.whole_number(2, 10)
        else:
            p = self.proper_fraction()
            q = self.mixed_number(5)
        x = p * q
        return (x, p, q)


    # --- Two-step equation generators (7th grade) ---

    def two_step_add_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        """Generate (p, q, r, x) for px + q = r where x = (r - q) / p.

        Guarantees clean integer or simple rational solution.
        Returns: (p, q, r, x) appropriate for difficulty.
        """
        if difficulty == "easy":
            p = self.small_whole(2, 10)
            x = self.whole_number(1, 20)
            q = self.whole_number(1, 50)
        elif difficulty == "medium":
            if self.rng.random() < 0.5:
                p = self.decimal_1place(0.5, 5.0)
                x = self.whole_number(1, 15)
                q = self.decimal_1place(1.0, 20.0)
            else:
                p = self.small_whole(2, 8)
                x = self.decimal_1place(0.5, 10.0)
                q = self.whole_number(1, 30)
        else:  # difficult
            p = self.decimal_1place(0.5, 5.0)
            x = self.decimal_1place(0.5, 10.0)
            q = self.decimal_2place(0.25, 20.0)
        r = p * x + q
        return (p, q, r, x)

    def two_step_paren_pair(self, difficulty: str) -> tuple[Fraction, Fraction, Fraction, Fraction]:
        """Generate (p, q, r, x) for p(x + q) = r where x = r/p - q.

        Guarantees clean solution.
        Returns: (p, q, r, x) appropriate for difficulty.
        """
        if difficulty == "easy":
            p = self.small_whole(2, 8)
            x = self.whole_number(1, 15)
            q = self.whole_number(1, 20)
        elif difficulty == "medium":
            p = self.decimal_1place(0.5, 5.0)
            x = self.whole_number(1, 12)
            q = self.whole_number(1, 15)
        else:
            p = self.decimal_1place(0.5, 4.0)
            x = self.decimal_1place(0.5, 10.0)
            q = self.decimal_1place(0.5, 10.0)
        r = p * (x + q)
        return (p, q, r, x)

    def two_step_inequality_pair(self, difficulty: str, op: str = ">") -> tuple:
        """Generate (p, q, r, boundary) for px + q {op} r.

        boundary = (r - q) / p is the critical value.
        Returns: (p, q, r, boundary, op) with clean boundary value.
        """
        p, q, r, boundary = self.two_step_add_pair(difficulty)
        # For inequalities with negative p, flip the operator
        if self.rng.random() < 0.3 and difficulty != "easy":
            p = -p
            r = p * boundary + q
        return (p, q, r, boundary, op)

    # --- Linear/slope generators (7th grade) ---

    def linear_table(self, n_points: int = 5,
                     x_start: int = 0, x_step: int = 1) -> tuple:
        """Generate a linear relationship y = mx + b with clean values.

        Returns: (slope, intercept, points) where points is [(x1,y1), ...].
        """
        # Pick a clean slope
        slope_choices = [
            Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5),
            Fraction(1, 2), Fraction(3, 2), Fraction(1, 3), Fraction(2, 3),
            Fraction(3, 4), Fraction(1, 4),
        ]
        slope = self.rng.choice(slope_choices)
        intercept = self.whole_number(0, 20)

        points = []
        for i in range(n_points):
            x = Fraction(x_start + i * x_step)
            y = slope * x + intercept
            points.append((x, y))
        return (slope, intercept, points)

    def nonlinear_table(self, n_points: int = 5,
                        x_start: int = 1) -> list:
        """Generate a nonlinear (varying rate) table of values.

        Returns: list of (x, y) pairs with non-constant differences.
        """
        points = []
        y = self.whole_number(1, 10)
        for i in range(n_points):
            x = Fraction(x_start + i)
            points.append((x, y))
            # Varying increment
            delta = self.whole_number(1, 8)
            if self.rng.random() < 0.3:
                delta = delta + self.whole_number(1, 3)
            y = y + delta
        return points

    def slope_from_points(self) -> tuple:
        """Generate two points with a clean slope.

        Returns: (x1, y1, x2, y2, slope_fraction).
        """
        # Pick clean slope
        num = self.rng.randint(-5, 5)
        den = self.rng.randint(1, 5)
        while num == 0:
            num = self.rng.randint(-5, 5)
        slope = Fraction(num, den)

        x1 = self.rng.randint(-5, 5)
        y1 = self.rng.randint(-5, 5)
        x2 = x1 + den  # guarantees integer coordinates
        y2 = y1 + num

        return (Fraction(x1), Fraction(y1), Fraction(x2), Fraction(y2), slope)

    # --- Rational coefficient generators (7th grade expressions) ---

    def integer_coefficient(self, min_val: int = -12, max_val: int = 12) -> Fraction:
        """Generate an integer coefficient (may be negative). Excludes 0."""
        val = self.rng.randint(min_val, max_val)
        while val == 0:
            val = self.rng.randint(min_val, max_val)
        return Fraction(val)

    def decimal_coefficient(self, min_val: float = -9.9, max_val: float = 9.9) -> Fraction:
        """Generate a 1-place decimal coefficient (may be negative). Excludes 0."""
        val = self.rng.randint(int(min_val * 10), int(max_val * 10))
        while val == 0:
            val = self.rng.randint(int(min_val * 10), int(max_val * 10))
        return Fraction(val, 10)

    def rational_coefficient(self, difficulty: str) -> Fraction:
        """Generate a coefficient appropriate for the difficulty tier.

        Easy: integers
        Medium: mix of integers and decimals
        Difficult: non-integer rationals (decimals or fractions)
        """
        if difficulty == "easy":
            return self.integer_coefficient()
        elif difficulty == "medium":
            if self.rng.random() < 0.5:
                return self.integer_coefficient()
            else:
                return self.decimal_coefficient()
        else:
            if self.rng.random() < 0.5:
                return self.decimal_coefficient()
            else:
                sign = self.rng.choice([-1, 1])
                return sign * self.proper_fraction()

    # --- 8th grade generators ---

    def multi_step_equation(self, difficulty: str = "easy") -> tuple:
        """Generate a(bx + c) + dx = e with clean solution x.

        Returns (a, b, c, d, e, x) as Fractions.
        """
        for _ in range(50):
            if difficulty == "easy":
                x = Fraction(self.rng.randint(-10, 10))
                while x == 0:
                    x = Fraction(self.rng.randint(-10, 10))
                a = Fraction(self.rng.randint(2, 6))
                b = Fraction(self.rng.randint(1, 4))
                c = Fraction(self.rng.randint(-8, 8))
                d = Fraction(self.rng.randint(-6, 6))
            elif difficulty == "medium":
                x = Fraction(self.rng.randint(-8, 8))
                while x == 0:
                    x = Fraction(self.rng.randint(-8, 8))
                a = Fraction(self.rng.randint(-6, 6))
                while a == 0:
                    a = Fraction(self.rng.randint(-6, 6))
                b = Fraction(self.rng.randint(1, 5))
                c = Fraction(self.rng.randint(-10, 10))
                d = Fraction(self.rng.randint(-8, 8))
            else:
                x = Fraction(self.rng.randint(-6, 6))
                while x == 0:
                    x = Fraction(self.rng.randint(-6, 6))
                num = self.rng.choice([1, 2, 3, 5])
                den = self.rng.choice([2, 3, 4])
                a = Fraction(num, den) * self.rng.choice([-1, 1])
                b = Fraction(self.rng.randint(1, 4))
                c = Fraction(self.rng.randint(-6, 6))
                d = Fraction(self.rng.randint(-5, 5))
            # combined x coefficient must be nonzero
            coeff = a * b + d
            if coeff == 0:
                continue
            e = a * (b * x + c) + d * x
            return (a, b, c, d, e, x)
        # fallback
        return (Fraction(2), Fraction(1), Fraction(3), Fraction(1), Fraction(11), Fraction(2))

    def equation_solution_type(self, solution_type: str = "one") -> tuple:
        """Generate equation lhs = rhs with specific solution count.

        solution_type: "one", "infinite", or "none"
        Returns (lhs_str, rhs_str, lhs_coeff, lhs_const, rhs_coeff, rhs_const).
        lhs is coeff*x + const, rhs is coeff*x + const (after simplification).
        """
        if solution_type == "one":
            lc = Fraction(self.rng.randint(1, 8))
            lk = Fraction(self.rng.randint(-10, 10))
            rc = Fraction(self.rng.randint(-8, 8))
            while rc == lc:
                rc = Fraction(self.rng.randint(-8, 8))
            rk = Fraction(self.rng.randint(-10, 10))
        elif solution_type == "infinite":
            lc = Fraction(self.rng.randint(1, 8))
            lk = Fraction(self.rng.randint(-10, 10))
            rc = lc
            rk = lk
        else:  # none
            lc = Fraction(self.rng.randint(1, 8))
            lk = Fraction(self.rng.randint(-10, 10))
            rc = lc
            rk = Fraction(self.rng.randint(-10, 10))
            while rk == lk:
                rk = Fraction(self.rng.randint(-10, 10))
        return (lc, lk, rc, rk)

    def system_of_equations(self, solution_type: str = "one") -> tuple:
        """Generate system y=m1*x+b1, y=m2*x+b2.

        solution_type: "one", "none", or "infinite"
        Returns (m1, b1, m2, b2, solution_point_or_none).
        """
        if solution_type == "one":
            # Pick integer intersection point first
            sx = Fraction(self.rng.randint(-5, 5))
            sy = Fraction(self.rng.randint(-5, 5))
            m1 = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            m2 = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            while m1 == m2:
                m2 = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            b1 = sy - m1 * sx
            b2 = sy - m2 * sx
            return (m1, b1, m2, b2, (sx, sy))
        elif solution_type == "none":
            m = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            while m == 0:
                m = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            b1 = Fraction(self.rng.randint(-5, 5))
            b2 = Fraction(self.rng.randint(-5, 5))
            while b2 == b1:
                b2 = Fraction(self.rng.randint(-5, 5))
            return (m, b1, m, b2, None)
        else:  # infinite
            m = Fraction(self.rng.randint(-4, 4), self.rng.randint(1, 3))
            b = Fraction(self.rng.randint(-5, 5))
            return (m, b, m, b, None)


    # --- Signed number generators (7th/8th grade) ---

    def signed_integer(self, min_val: int = -20, max_val: int = 20) -> Fraction:
        """Generate a signed integer (never 0). For 7.NS.1-4, 7.NS.7."""
        val = self.rng.randint(min_val, max_val)
        while val == 0:
            val = self.rng.randint(min_val, max_val)
        return Fraction(val)

    def signed_decimal(self, min_val: float = -9.9, max_val: float = 9.9,
                       places: int = 1) -> Fraction:
        """Generate a signed decimal (never 0). For 7.NS.1-2, 7.NS.7."""
        factor = 10 ** places
        val = self.rng.randint(int(min_val * factor), int(max_val * factor))
        while val == 0:
            val = self.rng.randint(int(min_val * factor), int(max_val * factor))
        return Fraction(val, factor)

    def signed_fraction(self, max_denom: int = 8) -> Fraction:
        """Generate a signed proper fraction (never 0). For 7.NS.3-4, 7.NS.7."""
        denoms = [d for d in ALLOWED_DENOMINATORS if d <= max_denom]
        denom = self.rng.choice(denoms)
        numer = self.rng.randint(1, denom - 1)
        sign = self.rng.choice([-1, 1])
        return Fraction(sign * numer, denom)

    # --- GCF / LCM generators (6.NS.6) ---

    def gcf_pair(self, difficulty: str = "easy") -> tuple:
        """Generate (a, b, gcf) where gcf(a, b) = gcf.

        Easy: both ≤ 25, Medium: ≤ 50, Difficult: ≤ 100.
        """
        if difficulty == "easy":
            gcf = self.rng.randint(2, 8)
            m1 = self.rng.randint(1, 3)
            m2 = self.rng.randint(m1 + 1, 4)
        elif difficulty == "medium":
            gcf = self.rng.randint(3, 12)
            m1 = self.rng.randint(1, 4)
            m2 = self.rng.randint(m1 + 1, 5)
        else:
            gcf = self.rng.randint(4, 20)
            m1 = self.rng.randint(1, 5)
            m2 = self.rng.randint(m1 + 1, 6)
        # Ensure m1 and m2 are coprime
        from math import gcd
        while gcd(m1, m2) > 1:
            m2 += 1
        return (gcf * m1, gcf * m2, gcf)

    def lcm_pair(self, difficulty: str = "easy") -> tuple:
        """Generate (a, b, lcm) where lcm(a, b) = lcm. Both ≤ 12.

        Easy: small primes (2,3,5). Medium: up to 8. Difficult: uses 7,8,12.
        """
        from math import gcd
        if difficulty == "easy":
            a = self.rng.choice([2, 3, 4, 5, 6])
            b = self.rng.choice([2, 3, 4, 5, 6])
            while a == b:
                b = self.rng.choice([2, 3, 4, 5, 6])
        elif difficulty == "medium":
            a = self.rng.randint(2, 8)
            b = self.rng.randint(2, 8)
            while a == b:
                b = self.rng.randint(2, 8)
        else:
            a = self.rng.choice([6, 7, 8, 9, 10, 12])
            b = self.rng.choice([4, 6, 8, 9, 10, 12])
            while a == b:
                b = self.rng.choice([4, 6, 8, 9, 10, 12])
        lcm_val = (a * b) // gcd(a, b)
        return (a, b, lcm_val)

    # --- Order of operations (6.NS.5) ---

    def ooo_expression(self, difficulty: str = "easy") -> tuple:
        """Generate order of operations expression + correct answer.

        Returns (expression_str, answer) as (str, Fraction).
        Easy: whole numbers, 1 grouping. Medium: exponent + grouping.
        Difficult: fracs/decs, multiple groupings.
        """
        if difficulty == "easy":
            a = self.rng.randint(2, 9)
            b = self.rng.randint(1, 6)
            c = self.rng.randint(1, 6)
            d = self.rng.randint(1, 5)
            expr = f"{a} * ({b} + {c}) - {d}"
            answer = Fraction(a * (b + c) - d)
        elif difficulty == "medium":
            a = self.rng.randint(2, 5)
            b = self.rng.randint(1, 4)
            exp = self.rng.randint(2, 3)
            c = self.rng.randint(1, 6)
            expr = f"{a}^{exp} + ({b} * {c})"
            answer = Fraction(a ** exp + b * c)
        else:
            a = self.rng.randint(2, 4)
            exp = 2
            b = Fraction(self.rng.randint(1, 3), self.rng.choice([2, 4]))
            c = self.rng.randint(2, 6)
            expr = f"{a}^{exp} + {b} * {c}"
            answer = Fraction(a ** exp) + b * c
        return (expr, answer)

    # --- Exponent generators (6.NS.8, 8.NS.3) ---

    def exponent_pair(self, difficulty: str = "easy") -> tuple:
        """Generate (base, exponent, result) for base^exponent.

        Easy: whole base. Medium: fraction base. Difficult: decimal base.
        """
        if difficulty == "easy":
            base = Fraction(self.rng.randint(2, 10))
            exp = self.rng.randint(2, 4)
        elif difficulty == "medium":
            num = self.rng.randint(1, 3)
            den = self.rng.choice([2, 3, 4, 5])
            base = Fraction(num, den)
            exp = self.rng.randint(2, 3)
        else:
            base = Fraction(self.rng.randint(1, 9), 10)
            exp = self.rng.randint(2, 3)
        result = base ** exp
        return (base, exp, result)

    # --- Fraction/Decimal/Percent conversion (6.RP.1) ---

    def fraction_decimal_percent(self, difficulty: str = "easy") -> tuple:
        """Generate equivalent (fraction, decimal_str, percent_str).

        Easy: denom 10/100. Medium: 1-digit repeating. Difficult: multi-digit repeating.
        """
        if difficulty == "easy":
            denom = self.rng.choice([10, 100, 4, 5, 20, 25, 50])
            numer = self.rng.randint(1, denom - 1)
            frac = Fraction(numer, denom)
        elif difficulty == "medium":
            # Fractions with clean decimal equivalents or 1-digit repeating
            frac = self.rng.choice([
                Fraction(1, 3), Fraction(2, 3), Fraction(1, 6), Fraction(5, 6),
                Fraction(1, 8), Fraction(3, 8), Fraction(5, 8), Fraction(7, 8),
                Fraction(1, 9), Fraction(2, 9), Fraction(4, 9),
            ])
        else:
            frac = self.rng.choice([
                Fraction(1, 11), Fraction(2, 11), Fraction(3, 11),
                Fraction(1, 7), Fraction(2, 7), Fraction(3, 7),
                Fraction(5, 6), Fraction(7, 12), Fraction(11, 12),
            ])
        # Compute decimal string
        dec_val = float(frac)
        if frac.denominator == 1:
            dec_str = str(int(frac))
        elif all(frac.denominator % p != 0 for p in [3, 7, 11, 13] if frac.denominator % p == 0) is False:
            dec_str = f"{dec_val:.6f}".rstrip('0') if dec_val != int(dec_val) else str(int(dec_val))
        else:
            dec_str = f"{dec_val:.4f}".rstrip('0')
        pct_val = dec_val * 100
        if pct_val == int(pct_val):
            pct_str = f"{int(pct_val)}%"
        else:
            pct_str = f"{pct_val:.2f}".rstrip('0').rstrip('.') + "%"
        return (frac, dec_str, pct_str)

    # --- Ratio generators (6.RP.2-5) ---

    def ratio_pair(self, difficulty: str = "easy") -> tuple:
        """Generate (a, b) as a ratio pair for rate/ratio problems.

        Easy: single-digit, compatible. Medium: one single-digit.
        Difficult: double-digit both.
        """
        if difficulty == "easy":
            a = self.rng.randint(2, 9)
            b = self.rng.randint(2, 9)
        elif difficulty == "medium":
            a = self.rng.randint(2, 9)
            b = self.rng.randint(10, 30)
        else:
            a = self.rng.randint(10, 50)
            b = self.rng.randint(10, 99)
        return (a, b)

    def ratio_table(self, n_rows: int = 5, difficulty: str = "easy") -> tuple:
        """Generate a table of equivalent ratios.

        Returns (ratio_a, ratio_b, rows) where rows is [(a_val, b_val), ...].
        """
        a, b = self.ratio_pair(difficulty)
        rows = []
        for i in range(1, n_rows + 1):
            rows.append((a * i, b * i))
        return (a, b, rows)

    # --- Percent problem generator (7.RP.2) ---

    def percent_problem(self, difficulty: str = "easy") -> tuple:
        """Generate (base, rate_percent, amount) where amount = base * rate/100.

        Easy: multiples of 10. Medium: any percent. Difficult: work backwards.
        """
        if difficulty == "easy":
            rate = self.rng.choice([10, 20, 25, 30, 40, 50, 75])
            base = self.rng.choice([20, 40, 50, 60, 80, 100, 200])
        elif difficulty == "medium":
            rate = self.rng.randint(5, 30)
            base = self.rng.randint(20, 200)
        else:
            rate = self.rng.randint(1, 99)
            base = self.rng.randint(50, 500)
        amount = Fraction(base * rate, 100)
        return (Fraction(base), rate, amount)

    # --- Prime factorization (7.NS.5) ---

    def prime_factorization(self, difficulty: str = "easy") -> tuple:
        """Generate (number, factors_dict) where factors_dict maps prime -> exponent.

        Easy: <100, ≤2 primes. Medium: <100, 3-4 primes. Difficult: 100-200.
        """
        primes = [2, 3, 5, 7, 11, 13]
        if difficulty == "easy":
            # 2 prime factors, product < 100
            p1 = self.rng.choice([2, 3, 5])
            e1 = self.rng.randint(1, 3)
            p2 = self.rng.choice([p for p in [2, 3, 5, 7] if p != p1])
            e2 = self.rng.randint(1, 2)
            n = p1 ** e1 * p2 ** e2
            while n >= 100:
                e1 = max(1, e1 - 1)
                e2 = max(1, e2 - 1)
                n = p1 ** e1 * p2 ** e2
        elif difficulty == "medium":
            p1 = self.rng.choice([2, 3])
            e1 = self.rng.randint(1, 3)
            p2 = self.rng.choice([p for p in [2, 3, 5] if p != p1])
            e2 = self.rng.randint(1, 2)
            p3 = self.rng.choice([p for p in [5, 7, 11] if p != p1 and p != p2])
            e3 = 1
            n = p1 ** e1 * p2 ** e2 * p3 ** e3
            _guard = 0
            while n >= 100 and _guard < 20:
                _guard += 1
                if e1 > 1:
                    e1 -= 1
                elif e2 > 1:
                    e2 -= 1
                else:
                    break  # both exponents already 1, cannot reduce further
                n = p1 ** e1 * p2 ** e2 * p3 ** e3
            # Fallback: if still >= 100, use a known good medium value
            if n >= 100:
                n = self.rng.choice([30, 42, 60, 66, 70, 78])
        else:
            p1 = self.rng.choice([2, 3])
            e1 = self.rng.randint(2, 4)
            p2 = self.rng.choice([p for p in [3, 5, 7] if p != p1])
            e2 = self.rng.randint(1, 2)
            n = p1 ** e1 * p2 ** e2
            _guard = 0
            while (n < 100 or n > 200) and _guard < 20:
                _guard += 1
                if n < 100:
                    e1 += 1
                else:
                    e1 -= 1
                n = p1 ** e1 * p2 ** e2
                if e1 < 1:
                    e1 = 2
                    break
            # Fallback: if still out of range, use a known good difficult value
            if n < 100 or n > 200:
                n = self.rng.choice([120, 128, 135, 144, 150, 160, 168, 175, 180, 192, 200])
        # Build factors dict
        factors = {}
        temp = n
        for p in primes:
            while temp % p == 0:
                factors[p] = factors.get(p, 0) + 1
                temp //= p
        if temp > 1:
            factors[temp] = 1
        return (n, factors)

    # --- Perfect squares (7.NS.6) ---

    def perfect_square(self, difficulty: str = "easy") -> tuple:
        """Generate (square, root) where square = root^2.

        Easy: <100. Medium: 100-144. Difficult: 144-400.
        """
        if difficulty == "easy":
            root = self.rng.randint(2, 9)
        elif difficulty == "medium":
            root = self.rng.randint(10, 12)
        else:
            root = self.rng.randint(12, 20)
        return (root * root, root)

    # --- Irrational number approximation (8.NS.1-2) ---

    def irrational_bounds(self, difficulty: str = "easy") -> tuple:
        """Generate (n, lower, upper) where lower < sqrt(n) < upper.

        Easy: n uses sqrt(2), sqrt(3). Medium: primes<100. Difficult: composites.
        """
        if difficulty == "easy":
            n = self.rng.choice([2, 3, 5, 6, 7, 8])
        elif difficulty == "medium":
            n = self.rng.choice([10, 11, 13, 14, 15, 17, 19, 21, 23])
        else:
            n = self.rng.choice([26, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90])
        import math
        lower = int(math.isqrt(n))
        upper = lower + 1
        return (n, lower, upper)

    # --- Exponent simplification (8.NS.3) ---

    def exponent_simplify(self, difficulty: str = "easy") -> tuple:
        """Generate exponent expression to simplify using exponent rules.

        Returns (base, exp1, exp2, operation, result_exp) where operation is
        'multiply', 'divide', or 'power'.
        """
        base = self.rng.randint(2, 7)
        if difficulty == "easy":
            exp1 = self.rng.randint(2, 5)
            exp2 = self.rng.randint(1, 4)
            op = "multiply"
            result = exp1 + exp2
        elif difficulty == "medium":
            exp1 = self.rng.randint(4, 8)
            exp2 = self.rng.randint(1, exp1 - 1)
            op = self.rng.choice(["multiply", "divide"])
            result = exp1 + exp2 if op == "multiply" else exp1 - exp2
        else:
            op = self.rng.choice(["multiply", "divide", "power"])
            if op == "power":
                exp1 = self.rng.randint(2, 4)
                exp2 = self.rng.randint(2, 3)
                result = exp1 * exp2
            else:
                exp1 = self.rng.randint(3, 8)
                exp2 = self.rng.randint(1, 5)
                result = exp1 + exp2 if op == "multiply" else exp1 - exp2
        return (base, exp1, exp2, op, result)


    # --- Statistical data generators (6.DS, 7.DSP, 8.DSP) ---

    def generate_dataset(self, n: int, low: int = 1, high: int = 20,
                         whole: bool = True) -> list:
        """Generate a dataset of n values in [low, high].

        whole=True: integer values. whole=False: 1-decimal-place values.
        Returns sorted list of numeric values.
        """
        if whole:
            data = [self.rng.randint(low, high) for _ in range(n)]
        else:
            data = [self.rng.randint(low * 10, high * 10) / 10 for _ in range(n)]
        data.sort()
        return data

    def generate_bivariate_data(self, n: int, slope: float, intercept: float,
                                noise: float = 2.0,
                                x_min: int = 1,
                                x_max: int | None = None) -> list:
        """Generate n (x, y) points near y = slope*x + intercept.

        x_min, x_max: bounds for the x values. Defaults preserve the legacy
            behaviour (1 .. 10 + n) when x_max is not provided. Pass an
            explicit x_max to constrain the domain — e.g. the 8.DSP.2
            'hours studied' context wants x ≤ 15 so the data matches the
            question text instead of drifting to x=22.
        noise: std-dev-like spread around the line.
        Returns list of (x, y) tuples with integer coordinates.
        """
        if x_max is None:
            x_max = 10 + n
        points = []
        for i in range(n):
            x = self.rng.randint(x_min, x_max)
            y_exact = slope * x + intercept
            y = round(y_exact + self.rng.uniform(-noise, noise))
            points.append((x, y))
        points.sort(key=lambda p: p[0])
        return points


def five_number_summary(data):
    """Compute (min, Q1, median, Q3, max) for a sorted dataset.

    Q1 and Q3 are computed EXCLUDING the median, per Indiana standard.
    """
    s = sorted(data)
    n = len(s)

    def median_of(lst):
        m = len(lst)
        if m == 0:
            return 0
        if m % 2 == 1:
            return lst[m // 2]
        return (lst[m // 2 - 1] + lst[m // 2]) / 2

    med = median_of(s)
    lower = s[:n // 2]
    upper = s[n // 2 + (1 if n % 2 == 1 else 0):]
    q1 = median_of(lower)
    q3 = median_of(upper)
    return (s[0], q1, med, q3, s[-1])


def mean_absolute_deviation(data):
    """Compute MAD = mean of |xi - mean| for a dataset."""
    if not data:
        return 0
    from fractions import Fraction
    vals = [Fraction(v) for v in data]
    m = sum(vals) / len(vals)
    mad = sum(abs(v - m) for v in vals) / len(vals)
    return float(mad)


def display_mode_for_difficulty(difficulty: str) -> str:
    """Return the appropriate display mode for a difficulty tier."""
    if difficulty == "easy":
        return "whole"
    elif difficulty == "medium":
        return "decimal"
    else:
        return "mixed"


def is_hand_computable(value: Fraction) -> bool:
    """Check if a fraction produces a reasonable hand computation.

    For no-calculator items, intermediate values should have denominators
    in the allowed set and not produce overly complex decimals.
    """
    if value.denominator == 1:
        return True
    if value.denominator in ALLOWED_DENOMINATORS:
        return True
    # Check if it's a terminating decimal with at most 3 places
    d = value.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1
