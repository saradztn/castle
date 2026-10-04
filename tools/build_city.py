#!/usr/bin/env python3
"""
build_city.py — مولّد مدينة القلعة الساحلية عالي التفصيل (High-Detail)
Castle & Palace — MTA:SA | مبني لمطابقة الصورة المرجعية

المخرجات:
  build/castle_city.obj / .mtl      ← الهندسة + ربط الخامات
  build/polys.json                  ← للتصيير والفحص
  build/lamps.json                  ← مواضع المشاعل/الفوانيس لنظام إضاءة MTA
  build/spawns.json                 ← نقاط اللعب (بوابة، ساحة، مرفأ، أسوار…)
"""

import argparse, math, os, json, random
import numpy as np

TAU = math.tau
R = random.Random(20261004)

SEA = 0.0
PLATEAU = 110.0
# جرف شبه عمودي: (منسوب، معامل نصف القطر)
CLIFF = [(0.0, 1.000), (9.0, 0.992), (20.0, 0.968), (32.0, 0.938), (44.0, 0.905),
         (56.0, 0.872), (68.0, 0.840), (80.0, 0.807), (92.0, 0.772), (101.0, 0.745), (110.0, 0.722)]
BASE_RX, BASE_RY = 232.0, 284.0
WALL_RINGS = [(20.0, 15.0, 6.0, 0.955), (45.0, 13.0, 5.0, 0.885), (70.0, 11.0, 4.0, 0.845)]
BRIDGE = dict(arches=8, span=20.0, deck_w=9.0, deck_z=15.0)
LAMPS = []
SPAWNS = {}

# المادة: (الخامة، مقياس البلاطة، اللون، هل تُضيء ليًلا)
MAT = {
    "rock":       ("rock_cliff_strata",        9.0, (0.47, 0.45, 0.43), False),
    "rock_dark":  ("rock_cliff_strata",        9.0, (0.33, 0.32, 0.31), False),
    "grass":      ("terrain_grass",            8.0, (0.30, 0.41, 0.21), False),
    "granite":    ("stone_granite_wall",       4.5, (0.47, 0.46, 0.45), False),
    "granite_d":  ("stone_granite_wall",       4.5, (0.38, 0.37, 0.36), False),
    "sandstone":  ("stone_sandstone_ashlar",   4.0, (0.80, 0.70, 0.53), False),
    "sandstone_l":("stone_sandstone_ashlar",   3.0, (0.88, 0.79, 0.62), False),
    "plaster":    ("plaster_lime_town",        4.0, (0.82, 0.77, 0.68), False),
    "plaster_w":  ("plaster_lime_town",        4.0, (0.90, 0.86, 0.78), False),
    "slate":      ("roof_slate",               3.2, (0.30, 0.33, 0.38), False),
    "slate_d":    ("roof_slate",               3.2, (0.22, 0.25, 0.29), False),
    "terracotta": ("roof_tile_terracotta",     3.0, (0.66, 0.42, 0.28), False),
    "shingle":    ("roof_shingle_wood",        3.0, (0.47, 0.42, 0.35), False),
    "wood":       ("wood_oak_timber",          2.0, (0.42, 0.30, 0.19), False),
    "door":       ("wood_oak_door",            2.0, (0.34, 0.23, 0.14), False),
    "cobble":     ("stone_cobble_street",      4.0, (0.50, 0.48, 0.44), False),
    "flag":       ("stone_flagstone_floor",    4.0, (0.62, 0.60, 0.55), False),
    "quay":       ("stone_quay_granite",       4.0, (0.52, 0.51, 0.49), False),
    "water":      ("water_ocean",              9.0, (0.11, 0.30, 0.37), False),
    "water_d":    ("water_ocean",              9.0, (0.09, 0.26, 0.33), False),
    "foam":       ("water_foam_shore",         5.0, (0.93, 0.94, 0.95), False),
    "copper":     ("metal_copper_verdigris",   2.2, (0.30, 0.52, 0.42), False),
    "gilded":     ("metal_gilded_bronze",      1.2, (0.82, 0.68, 0.32), False),
    "marble":     ("marble_floor_light",       4.0, (0.90, 0.88, 0.82), False),
    "banner":     ("fabric_banner_heraldry",   3.0, (0.52, 0.14, 0.14), False),
    "dirt":       ("terrain_dirt_road",        4.0, (0.60, 0.53, 0.42), False),
    "glass":      ("glass_leaded_pane",        3.0, (0.55, 0.68, 0.66), False),
    "wglow":      ("glass_leaded_pane_emissive", 3.0, (1.00, 0.72, 0.38), True),
    "lampglow":   ("glass_leaded_pane_emissive", 2.0, (1.00, 0.78, 0.45), True),
    "iron":       ("metal_iron_forged",        2.0, (0.16, 0.16, 0.17), False),
    "moss":       ("decal_moss_patch",         3.0, (0.40, 0.47, 0.28), False),
    "leaf":       ("foliage_leaves",           3.0, (0.32, 0.45, 0.22), False),
    "tapestry":   ("fabric_tapestry",          3.5, (0.62, 0.50, 0.32), False),
    "props":      ("wood_props_kit",           2.5, (0.45, 0.33, 0.22), False),
}


