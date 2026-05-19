#!/usr/bin/env python3
"""Extract muscle contour shapes from muscle_distribution.png -> SVG path data."""
from PIL import Image
import numpy as np
import math

IMG = '/Users/suestring/Desktop/Playground/re.set/user_input/muscle_distribution.png'
img = Image.open(IMG).convert('RGB')
arr = np.array(img)

# Crop bounds (in original image)
front = arr[70:870, 130:590]   # 800H × 460W
back  = arr[70:870, 880:1340]  # 800H × 460W

# ── Auto-detect figure bounds ────────────────────────────────────────────
# Background is near-white. Find figure bounding box by excluding very bright pixels.
def fig_bounds(crop):
    """Find bounding box of the drawn figure (non-white background)."""
    gray = crop.mean(axis=2)
    # Non-background: not very bright and not very dark (body outline)
    non_bg = (gray < 240) & (gray > 20)
    ys = np.where(non_bg.any(axis=1))[0]
    xs = np.where(non_bg.any(axis=0))[0]
    if not len(ys) or not len(xs):
        return 0, crop.shape[0], 0, crop.shape[1]
    return int(ys[0]), int(ys[-1]), int(xs[0]), int(xs[-1])

fy0, fy1, fx0, fx1 = fig_bounds(front)
by0, by1, bx0, bx1 = fig_bounds(back)
print(f"Front figure bounds in crop: y={fy0}-{fy1}, x={fx0}-{fx1}")
print(f"Back  figure bounds in crop: y={by0}-{by1}, x={bx0}-{bx1}")

# SVG coordinate mapping (viewBox "0 0 90 210")
SVG_W, SVG_H = 90, 210

def make_scale(y0, y1, x0, x1):
    sx = lambda cx: round((cx - x0) / (x1 - x0) * SVG_W, 2)
    sy = lambda cy: round((cy - y0) / (y1 - y0) * SVG_H, 2)
    return sx, sy

FSX, FSY = make_scale(fy0, fy1, fx0, fx1)
BSX, BSY = make_scale(by0, by1, bx0, bx1)

# ── Color mask ────────────────────────────────────────────────────────────
def mask_for(crop, hex_c, tol=22):
    r, g, b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
    d = np.max(np.abs(crop.astype(np.int16) - np.array([r,g,b], dtype=np.int16)), axis=2)
    return d <= tol

