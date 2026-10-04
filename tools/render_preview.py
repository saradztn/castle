#!/usr/bin/env python3
"""
render_preview.py — مُصيّر عالي الجودة (Software Rayless Rasteriser)
Castle & Palace — لمقارنة الموديل بالصورة المرجعية

الميزات: Supersampling، شمس + هالة (bloom)، سماء متدرجة + ضباب،
لمعة ماء (specular + fresnel)، إضاءة ذاتية للفوانيس (ليل)، نجوم وقمر،
تدريج لوني سينمائي + Vignette.

الاستخدام:
  python3 tools/render_preview.py --in build/polys.json --out renders/preview_day.png --mode day
  python3 tools/render_preview.py --in build/polys.json --out renders/preview_night.png --mode night
"""

import argparse, json, math, os
import numpy as np
from PIL import Image

TEXDIR = "textures/src"
_CACHE = {}


def tex(name, size=192):
    key = (name, size)
    if key not in _CACHE:
        p = os.path.join(TEXDIR, f"{name}_albedo.png")
        if os.path.exists(p):
            im = Image.open(p).convert("RGB").resize((size, size), Image.BILINEAR)
            _CACHE[key] = np.asarray(im, dtype=np.float32) / 255.0
        else:
            _CACHE[key] = np.full((size, size, 3), 0.5, dtype=np.float32)
    return _CACHE[key]