class Mesh:
    def __init__(self):
        self.v, self.f, self.uv, self.mat = [], [], [], []
        self.emissive = {k: v[3] for k, v in MAT.items()}

    def add(self, verts, faces, mat):
        if not faces:
            return
        tile = MAT[mat][1]
        off = len(self.v)
        V = np.asarray(verts, dtype=np.float64)
        self.v.extend([tuple(p) for p in V])
        for fc in faces:
            if len(fc) < 3:
                continue
            P = V[list(fc)]
            n = np.cross(P[1] - P[0], P[2] - P[0])
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                continue
            n /= ln
            ax = int(np.argmax(np.abs(n)))
            i, j = [k for k in range(3) if k != ax]
            self.f.append([off + k for k in fc])
            self.uv.append([(float(p[i]) / tile, float(p[j]) / tile) for p in P])
            self.mat.append(mat)

    def export(self, base):
        os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
        with open(base + ".obj", "w") as f:
            f.write("# Castle & Palace — coastal castle-city (high detail)\n")
            f.write(f"mtllib {os.path.basename(base)}.mtl\n")
            for m in sorted(set(self.mat)):
                f.write(f"\nusemtl mat_{m}\n")
                for fc, mm in zip(self.f, self.mat):
                    if mm != m:
                        continue
                    for vi in fc:
                        x, y, z = self.v[vi]
                        f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
        with open(base + ".mtl", "w") as fh:
            for m, (tex, tile, col, _e) in MAT.items():
                fh.write(f"newmtl mat_{m}\nKd {col[0]:.3f} {col[1]:.3f} {col[2]:.3f}\n")
                fh.write(f"map_Kd textures/src/{tex}_albedo.png\n\n")
        print(f"  ✓ {base}.obj  ({len(self.f)} وجه، {len(self.v)} رأس)")


# ============ أدوات هندسية ============
def ring(n, rx, ry, cx=0.0, cy=0.0, phase=0.0, j=0.0):
    return [(cx + math.cos(phase + TAU * k / n) * rx * (1 + (R.uniform(-j, j) if j else 0)),
             cy + math.sin(phase + TAU * k / n) * ry * (1 + (R.uniform(-j, j) if j else 0))) for k in range(n)]


def prism(M, poly, z0, z1, mat, cap=True):
    n = len(poly)
    v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    f = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    if cap:
        f.append(list(range(n, 2 * n)))
    M.add(v, f, mat)


def box(M, x0, y0, z0, x1, y1, z1, mat, rot=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(rot), math.sin(rot)
    pts = [((x0 - cx) * c - (y0 - cy) * s + cx, (x0 - cx) * s + (y0 - cy) * c + cy),
           ((x1 - cx) * c - (y0 - cy) * s + cx, (x1 - cx) * s + (y0 - cy) * c + cy),
           ((x1 - cx) * c - (y1 - cy) * s + cx, (x1 - cx) * s + (y1 - cy) * c + cy),
           ((x0 - cx) * c - (y1 - cy) * s + cx, (x0 - cx) * s + (y1 - cy) * c + cy)]
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
    f = [[3, 2, 1, 0], [4, 5, 6, 7]] + [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)]
    M.add(v, f, mat)
    return pts


def cyl(M, cx, cy, r, z0, z1, mat, seg=16, cap=True, r_top=None):
    rt = r if r_top is None else r_top
    v = [(cx + math.cos(TAU * k / seg) * r, cy + math.sin(TAU * k / seg) * r, z0) for k in range(seg)]
    v += [(cx + math.cos(TAU * k / seg) * rt, cy + math.sin(TAU * k / seg) * rt, z1) for k in range(seg)]
    f = [[k, (k + 1) % seg, seg + (k + 1) % seg, seg + k] for k in range(seg)]
    if cap:
        f.append(list(range(seg, 2 * seg)))
    M.add(v, f, mat)


def cone(M, cx, cy, r, z0, z1, mat, seg=16):
    v = [(cx + math.cos(TAU * k / seg) * r, cy + math.sin(TAU * k / seg) * r, z0) for k in range(seg)]
    v.append((cx, cy, z1))
    M.add(v, [[k, (k + 1) % seg, seg] for k in range(seg)], mat)


