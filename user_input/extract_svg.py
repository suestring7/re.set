#!/usr/bin/env python3
"""Generate final SVG path strings for frontSVG() and backSVG()."""
from PIL import Image
import numpy as np
import math

IMG = 'user_input/muscle_distribution.png'
img = Image.open(IMG).convert('RGB')
arr = np.array(img)

front = arr[70:870, 130:590]
back  = arr[70:870, 880:1340]

# Calibrated coordinate transforms
# Front: figure center x_crop=330 → SVG x=45; arm tips x_crop=168↔330+162 → SVG 4↔86
def fx(cx): return round(45 + (cx - 330) * 0.253, 1)
def fy(cy): return round(0.247 * cy - 2.1,        1)
# Back: figure center x_crop=124 → SVG x=45; use same y scale
def bx(cx): return round(45 + (cx - 124) * 0.253, 1)
def by_(cy): return round(0.247 * cy - 2.1,        1)

def mask_for(crop, hex_c, tol=22):
    r,g,b = int(hex_c[1:3],16),int(hex_c[3:5],16),int(hex_c[5:7],16)
    d = np.max(np.abs(crop.astype(np.int16)-np.array([r,g,b],np.int16)),axis=2)
    return d<=tol

def apply_range(mask, y0=0, y1=9999, x0=0, x1=9999):
    m = mask.copy()
    m[:y0,:]=0; m[y1:,:]=0; m[:,:x0]=0; m[:,x1:]=0
    return m

def row_scan(mask, step=2):
    h,w = mask.shape
    L,R = [],[]
    for y in range(0,h,step):
        xs = np.where(mask[y])[0]
        if len(xs):
            L.append((int(xs.min()),y))
            R.append((int(xs.max()),y))
    if not L: return []
    return L + list(reversed(R))

def rdp(pts, eps):
    if len(pts) < 3: return list(pts)
    def d(p,a,b):
        if a==b: return math.hypot(p[0]-a[0],p[1]-a[1])
        dx,dy = b[0]-a[0],b[1]-a[1]
        den = math.hypot(dx,dy)
        return abs(dy*p[0]-dx*p[1]+b[0]*a[1]-b[1]*a[0])/den if den else 0
    ds=[d(pts[i],pts[0],pts[-1]) for i in range(1,len(pts)-1)]
    if not ds: return [pts[0],pts[-1]]
    mi=max(range(len(ds)),key=lambda i:ds[i])+1
    if ds[mi-1]>eps:
        return rdp(pts[:mi+1],eps)[:-1]+rdp(pts[mi:],eps)
    return [pts[0],pts[-1]]

def path_from_mask(mask, tx, ty, eps, mirror=False):
    c = row_scan(mask)
    if not c: return ''
    pts = [(tx(cx),ty(cy)) for cx,cy in c]
    if mirror: pts = [(90-sx,sy) for sx,sy in pts]
    s = rdp(pts, eps)
    if len(s)<3: return ''
    return 'M'+' L'.join(f"{p[0]},{p[1]}" for p in s)+' Z'

def bilateral(crop, color, tol, y0, y1, x0, xcenter, tx, ty, eps=4.0):
    """Extract left-of-center mask, produce (L_path, R_path_mirrored)."""
    m = mask_for(crop, color, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=xcenter)
    if m.sum() < 80: return '',''
    L = path_from_mask(m, tx, ty, eps)
    R = path_from_mask(m, tx, ty, eps, mirror=True)
    return L, R

def center_muscle(crop, color, tol, y0, y1, x0, x1, tx, ty, eps=4.0):
    m = mask_for(crop, color, tol)
    m = apply_range(m, y0=y0, y1=y1, x0=x0, x1=x1)
    if m.sum() < 80: return ''
    return path_from_mask(m, tx, ty, eps)

CX_F = 330  # front figure center x in crop
CX_B = 124  # back figure center x in crop

