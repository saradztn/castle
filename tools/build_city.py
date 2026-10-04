#!/usr/bin/env python3
"""
build_city.py — مدينة القلعة الساحلية (Castle & Palace)
منهج: مصاطب مرسومة بقياسات مستخرجة من الصورة المرجعية + جرف وعِر + أسوار تتبع الكنتور.
الأبعاد بالأمتار. سطح البحر 0، القمة +112. الشمال = -Y، الشرق = +X.
المخرجات: build/castle_city.obj/.mtl + build/polys.json
"""
import argparse, math, os, json, random
import numpy as np

SEED = 20261
random.seed(SEED)

SEA = 0.0
PEAK = 112.0

MAT = {
    "rock":       ("rock_cliff_strata",        8.0, (0.40, 0.39, 0.37)),
    "rock_wet":   ("stone_seaweathered_mossy", 6.0, (0.30, 0.32, 0.31)),
    "grass":      ("terrain_grass",            8.0, (0.30, 0.40, 0.21)),
    "granite":    ("stone_granite_wall",       4.0, (0.44, 0.44, 0.45)),
    "sandstone":  ("stone_sandstone_ashlar",   4.0, (0.80, 0.69, 0.52)),
    "slate":      ("roof_slate",               3.0, (0.29, 0.32, 0.36)),
    "terracotta": ("roof_tile_terracotta",     3.0, (0.68, 0.44, 0.29)),
    "plaster":    ("plaster_lime_town",         4.0, (0.70, 0.65, 0.56)),
    "wood":       ("wood_oak_timber",          2.0, (0.44, 0.32, 0.21)),
    "cobble":     ("stone_cobble_street",      4.0, (0.44, 0.42, 0.39)),
    "quay":       ("stone_quay_granite",       4.0, (0.52, 0.51, 0.48)),
    "water":      ("water_ocean",              8.0, (0.13, 0.34, 0.40)),
    "foam":       ("water_foam_shore",         4.0, (0.95, 0.96, 0.97)),
    "copper":     ("metal_copper_verdigris",   2.0, (0.32, 0.52, 0.43)),
    "gilded":     ("metal_gilded_bronze",      1.0, (0.85, 0.68, 0.30)),
    "marble":     ("marble_floor_light",       4.0, (0.90, 0.88, 0.82)),
    "banner":     ("fabric_banner_heraldry",   3.0, (0.55, 0.16, 0.16)),
    "dirt":       ("terrain_dirt_road",        4.0, (0.56, 0.49, 0.38)),
    "window":     ("glass_leaded_pane",        1.0, (0.62, 0.74, 0.72)),
    "window_lit": ("glass_leaded_pane_emissive", 1.0, (1.00, 0.78, 0.45)),
    "iron":       ("metal_iron_forged",        2.0, (0.16, 0.16, 0.17)),
    "tapestry":   ("fabric_tapestry",          3.0, (0.55, 0.42, 0.30)),
    "leather":    ("leather_hide",             2.0, (0.38, 0.26, 0.16)),
}

# ====================== خريطة المصاطب (قياسات من الصورة المرجعية) ======================
# (منسوب م, (cx, cy), (rx, ry), مادة السطح)
TERRACES = [
    (112.0, (0.0, 0.0),         (96.0, 74.0),   "cobble"),
    (98.0,  (30.0, -6.0),      (128.0, 100.0),  "cobble"),    # الحدائق الملكية
    (84.0,  (52.0, -22.0),     (156.0, 126.0),  "cobble"),   # الساحة العليا
    (70.0,  (62.0, -40.0),     (182.0, 150.0),  "cobble"),   # المدينة العليا
    (56.0,  (58.0, -50.0),     (208.0, 172.0),  "cobble"),   # المدينة الوسطى
    (42.0,  (46.0, -52.0),     (234.0, 196.0),  "cobble"),   # المدينة السفلى
    (30.0,  (30.0, -46.0),     (252.0, 214.0),  "dirt"),
    (22.0,  (20.0, -38.0),     (262.0, 224.0),  "rock"),
    (12.0,  (6.0, -20.0),      (272.0, 234.0),  "rock"),
    (-2.0,  (-10.0, -2.0),     (286.0, 248.0),  "rock_wet"),
    (-30.0, (-24.0, 10.0),     (302.0, 266.0),  "rock_wet"),
]
WALL_RINGS = [(22.0, 15.0, 4.0), (44.0, 13.0, 3.4), (70.0, 11.0, 2.8)]
CAUSEWAY = dict(len=176.0, arches=8, deck_w=9.5, deck_z=15.0)
WATERFALLS = [(206.0, 62.0, 11.0, 72.0), (224.0, 38.0, 8.0, 47.0)]   # (زاوية°, ارتفاع, عرض, منسوب أعلى)