def look_at(eye, target, up=(0, 0, 1)):
    eye, target, up = map(lambda v: np.array(v, dtype=np.float64), (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = r, u, -f
    M[0, 3], M[1, 3], M[2, 3] = -r @ eye, -u @ eye, f @ eye
    return M


def sky_image(W, H, mode, sun_uv, horizon=0.56):
    """سماء متدرجة + شمس/قمر + هالة + نجوم."""
    yy = np.linspace(0.0, 1.0, H)[:, None, None]          # (H,1,1)
    if mode == "day":
        top = np.array([0.16, 0.38, 0.74], dtype=np.float32)
        mid = np.array([0.62, 0.75, 0.90], dtype=np.float32)
        low = np.array([0.97, 0.86, 0.67], dtype=np.float32)
    else:
        top = np.array([0.008, 0.014, 0.045], dtype=np.float32)
        mid = np.array([0.030, 0.050, 0.110], dtype=np.float32)
        low = np.array([0.100, 0.130, 0.220], dtype=np.float32)
    t_hi = np.clip(yy / max(horizon, 1e-3), 0, 1)
    t_lo = np.clip((yy - horizon) / max(1 - horizon, 1e-3), 0, 1)
    up = top[None, None, :] * (1 - t_hi) + mid[None, None, :] * t_hi
    dn = mid[None, None, :] * (1 - t_lo) + low[None, None, :] * t_lo
    row = np.where(yy < horizon, up, dn)                   # (H,1,3)
    sky = np.repeat(row, W, axis=1).astype(np.float32)

    # هالة الأفق
    gg = np.exp(-(((yy[:, :, 0] - horizon) ** 2) / (2 * 0.06 ** 2)))[:, :, None]   # (H,1,1)
    glow_c = (np.array([1.0, 0.72, 0.42], dtype=np.float32) if mode == "day"
              else np.array([0.35, 0.45, 0.75], dtype=np.float32))
    sky += np.repeat(gg, W, axis=1) * glow_c[None, None, :] * (0.55 if mode == "day" else 0.22)

    # الشمس / القمر
    sx, sy = sun_uv
    xs = np.arange(W, dtype=np.float32)[None, :, None]
    ys = np.arange(H, dtype=np.float32)[:, None, None]
    d = np.sqrt(((xs - sx * W) / W) ** 2 + ((ys - sy * H) / H) ** 2)
    core = np.exp(-(d ** 2) / (2 * (0.010 if mode == "day" else 0.007) ** 2))
    halo = np.exp(-(d ** 2) / (2 * (0.14 if mode == "day" else 0.09) ** 2))
    if mode == "day":
        sky += core * np.array([1.0, 0.93, 0.78], dtype=np.float32)[None, None, :] * 1.25
        sky += halo * np.array([1.0, 0.72, 0.45], dtype=np.float32)[None, None, :] * 0.75
    else:
        sky += core * np.array([0.92, 0.95, 1.0], dtype=np.float32)[None, None, :] * 1.0
        sky += halo * np.array([0.35, 0.45, 0.75], dtype=np.float32)[None, None, :] * 0.30
        rng = np.random.default_rng(4)
        stars = (rng.random((H, W, 1)) > 0.99915).astype(np.float32)
        vy = np.clip((horizon - yy[:, :, 0]) / horizon, 0, 1)[:, :, None]
        sky += stars * vy * 1.4
    return sky


def render(polys, out_path, W=1600, H=1000, eye=(560, -640, 205), target=(0, 6, 62),
           fov=43.0, mode="day", sun=(-0.55, -0.66, 0.52), ss=2):
    """ss = معامل الـSupersampling (1=سريع، 2=قياسي، 3=أعلى)."""
    Wr, Hr = W * ss, H * ss
    V = np.array(polys["v"], dtype=np.float32)
    MATDEF = polys.get("mats", {})
    F, UV, MATS = polys["f"], polys["uv"], polys["mat"]

    # تفكيك المضلعات إلى مثلثات
    tris, tri_uv, tri_mat, tri_emb = [], [], [], []
    for fc, uvs, mm in zip(F, UV, MATS):
        e = bool(MATDEF.get(mm, {}).get("emissive"))
        for k in range(1, len(fc) - 1):
            tris.append([fc[0], fc[k], fc[k + 1]])
            tri_uv.append([uvs[0], uvs[k], uvs[k + 1]])
            tri_mat.append(mm)
            tri_emb.append(e)
    F, UV, MATS, EMB = tris, tri_uv, tri_mat, tri_emb

    cam = look_at(eye, target)
    fpx = 1.0 / math.tan(math.radians(fov) / 2.0)
    aspect = Wr / Hr
    P = (cam @ np.hstack([V, np.ones((len(V), 1), dtype=np.float64)]).T).T
    X, Y, Z = P[:, 0], P[:, 1], -P[:, 2]
    ok = Z > 1.0
    sx = (X * fpx / aspect / np.maximum(Z, 1e-6) * 0.5 + 0.5) * Wr
    sy = (0.5 - Y * fpx / np.maximum(Z, 1e-6) * 0.5) * Hr

    ldir = np.array(sun, dtype=np.float64); ldir /= np.linalg.norm(ldir)
    # موضع الشمس على الشاشة (للهالة)
    sd = cam[:3, :3] @ ldir * 1500
    zz = -sd[2]
    sun_uv = (0.5 + sd[0] * fpx / aspect / zz * 0.5, 0.5 - sd[1] * fpx / zz * 0.5) if zz > 0 else (0.15, 0.12)
    img = sky_image(Wr, Hr, mode, sun_uv)
    zbuf = np.full((Hr, Wr), 1e12, dtype=np.float32)
    emb_mask = np.zeros((Hr, Wr), dtype=np.float32)

    amb = 0.21 if mode == "day" else 0.10
    dif = 0.88 if mode == "day" else 0.30
    sun_c = np.array([1.0, 0.90, 0.74]) if mode == "day" else np.array([0.60, 0.70, 1.0])
    fog_c = np.array([0.78, 0.80, 0.85]) if mode == "day" else np.array([0.04, 0.055, 0.105])
    fog_k = 0.000055 if mode == "day" else 0.00009
    order = np.argsort([-np.mean(Z[f]) for f in F])

    for fi in order:
        f = F[fi]
        if not all(ok[i] for i in f):
            continue
        xs, ys = sx[f], sy[f]
        x0, x1 = int(max(0, xs.min())), int(min(Wr - 1, xs.max()))
        y0, y1 = int(max(0, ys.min())), int(min(Hr - 1, ys.max()))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        p0 = np.array([xs[0], ys[0]]); p1 = np.array([xs[1], ys[1]]); p2 = np.array([xs[2], ys[2]])
        den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(den) < 1e-9:
            continue
        w0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / den
        w1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / den
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        z = w0 * Z[f[0]] + w1 * Z[f[1]] + w2 * Z[f[2]]
        sub_z = zbuf[y0:y1 + 1, x0:x1 + 1]
        vis = inside & (z <= sub_z + 0.05)
        if not vis.any():
            continue

        uvs = np.array(UV[fi], dtype=np.float32)
        u = w0 * uvs[0, 0] + w1 * uvs[1, 0] + w2 * uvs[2, 0]
        v = w0 * uvs[0, 1] + w1 * uvs[1, 1] + w2 * uvs[2, 1]
        mm = MATS[fi]
        tid = MATDEF.get(mm, {}).get("tex", mm)
        T = tex(tid)
        ts = T.shape[0]
        tu = (np.mod(u, 1.0) * (ts - 1)).astype(np.int32)
        tv = (np.mod(v, 1.0) * (ts - 1)).astype(np.int32)
        col = T[tv, tu]
        tint = MATDEF.get(mm, {}).get("color")
        if tint:
            col = col * np.array(tint, dtype=np.float32) * 1.5

        P0, P1, P2 = V[f[0]], V[f[1]], V[f[2]]
        n = np.cross(P1 - P0, P2 - P0)
        nl = np.linalg.norm(n)
        n = n / nl if nl > 1e-9 else np.array([0, 0, 1], dtype=np.float32)
        ndl = float(np.dot(n, ldir))
        shade = float(amb + max(0.0, ndl) * dif)
        col = col * shade

        # لمعة الماء / الزجاج
        if mm in ("water", "water_d", "glass", "marble"):
            view = np.array(eye, dtype=np.float32) - P0
            view /= (np.linalg.norm(view) + 1e-6)
            hv = ldir + view
            hv /= (np.linalg.norm(hv) + 1e-6)
            spec = max(0.0, float(np.dot(n, hv))) ** 34 * (1.1 if mode == "day" else 0.45)
            col = col + spec * sun_c.astype(np.float32) * (0.85 if mm.startswith("water") else 0.5)
            if mm.startswith("water"):
                fres = (1.0 - abs(float(np.dot(n, view)))) ** 3
                skytint = np.array([0.42, 0.60, 0.86], dtype=np.float32) if mode == "day" else \
                          np.array([0.05, 0.08, 0.17], dtype=np.float32)
                col = col * (1 - 0.35 * fres) + skytint * (0.55 * fres)

        # الإضاءة الذاتية (فوانيس/نوافذ)
        if EMB[fi]:
            if mode == "night":
                col = col * 2.5 + np.array([0.55, 0.34, 0.12], dtype=np.float32)
            else:
                col = col * 1.02

        # ضباب جوي
        kfog = 1.0 - np.exp(-fog_k * z)
        col = col * (1 - kfog[..., None]) + fog_c.astype(np.float32) * kfog[..., None]

        sub = img[y0:y1 + 1, x0:x1 + 1]
        m = vis[..., None]
        sub[:] = np.where(m, col, sub)
        if EMB[fi]:
            em = emb_mask[y0:y1 + 1, x0:x1 + 1]
            em[:] = np.where(vis, np.maximum(em, 1.0), em)
        sub_z[:] = np.where(vis, z, sub_z)

    # ---- Bloom على العناصر المضيئة ----
    if emb_mask.any():
        bright = np.zeros((Hr, Wr, 3), dtype=np.float32)
        bright[:] = img * emb_mask[..., None]
        k = 0
        blur = bright.copy()
        for _ in range(2):
            b = np.pad(blur, ((1, 1), (1, 1), (0, 0)), mode="edge")
            blur = (b[:-2, 1:-1] + b[2:, 1:-1] + b[1:-1, :-2] + b[1:-1, 2:] + b[1:-1, 1:-1]) / 5.0
        img = img + blur * (0.85 if mode == "night" else 0.25)

    # ---- تدرّج لوني + Vignette + تصغير ----
    img = np.clip(img, 0, 1)
    img = img * 1.0
    if mode == "day":
        img[..., 0] *= 1.045; img[..., 2] *= 0.985
    else:
        img[..., 2] *= 1.10; img[..., 0] *= 0.95
    xs = np.linspace(-1, 1, Wr)[None, :]
    ys = np.linspace(-1, 1, Hr)[:, None]
    r = np.sqrt(xs ** 2 + ys ** 2)
    img *= np.clip(1.06 - 0.20 * r ** 2, 0, 1)[..., None]
    img = np.clip((img - 0.5) * 1.16 + 0.5, 0, 1.2)   # تباين
    img = img / (img + 1.15) * 2.05                  # منحنى فيلمي
    img = np.clip(img, 0, 1) ** (1 / 2.2)

    out = Image.fromarray((img * 255).astype(np.uint8))
    if ss > 1:
        out = out.resize((W, H), Image.LANCZOS)
    out.save(out_path)
    print(f"  ✓ {out_path}  ({W}x{H}، SS={ss})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="build/polys.json")
    ap.add_argument("--out", default="renders/preview.png")
    ap.add_argument("--mode", default="day", choices=["day", "night"])
    ap.add_argument("--w", type=int, default=1600)
    ap.add_argument("--h", type=int, default=1000)
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--eye", default="")
    ap.add_argument("--target", default="0,6,62")
    ap.add_argument("--fov", type=float, default=43.0)
    a = ap.parse_args()
    polys = json.load(open(a.inp))
    eye = tuple(float(x) for x in a.eye.split(",")) if a.eye else (560, -640, 205)
    tgt = tuple(float(x) for x in a.target.split(","))
    render(polys, a.out, W=a.w, H=a.h, eye=eye, target=tgt, fov=a.fov, mode=a.mode, ss=a.ss)
