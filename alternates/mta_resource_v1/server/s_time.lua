--[[
    s_time.lua — إدارة وقت اليوم والإضاءة على السيرفر (متزامن لكل اللاعبين)
    Castle & Palace — مدينة القلعة الساحلية
]]

-- الحالة المتزامنة عبر عناصر البيانات: castle:lighting = "auto" | "day" | "night"
addEventHandler("onResourceStart", resourceRoot, function()
    setElementData(root, "castle:lighting", "auto")
    -- وقت اللعبة الافتراضي: نهار
    setTime(CASTLE.TIME.dayTime[1], CASTLE.TIME.dayTime[2])
    setMinuteDuration(CASTLE.TIME.minuteDuration)
    outputDebugString("[CASTLE] سيرفر القلعة جاهز", 3)
end)

-- تبديل الإضاءة عالميًا (يصدر حدثًا للعملاء)
addEvent("castle:setLighting", true)
addEventHandler("castle:setLighting", root, function(mode)
    if mode == "auto" or mode == "day" or mode == "night" then
        setElementData(root, "castle:lighting", mode)
        triggerClientEvent(root, "castle:onLightingChanged", resourceRoot, mode)
    end
end)
