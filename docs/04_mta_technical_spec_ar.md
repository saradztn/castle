# المواصفات التقنية — MTA:SA
### Castle & Palace (مدينة القلعة الساحلية) — البنية، الملفات، الإضاءة، والأداء

---

## 1. بنية المشروع (مطابقة للوحة التقنية في المرجع)

```
Castle_MTA/
├── meta.xml
├── client.lua
├── README.txt
├── models/
│   ├── castle.dff          ← 30 موديل: تُدمج في مجموعة DFF أو تُقسَّم حسب المنطقة
│   ├── castle.txd          ← كل الخامات مضغوطة داخل TXD واحد أو عدة TXD حسب الحجم
│   └── castle.col          ← ملف التصادم
├── textures/
│   └── src/                ← خاماتك المصدرية 4K (تُحوَّل داخل TXD)
└── lod/
    ├── high/
    ├── medium/
    ├── low/
    └── distant/
```

### توزيع الـ30 موديلًا على المناطق
| # | المنطقة | الموديلات |
|---|---|---|
| 1 | القصر/الكاتدرائية (القمة) | 6 (كتلة القصر، البرج المركزي، الأبراج الثانوية، الدعامات الطائرة، الواجهة والنوافذ، الدرج الاحتفالي) |
| 2 | الحلقة العليا والساحة | 4 (السور، الأبراج المستديرة، بيت البوابة، الساحة والنافورة) |
| 3 | الحلقة الوسطى + كنيسة المدينة | 4 |
| 4 | المصاطب الست + بيوت المدينة | 8 (3 كتل مصاطب + 5 تنويعات بيوت + الجسور المعقودة) |
| 5 | الحلقة السفلى + البوابة البحرية | 5 |
| 6 | المرفأ + السفن + الرافعة | 4 |
| 7 | الجسر السباعي + بوابة الجسر + المنارة | 3 |
| 8 | الشلالات + الجرف + القناة | 3 |

> ملاحظة أداء: الاستخدام في MTA يعتمد `engineLoadDFF/TXD/COL` عبر `engineLoadDFF`–`engineLoadTXD`–`engineLoadCOL` ثم `engineReplaceModel` (أو `createObject` مع `engineApplyShaderToWorldTexture`)، والأفضل تحميل الأقسام حسب موقع اللاعب (Streaming) لا تحميل المدينة كلها مرة واحدة.

---

## 2. مثال `meta.xml` (جاهز)

```xml
<meta>
    <info author="YourName" name="Castle &amp; Palace" version="1.0" type="script" description="Coastal castle-city with full interiors and day/night lighting"/>
    <file src="models/castle.dff"/>
    <file src="models/castle.txd"/>
    <file src="models/castle.col"/>
    <file src="lod/high/part_01.dff"/>
    <file src="lod/medium/part_01.dff"/>
    <file src="lod/low/part_01.dff"/>
    <file src="lod/distant/part_01.dff"/>
    <file src="client.lua" type="client"/>
</meta>
```

## 3. مثال `client.lua` — نظام النهار/الليل (مطابق للمرجع ومصحّح)

> الملاحظة المهمة: الكود في المرجع كان فيه خلط (`setTime` مع عنصر `root` وبلا اكتمال للدالة). هذا هو الكود الكامل والصحيح:

