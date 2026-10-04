#!/usr/bin/env python3
"""
make_lod.py — تقسيم المدينة إلى أجزاء + توليد 4 مستويات LOD (Castle & Palace)

المدخل:  build/polys.json
المخرجات:
  mta/models/parts/<part>.obj          (تفصيل كامل — يُصدَّر لاحقًا DFF)
  mta/models/lod/<part>_medium.obj
  mta/models/lod/<part>_low.obj
  mta/models/lod/<part>_distant.obj
  build/lod_report.json                (إحصاء لكل مستوى)

طريقة التبسيط: تجميع الرؤوس في شبكة (Vertex Clustering) بحجم خلية متدرّج،
مع إسقاط الأوجه المنحلّة — سريعة وفعّالة للإنتاج.
"""

import argparse, json, math, os
from collections import defaultdict
import numpy as np

# ============ قواعد تقسيم الأجزاء (بالمنطقة) ============
def part_of(cx, cy, cz):
    if cy > 5000.0:
        return "interiors"                     # الـ14 داخلية (منطقة الإزاحة 0,6000,0)
    if cz >= 100.0:
        return "palace"
    if cx > 175.0:
        return "causeway"                      # الجسر + البوابة البحرية
    if cy < -160.0 and cz < 40.0:
        return "harbour"                       # المرفأ والأرصفة والسفن
    if cz >= 18.0 and cy > -150.0 and abs(cx) < 175.0:
        return "town"                          # المدينة والمصاطب
    if 18.0 <= cz <= 90.0 and abs(cx) < 230.0:
        return "walls"                         # الأسوار والأبراج (تداخل مع المدينة مقصود)
    return "cliff"                             # الصخرة والجرف والشلالات


# ============ تبسيط: تجميع الرؤوس ============
def decimate(verts, faces, cell):
    grid = {}
    remap = np.empty(len(verts), dtype=np.int64)
    new_verts = []
    for i, (x, y, z) in enumerate(verts):
        key = (int(x // cell), int(y // cell), int(z // cell))
        idx = grid.get(key)
        if idx is None:
            idx = len(new_verts)
            grid[key] = idx
            new_verts.append((x, y, z))
        remap[i] = idx

    new_faces = []
    for fc in faces:
        m = [int(remap[i]) for i in fc]
        # إزالة التكرار داخل الوجه
        clean = []
        for v in m:
            if not clean or clean[-1] != v:
                clean.append(v)
        if len(clean) > 2 and clean[0] == clean[-1]:
            clean.pop()
        if len(clean) >= 3:
            new_faces.append(clean)
    return new_verts, new_faces


def write_obj(path, verts, faces, mats, matdef, part):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(f"# Castle & Palace — {part} LOD\n")
        f.write(f"mtllib {os.path.basename(path).replace('.obj', '.mtl')}\n")
        by_mat = defaultdict(list)
        for fc, m in zip(faces, mats):
            by_mat[m].append(fc)
        for m, fcs in by_mat.items():
            f.write(f"\nusemtl mat_{m}\n")
            for fc in fcs:
                for vi in fc:
                    x, y, z = verts[vi]
                    f.write(f"v {x:.2f} {y:.2f} {z:.2f}\n")
    with open(path.replace(".obj", ".mtl"), "w") as f:
        for m, d0 in matdef.items():
            tex = d0["tex"] if isinstance(d0, dict) else d0[0]
            col = d0["color"] if isinstance(d0, dict) else d0[2]
            f.write(f"newmtl mat_{m}\n")
            f.write(f"Kd {float(col[0]):.3f} {float(col[1]):.3f} {float(col[2]):.3f}\n")
            f.write(f"map_Kd textures/src/{tex}_albedo.png\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="build/polys.json")
    ap.add_argument("--out", default="mta/models")
    ap.add_argument("--lod-cells", default="0.9,2.2,5.0", help="خلية التبسيط (م) للمستويات medium/low/distant")
    a = ap.parse_args()

    data = json.load(open(a.inp))
    V = data["v"]; F = data["f"]; M = data["mat"]; MD = data["mats"]

    parts = defaultdict(lambda: {"faces": [], "mats": []})
    for fc, m in zip(F, M):
        cx = sum(V[i][0] for i in fc) / len(fc)
        cy = sum(V[i][1] for i in fc) / len(fc)
        cz = sum(V[i][2] for i in fc) / len(fc)
        p = part_of(cx, cy, cz)
        parts[p]["faces"].append(fc)
        parts[p]["mats"].append(m)

    cells = [float(x) for x in a.lod_cells.split(",")]
    report = {}
    print(f"تقسيم إلى {len(parts)} أجزاء…")
    for p, d in parts.items():
        verts = [tuple(x) for x in V]
        # حفظ الأجزاء الكامل
        write_obj(os.path.join(a.out, "parts", f"{p}.obj"), verts, d["faces"], d["mats"], MD, p)
        stats = {"full": len(d["faces"])}
        # توليد LOD
        for lvl, cell in zip(("medium", "low", "distant"), cells):
            v2, f2 = decimate(verts, d["faces"], cell)
            write_obj(os.path.join(a.out, "lod", f"{p}_{lvl}.obj"), v2, f2, d["mats"], MD, p)
            stats[lvl] = len(f2)
        report[p] = stats
        print(f"  ✓ {p:9s} كامل={stats['full']:6d} متوسط={stats['medium']:6d} "
              f"منخفض={stats['low']:5d} بعيد={stats['distant']:5d}")

    os.makedirs("build", exist_ok=True)
    json.dump(report, open("build/lod_report.json", "w"), indent=2, ensure_ascii=False)
    total = sum(s["full"] for s in report.values())
    print(f"المجموع الكامل: {total} وجه | التقرير: build/lod_report.json")


if __name__ == "__main__":
    main()
