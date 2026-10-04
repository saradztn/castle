--[[
    loader.lua — تحميل الموديلات والتصادم و LOD (عميل)
    Castle & Palace — مدينة القلعة الساحلية

    الترتيب الإلزامي في MTA: COL -> TXD -> DFF
]]

local function fileExists(path)
    return fileExists(path) and path or nil
end

-- ======== تحميل موديل واحد ========
local function loadCastleModel(cfg)
    local modelId = cfg.id

    -- 1) التصادم
    if cfg.col then
        local col = engineLoadCOL(cfg.col)
        if col then engineReplaceCOL(col, modelId) end
    end

    -- 2) الخامات
    if cfg.txd then
        local txd = engineLoadTXD(cfg.txd, true)
        if txd then engineImportTXD(txd, modelId) end
    end

    -- 3) الموديل
    if cfg.dff then
        local dff = engineLoadDFF(cfg.dff)
        if dff then engineReplaceModel(dff, modelId, true) end
    end

    -- 4) مسافة ظهور
    if modelId == CASTLE.MODELS.main.id then
        engineSetModelLODDistance(modelId, CASTLE.LOD.near)
    elseif modelId == CASTLE.MODELS.lod1.id then
        engineSetModelLODDistance(modelId, CASTLE.LOD.lod1)
    elseif modelId == CASTLE.MODELS.lod2.id then
        engineSetModelLODDistance(modelId, CASTLE.LOD.lod2)
    else
        engineSetModelLODDistance(modelId, CASTLE.LOD.lod3)
    end
    return true
end

-- ======== إنشاء الكائنات + سلسلة LOD ========
function createCastleObjects()
    local ox, oy, oz = CASTLE.ORIGIN.x, CASTLE.ORIGIN.y, CASTLE.ORIGIN.z
    local rx, ry, rz = CASTLE.ROTATION[1], CASTLE.ROTATION[2], CASTLE.ROTATION[3]

    local lod3 = createObject(CASTLE.MODELS.lod3.id, ox, oy, oz, rx, ry, rz, true)
    local lod2 = createObject(CASTLE.MODELS.lod2.id, ox, oy, oz, rx, ry, rz, true)
    local lod1 = createObject(CASTLE.MODELS.lod1.id, ox, oy, oz, rx, ry, rz, true)
    local main = createObject(CASTLE.MODELS.main.id, ox, oy, oz, rx, ry, rz, false)

    -- ربط المستويات: كل مستوى يتحول للذي بعده
    setLowLODElement(main, lod1)
    setLowLODElement(lod1, lod2)
    setLowLODElement(lod2, lod3)

    -- منع حذف الموديل من الذاكرة عند الابتعاد (المدينة كتلة واحدة كبيرة)
    for _, el in ipairs({ lod3, lod2, lod1, main }) do
        if isElement(el) then
            setElementStreamable(el, false)
            setElementFrozen(el, true)
        end
    end

    CASTLE.elements = { main = main, lod1 = lod1, lod2 = lod2, lod3 = lod3 }
    triggerEvent("castle:onLoaded", resourceRoot, main)
    return main
end

-- ======== نقطة البداية: إخفاء أي مبانٍ أصلية مكان القلعة (اختياري) ========
local function clearWorldArea()
    -- احذف هذا السطر أو عدّل الإحداثيات إن كنت تبني في منطقة فارغة من البحر
    -- removeWorldModel(3524, 3000, CASTLE.ORIGIN.x, CASTLE.ORIGIN.y, CASTLE.ORIGIN.z)
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    local ok = true
    for _, cfg in pairs(CASTLE.MODELS) do
        if not loadCastleModel(cfg) then ok = false end
    end
    if not ok then
        outputDebugString("[CASTLE] تعذّر تحميل بعض ملفات الموديل — تحقق من models/*.dff|txd|col", 1)
    end
    clearWorldArea()
    setFarClipDistance(CASTLE.LOD.farclip)
    createCastleObjects()
    outputDebugString("[CASTLE] تم تحميل مدينة القلعة", 3)
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    if CASTLE.elements then
        for _, el in pairs(CASTLE.elements) do
            if isElement(el) then destroyElement(el) end
        end
    end
end)