# ── Row-scan contour extraction ───────────────────────────────────────────
def row_scan(mask):
    """Extract boundary polygon via row scanning: left edge down, right edge up."""
    h, w = mask.shape
    # Downsample rows for speed and fewer points
    L, R = [], []
    step = max(1, h // 150)
    for y in range(0, h, step):
        xs = np.where(mask[y])[0]
        if len(xs):
            L.append((int(xs.min()), y))
            R.append((int(xs.max()), y))
    if not L:
        return []
    return L + list(reversed(R))

# ── RDP simplification ────────────────────────────────────────────────────
def rdp(pts, eps=2.0):
    if len(pts) < 3:
        return list(pts)
    def dist(p, a, b):
        if a == b:
            return math.hypot(p[0]-a[0], p[1]-a[1])
        dx, dy = b[0]-a[0], b[1]-a[1]
        den = math.hypot(dx, dy)
        if den == 0: return 0
        return abs(dy*p[0] - dx*p[1] + b[0]*a[1] - b[1]*a[0]) / den
    dists = [dist(pts[i], pts[0], pts[-1]) for i in range(1, len(pts)-1)]
    if not dists:
        return [pts[0], pts[-1]]
    mi = max(range(len(dists)), key=lambda i: dists[i]) + 1
    if dists[mi-1] > eps:
        return rdp(pts[:mi+1], eps)[:-1] + rdp(pts[mi:], eps)
    return [pts[0], pts[-1]]

def to_path(poly_crop, sx, sy, eps=2.0):
    """Convert crop-pixel polygon to SVG path string d="""
    if not poly_crop:
        return ''
    svg_pts = [(sx(cx), sy(cy)) for cx, cy in poly_crop]
    simp = rdp(svg_pts, eps)
    if len(simp) < 3:
        return ''
    d = 'M' + ' L'.join(f"{p[0]},{p[1]}" for p in simp) + ' Z'
    return d

def lr_split(mask, cx=None):
    cx = cx or mask.shape[1] // 2
    L = mask.copy(); L[:, cx:] = 0
    R = mask.copy(); R[:, :cx] = 0
    return L, R

# ── Show all significant colors ───────────────────────────────────────────
def show_colors(crop, label, n=20):
    print(f"\n{label} — significant colors:")
    q = (crop.astype(np.uint32) // 20 * 20)
    packed = q[:,:,0]*65536 + q[:,:,1]*256 + q[:,:,2]
    unique, counts = np.unique(packed.ravel(), return_counts=True)
    order = np.argsort(counts)[::-1]
    shown = 0
    for i in order:
        if shown >= n: break
        c = counts[i]
        if c < 200: break
        v = unique[i]
        r,g,b = (v>>16)&0xFF, (v>>8)&0xFF, v&0xFF
        if r > 200 and g > 200 and b > 200: continue  # skip near-white background
        if r < 30 and g < 30 and b < 30: continue     # skip near-black outlines
        print(f"  #{r:02x}{g:02x}{b:02x}  {c:6d}px")
        shown += 1

show_colors(front, "FRONT")
show_colors(back, "BACK")

print("\n")
print("=" * 70)
print("FRONT MUSCLES")
print("=" * 70)

# cx_mid: where to split left/right in crop
cx_mid_f = (fx0 + fx1) // 2

front_defs = [
    # name, hex, tol, bilateral
    ('neck',       '#dc8ca0', 22, False),   # pink — neck (sternocleidomastoid)
    ('chest',      '#f08c78', 22, True),    # salmon — pectoralis
    ('shoulders',  '#f0b464', 22, True),    # orange-tan — deltoid front
    ('biceps',     '#dc7864', 22, True),    # orange-red — biceps area
    ('abs',        '#b4c88c', 22, False),   # green — rectus abdominis
    ('obliques',   '#a0b478', 22, True),    # yellow-green — external obliques
    ('forearms',   '#a0a0c8', 22, True),    # lavender — forearms (+ shins)
    ('quads',      '#78c8c8', 22, True),    # teal — quadriceps
    ('adductors',  '#8cb4dc', 22, False),   # blue — adductors
    ('calves',     '#8ca0c8', 22, True),    # blue-lavender — shins/calves front
]

for name, color, tol, bilateral in front_defs:
    m = mask_for(front, color, tol)
    total = m.sum()
    if total < 200:
        print(f"\n// {name}: no data ({total}px)")
        continue
    if bilateral:
        Lm, Rm = lr_split(m, cx_mid_f)
        for side, sm in [('L', Lm), ('R', Rm)]:
            if sm.sum() < 100: continue
            c = row_scan(sm)
            p = to_path(c, FSX, FSY)
            print(f"\n// {name}_{side} ({int(sm.sum())}px)")
            print(f"// PATH: {p}")
    else:
        c = row_scan(m)
        p = to_path(c, FSX, FSY)
        print(f"\n// {name} ({total}px)")
        print(f"// PATH: {p}")

print("\n")
print("=" * 70)
print("BACK MUSCLES")
print("=" * 70)

cx_mid_b = (bx0 + bx1) // 2

back_defs = [
    ('neck_b',       '#dc8ca0', 22, False),  # pink — neck/trapezius top
    ('trapezius',    '#dc8ca0', 22, False),  # same pink — trap
    ('deltoids_b',   '#f0a064', 22, True),   # orange — rear deltoid + lats
    ('glutes',       '#c8a08c', 22, True),   # peach — gluteus maximus
    ('hamstrings',   '#78c8c8', 22, True),   # teal — hamstrings
    ('calves_b',     '#a0a0c8', 22, True),   # lavender — gastrocnemius
]

for name, color, tol, bilateral in back_defs:
    m = mask_for(back, color, tol)
    total = m.sum()
    if total < 200:
        print(f"\n// {name}: no data ({total}px)")
        continue
    if bilateral:
        Lm, Rm = lr_split(m, cx_mid_b)
        for side, sm in [('L', Lm), ('R', Rm)]:
            if sm.sum() < 100: continue
            c = row_scan(sm)
            p = to_path(c, BSX, BSY)
            print(f"\n// {name}_{side} ({int(sm.sum())}px)")
            print(f"// PATH: {p}")
    else:
        c = row_scan(m)
        p = to_path(c, BSX, BSY)
        print(f"\n// {name} ({total}px)")
        print(f"// PATH: {p}")

print("\nDone.")
