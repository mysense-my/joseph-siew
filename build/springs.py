"""Port of Framer Motion's spring maths (motion.mjs bundled with the template) -> CSS linear() easings.

Duration/bounce springs ("type: spring, duration, bounce") are resolved to stiffness/damping with the same
Newton solve Framer uses (`ut`), then sampled. Framer ends such springs at exactly `duration` (it snaps to the
target when t >= duration), so the CSS duration is the stated duration.
Stiffness/damping springs run until Framer's rest thresholds are met; that duration is computed here too.
"""
import math

EL = 0.001  # Framer's `el` (settle threshold used by the duration solver)


def solve_duration_spring(duration, bounce, mass=1.0):
    """Framer `ut()` : returns stiffness, damping for a duration (s) + bounce spring."""
    o = 1 - bounce
    o = min(max(o, 0.05), 1.0)
    e = min(max(duration, 0.01), 10.0)
    n = 0.0  # initial velocity

    if o < 1:
        def ct(t, z):
            return t * math.sqrt(1 - z * z)

        def f(t):
            r = t * o
            i = r * e
            a = r - n
            s = ct(t, o)
            return EL - a / s * math.exp(-i)

        def df(t):
            r = t * o * e
            a = r * n + n
            s = o * o * t * t * e
            c = math.exp(-r)
            l = ct(t * t, o)
            sign = -1 if (-f(t) + EL > 0) else 1
            return sign * ((a - s) * c) / l
    else:
        def f(t):
            r = math.exp(-t * e)
            i = (t - n) * e + 1
            return -EL + r * i

        def df(t):
            return math.exp(-t * e) * ((n - t) * (e * e))

    w = 5 / e
    for _ in range(1, 12):
        w -= f(w) / df(w)
    stiffness = w * w * mass
    damping = o * 2 * math.sqrt(mass * stiffness)
    return stiffness, damping


def spring_fn(stiffness, damping, mass=1.0, frm=0.0, to=1.0, velocity=0.0):
    """Framer `pt()` position function, time in seconds."""
    zeta = damping / (2 * math.sqrt(stiffness * mass))
    w0 = math.sqrt(stiffness / mass)
    g = to - frm
    m = velocity
    if zeta < 1:
        x = w0 * math.sqrt(1 - zeta * zeta)
        S = (m + zeta * w0 * g) / x
        return lambda t: to - math.exp(-zeta * w0 * t) * (S * math.sin(x * t) + g * math.cos(x * t))
    if zeta == 1:
        return lambda t: to - math.exp(-w0 * t) * (g + (m + w0 * g) * t)
    e = w0 * math.sqrt(zeta * zeta - 1)

    def y(t):
        r = min(e * t, 300)
        return to - math.exp(-zeta * w0 * t) * ((m + zeta * w0 * g) * math.sinh(r) + e * g * math.cosh(r)) / e
    return y


def physics_duration(stiffness, damping, mass=1.0, distance=100.0):
    """When a stiffness/damping spring reaches rest by Framer's default thresholds (px-scale motion)."""
    granular = abs(distance) < 5
    rest_speed = 0.01 if granular else 2.0
    rest_delta = 0.005 if granular else 0.5
    y = spring_fn(stiffness, damping, mass, 0, distance)
    t = 0.0
    dt = 0.001
    while t < 20:
        v = (y(t + dt) - y(t)) / dt
        if abs(v) <= rest_speed and abs(distance - y(t)) <= rest_delta:
            return t
        t += 0.002
    return 20.0


def linear_easing(fn, duration, samples=None):
    """Sample fn(t) (0->1 target) over [0,duration] as a CSS linear() string."""
    samples = samples or max(24, int(duration * 60))
    pts = []
    for i in range(samples + 1):
        t = duration * i / samples
        v = fn(t) if i < samples else 1.0
        pts.append(round(v, 4))
    # drop redundant points (linear runs) to keep strings short
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if abs((a + c) / 2 - b) > 0.0006:
            out.append(b)
        else:
            out.append(b)
    out.append(pts[-1])
    return 'linear(' + ', '.join(('%g' % v) for v in out) + ')'


def duration_spring(duration, bounce):
    k, d = solve_duration_spring(duration, bounce)
    return linear_easing(spring_fn(k, d), duration), duration


def physics_spring(stiffness, damping, mass=1.0, distance=34.0):
    dur = physics_duration(stiffness, damping, mass, distance)
    return linear_easing(spring_fn(stiffness, damping, mass), dur), dur


# every spring the template uses
SPRINGS = {
    # text effects
    'text-03': (0.3, 0.0),     # hero H1 letters
    'text-04': (0.4, 0.0),     # heading letter flip, word reveals
    'text-05': (0.5, 0.0),     # heading paragraph lines
    # component variants / scroll-section triggers
    'soft-04': (0.4, 0.2),     # icons roll, CTA photos, appointment content, nav, social, doctor card
    'faq-08': (0.8, 0.4),      # FAQ open/close
}

if __name__ == '__main__':
    for name, (d, b) in SPRINGS.items():
        k, dmp = solve_duration_spring(d, b)
        print(name, 'stiffness %.1f damping %.2f' % (k, dmp))
    s, dur = physics_spring(320, 48, 1, 34)
    print('button', round(dur, 3))