def gable(M, x0, y0, x1, y1, z, rise, mat, oh=0.7, hip=False):
    """سقف جملوني/هرمي بسيط على المحور الأطول."""
    a0, b0, a1, b1 = x0 - oh, y0 - oh, x1 + oh, y1 + oh
    if (y1 - y0) >= (x1 - x0):
        m = (y0 + y1) / 2
        v = [(a0, b0, z), (a1, b0, z), (a1, b1, z), (a0, b1, z), (a0, m, z + rise), (a1, m, z + rise)]
        f = [[0, 1, 5, 4], [3, 4, 5, 2], [0, 4, 3], [1, 2, 5]]
    else:
        m = (x0 + x1) / 2
        v = [(a0, b0, z), (a1, b0, z), (a1, b1, z), (a0, b1, z), (m, b0, z + rise), (m, b1, z + rise)]
        f = [[1, 0, 4, 5], [4, 3, 2, 5], [0, 3, 4], [1, 5, 2]]
    M.add(v, f, mat)


def arch(M, x0, y0, z0, span, thick, depth, mat, seg=10, rot=0.0):
    """قوس نصف دائري (ككتلة مبنية من قطع صغيرة) — يُستخدم للجسور والقناطر."""
    r = span / 2
    for k in range(seg):
        a0, a1 = math.pi * k / seg, math.pi * (k + 1) / seg
        p0 = (math.cos(a0) * r, z0 + math.sin(a0) * r)
        p1 = (math.cos(a1) * r, z0 + math.sin(a1) * r)
        cx0, cz0 = x0 + p0[0], p0[1]
        cx1, cz1 = x0 + p1[0], p1[1]
        dx, dz = cx1 - cx0, cz1 - cz0
        L = math.hypot(dx, dz) or 1e-6
        nx, nz = -dz / L * thick / 2, dx / L * thick / 2
        box(M, min(cx0 - nx, cx1 - nx), y0, min(cz0 - nz, cz1 - nz),
            max(cx0 + nx, cx1 + nx), y0 + depth, max(cz0 + nz, cz1 + nz), mat, rot=rot)


def flying_buttress(M, x, y0, y1, z_low, z_high, w, mat):
    """دعامة طائرة: عمود + قوس داعم."""
    box(M, x - w / 2, y1 - 1.2, z_low, x + w / 2, y1 + 1.2, z_high + 3, mat)   # العضادة
    n = 6
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        x0 = x - w / 2 + (x + w / 2 - (x - w / 2)) * 0
        y0 = y0 + (y1 - y0) * t0
        y1b = y0 + (y1 - y0) * t1
        zz = z_low + (z_high - z_low) * (1 - math.sin(math.pi * (t0 + t1) / 2))
        box(M, x - 0.5, y0, zz, x + 0.5, y1b, zz + 0.8, mat)


def lamp(M, x, y, z, h=4.0, kind="torch"):
    """فانوس/مشعل + تسجيل موضعه لنظام إضاءة MTA."""
    if kind == "torch":
        cyl(M, x, y, 0.12, z, z + 0.9, "iron", seg=6)
        box(M, x - 0.35, y - 0.35, z + 0.9, x + 0.35, y + 0.35, z + 1.5, "lampglow")
        LAMPS.append(dict(x=x, y=y, z=z + 1.2, r=22.0, c=[1.0, 0.62, 0.26], t="torch"))
    elif kind == "post":
        cyl(M, x, y, 0.16, z, z + 3.4, "iron", seg=6)
        box(M, x - 0.45, y - 0.45, z + 3.4, x + 0.45, y + 0.45, z + 4.3, "lampglow")
        cyl(M, x, y, 0.65, z + 4.3, z + 4.9, "iron", seg=6, cap=True, r_top=0.15)
        LAMPS.append(dict(x=x, y=y, z=z + 3.9, r=26.0, c=[1.0, 0.74, 0.40], t="lamp"))
    else:  # beacon على المنارة
        cyl(M, x, y, 1.0, z, z + 1.6, "lampglow", seg=10)
        LAMPS.append(dict(x=x, y=y, z=z + 0.8, r=60.0, c=[1.0, 0.86, 0.55], t="beacon"))


