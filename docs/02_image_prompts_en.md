# Reference Sheets — Ready-to-Paste Image Prompts (EN)
### Castle Aldurn — 9 sheets, ONE single design

**How to use**
1. Generate **Sheet A (hero)** first with the `MASTER PROMPT` below.
2. Lock the design: reuse the same seed, and use Sheet A as an **image reference / ControlNet input** for every following sheet (img2img strength ≈ 0.35–0.5 for elevations, 0.5–0.6 for courtyard/night).
3. If your tool supports it, add a **ControlNet depth or lineart** pass for B/C/D to force orthographic accuracy.
4. Deliver 3840 px PNG, sRGB, no watermark, no text (except the required scale bar).

> **Consistency rule:** same tower count (4 corner + 2 gatehouse + 1 stair turret), same heights, same materials, same colours, same weathering level, in every sheet. The silhouette sheet (I) is what the 3D reconstruction is measured against.

---

## 0. MASTER PROMPT (hero, Sheet A)

```text
Photorealistic architectural visualization of a historically accurate high-medieval European stone castle with an inner palace, Norman / early-English-Gothic transitional, real defensive architecture, not fantasy. Rectangular curtain wall 72 m by 54 m, 2.4 m thick, 9 m high to a 1.6 m wall-walk, crenellations with 1.8 m merlons and 1.2 m embrasures, arrow slits, string courses, stepped buttresses, three corbelled garderobe chutes on the north wall. Four round corner towers 9.5 m in diameter, 18 m to the cornice, projecting stone-corbelled machicolation rings at 15 m, crenellated parapets topped by steep dark blue-grey slate conical roofs with wrought-iron finials and pennants, about 26 m tall. Gatehouse projecting 4 m from the centre of the south wall: two identical round towers 11 m in diameter, 21 m tall, machicolated and crenellated, framing a pointed-arch gateway 4.6 m wide and 7 m tall with bold voussoirs, raised black iron portcullis, heavy double oak doors with iron bands and studs, timber drawbridge across a dry rock-cut moat 9 m wide and 6.5 m deep with ashlar revetment, low barbican wall stubs, vaulted gate passage with murder holes. Free-standing square keep 16 m by 16 m, 26 m high, crenellated, four corbelled corner bartizans and a round stair turret rising to 36 m with a conical slate roof, the tallest element. Inside the courtyard along the north wall a two-storey palace 36 m by 15 m, 13 m to the eaves, steep 52-degree dark slate pitched roof, three stone dormers, two stone chimney stacks with corbelled caps, south façade of tall pointed-arch mullioned and transomed windows with leaded diamond-pane glass and carved stone surrounds, east end with a chapel apse, buttresses and a 3 m stained-glass rose window, west end with an external stone staircase to a first-floor arched entrance behind a two-column portico. Service block along the west wall, single storey, pitched slate roof, arched timber doors, forge chimney. Cobbled courtyard 40 m by 30 m with a stone well under a small gabled canopy on oak posts, a wide stone stair to the wall-walk, a stone trough, two English oaks, iron torch brackets. The castle stands on a gentle grassy mound with steep natural bedrock outcrops below the east and south walls, a gravel path leading to the drawbridge. Materials: cool grey weathered limestone ashlar #9A958C with moss in the joints and dark water staining under cornices, rough rubble stone at the bases, smooth dressed limestone trim #ABA69C on quoins, copings and window surrounds, dark blue-grey slate roofs #3B4148, dark oak #5C4128 doors and timbers, black wrought iron #2A2A2C fittings, oxidized copper #4E8A72 on ridges and finials, crimson and gold banners #6E1B22 and #C8A24A bearing a golden crenellated tower on a crimson field. Golden hour lighting, sun 12 degrees above the horizon from the west-southwest, warm 3000K key, long soft shadows, cool 6500K ambient sky fill, light atmospheric haze. Three-quarter elevation view from the south-west at 25 m camera height, 35 mm lens, minimal perspective distortion, whole castle in frame, gatehouse clearly visible. Ultra-detailed geometry, crisp stone coursing, physically based materials, 4K, sharp focus, architectural reference photograph quality.
```

