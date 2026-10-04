--[[
    client/pointlights.lua — ★ قلب نظام الإضاءة القوي
    يُطبّق شيدر pointlight.fx على خامات الموديل فيمنح **حتى 32 مصدر ضوء حقيقي**
    تُحسب لكل بكسل (Lambert نصف ناعم + انحلال مزدوج + ارتعاش لهب + نبض منارة).

    لماذا شيدر بدل createLight؟
      • MTA تحدّد الأضواء الحقيقية (createLight) بـ8 فقط في المشهد كله.
      • الشيدر لا حدّ له عمليًا: 275 مصدر ضوء مُستخرجًا من هندسة المدينة
        (191 فانوس شارع، 49 مشعل سور، 22 نافذة قصر، 12 منقل، منارة) نمرّر
        منها أقرب 32 مصدرًا للمشهد المطلوب ونتدرّج بالمسافة.
      • المشاعل ترتعش والمنارة تنبض زمنيًا — حياة حقيقية في المدينة ليلًا.

    متغيّرات عامة (تُقرأ من موارد أخرى):
      castle:lighting  = "day" | "night" | "auto"   (تُضبط من lighting.lua)
      castle:lampBoost = 0.0 … 3.0                  (شدّة إضافية اختيارية)
]]

local SHADER, GLOW                       -- شيدر الإضاءة + شيدر الهالة
local GLOW_TEX
local LAMPS = {}                         -- كل المصابيح (من mta/data/lamps.json)
local lampsLoaded = false

local posBuf, colBuf, parBuf = {}, {}, {}
local lastUpdate = 0
local CUR_MODE = "auto"

-- ================= أدوات =================
local function loadJSON(path)
    local f = fileExists(path) and fileOpen(path)
    if not f then
        outputDebugString("[CASTLE] تعذّر قراءة " .. tostring(path), 2)
        return {}
    end
    local raw = fileRead(f, fileGetSize(f))
    fileClose(f)
    return fromJSON(raw) or {}
end

