# Texture Prompt Sheet — PBR 4K Masters
### Castle Aldurn — حزمة الخامات التي ستولّدها بالـAI

> **مهم:** هذه الصفحة تُسلَّم لمولّد الخامات (أو مصمم الخامات). بعد التوليد تضع الملفات في المستودع `saradztn/castle` داخل المجلد `textures/src/` بالأسماء المذكورة حرفيًا، وأنا أتولّى تلقائيًا: المعالجة، الـMipmaps، الضغط DXT1/DXT3/DXT5، بناء TXD، والربط على UVs النموذج.

---

## 1. قواعد التسليم (Delivery Spec — إلزامية)

| البند | المواصفة |
|---|---|
| الخامة الرئيسية | **4096 × 4096 px PNG** (المasters؛ سأنزّلها أنا إلى 2048/1024 للـLOD وTXD) |
| الصيغة | PNG، 8-bit لكل قناة، بلا ضغط مفقود، بلا حدود/إطارات/علامة مائية |
| Albedo (Base Color) | sRGB — **بلا أي إضاءة محفورة، بلا ظلال، بلا AO**، قيمة رمادية متوسطة (ليست سوداء ولا بيضاء) |
| Normal | **Linear (Raw)**، ترميز DirectX/OpenGL — أرسلها **OpenGL (+Y up)** إن أمكن وإلا أخبرني بالترميز |
| Roughness | **Linear (Raw)** — grayscale، تباين كامل 0–255 |
| AO | **Linear (Raw)** — grayscale، Ambient Occlusion نظيف فقط (ظلال الفجوات الضيقة) |
| Height/Displacement | Optional — grayscale، للمزاريب والفواصل بين الحجارة |
| التكرار (Tiling) | **Seamless 100% على الحواف الأربعة** (ما عدا الخامات المعلّمة `non-tiling`) |
| مقياس البلاطة | مذكور لكل خامة `tile_m` — يجب أن يكون حجم العناصر الحقيقي مطابقًا (مثال: بلاطة الحجر 4 م تعني أن الحجر الواحد 60×30 سم) |
| وحدة الأسلوب | **نفس شدة التلف والأوساخ في كل الخامات** — نفس "طقس" القلعة: مطر معتدل، طحالب خفيفة، بلا صحراء وبلا استوائي |
| التسمية | `<id>_<map>.png` مثال: `stone_ashlar_wall_albedo.png` |
| المجلد | `textures/src/` |

### الوحدة الأسلوبية (Style Lock) — أضفها إلى نهاية كل برومبت

```text
photorealistic scanned material, high-medieval European castle at temperate climate, consistent weathering level across the whole set: light moss growth in recesses, mild water staining, matte weathered surfaces, no fresh damage, no mud, no tropical or desert look.
```

### البرومبت السلبي الموحّد (Negative — استخدمه دائمًا)

```text
baked shadows, baked lighting, ambient occlusion in albedo, strong highlights, vignette, border, frame, watermark, text, logo, perspective distortion, non-seamless edges, visible tile repetition, image of an object, product shot, cartoon, painting, illustration, low resolution, blurry, noisy, oversaturated, HDR glow, lens flare, depth of field
```

### البادئة الموحّدة للخامات القابلة للتكرار

```text
Seamless tileable PBR material texture, perfectly seamless on all four edges, flat orthographic top-down view, even diffuse lighting, no shadows, no specular highlights, no perspective, 4096x4096, sharp micro-detail.
```

---

## 2. المستويات (Tiers) — لتوزيع الجهد

| Tier | المحتوى | عدد الخامات |
|---|---|---|
| **1 — أساسي** | كل ما يُرى من الخارج: الحجر، الأردواز، الخشب، الحديد، الحجر البلاطي، العشب | 12 |
| **2 — داخلي وثانوي** | أرضيات، جص، جرف صخري، مسار، زجاج، راية | 9 |
| **3 — تفاصيل وجو** | Decals (طحالب، تسرّب ماء، شقوق، سخام)، شبك حديد، جلد/أثاث، معدن مذهّب | 7 |

> إن أردت تقليص الجهد: **Tier 1 + Albedo/Normal فقط** يكفي لإنتاج أول تجربة لعب، والباقي يُضاف لاحقًا.

---

