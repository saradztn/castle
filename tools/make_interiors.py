#!/usr/bin/env python3
"""
make_interiors.py — يبني mta/data/interiors.json من طاولة الداخليات في المولّد:
  • موضع الباب الخارجي في المدينة (من مصاطب المدينة الفعلية).
  • موضع الولادة الداخلي = شبكة الداخليات عند الإزاحة (0, 6000, 0) كما بناها build_city.py.
يُستهلك من mta/client/interior.lua ومِن server/main.lua.
"""
import importlib.util, json, os, sys

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HOME)

spec = importlib.util.spec_from_file_location("bc", os.path.join(HOME, "tools", "build_city.py"))
bc = importlib.util.module_from_spec(spec)
sys.modules["bc"] = bc
spec.loader.exec_module(bc)                      # لا يُشغّل البناء (محمي بـ __main__)

# أبواب خارجية واقعية موزّعة على المدينة (من TERRACES الفعلية)
DOORS = {
    "main_gatehouse":    (95.0, -112.0, 15.0),    # البوابة المحصّنة عند شاطئ الجزيرة
    "inner_courtyard":   (30.0, -6.0, 98.0),      # الساحة العليا
    "state_corridor":    (62.0, -40.0, 70.0),     # المدينة العليا
    "kings_bedchamber":  (0.0, 0.0, 112.0),       # القصر
    "great_library":     (52.0, -22.0, 84.0),     # الساحة العليا
    "dungeons":          (-180.0, -230.0, 26.0),  # تحت السور السفلي
    "great_dining_hall": (46.0, -52.0, 42.0),     # المدينة السفلى
    "kitchens":          (58.0, -50.0, 56.0),     # المدينة الوسطى
    "armoury":           (20.0, -38.0, 22.0),     # المصطبة الصخرية
    "guest_chamber":     (30.0, -46.0, 30.0),
    "royal_gardens":     (92.0, -6.0, 98.0),      # الحدائق الملكية
    "tower_interior":    (70.0, -6.0, 112.0),     # البرج الغربي
    "secret_passages":   (-10.0, -2.0, -2.0),     # داخل الصخر
    "vaults_cellars":    (-24.0, 10.0, -30.0),    # الأقبية السفلى
}

rooms = []
for i, (name, w, d, fl, wl, props) in enumerate(bc.INTERIORS):
    ix = 0.0 + (i % 2) * 120.0
    iy = 6000.0 + (i // 2) * 120.0
    dx, dy, dz = DOORS.get(name, (30.0, -46.0, 30.0))
    rooms.append({
        "id": name, "name": name,
        "w": w, "d": d,
        "x": dx, "y": dy, "z": dz,                 # الباب الخارجي
        "ix": ix, "iy": iy, "iz": 2.0,             # موضع الولادة داخل الغرفة
        "props": list(props),
    })

os.makedirs("mta/data", exist_ok=True)
with open("mta/data/interiors.json", "w") as f:
    json.dump(rooms, f, ensure_ascii=False, indent=1)

print(f"✓ {len(rooms)} داخلية → mta/data/interiors.json")
for r in rooms[:4]:
    print(f"    {r['id']:20s} باب=({r['x']},{r['y']},{r['z']})  داخل=({r['ix']},{r['iy']})")
print("    …")
