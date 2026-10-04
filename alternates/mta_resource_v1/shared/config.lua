--[[
    config.lua — إعدادات مشتركة (سيرفر + عميل)
    Castle & Palace — مدينة القلعة الساحلية
]]

CASTLE = {}

-- ======== معرّفات الموديلات ========
-- إن كان سيرفرك على MTA 1.6+ نستخدم engineRequestModel لمعرّفات حرة،
-- وإلا نستبدل موديلات GTA أصلية غير مستخدمة (القيم أدناه احتياطية).
CASTLE.MODELS = {
    main   = { id = 15000, col = "models/castle_city.col", dff = "models/castle_city.dff", txd = "models/castle_city.txd" },
    lod1   = { id = 15001, dff = "models/city_lod1.dff" },
    lod2   = { id = 15002, dff = "models/city_lod2.dff" },
    lod3   = { id = 15003, dff = "models/city_lod3.dff" },
}

-- احتياطي: موديلات GTA أصلية تُستبدل عند عدم دعم engineRequestModel
CASTLE.FALLBACK_IDS = { main = 3524, lod1 = 3525, lod2 = 3526, lod3 = 3527 }

-- ======== الموضع في العالم ========
-- ضع المدينة حيث تريد (مثال: جزيرة قبالة سان أندرياس). القمة في هذا الموديل عند Z = 110م.
CASTLE.ORIGIN    = { x = 1500.0, y = -2600.0, z = 0.0 }
CASTLE.ROTATION  = { 0, 0, 0 }

-- ======== مسافات LOD ========
CASTLE.LOD = {
    near    = 320,    -- المسافة التي يظهر فيها الموديل التفصيلي كاملًا
    lod1    = 700,    -- أول مستوى مختصر
    lod2    = 1400,
    lod3    = 2600,
    farclip = 3400,
}

-- ======== الإضاءة ========
CASTLE.LIGHT = {
    maxLights      = 32,       -- الحد الأقصى للمصابيح في الشيدر (القريبة من اللاعب)
    updateRateMs   = 120,      -- معدّل تحديث الإضاءة
    glowRange      = 90,       -- مدى رسم هالات الضوء
    dayFogDistance = 900,
    nightFogDistance = 420,
    torchColor     = { 1.00, 0.62, 0.26 },
    lampColor      = { 1.00, 0.76, 0.42 },
    windowColor    = { 1.00, 0.72, 0.38 },
    beaconColor    = { 1.00, 0.88, 0.58 },
}

-- ======== أوقات النهار/الليل ========
CASTLE.TIME = {
    dayStartHour   = 7,
    nightStartHour = 19,
    dayTime        = { 12, 30 },
    nightTime      = { 0, 15 },
    minuteDuration = 60000,     -- 60000ms = دقيقة لعب حقيقية لكل دقيقة لعبة
}

-- ======== مناطق القلعة (تسميات + نقاط) ========
CASTLE.ZONES = {
    palace_cathedral = "القصر والكاتدرائية",
    upper_courtyard  = "الساحة العليا",
    main_gate        = "البوابة البحرية",
    wall_walks       = "الأبراج والمتاريس",
    mid_town         = "المدينة الوسطى",
    market           = "سوق المدينة",
    harbour          = "المرفأ",
    causeway         = "الجسر المقوّس",
    royal_gardens    = "الحدائق الملكية",
    lighthouse       = "المنارة",
    waterfalls       = "الشلالان",
}