## 3. جدول الخامات الكامل

| # | المعرّف `id` | Tier | tile_m | النوع | الخرائط | الاستخدام في الموديل |
|---|---|---|---|---|---|---|
| 1 | `stone_ashlar_wall` | 1 | 4.0 | tiling | albedo, normal, roughness, ao, height | الأسوار، الأبراج، الحصن، الجدران الخارجية |
| 2 | `stone_rubble_wall` | 1 | 4.0 | tiling | albedo, normal, roughness, ao, height | قواعد الجدران، أسافل الأبراج، الترميمات |
| 3 | `stone_trim_ashlar` | 1 | 2.0 | tiling | albedo, normal, roughness, ao | الأفاريز، الحواف، إطارات النوافذ، الدعامات، الشرفات |
| 4 | `stone_ashlar_soot` | 1 | 4.0 | tiling | albedo, normal, roughness, ao | ممر البوابة، قرب المشاعل، داخل المداخن |
| 5 | `roof_slate` | 1 | 3.0 | tiling | albedo, normal, roughness, ao | أسقف الأبراج، القصر، الإصطبل، مظلة البئر |
| 6 | `roof_tile_clay` | 1 | 3.0 | tiling | albedo, normal, roughness, ao | مظلة البئر، امتدادات خدمية |
| 7 | `wood_oak_door` | 1 | 2.0 | tiling (رأسي) | albedo, normal, roughness, ao | أبواب البوابة، أبواب القصر، أبواب الإصطبل |
| 8 | `wood_beam_oak` | 1 | 2.0 | tiling | albedo, normal, roughness, ao | الجسر المتحرك، المظلة، الجسور الداخلية، الجوائز |
| 9 | `metal_iron_forged` | 1 | 2.0 | tiling | albedo, normal, roughness, ao | البوابة الحديدية، الأحزمة، المفصلات، حامل المشاعل |
| 10 | `metal_copper_verdigris` | 1 | 2.0 | tiling | albedo, normal, roughness, ao | حواف الأسقف، المزاريب، النقاط العلوية |
| 11 | `stone_cobble_courtyard` | 1 | 4.0 | tiling | albedo, normal, roughness, ao, height | فناء القلعة، الممرات الخارجية |
| 12 | `grass_terrain` | 1 | 8.0 | tiling | albedo, normal, roughness, ao | الرابية والمنحدرات |
| 13 | `stone_flagstone_floor` | 2 | 4.0 | tiling | albedo, normal, roughness, ao | أرضيات الحصن والقصر والقاعة |
| 14 | `plaster_lime_wall` | 2 | 4.0 | tiling | albedo, normal, roughness, ao | الجدران الداخلية البيضاء |
| 15 | `wood_plank_floor` | 2 | 4.0 | tiling | albedo, normal, roughness, ao | أرضيات خشبية داخلية |
| 16 | `wood_plank_weathered` | 2 | 2.0 | tiling | albedo, normal, roughness, ao | مصاريع، أبواب ثانوية، صناديق |
| 17 | `rock_outcrop_cliff` | 2 | 8.0 | tiling | albedo, normal, roughness, ao | الجرف الصخري تحت السور الشرقي/الجنوبي |
| 18 | `dirt_gravel_path` | 2 | 4.0 | tiling | albedo, normal, roughness, ao | المسار المؤدي للجسر |
| 19 | `glass_leaded_pane` | 2 | 1.0 | tiling | albedo(+alpha), normal, roughness | نوافذ القصر والحصن، **نسخة إضافية مضيئة للّيل** |
| 20 | `glass_stained_rose` | 2 | — | **non-tiling** | albedo(+alpha), normal, roughness | نافذة الوردة في الكنيسة (قطر 3 م) |
| 21 | `fabric_banner_heraldry` | 2 | — | **non-tiling** | albedo(+alpha), normal, roughness | الرايات والبيارق — الوجهان |
| 22 | `decal_moss_patch` | 3 | 2.0 | decal (alpha) | albedo+alpha, normal | على الحجر والأردواز |
| 23 | `decal_water_streak` | 3 | 2.0 | decal (alpha) | albedo+alpha, normal | تحت الأفاريز وعتبات النوافذ |
| 24 | `decal_stone_crack` | 3 | 2.0 | decal (alpha) | albedo+alpha, normal | شقوق موضعية على الجدران |
| 25 | `decal_soot_grime` | 3 | 2.0 | decal (alpha) | albedo+alpha, roughness | فوق المشاعل والمداخل |
| 26 | `metal_iron_grille` | 3 | 1.0 | decal (alpha) | albedo+alpha | شبكات النوافذ والأقواس |
| 27 | `metal_gilded_bronze` | 3 | 2.0 | tiling | albedo, normal, roughness, ao, metalness | شعار القلعة النحاسي المذهّب فوق البوابة، زخارف المذبح |
| 28 | `fabric_tapestry` | 3 | — | **non-tiling** | albedo(+alpha), normal, roughness | جدارية القاعة الكبرى |
| 29 | `wood_props_kit` | 3 | 4.0 | tiling | albedo, normal, roughness, ao | أثاث، براميل، طاولات، ألواح |

