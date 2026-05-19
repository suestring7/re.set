#!/usr/bin/env python3
"""
Final muscle contour extraction.
Calibrated coordinate mapping:
  x_svg = 45 + (x_crop - 330) * 0.253   (figure center x_crop=330 → SVG x=45)
  y_svg = 0.247 * y_crop - 2.1           (calibrated from neck & quads landmarks)
"""
from PIL import Image
import numpy as np
import math

IMG = 'user_input/muscle_distribution.png'
img = Image.open(IMG).convert('RGB')
arr = np.array(img)

front = arr[70:870, 130:590]
back  = arr[70:870, 880:1340]

# Coordinate transforms
CX = 330   # figure center x in front crop
BX = 124   # figure center x in back crop

def fx(cx):  return round(45 + (cx - CX) * 0.253, 1)
def fy(cy):  return round(0.247 * cy - 2.1,        1)
def bx(cx):  return round(45 + (cx - BX) * 0.258, 1)  # back: scale ~same
def by_(cy): return round(0.247 * cy - 2.1,        1)

def mask_for(crop, hex_c, tol=22):
    r,g,b = int(hex_c[1:3],16),int(hex_c[3:5],16),int(hex_c[5:7],16)
    d = np.max(np.abs(crop.astype(np.int16)-np.array([r,g,b],np.int16)),axis=2)
    return d<=tol

def apply_range(mask, y0=0, y1=None, x0=0, x1=None):
    """Restrict mask to a y/x bounding box."""
    m = mask.copy()
    if y0: m[:y0, :] = 0
    if y1: m[y1:, :] = 0
    if x0: m[:, :x0] = 0
    if x1: m[:, x1:] = 0
    return m

def row_scan(mask, step=3):
    h, w = mask.shape
    L, R = [], []
    for y in range(0, h, step):
        xs = np.where(mask[y])[0]
        if len(xs):
            L.append((int(xs.min()), y))
            R.append((int(xs.max()), y))
    if not L: return []
    return L + list(reversed(R))

def rdp(pts, eps=1.8):
    if len(pts) < 3: return list(pts)
    def d(p,a,b):
        if a==b: return math.hypot(p[0]-a[0],p[1]-a[1])
        dx,dy = b[0]-a[0],b[1]-a[1]
        den = math.hypot(dx,dy)
        return abs(dy*p[0]-dx*p[1]+b[0]*a[1]-b[1]*a[0])/den if den else 0
    ds = [d(pts[i],pts[0],pts[-1]) for i in range(1,len(pts)-1)]
    if not ds: return [pts[0],pts[-1]]
    mi = max(range(len(ds)),key=lambda i:ds[i])+1
    if ds[mi-1]>eps:
        return rdp(pts[:mi+1],eps)[:-1]+rdp(pts[mi:],eps)
    return [pts[0],pts[-1]]

def to_path(mask, tx, ty, eps=1.8, mirror=False):
    """Extract SVG path from mask. If mirror, flip the shape around SVG center x=45."""
    contour = row_scan(mask)
    if not contour: return ''
    pts = [(tx(cx), ty(cy)) for cx,cy in contour]
    if mirror:
        pts = [(90-sx, sy) for sx,sy in pts]
    simp = rdp(pts, eps)
    if len(simp) < 3: return ''
    return 'M'+' L'.join(f"{p[0]},{p[1]}" for p in simp)+' Z'

def bbox(mask):
    ys = np.where(mask.any(axis=1))[0]
    xs = np.where(mask.any(axis=0))[0]
    if not len(ys): return None
    return int(ys.min()),int(ys.max()),int(xs.min()),int(xs.max())

# ─────────────────────────────────────────────────────────────────────
# FRONT — extract LEFT half (x<330), mirror to get right half
# ─────────────────────────────────────────────────────────────────────
print("/* ============================================================")
print("   FRONT SVG — extracted muscle paths")
print("   Each bilateral muscle: LEFT path (x<45) + mirrored RIGHT path (x>45)")
print("   ============================================================ */\n")

def front_bilateral(name, hex_c, tol, y0, y1, x0=None, x1=330, eps=1.8):
    """Extract left-half mask, produce LEFT and mirrored RIGHT paths."""
    m = mask_for(front, hex_c, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=x1)
    px = m.sum()
    if px < 100:
        print(f"// {name}: no data")
        return None, None
    Lpath = to_path(m, fx, fy, eps)
    Rpath = to_path(m, fx, fy, eps, mirror=True)
    print(f"// {name} ({int(px)}px)")
    print(f"// L: {Lpath}")
    print(f"// R: {Rpath}")
    print()
    return Lpath, Rpath

