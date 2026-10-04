#!/usr/bin/env python3
"""
make_lamps.py — يستخرج/يولّد مواضع المصابيح (فوانيس، مشاعل، مناقل، نوافذ مضيئة)
من هندسة المدينة الفعلية → mta/data/lamps.json ليستهلكها شيدر الإضاءة النقطية.

المنهج:
  • فوانيس شوارع على حدود كل مصطبة (walk-around على محيط المستطيل بتباعد ~34 م) عند سطح المصطبة.
  • مشاعل على أبراج الأسوار الثلاث (WALL_RINGS: برج كل 5 قطع).
  • مناقل عند البوابة البحرية والجسر والمنارة.
  • نوافذ مضيئة موزّعة على واجهات القصر (نوع window).
"""
import json, math, os, sys, re

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HOME, "tools"))
os.chdir(HOME)

# نستورد طاولة المصاطب وبيانات الأسوار من المولّد نفسه (مصدر حقيقة واحد)
src = open("tools/build_city.py").read()

def grab_list(name):
    m = re.search(rf"^{name}\s*=\s*\[(.*?)\]", src, re.S | re.M)
    ns = {}
    exec(name + " = [" + m.group(1) + "]", ns)
    return ns[name]

TERRACES = grab_list("TERRACES")
WALL_RINGS = grab_list("WALL_RINGS")

lamps = []

def add(x, y, z, r, c, t="lamp"):
    lamps.append({"x": round(x, 2), "y": round(y, 2), "z": round(z, 2),
                  "r": r, "c": list(c), "t": t})

WARM  = [1.00, 0.74, 0.42]      # فانوس دافئ
TORCH = [1.00, 0.55, 0.22]      # مشعل
FIRE  = [1.00, 0.50, 0.17]      # منقل
BEAC  = [1.00, 0.86, 0.55]      # منارة

# ---------- 1) فوانيس الشوارع على حدود المصاطب ----------
SPACING = 34.0
for (z, (cx, cy), (w, d), mat) in TERRACES:
    if z < 0:            # المصاطب الصخرية تحت الماء/المدّ لا فوانيس عليها
        continue
    per = 2 * (w + d)
    n = max(6, int(per / SPACING))
    for i in range(n):
        t = (i + 0.5) / n * per
        if t < w:              x, y = cx - w / 2 + t,          cy - d / 2
        elif t < w + d:        x, y = cx + w / 2,              cy - d / 2 + (t - w)
        elif t < 2 * w + d:    x, y = cx + w / 2 - (t - w - d), cy + d / 2
        else:                  x, y = cx - w / 2,              cy + d / 2 - (t - 2 * w - d)
        # إن كان الطرف خارج المدينة (بعيد جدًا)، نتخطّاه
        add(x, y, z + 3.4, 17.0, WARM)

# ---------- 2) مشاعل الأسوار (تتبع محيط حلقة السور على مصطبتها) ----------
for (lv, hh, th) in WALL_RINGS:
    z, (cx, cy), (w, d), _mat = min(TERRACES, key=lambda t: abs(t[0] - lv))
    w2, d2 = w / 2 + 1.2, d / 2 + 1.2          # على الوجه الخارجي للسور
    per = 2 * (w2 + d2)
    n = max(8, int(per / 26.0))
    for i in range(n):
        t = (i + 0.5) / n * per
        if t < 2 * w2:              x, y = cx - w2 + t,          cy - d2
        elif t < 2 * w2 + 2 * d2:   x, y = cx + w2,              cy - d2 + (t - 2 * w2)
        else:                       x, y = cx + w2 - (t - 2 * w2 - 2 * d2), cy + d2
        add(x, y, z + hh + 1.6, 20.0, TORCH, "torch")

# ---------- 3) البوابة البحرية + الجسر + المنارة ----------
for i in range(8):                       # مناقل على طول الجسر
    add(196.0 - i * 22.0, -256.0, 19.0, 24.0, FIRE, "brazier")
add(198.0, -232.0, 42.0, 26.0, FIRE, "brazier")        # برجا البوابة البحرية
add(198.0, -280.0, 42.0, 26.0, FIRE, "brazier")
add(246.0, -184.0, 41.0, 34.0, BEAC, "beacon")          # المنارة

# ---------- 4) نوافذ القصر المضيئة (نوع window) ----------
WINDOWS = [
    (0, -60, 112), (0, -42, 112), (26, -60, 112), (-26, -60, 112),
    (30, -6, 130), (52, -6, 130), (74, -6, 130), (8, -6, 130),
    (0, -40, 146), (0, -80, 146),
    (62, -8, 116), (-62, -8, 116),
    (10, -20, 96), (-10, -20, 96), (40, -40, 96), (-40, -40, 96),
    (70, -60, 80), (-70, -60, 80),
]
for (x, y, z) in WINDOWS:
    add(x, y, z, 15.0, [1.00, 0.70, 0.38], "window")

# ---------- 5) مصابيح إضافية مما أعلنه config.lua ----------
try:
    cfg = open("mta/config.lua").read()
    for m in re.finditer(r"\{ x = (-?\d+),\s*y = (-?\d+),\s*z = (\d+),\s*kind = \"(\w+)\",\s*radius = (\d+),\s*color = \{(\d+),\s*(\d+),\s*(\d+)\}", cfg):
        x, y, z, kind, rad, r0, g0, b0 = m.groups()
        add(float(x), float(y), float(z), float(rad),
            [int(r0) / 255, int(g0) / 255, int(b0) / 255], kind)
except Exception as e:  # noqa
    print("تحذير: تعذّرت قراءة config.lua —", e)

# ---------- كتابة ----------
out = "mta/data"
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, "lamps.json"), "w") as f:
    json.dump(lamps, f, ensure_ascii=False, separators=(",", ":"))

kinds = {}
for L in lamps:
    kinds[L["t"]] = kinds.get(L["t"], 0) + 1
print(f"✓ {len(lamps)} مصدر ضوء → mta/data/lamps.json")
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print(f"    {k:8s} {v}")
