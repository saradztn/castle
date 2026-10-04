--[[
    client/lighting.lua — نظام الإضاءة اليومي/الليلي لمنطقة القلعة
    يطابق دالة setCastleLighting في لوحة المشروع، لكن كاملة ومصحّحة.
]]

local shaderEmissive           -- شيدر النوافذ المضيئة
local isNight = false
local lightingReady = false

-- ================= أدوات =================
local function lerp(a, b, t) return a + (b - a) * t end

local function applyWorldLook(mode)
    -- سماء وماء وضباب تتغيّر مع الوضع
    if mode == "night" then
        setSkyGradient(6, 9, 22, 18, 24, 48)
        setWaterColor(10, 32, 44, 190)
        setFogDistance(240)
        setFarClipDistance(2600)
        setSunSize(0)
    else
        setSkyGradient(96, 150, 220, 240, 208, 160)
        setWaterColor(24, 78, 92, 170)
        setFogDistance(420)
        setFarClipDistance(4200)
        setSunSize(4)
    end
end

-- ================= التبديل الأساسي =================
function setCastleLighting(mode)
    mode = (mode == "night") and "night" or "day"
    isNight = (mode == "night")

    -- 1) وقت اللعبة
    setTime(isNight and (CASTLE.nightHour or 0) or (CASTLE.dayHour or 12), 0)

    -- 2) المظهر العام
    applyWorldLook(mode)

    -- 3) الأضواء والنوافذ والفكسات (يستمع لها باقي ملفات العميل)
    triggerEvent("castle:modeChanged", resourceRoot, mode)

    -- 4) شيدر النوافذ المضيئة
    if shaderEmissive and isElement(shaderEmissive) then
        dxSetShaderValue(shaderEmissive, "gIntensity", isNight and 1.0 or 0.0)
        local tint = isNight and { 1.0, 0.72, 0.40 } or { 0.65, 0.80, 0.95 }
        dxSetShaderValue(shaderEmissive, "gColor", tint[1], tint[2], tint[3])
    end

    -- 5) تحديث بيانات العالم (تُستخدم من السيرفر/اللوحات)
    setElementData(resourceRoot, "castle:mode", mode)
    lightingReady = true
end

-- ================= الجاهزية =================
addEventHandler("castle:ready", resourceRoot, function()
    local mode = getElementData(resourceRoot, "castle:mode") or "day"
    setCastleLighting(mode)
end)

-- استقبال التبديل من السيرفر (أو من سكربت آخر)
addEvent("setCastleLighting", true)
addEventHandler("setCastleLighting", root, function(mode)
    setCastleLighting(mode)
end)
addEvent("castle:syncMode", true)
addEventHandler("castle:syncMode", root, function(mode)
    setCastleLighting(mode)
end)

-- ================= التبديل التلقائي =================
setTimer(function()
    if not lightingReady or not CASTLE.autoTime then return end
    local h = getTime()
    local shouldBeNight = (h < CASTLE.dayStart) or (h >= CASTLE.nightStart)
    if shouldBeNight and not isNight then
        triggerServerEvent("castle:requestMode", localPlayer, "night")
    elseif (not shouldBeNight) and isNight then
        triggerServerEvent("castle:requestMode", localPlayer, "day")
    end
end, CASTLE.autoTick or 30000, 0)

function isCastleNight()
    return isNight
end
