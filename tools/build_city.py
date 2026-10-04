#!/usr/bin/env python3
"""
build_city.py — مولّد هندسة مدينة القلعة الساحلية (بلوك-أوت تفصيلي)
Castle & Palace (MTA:SA) — مبني على الصورة المرجعية المرفقة

الأبعاد بالأمتار، سطح البحر = 0، القمة = +110 م، الشمال = -Y.
المخرجات: build/castle_city.obj + .mtl + build/polys.json (للتصيير)
"""

import argparse, math, os, json, random
import numpy as np

TAU = math.tau
random.seed(11)

SEA = 0.0
PLATEAU = 110.0
ROCK_STEPS = [4, 12, 22, 34, 48, 62, 76, 89, 100, 110]      # درجات الجرف (لتبدو صخرة لا كعكة)
WALL_RINGS = [(20.0, 16.0, 4.2, 1.03), (45.0, 14.0, 3.6, 0.88), (70.0, 12.0, 3.0, 0.73)]
CAUSEWAY = dict(len=170.0, arches=8, deck_w=9.0, deck_z=14.0)
WATERFALLS = [dict(h=60.0, w=9.5), dict(h=35.0, w=7.5)]
HARBOUR_Z = 4.0

# مفتاح المادة -> (معرّف الخامة، مقياس البلاطة، لون تقريبي)
MAT = {
    "rock":       ("rock_cliff_strata",      8.0, (0.46, 0.44, 0.42)),
    "grass":      ("terrain_grass",          8.0, (0.36, 0.46, 0.26)),
    "granite":    ("stone_granite_wall",     4.0, (0.42, 0.42, 0.43)),
    "sandstone":  ("stone_sandstone_ashlar", 4.0, (0.80, 0.70, 0.55)),
    "slate":      ("roof_slate",             3.0, (0.34, 0.37, 0.41)),
    "terracotta": ("roof_tile_terracotta",   3.0, (0.64, 0.44, 0.31)),
    "plaster":    ("plaster_lime_town",      4.0, (0.70, 0.66, 0.58)),
    "wood":       ("wood_oak_timber",        2.0, (0.48, 0.35, 0.23)),
    "cobble":     ("stone_cobble_street",    4.0, (0.52, 0.50, 0.46)),
    "quay":       ("stone_quay_granite",     4.0, (0.56, 0.55, 0.53)),
    "water":      ("water_ocean",            8.0, (0.16, 0.40, 0.45)),
    "foam":       ("water_foam_shore",       4.0, (0.94, 0.95, 0.96)),
    "copper":     ("metal_copper_verdigris", 2.0, (0.34, 0.55, 0.45)),
    "gilded":     ("metal_gilded_bronze",    1.0, (0.80, 0.66, 0.32)),
    "marble":     ("marble_floor_light",     4.0, (0.90, 0.88, 0.82)),
    "banner":     ("fabric_banner_heraldry", 3.0, (0.56, 0.19, 0.19)),
    "dirt":       ("terrain_dirt_road",      4.0, (0.62, 0.55, 0.44)),
}


class Mesh:
    """يجمع المضلعات + UV + اسم المادة."""

    def __init__(self):
        self.v, self.f, self.uv, self.mat = [], [], [], []

    def add(self, verts, faces, mat):
        """faces: مضلعات بفهارس محلية. UV = إسقاط مستوٍ على المحور الغالب للمادة."""
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

    def export(self, path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path + ".obj", "w") as f:
            f.write("# Castle & Palace — coastal castle-city (blockout)\n")
            f.write(f"mtllib {os.path.basename(path)}.mtl\n")
            for m in sorted(set(self.mat)):
                f.write(f"\nusemtl mat_{m}\n")
                for fc, mm in zip(self.f, self.mat):
                    if mm != m:
                        continue
                    for vi in fc:
                        x, y, z = self.v[vi]
                        f.write(f"v {x:.3f} {y:.3f} {z:.3f}\n")
            f.write("\n")
        with open(path + ".mtl", "w") as fh:
            for m, (tex, tile, col) in MAT.items():
                fh.write(f"newmtl mat_{m}\nKd {col[0]:.3f} {col[1]:.3f} {col[2]:.3f}\n")
                fh.write(f"map_Kd textures/src/{tex}_albedo.png\n\n")
        print(f"  ✓ {path}.obj  ({len(self.f)} وجه، {len(self.v)} رأس)")


