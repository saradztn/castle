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

# 2) الخامات
tex = count("textures/src/*_albedo.png")
STAGES.append((f"2) الخامات PBR ({tex}/39)", min(100, round(tex / 39 * 100)), 15, "textures/src/"))

# 3) الهندسة (الهدف 45,000 وجه)
faces = 0
if exists("build/polys.json"):
    faces = len(json.load(open("build/polys.json"))["f"])
STAGES.append((f"3) هندسة المدينة ({faces} وجه)", min(100, round(faces / 45000 * 100)), 22, "tools/build_city.py"))

# 4) الداخليات: 14 غرفة مبنية + بيانات + نظام انتقال
rooms = 0
if exists("mta/data/interiors.json"):
    rooms = len(json.load(open("mta/data/interiors.json")))
p4 = 0
if rooms:
    p4 = 70
    if exists("mta/client/interior.lua"):
        p4 += 20
    if exists("build/lod_report.json") and "interiors" in open("build/lod_report.json").read():
        p4 += 10
STAGES.append((f"4) الداخليات ({rooms}/14)", p4, 10, "mta/data/interiors.json"))

# 5) كود MTA
mta_files = count("mta/**/*.lua") + count("mta/**/*.fx") + count("mta/*.xml")
STAGES.append((f"5) كود MTA:SA الكامل ({mta_files} ملف)", min(100, round(mta_files / 18 * 100)), 16, "mta/"))

# 6) LOD: 7 أجزاء × 4 مستويات
lod = count("mta/models/lod/*.obj") + count("mta/models/parts/*.obj")
STAGES.append((f"6) مستويات LOD ({lod}/28 ملف)", min(100, round(lod / 28 * 100)), 6, "mta/models/lod/"))

# 7) الجاهزية للتصدير: OBJ + COL/TXD المطلوبة
web = 0
parts = count("mta/models/parts/*.obj")
web += min(50, round(parts / 7 * 50))
web += 25 if exists("build/txd/high") else 0
web += 10 if exists("mta/models/castle.txd") or exists("docs/05_mta_install_ar.md") else 0
STAGES.append((f"7) التصدير DFF/TXD/COL ({parts}/7 أجزاء OBJ)", min(100, web), 14, "mta/models/parts/"))

# 8) المقارنة البصرية
vis = 0
vis += 40 if exists("renders/compare_day_night.jpg") else 0
vis += 35 if exists("docs/06_visual_comparison_ar.md") else 0
vis += 25 if count("renders/preview_*.png") >= 2 else 0
STAGES.append(("8) المقارنة البصرية (11 نقطة)", min(100, vis), 12, "docs/06_visual_comparison_ar.md"))

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
