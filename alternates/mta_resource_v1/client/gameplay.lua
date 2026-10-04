--[[
    gameplay.lua — اللعب والتنقّل داخل المدينة
    Castle & Palace — مدينة القلعة الساحلية
]]

local SPAWNS = {}

local function loadJSON(path)
    local f = fileOpen(path)
    if not f then return {} end
    local d = fromJSON(fileRead(f, fileGetSize(f))) or {}
    fileClose(f)
    return d
end

-- ======== مناطق + نقاط انتقال ========
local AREAS = {
    { name = "main_square",  label = "الساحة العليا",   x = 0,    y = 0,     z = 112 },
    { name = "palace_gate",  label = "بوابة القصر",     x = 0,    y = -30,   z = 112 },
    { name = "garden",       label = "الحدائق الملكية", x = -57,  y = 80,    z = 112 },
    { name = "town_mid",     label = "المدينة الوسطى",  x = 0,    y = -140,  z = 46 },
    { name = "market",       label = "سوق المدينة",     x = 60,   y = -150,  z = 24 },
    { name = "wall_walk",    label = "ممر الأسوار",     x = 0,    y = -230,  z = 84 },
    { name = "harbour",      label = "المرفأ",          x = -40,  y = -220,  z = 7 },
    { name = "causeway",     label = "الجسر المقوّس",   x = 180,  y = -300,  z = 17 },
    { name = "lighthouse",   label = "المنارة",         x = 245,  y = -140,  z = 12 },
    { name = "waterfalls",   label = "الشلالان",        x = -180, y = -230,  z = 20 },
}

function teleportTo(name)
    for _, a in ipairs(AREAS) do
        if a.name == name then
            local px = a.x + CASTLE.ORIGIN.x
            local py = a.y + CASTLE.ORIGIN.y
            local pz = a.z + CASTLE.ORIGIN.z
            local ped = localPlayer
            if getElementDimension(ped) ~= 0 then setElementDimension(ped, 0) end
            setElementPosition(ped, px, py, pz + 2)
            setElementVelocity(ped, 0, 0, 0)
            outputChatBox("📍 " .. a.label, 180, 220, 255)
            return true
        end
    end
    outputChatBox("منطقة غير معروفة. المناطق: " .. table.concat((function()
        local t = {}
        for _, a in ipairs(AREAS) do t[#t + 1] = a.name end
        return t
    end)(), ", "), 255, 120, 120)
    return false
end

addCommandHandler("castle", function(_, area)
    if not area then
        outputChatBox("استخدم: /castle <منطقة> — مثال: /castle harbour", 255, 220, 150)
        teleportTo("none")
        return
    end
    teleportTo(area)
end)

-- ======== انتقال يطلبه السيرفر ========
addEvent("castle:onGotoRequest", true)
addEventHandler("castle:onGotoRequest", resourceRoot, function(area)
    teleportTo(area)
end)

-- ======== اقتراحات أوامر ========
addEventHandler("onClientResourceStart", resourceRoot, function()
    SPAWNS = loadJSON("data/spawns.json")
    outputChatBox("#FFD27F[القلعة] #FFFFFFاكتب /castle لرؤية المناطق، و /castle_time day|night لتبديل الإضاءة.", 255, 255, 255, true)
end)

-- ======== مناطق الخريطة (اسم المنطقة أسفل الشاشة) ========
addEventHandler("onClientRender", root, function()
    local px, py, pz = getElementPosition(localPlayer)
    local best, bd = nil, 1e9
    for _, a in ipairs(AREAS) do
        local d = getDistanceBetweenPoints3D(px, py, pz,
            a.x + CASTLE.ORIGIN.x, a.y + CASTLE.ORIGIN.y, a.z + CASTLE.ORIGIN.z)
        if d < bd then bd, best = d, a end
    end
    if best and bd < 140 then
        local w, h = dxGetTextWidth(best.label, 1.4, "default-bold"), 26
        local x, y = (screenW - w) / 2 - 12, screenH - 120
        dxDrawRectangle(x, y, w + 24, h, tocolor(8, 12, 22, 165))
        dxDrawText(best.label, x, y, x + w + 24, y + h, tocolor(255, 214, 150, 255),
                   1.4, "default-bold", "center", "center")
    end
end)
