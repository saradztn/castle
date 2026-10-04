# Texture Prompt Sheet — PBR 4K Masters
### Castle & Palace (مدينة القلعة الساحلية) — حزمة الخامات مطابقة للوحة الخامات في المرجع

> **مهم:** أنت (أو المصمم) تولّد الخامات، وتضعها في `textures/src/` بالأسماء أدناه، وأنا أتولّى: المعالجة، الـMipmaps، الضغط DXT1/3/5، بناء TXD لكل مستوى LOD، والربط على UVs النموذج.

---

## 1. قواعد التسليم (إلزامية)

| البند | المواصفة |
|---|---|
| المقاس الرئيسي | **4096 × 4096 PNG** (سأنزل أنا 2048 / 1024 / 512 / 256 لمستويات LOD وTXD) |
| القنوات | `albedo` (sRGB بلا إضاءة/ظلال/AO محفور) · `normal` (Linear, **OpenGL +Y up**) · `roughness` (Linear) · `ao` (Linear) · `height` (اختياري) · `alpha` للعناصر الشفافة |
| التكرار | **Seamless 100%** لكل الخامات ما عدا المعلّمة `non_tiling` |
| مقياس البلاطة | `tile_m` مذكور لكل خامة — التزم بحجم العناصر الحقيقي داخل الصورة (حجر 60×30 سم داخل بلاطة 4 م ≈ 13×7 حجرًا) |
| وحدة الأسلوب | مناخ **بحري معتدل**: طحالب خفيفة، ملح على الحجر قرب البحر، أوساخ مائية، تلف خفيف موحّد في كل الحزمة (لا صحراء، لا استوائي) |
| التسمية | `<id>_<map>.png` — مثال `stone_sandstone_ashlar_albedo.png` في مجلد `textures/src/` |

**Style Lock — أضفه لنهاية كل برومبت خامات:**
```text
photorealistic scanned material, temperate maritime climate, consistent weathering across the whole set: light moss in recesses, faint salt bloom near the sea, mild water staining, matte weathered surfaces, no fresh damage, no mud, no tropical look.
```

**Negative الموحّد:**
```text
baked shadows, baked lighting, AO in albedo, strong highlights, vignette, border, frame, watermark, text, logo, perspective distortion, non-seamless edges, visible tiling repetition, object shot, product photo, cartoon, painting, illustration, blurry, noisy, oversaturated, HDR glow, lens flare, depth of field
```

**البادئة القياسية (للخامات المتكرّرة):**
```text
Seamless tileable PBR material texture, perfectly seamless on all four edges, flat orthographic top-down view, even diffuse lighting, no shadows, no specular highlights, no perspective, 4096x4096, sharp micro-detail.
```

---

## 2. جدول الخامات (29 خامة — مطابقة للوحة الخامات في المرجع + ما تتطلبه المدينة)

### Tier 1 — العمارة الخارجية (أساسي)
| # | `id` | tile_m | الخرائط | الاستخدام |
|---|---|---|---|---|
| 1 | `stone_sandstone_ashlar` | 4.0 | albedo, normal, roughness, ao, height | القصر والكاتدرائية والحلقة العليا |
| 2 | `stone_granite_wall` | 4.0 | albedo, normal, roughness, ao, height | الحلقتان الوسطى والسفلى، الأبراج، الجسور |
| 3 | `stone_seaweathered_mossy` | 4.0 | albedo, normal, roughness, ao | الأسافل، الحوائط المواجهة للبحر، المرفأ |
| 4 | `plaster_lime_town` | 4.0 | albedo, normal, roughness, ao | جدران بيوت المدينة |
| 5 | `stone_quay_granite` | 4.0 | albedo, normal, roughness, ao, height | الأرصفة، الدعامات، درج الماء |
| 6 | `stone_cobble_street` | 4.0 | albedo, normal, roughness, ao, height | الأزقة والساحات |
| 7 | `roof_slate` | 3.0 | albedo, normal, roughness, ao | أسقف الأبراج والقصر والمباني |
| 8 | `roof_tile_terracotta` | 3.0 | albedo, normal, roughness, ao | أسقف مدينة متنوعة |
| 9 | `roof_shingle_wood` | 3.0 | albedo, normal, roughness, ao | أسقف خشبية للمخازن والبيوت الفقيرة |
| 10 | `wood_oak_timber` | 2.0 | albedo, normal, roughness, ao | العوارض، half-timber، الجسور الخشبية |
| 11 | `wood_oak_door` | 2.0 | albedo, normal, roughness, ao | الأبواب (ألياف رأسية) |
| 12 | `rock_cliff_strata` | 8.0 | albedo, normal, roughness, ao | الجرف الطبقي، الصخور |
| 13 | `terrain_grass` | 8.0 | albedo, normal, roughness, ao | المصاطب، القمة، الحدائق |
| 14 | `water_ocean` | 8.0 | albedo, normal, roughness, height | سطح البحر حول الجزيرة |
| 15 | `water_foam_shore` | 4.0 | albedo_alpha, normal | رغوة عند الصخور وشلالات الماء |