# ═══════════════════════════════════════════════════════════════════
# FRONT MUSCLES
# ═══════════════════════════════════════════════════════════════════

F = {}
# Chest (pecs) — salmon
L,R = bilateral(front,'#f08c78',22, 130,265, 204,CX_F, fx,fy, eps=4.0)
F['chest_L'], F['chest_R'] = L, R

# Anterior deltoid — orange-tan (shoulder front, below/beside chest)
L,R = bilateral(front,'#f0b464',22, 193,305, 195,CX_F, fx,fy, eps=4.0)
F['delt_L'], F['delt_R'] = L, R

# Abs — green (center, no bilateral split)
F['abs'] = center_muscle(front,'#b4c88c',22, 228,440, 260,402, fx,fy, eps=5.0)

# Obliques — yellow-green
L,R = bilateral(front,'#a0b478',22, 228,425, 255,CX_F, fx,fy, eps=5.0)
F['obl_L'], F['obl_R'] = L, R

# Forearms — lavender, lateral arm area
L,R = bilateral(front,'#a0a0c8',22, 290,425, 160,230, fx,fy, eps=3.5)
F['fore_L'], F['fore_R'] = L, R

# Quads — teal
L,R = bilateral(front,'#78c8c8',22, 380,590, 241,CX_F, fx,fy, eps=5.0)
F['quad_L'], F['quad_R'] = L, R

# Adductors — blue, inner thigh (narrow x range near center)
F['add'] = center_muscle(front,'#8cb4dc',22, 387,580, 295,365, fx,fy, eps=5.0)

# Calves/shins front — blue-lavender
L,R = bilateral(front,'#8ca0c8',22, 575,780, 240,CX_F, fx,fy, eps=4.0)
F['calf_L'], F['calf_R'] = L, R

# ═══════════════════════════════════════════════════════════════════
# BACK MUSCLES
# ═══════════════════════════════════════════════════════════════════

B = {}
# Trapezius — pink, upper back (full width shape)
B['trap'] = center_muscle(back,'#dc8ca0',22, 58,200, 20,240, bx,by_, eps=4.0)

# Rear deltoids / upper lats — orange #f0a064
L,R = bilateral(back,'#f0a064',22, 135,350, 0,CX_B, bx,by_, eps=5.0)
B['rdelt_L'], B['rdelt_R'] = L, R

# Mid/lower lats — orange-red #f08c64
L,R = bilateral(back,'#f08c64',22, 135,365, 0,CX_B, bx,by_, eps=5.0)
B['lat_L'], B['lat_R'] = L, R

# Triceps — orange-red #dc7864 at y=134-280 (arm area, x near edges)
L,R = bilateral(back,'#dc7864',22, 134,285, 0,CX_B, bx,by_, eps=4.0)
B['tri_L'], B['tri_R'] = L, R

# Glutes — peach
L,R = bilateral(back,'#c8a08c',22, 350,540, 10,CX_B, bx,by_, eps=4.0)
B['glute_L'], B['glute_R'] = L, R

# Hamstrings — teal
L,R = bilateral(back,'#78c8c8',22, 455,615, 30,CX_B, bx,by_, eps=4.0)
B['ham_L'], B['ham_R'] = L, R

# Calves back — lavender
L,R = bilateral(back,'#a0a0c8',22, 580,800, 0,CX_B, bx,by_, eps=4.0)
B['bcalf_L'], B['bcalf_R'] = L, R

# ═══════════════════════════════════════════════════════════════════
# OUTPUT: JS function bodies
# ═══════════════════════════════════════════════════════════════════

def mk(id, path, mirror=False):
    if not path: return f'    // {id}: no path\n'
    return f'    ${{mkShape(\'{id}\',`<path d="{path}" fill="FILL" ${{S}} class="muscle-region"><title>TIP</title></path>`)}}\n'

