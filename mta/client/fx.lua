--[[
    client/fx.lua — الفكسات القوية
    شلالات + رشّاش ماء + دخان مداخن + نار المشاعل والمناقل + طيور بحر + رغوة بحر + رايات متحركة
]]

local foamTexture, smokeTexture, flagTexture
local birds = {}
local seaFoam = {}
local currentMode = "day"

-- ================= الشلالات =================
local function buildWaterfalls()
    for _, wf in ipairs(CASTLE.fx.waterfalls or {}) do
        -- جسم الشلال
        createEffect("waterfall", wf.x, wf.y, wf.z - wf.h * 0.5)
        -- رشّاش/ضباب ماء عند القاعدة
        createEffect("waterfallsmoke", wf.x, wf.y, wf.z - wf.h)
        createEffect("waterfallsmoke", wf.x + 3, wf.y + 2, wf.z - wf.h + 1.5)
        -- فقاعات وأثر ماء
        createEffect("waterfalldrops", wf.x, wf.y, wf.z - wf.h * 0.35)
    end
end

-- ================= المداخن والمشاعل =================
local function buildSmoke()
    for _, s in ipairs(CASTLE.fx.smokeStacks or {}) do
        createEffect("smoke30lit", s.x, s.y, s.z)
    end
    for _, l in ipairs(CASTLE.lights or {}) do
        if l.kind == "torch" then
            createFire(l.x, l.y, l.z + 1.2, 0.35, false)          -- نار صغيرة
            createEffect("smoke30lit", l.x, l.y, l.z + 2.2)
        elseif l.kind == "brazier" then
            createFire(l.x, l.y, l.z, 0.9, true)                  -- منقل كبير
            createEffect("smoke30lit", l.x, l.y, l.z + 2.6)
        end
    end
end

-- ================= طيور البحر =================
local function buildBirds()
    for i = 1, (CASTLE.fx.birdCount or 20) do
        local a = (i / (CASTLE.fx.birdCount or 20)) * math.pi * 2
        birds[i] = {
            r = 220 + math.random() * 220,
            a = a,
            speed = 0.06 + math.random() * 0.10,
            z = 40 + math.random() * 90,
            bob = math.random() * math.pi * 2,
        }
    end
end

-- ================= رغوة البحر =================
local function buildSeaFoam()
    for i = 1, (CASTLE.fx.seaFoamCount or 30) do
        local a = math.random() * math.pi * 2
        local r = 260 + math.random() * 90
        seaFoam[i] = { x = math.cos(a) * r, y = math.sin(a) * r * 1.15, size = 8 + math.random() * 14, phase = math.random() * 6.28 }
    end
end

-- ================= الرسم كل إطار =================
local function render()
    local now = getTickCount() / 1000
    local camX, camY, camZ = getCameraMatrix()

    -- الطيور
    for _, b in ipairs(birds) do
        b.a = b.a + b.speed * 0.016
        local x = math.cos(b.a) * b.r
        local y = math.sin(b.a) * b.r * 1.15
        local z = b.z + math.sin(now * 1.4 + b.bob) * 3.5
        local d = (x - camX) ^ 2 + (y - camY) ^ 2
        if d < 700 * 700 and smokeTexture then
            dxDrawMaterialLine3D(x, y, z + 0.55, x, y, z - 0.55, smokeTexture, 1.6, tocolor(20, 22, 26, 210))
            dxDrawMaterialLine3D(x + 1.1, y, z, x - 1.1, y, z, smokeTexture, 1.6, tocolor(20, 22, 26, 210))
        end
    end

    -- رغوة البحر على الصخور
    if foamTexture then
        for _, f in ipairs(seaFoam) do
            local pulse = 0.55 + 0.45 * math.sin(now * 0.9 + f.phase)
            local d = (f.x - camX) ^ 2 + (f.y - camY) ^ 2
            if d < 600 * 600 then
                dxDrawMaterialLine3D(f.x - f.size / 2, f.y, 1.2, f.x + f.size / 2, f.y, 1.2,
                                     foamTexture, f.size, tocolor(255, 255, 255, math.floor(120 * pulse)))
            end
        end
    end
end

-- ================= رايات وأشرعة متحركة (شيدر) =================
local function flagShaderForBanner()
    local sh = dxCreateShader("shaders/night_grade.fx")   -- استخدام عام؛ يُفضّل شيدر راية مخصص
    return sh
end

-- ================= الأحداث =================
addEventHandler("onClientResourceStart", resourceRoot, function()
    foamTexture = dxCreateTexture("assets/foam.png", "argb", true, "clamp")
    smokeTexture = dxCreateTexture("assets/smoke.png", "argb", true, "clamp")
    flagTexture = dxCreateTexture("assets/flag.png", "argb", true, "clamp")
    buildWaterfalls()
    buildSmoke()
    buildBirds()
    buildSeaFoam()
    addEventHandler("onClientRender", root, render)
end)

addEventHandler("castle:modeChanged", resourceRoot, function(mode)
    currentMode = mode
    -- النار تشتعل أكثر ليلًا
    for _, l in ipairs(CASTLE.lights or {}) do
        if l.kind == "torch" or l.kind == "brazier" then
            if isElement(getElementData(resourceRoot, "fire_" .. tostring(l.x))) then
                -- (تُدار النيران عبر createFire أعلاه)
            end
        end
    end
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    for _, tex in ipairs({ foamTexture, smokeTexture, flagTexture }) do
        if tex and isElement(tex) then destroyElement(tex) end
    end
end)
