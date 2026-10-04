--[[
    client/shaders.lua — تحميل وتشغيل الشيدرات
    1) window_emissive : نوافذ مضيئة ليلًا
    2) ocean           : ماء متحرك بموجات وانعكاس
    3) terrain_detail  : تفاصيل تضاريس + بلاطة صخر/عشب حسب الميل
    4) night_grade     : دَرْج لوني ليلي + تعتيم حواف (Post-Processing)
]]

local shWindow, shOcean, shTerrain, shGrade
local screenSrc
local time = 0

-- ================= الإعداد =================
local function setupShaders()
    shWindow  = dxCreateShader("shaders/window_emissive.fx", 0, 300, false)
    shOcean   = dxCreateShader("shaders/ocean.fx", 0, 900, false)
    shTerrain = dxCreateShader("shaders/terrain_detail.fx", 0, 700, false)
    shGrade   = dxCreateShader("shaders/night_grade.fx", 0, 0, false)

    if shWindow then
        engineApplyShaderToWorldTexture(shWindow, "glass_leaded_pane_emissive")
        dxSetShaderValue(shWindow, "gIntensity", 0.0)
    end
    if shOcean then
        engineApplyShaderToWorldTexture(shOcean, "water_ocean")
        dxSetShaderValue(shOcean, "gWaveScale", 0.35)
    end
    if shTerrain then
        -- تُطبَّق على خامات التضاريس الأساسية
        for _, t in ipairs({ "rock_cliff_strata", "terrain_grass", "stone_cobble_street", "terrain_dirt_road" }) do
            engineApplyShaderToWorldTexture(shTerrain, t)
        end
    end

    local sw, sh = guiGetScreenSize()
    screenSrc = dxCreateScreenSource(sw, sh)
end

-- ================= التحديث كل إطار =================
local function update()
    time = time + 0.016

    if shOcean then
        dxSetShaderValue(shOcean, "gTime", time)
    end
    if shTerrain then
        dxSetShaderValue(shTerrain, "gTime", time * 0.35)
    end

    -- الدَرْج الليلي (Post-Processing) — يُرسم فقط ليلًا وبعيدًا عن القوائم
    if shGrade and screenSrc and isCastleNight and isCastleNight() then
        if isPlayerMapVisible and isPlayerMapVisible() then return end
        local sw, sh = guiGetScreenSize()
        dxUpdateScreenSource(screenSrc, true)
        dxSetShaderValue(shGrade, "gScreen", screenSrc)
        dxSetShaderValue(shGrade, "gTime", time)
        dxSetShaderValue(shGrade, "gStrength", 0.85)
        dxDrawImage(0, 0, sw, sh, shGrade, 0, 0, 0, tocolor(255, 255, 255, 255), false)
    end
end

addEventHandler("onClientResourceStart", resourceRoot, function()
    if not dxCreateShader then
        outputChatBox("#ff8888[Castle] الشيدرات غير مدعومة على هذا الجهاز", 255, 255, 255, true)
        return
    end
    setupShaders()
    addEventHandler("onClientRender", root, update)
end)

addEventHandler("castle:modeChanged", resourceRoot, function(mode)
    if shGrade then
        dxSetShaderValue(shGrade, "gStrength", mode == "night" and 0.9 or 0.0)
    end
end)

addEventHandler("onClientResourceStop", resourceRoot, function()
    for _, s in ipairs({ shWindow, shOcean, shTerrain, shGrade }) do
        if s and isElement(s) then destroyElement(s) end
    end
    if screenSrc and isElement(screenSrc) then destroyElement(screenSrc) end
end)
