#!/usr/bin/env python3
"""
process_textures.py — معالجة الخامات الفردية (صورة لكل خامة)
Castle & Palace (MTA:SA)

لكل ملف <id>_albedo.png داخل مجلد المصدر:
  1) (اختياري) --seamless      : مزج الحواف لجعل الخامة قابلة للتكرار.
  2) (اختياري) --derive-pbr    : استخراج <id>_normal.png / <id>_roughness.png / <id>_ao.png
  3) (اختياري) --alpha-decals  : تحويل الخلفية البيضاء إلى شفافية -> <id>_alpha.png
  4) (اختياري) --size N        : توحيد المقاس لكل الخرائط.
  5) (اختياري) --contact-sheet : صورة معاينة واحدة تجمع كل الخامات.

أمثلة:
  python3 tools/process_textures.py --src textures/src --size 1024 --seamless --derive-pbr --alpha-decals \
      --contact-sheet textures/preview/contact_sheet.jpg
"""

import argparse
import os
import glob
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("PIL غير مثبّت:  pip install --break-system-packages pillow")

try:
    import numpy as np
except ImportError:
    np = None


# ============================ الإعدادات ============================

# خامات لا تُكرَّر (بطاقة واحدة كاملة)
NON_TILEABLE = {
    "glass_stained_rose",
    "fabric_banner_heraldry",
    "glass_leaded_pane",
    "glass_leaded_pane_emissive",
    "fabric_tapestry",
}

# خامات شفافة (تُقصّ خلفيتها البيضاء إلى alpha)
ALPHA_IDS = {
    "water_foam_shore",
    "foliage_leaves",
    "decal_moss_patch",
    "decal_salt_bloom",
    "decal_water_streak",
    "decal_soot_grime",
    "decal_stone_crack",
    "metal_iron_grille",
}

# شدة بروز النورمال حسب نوع الخامة (أعلى = تفاصيل أعمق)
NORMAL_STRENGTH = {
    "stone_sandstone_ashlar": 2.2, "stone_granite_wall": 2.6, "stone_seaweathered_mossy": 3.0,
    "stone_quay_granite": 2.4, "stone_cobble_street": 3.2, "stone_flagstone_floor": 2.0,
    "roof_slate": 2.6, "roof_tile_terracotta": 3.0, "roof_shingle_wood": 3.0,
    "wood_oak_timber": 2.4, "wood_oak_door": 2.2, "wood_plank_floor": 2.0,
    "wood_walnut_panel": 2.4, "rock_cliff_strata": 3.4, "plaster_lime_town": 1.5,
    "terrain_grass": 3.0, "water_ocean": 1.8, "marble_floor_light": 0.9,
    "fabric_damask_red": 1.6, "fabric_carpet_woven": 2.6, "leather_hide": 1.8,
    "metal_iron_forged": 2.0, "metal_gilded_bronze": 1.8, "metal_copper_verdigris": 1.6,
    "terrain_dirt_road": 2.2, "wood_props_kit": 2.2,
}
DEFAULT_STRENGTH = 2.2


# ============================ الدوال ============================

def seamless_blend(img, band=20):
    """مزج الحواف المتقابلة لتقليل الخط الفاصل عند التكرار."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w, _ = a.shape
    band = max(2, min(band, w // 4, h // 4))
    t = ((np.arange(band, dtype=np.float32) + 0.5) / band)[None, :, None]
    # الحافة اليسرى مع اليمنى (معكوسة) ثم العليا مع السفلى
    left, right = a[:, :band].copy(), a[:, w - band:w][:, ::-1].copy()
    a[:, :band] = left * t + right * (1 - t)
    t2 = ((np.arange(band, dtype=np.float32) + 0.5) / band)[:, None, None]
    top, bot = a[:band].copy(), a[h - band:h][::-1].copy()
    a[:band] = top * t2 + bot * (1 - t2)
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"), "RGB")


def derive_pbr(img, out_base, strength, size):
    """استخراج normal / roughness / ao من صورة الألوان."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]

    # --- Normal من انحدار السطوع (Sobel بسيط) ---
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
    nx, ny, nz = -gx * strength, gy * strength, np.ones_like(lum)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    normal = np.stack([nx * 0.5 + 0.5, ny * 0.5 + 0.5, nz * 0.5 + 0.5], axis=-1)
    Image.fromarray((normal * 255).astype("uint8"), "RGB").resize((size, size), Image.LANCZOS) \
        .save(out_base + "_normal.png")

    # --- Roughness من السطوع المعكوس بعد تنعيم ---
    k = 4
    pad = np.pad(lum, k, mode="edge")
    acc = np.zeros_like(lum)
    for dy in range(-k, k + 1):
        for dx in range(-k, k + 1):
            acc += pad[k + dy:k + dy + lum.shape[0], k + dx:k + dx + lum.shape[1]]
    blur = acc / ((2 * k + 1) ** 2)
    rough = np.clip(0.35 + 0.5 * (1.0 - blur), 0.05, 1.0)
    Image.fromarray((rough * 255).astype("uint8"), "L").resize((size, size), Image.LANCZOS) \
        .save(out_base + "_roughness.png")

    # --- AO من التباين المحلي حول الفتحات ---
    ao = np.clip(blur ** 0.75, 0.0, 1.0)
    Image.fromarray((ao * 255).astype("uint8"), "L").resize((size, size), Image.LANCZOS) \
        .save(out_base + "_ao.png")