### Tier 2 — الزخرفة الداخلية والخامات الثانوية
| # | `id` | tile_m | الخرائط | الاستخدام |
|---|---|---|---|---|
| 16 | `marble_floor_light` | 4.0 | albedo, normal, roughness, ao | أرضيات القاعات والممرات الملكية |
| 17 | `stone_flagstone_floor` | 4.0 | albedo, normal, roughness, ao | الممرات، السجون، الأقبية، البوابات |
| 18 | `wood_plank_floor` | 4.0 | albedo, normal, roughness, ao | الطوابق العلوية، المكتبة |
| 19 | `wood_walnut_panel` | 2.0 | albedo, normal, roughness, ao | تلبيس جدران الغرف الملكية |
| 20 | `fabric_damask_red` | 2.0 | albedo, normal, roughness | ستائر، مفارش، تنجيد — أحمر ملكي مطرّز |
| 21 | `fabric_carpet_woven` | 4.0 | albedo, normal, roughness | السجاد، حصائر الأزقة (نمط هندسي مملوك) |
| 22 | `leather_hide` | 2.0 | albedo, normal, roughness | المفروشات، الدروع، أكياس |
| 23 | `metal_iron_forged` | 2.0 | albedo, normal, roughness, ao | الحديديات، المتاريس، السلاسل، المشاعل |
| 24 | `metal_gilded_bronze` | 1.0 | albedo, normal, roughness, metalness | رؤوس الأبراج، الشعارات، المفصلات الملكية |
| 25 | `metal_copper_verdigris` | 2.0 | albedo, normal, roughness, ao | قمم القباب، المزاريب |
| 26 | `glass_leaded_pane` | 1.0 | albedo_alpha, normal, roughness | كل النوافذ — **+ نسخة `_emissive` للّيل** |
| 27 | `glass_stained_rose` | non-tiling | albedo_alpha, normal, roughness | نافذة الوردة في الكاتدرائية |
| 28 | `fabric_banner_heraldry` | non-tiling | albedo_alpha, normal, roughness | الرايات والبيارق (وجهان) |
| 29 | `terrain_dirt_road` | 4.0 | albedo, normal, roughness, ao | الطرق الترابية، الجسر، مدخل المصاطب |
| 30 | `foliage_leaves` | 2.0 | albedo_alpha, normal | أوراق الأشجار والشجيرات (بطاقات مقطوعة) |

### Tier 3 — Decals وتفاصيل الجو (تُستخدم نُدَبًا فوق الخامات الأساسية)
| # | `id` | tile_m | نوع |
|---|---|---|---|
| 31 | `decal_moss_patch` | 2.0 | albedo_alpha + normal |
| 32 | `decal_salt_bloom` | 2.0 | albedo_alpha + normal |
| 33 | `decal_water_streak` | 2.0 | albedo_alpha + normal |
| 34 | `decal_soot_grime` | 2.0 | albedo_alpha |
| 35 | `decal_stone_crack` | 2.0 | albedo_alpha + normal |
| 36 | `metal_iron_grille` | 1.0 | albedo_alpha |
| 37 | `fabric_tapestry` | non-tiling | albedo_alpha + normal |
| 38 | `wood_props_kit` | 4.0 | albedo, normal, roughness, ao | (براميل، طاولات، صناديق، عجل الرافعة) |

> يمكن البدء بـ **Tier 1 (15 خامة) + albedo/normal** فقط لبناء أول نسخة قابلة للعب.

---

## 3. البرومبتات التفصيلية