**Negative prompt (use everywhere):**
```text
fantasy castle, cartoon, anime, stylised illustration, low-poly, toy-like, neon, over-saturated, glowing magic, floating structures, dragons, modern elements, cars, power lines, crowds, text, watermark, signature, motion blur, heavy vignette, fog hiding architecture, tilted camera, fisheye, warped proportions, extra towers, inconsistent architecture
```

---

## 1. Sheet B — South Elevation (orthographic)

```text
Orthographic architectural elevation, true orthographic projection with no perspective distortion, straight-on front view of the SOUTH facade of the castle described below, flat neutral light-grey background, even overcast diffuse lighting, no harsh shadows, all architectural detail perfectly readable, no vegetation covering the masonry.

Subject: rectangular curtain wall 72 m wide and 10.4 m to the top of the crenellated parapet, stepped buttresses every 9 m, horizontal string courses at 4 m and 8 m, thin vertical arrow slits and a few cross-shaped embrasures. Perfectly centred gatehouse projecting forward: two identical round towers 11 m in diameter and 21 m tall, machicolated with two projecting stone rings on corbels, crenellated parapets, framing a pointed-arch gateway 4.6 m wide and 7 m tall with bold voussoirs, a raised black iron portcullis, heavy double oak doors with iron bands, a timber drawbridge, low barbican wall stubs to each side. Behind the wall, rising above it: the four corner towers with steep dark slate conical roofs and iron finials on the far corners, the square keep in the middle background with its crenellated parapet and four corner bartizans, the round stair turret with its tall conical slate roof, and the palace roof ridge with two stone chimney stacks and dormers.

Materials: weathered grey limestone ashlar with visible 60 by 30 cm coursing and moss in the joints, darker rubble stone at the base, smooth lighter limestone trim on quoins, copings, machicolations and window surrounds, dark blue-grey slate roofs, dark oak doors, black wrought iron. Include one standing human figure 1.8 m tall at the foot of the gatehouse as a scale reference and a 5 m / 10 m scale bar beneath the elevation, plus a thin ground line. Photorealistic architectural drafting render, crisp masonry joints, 4K, no text other than the scale bar, no watermark.
```

---

## 2. Sheet C — East Elevation (orthographic)

```text
Orthographic architectural elevation, true orthographic projection with no perspective distortion, straight-on side view of the EAST facade of the castle described below, flat neutral light-grey background, even overcast diffuse lighting, no harsh shadows, all masonry readable.

Subject: rectangular curtain wall 54 m wide, 2.4 m thick, 9 m to the wall-walk and 10.4 m to the top of the crenellated parapet, stepped buttresses every 9 m, string courses at 4 m and 8 m, two rows of thin vertical arrow slits, corbelled garderobe chutes. At both corners two round towers 9.5 m in diameter and 18 m to the cornice with projecting machicolation rings and crenellated parapets crowned by steep dark slate conical roofs with wrought-iron finials. Above the wall, seen in the interior: the square keep with crenellations and corner bartizans, the round stair turret with its conical slate roof, and the palace gable end with its steep 52-degree slate roof, stone dormer, chimney stack and the chapel apse with a stained-glass rose window and buttresses. Below the wall a steep natural rock outcrop and a dry rock-cut moat with ashlar revetment.

Materials: weathered grey limestone ashlar with visible coursing, moss in the joints, dark water staining under the cornices, rubble stone at the base, lighter dressed limestone trim, dark slate roofs, oxidized copper ridge caps. Include one 1.8 m human figure and a 5 m / 10 m scale bar with a thin ground line. Photorealistic architectural drafting render, 4K, no watermark.
```

---

## 3. Sheet D — North Elevation (orthographic)

```text
Orthographic architectural elevation, true orthographic projection with no perspective distortion, straight-on view of the NORTH facade of the castle described below, flat neutral light-grey background, even overcast diffuse lighting, no harsh shadows.

Subject: 72 m long curtain wall with crenellated parapet, stepped buttresses, string courses, thin arrow slits and three corbelled garderobe chutes projecting on stone corbels. Rising above the wall: the palace back roof — a long steep 52-degree dark slate pitch with three stone dormers, two tall stone chimney stacks with corbelled caps, and carved stone gable ends — plus the four corner towers with their conical slate roofs and the keep with its stair turret behind them.

Materials: weathered grey limestone ashlar with coursing and moss in the joints, rubble base, lighter trim on copings and chutes, dark blue-grey slate roofing, dark oak shutters, black iron fittings. Include one standing 1.8 m human figure and a 5 m / 10 m scale bar with a thin ground line. Photorealistic architectural drafting render, 4K, no watermark.
```