def vnoise_scalar(x, y):
    n = math.sin(x * 127.1 + y * 311.7 + SEED * 0.013) * 43758.5453
    return n - math.floor(n)


# ============================ المش ============================
class Mesh:
    def __init__(self):
        self.v, self.f, self.uv, self.mat = [], [], [], []

    def add(self, verts, faces, mat):
        if not faces:
            return
        tile = MAT[mat][1]
        off = len(self.v)
        V = np.asarray(verts, dtype=np.float64)
        self.v.extend([(float(p[0]), float(p[1]), float(p[2])) for p in V])
        for fc in faces:
            if len(fc) < 3:
                continue
            P = V[list(fc)]
            n = np.cross(P[1] - P[0], P[2] - P[0])
            ln = np.linalg.norm(n)
            if ln < 1e-9:
                continue
            ax = int(np.argmax(np.abs(n / ln)))
            i, j = [q for q in range(3) if q != ax]
            self.f.append([int(off + q) for q in fc])
            self.uv.append([(float(p[i]) / tile, float(p[j]) / tile) for p in P])
            self.mat.append(mat)

    def export(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path + ".obj", "w") as f:
            f.write("# Castle & Palace — coastal castle-city\n")
            f.write(f"mtllib {os.path.basename(path)}.mtl\n")
            for m in sorted(set(self.mat)):
                f.write(f"\nusemtl mat_{m}\n")
                for fc, mm in zip(self.f, self.mat):
                    if mm != m:
                        continue
                    for vi in fc:
                        x, y, z = self.v[vi]
                        f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
        with open(path + ".mtl", "w") as fh:
            for m, (tex, tile, col) in MAT.items():
                fh.write(f"newmtl mat_{m}\nKd {col[0]:.3f} {col[1]:.3f} {col[2]:.3f}\n")
                fh.write(f"map_Kd textures/src/{tex}_albedo.png\n\n")
        print(f"  ✓ {path}.obj  ({len(self.f)} وجه، {len(self.v)} رأس)")


# ---------- أدوات ----------
def poly_at(t, n=44, jitter=0.055):
    z, (cx, cy), (rx, ry), mat = t
    pts = []
    for k in range(n):
        a = math.tau * k / n
        j = 1.0 + jitter * (math.sin(a * 3 + cx * 0.013) * 0.62 + math.sin(a * 7 + cy * 0.017) * 0.38)
        pts.append((cx + math.cos(a) * rx * j, cy + math.sin(a) * ry * j))
    return pts


def add_prism(mesh, poly, z0, z1, mat_top, mat_side, cap=True):
    n = len(poly)
    v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    mesh.add(v, [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)], mat_side)
    if cap:
        mesh.add([(x, y, z1) for x, y in poly], [list(range(n))], mat_top)