# ---------------- أدوات هندسية ----------------
def poly_ring(n, rx, ry, cx, cy, phase=0.0, jitter=0.0):
    pts = []
    for k in range(n):
        a = phase + TAU * k / n
        r = 1.0 + (random.uniform(-jitter, jitter) if jitter else 0.0)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return pts


def add_prism(mesh, poly, z0, z1, mat, cap_top=True):
    n = len(poly)
    v = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    f = [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)]
    if cap_top:
        f.append(list(range(n, 2 * n)))
    mesh.add(v, f, mat)


def add_box(mesh, x0, y0, z0, x1, y1, z1, mat, rot=0.0):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for x, y in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:
        px, py = x - cx, y - cy
        pts.append((cx + px * c - py * s, cy + px * s + py * c))
    v = [(p[0], p[1], z0) for p in pts] + [(p[0], p[1], z1) for p in pts]
    f = [[3, 2, 1, 0], [4, 5, 6, 7]] + [[k, (k + 1) % 4, 4 + (k + 1) % 4, 4 + k] for k in range(4)]
    mesh.add(v, f, mat)


def add_cyl(mesh, cx, cy, r, z0, z1, mat, seg=14, cap=True):
    v = [(cx + math.cos(TAU * k / seg) * r, cy + math.sin(TAU * k / seg) * r, z0) for k in range(seg)]
    v += [(cx + math.cos(TAU * k / seg) * r, cy + math.sin(TAU * k / seg) * r, z1) for k in range(seg)]
    f = [[k, (k + 1) % seg, seg + (k + 1) % seg, seg + k] for k in range(seg)]
    if cap:
        f.append(list(range(seg, 2 * seg)))
    mesh.add(v, f, mat)


def add_cone(mesh, cx, cy, r, z0, z1, mat, seg=14):
    v = [(cx + math.cos(TAU * k / seg) * r, cy + math.sin(TAU * k / seg) * r, z0) for k in range(seg)]
    v.append((cx, cy, z1))
    mesh.add(v, [[k, (k + 1) % seg, seg] for k in range(seg)], mat)


def add_gable(mesh, x0, y0, x1, y1, z_eave, rise, mat, oh=0.6):
    """سقف جملوني: الجملون على المحور الأطول."""
    a0, b0, a1, b1 = x0 - oh, y0 - oh, x1 + oh, y1 + oh
    if (y1 - y0) >= (x1 - x0):
        m = (y0 + y1) / 2
        v = [(a0, b0, z_eave), (a1, b0, z_eave), (a1, b1, z_eave), (a0, b1, z_eave),
             (a0, m, z_eave + rise), (a1, m, z_eave + rise)]
        f = [[0, 1, 5, 4], [3, 4, 5, 2], [0, 4, 3], [1, 2, 5]]
    else:
        m = (x0 + x1) / 2
        v = [(a0, b0, z_eave), (a1, b0, z_eave), (a1, b1, z_eave), (a0, b1, z_eave),
             (m, b0, z_eave + rise), (m, b1, z_eave + rise)]
        f = [[1, 0, 4, 5], [4, 3, 2, 5], [0, 3, 4], [1, 5, 2]]
    mesh.add(v, f, mat)