---

## 4. Sheet E — Roof Plan (orthographic, top view)

```text
True orthographic top-down roof plan of the castle described below, flat neutral grey background, even diffuse lighting, architectural plan clarity, all roof surfaces and wall tops readable, no perspective distortion.

Layout: a rectangular curtain wall 72 m by 54 m, 2.4 m thick, its crenellated wall-walk drawn as a continuous band; four round corner towers 9.5 m in diameter with four-segment conical slate roofs and iron finials at the corners; a projecting gatehouse at the centre of the south wall with two round towers 11 m in diameter and a central gate passage; a free-standing square keep 16 m by 16 m at the centre of the courtyard with a crenellated flat top, four corner bartizans and a round stair turret with a conical roof at the north-east corner; a long palace block 36 m by 15 m along the inner face of the north wall with a steep pitched slate roof, a central ridge, two chimney stacks and three dormers on the south pitch, plus a semicircular chapel apse at its east end with a small conical roof; a single-storey service block 22 m by 9 m along the inner face of the west wall with a pitched roof and a small forge chimney; a cobbled courtyard 40 m by 30 m with a central stone well under a small square gabled canopy, a stone staircase running up to the wall-walk along the west wall, a stone trough, and two trees.

Materials: grey weathered limestone wall tops with visible coursing, dark blue-grey slate roofing with visible overlapping courses, weathered terracotta on the well canopy, cobblestone paving in the courtyard. Add a 5 m / 10 m scale bar and a north arrow. Photorealistic architectural plan render, sharp detail, 4K, no watermark.
```

---

## 5. Sheet F — Courtyard Interior

```text
Photorealistic architectural interior view standing in the cobbled courtyard of a high-medieval stone castle, eye height 1.8 m, 24 mm lens, natural perspective. In front of the camera the free-standing square keep, 16 m by 16 m, 26 m tall, crenellated, with corbelled corner bartizans and a round stair turret rising taller with a conical dark slate roof. To the right, the two-storey palace along the north wall: 13 m to the eaves, steep 52-degree dark slate roof, three stone dormers, two stone chimney stacks, and a regular rhythm of tall pointed-arch mullioned and transomed windows with leaded diamond-pane glass and carved stone surrounds; at its east end the chapel apse with a stained-glass rose window. To the left, the single-storey service block with arched timber doors and a forge chimney. Behind, the gatehouse with its vaulted passage and timber double doors. In the middle of the courtyard a stone well with a small gabled canopy on two oak posts, a pulley and a bucket, a stone trough, an iron wall torch bracket, two English oaks, and a wide stone staircase climbing to the crenellated wall-walk. Cobblestone paving worn into a walking path.

Lighting: late-afternoon warm light raking across the courtyard, soft shadows, cool blue skylight fill in the shaded arcades, dust motes in the light beams. Materials: weathered grey limestone ashlar with moss in the joints and dark staining under cornices, lighter dressed trim, dark oak, black wrought iron, dark blue-grey slate, crimson and gold banner hanging from the keep wall bearing a golden crenellated tower on a crimson field. Ultra-detailed, physically based materials, 4K, sharp focus.
```

---

## 6. Sheet G — Night View

```text
Photorealistic night architectural view of the same high-medieval stone castle from the south-west three-quarter angle, 35 mm lens, whole castle in frame, gatehouse visible, exactly the same design and proportions as the daytime views. Cool blue moonlight from behind thin clouds, deep blue ambient sky, warm orange torch light pooling around the gatehouse, along the curtain wall and in the courtyard, warm glowing leaded windows in the palace and keep, faint reflections on the dry moat revetment and wet cobbles, stars visible, thin mist in the low ground. The crenellated silhouette of the towers, the keep, the conical slate roofs and the palace ridge reads clearly against the night sky. Realistic film-like exposure, deep shadows but readable masonry, physically based lighting, 4K, sharp focus, no fantasy glow, no magic effects, no watermark.
```