def key_white_to_alpha(img, thr=236, feather=14):
    """تحويل الخلفية البيضاء إلى قناة شفافية (للـdecals)."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    lum = a.mean(axis=2)
    alpha = np.clip((thr - lum) / feather * 255.0, 0, 255)
    out = np.dstack([a, alpha]).astype("uint8")
    return Image.fromarray(out, "RGBA")


def make_contact_sheet(files, out_path, cols=7, thumb=210, label_h=16):
    """صورة معاينة واحدة تجمع كل الخامات بصورة مصغّرة + اسم الخامة."""
    if not files:
        print("  (لا ملفات لبناء لوح المعاينة)")
        return
    rows = (len(files) + cols - 1) // cols
    cell = thumb + label_h + 8
    sheet = Image.new("RGB", (cols * cell + 8, rows * cell + 8), (32, 33, 36))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB").resize((thumb, thumb), Image.LANCZOS)
        cx, cy = 8 + (i % cols) * cell, 8 + (i // cols) * cell
        sheet.paste(im, (cx, cy))
        name = os.path.basename(f).replace("_albedo.png", "")
        draw.text((cx + 2, cy + thumb + 2), name[:30], fill=(210, 210, 210))
    sheet.save(out_path, quality=90)
    print(f"  ✓ لوح المعاينة: {out_path}  ({len(files)} خامة)")


# ============================ التنفيذ ============================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="textures/src")
    ap.add_argument("--size", type=int, default=1024, help="0 = إبقاء المقاس الأصلي")
    ap.add_argument("--seamless", action="store_true")
    ap.add_argument("--band", type=int, default=20, help="عرض شريط المزج بالبكسل")
    ap.add_argument("--derive-pbr", action="store_true")
    ap.add_argument("--alpha-decals", action="store_true")
    ap.add_argument("--contact-sheet", default="")
    ap.add_argument("--cols", type=int, default=7)
    ap.add_argument("--no-square-crop", dest="square_crop", action="store_false",
                    help="تعطيل الاقتطاع المربّع")
    ap.add_argument("--quantize", type=int, default=0,
                    help="تقليل ألوان الألبيو إلى N لون (مثال 256) لتخفيف حجم المستودع")
    args = ap.parse_args()

    if np is None:
        sys.exit("numpy مطلوب:  pip install --break-system-packages numpy")

    files = sorted(glob.glob(os.path.join(args.src, "*_albedo.png")))
    if not files:
        sys.exit(f"لم أجد أي ملف *_albedo.png داخل {args.src}")

    print(f"معالجة {len(files)} خامة من {args.src}")
    for f in files:
        tid = os.path.basename(f).replace("_albedo.png", "")
        base = os.path.join(os.path.dirname(f), tid)
        im = Image.open(f).convert("RGB")

        # اقتطاع مربّع من المنتصف (المولّد يُخرج 16:9) للحفاظ على النسب الحقيقية
        if args.square_crop and im.size[0] != im.size[1]:
            s = min(im.size)
            im = im.crop(((im.size[0] - s) // 2, (im.size[1] - s) // 2,
                          (im.size[0] - s) // 2 + s, (im.size[1] - s) // 2 + s))

        if args.size and im.size[0] != args.size:
            im = im.resize((args.size, args.size), Image.LANCZOS)

        tileable = tid not in NON_TILEABLE
        if args.seamless and tileable:
            im = seamless_blend(im, args.band)
        im.save(base + "_albedo.png")
        if args.quantize:
            q = im.convert("P", palette=Image.ADAPTIVE, colors=args.quantize, dither=Image.FLOYDSTEINBERG)
            q.save(base + "_albedo.png", optimize=True)

        if args.alpha_decals and tid in ALPHA_IDS:
            key_white_to_alpha(im).save(base + "_alpha.png")

        if args.derive_pbr:
            derive_pbr(im, base, NORMAL_STRENGTH.get(tid, DEFAULT_STRENGTH), im.size[0])

        print(f"  ✓ {tid}  ({im.size[0]}px)" + ("" if tileable else "  [بطاقة كاملة]"))

    if args.contact_sheet:
        os.makedirs(os.path.dirname(args.contact_sheet), exist_ok=True)
        make_contact_sheet(files, args.contact_sheet, cols=args.cols)

    print("تم.")


if __name__ == "__main__":
    main()