-- ================= تحميل المصابيح =================
local function loadLamps()
    local raw = loadJSON("data/lamps.json")
    for _, L in ipairs(raw) do
        LAMPS[#LAMPS + 1] = {
            x = L.x + (CASTLE.origin and CASTLE.origin[1] or 0),
            y = L.y + (CASTLE.origin and CASTLE.origin[2] or 0),
            z = L.z + (CASTLE.origin and CASTLE.origin[3] or 0),
            r = L.r, c = L.c, t = L.t,
        }
    end
    lampsLoaded = #LAMPS > 0
    outputDebugString(("[CASTLE] نظام الإضاءة: %d مصدر ضوء مُحمّل"):format(#LAMPS), 3)
end

-- ================= الشيدرات =================
local MAT_PATTERNS = {
    "mat_*", "stone_*", "rock_*", "roof_*", "plaster_*", "wood_*", "terrain_*",
    "metal_*", "marble_*", "fabric_*", "glass_*", "water_*", "cobble*", "dirt*",
    "sandstone*", "granite*", "slate*", "shingle*", "terracotta*", "quay*",
}

local function initShaders()
    SHADER = dxCreateShader("shaders/pointlight.fx", 0, 0, true, "all")
    if not SHADER then
        outputDebugString("[CASTLE] فشل تحميل shaders/pointlight.fx — شغّل debugscript 3", 1)
    else
        -- نطبّقه على كل خامات الموديل والمدينة
        for _, pat in ipairs(MAT_PATTERNS) do
            engineApplyShaderToWorldTexture(SHADER, pat)
        end
        dxSetShaderValue(SHADER, "gAmbient", { 0.44, 0.46, 0.52 })
        dxSetShaderValue(SHADER, "gLightCount", 0)
        dxSetShaderValue(SHADER, "gTime", 0.0)
    end

    GLOW_TEX = dxCreateTexture("assets/glow.png", "argb", true, "clamp")
    if GLOW_TEX and dxCreateShader then
        GLOW = dxCreateShader("shaders/glow.fx")
        if GLOW then
            dxSetShaderValue(GLOW, "gTexture", GLOW_TEX)
            dxSetShaderValue(GLOW, "gFalloff", 1.0)
        end
    end
end

-- ================= أقرب N مصابيح =================
local function nearestLamps(px, py, pz, want)
    local list, n = {}, 0
    for i = 1, #LAMPS do
        local L = LAMPS[i]
        local dx, dy, dz = L.x - px, L.y - py, L.z - pz
        local d2 = dx * dx + dy * dy + dz * dz
        local reach = (L.r + 30.0)
        if d2 < reach * reach then
            n = n + 1
            list[n] = { d2 = d2, L = L }
        end
    end
    table.sort(list, function(a, b) return a.d2 < b.d2 end)
    local out = {}
    for i = 1, math.min(want, #list) do out[i] = list[i].L end
    return out
end

-- ================= تمرير بيانات الإضاءة للشيدر =================
local MAXL = 32
local function updatePointLights()
    if not SHADER or not lampsLoaded then return end

    local px, py, pz = getCameraMatrix()
    local night = (CUR_MODE == "night")
    local boost = tonumber(getElementData(resourceRoot, "castle:lampBoost")) or 1.0
    local near = nearestLamps(px, py, pz, MAXL)
    local t = getTickCount() / 1000.0

    for i = 1, MAXL do
        local i4, i3, i2 = (i - 1) * 4, (i - 1) * 3, (i - 1) * 2
        local L = near[i]
        if L then
            local k = night and 1.0 or 0.22          -- نهارًا تبقى لمعة خفيفة جدًا
            posBuf[i4 + 1], posBuf[i4 + 2], posBuf[i4 + 3], posBuf[i4 + 4] =
                L.x, L.y, L.z, L.r
            colBuf[i3 + 1], colBuf[i3 + 2], colBuf[i3 + 3] =
                (L.c[1] or 1) * k * boost, (L.c[2] or 0.7) * k * boost, (L.c[3] or 0.4) * k * boost
            parBuf[i2 + 1] = (L.t == "beacon") and 2.0 or 1.0
            parBuf[i2 + 2] = 1.0
        else
            posBuf[i4 + 1], posBuf[i4 + 2], posBuf[i4 + 3], posBuf[i4 + 4] = 0, -9999, 0, 0
            colBuf[i3 + 1], colBuf[i3 + 2], colBuf[i3 + 3] = 0, 0, 0
            parBuf[i2 + 1], parBuf[i2 + 2] = 0, 0
        end
    end

    dxSetShaderValue(SHADER, "gLightPos", posBuf)
    dxSetShaderValue(SHADER, "gLightColor", colBuf)
    dxSetShaderValue(SHADER, "gLightParams", parBuf)
    dxSetShaderValue(SHADER, "gLightCount", #near)
    dxSetShaderValue(SHADER, "gTime", t)
    dxSetShaderValue(SHADER, "gAmbient", night and { 0.055, 0.070, 0.140 } or { 0.440, 0.460, 0.520 })
end

-- ================= هالات مرئية لكل مصباح (حتى 275) =================
local GLOW_RANGE = 420.0
local function drawGlows()
    if not GLOW then return end
    local px, py, pz = getCameraMatrix()
    local t = getTickCount() / 1000.0
    for i = 1, #LAMPS do
        local L = LAMPS[i]
        local dx, dy, dz = L.x - px, L.y - py, L.z - pz
        if dx * dx + dy * dy + dz * dz < GLOW_RANGE * GLOW_RANGE then
            -- مشاعل ومناقل ترتعش أسرع من الفوانيس
            local spd = (L.t == "torch" or L.t == "brazier") and 9.0 or 3.0
            local flick = 0.80 + 0.20 * math.sin(t * spd + i * 2.1)
            local s = math.max(1.1, L.r / 28.0) * flick
            local cr, cg, cb = (L.c[1] or 1) * 255, (L.c[2] or .7) * 255, (L.c[3] or .4) * 255
            dxSetShaderValue(GLOW, "gColor", { L.c[1] or 1, L.c[2] or .7, L.c[3] or .4, 0.85 * flick })
            dxDrawMaterialLine3D(L.x, L.y, L.z + s, L.x, L.y, L.z - s, GLOW, s * 2.2,
                px, py, pz, false, tocolor(cr, cg, cb, 255))
        end
    end
end

-- ================= الحلقة =================
addEventHandler("onClientResourceStart", resourceRoot, function()
    loadLamps()
    initShaders()
    CUR_MODE = getElementData(root, "castle:lighting") or "auto"
    addEventHandler("onClientPreRender", root, function()
        local m = getElementData(root, "castle:lighting") or "auto"
        if m == "auto" then
            local h = getTime()
            m = (h >= (CASTLE.nightStart or 19) or h < (CASTLE.dayStart or 7)) and "night" or "day"
        end
        CUR_MODE = m
        if getTickCount() - lastUpdate > 100 then
            lastUpdate = getTickCount()
            updatePointLights()
        end
        drawGlows()
    end)
    outputDebugString("[CASTLE] pointlights.lua جاهز — إضاءة نقطية بالشيدر (حتى 32 مصدرًا)", 3)
end)

-- ================= واجهة =================
function setCastleLampBoost(v)
    setElementData(resourceRoot, "castle:lampBoost", math.max(0.0, math.min(3.0, tonumber(v) or 1.0)))
end

function getCastleLampCount()
    return #LAMPS
end
