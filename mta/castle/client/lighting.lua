--[[
    lighting.lua — نظام الإضاءة القوي (نهار/ليل + إضاءة نقطية بمصابيح حقيقية)
    Castle & Palace — مدينة القلعة الساحلية

    الآلية:
      1) دورة نهار/ليل: setTime + setSunColor + setSkyGradient + setWaterColor + الضباب.
      2) إضاءة نقطية حقيقية: شيدر shaders/pointlight.fx على خامات الموديل،
         وتُمرَّر إليه أقرب 32 مصدر ضوء (من data/lamps.json) كل 120ms.
      3) هالات مرئية: shaders/glow.fx عبر dxDrawMaterialLine3D مع ارتعاش لهب.
]]

local LAMPS = {}          -- إحداثيات عالمية
local SHADER_LIGHT, SHADER_GLOW, GLOW_TEX
local lastUpdate = 0
local posBuf, colBuf, parBuf = {}, {}, {}

-- ======== قراءة JSON ========
local function loadJSON(path)
    local f = fileOpen(path)
    if not f then
        outputDebugString("[CASTLE] لا يمكن قراءة " .. path, 1)
        return {}
    end
    local data = fromJSON(fileRead(f, fileGetSize(f))) or {}
    fileClose(f)
    return data
end

-- ======== الشيدرات ========
local function initShaders()
    SHADER_LIGHT = dxCreateShader("shaders/pointlight.fx")
    if not SHADER_LIGHT then
        outputDebugString("[CASTLE] فشل تحميل شيدر الإضاءة (شغّل debugscript 3)", 1)
    else
        dxSetShaderValue(SHADER_LIGHT, "gAmbient", { 0.42, 0.44, 0.50 })
        -- نطبّق الإضاءة على كل خامات الموديل وخامات المدينة
        for _, pat in ipairs({ "mat_*", "stone_*", "roof_*", "plaster_*", "wood_*",
                               "rock_*", "terrain_*", "metal_*", "fabric_*", "marble_*" }) do
            engineApplyShaderToWorldTexture(SHADER_LIGHT, pat)
        end
    end

    SHADER_GLOW = dxCreateShader("shaders/glow.fx")
    GLOW_TEX = dxCreateTexture("textures/glass_leaded_pane_emissive_albedo.png", "argb", true, "clamp")
    if SHADER_GLOW and GLOW_TEX then
        dxSetShaderValue(SHADER_GLOW, "gTexture", GLOW_TEX)
        dxSetShaderValue(SHADER_GLOW, "gFalloff", 1.0)
    end
end

-- ======== نهار / ليل ========
local function isNight(h) return h >= CASTLE.TIME.nightStartHour or h < CASTLE.TIME.dayStartHour end

function applyDayLighting()
    setTime(CASTLE.TIME.dayTime[1], CASTLE.TIME.dayTime[2])
    setMinuteDuration(CASTLE.TIME.minuteDuration)
    setSunColor(255, 232, 198, 255)
    setSkyGradient(88, 148, 232, 232, 208, 168)
    setWaterColor(22, 86, 100, 210)
    setFogDistance(CASTLE.LIGHT.dayFogDistance)
    setFarClipDistance(CASTLE.LOD.farclip)
    setSunSize(3)
    if SHADER_LIGHT then dxSetShaderValue(SHADER_LIGHT, "gAmbient", { 0.44, 0.46, 0.52 }) end
end

function applyNightLighting()
    setTime(CASTLE.TIME.nightTime[1], CASTLE.TIME.nightTime[2])
    setMinuteDuration(CASTLE.TIME.minuteDuration)
    setSunColor(38, 58, 118, 255)
    setSkyGradient(4, 8, 26, 14, 20, 50)
    setWaterColor(7, 24, 42, 225)
    setFogDistance(CASTLE.LIGHT.nightFogDistance)
    setFarClipDistance(CASTLE.LOD.farclip)
    setMoonSize(4)
    if SHADER_LIGHT then dxSetShaderValue(SHADER_LIGHT, "gAmbient", { 0.050, 0.065, 0.135 }) end
end