**1) `stone_sandstone_ashlar`**
```text
[PREFIX] Warm sandstone ashlar masonry of the palace and cathedral, hand-cut rectangular blocks about 60 by 30 cm laid in regular courses, tight 1.5 cm recessed joints, warm honey-grey #BFA57E with variation to #9C8262 and #D6C29B, fine chisel marks, gentle erosion on the corners, faint water staining under the upper courses, a little moss in the joints, matte weathered surface. [STYLE LOCK]
```

**2) `stone_granite_wall`**
```text
[PREFIX] Course granite curtain-wall masonry, grey blocks 55 by 28 cm with slightly irregular faces, medium 2 cm joints of lime mortar, cool grey #8E8C86 to #6B6963 with darker mineral speckling, chipped edges, light soiling and thin moss lines along the joints, very matte. [STYLE LOCK]
```

**3) `stone_seaweathered_mossy`**
```text
[PREFIX] Sea-weathered stone wall washed by spray, darker grey-brown #6B6963 to #57544E, salt bloom patches, dried seaweed strands and barnacle traces near the bottom, heavy moss and lichen in the joints, waterline tide staining, matte and rough. [STYLE LOCK]
```

**4) `plaster_lime_town`**
```text
[PREFIX] Lime-washed town plaster, warm off-white #D9CFB8 with subtle trowel undulation, small hairline cracks, patches flaking away to reveal stone and brick beneath, dust and rain streaks below the window lines, matte and chalky. [STYLE LOCK]
```

**5) `stone_quay_granite`**
```text
[PREFIX] Harbour quay granite paving and blocks, heavy grey slabs 80 by 60 cm laid in rows, joints filled with sand and grit, dark damp staining, patches of green algae and dried salt, iron mooring-ring rust marks, worn smooth where ropes rub, matte and cool. [STYLE LOCK]
```

**6) `stone_cobble_street`**
```text
[PREFIX] Medieval town street cobbles, rounded stones 8 to 18 cm set in packed sand, tones from #7C766B to #5F5A52 with occasional reddish-brown stones, wide sandy joints, damp dark patches and puddles, worn shiny walking lines down the centre, scattered straw and grit, top-down. [STYLE LOCK]
```

**7) `roof_slate`**
```text
[PREFIX] Dark blue-grey slate roofing in overlapping graduated courses, individual slates about 30 by 20 cm, colour #3A4148 to #4A535C with occasional brown and green-grey slates, thin chipped edges, moss and lichen along the courses and near the eaves, gull droppings, faint rain polish. [STYLE LOCK]
```

**8) `roof_tile_terracotta`**
```text
[PREFIX] Weathered terracotta roof tiles in overlapping courses, hand-made barrel tiles #8C5A43 with variation to #6E4433 and #A67154, chipped edges, green-grey lichen patches, thin mortar lines showing, dust and grit in the overlaps, matte and dusty. [STYLE LOCK]
```

**9) `roof_shingle_wood`**
```text
[PREFIX] Weathered oak roof shingles, small overlapping rectangular wooden tiles 25 by 15 cm, silvered grey-brown #7A6A57 to #5A4B3B, split and curled edges, dark grooves between shingles, moss in the damp spots, matte. [STYLE LOCK]
```

**10) `wood_oak_timber`**
```text
[PREFIX] Structural oak timber beam surface, adze-hewn, warm brown #6B4A2F to darker #4C3524, strong straight grain with knots and old peg holes, fine surface checks, dusty matte finish. [STYLE LOCK]
```

**11) `wood_oak_door`**
```text
[PREFIX] Vertical oak door planks, seven to eight planks of about 25 cm per 2 m, aged oak #5C4128 to #7A5A38, pronounced vertical grain, hand-hewn surface, old nail holes and cracks, matte oiled finish, subtle cups between planks. [STYLE LOCK]
```

**12) `rock_cliff_strata`**
```text
[PREFIX] Natural sea cliff rock face, horizontal stratified beds of grey limestone and dark grey-brown #6B655C, deep fractures, fissures and overhangs, dry faces mixed with dark wet areas, lichen spots and moss in the cracks, no vegetation, top-down rock surface. [STYLE LOCK]
```

**13) `terrain_grass`**
```text
[PREFIX] Temperate maritime meadow grass, short dense blades #4E6B3A with lighter and darker patches, clumps of clover and moss, small stones and bare earth spots, tiny wildflowers, seen from directly above in even diffuse light, no shadows. [STYLE LOCK]
```

