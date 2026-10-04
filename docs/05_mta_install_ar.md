# دليل التركيب والتشغيل — Castle & Palace (MTA:SA)

> حزمة الموارد جاهزة في مجلد **`mta/`**، والهندسة بصيغة **OBJ** جاهزة في `mta/models/parts/`.
> المتبقي هو تحويل OBJ → **DFF** وبناء **TXD** (خطوتان مؤتمتتان بأدوات مجانية، مشروحتان أدناه).

---

## 1. بنية موارد MTA (جاهزة)

```
mta/
├── meta.xml                      ✅
├── config.lua                    ✅ (الأضواء، LOD، الفكسات، الداخليات)
├── assets/                       ✅ glow.png · foam.png · smoke.png · flag.png
├── models/
│   ├── castle.dff / .txd / .col   ⬜ يُبنى من OBJ (خطوة 2)
│   ├── parts/                    ✅ 6 ملفات OBJ (palace, walls, town, harbour, causeway, cliff)
│   └── lod/                      ✅ 18 ملف OBJ (3 مستويات × 6 أجزاء)
├── shaders/                      ✅ window_emissive · ocean · terrain_detail · night_grade
├── client/                       ✅ main · lighting · lights · fx · shaders · interior · camera
└── server/                       ✅ main.lua
```

**التركيب:** انسخ مجلد `mta/` إلى `MTA San Andreas/server/mods/deathmatch/resources/` باسم `castle`، ثم `/start castle`.

---

## 2. تحويل OBJ → DFF (خطوة واحدة، مجانية)

1. نزّل **Blender** (مجاني) + إضافة **"MTA:SA DFF Exporter"** أو استخدم **GIMS Evo** مع 3ds Max.
2. في Blender: `File → Import → Wavefront (.obj)` واختر `mta/models/parts/palace.obj` (ثم بقية الأجزاء).
3. تأكد أن:
   - المقياس **1 وحدة = 1 متر** (لا تُكبّر).
   - `Shading → Smooth` على الأجزاء المنحنية، و`Flat` على الجدران.
   - كل خامة من خاماتك مربوطة بملف `textures/src/<id>_albedo.png`.
4. صدّر: `File → Export → RenderWare DFF (.dff)` — النتيجة: `palace.dff`.
5. **COL**: صدّر نسخة مبسّطة (بلا زخارف) عبر `Export → COL` لنفس الأجزاء → `palace.col`.
6. **LOD**: كرّر مع ملفات `mta/models/lod/*_medium.obj` → `palace_medium.dff` … إلخ.

> إن أردت الأسهل: ادمج الأجزاء الستة في DFF واحد (`castle.dff`) و COL واحد، واترك LOD منفصلة.

---

## 3. بناء TXD (الخامات)

1. نزّل **Magic.TXD** (مجاني) أو **TXD Workshop**.
2. أنشئ TXD جديدًا، وأضف الخامات بالأسماء **نفسها** المستخدمة في الموديل:
   `stone_sandstone_ashlar`, `roof_slate`, `plaster_lime_town`, `terrain_grass`, `water_ocean` … (39 اسمًا).
3. المقاسات المقترحة لكل خامة:
   | الاستخدام | المقاس |
   |---|---|
   | High LOD (قريب ≤320 م) | 2048×2048 |
   | Medium LOD | 1024×1024 |
   | Low LOD | 512×512 |
   | Distant LOD | 256×256 |
4. الضغط: **DXT1** للألوان (بلا شفافية)، **DXT5** لِما فيه alpha.
5. احفظ: `castle.txd`.

**سكربت جاهز لتوليد كل المقاسات تلقائيًا:**
```bash
python3 tools/make_txd_sets.py --src textures/src --out build/txd --sets 2048,1024,512,256
```

---

## 4. كود MTA — ما تفعله كل قطعة

| الملف | الوظيفة |
|---|---|
| `client/main.lua` | تحميل الأجزاء + تخصيص معرّفات الموديلات (`engineRequestModel`) + ربط LOD + تتبّع نسبة التحميل |
| `client/lighting.lua` | **`setCastleLighting("day"/"night")`** — يُغيّر الوقت والسماء والماء والضباب ويشغّل شيدر النوافذ (مطابق لدالة لوحة المشروع، لكن مصحّحة وكاملة) |
| `client/lights.lua` | مدير أضواء ذكي: MTA تحدّ الأضواء الحقيقية بـ8، فنُنشئ فقط **أقرب 7 مصادر** ونُعيد تدويرها كل 0.9 ث، مع **هالة (corona)** تُرسم لكل مصدر لتظهر 120 مصدرًا بصريًا |
| `client/fx.lua` | **فكسات**: شلالان (waterfall + waterfallsmoke + waterfalldrops)، رشّاش، دخان مداخن ومشاعل، نار المناقل، 26 طائرًا، 40 بقعة رغوة بحر |
| `client/shaders.lua` | تشغيل الشيدرات الأربعة + دَرْج ليلي كـPost-Processing (`dxCreateScreenSource`) |
| `client/interior.lua` | 14 داخلية: مدخل خارجي في المدينة + توصيل بعيد + تعتيم انتقالي |
| `client/camera.lua` | جولة سينمائية 6 لقطات (`/castlecinema`) |
| `server/main.lua` | مزامنة الوضع، مستوى البحر، الطقس، أوامر `/castlemode` `/castletp` |

### الشيدرات
| الشيدر | التأثير |
|---|---|
| `window_emissive.fx` | نوافذ تتوهّج ليلًا بلون دافئ (شدّة قابلة للتحكّم من Lua) |
| `ocean.fx` | بحر بموجات ضجيج متراكبة + لمعة شمس + رغوة على القمم |
| `terrain_detail.fx` | بلاطة ماكرو تُخفي تكرار الخامات + طحالب في المنخفضات + حبيبات دقيقة |
| `night_grade.fx` | تباين + تلوين بارد للظلال ودافئ للإضاءات + تعتيم حواف (Look فيلم) |

### الأوامر
```
/castlemode day | night      تبديل الوضع (يحتاج صلاحية)
/castlecinema                جولة سينمائية
/castletp gate|harbour|keep|gardens|causeway|waterfall
```

---

## 5. الأداء (مهم لمدينة بهذا الحجم)

1. **LOD**: كل جزء عالي مربوط ببدائله؛ المسافات في `config.lua → lod`.
2. **الأضواء**: لا تزد `maxLights` عن 7 (حد MTA).
3. **الشيدرات**: `night_grade` يعمل ليلًا فقط؛ التضاريس تعمل على 4 خامات فقط.
4. **الخامات**: 256px للمستوى البعيد، وتُبنى TXD منفصلة لكل LOD إن أردت.
5. **الداخليات**: تُبنى في منطقة بعيدة (`interiorOffset`) فلا تُحمَّل إلا عند الدخول.
6. **`setFarClipDistance`**: 4200 نهارًا / 2600 ليلًا (يقلّل الحمل الليلي).

---

## 6. قائمة تحقّق نهائية

- [ ] OBJ → DFF لكل الأجزاء الستة + COL
- [ ] LOD → DFF للمستويات الثلاثة
- [ ] TXD مبنية بالـ39 خامة بالأسماء الصحيحة
- [ ] `/start castle` بلا أخطاء في الكونسول
- [ ] `/castlemode night` → النوافذ تضيء والهالات تظهر
- [ ] `/castlecinema` → الجولة تعمل
- [ ] قياس FPS في الكاميرا البطهورية
