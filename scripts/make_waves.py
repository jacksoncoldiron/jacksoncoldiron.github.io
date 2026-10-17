"""
Generate the site's signature "contour wave" artwork as SVG.

Soft gradient bands (water -> dune lavender -> sand) overlaid with fine white
contour lines, in the spirit of topographic maps and the Carbon Wave cover.

Usage:
    python3 scripts/make_waves.py            # writes assets/waves-*.svg
    python3 scripts/make_waves.py --seed 7   # try a different wave shape

Edit the BAND colors below to re-tint the artwork. Keep them light/pastel so
dark text stays readable on top.
"""

import argparse
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

# Top -> bottom. Pastel tints derived from the ploen palette + water tones.
HERO_BANDS = [
    "#B9DAD9",  # seafoam mist
    "#A6C4DD",  # light periwinkle
    "#BDB7DB",  # blue-lavender
    "#D6C2D8",  # dune lavender
    "#B4D0DC",  # sky
    "#A9D3CC",  # seafoam
    "#C6DDD3",  # pale sage
    "#EBDCCB",  # dune sand
    "#F6D9BC",  # apricot sand
]

BANNER_BANDS = ["#B9DAD9", "#A6C4DD", "#C7BBDB", "#D6C2D8", "#B4D0DC", "#C6DDD3", "#F1DCC4"]


def catmull_rom_path(pts):
    """Smooth path through points (Catmull-Rom converted to cubic Bezier)."""
    d = [f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}")
    return "".join(d)


def make_boundaries(n, width, height, rng, amp, step=40):
    """n+1 flowing boundary curves; neighbours share phase so bands 'flow'."""
    xs = list(range(-step, width + 2 * step, step))
    phase1, phase2, phase3 = rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    lam1, lam2, lam3 = width * rng.uniform(0.9, 1.3), width * rng.uniform(0.45, 0.6), width * rng.uniform(0.22, 0.3)
    curves = []
    for k in range(n + 1):
        base = -0.14 * height + k * (1.28 * height / n)
        drift = k * 0.55
        a = amp * (0.6 + 0.8 * abs(math.sin(k * 1.3 + phase3)))
        ys = [
            base
            + a * math.sin(2 * math.pi * x / lam1 + phase1 + drift)
            + 0.45 * a * math.sin(2 * math.pi * x / lam2 + phase2 - drift * 0.6)
            + 0.15 * a * math.sin(2 * math.pi * x / lam3 + phase3 + drift * 1.4)
            for x in xs
        ]
        curves.append(list(zip(xs, ys)))
    return curves


def lerp_curve(a, b, t):
    return [(x, ya + (yb - ya) * t) for (x, ya), (_, yb) in zip(a, b)]


def build_svg(bands, width, height, seed, amp, lines_per_band, line_color, line_opacity,
              fill=True, line_width=1.0):
    rng = random.Random(seed)
    curves = make_boundaries(len(bands), width, height, rng, amp)
    defs, body = [], []

    for i, color in enumerate(bands):
        top, bot = curves[i], curves[i + 1]
        if fill:
            nxt = bands[min(i + 1, len(bands) - 1)]
            gid = f"g{i}"
            defs.append(
                f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0.35">'
                f'<stop offset="0" stop-color="{color}"/>'
                f'<stop offset="0.55" stop-color="{nxt}" stop-opacity="0.9"/>'
                f'<stop offset="1" stop-color="{color}"/></linearGradient>'
            )
            # band polygon: top curve left->right, bottom curve right->left
            back = list(reversed(bot))
            d = catmull_rom_path(top) + "L" + catmull_rom_path(back)[1:] + "Z"
            body.append(f'<path d="{d}" fill="url(#{gid})"/>')
        for j in range(lines_per_band):
            t = j / lines_per_band
            body.append(f'<path d="{catmull_rom_path(lerp_curve(top, bot, t))}"/>')

    line_group_open = (
        f'<g fill="none" stroke="{line_color}" stroke-opacity="{line_opacity}" '
        f'stroke-width="{line_width}" vector-effect="non-scaling-stroke" stroke-linecap="round">'
    )
    fills = [p for p in body if 'fill="url' in p]
    strokes = [p.replace("/>", ' vector-effect="non-scaling-stroke"/>') for p in body if 'fill="url' not in p]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'preserveAspectRatio="xMidYMid slice" role="img" aria-label="Flowing contour waves">'
        f'<defs>{"".join(defs)}</defs>'
        + (f'<rect width="{width}" height="{height}" fill="{bands[0]}"/>' if fill else "")
        + "".join(fills)
        + line_group_open + "".join(strokes) + "</g></svg>"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)

    files = {
        "waves-hero.svg": build_svg(HERO_BANDS, 1600, 900, args.seed, 70, 7, "#FFFFFF", 0.62),
        "waves-banner.svg": build_svg(BANNER_BANDS, 1600, 320, args.seed + 3, 34, 6, "#FFFFFF", 0.6),
        # faint line-only texture for light section backgrounds
        "waves-lines.svg": build_svg(HERO_BANDS, 1600, 900, args.seed + 5, 60, 6, "#3F5671", 0.07,
                                     fill=False),
    }
    for name, svg in files.items():
        (OUT / name).write_text(svg)
        print(f"wrote assets/{name}  ({len(svg) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
