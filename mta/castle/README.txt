================================================================================
  Castle & Palace — مورد MTA:SA كامل
  مدينة القلعة الساحلية (قصر/كاتدرائية + 3 حلقات أسوار + 6 مصاطب + مرفأ + جسر)
================================================================================

  المحتويات
  ---------
  meta.xml                تعريف المورد وكل ملفاته
  shared/config.lua       الإعدادات (معرّفات الموديل، LOD، الإضاءة، الأوقات، المناطق)
  server/s_time.lua       وقت اليوم + مزامنة حالة الإضاءة لكل اللاعبين
  server/s_commands.lua   أوامر الأدمن: /castletime و /castlegoto
  client/loader.lua       تحميل COL→TXD→DFF + سلسلة LOD (4 مستويات)
  client/lighting.lua     نظام الإضاءة: نهار/ليل + 32 مصدر ضوء نقطي + هالات
  client/gameplay.lua     النقل بين المناطق (/castle) + أسماء المناطق على الشاشة
  client/hud.lua          شاشة تحميل + معلومات الموقع/الإضاءة + /castle_time
  shaders/pointlight.fx   ★ شيدر الإضاءة النقطية (Ambient + Lambert + انحلال مزدوج)
  shaders/glow.fx         شيدر هالات الضوء (مشاعل/فوانيس/منارة)
  data/lamps.json         مواضع المصابيح المستخرجة من الموديل (83 مصدر ضوء)
  data/spawns.json        نقاط اللعب المستخرجة من الموديل
  data/parts.json         إحصاءات الهندسة وخطة LOD
  models/                 ← ضع هنا DFF/TXD/COL بعد التحويل (انظر أدناه)
  textures/               خامات PBR الجاهزة (23 خامة)


  التثبيت
  -------
  1) انسخ مجلد "castle" إلى:  server/mods/deathmatch/resources/
  2) شغّل:                    /start castle          (أو أضف <resource src="castle"/> في acl)
  3) انسخ مجلد data + textures من المستودع (أو شغّل tools/install_mta_assets.py) إن لم تكن موجودة.
  4) للعب:  /castle harbour   |   الأدمن: /castletime night


  ★ تحويل الموديل إلى DFF/TXD/COL
  --------------------------------
  الموديل المولَّد: build/castle_city.obj (46,604 وجه، 65,453 رأس، 33 مادة)
  المطلوب لمحرك MTA: DFF + TXD + COL
  الطرق المتاحة (أي واحدة):
    • Blender:  استورد OBJ → صدّر DFF عبر إضافة "DragonFF" أو "RenderWare GTA" (DFF+COL).
    • 3ds Max:  استورد OBJ → استخدم "KAM's GTA Scripts" (DFF + COL + TXD).
    • الأدوات:  G-TXD لبناء TXD من صور PNG (استخدم ملفات textures/*_albedo.png).
  بعد التحويل ضع الملفات في models/ بنفس الأسماء الموجودة في meta.xml:
      castle_city.dff | castle_city.txd | castle_city.col
      city_lod1.dff   | city_lod2.dff   | city_lod3.dff     (تقليل بالمثلثات للنسب في data/parts.json)
  ملاحظة: إن لم تصنع TXD، يمكن إبقاء الخامات تُطبَّق عبر الشيدر (النظام يدعم الحالتين).


  ★ نظام الإضاءة القوي (من الفوانيس)
  ----------------------------------
  1) شيدر pointlight.fx يُطبَّق على خامات الموديل: mat_*, stone_*, roof_*, plaster_*,
     wood_*, rock_*, terrain_*, metal_*, fabric_*, marble_*
  2) يُمرَّر إليه كل 120ms أقرب 32 مصدر ضوء (من 83 موضعًا مستخرجًا من الموديل):
         gLightPos[32] (xyz + المدى) | gLightColor[32] | gLightParams[32] | gLightCount
  3) أنواع المصابيح: torch (مشعل بارتعاش 9Hz)، lamp (فانوس شارع)، beacon (منارة بنبض 1.7Hz)
  4) نموذج الإضاءة: Ambient + Lambert نصف-ناعم + انحلال مزدوج + تشبّع ناعم
  5) نهار/ليل: setSunColor + setSkyGradient + setWaterColor + الضباب + gAmbient (متغيّر بالشيدر)
  6) هالات مرئية: glow.fx عبر dxDrawMaterialLine3D لكل مصدر داخل 90م


  الأوامر
  -------
  /castle <منطقة>          انتقال سريع (عميل)
  /castle_time day|night    تبديل محلي للإضاءة
  /castletime day|night|auto  تبديل عالمي (أدمن)
  /castlegoto <منطقة>       نقل لاعب (أدمن)


  متطلبات
  -------
  MTA:SA 1.6.0+  (شيدر ps_3_0 + engineApplyShaderToWorldTexture + setLowLODElement)
================================================================================
