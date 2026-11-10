from fractions import Fraction as Q

def f(x, y, k):
    """Кубика C_k:  x³ + 12x + 4y³ − 3k·y(x² − 4) = 0."""
    return x**3 + 12*x + 4*y**3 - 3*k*y*(x*x - 4)

def restrict(P, d, k):
    """Коэффициенты c0..c3 многочлена t ↦ f(P + t·d) (кубика ⇒ степень ≤ 3)."""
    v = [f(P[0] + t*d[0], P[1] + t*d[1], k) for t in range(4)]
    d1 = [v[i+1] - v[i] for i in range(3)]
    d2 = [d1[1] - d1[0], d1[2] - d1[1]]
    c3 = Q(d2[1] - d2[0], 6); c2 = Q(d2[0], 2) - 3*c3; c1 = d1[0] - c2 - c3
    return v[0], c1, c2, c3

# три точки и прямые, которые пересекают кривую только в них (касательные)
FLEX = {
    'A': ((-2, 2), lambda k: (2, -(1 + k))),   # касательная (1+k)x + 2y + 2k − 2 = 0
    'B': ((0, 0),  lambda k: (k, -1)),         # касательная x + ky = 0
    'C': ((2, -2), lambda k: (2, -(1 + k))),   # касательная (1+k)x + 2y + 2 − 2k = 0
}
print("Ограничение f на касательную в перегибе:  f(P + t·d) = c0 + c1·t + c2·t² + c3·t³")
for k in [Q(-3), Q(-1), Q(0), Q(1, 2), Q(2)]:
    row = []
    for name, (P, d) in FLEX.items():
        c = restrict(P, d(k), k)
        assert c[:3] == (0, 0, 0) and c[3] == (4 if name != 'B' else -4) * (1 - k**3)
        row.append(f"{name}: {c[3]}·t³")
    print(f"  k = {str(k):>4}:  " + ",   ".join(row))
print("  на одной прямой y = −x:", all(P[0] + P[1] == 0 for P, _ in FLEX.values()))

# Других вещественных перегибов нет: ищем все решения системы
#   f = 0,  Φ = f_xx·f_y² − 2 f_xy·f_x·f_y + f_yy·f_x² = 0   (Φ = 0 ⇔ кривизна равна нулю)
def grad_hess(x, y, k):
    fx, fy = 3*x*x + 12 - 6*k*x*y, 12*y*y - 3*k*(x*x - 4)
    return fx, fy, 6*x - 6*k*y, -6*k*x, 24*y

def system(x, y, k):
    fx, fy, fxx, fxy, fyy = grad_hess(x, y, k)
    return f(x, y, k), fxx*fy*fy - 2*fxy*fx*fy + fyy*fx*fx

def newton(x, y, k, steps=60):
    for _ in range(steps):
        F0, G0 = system(x, y, k); h = 1e-7
        Fx, Gx = [(a - b) / h for a, b in zip(system(x + h, y, k), (F0, G0))]
        Fy, Gy = [(a - b) / h for a, b in zip(system(x, y + h, k), (F0, G0))]
        det = Fx*Gy - Fy*Gx
        if abs(det) < 1e-14: return None
        x, y = x - (F0*Gy - Fy*G0) / det, y - (Fx*G0 - F0*Gx) / det
        if abs(x) > 1e4 or abs(y) > 1e4: return None
    F0, G0 = system(x, y, k)
    return (x, y) if abs(F0) < 1e-8 and abs(G0) < 1e-6 else None

for k in [-3, -1, 0, 0.5, 2]:
    found = set()
    for i in range(-30, 31):
        for j in range(-30, 31):
            r = newton(i / 3, j / 3, k)
            if r: found.add((round(r[0], 6) + 0.0, round(r[1], 6) + 0.0))
    print(f"k = {k:>4}: вещественные перегибы", sorted(found))