---

## 7. Sheet H — Detail Sheet (six close-ups, one image, same design and lighting)

```text
Architectural detail sheet: six close-up photographs of the same high-medieval castle, arranged in a clean 3 by 2 grid with thin gutters, identical overcast lighting and materials in every tile, photorealistic, ultra-detailed, 4K.

Tile 1: the gatehouse — round machicolated tower, corbelled stone ring with murder holes, crenellated parapet, pointed-arch gateway with bold voussoirs, raised black iron portcullis, heavy double oak doors with iron bands and studs.
Tile 2: a tall pointed-arch mullioned and transomed palace window with carved stone surround, leaded diamond-pane glass, a stone sill with water staining, and a small square hood mould above.
Tile 3: crenellation and machicolation detail — merlons 1.8 m wide and 1.4 m tall with sloped coping, embrasures, weathering, moss in joints, dark water streaks running down the ashlar.
Tile 4: the courtyard well — a 3.2 m stone drum with a low parapet, a small gabled terracotta canopy on two oak posts, a wooden pulley wheel, an iron chain and a bucket, cobblestone ground around it.
Tile 5: a stone chimney stack with corbelled cap rising above a steep dark slate roof, three courses of visible slates, a lead flashing and oxidized copper ridge cap.
Tile 6: the heraldic banner — crimson cloth with a golden crenellated tower and an open arched gate, a gold chevron below, woven texture, wind creases, hanging on an iron rod against ashlar masonry.

Materials consistent across all tiles: weathered grey limestone ashlar #9A958C, lighter dressed trim #ABA69C, dark blue-grey slate #3B4148, dark oak #5C4128, black wrought iron #2A2A2C, oxidized copper #4E8A72, crimson and gold cloth #6E1B22 and #C8A24A. No text, no watermark, no logos.
```

---

## 8. Sheet I — Silhouette Sheet (critical for 3D accuracy)

```text
Pure black silhouette sheet on a plain white background, no shading, no interior detail, no texture, hard clean edges, true orthographic projections, three views side by side on one canvas: front elevation (south facade, 72 m wide), side elevation (east facade, 54 m wide) and a top-down roof plan, of the following structure. Rectangular curtain wall with a crenellated parapet and stepped buttresses; a projecting central gatehouse with two round towers; four round corner towers with tall conical roofs; behind the wall a free-standing square keep with a crenellated top, four small corner bartizan turrets and a taller round stair turret with a conical roof; a long palace block with a steep pitched roof, two chimney stacks and three dormers; a chapel apse at one end of the palace; a single-storey service block. The silhouette must show the exact massing, proportion and height relationships between the wall, the corner towers, the keep and the stair turret. Include a 5 m / 10 m scale bar beneath each view and a thin ground line. Flat vector-like precision, no perspective, no shadows, no gradients, no watermark.
```

---

## 9. Variants / extra shots (optional but useful to me)

| Sheet | Prompt gist |
|---|---|
| **J — Aerial 45°** | "Aerial three-quarter view from 60 m altitude looking down at 45 degrees, whole castle and grounds in frame, same design, same materials, golden hour." |
| **K — Gate passage** | "Interior of the vaulted gate passage, ribbed stone vault, murder holes in the ceiling, portcullis above, warm light from the courtyard end, dark oak doors." |
| **L — Keep interior** | "Ground floor of the square keep, massive ashlar walls, a stone spiral stair in the corner turret, a large arched fireplace, arrow slit windows, oak table, iron chandelier with candles, torch light." |
| **M — Great hall interior** | "Two-storey great hall of the palace, tall pointed-arch mullioned windows with leaded glass, exposed oak trusses, a long oak table, a stone fireplace, a woven tapestry with the castle heraldry, warm candlelight." |
| **N — Wall-walk** | "View standing on the crenellated wall-walk looking along the curtain wall toward a round corner tower with its conical slate roof, the courtyard and keep below, overcast daylight." |
