--[[
    hud.lua — واجهة/معلومات + شاشة تحميل + مؤشر الموقع والمسافة
    Castle & Palace — مدينة القلعة الساحلية
]]

local loading = true
local loadStart = getTickCount()

addEventHandler("onClientResourceStart", resourceRoot, function()
    loading = true
    loadStart = getTickCount()
    setTimer(function() loading = false end, 3500, 1)
end)

addEventHandler("castle:onLoaded", resourceRoot, function()
    setTimer(function() loading = false end, 800, 1)
end)

addEventHandler("onClientRender", root, function()
    -- شاشة تحميل بسيطة
    if loading then
        local a = math.min(255, (getTickCount() - loadStart) / 6)
        dxDrawRectangle(0, screenH * 0.40, screenW, 120, tocolor(6, 10, 18, a * 0.85))
        dxDrawText("Castle & Palace", 0, screenH * 0.40, screenW, screenH * 0.40 + 60,
                   tocolor(255, 216, 150, a), 2.0, "default-bold", "center", "center")
        dxDrawText("مدينة القلعة الساحلية — جارٍ تحميل الموديل والخامات…", 0, screenH * 0.40 + 58,
                   screenW, screenH * 0.40 + 100, tocolor(210, 220, 235, a), 1.0, "default", "center", "center")
        return
    end

    -- معلومات صغيرة أعلى اليسار
    local px, py, pz = getElementPosition(localPlayer)
    local dx = px - CASTLE.ORIGIN.x
    local dy = py - CASTLE.ORIGIN.y
    local dist = math.sqrt(dx * dx + dy * dy + pz * pz)
    if dist < 2500 then
        dxDrawText(("ارتفاع: %d م   |   الإضاءة: %s"):format(math.floor(pz - CASTLE.ORIGIN.z),
            CASTLE.lightState == "night" and "ليل" or "نهار"),
            14, 14, 600, 40, tocolor(255, 236, 200, 220), 1.05, "default-bold")
    end
end)

-- ======== مفتاح F للتبديل بين نهار/ليل محليًا (لا يؤثر على السيرفر) ========
addCommandHandler("castle_time", function(_, mode)
    if mode == "day" or mode == "night" then
        setElementData(root, "castle:lighting", mode)
        outputChatBox("🌗 الإضاءة: " .. (mode == "night" and "ليل" or "نهار"), 200, 230, 255)
    else
        outputChatBox("استخدم: /castle_time day | night | auto", 255, 200, 150)
    end
end)