```lua
--- الإعدادات
local modelIDs = { 1337, 1338, 1339 }  -- معرّفات الموديلات المستبدلة
local dayTime, nightTime = 12, 0        -- ساعة النهار، ساعة الليل

--- تحميل الموديلات (التصادم + DFF + TXD)
local function loadCastle()
    local txd = engineLoadTXD("models/castle.txd", true)
    engineImportTXD(txd, modelIDs[1])
    local dff = engineLoadDFF("models/castle.dff")
    engineReplaceModel(dff, modelIDs[1])
    local col = engineLoadCOL("models/castle.col")
    engineReplaceCOL(col, modelIDs[1])
    engineSetModelLODDistance(modelIDs[1], 800)   -- مسافة ظهور LOD
end

--- إضاءة القصر: نهار/ليل (المشاعل والنوافذ المضيئة)
local castleLights = {}   -- { element = element, shader = shader }

local function setCastleLighting(mode)
    if mode == "day" then
        setTime(dayTime, 0)
        for _, l in ipairs(castleLights) do
            setElementData(l.element, "castle.light.on", false)
            if l.shader then engineRemoveShaderFromWorldTexture(l.shader, "*") end
        end
    else
        setTime(nightTime, 0)
        for _, l in ipairs(castleLights) do
            setElementData(l.element, "castle.light.on", true)   -- يشغّل نقطة الإضاءة/الـshader
        end
        -- تشغيل إضاءة النوافذ الليلية
        local shader = dxCreateShader("shaders/window_emissive.fx")
        if shader then
            engineApplyShaderToWorldTexture(shader, "glass_leaded_pane_emissive")
            table.insert(castleLights, { element = root, shader = shader })
        end
    end
    setElementData(root, "castle.lighting", mode)   -- للمزامنة مع كل اللاعبين
end

--- الأحداث
addEvent("setCastleLighting", true)
addEventHandler("setCastleLighting", root, function(mode)
    setCastleLighting(mode)
end)

--- مزامنة الحالة عند دخول اللاعب
addEventHandler("onClientResourceStart", resourceRoot, function()
    loadCastle()
    local mode = getElementData(root, "castle.lighting") or "day"
    setCastleLighting(mode)
end)

--- تبديل تلقائي حسب وقت اللعبة
setTimer(function()
    local hour = getTime()
    if hour >= 7 and hour < 19 then
        if getElementData(root, "castle.lighting") ~= "day" then setCastleLighting("day") end
    else
        if getElementData(root, "castle.lighting") ~= "night" then setCastleLighting("night") end
    end
end, 30000, 0)
```

**الشيدر المطلوب (`shaders/window_emissive.fx`)** — بسيط: يُضاعف لون الألبيو للنسيج `glass_leaded_pane_emissive` كإضاءة ذاتية عند الليل (Additive/Unlit pass) مع تعطيله نهارًا.

---

## 4. الأداء ومستويات LOD

| المستوى | المدى | ما يُحمَّل | ميزانية تقريبية |
|---|---|---|---|
| High | 0–120 م | كل التفاصيل، الخامات 2K، الداخليات، الأدراج، الأبواب | ≤ 700k مثلث للمشهد كامل |
| Medium | 120–350 م | بلا زخارف دقيقة، الخامات 1K، دمج البيوت الصغيرة | ≤ 220k |
| Low | 350–800 م | كتل وأسقف فقط، خامات 512 | ≤ 70k |
| Distant | +800 م | صومعة المدينة والقمة فقط، خامات 256 | ≤ 12k |

**قواعد إجبارية:**
1. `engineSetModelLODDistance` لكل قسم + `setLowLODElement` للربط بين المستويات.
2. تحميل الأقسام عند الحاجة (Streaming) لا تحميل المدينة كلها في البداية.
3. **Occlusion/Portal**: لا تُحمَّل داخليات المنازل إلا عند الاقتراب (Interiors كـ`createObject` تُنشأ عند الطلب أو كأبعاد منفصلة `dimension`).
4. دمج الخامات في **أقل عدد TXD ممكن** (تجميع حسب المنطقة) لتقليل الـdraw calls.
5. `engineSetModelPhysicalRadius` و`setElementStreamable(false)` للعناصر الصغيرة كي لا تُحذف أثناء اللعب.
6. COLL: صناديق (Box) ومسطّحات بسيطة قدر الإمكان، ويفضّل `COL` منفصل لكل قسم كبير بدلًا من COL هائل واحد.

---

## 5. خطة التنفيذ بعد وصول الخامات

| المرحلة | المخرج |
|---|---|
| 1. تحليل وقياس | شبكة قياس من المرجع (الصخرة، المصاطب، الأسوار، القمة) + مخطط كتل أولي |
| 2. بلوك-أوت | مجسّم كتل بلا تفاصيل (Silhouette match أولًا) — مطابقة الظل قبل أي تفصيل |
| 3. تفصيل خارجي | القصر/الكتدرائية، الأسوار الثلاثة، البوابات، المدينة والمصاطب، المرفأ، الجسر، الشلالات |
| 4. داخلية | 14 داخلية المرجع (بوابة، ساحة، ممر، غرفة ملك، مكتبة، سجون، قاعة طعام، مطبخ، أسلحة، ضيوف، حدائق، أبراج، ممرات سرية، أقبية) |
| 5. UV + خامات | UV يدوية + خاماتك + decals (طحالب/ملح/تسربات/سخام) |
| 6. LOD | 4 مستويات + ربط + قياس أداء |
| 7. الإضاءة | نظام نهار/ليل + مشاعل + نوافذ مضيئة + شيدر |
| 8. المقارنة البصرية | 11 نقطة مقابل المرجع + تعديل أي انحراف خارجي |
