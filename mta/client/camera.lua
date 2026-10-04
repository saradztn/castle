--[[
    client/camera.lua — كاميرا سينمائية (جولة تعريفية بالمدينة)
    تُنشئ مسار كاميرا ناعم يطابق اللقطات: بطهورية → المرفأ → الجسر → القصر → ليل
]]

local active = false
local shotIdx = 1
local shotT = 0

-- لقطات: {pos, lookAt, ms, mode}
local SHOTS = {
    { pos = { 620, -980, 300 },  look = { 20, -40, 90 },   ms = 12000, mode = "day"   },   -- بطهورية
    { pos = { 250, -300, 60 },   look = { 90, -250, 22 },  ms = 9000,  mode = "day"   },   -- المرفأ
    { pos = { 380, -300, 40 },   look = { 210, -256, 24 }, ms = 9000,  mode = "day"   },   -- الجسر
    { pos = { 60, -180, 160 },   look = { 0, -10, 120 },   ms = 10000, mode = "day"   },   -- القصر
    { pos = { -180, -220, 120 }, look = { -150, -160, 60 },ms = 8000,  mode = "day"   },   -- الشلالات
    { pos = { 420, -620, 200 },  look = { 30, -80, 90 },   ms = 12000, mode = "night" },   -- ليل
}

local function applyShot(i)
    local s = SHOTS[i]
    setCameraMatrix(s.pos[1], s.pos[2], s.pos[3], s.look[1], s.look[2], s.look[3])
    if s.mode and setCastleLighting then
        setCastleLighting(s.mode)
    end
    shotT = getTickCount()
end

local function render()
    if not active then return end
    local s = SHOTS[shotIdx]
    if not s then return end
    -- حركة بطيئة (dolly) داخل اللقطة
    local p = math.min(1, (getTickCount() - shotT) / s.ms)
    local ox = math.sin(p * math.pi) * 18
    local oz = math.cos(p * math.pi) * 10
    setCameraMatrix(s.pos[1] + ox, s.pos[2], s.pos[3] + oz, s.look[1], s.look[2], s.look[3])
    if p >= 1 then
        shotIdx = shotIdx + 1
        if shotIdx > #SHOTS then
            stopCinema()
        else
            applyShot(shotIdx)
        end
    end
end

function startCinema()
    if active then return end
    active = true
    shotIdx = 1
    applyShot(1)
    setElementData(resourceRoot, "castle:cinema", true)
    addEventHandler("onClientRender", root, render)
    outputChatBox("#ffd27f[Castle] #ffffffبدأ العرض السينمائي — اكتب /castlecinema للإيقاف", 255, 255, 255, true)
end

function stopCinema()
    if not active then return end
    active = false
    removeEventHandler("onClientRender", root, render)
    setCameraTarget(localPlayer)
    setElementData(resourceRoot, "castle:cinema", false)
    local mode = getElementData(resourceRoot, "castle:mode") or "day"
    if setCastleLighting then setCastleLighting(mode) end
    outputChatBox("#ffd27f[Castle] #ffffffانتهى العرض السينمائي", 255, 255, 255, true)
end

addCommandHandler("castlecinema", function()
    if active then stopCinema() else startCinema() end
end)

addEvent("castle:startCinema", true)
addEventHandler("castle:startCinema", root, function()
    if not localPlayer or source ~= localPlayer then return end
    startCinema()
end)
