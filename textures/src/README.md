# textures/src — الخامات (كل خامة في صورة منفصلة)

كل خامة تُولَّد **بصورة مستقلة** بالذكاء الاصطناعي وتُحفظ هنا باسم:

```
textures/src/<id>_albedo.png        ← صورة الخامة الأساسية (الملوّن)
```

ثم يولّد السكربت تلقائيًا بجوارها: `<id>_normal.png` و `<id>_roughness.png` و `<id>_ao.png`
(+ `<id>_alpha.png` للخامات الشفافة)، وهي ملفات مشتقّة لا تُرفع إلى Git.

## إعادة التوليد / المعالجة بأمر واحد

```bash
pip install --break-system-packages numpy pillow
python3 tools/process_textures.py --src textures/src --size 1024 --seamless --derive-pbr --alpha-decals --contact-sheet textures/preview/contact_sheet.jpg
```

* `--seamless` : مزج الحواف لجعل الخامة قابلة للتكرار في الاتجاهين.
* `--derive-pbr` : استخراج Normal / Roughness / AO من صورة الألوان.
* `--alpha-decals` : تحويل خلفية الـdecals البيضاء إلى قناة شفافية.
* `--contact-sheet` : صورة معاينة واحدة تجمع كل الخامات (للاستعراض فقط).
