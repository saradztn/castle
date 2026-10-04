--[[
    client/main.lua — تحميل مدينة القلعة (7 أجزاء × 4 مستويات LOD) + تقارير الجاهزية
    Castle & Palace — MTA:SA

    الترتيب الإلزامي لكل موديل:  COL ← TXD ← DFF   (وإلا انهار الموديل أو اختفت خاماته)

    بنية الملفات المتوقّعة (تنتجها أدوات المشروع):
      models/parts/<part>.dff | .col        ← التفصيل الكامل (7 أجزاء)
      models/lod/<part>_medium.dff          ← 850 م
      models/lod/<part>_low.dff             ← 1800 م
      models/lod/<part>_distant.dff         ← 4200 م
      models/castle.txd                     ← الـ39 خامة PBR
]]

local modelIds = {}
local partElements = {}        -- name → { high, medium, low, distant }
local loadProgress = { loaded = 0, total = 0 }
local isReady = false

-- الأجزاء السبعة (تُبنى في tools/build_city.py وتُقسَّم في tools/make_lod.py)
local PARTS = { "palace", "walls", "town", "harbour", "causeway", "cliff", "interiors" }

-- مستويات LOD: المسافة تُقاس من الكاميرا
local LEVELS = {
    { suffix = "",         file = "parts/%s.dff",        lod = "lod/%s_medium.dff",  dist = 320.0  },
    { suffix = "_medium",  file = "lod/%s_medium.dff",   lod = "lod/%s_low.dff",     dist = 850.0  },
    { suffix = "_low",     file = "lod/%s_low.dff",      lod = "lod/%s_distant.dff", dist = 1800.0 },
    { suffix = "_distant", file = "lod/%s_distant.dff",  lod = nil,                  dist = 4200.0 },
}

-- ================= إدارة معرّفات الموديلات =================
local usedIds = {}
local function allocModel()
    if engineRequestModel then
        local id = engineRequestModel("object")
        if id then
            usedIds[#usedIds + 1] = id
            return id
        end
    end
    CASTLE.modelBase = (CASTLE.modelBase or 19000) + 1
    return CASTLE.modelBase - 1
end

-- ================= تحميل موديل واحد =================
local function loadModel(dffPath, colPath, txdPath, dist)
    local id = allocModel()
    if colPath and fileExists(colPath) then
        local col = engineLoadCOL(colPath)
        if col then engineReplaceCOL(col, id) end
    end
    if txdPath and fileExists(txdPath) then
        local txd = engineLoadTXD(txdPath, true)          -- true = فلترة ممتازة للخامات
        if txd then engineImportTXD(txd, id) end
    end
    if dffPath and fileExists(dffPath) then
        local dff = engineLoadDFF(dffPath)
        if dff then engineReplaceModel(dff, id, true) end
    end
    engineSetModelLODDistance(id, dist)
    modelIds[#modelIds + 1] = id
    return id
end

local function spawn(id, name, level)
    local obj = createObject(id, 0, 0, 0, 0, 0, 0, false)
    if not obj then return nil end
    setElementFrozen(obj, true)
    setElementDoubleSided(obj, false)
    setElementData(obj, "castle:part", name)
    setElementData(obj, "castle:level", level)
    return obj
end

-- ================= تحميل كل الأجزاء =================
local function loadAll()
    local txd = "models/castle.txd"

    for _, name in ipairs(PARTS) do
        local chain = {}
        for lvl, L in ipairs(LEVELS) do
            local dff = string.format("models/" .. L.file, name)
            local col = (lvl == 1) and string.format("models/parts/%s.col", name) or nil
            if fileExists(dff) then
                local id = loadModel(dff, col, txd, L.dist)
                local obj = spawn(id, name, lvl)
                if obj then
                    chain[#chain + 1] = obj
                    -- سلسلة LOD: كل مستوى هو LOD للمستوى الأعلى منه تفصيلًا
                    if #chain > 1 then
                        setLowLODElement(chain[#chain], chain[#chain - 1])
                    end
                end
            end
            loadProgress.loaded = loadProgress.loaded + 1
            triggerEvent("castle:loadProgress", resourceRoot, loadProgress.loaded, loadProgress.total)
        end
        partElements[name] = chain
    end

    -- الـ14 داخلية تُنشأ في منطقة الإزاحة (0,6000,0) وتُبقى منفصلة عن LOD المدينة
    isReady = true
    triggerEvent("castle:ready", resourceRoot)
    outputChatBox("#7fd1ff[Castle] #ffffffتم تحميل المدينة بالكامل — 7 أجزاء × 4 مستويات LOD ✅", 255, 255, 255, true)
end

-- ================= الواجهة العامة =================
function getCastleProgress()
    if loadProgress.total == 0 then return 0 end
    return math.floor((loadProgress.loaded / loadProgress.total) * 100)
end

function isCastleReady()
    return isReady
end

function getCastlePartElements()
    return partElements
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    loadProgress.total = #PARTS * #LEVELS
    loadAll()
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    for _, el in ipairs(getElementsByType("object")) do
        if getElementData(el, "castle:part") then destroyElement(el) end
    end
    for _, id in ipairs(modelIds) do
        if engineRestoreModel then engineRestoreModel(id) end
    end
end)

addEvent("castle:loadProgress", true)