def add_box(mesh, x0, y0, z0, x1, y1, z1, mat, rot=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(rot), math.sin(rot)
    pts = [(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c) for x, y in
           [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
    f = [[3, 2, 1, 0], [4, 5, 6, 7]] + [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)]
    mesh.add(v, f, mat)


def add_cyl(mesh, cx, cy, r, z0, z1, mat, seg=12, cap=True, r2=None):
    r2 = r if r2 is None else r2
    v = [(cx + math.cos(math.tau * k / seg) * r, cy + math.sin(math.tau * k / seg) * r, z0) for k in range(seg)]
    v += [(cx + math.cos(math.tau * k / seg) * r2, cy + math.sin(math.tau * k / seg) * r2, z1) for k in range(seg)]
    f = [[k, (k + 1) % seg, seg + (k + 1) % seg, seg + k] for k in range(seg)]
    if cap:
        f.append(list(range(seg, 2 * seg)))
    mesh.add(v, f, mat)


def add_cone(mesh, cx, cy, r, z0, z1, mat, seg=12):
    v = [(cx + math.cos(math.tau * k / seg) * r, cy + math.sin(math.tau * k / seg) * r, z0) for k in range(seg)]
    v.append((cx, cy, z1))
    mesh.add(v, [[k, (k + 1) % seg, seg] for k in range(seg)], mat)


def add_gable(mesh, x0, y0, x1, y1, z, rise, mat, oh=0.6, rot=0.0):
    a0, b0, a1, b1 = x0 - oh, y0 - oh, x1 + oh, y1 + oh
    if (y1 - y0) >= (x1 - x0):
        m = (y0 + y1) / 2
        v = [(a0, b0, z), (a1, b0, z), (a1, b1, z), (a0, b1, z), (a0, m, z + rise), (a1, m, z + rise)]
        f = [[0, 1, 5, 4], [3, 4, 5, 2], [0, 4, 3], [1, 2, 5]]
    else:
        m = (x0 + x1) / 2
        v = [(a0, b0, z), (a1, b0, z), (a1, b1, z), (a0, b1, z), (m, b0, z + rise), (m, b1, z + rise)]
        f = [[1, 0, 4, 5], [4, 3, 2, 5], [0, 3, 4], [1, 5, 2]]
    if rot:
        cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
        c, s = math.cos(rot), math.sin(rot)
        v = [((p[0] - cx) * c - (p[1] - cy) * s + cx, (p[0] - cx) * s + (p[1] - cy) * c + cy, p[2]) for p in v]
    mesh.add(v, f, mat)


def add_windows(mesh, x0, y0, x1, y1, z0, z1, rot=0.0, cols=3, rows=2, lit=0.35):
    """نوافذ على واجهة واحدة (شرائح صغيرة) — بعضها مضيء."""
    w = (x1 - x0) / (cols * 2 + 1)
    h = (z1 - z0) / (rows * 2 + 1)
    for r in range(rows):
        for c in range(cols):
            wx0 = x0 + w * (2 * c + 1)
            wz0 = z0 + h * (2 * r + 1)
            mat = "window_lit" if random.random() < lit else "window"
            add_box(mesh, wx0, y0 - 0.12, wz0, wx0 + w, y1 + 0.12, wz0 + h, mat, rot=rot)


def add_machicolation(mesh, cx, cy, r, z, seg=14, mat="granite"):
    """حلقة ميزابية بارزة (كوابيل) — كما في المرجع."""
    for k in range(seg):
        a = math.tau * k / seg
        px, py = cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92
        add_box(mesh, px - 0.75, py - 0.75, z - 1.6, px + 0.75, py + 0.75, z, mat, rot=a)
    add_cyl(mesh, cx, cy, r * 1.10, z, z + 2.4, mat, seg=seg, cap=False)


def add_stairs(mesh, x0, y0, x1, y1, z_low, z_high, mat="granite", width=3.0, steps=None):
    """درج مستقيم بين مصطبتين."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    if L < 1:
        return
    n = steps or max(4, int(abs(z_high - z_low) / 0.24))
    ang = math.atan2(dy, dx)
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        z = z_low + (z_high - z_low) * t0
        px0, py0 = x0 + dx * t0, y0 + dy * t0
        add_box(mesh, px0 - width / 2, py0 - 1.2, z, px0 + width / 2 + L / n, py0 + 1.2, z + 0.24, mat, rot=ang)


# ============================ البناء ============================
def build(out_dir):
    mesh = Mesh()
    print("  · الصخرة والمصاطب…")
    polys = []
    for i, t in enumerate(TERRACES):
        poly = poly_at(t)
        polys.append(poly)
        z, _, _, mat_top = t
        z_next = TERRACES[i + 1][0] if i + 1 < len(TERRACES) else SEA - 60
        mat_side = "rock_wet" if z <= 20 else "rock"
        add_prism(mesh, poly, z_next, z, mat_top, mat_side)

    # حواف صخرية بارزة (طبقات الجرف)
    print("  · وعورة الجرف (نتوءات صخرية)…")
    for i in range(2, 7):
        poly = polys[i]
        z = TERRACES[i][0]
        for k in range(0, len(poly), 2):
            x, y = poly[k]
            d = math.hypot(x, y) or 1.0
            out = 1.0 + random.uniform(0.02, 0.075)
            lx, ly = x * out, y * out
            w = random.uniform(12, 26)
            ang = math.atan2(y, x) + math.pi / 2
            add_box(mesh, lx - w / 2, ly - 6, z - random.uniform(5, 13), lx + w / 2, ly + 6, z, "rock", rot=ang)

    # ===== الأسوار =====
    print("  · الأسوار الثلاثة والأبراج…")
    for (lv, hh, th) in WALL_RINGS:
        idx = min(range(len(TERRACES)), key=lambda i: abs(TERRACES[i][0] - lv))
        base = polys[idx]
        cx0, cy0 = TERRACES[idx][1]
        outer = [(x, y, lv) for x, y in base]
        inner = []
        for (x, y) in base:
            d = math.hypot(x - cx0, y - cy0) or 1.0
            s = (d - th) / d
            inner.append((cx0 + (x - cx0) * s, cy0 + (y - cy0) * s, lv))
        n = len(outer)
        verts = outer + inner + [(p[0], p[1], lv + hh) for p in outer] + [(p[0], p[1], lv + hh) for p in inner]
        fcs = []
        for k in range(n):
            k2 = (k + 1) % n
            fcs.append([k, k2, n + k2, n + k])                              # خارجي
            fcs.append([2 * n + k2, 2 * n + k, 3 * n + k, 3 * n + k2])      # داخلي
            fcs.append([n + k, n + k2, 3 * n + k2, 3 * n + k])              # ممر
        mesh.add(verts, fcs, "granite")
        for k in range(0, n, 2):                                            # شرفات
            x, y = outer[k][0], outer[k][1]
            ang = math.atan2(y - cy0, x - cx0) + math.pi / 2
            add_box(mesh, x - 1.7, y - 1.4, lv + hh, x + 1.7, y + 1.4, lv + hh + 1.35, "granite", rot=ang)
        for k in range(0, n, 5):                                            # أبراج
            x, y = outer[k][0], outer[k][1]
            r = 6.5 + (k % 3) * 1.2
            add_cyl(mesh, x, y, r, lv - 6, lv + 24, "granite", seg=12)
            add_machicolation(mesh, x, y, r, lv + 22)
            add_cone(mesh, x, y, r * 1.30, lv + 26, lv + 26 + r * 1.85, "slate", seg=12)
            add_cyl(mesh, x, y, 0.4, lv + 26 + r * 1.85, lv + 30 + r * 1.85, "gilded", seg=6)

    # ===== المدينة =====
    print("  · بيوت المدينة (مصاطب 3–6)…")
    houses = 0
    for i in (3, 4, 5, 6):
        t = TERRACES[i]
        z, (cx0, cy0), (rx, ry), _ = t
        poly = polys[i]
        n = len(poly)
        for k in range(0, n, 1):
            for row in range(3):
                f = 1.0 - 0.055 * (row + 1)
                x = cx0 + (poly[k][0] - cx0) * f
                y = cy0 + (poly[k][1] - cy0) * f
                ang = math.atan2(y - cy0, x - cx0) + math.pi / 2
                w = random.uniform(6.5, 9.5)
                d = random.uniform(6.0, 8.5)
                hb = random.uniform(6.5, 13.5)
                add_box(mesh, x - w / 2, y - d / 2, z - 1.2, x + w / 2, y + d / 2, z + hb, "plaster", rot=ang)
                if random.random() < 0.42:                                   # طابق half-timber بارز
                    add_box(mesh, x - w / 2 - 0.35, y - d / 2 - 0.35, z + hb, x + w / 2 + 0.35,
                            y + d / 2 + 0.35, z + hb + hb * 0.45, "wood", rot=ang)
                    hb += hb * 0.45
                add_gable(mesh, x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + hb,
                          d * 0.68 if d >= w else w * 0.68,
                          "terracotta" if random.random() < 0.60 else "slate", rot=ang)
                add_windows(mesh, x - w / 2 + 0.6, y - d / 2, x + w / 2 - 0.6, y - d / 2 + 0.25,
                            z + 1.6, z + hb - 1.0, rot=ang, cols=2, rows=2, lit=0.4)
                if random.random() < 0.5:                                    # مدخنة
                    add_box(mesh, x + w * 0.22, y + d * 0.1, z + hb, x + w * 0.22 + 1.1, y + d * 0.1 + 1.1,
                            z + hb + 3.2, "granite", rot=ang)
                houses += 1
        for k in range(0, n, 6):                                             # أبراج المدينة الصغيرة
            x, y = poly[k][0], poly[k][1]
            r = 4.2
            add_cyl(mesh, x, y, r, z - 8, z + 16, "granite", seg=10)
            add_cone(mesh, x, y, r * 1.35, z + 16, z + 22, "slate", seg=10)

    # أدراج تربط المصاطب (قابلة للعب)
    print("  · الأدراج والجسور المعقودة الداخلية…")
    for i in range(1, 7):
        z_hi, (cxa, cya), (rxa, rya), _ = TERRACES[i]
        z_lo, (cxb, cyb), (rxb, ryb), _ = TERRACES[i + 1]
        ang = math.radians(230 + i * 22)
        xa = cxa + math.cos(ang) * rxa * 0.92
        ya = cya + math.sin(ang) * rya * 0.92
        xb = cxb + math.cos(ang) * rxb * 0.86
        yb = cyb + math.sin(ang) * ryb * 0.86
        add_stairs(mesh, xa, ya, xb, yb, z_lo, z_hi, "granite", width=3.2)
    for i in (4, 5):                                                         # جسور معقودة
        z, (cx0, cy0), (rx, ry), _ = TERRACES[i]
        ang = math.radians(60 + i * 30)
        x0 = cx0 + math.cos(ang) * rx * 0.75
        y0 = cy0 + math.sin(ang) * ry * 0.75
        add_box(mesh, x0 - 14, y0 - 2.4, z - 0.6, x0 + 14, y0 + 2.4, z, "granite", rot=ang)
        for sx in (-1, 1):
            add_box(mesh, x0 - 14, y0 + sx * 2.0, z, x0 + 14, y0 + sx * 2.4, z + 1.2, "granite", rot=ang)
        for k in range(4):                                                   # أعمدة العقد
            px = x0 - 10 + k * 6.6
            add_box(mesh, px - 1.0, y0 - 1.2, z - 10, px + 1.0, y0 + 1.2, z - 0.6, "granite", rot=ang)

    # ===== القصر/الكاتدرائية =====
    print("  · القصر والكاتدرائية على القمة…")
    zt = TERRACES[0][0]
    add_box(mesh, -64, -42, zt - 8, 64, 42, zt + 32, "sandstone")            # الكتلة الرئيسية
    add_gable(mesh, -64, -42, 64, 42, zt + 32, 32.0, "slate", oh=1.8)
    add_box(mesh, -36, -28, zt + 32, 36, 28, zt + 48, "sandstone")           # صحن الكاتدرائية
    add_gable(mesh, -36, -28, 36, 28, zt + 48, 17.0, "slate", oh=1.3)
    add_windows(mesh, -58, -42.4, 58, -42.0, zt + 4, zt + 30, cols=7, rows=2, lit=0.3)
    for sx in (-1, 1):                                                       # برجان غربيان مستديران
        add_cyl(mesh, sx * 70, -6, 8.5, zt - 10, zt + 56, "sandstone", seg=16)
        add_machicolation(mesh, sx * 70, -6, 8.5, zt + 54, mat="sandstone")
        add_cone(mesh, sx * 70, -6, 10.5, zt + 58, zt + 80, "slate", seg=16)
        add_cyl(mesh, sx * 70, -6, 0.45, zt + 80, zt + 86, "gilded", seg=6)
    add_box(mesh, -16, -16, zt + 30, 16, 16, zt + 88, "sandstone")           # البرج المركزي
    add_windows(mesh, -15, -16.4, 15, -16.0, zt + 40, zt + 80, cols=3, rows=3, lit=0.25)
    add_cone(mesh, 0, 0, 17.5, zt + 88, zt + 126, "slate", seg=18)
    add_cyl(mesh, 0, 0, 0.6, zt + 126, zt + 134, "gilded", seg=6)
    for k, (dx, dy) in enumerate([(-54, 32), (54, 32), (-54, -34), (54, -34), (-28, 36), (28, 36), (-28, -38), (28, -38)]):
        r = 4.6 if k < 4 else 3.2
        hh = 48.0 if k < 4 else 36.0
        add_cyl(mesh, dx, dy, r, zt + 16, zt + 16 + hh, "sandstone", seg=10)
        add_cone(mesh, dx, dy, r * 1.42, zt + 16 + hh, zt + 16 + hh + r * 3.3, "slate", seg=10)
    for k in range(14):                                                      # دعامات طائرة
        x = -60 + k * 9.2
        for sy in (-1, 1):
            mesh.add([(x, sy * 42, zt + 12), (x + 4.2, sy * 42, zt + 12),
                      (x + 4.2, sy * 54, zt + 28), (x, sy * 54, zt + 28)], [[0, 1, 2, 3]], "sandstone")
    for (x, y) in [(-54, 36), (54, 36), (-70, -6), (70, -6)]:                # رايات
        mesh.add([(x, y, zt + 56), (x + 7.5, y, zt + 56), (x + 7.5, y, zt + 34), (x, y, zt + 34)],
                 [[0, 1, 2, 3]], "banner")
    add_box(mesh, -22, -14, zt + 0.2, 22, -2, zt + 1.2, "marble")            # ساحة القصر

    # ===== الحدائق الملكية =====
    print("  · الحدائق الملكية…")
    zg, (cgx, cgy), _, _ = TERRACES[1]
    add_cyl(mesh, cgx + 30, cgy + 26, 7.0, zg, zg + 1.8, "marble", seg=16)
    for k in range(40):                                                      # أشجار
        a = math.tau * k / 40
        add_cyl(mesh, cgx + math.cos(a) * 52, cgy + math.sin(a) * 40, 0.7, zg, zg + 5.0, "wood", seg=6)
        add_cone(mesh, cgx + math.cos(a) * 52, cgy + math.sin(a) * 40, 4.2, zg + 4.0, zg + 12.0, "grass", seg=8)
    for k in range(18):                                                      # أشجار المدينة
        i = 3 + (k % 3)
        z, (cx0, cy0), (rx, ry), _ = TERRACES[i]
        a = math.tau * k / 18 + 0.4
        x, y = cx0 + math.cos(a) * rx * 0.68, cy0 + math.sin(a) * ry * 0.68
        add_cyl(mesh, x, y, 0.6, z, z + 4.5, "wood", seg=6)
        add_cone(mesh, x, y, 3.6, z + 3.6, z + 10.5, "grass", seg=8)

    # ===== المرفأ =====
    print("  · المرفأ والأرصفة والسفن والرافعة…")
    zq = TERRACES[7][0]
    for (ax0, ay0, ax1, ay1) in [(-150, -262, 130, -216), (-256, -212, -164, -170), (72, -240, 196, -192)]:
        add_box(mesh, ax0, ay0, -3, ax1, ay1, zq, "quay")
    for i in range(11):
        x = -142 + i * 30
        add_box(mesh, x, -258, zq, x + 17, -236, zq + 8.0, "plaster")
        add_gable(mesh, x, -258, x + 17, -236, zq + 8.0, 6.4, "slate")
        add_windows(mesh, x + 2, -236.4, x + 15, -236.0, zq + 2.0, zq + 6.5, cols=2, rows=1, lit=0.5)
    for i in range(20):
        add_cyl(mesh, -244 + i * 22, -208, 0.5, -2, 10.0, "wood", seg=6)
    for i in range(7):
        sx = -120 + i * 46
        add_box(mesh, sx, -198, 0.5, sx + 22, -188, 6.2, "wood")
        add_cyl(mesh, sx + 11, -193, 0.42, 6.2, 24.0, "wood", seg=6)
        add_box(mesh, sx + 3, -212, 0.4, sx + 9, -202, 4.2, "wood")
    add_box(mesh, 118, -232, zq, 130, -220, zq + 13, "wood")
    add_box(mesh, 112, -228, zq + 13, 136, -224, zq + 14, "wood")

    # ===== الجسر + البوابة البحرية + المنارة =====
    print("  · الجسر المقوّس والبوابة البحرية والمنارة…")
    gx, gy = 198, -256
    for sx in (-1, 1):
        add_cyl(mesh, gx + sx * 16, gy, 7.5, 0, 42, "granite", seg=16)
        add_machicolation(mesh, gx + sx * 16, gy, 7.5, 40)
        add_cone(mesh, gx + sx * 16, gy, 9.5, 44, 66, "slate", seg=16)
    add_box(mesh, gx - 10, gy - 9, 0, gx + 10, gy + 9, 34, "granite")
    L, na, dw, dz = CAUSEWAY["len"], CAUSEWAY["arches"], CAUSEWAY["deck_w"], CAUSEWAY["deck_z"]
    x0, y0 = gx + 16, gy
    seg = L / na
    for i in range(na + 1):
        x = x0 + i * seg
        add_box(mesh, x - 4.4, y0 - dw / 2 - 1.0, -2, x + 4.4, y0 + dw / 2 + 1.0, dz - 3.4, "granite")
        add_box(mesh, x - 5.2, y0 - 1.4, -2, x + 5.2, y0 + 1.4, dz - 2.6, "granite")   # كتف مائي
    add_box(mesh, x0 - 9, y0 - dw / 2, dz - 3.4, x0 + L + 9, y0 + dw / 2, dz, "granite")
    for sx in (-1, 1):
        add_box(mesh, x0 - 9, y0 + sx * dw / 2 - 0.6, dz, x0 + L + 9, y0 + sx * dw / 2 + 0.6, dz + 1.7, "granite")
    for i in range(na):
        cxx = x0 + i * seg + seg / 2
        r = seg / 2 - 1.0
        for k in range(11):
            a0, a1 = math.pi * k / 11, math.pi * (k + 1) / 11
            p0x, p0z = cxx + math.cos(a0) * r, dz - 3.4 - math.sin(a0) * r
            p1x, p1z = cxx + math.cos(a1) * r, dz - 3.4 - math.sin(a1) * r
            for sy in (-1, 1):
                yy = y0 + sy * (dw / 2 + 1.0)
                mesh.add([(p0x - 0.7, yy, p0z), (p0x + 0.7, yy, p0z),
                          (p1x + 0.7, yy, p1z), (p1x - 0.7, yy, p1z)], [[0, 1, 2, 3]], "granite")
    for i in range(0, na + 1, 2):
        x = x0 + i * seg
        for sy in (-1, 1):
            add_cyl(mesh, x, y0 + sy * (dw / 2 + 0.7), 0.4, dz + 1.7, dz + 4.6, "granite", seg=6)
            add_box(mesh, x - 0.8, y0 + sy * (dw / 2 + 0.7) - 0.8, dz + 4.6, x + 0.8,
                    y0 + sy * (dw / 2 + 0.7) + 0.8, dz + 5.4, "gilded")
    lx, ly = 246, -184
    add_cyl(mesh, lx, ly, 5.5, 0, 38, "granite", seg=14)
    add_cyl(mesh, lx, ly, 6.4, 38, 41, "granite", seg=14)
    add_cone(mesh, lx, ly, 7.0, 41, 58, "slate", seg=14)
    add_cyl(mesh, lx, ly, 0.5, 58, 62, "gilded", seg=6)

    # ===== الشلالان =====
    print("  · الشلالان…")
    for (ang_deg, wf_h, wf_w, top_z) in WATERFALLS:
        a = math.radians(ang_deg)
        rad = 1.0
        # نجد نصف قطر المصطبة عند هذا المنسوب تقريبًا
        for i, t in enumerate(TERRACES):
            if t[0] <= top_z:
                z, (cx0, cy0), (rx, ry), _ = t
                break
        bx = cx0 + math.cos(a) * rx * 0.995
        by = cy0 + math.sin(a) * ry * 0.995
        nx_, ny_ = math.cos(a), math.sin(a)
        tx_, ty_ = -math.sin(a), math.cos(a)
        top = [(bx + tx_ * wf_w * 0.5, by + ty_ * wf_w * 0.5, top_z),
               (bx + tx_ * wf_w * 0.5 + nx_ * 2, by + ty_ * wf_w * 0.5 + ny_ * 2, top_z),
               (bx - tx_ * wf_w * 0.5 + nx_ * 2, by - ty_ * wf_w * 0.5 + ny_ * 2, top_z),
               (bx - tx_ * wf_w * 0.5, by - ty_ * wf_w * 0.5, top_z)]
        bot = [(p[0] + nx_ * 9, p[1] + ny_ * 9, max(0.5, p[2] - wf_h)) for p in top]
        n = len(top)
        v = top + bot
        mesh.add(v, [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)], "foam")
        add_box(mesh, bx - 16, by - 12, 0.4, bx + 16, by + 18, 3.2, "foam")

    # ===== البحر (بلاطات كبيرة) =====
    print("  · البحر…")
    N, span = 34, 9000.0
    step = 2 * span / N
    for i in range(N):
        for j in range(N):
            x0 = -span + i * step
            y0 = -span + j * step
            add_box(mesh, x0, y0, -18, x0 + step, y0 + step, 0.0, "water")

    # ===== نتوءات الجرف الرأسية (أسنان صخرية على الوجه الخارجي) =====
    print("  · أسنان الجرف…")
    for i in range(2, 8):
        t = TERRACES[i]
        z = t[0]
        poly = polys[i]
        base_poly = polys[min(i + 1, len(polys) - 1)]
        zlow = TERRACES[min(i + 1, len(TERRACES) - 1)][0]
        for k in range(0, len(poly), 2):
            x, y = poly[k]
            bx, by = base_poly[k]
            ang = math.atan2(y, x)
            h = (z - zlow) + random.uniform(4, 14)
            w = random.uniform(10, 24)
            add_box(mesh, x - w / 2, y - 5, z - h, x + w / 2, y + 5, z + random.uniform(1, 4),
                    "rock", rot=ang + math.pi / 2)
        # أكتاف أفقية (طبقات)
        if i % 2 == 0:
            for k in range(0, len(poly), 4):
                x, y = poly[k]
                ang = math.atan2(y, x)
                add_box(mesh, x - 16, y - 7, z - 4.5, x + 16, y + 7, z - 2.0, "rock", rot=ang + math.pi / 2)

    mesh.export(os.path.join(out_dir, "castle_city"))
    with open(os.path.join(out_dir, "polys.json"), "w") as fh:
        json.dump({"v": [[round(c, 3) for c in p] for p in mesh.v],
                   "f": mesh.f, "uv": mesh.uv, "mat": mesh.mat,
                   "mats": {k: {"tex": v[0], "tile": v[1], "color": v[2]} for k, v in MAT.items()}}, fh)
    print(f"  ✓ {houses} مبنى | {len(mesh.f)} وجه | جاهز للتصيير")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    build(a.out)
