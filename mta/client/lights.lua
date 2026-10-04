--[[
    client/lights.lua — مدير الأضواء (LOD للأضواء)
    MTA تسمح بعدد محدود من الأضواء الحقيقية (createLight) في نفس اللحظة،
    لذلك نُنشئ فقط أقرب CASTLE.maxLights مصدرًا ونُعيد تدويرها كل إطار تقريبًا،
    ونعرض هالة (corona) لكل مصدر حتى لو لم يكن له ضوء حقيقي.
]]

local activeLights = {}          -- { element = lightElement, sourceIdx = n }
local glowTexture
local lastUpdate = 0
local currentMode = "day"

-- ================= أدوات =================
local function lightSources()
    return CASTLE.lights or {}
end

local function distanceSq(x1, y1, z1, x2, y2, z2)
    local dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
    return dx * dx + dy * dy + dz * dz
end

-- ================= إنشاء الأضواء الحقيقية =================
local function updateRealLights()
    local px, py, pz = getCameraMatrix()            -- نستخدم الكاميرا لا اللاعب
    local src = lightSources()
    local idxDist = {}
    for i, l in ipairs(src) do
        idxDist[i] = { i = i, d = distanceSq(px, py, pz, l.x, l.y, l.z) }
    end
    table.sort(idxDist, function(a, b) return a.d < b.d end)

    local want = (currentMode == "night") and math.min(#activeLights > 0 and #CASTLE.lights or CASTLE.maxLights, CASTLE.maxLights) or 0

    -- تأمين عدد الأضواء المطلوب
    while #activeLights < want do
        local li = #activeLights + 1
        local srcIdx = idxDist[li] and idxDist[li].i or 1
        local l = src[srcIdx]
        local el = createLight("point", l.x, l.y, l.z, l.radius or 20, unpack(l.color or { 255, 170, 90 }))
        if el then
            activeLights[#activeLights + 1] = { element = el, sourceIdx = srcIdx }
        else
            break
        end
    end
    while #activeLights > want do
        local last = table.remove(activeLights)
        if isElement(last.element) then destroyElement(last.element) end
    end

    -- توجيه الأضواء الحقيقية إلى أقرب المصادر
    for i, a in ipairs(activeLights) do
        local pick = idxDist[i]
        if pick then
            local l = src[pick.i]
            if isElement(a.element) then
                setElementPosition(a.element, l.x, l.y, l.z)
                setLightColor(a.element, unpack(l.color or { 255, 170, 90 }))
                if setLightRadius then setLightRadius(a.element, l.radius or 20) end
            end
        end
    end
end

-- ================= الهالات (تُرسم دائمًا) =================
local function drawCoronas()
    if currentMode ~= "night" or not glowTexture then return end
    local px, py, pz = getCameraMatrix()
    local src = lightSources()
    for _, l in ipairs(src) do
        local d = distanceSq(px, py, pz, l.x, l.y, l.z)
        if d < 400 * 400 then                        -- لا تُرسم الهالات من بعيد
            local scale = (l.kind == "brazier") and 6.0 or 4.0
            local fade = 1.0 - math.min(1.0, math.sqrt(d) / 400.0)
            local a = 150 * fade * (l.intensity or 1.0)
            local size = scale * (0.6 + 0.4 * fade)
            dxDrawMaterialLine3D(l.x, l.y, l.z + size * 0.3, l.x, l.y, l.z - size * 0.3,
                                 glowTexture, size, tocolor(l.color[1], l.color[2], l.color[3], a))
        end
    end
end

-- ================= الأحداث =================
addEventHandler("castle:modeChanged", resourceRoot, function(mode)
    currentMode = mode
    if mode == "night" then
        while #activeLights < math.min(CASTLE.maxLights or 7, #(CASTLE.lights or {})) do
            local i = #activeLights + 1
            local l = (CASTLE.lights or {})[i]
            if not l then break end
            local el = createLight("point", l.x, l.y, l.z, l.radius or 20, unpack(l.color or { 255, 170, 90 }))
            if el then activeLights[#activeLights + 1] = { element = el, sourceIdx = i } else break end
        end
    else
        for _, a in ipairs(activeLights) do
            if isElement(a.element) then destroyElement(a.element) end
        end
        activeLights = {}
    end
end)

addEventHandler("onClientResourceStart", resourceRoot, function()
    glowTexture = dxCreateTexture("assets/glow.png", "argb", true, "clamp")
    addEventHandler("onClientRender", root, drawCoronas)
    addEventHandler("onClientPreRender", root, function()
        local now = getTickCount()
        if now - lastUpdate > 900 then                 -- إعادة حساب كل 0.9 ثانية
            updateRealLights()
            lastUpdate = now
        end
    end)
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    for _, a in ipairs(activeLights) do
        if isElement(a.element) then destroyElement(a.element) end
    end
    activeLights = {}
    if glowTexture and isElement(glowTexture) then destroyElement(glowTexture) end
end)
