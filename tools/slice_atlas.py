#!/usr/bin/env python3
"""
slice_atlas.py — تقطيع لوحة الأطلس إلى خامات منفصلة + توليد خرائط PBR
Castle & Palace (MTA:SA)

الاستخدام:
  python3 tools/slice_atlas.py textures/atlas/atlas.png --grid 6x4 --out textures/src --size 2048 --derive-pbr
  python3 tools/slice_atlas.py textures/atlas/atlas.png --grid 4x4 --out textures/src
  python3 tools/slice_atlas.py textures/atlas/atlas.png --grid 2x3 --out textures/src --trim 1.5

المعاملات:
  --grid CxR     أعمدة × صفوف (المتاح: 6x4 و 4x4 و 2x3) الافتراضي 6x4
  --out DIR      مجلد الخرج (الافتراضي textures/src)
  --size N       مقاس كل خامة بعد القص (الافتراضي 2048، اكتب 0 للإبقاء على المقاس الأصلي)
  --trim PCT     نسبة اقتطاع من كل خانة لإزالة الفواصل الفاصلة بين الخانات (الافتراضي 1.0%)
  --suffix STR   لاحقة اسم الملف (الافتراضي _albedo)
  --derive-pbr   توليد _normal و _roughness و _ao من الألبيو (يحتاج numpy)
  --seamless     مزج الحواف لتقليل الخط الفاصل عند التكرار
"""

import argparse
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("PIL غير مثبّت:  pip install --break-system-packages pillow")

GRIDS = {
    # 6 أعمدة × 4 صفوف — 24 خامة (البرومبت الرئيسي)
    "6x4": [
        "stone_sandstone_ashlar", "stone_granite_wall", "stone_seaweathered_mossy",
        "plaster_lime_town", "stone_quay_granite", "stone_cobble_street",
        "roof_slate", "roof_tile_terracotta", "roof_shingle_wood",
        "wood_oak_timber", "wood_oak_door", "rock_cliff_strata",
        "terrain_grass", "water_ocean", "marble_floor_light",
        "stone_flagstone_floor", "wood_plank_floor", "wood_walnut_panel",
        "fabric_damask_red", "fabric_carpet_woven", "leather_hide",
        "metal_iron_forged", "metal_gilded_bronze", "metal_copper_verdigris",
    ],
    # 4 × 4 — 16 خامة (النسخة البديلة)
    "4x4": [
        "stone_sandstone_ashlar", "stone_granite_wall", "stone_seaweathered_mossy", "plaster_lime_town",
        "stone_cobble_street", "stone_quay_granite", "roof_slate", "roof_tile_terracotta",
        "wood_oak_timber", "wood_oak_door", "rock_cliff_strata", "terrain_grass",
        "water_ocean", "marble_floor_light", "metal_iron_forged", "fabric_carpet_woven",
    ],
    # 2 × 3 — 6 خامات (نسخة مصغّرة)
    "2x3": [
        "stone_sandstone_ashlar", "stone_granite_wall",
        "roof_slate", "wood_oak_timber",
        "stone_cobble_street", "rock_cliff_strata",
    ],
}


def seamless_blend(img, band=12):
    """مزج شريط الحواف المتقابل لتقليل الخط الفاصل عند التكرار (بسيط وسريع)."""
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(band):
            a = px[x, y]
            b = px[w - band + x, y]
            t = (x + 0.5) / band
            px[x, y] = tuple(int(a[i] * t + b[i] * (1 - t)) for i in range(3))
    for x in range(w):
        for y in range(band):
            a = px[x, y]
            b = px[x, h - band + y]
            t = (y + 0.5) / band
            px[x, y] = tuple(int(a[i] * t + b[i] * (1 - t)) for i in range(3))
    return img


def derive_pbr(img, out_base, size):
    """توليد normal / roughness / ao تقريبية من الألبيو."""
    try:
        import numpy as np
    except ImportError:
        print("  ! numpy غير مثبّت — تخطّي توليد الخرائط (pip install --break-system-packages numpy)")
        return
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

    # --- Normal من انحدار السطوع (Sobel) ---
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
    strength = 2.5
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(lum)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    normal = np.stack([(nx * 0.5 + 0.5), (ny * 0.5 + 0.5), (nz * 0.5 + 0.5)], axis=-1)
    Image.fromarray((normal * 255).astype("uint8")).resize((size, size), Image.LANCZOS).save(out_base + "_normal.png")

    # --- Roughness من السطوع المعكوس (الأسطح الفاتحة = أخشن عادةً في هذه المجموعة) ---
    k = 5
    pad = np.pad(lum, k, mode="edge")
    acc = np.zeros_like(lum)
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            acc += pad[k + dy:k + dy + lum.shape[0], k + dx:k + dx + lum.shape[1]]
    blur = acc / ((2 * k + 1) ** 2)
    rough = np.clip(0.35 + 0.5 * (1.0 - blur), 0.05, 1.0)
    Image.fromarray((rough * 255).astype("uint8")).resize((size, size), Image.LANCZOS).save(out_base + "_roughness.png")

    # --- AO من التباين المحلي (الفتحات أغمق) ---
    ao = np.clip(blur ** 0.75, 0.0, 1.0)
    Image.fromarray((ao * 255).astype("uint8")).resize((size, size), Image.LANCZOS).save(out_base + "_ao.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("atlas")
    ap.add_argument("--grid", default="6x4", choices=list(GRIDS.keys()))
    ap.add_argument("--out", default="textures/src")
    ap.add_argument("--size", type=int, default=2048)
    ap.add_argument("--trim", type=float, default=1.0, help="نسبة الاقتطاع من كل خانة %")
    ap.add_argument("--suffix", default="_albedo")
    ap.add_argument("--derive-pbr", action="store_true")
    ap.add_argument("--seamless", action="store_true")
    args = ap.parse_args()

    cols, rows = (int(v) for v in args.grid.split("x"))
    names = GRIDS[args.grid]
    assert len(names) == cols * rows, "عدد الأسماء لا يطابق الشبكة"

    img = Image.open(args.atlas).convert("RGB")
    W, H = img.size
    cw, ch = W // cols, H // rows
    pad_x, pad_y = int(cw * args.trim / 100), int(ch * args.trim / 100)
    os.makedirs(args.out, exist_ok=True)

    print(f"الأطلس {W}x{H} | شبكة {args.grid} | خانة {cw}x{ch} | الخرج: {args.out}")
    made = 0
    for r in range(rows):
        for c in range(cols):
            name = names[r * cols + c]
            box = (c * cw + pad_x, r * ch + pad_y, (c + 1) * cw - pad_x, (r + 1) * ch - pad_y)
            cell = img.crop(box)
            size = args.size if args.size else cell.size[0]
            if size:
                cell = cell.resize((size, size), Image.LANCZOS)
            if args.seamless:
                cell = seamless_blend(cell)
            base = os.path.join(args.out, name + args.suffix)
            cell.save(base + ".png")
            if args.derive_pbr:
                derive_pbr(cell, os.path.join(args.out, name), cell.size[0])
            print(f"  ✓ {name}{args.suffix}.png  ({cell.size[0]}x{cell.size[1]})")
            made += 1
    print(f"تم: {made} خامة" + ("  (+ normal/roughness/ao)" if args.derive_pbr else ""))


if __name__ == "__main__":
    main()