def add_ring_wall(mesh, poly, thickness, z0, h, mat, merlon=True):
    """سور حلقي + ممر + شرفات على الحافة الخارجية فقط."""
    n = len(poly)
    cx = sum(p[0] for p in poly) / n
    cy = sum(p[1] for p in poly) / n
    inner = []
    for x, y in poly:
        d = math.hypot(x - cx, y - cy) or 1.0
        s = max(0.0, d - thickness) / d
        inner.append((cx + (x - cx) * s, cy + (y - cy) * s))
    z1 = z0 + h
    ov = [(x, y, z0) for x, y in poly] + [(x, y, z1) for x, y in poly]
    mesh.add(ov, [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)], mat)
    iv = [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in inner]
    mesh.add(iv, [[(k + 1) % n, k, n + k, n + (k + 1) % n] for k in range(n)], mat)
    top = [(poly[k][0], poly[k][1], z1) for k in range(n)] + [(inner[k][0], inner[k][1], z1) for k in range(n)]
    mesh.add(top, [[k, (k + 1) % n, n + (k + 1) % n, n + k] for k in range(n)], mat)

    if merlon:
        for k in range(n):
            x0, y0 = poly[k]
            x1, y1 = poly[(k + 1) % n]
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 3.0:
                continue
            ang = math.atan2(y1 - y0, x1 - x0)
            nm = max(1, int(L / 3.0))
            for m in range(nm):
                t = (m + 0.5) / nm
                mx, my = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                bx = mx + math.cos(ang) * 0.9
                by = my + math.sin(ang) * 0.9
                add_box(mesh, bx - 0.7, by - 0.45, z1, bx + 0.7, by + 0.45, z1 + 1.25, mat, rot=ang)


