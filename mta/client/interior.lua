--[[
    client/interior.lua — نظام الداخليات (14 منطقة كما في لوحة المشروع)
    كل داخلية لها مدخل في المدينة + نسخة داخلية عند CASTLE.interiorOffset.
]]

local insideId = nil
local fading = false

local function fade(toBlack, ms, cb)
    if fading then return end
    fading = true
    local a = toBlack and 0 or 255
    local target = toBlack and 255 or 0
    local start = getTickCount()
    local t = {}
    t[1] = setTimer(function()
        local p = math.min(1, (getTickCount() - start) / ms)
        local v = math.floor(a + (target - a) * p)
        if cb then cb(v) end
        if p >= 1 then
            if t[1] and isTimer(t[1]) then killTimer(t[1]) end
            fading = false
        end
    end, 16, 0)
end

local function getInterior(id)
    for _, it in ipairs(CASTLE.interiors or {}) do
        if it.id == id then return it end
    end
end

local function enterInterior(it)
    local off = CASTLE.interiorOffset
    fade(true, 260, function(a)
        dxDrawRectangle(0, 0, guiGetScreenSize(), 1)   -- (يُرسم في onClientRender الفعلي)
    end)
    setTimer(function()
        setElementPosition(localPlayer, it.x + off.x, it.y + off.y, it.z + off.z + 2)
        setElementFrozen(localPlayer, false)
        insideId = it.id
        fade(false, 320)
        outputChatBox("#ffd27f[Castle] #ffffff" .. (it.name or "interior"), 255, 255, 255, true)
    end, 280, 1)
end

local function exitInterior(it)
    fade(true, 240)
    setTimer(function()
        setElementPosition(localPlayer, it.x, it.y, it.z + 2)
        insideId = nil
        fade(false, 300)
    end, 260, 1)
end

-- ================= شاشة التعتيم =================
local alpha = 0
local function renderFade()
    if alpha <= 0 then return end
    local sw, sh = guiGetScreenSize()
    dxDrawRectangle(0, 0, sw, sh, tocolor(0, 0, 0, alpha), false)
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    local off = CASTLE.interiorOffset
    for _, it in ipairs(CASTLE.interiors or {}) do
        -- مدخل خارجي
        local mOut = createMarker(it.x, it.y, it.z + 1.2, "cylinder", 2.4, 255, 200, 90, 90)
        setElementData(mOut, "castle:interior", it.id)
        addEventHandler("onClientMarkerHit", mOut, function(hit, dim)
            if hit ~= localPlayer or not dim or insideId then return end
            enterInterior(it)
        end)
        -- مخرج داخلي
        local mIn = createMarker(it.x + off.x, it.y + off.y, it.z + off.z + 2.2, "cylinder", 2.4, 120, 200, 255, 90)
        addEventHandler("onClientMarkerHit", mIn, function(hit, dim)
            if hit ~= localPlayer or not dim then return end
            exitInterior(it)
        end)
        -- مالك الداخلية
        local def = { id = it.id, out = mOut, inp = mIn }
        setElementData(mOut, "castle:def", it.id)
    end
    addEventHandler("onClientRender", root, renderFade)
end)

function getInsideInterior()
    return insideId
end
