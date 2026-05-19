#!/usr/bin/env python3
"""Explore muscle color spatial layout."""
from PIL import Image
import numpy as np

IMG = '/Users/suestring/Desktop/Playground/re.set/user_input/muscle_distribution.png'
img = Image.open(IMG).convert('RGB')
arr = np.array(img)

front = arr[70:870, 130:590]
back  = arr[70:870, 880:1340]

def mask_for(crop, hex_c, tol=22):
    r,g,b = int(hex_c[1:3],16), int(hex_c[3:5],16), int(hex_c[5:7],16)
    d = np.max(np.abs(crop.astype(np.int16) - np.array([r,g,b], np.int16)), axis=2)
    return d <= tol

def bbox(mask):
    ys = np.where(mask.any(axis=1))[0]
    xs = np.where(mask.any(axis=0))[0]
    if not len(ys): return None
    return int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())

# Find the actual figure silhouette bounds
# The background should be near-white
# Let's look for the body outline by finding the topmost/bottommost non-bright pixels
# in the center column
CX = 230  # center x in crop
col = front[:, CX, :]  # center column pixels
non_white = np.where(col.max(axis=1) < 230)[0]
if len(non_white):
    print(f"Front center col: non-white rows {non_white[0]}–{non_white[-1]}")

# Look at specific row profiles to understand figure extent
# Check 10% from top/bottom/left/right to find bounds
for y_frac in [0.05, 0.1, 0.15, 0.9, 0.95]:
    y = int(y_frac * 800)
    row = front[y, :, :]
    non_white = np.where(row.max(axis=1) < 230)[0]
    if len(non_white):
        print(f"  Front row y={y}: non-white cols {non_white[0]}–{non_white[-1]}")

print()
print("=== FRONT: Color bounding boxes ===")
front_colors = {
    'neck':      ('#dc8ca0', 22),
    'chest':     ('#f08c78', 22),
    'deltoids':  ('#f0b464', 22),
    'biceps_area': ('#dc7864', 22),
    'abs':       ('#b4c88c', 22),
    'obliques':  ('#a0b478', 22),
    'lavender':  ('#a0a0c8', 22),   # forearms + shins
    'teal':      ('#78c8c8', 22),   # quads
    'blue':      ('#8cb4dc', 22),   # adductors
    'blu_lav':   ('#8ca0c8', 22),   # shins
}
for name, (color, tol) in front_colors.items():
    m = mask_for(front, color, tol)
    b = bbox(m)
    if b:
        y0,y1,x0,x1 = b
        cy = int(np.mean(np.where(m)[0]))
        cx = int(np.mean(np.where(m)[1]))
        print(f"  {name:<15} {int(m.sum()):6d}px  y={y0:3d}-{y1:3d}  x={x0:3d}-{x1:3d}  centroid=({cy},{cx})")
    else:
        print(f"  {name:<15} no data")

print()
print("=== FRONT: Lavender (#a0a0c8) column distribution ===")
m = mask_for(front, '#a0a0c8', 22)
# Show which y-bands have the most pixels
bands = [(i*100, (i+1)*100, int(m[i*100:(i+1)*100].sum())) for i in range(8)]
for y0,y1,cnt in bands:
    print(f"  y={y0:3d}-{y1:3d}: {cnt}px  {'▓'*(cnt//100)}")

# Check if left/right halves are separate
print("\n  Left (x<230) vs Right (x>=230) by y-band:")
for y0,y1,_ in bands:
    L = int(m[y0:y1, :230].sum())
    R = int(m[y0:y1, 230:].sum())
    print(f"  y={y0:3d}-{y1:3d}: L={L:4d} R={R:4d}")

print()
print("=== FRONT: Teal (#78c8c8) column distribution ===")
m = mask_for(front, '#78c8c8', 22)
for y0,y1,_ in bands:
    L = int(m[y0:y1, :230].sum())
    R = int(m[y0:y1, 230:].sum())
    print(f"  y={y0:3d}-{y1:3d}: L={L:4d} R={R:4d}")

print()
print("=== BACK: Color bounding boxes ===")
back_colors = {
    'pink_trap':  ('#dc8ca0', 22),
    'orange_lat': ('#f0a064', 22),
    'peach_glut': ('#c8a08c', 22),
    'teal_ham':   ('#78c8c8', 22),
    'lavender_c': ('#a0a0c8', 22),
    'f08c64':     ('#f08c64', 22),  # what is this?
    'dc7864':     ('#dc7864', 22),  # what is this?
    'f0b464':     ('#f0b464', 22),  # orange-tan back
}
for name, (color, tol) in back_colors.items():
    m = mask_for(back, color, tol)
    b = bbox(m)
    if b:
        y0,y1,x0,x1 = b
        cy = int(np.mean(np.where(m)[0]))
        cx = int(np.mean(np.where(m)[1]))
        print(f"  {name:<15} {int(m.sum()):6d}px  y={y0:3d}-{y1:3d}  x={x0:3d}-{x1:3d}  centroid=({cy},{cx})")
    else:
        print(f"  {name:<15} no data")

print()
print("=== BACK: Lavender (#a0a0c8) distribution ===")
m = mask_for(back, '#a0a0c8', 22)
for y0,y1,_ in bands:
    L = int(m[y0:y1, :230].sum())
    R = int(m[y0:y1, 230:].sum())
    print(f"  y={y0:3d}-{y1:3d}: L={L:4d} R={R:4d}")

print()
print("=== BACK: Orange (#f0a064) distribution ===")
m = mask_for(back, '#f0a064', 22)
for y0,y1,_ in bands:
    L = int(m[y0:y1, :230].sum())
    R = int(m[y0:y1, 230:].sum())
    print(f"  y={y0:3d}-{y1:3d}: L={L:4d} R={R:4d}")

print()
print("=== Figure actual bounds (by muscle colors) ===")
# Use all muscle colors to find actual figure extent
all_muscle = np.zeros(front.shape[:2], dtype=bool)
for color, tol in front_colors.values():
    all_muscle |= mask_for(front, color, tol)
b = bbox(all_muscle)
if b:
    y0,y1,x0,x1 = b
    print(f"  Front muscle region: y={y0}-{y1}, x={x0}-{x1}")
    print(f"  This spans {y1-y0}px height, {x1-x0}px width")

# Check where head/neck is in crop
print(f"\nNeck centroid y in crop: ~{int(np.mean(np.where(mask_for(front,'#dc8ca0',22))[0]))}")
print("This will map to SVG y=22-31 (neck rect in current SVG)")