-- ======== أقرب المصابيح ========
local function nearest(px, py, pz, want)
    local list = {}
    for i = 1, #LAMPS do
        local L = LAMPS[i]
        local dx, dy, dz = L.x - px, L.y - py, L.z - pz
        local d2 = dx * dx + dy * dy + dz * dz
        if d2 < (L.r * 1.5) ^ 2 then
            list[#list + 1] = { d2 = d2, L = L }
        end
    end
    table.sort(list, function(a, b) return a.d2 < b.d2 end)
    local out = {}
    for i = 1, math.min(want, #list) do out[i] = list[i].L end
    return out
end

-- ======== تمرير بيانات الإضاءة ========
local function updatePointLights()
    if not SHADER_LIGHT then return end
    local px, py, pz = getElementPosition(localPlayer)
    local near = nearest(px, py, pz, CASTLE.LIGHT.maxLights)
    local t = getTickCount() / 1000

    for i = 1, CASTLE.LIGHT.maxLights do
        local L = near[i]
        local i4, i3, i2 = (i - 1) * 4, (i - 1) * 3, (i - 1) * 2
        if L then
            posBuf[i4 + 1], posBuf[i4 + 2], posBuf[i4 + 3], posBuf[i4 + 4] = L.x, L.y, L.z, L.r
            colBuf[i3 + 1], colBuf[i3 + 2], colBuf[i3 + 3] = L.c[1], L.c[2], L.c[3]
            parBuf[i2 + 1] = (L.t == "beacon") and 2.0 or 1.0
            parBuf[i2 + 2] = 1.0
        else
            posBuf[i4 + 1], posBuf[i4 + 2], posBuf[i4 + 3], posBuf[i4 + 4] = 0, -9999, 0, 0
            colBuf[i3 + 1], colBuf[i3 + 2], colBuf[i3 + 3] = 0, 0, 0
            parBuf[i2 + 1], parBuf[i2 + 2] = 0, 0
        end
    end
    dxSetShaderValue(SHADER_LIGHT, "gLightPos", posBuf)
    dxSetShaderValue(SHADER_LIGHT, "gLightColor", colBuf)
    dxSetShaderValue(SHADER_LIGHT, "gLightParams", parBuf)
    dxSetShaderValue(SHADER_LIGHT, "gLightCount", #near)
    dxSetShaderValue(SHADER_LIGHT, "gTime", t)
end

-- ======== الهالات المرئية ========
local function drawGlows()
    if not SHADER_GLOW then return end
    local px, py, pz = getElementPosition(localPlayer)
    local rng = CASTLE.LIGHT.glowRange
    for i = 1, #LAMPS do
        local L = LAMPS[i]
        if getDistanceBetweenPoints3D(px, py, pz, L.x, L.y, L.z) < rng then
            local flick = 0.82 + 0.18 * math.sin(getTickCount() / 65 + i * 2.1)
            local s = math.max(1.2, L.r / 30) * flick
            dxSetShaderValue(SHADER_GLOW, "gColor", { L.c[1], L.c[2], L.c[3], 0.80 * flick })
            dxDrawMaterialLine3D(L.x, L.y, L.z + s, L.x, L.y, L.z - s,
                SHADER_GLOW, s * 2, L.x + 1, L.y + 1, L.z, false, tocolor(255, 255, 255, 255))
        end
    end
end

-- ======== الحلقة الرئيسية ========
local function mainLoop()
    local mode = getElementData(root, "castle:lighting") or "auto"
    local night = (mode == "night") or (mode == "auto" and isNight(getTime()))
    local state = night and "night" or "day"
    if CASTLE.lightState ~= state then
        CASTLE.lightState = state
        if night then applyNightLighting() else applyDayLighting() end
        triggerEvent("castle:onLightingChanged", resourceRoot, state)
    end
    if getTickCount() - lastUpdate > CASTLE.LIGHT.updateRateMs then
        lastUpdate = getTickCount()
        updatePointLights()
    end
    drawGlows()
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    local raw = loadJSON("data/lamps.json")
    for _, L in ipairs(raw) do                     -- تحويل لإحداثيات العالم
        LAMPS[#LAMPS + 1] = {
            x = L.x + CASTLE.ORIGIN.x,
            y = L.y + CASTLE.ORIGIN.y,
            z = L.z + CASTLE.ORIGIN.z,
            r = L.r, c = L.c, t = L.t,
        }
    end
    initShaders()
    applyDayLighting()
    addEventHandler("onClientPreRender", root, mainLoop)
    outputDebugString(("[CASTLE] إضاءة جاهزة — %d مصدر ضوء"):format(#LAMPS), 3)
end)
