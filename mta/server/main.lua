--[[
    server/main.lua — مزامنة الوقت والإضاءة وإعدادات العالم
    Castle & Palace — MTA:SA
]]

local mode = "day"

-- ================= إعداد العالم =================
local function setupWorld()
    setWaterLevel(0.0)                      -- البحر عند مستوى 0 (قاعدة الجزيرة)
    setWeather(0)                           -- صافٍ
    setMinuteDuration(60000)                -- دقيقة واقعية = دقيقة لعب
    setTime(CASTLE.dayHour, 0)
    setFogDistance(420)
    setFarClipDistance(4200)
    setJetpackMaxHeight(400)                -- للسماح بالتصوير من الأعلى
    setGameSpeed(1)

    -- ألوان الماء الافتراضية (تُغيَّر من العميل حسب الوضع)
    setWaterColor(24, 78, 92, 170)
    setSkyGradient(96, 150, 220, 240, 208, 160)

    -- منع السيارات/المشاة العشوائية حول المدينة
    for i, v in ipairs(getElementsByType("vehicle")) do
        if getElementInterior(v) == 0 then setElementFrozen(v, true) end
    end
end

-- ================= المزامنة =================
local function broadcast(newMode)
    mode = newMode
    triggerClientEvent(root, "setCastleLighting", root, mode)
    setElementData(root, "castle:mode", mode)
    outputChatBox("#7fd1ff[Castle] #ffffffالوضع الحالي: " .. (mode == "night" and "ليل 🌙" or "نهار ☀️"), 255, 255, 255, true)
end

addEventHandler("onResourceStart", resourceRoot, function()
    setupWorld()
    setTimer(function()
        local s = get("*castle:autoTime") or "true"
        if tostring(s) == "true" then
            local h = getTime()
            local want = (h >= 7 and h < 19) and "day" or "night"
            if want ~= mode then broadcast(want) end
        end
    end, 30000, 0)
end)

addEventHandler("castle:requestMode", root, function(requested)
    if not client then return end
    broadcast(requested == "night" and "night" or "day")
    triggerClientEvent(client, "castle:syncMode", client, mode)
end)

-- ================= أوامر الأدمن =================
addCommandHandler("castlemode", function(player, _, arg)
    if not hasObjectPermissionTo(player, "command.setTime", true) then
        outputChatBox("لا تملك صلاحية.", player, 255, 80, 80)
        return
    end
    broadcast((arg == "night") and "night" or "day")
end)

addCommandHandler("castlecinema", function(player, _)
    triggerClientEvent(player, "castle:startCinema", player)
end)

addCommandHandler("castletp", function(player, _, which)
    local spots = {
        gate     = { 196, -256, 20 },
        harbour  = { 60, -190, 12 },
        keep     = { 0, -10, 130 },
        gardens  = { 90, -10, 104 },
        causeway = { 320, -256, 22 },
        waterfall= { -150, -200, 80 },
    }
    local s = spots[which or "gate"]
    if s then
        setElementPosition(player, s[1], s[2], s[3] + 2)
        outputChatBox("#ffd27f[Castle] #ffffffتم النقل إلى: " .. tostring(which or "gate"), player, 255, 255, 255, true)
    else
        outputChatBox("المواضع: gate, harbour, keep, gardens, causeway, waterfall", player, 255, 255, 255)
    end
end)

-- ================= حفظ الحالة =================
addEventHandler("onResourceStop", resourceRoot, function()
    setWaterLevel(0.0)
end)