---

## 4. البرومبتات التفصيلية (جاهزة للنسخ)

### 1) `stone_ashlar_wall` — الحجر الجيري المقطوع
```text
[PREFIX] Weathered grey limestone ashlar masonry wall, large hand-cut rectangular blocks roughly 60 by 30 cm, tight 1.5 cm recessed mortar joints, cool grey stone #9A958C with subtle block-to-block tonal variation between #7E7A72 and #B3ADA2, fine tooling marks on the faces, light moss growth in the joints, mild dark water staining running down from the upper blocks, a few chipped corners, matte finish. [STYLE LOCK]
```

### 2) `stone_rubble_wall` — حجر خشن
```text
[PREFIX] Rough rubble stone wall of irregular undressed field stones in a thick lime mortar bed, stones 15 to 45 cm, greys and grey-browns #6E6A62 to #57544E, deep mortar recesses, encrusted with dirt, small patches of moss and lichen, very matte, heavily weathered. [STYLE LOCK]
```

### 3) `stone_trim_ashlar` — الحجر المشغول الناعم
```text
[PREFIX] Smoothly dressed fine limestone ashlar, tightly jointed, pale warm grey #ABA69C, very fine grain, subtle chisel marks, slightly lighter than the main wall stone, small weathered pits and faint dark streaks, matte with a faint satin sheen. [STYLE LOCK]
```

### 4) `stone_ashlar_soot` — نسخة مدخّنة
```text
[PREFIX] Soot-darkened limestone ashlar wall from a medieval gate passage and torch-lit corridor, same coursing as a clean ashlar wall but grey-black smoke staining concentrated in the upper areas and around joint lines, soot fading toward the bottom, light greasy sheen from centuries of handling. [STYLE LOCK]
```

### 5) `roof_slate` — أردواز
```text
[PREFIX] Dark blue-grey slate roof shingles in overlapping horizontal courses with a traditional graduated pattern, individual slates 30 by 20 cm, colour between #2C3137 and #4A525B with occasional rusty-brown and green-grey variation, thin slate edges, faint moss and lichen at the overlaps and near the eaves, slight surface sheen where the rain polishes the stone. [STYLE LOCK]
```

### 6) `roof_tile_clay` — قرميد طيني
```text
[PREFIX] Weathered terracotta roof tiles in overlapping courses, slightly irregular hand-made barrel tiles #8C5A43 with variation to #6E4433 and #A67154, chipped edges, patches of green-grey lichen, thin mortar lines showing between tiles, matte and dusty. [STYLE LOCK]
```

### 7) `wood_oak_door` — خشب البلوط للأبواب
```text
[PREFIX] Vertical oak door planks, eight planks of about 25 cm width per 2 m, dark aged oak #5C4128 with variation to #7A5A38, pronounced vertical grain, hand-hewn surface, fine longitudinal cracks and old nail holes, matte oiled finish, subtle cup and shadow where planks meet. [STYLE LOCK]
```
> **ملاحظة:** يجب أن تكون الألياف رأسية في الصورة (سيتم استخدامها عموديًا على الأبواب).

### 8) `wood_beam_oak` — العوارض
```text
[PREFIX] Rough-sawn structural oak timber surface, adze-hewn, medium brown #6B4A2F with grey weathering and darker #4C3524 tones, strong straight grain, knots, checks and old mortise holes, dusty matte finish. [STYLE LOCK]
```