def mk2(id, L, R):
    if not L or not R: return f'    // {id}: missing path\n'
    return (f'    ${{mkShape(\'{id}\',`<path d="{L}" fill="FILL" ${{S}} class="muscle-region"><title>TIP</title></path>'
            f'<path d="{R}" fill="FILL" ${{S}} class="muscle-region"><title>TIP</title></path>`)}}\n')

print("// ──────────────────────────────────────────────────────")
print("// PASTE INTO frontSVG() — replace '<!-- muscles -->' section")
print("// ──────────────────────────────────────────────────────")
print()
print("    <!-- muscles -->")
sys_out = ""
sys_out += mk2('chest',    F['chest_L'],  F['chest_R'])
sys_out += mk2('shoulders',F['delt_L'],   F['delt_R'])
sys_out += "    ${mkShape('biceps',`<rect x=\"5\" y=\"51\" width=\"10\" height=\"21\" rx=\"5\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect><rect x=\"75\" y=\"51\" width=\"10\" height=\"21\" rx=\"5\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect>`)}\n"
sys_out += mk2('forearms', F['fore_L'],   F['fore_R'])
sys_out += mk2('obliques', F['obl_L'],    F['obl_R'])
sys_out += mk('abs',       F['abs'])
sys_out += "    ${mkShape('hip_flexors',`<rect x=\"26\" y=\"84\" width=\"38\" height=\"8\" rx=\"3\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect>`)}\n"
sys_out += mk2('quads',    F['quad_L'],   F['quad_R'])
sys_out += mk('adductors', F['add'])
sys_out += mk2('calves',   F['calf_L'],   F['calf_R'])
print(sys_out)

print()
print("// ──────────────────────────────────────────────────────")
print("// PASTE INTO backSVG() — replace '<!-- muscles -->' section")
print("// ──────────────────────────────────────────────────────")
print()
print("    <!-- muscles -->")
bk_out = ""
bk_out += "    ${mkShape('neck',`<rect x=\"41\" y=\"22\" width=\"8\" height=\"9\" rx=\"2\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect>`)}\n"
bk_out += mk('trapezius',     B['trap'])
bk_out += mk2('mid_back',     B['rdelt_L'],  B['rdelt_R'])
bk_out += mk2('shoulders_back',B['lat_L'],   B['lat_R'])
bk_out += mk2('lats',         B['lat_L'],   B['lat_R'])
bk_out += mk2('triceps',      B['tri_L'],   B['tri_R'])
bk_out += "    ${mkShape('forearms',`<rect x=\"5\" y=\"74\" width=\"9\" height=\"17\" rx=\"4\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect><rect x=\"76\" y=\"74\" width=\"9\" height=\"17\" rx=\"4\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect>`)}\n"
bk_out += "    ${mkShape('lower_back',`<rect x=\"37\" y=\"66\" width=\"7\" height=\"20\" rx=\"3\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect><rect x=\"46\" y=\"66\" width=\"7\" height=\"20\" rx=\"3\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></rect>`)}\n"
bk_out += mk2('glutes',       B['glute_L'], B['glute_R'])
bk_out += "    ${mkShape('glutes_med',`<path d=\"M20,84 C14,86 12,94 17,99 C20,103 26,102 27,97 L25,85 Z\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></path><path d=\"M70,84 C76,86 78,94 73,99 C70,103 64,102 63,97 L65,85 Z\" fill=\"FILL\" ${S} class=\"muscle-region\"><title>TIP</title></path>`)}\n"
bk_out += mk2('hamstrings',   B['ham_L'],   B['ham_R'])
bk_out += mk2('calves',       B['bcalf_L'], B['bcalf_R'])
print(bk_out)

print()
print("// Pixel counts for reference:")
for k,v in F.items(): print(f"//   F.{k}: {v[:60] if v else 'empty'}...")
for k,v in B.items(): print(f"//   B.{k}: {v[:60] if v else 'empty'}...")