def front_center(name, hex_c, tol, y0, y1, x0=None, x1=None, eps=1.8):
    """Extract center muscle (no bilateral split)."""
    m = mask_for(front, hex_c, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=x1)
    px = m.sum()
    if px < 100:
        print(f"// {name}: no data")
        return None
    p = to_path(m, fx, fy, eps)
    print(f"// {name} ({int(px)}px)")
    print(f"// PATH: {p}")
    print()
    return p

# Neck — center, small area at top
front_center('neck', '#dc8ca0', 22, y0=83, y1=155)

# Chest (pecs) — salmon, bilateral, upper torso
front_bilateral('chest', '#f08c78', 22, y0=130, y1=265, x0=200, x1=330)

# Deltoids (front) — orange-tan, bilateral, shoulder
front_bilateral('shoulders', '#f0b464', 22, y0=193, y1=305, x0=195, x1=330)

# Biceps — orange-red, bilateral, upper arm
front_bilateral('biceps', '#dc7864', 22, y0=130, y1=245, x0=195, x1=330)

# Abs — green, center
front_center('abs', '#b4c88c', 22, y0=228, y1=425, x0=258, x1=402)

# Obliques — yellow-green, bilateral
front_bilateral('obliques', '#a0b478', 22, y0=228, y1=425, x0=258, x1=330)

# Forearms — lavender, lateral arm area (y=295-420, left arm at x=160-230)
front_bilateral('forearms', '#a0a0c8', 22, y0=295, y1=420, x0=160, x1=230)

# Quads — teal, bilateral thigh
front_bilateral('quads', '#78c8c8', 22, y0=380, y1=590, x0=241, x1=330)

# Adductors — blue, inner thigh (center)
front_center('adductors', '#8cb4dc', 22, y0=387, y1=580, x0=270, x1=390)

# Calves/shins front — blue-lavender, lower leg
front_bilateral('calves_front', '#8ca0c8', 22, y0=580, y1=780, x0=240, x1=330)

# ─────────────────────────────────────────────────────────────────────
# BACK — same pattern
# ─────────────────────────────────────────────────────────────────────
print("\n/* ============================================================")
print("   BACK SVG — extracted muscle paths")
print("   ============================================================ */\n")

def back_bilateral(name, hex_c, tol, y0, y1, x0=None, x1=None, bx_limit=124, eps=1.8):
    """Extract left-half of back figure (x<bx_limit), mirror for right."""
    m = mask_for(back, hex_c, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=bx_limit if x1 is None else x1)
    px = m.sum()
    if px < 100:
        print(f"// {name}: no data")
        return None, None
    Lpath = to_path(m, bx, by_, eps)
    Rpath = to_path(m, bx, by_, eps, mirror=True)
    print(f"// {name} ({int(px)}px)")
    print(f"// L: {Lpath}")
    print(f"// R: {Rpath}")
    print()
    return Lpath, Rpath

def back_center(name, hex_c, tol, y0, y1, x0=None, x1=None, eps=1.8):
    m = mask_for(back, hex_c, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=x1)
    px = m.sum()
    if px < 100:
        print(f"// {name}: no data")
        return None
    p = to_path(m, bx, by_, eps)
    print(f"// {name} ({int(px)}px)")
    print(f"// PATH: {p}")
    print()
    return p

# Back figure center is at x_crop≈124
# Left half = x<124, Right half = x>124

# Trapezius — pink, upper back (spans across top)
back_center('trapezius', '#dc8ca0', 22, y0=58, y1=200, x0=20, x1=240)

# Rear deltoids / lats — orange, upper-mid back, bilateral
back_bilateral('deltoids_back', '#f0a064', 22, y0=135, y1=420, bx_limit=124)

# Also check #f08c64 and #f0b464 for back muscles
back_bilateral('lats_extra', '#f08c64', 22, y0=135, y1=380, bx_limit=124)

# Glutes — peach, bilateral
back_bilateral('glutes', '#c8a08c', 22, y0=350, y1=540, bx_limit=124)

# Hamstrings — teal, bilateral
back_bilateral('hamstrings', '#78c8c8', 22, y0=455, y1=610, bx_limit=124)

# Calves back — lavender, bilateral
back_bilateral('calves_back', '#a0a0c8', 22, y0=580, y1=800, bx_limit=124)

# ─────────────────────────────────────────────────────────────────────
# Print calibration check
# ─────────────────────────────────────────────────────────────────────
print("\n/* Calibration check:")
print(f"   fx(330)={fx(330)} (should be 45)")
print(f"   fx(168)={fx(168)} (should be ~4)")
print(f"   fy(118)={fy(118)} (neck centroid, should be ~26)")
print(f"   fy(490)={fy(490)} (quads centroid, should be ~119)")
print(f"   bx(124)={bx(124)} (should be 45)")
print("*/")