### 9) `metal_iron_forged` — حديد مطروق
```text
[PREFIX] Blackened hand-forged wrought iron surface, near-black #2A2A2C with faint blue-grey sheen, visible hammer marks and scale, pitting, light orange-brown surface rust in recesses and around rivets, slightly uneven and hand-made, semi-matte metal. [STYLE LOCK]
```

### 10) `metal_copper_verdigris` — نحاس مؤكسد
```text
[PREFIX] Oxidized copper sheet and strip with verdigris patina, deep green #4E8A72 blending into teal and dark brown #4A3A2A in sheltered areas, streaky run-off staining, small polished bright copper spots on the raised edges, matte to satin metal. [STYLE LOCK]
```

### 11) `stone_cobble_courtyard` — الحجر البلاطي
```text
[PREFIX] Courtyard cobblestone paving of rounded field stones 10 to 20 cm set in packed sand and lime, tones from #7C766B to #5F5A52 with occasional reddish-brown stones, wide sandy joints, worn smooth in the walking lines, patches of moss and dark damp staining in the low areas, subtle puddle-darkened spots. [STYLE LOCK]
```

### 12) `grass_terrain` — العشب
```text
[PREFIX] Temperate meadow grass ground, dense short green blades #5E6B3A with darker and lighter patches, clumps of moss, small stones and patches of bare brown earth, tiny wildflowers, viewed from directly above, even diffuse daylight, no shadow. [STYLE LOCK]
```

### 13) `stone_flagstone_floor`
```text
[PREFIX] Worn medieval limestone floor slabs, large irregular flagstones 60 to 120 cm, pale grey-beige #8E887D with darker worn traffic lanes, chipped edges, dust and grit in the joints, faint polish from centuries of footsteps, no gloss, even diffuse light. [STYLE LOCK]
```

### 14) `plaster_lime_wall`
```text
[PREFIX] Interior lime-plastered wall, hand-applied whitewash #D8D2C4 with subtle trowel undulation, faint warm and cool blotches, small hairline cracks and a few patches where the plaster has fallen away to reveal stone beneath, dusty matte, no gloss. [STYLE LOCK]
```

### 15) `wood_plank_floor`
```text
[PREFIX] Old oak plank floorboards, boards 20 to 25 cm wide laid along one direction, warm honey-brown #8A6238 with darker grain lines, nail heads, waxed satin sheen, light traffic wear, dust in the joints. [STYLE LOCK]
```

### 16) `wood_plank_weathered`
```text
[PREFIX] Weathered silver-grey exterior wood boards, sun-bleached and rain-washed #8A8378, strong cracking and raised grain, dark streaks below nail lines, matte dry surface. [STYLE LOCK]
```

### 17) `rock_outcrop_cliff`
```text
[PREFIX] Natural bedrock outcrop surface, layered grey limestone and dark grey-brown rock #6B655C, horizontal strata, deep fractures and fissures, dry patches mixed with damp dark areas, lichen spots, small moss in the cracks, no vegetation, top-down rock face. [STYLE LOCK]
```

### 18) `dirt_gravel_path`
```text
[PREFIX] Trodden gravel and dirt path, compacted light brown earth with small grey stones, wheel ruts, patches of mud and scattered leaves, scattered moss along the edges, matte dry surface. [STYLE LOCK]
```

### 19) `glass_leaded_pane`
```text
[PREFIX, non-tiling] Medieval leaded window glazing, small diamond quarries of slightly irregular hand-blown glass in pale green-grey #8FA39B with visible bubbles and waviness, thick dark grey lead cames forming a diamond lattice, dirty at the edges, mild dust film, even diffuse light from behind, matte glass. [STYLE LOCK]
```
> + نسخة ليلية: نفس الخامة مع **`emissive`** (لون `#FFB25E` متوسط) باسم `glass_leaded_pane_emissive_albedo.png`.

### 20) `glass_stained_rose` — **non-tiling**
```text
Medieval stained glass rose window, radial circular design 1:1, twelve petal segments of deep blue #2F4E8C, deep crimson #8C2F35, emerald green #2F6B4A and amber gold #C8A24A, central medallion with a simple geometric rosette, thick black lead lines, hand-blown glass with bubbles, backlit by even diffuse light, entirely geometric and non-figurative, full bleed circular composition centred in the image, no border, no background scenery.
```

