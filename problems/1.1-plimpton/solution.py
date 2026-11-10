from fractions import Fraction
from math import gcd, isqrt

def is_regular(n: int) -> bool:
    """Делится только на 2, 3 и 5: у такого числа конечная обратная в 60-ричной системе."""
    for p in (2, 3, 5):
        while n % p == 0:
            n //= p
    return n == 1

def triple(t: Fraction) -> tuple[int, int, int]:
    """Прямая из (-1, 0) с наклоном t = q/p даёт тройку (p² − q², 2pq, p² + q²)."""
    q, p = t.numerator, t.denominator
    a, b, c = p*p - q*q, 2*p*q, p*p + q*q
    g = gcd(a, gcd(b, c))
    return a // g, b // g, c // g

def parameter(a: int, b: int, c: int) -> Fraction:
    """Обратно: наклон прямой из (-1, 0) в точку (a/c, b/c)."""
    return Fraction(b, a + c)

# На табличке записаны короткий катет и гипотенуза
plimpton = {3: (4601, 6649), 4: (12709, 18541), 10: (4961, 8161)}

for row, (a, c) in plimpton.items():
    b = isqrt(c*c - a*a)              # длинный катет восстанавливаем
    t = parameter(a, b, c)
    assert triple(t) == (a, b, c)
    reg = is_regular(t.numerator) and is_regular(t.denominator)
    print(f"строка {row:>2}: t = {t},  p и q регулярны: {reg}")
