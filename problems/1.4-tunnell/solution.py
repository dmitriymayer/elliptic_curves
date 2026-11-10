from fractions import Fraction
from math import gcd, isqrt

def count(n, a, b, c):
    """Число целых точек на эллипсоиде a·x² + b·y² + c·z² = n."""
    total = 0
    for x in range(-isqrt(n // a), isqrt(n // a) + 1):
        for z in range(-isqrt(n // c), isqrt(n // c) + 1):
            r = n - a*x*x - c*z*z
            if r >= 0 and r % b == 0:
                y = isqrt(r // b)
                if y*y == r // b:
                    total += 1 if y == 0 else 2
    return total

def tunnell(n):
    """Критерий Таннелла для бесквадратного n."""
    if n % 2:                                    # эллипсоиды 2x² + y² + 8z², 2x² + y² + 32z²
        A, B = count(n, 2, 1, 8), count(n, 2, 1, 32)
    else:                                        # чётный случай
        A, B = count(n // 2, 4, 1, 8), count(n // 2, 4, 1, 32)
    return A == 2 * B

def squarefree(n):
    return all(n % (d*d) for d in range(2, isqrt(n) + 1))

def divisors_2n(n):
    return [d for d in range(1, 2*n + 1) if (2*n) % d == 0 and squarefree(d)]

def triangle(n, L):
    """Ищем точку x = d·a²/e² на кривой y² = x³ − n²x (d | 2n, a, e ≤ L)
    и превращаем её в прямоугольный треугольник площади n."""
    for e in range(1, L + 1):
        for a in range(1, L + 1):
            if gcd(a, e) > 1:
                continue
            for d in divisors_2n(n) + [-d for d in divisors_2n(n)]:
                v = d * (d*a*a - n*e*e) * (d*a*a + n*e*e)
                if v > 0 and isqrt(v)**2 == v:
                    x = Fraction(d*a*a, e*e)
                    y = Fraction(isqrt(v) * a, e**3)
                    return sorted(abs(s) for s in ((x*x - n*n) / y, 2*n*x / y, (x*x + n*n) / y))
    return None

N, L = 200, 60
ns = [n for n in range(1, N + 1) if squarefree(n)]
yes = [n for n in ns if tunnell(n)]
found = {n: triangle(n, L) for n in yes}
found = {n: t for n, t in found.items() if t}

for n, (a, b, c) in found.items():
    assert a*a + b*b == c*c and a*b/2 == n           # треугольник честный

print(f"бесквадратных n ≤ {N}: {len(ns)}, из них A = 2B: {len(yes)}")
print(f"треугольник найден для {len(found)}: {list(found)[:12]} …")
print(f"A = 2B, треугольник с a, e ≤ {L} не найден: {[n for n in yes if n not in found]}")
print("n = 5:", *found[5], "  n = 6:", *found[6])