### 21) `fabric_banner_heraldry` — **non-tiling**
```text
Medieval woven heraldic banner cloth, tall 1 by 3 composition, deep crimson field #6E1B22 with a golden crenellated stone tower with an open arched gateway as the central charge, a single gold chevron below, subtle woven wool and linen texture with visible warp and weft, gentle vertical wind creases, slightly faded and dusty, no text, no letters, full bleed, no border.
```

### 22) `decal_moss_patch`
```text
[PREFIX, decal with alpha] Irregular patch of moss and lichen growth for stone walls, dark green #3F5B2E to yellowish #6E7A3A, soft fuzzy cluster shapes spreading from a centre, thin frayed edges, isolated on a plain white background for alpha extraction, top-down flat.
```

### 23) `decal_water_streak`
```text
[PREFIX, decal with alpha] Vertical dark water run-off staining for masonry, translucent grey-brown streaks starting from a horizontal line at the top and tapering downward, edges feathered, varied opacity, isolated on a plain white background for alpha extraction.
```

### 24) `decal_stone_crack`
```text
[PREFIX, decal with alpha] Set of hairline and medium stone cracks, irregular branching fracture lines, dark grey-brown, thin at the ends, subtle shadow in the deeper cracks, isolated on a plain white background for alpha extraction, top-down flat.
```

### 25) `decal_soot_grime`
```text
[PREFIX, decal with alpha] Soot and grime stain above a torch bracket, soft black-grey soot plume spreading upward with a greasy edge, mottled opacity, isolated on a plain white background for alpha extraction.
```

### 26) `metal_iron_grille`
```text
[PREFIX, decal with alpha] Wrought iron window grille pattern, vertical bars with horizontal cross bracing and rivets, black hand-forged iron, seen flat-on, bars only with transparent gaps, isolated on a plain white background for alpha extraction.
```

### 27) `metal_gilded_bronze`
```text
[PREFIX] Gilded bronze heraldic ornament surface, warm gold #C8A24A over bronze with dark patina #6B5A32 in the recesses, worn gilding showing bronze beneath, fine tooled texture, matte antique gold, no bright modern polish. [STYLE LOCK]
```

### 28) `fabric_tapestry` — **non-tiling**
```text
Medieval woven wall tapestry, horizontal composition, muted wool dyes — deep red #7A2B2B, forest green #3E5548, gold #C8A24A, indigo #2F3E6B — a stylised geometric and floral border framing a central simple motif of a crenellated tower, coarse weaving with visible weft, slightly faded, dusty and with a few repaired threads, no text, no human faces, full bleed, no border.
```

### 29) `wood_props_kit`
```text
[PREFIX] Interior oak furniture and prop surface, well-worn dark oak #5A3E27 with visible grain, scratches, ring marks from cups, small dents and dings, waxed satin finish, dusty in the details. [STYLE LOCK]
```

---

## 5. ملاحظات فنية (لماذا هذه القيود)

1. **بلا AO في الألبيو:** سأعطي كل قطعة هندسية UVs حقيقية، وAO يأتي من الخرائط نفسها ومن إضاءة MTA — حرق الظلال يجعل الموديل يبدو مسطحًا.
2. **Seamless إلزامي:** الجدران ستُبلَّط كثيرًا (كل 4 م)، أي خط في الحواف سيتكرر مئات المرات ويُفسد المنظر.
3. **4K → 2K/1K:** في MTA سأبني TXD بضغط DXT1/5 مع mipmaps، فالمصدر 4K يعطيني جودة عند الاقتراب مع أداء جيد.
4. **حجم العناصر الحقيقي:** إذا ظهر الحجر في الصورة بحجم 30×60 سم عند بلاطة 4 م من الفضاء، فهذا يعني ~13×7 حجرًا في الصورة — احترم هذا العدد لتتطابق النسب مع الصورة المرجعية.
5. **Normal OpenGL (+Y up):** أخبرني إن كانت أداة التوليد تُخرج DirectX — سأقلب القناة الخضراء تلقائيًا.
6. **خامات non-tiling:** تُسلَّم بأبعاد البطاقة كما هي (بدون تكرار)، وتُستخدم مرة واحدة.
