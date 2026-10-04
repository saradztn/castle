# textures/src — هنا تضع خاماتك

ارفع ملفاتك بالأسماء الموجودة في `docs/03_texture_prompts_en.md` (أو في الأطلس):

```
textures/src/
├── stone_sandstone_ashlar_albedo.png
├── stone_sandstone_ashlar_normal.png
├── stone_sandstone_ashlar_roughness.png
├── stone_sandstone_ashlar_ao.png
├── roof_slate_albedo.png
└── ... (38 خامة × القنوات المطلوبة)
```

**أو الأسهل:** ضع صورة الأطلس الواحدة في `textures/atlas/atlas.png` ثم شغّل:

```bash
pip install --break-system-packages numpy pillow
python3 tools/slice_atlas.py textures/atlas/atlas.png --grid 6x4 --out textures/src --size 2048 --seamless --derive-pbr
```

وسيقصّها إلى 24 خامة مسمّاة ويولّد Normal/Roughness/AO لكل واحدة تلقائيًا.
(الخرائط المشتقة مُستثناة من Git لأنها تُولَّد بأمر واحد — انظر `.gitignore`.)