**14) `water_ocean`**
```text
[PREFIX] Open sea water surface, deep teal-green #2E5E63 shading toward #12333B, small wind chop and long swells with fine whitecap streaks, subtle foam flecks, semi-transparent in the thin edges, flat top-down view of the water surface only, no horizon, no sky reflection of objects, even light. [STYLE LOCK]
```

**15) `water_foam_shore`**
```text
[PREFIX, decal with alpha] Breaking-wave foam and spray for rocks and shorelines, lacy white foam with thin translucent gaps, streaked run-off shapes, isolated on a plain white background for alpha extraction, top-down flat.
```

**16) `marble_floor_light`**
```text
[PREFIX] Polished pale marble floor tiles, cream-white #E3DCCF with soft grey-ochre veining #B8AC96, large square slabs 60 cm with fine joints, subtle scuffs and a few small chips, low satin polish, even diffuse light, flat top-down. [STYLE LOCK]
```

**17) `stone_flagstone_floor`**
```text
[PREFIX] Worn medieval limestone floor slabs, large irregular flags 60 to 120 cm, pale grey-beige #8E887D with darker traffic wear, chipped edges, dust and grit in the joints, faint foot-polish, matte, even light. [STYLE LOCK]
```

**18) `wood_plank_floor`**
```text
[PREFIX] Old oak plank floorboards, boards 20 to 25 cm wide, honey-brown #8A6238 with darker grain lines, iron nail heads, waxed satin sheen, traffic wear, dust in the joints. [STYLE LOCK]
```

**19) `wood_walnut_panel`**
```text
[PREFIX] Carved dark walnut wall panelling, rich brown #4A3220 with lighter figure and fine grain, recessed linenfold or shallow Gothic panels, waxed satin finish, dust in the mouldings, faint wear on the raised edges. [STYLE LOCK]
```

**20) `fabric_damask_red`**
```text
[PREFIX] Deep crimson royal damask fabric, #6E1B22 ground with a subtle tone-on-tone woven damask pattern of stylised Gothic foliage, wool-silk sheen, gentle folds and creases, slightly dusty, not glossy, flat top-down. [STYLE LOCK]
```

**21) `fabric_carpet_woven`**
```text
[PREFIX] Hand-woven wool carpet, deep red ground #7A2B2B with geometric border bands in indigo #2F3E6B, gold #C8A24A and cream, coarse visible weave and weft, slightly worn pile, dusty, flat top-down, no text or figures. [STYLE LOCK]
```

**22) `leather_hide`**
```text
[PREFIX] Aged brown leather, #5A3B22 with lighter creased highlights, visible grain and fine cracks, worn edges, faint oil sheen, dust in the creases, flat top-down. [STYLE LOCK]
```

**23) `metal_iron_forged`**
```text
[PREFIX] Blackened hand-forged wrought iron, near-black #2A2A2C with blue-grey sheen, hammer marks and scale, pitting, light orange surface rust in the recesses and around rivets, semi-matte. [STYLE LOCK]
```

**24) `metal_gilded_bronze`**
```text
[PREFIX] Gilded bronze ornament surface, warm gold #C8A24A over bronze with dark patina #6B5A32 in the recesses, wear showing bronze on the raised edges, fine tooled texture, antique matte gold, no modern polish. [STYLE LOCK]
```

**25) `metal_copper_verdigris`**
```text
[PREFIX] Oxidized copper sheet with verdigris patina, green #4E8A72 blending into teal and dark brown #4A3A2A in sheltered areas, streaked run-off staining, small bright copper spots on the raised edges, matte to satin metal. [STYLE LOCK]
```

**26) `glass_leaded_pane`**
```text
[PREFIX, non-tiling] Medieval leaded window glazing, small diamond quarries of irregular hand-blown glass in pale green-grey #8FA39B with bubbles and waviness, thick dark lead cames in a diamond lattice, dusty and dirty at the edges, even diffuse light from behind, matte glass.
```
> **+ نسخة ليلية:** نفس الخامة بـ`emissive` بلون `#FFB25E` باسم `glass_leaded_pane_emissive_albedo.png`.

**27) `glass_stained_rose`** — non-tiling
```text
Medieval stained-glass rose window, radial circular composition filled edge to edge, twelve petal segments of deep blue #2F4E8C, crimson #8C2F35, emerald #2F6B4A and amber #C8A24A, a central geometric rosette medallion, thick black lead lines, hand-blown glass with bubbles, backlit by even diffuse light, entirely geometric and non-figurative, no border, no background.
```

