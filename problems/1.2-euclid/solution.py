from math import gcd, isqrt

def euclid(m, n):
    """Тройка Евклида: (m² − n², 2mn, m² + n²)."""
    return m*m - n*n, 2*m*n, m*m + n*n

def from_euclid(a, b, c):
    """Есть ли m > n > 0 с {m² − n², 2mn} = {a, b} (порядок катетов не важен)?"""
    for x, y in ((a, b), (b, a)):
        if y % 2 == 0:
            for m in range(1, isqrt(c) + 1):
                n2 = m*m - x
                if n2 > 0 and isqrt(n2)**2 == n2 and 2*m*isqrt(n2) == y:
                    return True
    return False

def square_or_twice(k):
    """k = s² или k = 2s²?"""
    return isqrt(k)**2 == k or (k % 2 == 0 and isqrt(k // 2)**2 == k // 2)

N = 1000
triples = [(a, b, isqrt(a*a + b*b)) for a in range(1, N) for b in range(a + 1, N)
           if isqrt(a*a + b*b)**2 == a*a + b*b and isqrt(a*a + b*b) <= N]

# Теорема 2: формула даёт тройку ⇔ НОД = s² или 2s²
for a, b, c in triples:
    assert from_euclid(a, b, c) == square_or_twice(gcd(a, b))

bad = [t for t in triples if not from_euclid(*t)]
print(f"троек с c ≤ {N} (a < b): {len(triples)}; формула Евклида не даёт: {len(bad)}")
print("критерий «НОД = s² или 2s²» подтверждён для всех")
print("самые маленькие контрпримеры:", bad[:4])
