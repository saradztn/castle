--[[
    s_commands.lua — أوامر السيرفر
    Castle & Palace — مدينة القلعة الساحلية
]]

-- /castle_time day|night|auto  (للأدمن فقط)
addCommandHandler("castletime", function(player, _, mode)
    if not hasObjectPermissionTo(player, "function.banPlayer", false) then
        outputChatBox("هذا الأمر للأدمن فقط.", player, 255, 120, 120)
        return
    end
    if mode == "day" or mode == "night" or mode == "auto" then
        triggerEvent("castle:setLighting", root, mode)
        outputChatBox("🌗 تم ضبط الإضاءة على: " .. mode, root, 200, 230, 255)
    else
        outputChatBox("استخدم: /castletime day | night | auto", player, 255, 200, 150)
    end
end)

-- /castlegoto <منطقة>  (ينقل اللاعب)
addCommandHandler("castlegoto", function(player, _, area)
    if not area then
        outputChatBox("المناطق: main_square, palace_gate, garden, town_mid, market, wall_walk, harbour, causeway, lighthouse, waterfalls", player, 255, 220, 150)
        return
    end
    triggerClientEvent(player, "castle:onGotoRequest", resourceRoot, area)
end)

-- مزامنة حالة الإضاءة لكل لاعب يدخل
addEventHandler("onPlayerJoin", root, function()
    local p = source
    setTimer(function()
        if isElement(p) then
            triggerClientEvent(p, "castle:onLightingChanged", resourceRoot,
                getElementData(root, "castle:lighting") or "auto")
        end
    end, 4000, 1)
end)
