--[[
    client/main.lua — تحميل موديل المدينة، ربط LOD، وتقارير التقدّم
    Castle & Palace — MTA:SA
]]

local modelIds = {}
local lodElements = {          -- { {highElement, medElement, lowElement, distElement}, ... }
}
local loadProgress = { loaded = 0, total = 0 }
local isReady = false

-- ================= إدارة معرّفات الموديلات =================
local function allocModel()
    if engineRequestModel then
        local id = engineRequestModel("object")
        if id then return id end
    end
    CASTLE.modelBase = CASTLE.modelBase + 1
    return CASTLE.modelBase - 1
end

-- ================= التحميل =================
local function loadPart(name, dffPath, txdPath, colPath, pos, rot, lodIndex)
    loadProgress.total = loadProgress.total + 1
    local id = allocModel()
    modelIds[name] = id

    if txdPath and fileExists(txdPath) then
        local txd = engineLoadTXD(txdPath, true)
        if txd then engineImportTXD(txd, id) end
    end
    if dffPath and fileExists(dffPath) then
        local dff = engineLoadDFF(dffPath)
        if dff then engineReplaceModel(dff, id, true) end
    end
    if colPath and fileExists(colPath) then
        local col = engineLoadCOL(colPath)
        if col then engineReplaceCOL(col, id) end
    end

    local obj = createObject(id, pos[1], pos[2], pos[3], rot and rot[1] or 0, rot and rot[2] or 0, rot and rot[3] or 0, false)
    setElementFrozen(obj, true)
    setElementDoubleSided(obj, false)
    engineSetModelLODDistance(id, CASTLE.lod[lodIndex or 1].distance)

    loadProgress.loaded = loadProgress.loaded + 1
    triggerEvent("castle:loadProgress", resourceRoot, loadProgress.loaded, loadProgress.total)
    return obj
end

local function loadAll()
    -- الكتل الرئيسية: القصر، الأسوار، المدينة، المرفأ، الجسر (تُقسَّم إلى أجزاء DFF منفصلة)
    local parts = {
        { name = "palace",     dff = "models/parts/palace.dff",     txd = "models/castle.txd", col = "models/parts/palace.col",     pos = {0, 0, 112},   lod = 1 },
        { name = "walls",      dff = "models/parts/walls.dff",      txd = "models/castle.txd", col = "models/parts/walls.col",      pos = {0, 0, 0},     lod = 1 },
        { name = "town",       dff = "models/parts/town.dff",       txd = "models/castle.txd", col = "models/parts/town.col",       pos = {0, 0, 0},     lod = 1 },
        { name = "harbour",    dff = "models/parts/harbour.dff",    txd = "models/castle.txd", col = "models/parts/harbour.col",    pos = {0, 0, 0},     lod = 2 },
        { name = "causeway",   dff = "models/parts/causeway.dff",   txd = "models/castle.txd", col = "models/parts/causeway.col",   pos = {0, 0, 0},     lod = 2 },
        { name = "cliff",      dff = "models/parts/cliff.dff",      txd = "models/castle.txd", col = "models/parts/cliff.col",      pos = {0, 0, 0},     lod = 1 },
    }

    local elements = {}
    for _, p in ipairs(parts) do
        local obj = loadPart(p.name, p.dff, p.txd, p.col, p.pos, nil, p.lod)
        if obj then elements[#elements + 1] = obj end
    end

    -- LOD متعدد المستويات: كل جزء عالي يُربط ببديله الأدنى
    local high = createObject(allocModel(), 0, 0, 0)
    -- (نموذج LOD يُحمَّل بنفس الطريقة — يُستبدل موديله في loadPart إن رغبت)
    for i, el in ipairs(elements) do
        local lowEl = elements[i + 1] or elements[i]
        if lowEl and lowEl ~= el then setLowLODElement(lowEl, el) end
    end

    isReady = true
    triggerEvent("castle:ready", resourceRoot)
    outputChatBox("#7fd1ff[Castle] #ffffffتم تحميل المدينة بالكامل ✅", 255, 255, 255, true)
end

-- ================= الواجهة =================
function getCastleProgress()
    if loadProgress.total == 0 then return 0 end
    return math.floor((loadProgress.loaded / loadProgress.total) * 100)
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    if getElementData(resourceRoot, "castle:timeSynced") == nil then
        -- القيم الافتراضية قبل مزامنة السيرفر
        setElementData(resourceRoot, "castle:timeSynced", true)
    end
    loadAll()
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    for _, el in pairs(modelIds) do
        engineRestoreModel(el)
    end
    for _, el in ipairs(getElementsByType("object")) do
        if getElementData(el, "castle:part") then destroyElement(el) end
    end
end)

addEvent("castle:loadProgress", true)
addEventHandler("castle:loadProgress", resourceRoot, function(loaded, total)
    triggerEvent("onClientRender", resourceRoot)   -- يُستخدم من الواجهة إن وُجدت
end)