# ============ المشهد ============
def build(out):
    M = Mesh()

    # ---------- البحر (بلاطات كبيرة) ----------
    N = 14
    span = 4200.0
    st = 2 * span / N
    for i in range(N):
        for j in range(N):
            x0 = -span + i * st
            y0 = -span + j * st
            zz = SEA - (i + j) * 0.002
            M.add([(x0 - 0.5, y0 - 0.5, zz), (x0 + st + 0.5, y0 - 0.5, zz),
                   (x0 + st + 0.5, y0 + st + 0.5, zz), (x0 - 0.5, y0 + st + 0.5, zz)],
                  [[3, 2, 1, 0]], "water")

    # ---------- الجرف ----------
    levels = []
    for i, (z, k) in enumerate(CLIFF):
        poly = ring(44, BASE_RX * k, BASE_RY * k, cx=-6 + i * 2.0, cy=10 - i * 4.0, phase=0.4, j=0.05)
        levels.append((poly, z, k))
    z_prev = SEA - 6
    for i, (poly, z, k) in enumerate(levels):
        if i == len(levels) - 1:
            mat = "grass"
        elif i >= len(levels) - 3:
            mat = "dirt"
        else:
            mat = "rock" if i % 2 else "rock_dark"
        prism(M, poly, z_prev, z, mat)
        # ألسنة صخرية بارزة
        if i < 2:
            for kk in range(0, len(poly), 3):
                x, y = poly[kk]
                d = math.hypot(x, y) or 1.0
                o = 1.0 + R.uniform(0.02, 0.075)
                lx, ly = x * o, y * o
                w = R.uniform(10, 30)
                ang = math.atan2(y, x) + math.pi / 2
                box(M, lx - w / 2, ly - 7, z - R.uniform(5, 16), lx + w / 2, ly + 7, z - 1, "rock_dark", rot=ang)
        z_prev = z
    plateau, Z_TOP, _ = levels[-1]

    # ============ المدينة: 5 مصاطب ============
    town_levels = []
    for idx in [4, 5, 6, 7, 8, 9]:
        poly, z, k = levels[idx]
        town_levels.append((poly, z))
    houses = 0
    for li, (poly, z) in enumerate(town_levels):
        inner_f = 1.0 - 0.15 * (li / len(town_levels))
        for kk in range(len(poly)):
            for rep in range(4):
                t = rep / 4.0
                sc = 1.0 - 0.135 * t
                x, y = poly[kk][0] * sc, poly[kk][1] * sc
                if li == len(town_levels) - 1 and (abs(x) > 70 or abs(y) > 90):
                    continue
                w = R.uniform(7.0, 11.0)
                d = R.uniform(6.5, 9.5)
                h = R.uniform(7.5, 14.0)
                ang = math.atan2(y, x) + math.pi / 2 + R.uniform(-0.15, 0.15)
                base_mat = "plaster" if R.random() < 0.6 else ("plaster_w" if R.random() < 0.5 else "sandstone")
                box(M, x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, base_mat, rot=ang)
                roof = R.choices(["terracotta", "slate", "shingle"], [0.5, 0.32, 0.18])[0]
                gable(M, x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + h, (d if d >= w else w) * 0.68, roof, oh=0.8)
                # مدخنة
                if R.random() < 0.7:
                    box(M, x + w * 0.25, y + d * 0.2, z + h + 0.3, x + w * 0.25 + 1.2, y + d * 0.2 + 1.2,
                        z + h + R.uniform(2.5, 4.5), "granite")
                # نوافذ مضيئة (طبقة واحدة على الواجهة المواجهة للخارج)
                if R.random() < 0.5:
                    nx = x + math.cos(ang) * (w / 2 + 0.05)
                    ny = y + math.sin(ang) * (d / 2 + 0.05)
                    box(M, nx - 0.9, ny - 0.9, z + h * 0.45, nx + 0.9, ny + 0.9, z + h * 0.45 + 1.6, "wglow")
                houses += 1
            # أبراج زاوية على حواف المصاطب
            if kk % 4 == 0:
                x, y = poly[kk]
                r = R.uniform(4.5, 6.5)
                cyl(M, x, y, r, z - 8, z + R.uniform(18, 24), "granite", seg=12)
                cone(M, x, y, r * 1.3, z + 20, z + 20 + r * 2.2, "slate", seg=12)
                if R.random() < 0.5:
                    lamp(M, x, y, z + 24, kind="torch")
        # مدرجات/أدراج بين المصاطب + جسور معقودة
        if li > 0:
            p0, z0 = town_levels[li - 1]
            for kk in range(0, len(poly), 7):
                x0, y0 = p0[kk]
                x1, y1 = poly[kk]
                if R.random() < 0.4:
                    arch(M, (x0 + x1) / 2, (y0 + y1) / 2 - 3, z0, 14, 1.4, 6, "granite", seg=8)

    # ============ الأسوار الثلاثة ============
    def wall_ring(z0, h, th, k):
        poly = [(x * k, y * k) for x, y in levels[min(range(len(levels)), key=lambda i: abs(levels[i][1] - z0))][0]]
        n = len(poly)
        cx = sum(p[0] for p in poly) / n
        cy = sum(p[1] for p in poly) / n
        inner = [(cx + (x - cx) * (1 - th / max(math.hypot(x - cx, y - cy), 1e-6)), 
                  cy + (y - cy) * (1 - th / max(math.hypot(x - cx, y - cy), 1e-6))) for x, y in poly]
        z1 = z0 + h
        # وجهان
        ov = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
        M.add(ov, [[k2, (k2 + 1) % n, n + (k2 + 1) % n, n + k2] for k2 in range(n)], "granite")
        iv = [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner]
        M.add(iv, [[(k2 + 1) % n, k2, n + k2, n + (k2 + 1) % n] for k2 in range(n)], "granite_d")
        # ممر الحراسة
        top = [(poly[i2][0], poly[i2][1], z1) for i2 in range(n)] + [(inner[i2][0], inner[i2][1], z1) for i2 in range(n)]
        M.add(top, [[i2, (i2 + 1) % n, n + (i2 + 1) % n, n + i2] for i2 in range(n)], "flag")
        # شرفات + ميزابية (كوابيل)
        for i2 in range(n):
            x0, y0 = poly[i2]
            x1w, y1w = poly[(i2 + 1) % n]
            L = math.hypot(x1w - x0, y1w - y0)
            if L < 4:
                continue
            ang = math.atan2(y1w - y0, x1w - x0)
            nm = max(1, int(L / 3.2))
            for m2 in range(nm):
                t = (m2 + 0.5) / nm
                mx, my = x0 + (x1w - x0) * t, y0 + (y1w - y0) * t
                box(M, mx - 0.8, my - 0.55, z1, mx + 0.8, my + 0.55, z1 + 1.3, "granite", rot=ang)
                if m2 % 2 == 0:
                    box(M, mx - 0.5, my - 0.5, z1 + 1.3, mx + 0.5, my + 0.5, z1 + 2.6, "granite_d", rot=ang)
            # كابولي ميزابية كل ~10م
            if i2 % 3 == 0:
                box(M, x0 - 1.0, y0 - 1.0, z1 - 1.2, x0 + 1.0, y0 + 1.0, z1 + 0.2, "granite_d")
        # أبراج السور
        for i2 in range(0, n, 4):
            x, y = poly[i2]
            r = R.uniform(6.0, 8.5)
            ht = R.uniform(26, 33)
            cyl(M, x, y, r, z0 - 4, z0 + ht, "granite", seg=14)
            # ميزابية
            cyl(M, x, y, r * 1.22, z0 + ht - 3.5, z0 + ht - 1.5, "granite_d", seg=14)
            for kk in range(10):
                a = TAU * kk / 10
                box(M, x + math.cos(a) * r * 1.1 - 0.4, y + math.sin(a) * r * 1.1 - 0.4,
                    z0 + ht - 4.5, x + math.cos(a) * r * 1.1 + 0.4, y + math.sin(a) * r * 1.1 + 0.4,
                    z0 + ht - 3.0, "granite_d")
            cone(M, x, y, r * 1.28, z0 + ht, z0 + ht + r * 1.9, "slate", seg=14)
            cyl(M, x, y, 0.28, z0 + ht + r * 1.9, z0 + ht + r * 1.9 + 4.5, "gilded", seg=6)
            if R.random() < 0.6:
                box(M, x + r * 0.6, y - 1.0, z0 + ht + r * 1.9 + 1.0, x + r * 0.6 + 0.3, y + 1.0,
                    z0 + ht + r * 1.9 + 7.0, "banner")
            if R.random() < 0.5:
                lamp(M, x, y, z0 + ht + 2, kind="torch")
    for (z0, h, th, k) in WALL_RINGS:
        wall_ring(z0, h, th, k)

    # ============ القصر / الكاتدرائية ============
    Z = Z_TOP
    # الساحة العليا
    box(M, -95, -105, Z, 95, 105, Z + 0.6, "cobble")
    # صحن الكاتدرائية
    box(M, -40, -22, Z, 40, 22, Z + 42, "sandstone")
    gable(M, -40, -22, 40, 22, Z + 42, 32, "slate_d", oh=1.4)
    # أروقة جانبية
    for sx in (-1, 1):
        box(M, sx * 40 - 10 * (sx > 0), -20, Z, sx * 40 + 10 * (sx < 0), 20, Z + 24, "sandstone_l")
        gable(M, sx * 40 - 10 * (sx > 0), -20, sx * 40 + 10 * (sx < 0), 20, Z + 24, 12, "slate", oh=0.9)
    # الجناح العرضي (transept)
    box(M, -17, -54, Z, 17, 54, Z + 40, "sandstone")
    gable(M, -17, -54, 17, 54, Z + 40, 26, "slate_d", oh=1.1)
    # الأبسيدة (نصف دائرية)
    cyl(M, 0, 60, 16, Z, Z + 30, "sandstone", seg=20)
    cone(M, 0, 60, 16.5, Z + 30, Z + 48, "slate", seg=20)
    # البرج المركزي العظيم + الصوامع
    box(M, -16, -16, Z + 38, 16, 16, Z + 88, "sandstone_l")
    for k in range(4):
        a = math.pi / 2 * k + math.pi / 4
        box(M, math.cos(a) * 16 - 1.6, math.sin(a) * 16 - 1.6, Z + 88,
            math.cos(a) * 16 + 1.6, math.sin(a) * 16 + 1.6, Z + 100, "sandstone_l")
        cone(M, math.cos(a) * 16, math.sin(a) * 16, 2.3, Z + 100, Z + 110, "slate")
    cone(M, 0, 0, 17.5, Z + 88, Z + 132, "slate_d", seg=22)
    cyl(M, 0, 0, 0.6, Z + 132, Z + 142, "gilded", seg=6)
    cyl(M, 0, 0, 1.6, Z + 122, Z + 127, "gilded", seg=8)
    # برجان غربيان
    for k, (dx, dy) in enumerate([(-56, 34), (56, 34), (-56, -34), (56, -34), (-70, 0), (70, 0), (0, -72), (0, 88)]):
        r = 6.0 if k < 4 else 4.8
        hh = 46 if k < 4 else 38
        cyl(M, dx, dy, r, Z - 2, Z + hh, "sandstone", seg=12)
        cone(M, dx, dy, r * 1.32, Z + hh, Z + hh + r * 3.2, "slate_d", seg=12)
        cyl(M, dx, dy, 0.3, Z + hh + r * 3.2, Z + hh + r * 3.2 + 3.5, "gilded", seg=6)
    for sx in (-1, 1):
        cyl(M, sx * 44, 0, 9.5, Z - 3, Z + 54, "sandstone", seg=16)
        for k in range(4):
            a = math.pi / 2 * k + math.pi / 4
            box(M, sx * 44 + math.cos(a) * 9.5 - 1.2, math.sin(a) * 9.5 - 1.2, Z + 54,
                sx * 44 + math.cos(a) * 9.5 + 1.2, math.sin(a) * 9.5 + 1.2, Z + 63, "sandstone_l")
        cone(M, sx * 44, 0, 10.6, Z + 54, Z + 78, "slate_d", seg=16)
        cyl(M, sx * 44, 0, 0.4, Z + 78, Z + 84, "gilded", seg=6)
        lamp(M, sx * 44, 0, Z + 56, kind="torch")
    # دعامات طائرة (12)
    for k in range(12):
        x = -34 + k * 6.2
        for sy in (-1, 1):
            flying_buttress(M, x, sy * 18, sy * 30, Z + 10, Z + 26, 2.6, "sandstone_l")
    # واجهة غربية: مدخل + نافذة وردة + بوابات
    box(M, -30, -19.5, Z, 30, -18.5, Z + 8, "sandstone_l")           # بروز الواجهة
    cyl(M, 0, -19, 6.5, Z + 12, Z + 12.6, "marble", seg=20)          # النافذة الوردة (قرص)
    for k in range(5):
        box(M, -4 + k * 2, -21.5, Z, -4 + k * 2 + 1.2, -20.5, Z + 11, "door")
    for k in range(5):
        box(M, -2 + k, -22.5, Z + 16, -2 + k + 0.5, -21.5, Z + 24, "wglow")
    # القصر الملكي الملحق (شرق)
    box(M, 40, -30, Z, 86, 26, Z + 26, "sandstone")
    gable(M, 40, -30, 86, 26, Z + 26, 18, "slate", oh=1.2)
    for k in range(6):
        box(M, 44 + k * 7, -32.5, Z + 10, 44 + k * 7 + 2.2, -31.5, Z + 20, "wglow")
    box(M, 52, 28, Z, 58, 46, Z + 40, "sandstone_l")               # برج القصر
    cone(M, 55, 37, 4.6, Z + 40, Z + 56, "slate_d")
    # حدائق ملكية
    box(M, -95, 60, Z, -20, 100, Z + 0.5, "grass")
    for k in range(6):
        box(M, -92 + k * 12, 62, Z + 0.5, -92 + k * 12 + 3, 96, Z + 2.2, "leaf")
    cyl(M, -57, 80, 6.5, Z + 0.5, Z + 2.0, "marble", seg=18)
    cyl(M, -57, 80, 1.2, Z + 2.0, Z + 6.0, "marble", seg=12)
    for k in range(8):
        a = TAU * k / 8
        box(M, -57 + math.cos(a) * 14 - 0.8, 80 + math.sin(a) * 14 - 0.8, Z + 0.5,
            -57 + math.cos(a) * 14 + 0.8, 80 + math.sin(a) * 14 + 0.8, Z + 4.0, "marble")
    # فوانيس الساحة العليا
    for k in range(10):
        a = TAU * k / 10
        lamp(M, math.cos(a) * 62, math.sin(a) * 62 + 10, Z + 0.6, kind="post")

    # ============ المرفأ ============
    HQ = 5.0
    quays = [(-120, -270, 60, -215), (-190, -240, -110, -185), (-60, -235, 90, -175), (120, -215, 230, -160)]
    for (x0, y0, x1, y1) in quays:
        box(M, x0, y0, 0, x1, y1, HQ, "quay")
        box(M, x0 - 1, y0 - 1, HQ - 1.0, x1 + 1, y1 + 1, HQ, "granite_d")
    for k in range(12):                                  # مخازن
        x = -110 + k * 26
        box(M, x, -262, HQ, x + 16, -240, HQ + 8.0, "plaster" if k % 2 else "sandstone")
        gable(M, x, -262, x + 16, -240, HQ + 8.0, 6.2, "terracotta" if k % 3 else "slate")
        if k % 3 == 0:
            lamp(M, x + 8, -240, HQ, kind="torch")
    for k in range(26):                                  # أعمدة خشبية + أرصفة
        x = -180 + k * 15
        cyl(M, x, -200 - (k % 3) * 6, 0.5, 0, 9.0, "wood", seg=6)
        if k % 4 == 0:
            box(M, x - 6, -206 - (k % 3) * 6, 6.0, x + 6, -194 - (k % 3) * 6, 7.0, "wood")
    for k in range(4):                                   # رافعات خشبية
        x, y = -150 + k * 90, -215
        box(M, x - 3, y - 3, HQ, x + 3, y + 3, HQ + 16, "wood")
        box(M, x, y - 14, HQ + 14, x + 1.6, y + 2, HQ + 16, "wood")
        lamp(M, x, y, HQ + 16, kind="torch")
    for k in range(9):                                   # سفن
        sx, sy = -170 + k * 44, -163 - (k % 2) * 12
        hull = [(sx - 11, sy - 4), (sx + 11, sy - 4.6), (sx + 13, sy + 4.6), (sx - 9, sy + 4)]
        M.add([(p[0], p[1], 1.2) for p in hull] + [(p[0] * 0.92 + sx * 0.08, p[1] * 0.92, 5.2) for p in hull],
              [[0, 1, 2, 3], [4, 5, 6, 7]] + [[i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i][::-1] for i in range(4)], "wood")
        box(M, sx - 7, sy - 0.6, 5.2, sx + 7, sy + 0.6, 6.0, "wood")
        cyl(M, sx - 3, sy, 0.32, 6.0, 21.0, "wood", seg=6)
        cyl(M, sx + 5, sy - 1, 0.28, 6.0, 17.0, "wood", seg=6)
        box(M, sx - 4.2, sy - 0.2, 9.0, sx - 1.8, sy + 0.2, 16.0, "banner")   # أشرعة
        box(M, sx + 3.8, sy - 1.2, 8.0, sx + 6.2, sy - 0.8, 14.0, "banner")
    # المنارة
    lx, ly = 245.0, -120.0
    box(M, lx - 16, ly - 16, 0, lx + 16, ly + 16, 6.0, "granite_d")
    cyl(M, lx, ly, 6.0, 0, 30.0, "plaster_w", seg=14, r_top=4.0)
    box(M, lx - 5, ly - 5, 30.0, lx + 5, ly + 5, 33.0, "granite")
    lamp(M, lx, ly, 33.2, kind="beacon")
    cone(M, lx, ly, 5.6, 33.2, 40.0, "slate_d", seg=14)
    SPAWNS["lighthouse"] = [lx, ly - 20, 12]

    # ============ البوابة البحرية + الجسر ============
    gx, gy = 150.0, -300.0
    for sx in (-1, 1):
        cyl(M, gx + sx * 17, gy, 8.0, 4, 42, "granite", seg=16)
        cyl(M, gx + sx * 17, gy, 9.8, 38, 40, "granite_d", seg=16)
        cone(M, gx + sx * 17, gy, 9.2, 42, 62, "slate", seg=16)
        cyl(M, gx + sx * 17, gy, 0.35, 62, 67, "gilded", seg=6)
        box(M, gx + sx * 17 + (6 if sx > 0 else -6.3), gy - 1, 12, gx + sx * 17 + (6.3 if sx > 0 else -6), gy + 1, 24, "banner")
        lamp(M, gx + sx * 17, gy - 6, 14, kind="torch")
    box(M, gx - 10, gy - 9, 4, gx + 10, gy + 9, 34, "granite")
    box(M, gx - 5, gy - 7, 4, gx + 5, gy + 7, 14, "door")
    SPAWNS["sea_gate"] = [gx, gy + 14, 15]

    L = BRIDGE["arches"] * BRIDGE["span"]
    dz = BRIDGE["deck_z"]
    for i in range(BRIDGE["arches"] + 1):
        x = gx + 16 + i * BRIDGE["span"]
        box(M, x - 5, gy - 6.5, 0, x + 5, gy + 6.5, dz - 3.5, "granite")
        if i % 2 == 0:
            lamp(M, x, gy - 7.5, dz, kind="post")
    box(M, gx + 8, gy - 4.5, dz - 3.5, gx + 16 + L + 8, gy + 4.5, dz, "granite")
    for sx in (-1, 1):
        box(M, gx + 8, gy + sx * 4.5 - 0.6, dz, gx + 16 + L + 8, gy + sx * 4.5 + 0.6, dz + 1.6, "granite")
    for i in range(BRIDGE["arches"]):
        cx = gx + 16 + i * BRIDGE["span"] + BRIDGE["span"] / 2
        arch(M, cx, gy - 6, dz - 3.5, BRIDGE["span"] - 2, 1.6, 12, "granite", seg=12)
    SPAWNS["causeway"] = [gx + 16, gy, dz + 2]

    # ============ الشلالان ============
    for i, (ang, top, h, w) in enumerate([(3.55, 78, 66, 13), (3.30, 62, 44, 9)]):
        cxx, cyy = math.cos(ang) * BASE_RX, math.sin(ang) * BASE_RY
        d = math.hypot(cxx, cyy) or 1.0
        ox, oy = cxx / d, cyy / d
        px, py = -oy, ox
        # سطح الشلال (شريحة كبيرة من الأعلى إلى الأسفل)
        M.add([(cxx - px * w / 2, cyy - py * w / 2, top),
               (cxx + px * w / 2, cyy + py * w / 2, top),
               (cxx + px * w * 0.8 + ox * 10, cyy + py * w * 0.8 + oy * 10, top - h),
               (cxx - px * w * 0.8 + ox * 10, cyy - py * w * 0.8 + oy * 10, top - h)],
              [[0, 1, 2, 3]], "foam")
        # جدار الشلال الأوسط (كثافة)
        M.add([(cxx - px * w * 0.35 + ox * 2, cyy - py * w * 0.35 + oy * 2, top),
               (cxx + px * w * 0.35 + ox * 2, cyy + py * w * 0.35 + oy * 2, top),
               (cxx + px * w * 0.3 + ox * 7, cyy + py * w * 0.3 + oy * 7, top - h * 0.98),
               (cxx - px * w * 0.3 + ox * 7, cyy - py * w * 0.3 + oy * 7, top - h * 0.98)],
              [[0, 1, 2, 3]], "foam")
        # بركة + رشّاش عند القاعدة
        box(M, cxx + ox * 8 - w, cyy + oy * 8 - w * 0.5, 0.5, cxx + ox * 8 + w, cyy + oy * 8 + w * 0.5, 3.5, "foam")
        cyl(M, cxx + ox * 14, cyy + oy * 14, w * 0.7, 0.2, 1.8, "foam", seg=12)

    # ============ الأشجار ============
    for k in range(120):
        a = TAU * R.random()
        rr = R.uniform(0.45, 0.95)
        x = math.cos(a) * BASE_RX * rr
        y = math.sin(a) * BASE_RY * rr
        z = 0
        for (poly, zz, kk) in levels:
            if math.hypot(x, y) < kk * BASE_RX * 0.98:
                z = zz
        cyl(M, x, y, 0.5, z, z + 6.0, "wood", seg=5)
        cone(M, x, y, 4.2, z + 5.0, z + 14.0, "leaf", seg=7)

    # ============ نقاط اللعب ============
    SPAWNS.update({
        "main_square": [0, 0, Z + 2], "harbour": [-40, -220, HQ + 2], "wall_walk": [0, -230, 84],
        "town_mid": [0, -140, 40], "palace_gate": [0, -30, Z + 2], "garden": [-57, 80, Z + 2],
    })

    M.export(os.path.join(out, "castle_city"))
    json.dump({"v": [[round(c, 3) for c in p] for p in M.v], "f": M.f, "uv": M.uv, "mat": M.mat,
               "mats": {k: {"tex": v[0], "tile": v[1], "color": v[2], "emissive": v[3]} for k, v in MAT.items()}},
              open(os.path.join(out, "polys.json"), "w"))
    json.dump(LAMPS, open(os.path.join(out, "lamps.json"), "w"), indent=1)
    json.dump(SPAWNS, open(os.path.join(out, "spawns.json"), "w"), indent=1)
    print(f"  ✓ {houses} مبنى | {len(M.f)} وجه | {len(LAMPS)} مصدر ضوء")
    return len(M.f), len(LAMPS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    build(a.out)
