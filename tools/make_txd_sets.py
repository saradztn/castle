#!/usr/bin/env python3
"""
make_txd_sets.py — توليد مجموعات الخامات بمقاسات LOD الأربعة استعدادًا لبناء TXD
الاستخدام:
  python3 tools/make_txd_sets.py --src textures/src --out build/txd --sets 2048,1024,512,256
"""
import argparse, glob, os
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("--src", default="textures/src")
ap.add_argument("--out", default="build/txd")
ap.add_argument("--sets", default="2048,1024,512,256")
a = ap.parse_args()

sizes = [int(s) for s in a.sets.split(",")]
files = sorted(glob.glob(os.path.join(a.src, "*_albedo.png")))
if not files:
    raise SystemExit("لا خامات في " + a.src)

names = {"high": sizes[0] if len(sizes) > 0 else 2048,
         "medium": sizes[1] if len(sizes) > 1 else 1024,
         "low": sizes[2] if len(sizes) > 2 else 512,
         "distant": sizes[3] if len(sizes) > 3 else 256}

print(f"{len(files)} خامة → {len(names)} مجموعات")
for lvl, sz in names.items():
    d = os.path.join(a.out, lvl)
    os.makedirs(d, exist_ok=True)
    for f in files:
        n = os.path.basename(f)
        im = Image.open(f).convert("RGB").resize((sz, sz), Image.LANCZOS)
        im.save(os.path.join(d, n), optimize=True)
    print(f"  ✓ {lvl:8s} {sz}px → {d}  ({len(files)} ملف)")

print("\nالخطوة التالية: افتح كل مجلد في Magic.TXD وأنشئ ملف .txd بنفس الأسماء (DXT1، وDXT5 للشفاف).")
