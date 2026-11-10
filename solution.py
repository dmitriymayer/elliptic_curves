from fractions import Fraction as Q

def add(P, R, n):
    """Сумма точек на y² = x³ − n²x методом секущих и касательных."""
    if P is None: return R
    if R is None: return P
    (x1, y1), (x2, y2) = P, R
    if x1 == x2 and y1 == -y2:
        return None                               # точка на бесконечности
    if P == R:
        lam = (3*x1*x1 - n*n) / (2*y1)            # касательная
    else:
        lam = (y2 - y1) / (x2 - x1)               # секущая
    x3 = lam*lam - x1 - x2                        # третья точка пересечения…
    y3 = lam*(x1 - x3) - y1                       # …отражённая относительно оси x
    return (x3, y3)

def triangle(P, n):
    """Точка (x, y), y ≠ 0  →  прямоугольный треугольник площади n."""
    x, y = P
    return abs((x*x - n*n) / y), abs(2*n*x / y), abs((x*x + n*n) / y)

def digits(q):
    return max(len(str(abs(q.numerator))), len(str(q.denominator)))

# Стартовые точки найдены перебором маленьких целых x
start = {5: (Q(-4), Q(6)), 6: (Q(-3), Q(9)), 7: (Q(25), Q(120))}

for n, P in start.items():
    assert P[1]**2 == P[0]**3 - n*n*P[0]
    print(f"n = {n}, P = ({P[0]}, {P[1]})")
    R = P
    for k in range(1, 9):
        a, b, c = triangle(R, n)
        assert a*a + b*b == c*c and a*b/2 == n          # честный треугольник
        print(f"  {k}P: цифр в x — {digits(R[0]):>4};  треугольник с гипотенузой {c}"
              if k < 3 else f"  {k}P: цифр в x — {digits(R[0]):>4}")
        R = add(R, P, n)
