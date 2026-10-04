--[[
    config.lua — إعدادات مشتركة (Castle & Palace)
    تُقرأ من السيرفر والعميل.
]]

CASTLE = {
    -- ===== الهوية =====
    resource   = "castle",
    modelBase  = 19000,          -- أول معرّف موديل نستخدمه (قابل للتعديل)
    parts      = {},             -- تُملأ في main.lua حسب عدد الأجزاء

    -- ===== الوقت والإضاءة =====
    dayHour    = 12,
    nightHour  = 0,
    autoTime   = true,           -- تبديل تلقائي عند 7 و19
    dayStart   = 7,
    nightStart = 19,
    autoTick   = 30000,          -- كل 30 ثانية
    maxLights  = 7,              -- أقصى عدد أضواء حقيقية (createLight) في نفس اللحظة
    shaderLights = 32,           -- ★ أضواء الشيدر النقطية لكل بكسل (pointlight.fx) — بلا حدّ MTA
    glowRange  = 420,            -- مدى رسم هالات المصابيح (متر)

    -- ===== LOD =====
    -- 7 أجزاء × 4 مستويات (تنتجها tools/make_lod.py إلى models/parts و models/lod)
    parts = { "palace", "walls", "town", "harbour", "causeway", "cliff", "interiors" },
    lod = {
        { level = 1, name = "high",    distance = 320,  path = "models/parts/%s.dff"       },
        { level = 2, name = "medium",  distance = 850,  path = "models/lod/%s_medium.dff"  },
        { level = 3, name = "low",     distance = 1800, path = "models/lod/%s_low.dff"     },
        { level = 4, name = "distant", distance = 4200, path = "models/lod/%s_distant.dff" },
    },

    -- ===== مصفوفة الإضاءة الليلية =====
    -- النوع: "window" = نافذة مضيئة | "lamp" = فانوس | "torch" = مشعل | "brazier" = منقل
    lights = {
        -- (الموضع، النوع، نصف القطر، اللون، الشدة)
        { x = 0,    y = -60,  z = 132, kind = "torch",   radius = 22, color = {255, 150, 60},  intensity = 1.0 },
        { x = 62,   y = -8,   z = 112, kind = "lamp",    radius = 18, color = {255, 190, 110}, intensity = 0.9 },
        { x = -62,  y = -8,   z = 112, kind = "lamp",    radius = 18, color = {255, 190, 110}, intensity = 0.9 },
        { x = 36,   y = -78,  z = 96,  kind = "window",  radius = 14, color = {255, 196, 120}, intensity = 0.8 },
        { x = -30,  y = -70,  z = 96,  kind = "window",  radius = 14, color = {255, 196, 120}, intensity = 0.8 },
        { x = 96,   y = -180, z = 34,  kind = "torch",   radius = 20, color = {255, 140, 55},  intensity = 1.0 },
        { x = 196,  y = -256, z = 40,  kind = "brazier", radius = 26, color = {255, 130, 45},  intensity = 1.1 },
        { x = -180, y = -230, z = 26,  kind = "torch",   radius = 20, color = {255, 140, 55},  intensity = 1.0 },
        { x = 246,  y = -184, z = 44,  kind = "brazier", radius = 30, color = {255, 170, 80},  intensity = 1.2 },
        { x = 60,   y = -150, z = 60,  kind = "window",  radius = 12, color = {255, 196, 120}, intensity = 0.7 },
        { x = -40,  y = -140, z = 60,  kind = "window",  radius = 12, color = {255, 196, 120}, intensity = 0.7 },
    },

    -- ===== الفكسات =====
    fx = {
        waterfalls = {                       -- الشلالان (تمويه + رشّاش + دخان ماء)
            { x = -168, y = -166, z = 74, h = 62 },
            { x = -138, y = -232, z = 47, h = 38 },
        },
        birdCount   = 26,                    -- طيور بحر
        seaFoamCount= 40,                    -- رغوة قرب الصخور
        smokeStacks = {                      -- مداخن المدينة
            { x = 84,  y = -118, z = 96 },
            { x = -62, y = -104, z = 82 },
            { x = 128, y = -172, z = 62 },
            { x = -20, y = -196, z = 40 },
        },
        flagCount   = 8,
    },

    -- ===== الداخليات (14 منطقة كما في لوحة المشروع) =====
    interiors = {
        { id = 1,  name = "main_gatehouse",   x = 196, y = -256, z = 18,  iw = 40,  ih = 12, ihh = 6  },
        { id = 2,  name = "inner_courtyard",  x = 30,  y = -30,  z = 112, iw = 60,  ih = 50, ihh = 14 },
        { id = 3,  name = "state_corridor",   x = 0,   y = -70,  z = 118, iw = 42,  ih = 10, ihh = 5  },
        { id = 4,  name = "kings_bedchamber", x = -30, y = -60,  z = 120, iw = 18,  ih = 16, ihh = 5  },
        { id = 5,  name = "great_library",    x = 30,  y = -60,  z = 120, iw = 22,  ih = 18, ihh = 7  },
        { id = 6,  name = "dungeons",         x = 0,   y = 40,   z = 86,  iw = 30,  ih = 12, ihh = 4  },
        { id = 7,  name = "great_dining_hall",x = -10, y = -50,  z = 121, iw = 34,  ih = 16, ihh = 8  },
        { id = 8,  name = "kitchens",         x = 40,  y = -20,  z = 110, iw = 20,  ih = 14, ihh = 5  },
        { id = 9,  name = "armoury",          x = -40, y = -20,  z = 110, iw = 18,  ih = 14, ihh = 5  },
        { id = 10, name = "guest_chamber",    x = -20, y = -78,  z = 118, iw = 16,  ih = 14, ihh = 5  },
        { id = 11, name = "royal_gardens",    x = 62,  y = -22,  z = 98,  iw = 70,  ih = 50, ihh = 8  },
        { id = 12, name = "tower_interior",   x = 70,  y = -6,   z = 110, iw = 16,  ih = 16, ihh = 40 },
        { id = 13, name = "secret_passages",  x = 10,  y = 20,   z = 80,  iw = 60,  ih = 6,  ihh = 4  },
        { id = 14, name = "vaults_cellars",   x = -10, y = 30,   z = 74,  iw = 34,  ih = 18, ihh = 5  },
    },
    interiorOffset = { x = 0, y = 6000, z = 0 },   -- منطقة الداخليات بعيدة عن العالم المفتوح
}

-- ألوان لوحة المشروع (تُستخدم في الواجهة والخرائط)
CASTLE_PALETTE = {
    sandstone = { 0.80, 0.69, 0.52 },
    granite   = { 0.44, 0.44, 0.45 },
    slate     = { 0.29, 0.32, 0.36 },
    terracotta= { 0.68, 0.44, 0.29 },
    water     = { 0.13, 0.34, 0.40 },
    banner    = { 0.55, 0.16, 0.16 },
    gold      = { 0.85, 0.68, 0.30 },
}