# ---------------- المشهد ----------------
def build(out_dir):
    mesh = Mesh()

    # ===== البحر (شبكة بلاطات كبيرة — تفادي مشاكل القصّ عند حدود الكاميرا) =====
    N = 26
    span = 4400.0
    step = 2 * span / N
    for i in range(N):
        for j in range(N):
            x0 = -span + i * step
            y0 = -span + j * step
            add_box(mesh, x0, y0, SEA - 6, x0 + step, y0 + step, SEA, "water")

    # ===== الصخرة (طبقات متتابعة) =====
    levels = []
    for i, z in enumerate(ROCK_STEPS):
        t = i / (len(ROCK_STEPS) - 1)
        s = 1.0 - 0.68 * (t ** 1.85)
        poly = poly_ring(40, 215 * s, 275 * s, -8 + i * 3.5, 18 - i * 6.5, phase=0.35, jitter=0.07)
        levels.append((poly, float(z)))
    z_prev = SEA - 4
    for i, (poly, z) in enumerate(levels):
        mat = "grass" if i == len(levels) - 1 else ("rock" if i < len(levels) - 3 else "dirt")
        add_prism(mesh, poly, z_prev, z, mat)
        # حواف صخرية بارزة (كسور الطبقات) — تظهر الجرف دراميًا من البحر
        if i < 6:
            for k in range(0, len(poly), 2):
                x, y = poly[k]
                d = math.hypot(x, y) or 1.0
                out = 1.0 + random.uniform(0.03, 0.10)
                lx, ly = x * out, y * out
                w = random.uniform(9.0, 22.0)
                ang = math.atan2(y, x) + math.pi / 2
                add_box(mesh, lx - w / 2, ly - 6, z - random.uniform(6, 14), lx + w / 2, ly + 6, z, "rock", rot=ang)
        z_prev = z

    # ===== المدينة (5 مصاطب) =====
    houses = 0
    for li in range(4, len(levels) - 1):
        poly, z = levels[li]
        for k in range(0, len(poly), 1):
            for rep in range(5):
                t = rep / 5.0
                sc = 1.0 - 0.115 * t
                x = poly[k][0] * sc
                y = poly[k][1] * sc
                w = random.uniform(7.0, 9.5)
                d = random.uniform(6.5, 8.5)
                h = random.uniform(7.0, 13.0)
                ang = math.atan2(y, x) + math.pi / 2
                add_box(mesh, x - w / 2, y - d / 2, z, x + w / 2, y + d / 2, z + h, "plaster", rot=ang)
                add_gable(mesh, x - w / 2, y - d / 2, x + w / 2, y + d / 2, z + h,
                          (d * 0.66 if d >= w else w * 0.66),
                          "terracotta" if random.random() < 0.63 else "slate")
                houses += 1
            # أبراج صغيرة على حافة المصطبة (كما في المرجع: نقاط دفاعية متكررة)
            if k % 3 == 0:
                x, y = poly[k]
                r = random.uniform(4.0, 5.5)
                add_cyl(mesh, x, y, r, z - 6, z + 18, "granite", seg=12)
                add_cone(mesh, x, y, r * 1.35, z + 18, z + 18 + r * 1.8, "slate", seg=12)

    # ===== الأسوار الثلاثة =====
    def level_at(z):
        return min(range(len(levels)), key=lambda i: abs(levels[i][1] - z))

    for (z0, h, th, s) in WALL_RINGS:
        base = levels[level_at(z0)][0]
        poly = [(x * s, y * s) for x, y in base]
        add_ring_wall(mesh, poly, th, z0, h, "granite")
        n = len(poly)
        for k in range(0, n, 4):
            x, y = poly[k]
            r = random.uniform(5.5, 7.5)
            th_t = random.uniform(24.0, 30.0)
            add_cyl(mesh, x, y, r, z0 - 3, z0 + th_t, "granite", seg=12)
            add_cone(mesh, x, y, r * 1.3, z0 + th_t, z0 + th_t + r * 1.9, "slate", seg=12)
            if random.random() < 0.6:
                add_cyl(mesh, x, y, 0.4, z0 + th_t + r * 1.9, z0 + th_t + r * 1.9 + 4.0, "gilded", seg=6)

    # ===== بوابة بحرية + الجسر =====
    gx, gy = 236.0, -150.0
    for sx in (-1, 1):
        add_cyl(mesh, gx + sx * 15, gy, 7.0, 4.0, 38.0, "granite", seg=16)
        add_cone(mesh, gx + sx * 15, gy, 9.0, 38.0, 56.0, "slate", seg=16)
    add_box(mesh, gx - 9, gy - 8, 4.0, gx + 9, gy + 8, 30.0, "granite")

    L, na, dw, dz = CAUSEWAY["len"], CAUSEWAY["arches"], CAUSEWAY["deck_w"], CAUSEWAY["deck_z"]
    x0, y0 = gx + 14, gy
    seg = L / na
    for i in range(na + 1):
        x = x0 + i * seg
        add_box(mesh, x - 4.0, y0 - dw / 2 - 0.6, 0.0, x + 4.0, y0 + dw / 2 + 0.6, dz - 3.0, "granite")
    add_box(mesh, x0 - 8, y0 - dw / 2, dz - 3.0, x0 + L + 8, y0 + dw / 2, dz, "granite")
    for sx in (-1, 1):
        add_box(mesh, x0 - 8, y0 + sx * dw / 2 - 0.5, dz, x0 + L + 8, y0 + sx * dw / 2 + 0.5, dz + 1.5, "granite")
    for i in range(na):                       # عقود
        cxx = x0 + i * seg + seg / 2
        r = seg / 2 - 0.8
        for k in range(10):
            a0, a1 = math.pi * k / 10, math.pi * (k + 1) / 10
            p0x, p0z = cxx + math.cos(a0) * r, dz - 3.0 - math.sin(a0) * r
            p1x, p1z = cxx + math.cos(a1) * r, dz - 3.0 - math.sin(a1) * r
            for sy in (-1, 1):
                yy = y0 + sy * (dw / 2 + 0.7)
                mesh.add([(p0x - 0.6, yy, p0z), (p0x + 0.6, yy, p0z), (p1x + 0.6, yy, p1z), (p1x - 0.6, yy, p1z)],
                         [[0, 1, 2, 3]], "granite")

    # ===== المرفأ =====
    qz = HARBOUR_Z
    for (ax0, ay0, ax1, ay1) in [(-70, -250, 150, -200), (-160, -215, -80, -175), (60, -195, 150, -155)]:
        add_box(mesh, ax0, ay0, 0, ax1, ay1, qz, "quay")
    for i in range(9):
        x = -60 + i * 24
        add_box(mesh, x, -246, qz, x + 15, -226, qz + 7.0, "plaster")
        add_gable(mesh, x, -246, x + 15, -226, qz + 7.0, 5.4, "slate")
    for i in range(16):
        add_cyl(mesh, -150 + i * 19, -196, 0.5, 0, 9.0, "wood", seg=6)
    for i in range(6):
        sx = -40 + i * 40
        add_box(mesh, sx, -178, 0.5, sx + 20, -168, 5.5, "wood")
        add_cyl(mesh, sx + 10, -173, 0.4, 5.5, 21.0, "wood", seg=6)

    # ===== الشلالان =====
    for i, wf in enumerate(WATERFALLS):
        wx = -150 + i * 62
        wy = -215 - i * 12
        top = 74.0 - i * 10
        h = wf["h"]
        mesh.add([(wx, wy, top), (wx + wf["w"], wy, top),
                  (wx + wf["w"] + 5, wy + 8, top - h), (wx - 5, wy + 8, top - h)],
                 [[0, 1, 2, 3]], "foam")
        add_box(mesh, wx - 9, wy - 2, 0.2, wx + wf["w"] + 9, wy + 13, 2.4, "foam")

    # ===== قصر/كاتدرائية القمة =====
    _, z_top = levels[-1]
    add_box(mesh, -58, -36, z_top, 58, 36, z_top + 30, "sandstone")
    add_gable(mesh, -58, -36, 58, 36, z_top + 30, 26.0, "slate", oh=1.4)
    add_box(mesh, -30, -22, z_top + 30, 30, 22, z_top + 44, "sandstone")   # صحن الكاتدرائية
    add_box(mesh, -14, -14, z_top + 24, 14, 14, z_top + 76, "sandstone")
    add_cone(mesh, 0, 0, 15.5, z_top + 76, z_top + 112, "slate", seg=18)
    add_cyl(mesh, 0, 0, 0.55, z_top + 112, z_top + 120, "gilded", seg=6)
    for sx in (-1, 1):
        add_cyl(mesh, sx * 64, 0, 7.5, z_top - 3, z_top + 52, "sandstone", seg=16)
        add_box(mesh, sx * 71.5, -8, z_top + 46, sx * 56.5, 8, z_top + 52, "sandstone")
    for k, (dx, dy) in enumerate([(-44, 28), (44, 28), (-44, -28), (44, -28), (-22, 32), (22, 32)]):
        r, hh = (4.2, 50.0) if k < 4 else (3.4, 40.0)
        add_cyl(mesh, dx, dy, r, z_top - 2, z_top + hh, "sandstone", seg=12)
        add_cone(mesh, dx, dy, r * 1.35, z_top + hh, z_top + hh + r * 3.0, "slate", seg=12)
    for k in range(10):                                   # دعامات طائرة
        x = -50 + k * 11.0
        for sy in (-1, 1):
            mesh.add([(x, sy * 36, z_top + 9), (x + 4.5, sy * 36, z_top + 9),
                      (x + 4.5, sy * 49, z_top + 24), (x, sy * 49, z_top + 24)],
                     [[0, 1, 2, 3]], "sandstone")
    for (x, y) in [(-44, 32), (44, 32), (-64, 0), (64, 0)]:   # رايات
        mesh.add([(x, y, z_top + 48), (x + 6.5, y, z_top + 48),
                  (x + 6.5, y, z_top + 30), (x, y, z_top + 30)], [[0, 1, 2, 3]], "banner")

    # ===== الحدائق الملكية =====
    add_box(mesh, 74, 44, z_top, 136, 96, z_top + 0.5, "grass")
    add_cyl(mesh, 105, 70, 6.0, z_top, z_top + 1.4, "marble", seg=16)

    mesh.export(os.path.join(out_dir, "castle_city"))
    with open(os.path.join(out_dir, "polys.json"), "w") as fh:
        json.dump({"v": [[round(c, 3) for c in p] for p in mesh.v],
                   "f": mesh.f, "uv": mesh.uv, "mat": mesh.mat,
                   "mats": {k: {"tex": v[0], "tile": v[1], "color": v[2]} for k, v in MAT.items()}},
                  fh)
    print(f"  ✓ {houses} مبنى | {len(mesh.f)} وجه إجمالًا")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="build")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    build(a.out)