**28) `fabric_banner_heraldry`** — non-tiling
```text
Woven heraldic banner cloth, tall 1 by 3 composition filled edge to edge, deep crimson field #6E1B22 with a golden crenellated tower charge and a gold chevron below, coarse wool-linen weave with visible warp and weft, gentle wind creases, slightly faded and dusty, no text, no letters, no border.
```

**29) `terrain_dirt_road`**
```text
[PREFIX] Trodden dirt and gravel road, compacted light brown earth #A89677 with small grey stones, cart ruts, patches of mud and scattered leaves, thin grass creeping in at the edges, matte dry surface. [STYLE LOCK]
```

**30) `foliage_leaves`**
```text
[PREFIX, decal with alpha] Dense temperate tree foliage seen from above, overlapping oak and pine leaf clusters in mixed greens #4E6B3A to #6E7C42, natural irregular outline, thin twigs visible, isolated on a plain white background for alpha extraction.
```

**31–35) خامات Decal** (نفس صياغة السابق)
- `decal_moss_patch`: `[PREFIX, decal with alpha] Irregular moss and lichen patch, dark green #3F5B2E to yellowish #6E7A3A, fuzzy cluster with frayed edges, isolated on white for alpha extraction, top-down flat.`
- `decal_salt_bloom`: `[PREFIX, decal with alpha] White salt efflorescence bloom on stone, powdery crystalline crust spreading irregularly, soft feathered edges, isolated on a mid-grey background for alpha extraction, top-down flat.`
- `decal_water_streak`: `[PREFIX, decal with alpha] Vertical dark water run-off staining, translucent grey-brown streaks starting from a horizontal line at the top and tapering downward, feathered edges, varied opacity, isolated on white for alpha extraction.`
- `decal_soot_grime`: `[PREFIX, decal with alpha] Soot plume above a torch bracket, soft black-grey soot spreading upward with a greasy edge, mottled opacity, isolated on white for alpha extraction.`
- `decal_stone_crack`: `[PREFIX, decal with alpha] Hairline and medium stone cracks, irregular branching fracture lines, dark grey-brown, thin at the tips, subtle depth shadow, isolated on white for alpha extraction.`

**36–38)**
- `metal_iron_grille`: `[PREFIX, decal with alpha] Wrought iron grille of vertical bars with horizontal cross bars and rivets, hand-forged black iron seen flat-on, bars only with transparent gaps, isolated on white for alpha extraction.`
- `fabric_tapestry`: `Woven medieval wall tapestry, horizontal composition filled edge to edge, muted wool dyes — red #7A2B2B, green #3E5548, gold #C8A24A, indigo #2F3E6B — a geometric border framing a central crenellated-tower motif, coarse weave, faded and dusty, a few repaired threads, no text, no faces, no border.`
- `wood_props_kit`: `[PREFIX] Prop timber surface, mixed worn oak and pine boards for barrels, crates, tables, ladders and a crane frame, warm brown #6B4A2F with nicks, nail heads and tool marks, matte dusty finish. [STYLE LOCK]`


---

## 4. ملاحظات فنية

1. **بلا ظلال في الألبيو** — الألوان يجب أن تكون محايدة لأن الإضاءة تُحسب في MTA.
2. **Seamless إلزامي** — الأسوار تُبلَّط كل 4 م؛ أي خط في الحواف يتكرر مئات المرات.
3. **4K ماستر → 2K/1K/512/256** حسب مستوى LOD: القريب 2K، المتوسط 1K، البعيد 512، البعيد جدًا 256.
4. **ضغط TXD**: DXT1 للألوان المعتمة، DXT5 لما فيه alpha، وعدم ضغط الخرائط الـNormal/الرمادية (8-bit) للحفاظ على الدقة.
5. **حجم العناصر داخل الصورة** هو ما يحدد تطابق النسب مع المرجع — التزم بـ`tile_m`.
6. **الـNormal بصيغة OpenGL (+Y up)** — أخبرني إن كانت الأداة تُخرج DirectX وسأقلب القناة الخضراء.
7. خامات `non_tiling` تُسلَّم بحجم البطاقة كما هي وتُستخدم مرة واحدة (النوافذ الوردية، الرايات، الجداريات).
