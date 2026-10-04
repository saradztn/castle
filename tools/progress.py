#!/usr/bin/env python3
"""
progress.py — حساب نسبة الإنجاز لكل جزء من المشروع (من 100%)
يقرأ ما هو موجود فعليًا في المستودع ويطبع جدولًا + النسبة الإجمالية الموزونة.
"""
import os, glob, json, sys

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HOME)


def count(pattern):
    return len(glob.glob(pattern))


def exists(p):
    return os.path.exists(p)


def file_size_mb(p):
    tot = 0
    for f in glob.glob(p):
        try:
            tot += os.path.getsize(f)
        except OSError:
            pass
    return tot / 1e6


STAGES = []

# 1) تحليل المرجع
p1 = 100 if exists("docs/01_reference_brief_ar.md") else 0
STAGES.append(("1) تحليل الصورة المرجعية وقياساتها", p1, 5, "docs/01_reference_brief_ar.md"))

# 2) الخامات (39 مطلوبة)
tex = count("textures/src/*_albedo.png")
p2 = min(100, round(tex / 39 * 100))
STAGES.append((f"2) الخامات PBR ({tex}/39)", p2, 20, "textures/src/"))

# 3) الهندسة الخارجية (تقدير من عدد الأوجه والمراحل المنفّذة)
faces = 0
if exists("build/polys.json"):
    faces = len(json.load(open("build/polys.json"))["f"])
p3 = min(100, round(faces / 60000 * 100)) if faces else 0
STAGES.append((f"3) هندسة المدينة ({faces} وجه)", p3, 22, "tools/build_city.py"))

# 4) الداخليات (14) — الإطار موجود، الهندسة لم تُبنَ
p4 = 15
STAGES.append(("4) الداخليات الأربع عشرة", p4, 10, "mta/client/interior.lua"))

# 5) كود MTA
mta_files = count("mta/**/*.lua") + count("mta/**/*.fx") + count("mta/*.xml")
p5 = min(100, round(mta_files / 16 * 100))
STAGES.append((f"5) كود MTA:SA الكامل ({mta_files} ملف)", p5, 18, "mta/"))

# 6) LOD
lod = count("mta/models/lod/*.obj")
p6 = min(100, round(lod / 18 * 100))
STAGES.append((f"6) مستويات LOD ({lod}/18 ملف)", p6, 6, "mta/models/lod/"))

# 7) تحويل DFF/TXD/COL
p7 = 10 if count("mta/models/parts/*.obj") else 0
STAGES.append(("7) تحويل إلى DFF + TXD + COL", p7, 12, "mta/models/parts/"))

# 8) المقارنة البصرية والتوليد
p8 = 55 if count("renders/preview_*.png") else 0
STAGES.append(("8) المقارنة البصرية (نهار/ليل)", p8, 7, "renders/"))

total_w = sum(s[2] for s in STAGES)
overall = sum(s[1] * s[2] for s in STAGES) / total_w

print("=" * 62)
print("  تقدّم مشروع Castle & Palace — مدينة القلعة الساحلية (MTA:SA)")
print("=" * 62)
for name, pct, w, path in STAGES:
    bar = "█" * round(pct / 5) + "░" * (20 - round(pct / 5))
    print(f"  {name:38s} {bar} {pct:5.1f}%")
print("-" * 62)
print(f"  الإجمالي الموزون: {overall:.1f}% من 100%")
print(f"  حجم المستودع: {file_size_mb('**/*'):.0f} MB تقريبًا")
print("=" * 62)
