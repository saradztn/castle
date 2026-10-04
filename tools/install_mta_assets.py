#!/usr/bin/env python3
"""
install_mta_assets.py — تجهيز أصول مورد MTA من مخرجات الموديل والخامات
Castle & Palace

ينسخ:
  textures/src/*_albedo.png  →  mta/castle/textures/
  build/lamps.json           →  mta/castle/data/lamps.json
  build/spawns.json          →  mta/castle/data/spawns.json
ويولّد:
  mta/castle/data/parts.json (تقسيم الموديل لأجزاء + مقاسات LOD للتوثيق)

الاستخدام:
  python3 tools/install_mta_assets.py
"""

import json, os, shutil, glob, sys

SRC_TEX = "textures/src"
DST = "mta/castle"

# الخامات التي يحتاجها الموديل في MTA (تُستخدم عبر الشيدر/الـTXD)
NEEDED = [
    "stone_sandstone_ashlar", "stone_granite_wall", "plaster_lime_town",
    "roof_slate", "roof_tile_terracotta", "roof_shingle_wood",
    "wood_oak_timber", "wood_oak_door", "rock_cliff_strata",
    "terrain_grass", "terrain_dirt_road", "water_ocean", "water_foam_shore",
    "stone_cobble_street", "stone_flagstone_floor", "stone_quay_granite",
    "marble_floor_light", "metal_iron_forged", "metal_gilded_bronze",
    "metal_copper_verdigris", "fabric_banner_heraldry",
    "glass_leaded_pane_emissive", "foliage_leaves",
]


def main():
    os.makedirs(f"{DST}/textures", exist_ok=True)
    os.makedirs(f"{DST}/data", exist_ok=True)
    os.makedirs(f"{DST}/models", exist_ok=True)

    copied = 0
    for name in NEEDED:
        s = f"{SRC_TEX}/{name}_albedo.png"
        if os.path.exists(s):
            shutil.copy2(s, f"{DST}/textures/{name}_albedo.png")
            copied += 1
        else:
            print(f"  ! مفقودة: {name}")
    print(f"  ✓ نُسخت {copied} خامة إلى {DST}/textures")

    for src, dst in [("build/lamps.json", f"{DST}/data/lamps.json"),
                     ("build/spawns.json", f"{DST}/data/spawns.json")]:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            n = len(json.load(open(src)))
            print(f"  ✓ {dst}  ({n} عنصر)")
        else:
            print(f"  ! مفقود: {src} — شغّل tools/build_city.py أولًا")

    polys = "build/polys.json"
    if os.path.exists(polys):
        d = json.load(open(polys))
        parts = {
            "total_faces": len(d["f"]),
            "total_vertices": len(d["v"]),
            "materials": sorted(set(d["mat"])),
            "lod_plan": {
                "lod0_full": {"faces": len(d["f"]), "desc": "الهندسة الكاملة — حتى 320م"},
                "lod1": {"target_faces": int(len(d["f"]) * 0.35), "desc": "إسقاط الزخارف والنوافذ"},
                "lod2": {"target_faces": int(len(d["f"]) * 0.10), "desc": "كتل وأسقف فقط"},
                "lod3": {"target_faces": int(len(d["f"]) * 0.02), "desc": "صومعة المدينة والقمة فقط"},
            },
        }
        json.dump(parts, open(f"{DST}/data/parts.json", "w"), indent=1)
        print(f"  ✓ {DST}/data/parts.json  ({parts['total_faces']} وجه، {len(parts['materials'])} مادة)")

    print("\nالخطوة التالية: حوّل build/castle_city.obj إلى DFF/COL (انظر mta/castle/README.txt)")


if __name__ == "__main__":
    main()
