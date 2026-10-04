#!/usr/bin/env python3
"""
render_preview.py — مُصيّر معماري (z-buffer + Shadow Map + إضاءة ذهبية + انعكاس بحر + إضاءة ليلية)
يعطي معاينة قريبة من المرجع لمقارنة النموذج قبل التصدير إلى MTA.

  python3 tools/render_preview.py --in build/polys.json --out renders/preview_day.png --mode day
  python3 tools/render_preview.py --in build/polys.json --out renders/preview_night.png --mode night
"""
import argparse, json, math, os
import numpy as np
from PIL import Image

TEXDIR = "textures/src"
_CACHE = {}
SM = 1400          # دقة خريطة الظل


def load_tex(name, size=192):
    k = (name, size)
    if k in _CACHE:
        return _CACHE[k]
    p = os.path.join(TEXDIR, f"{name}_albedo.png")
    if not os.path.exists(p):
        a = np.ones((size, size, 3), np.float32) * 0.5
    else:
        a = np.asarray(Image.open(p).convert("RGB").resize((size, size), Image.BILINEAR), np.float32) / 255.0
    _CACHE[k] = a
    return a


def look_at(eye, target, up=(0, 0, 1)):
    eye, target, up = (np.array(v, float) for v in (eye, target, up))
    f = target - eye; f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = r, u, -f
    M[0, 3], M[1, 3], M[2, 3] = -r @ eye, -u @ eye, f @ eye
    return M


def rasterize(V, tris, uv, color_fn, W, H, xform, zbuf, img, fov, aspect, sun_dir=None):
    """رَستَرة عامة: color_fn(world_pos, uv, mat, fi) -> لون (N,3)."""
    P = (xform @ np.hstack([V, np.ones((len(V), 1))]).T).T
    X, Y, Z = P[:, 0], P[:, 1], -P[:, 2]
    fpx = 1.0 / math.tan(math.radians(fov) / 2.0)
    sx = (X * fpx / aspect / np.maximum(Z, 1e-6) * 0.5 + 0.5) * W
    sy = (0.5 - Y * fpx / np.maximum(Z, 1e-6) * 0.5) * H
    order = np.argsort([-np.mean(Z[t]) for t in tris])
    for fi in order:
        t = tris[fi]
        if Z[t[0]] <= 0.5 or Z[t[1]] <= 0.5 or Z[t[2]] <= 0.5:
            continue
        xs, ys = sx[t], sy[t]
        x0, x1 = int(max(0, xs.min())), int(min(W - 1, xs.max()))
        y0, y1 = int(max(0, ys.min())), int(min(H - 1, ys.max()))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        p0, p1, p2 = np.array([xs[0], ys[0]]), np.array([xs[1], ys[1]]), np.array([xs[2], ys[2]])
        den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if abs(den) < 1e-9:
            continue
        w0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / den
        w1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / den
        w2 = 1 - w0 - w1
        ins = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
        if not ins.any():
            continue
        z = w0 * Z[t[0]] + w1 * Z[t[1]] + w2 * Z[t[2]]
        sub = zbuf[y0:y1 + 1, x0:x1 + 1]
        vis = ins & (z < sub)
        if not vis.any():
            continue
        uu, vv = uv[fi]
        u = w0 * uu[0] + w1 * uu[1] + w2 * uu[2]
        v = w0 * vv[0] + w1 * vv[1] + w2 * vv[2]
        col = color_fn(t, u, v, w0, w1, w2)
        subimg = img[y0:y1 + 1, x0:x1 + 1]
        subimg[:] = np.where(vis[..., None], col, subimg)
        sub[:] = np.where(vis, z, sub)


def build_tris(polys):
    F, UV, MATS = polys["f"], polys["uv"], polys["mat"]
    tris, tuv, tm = [], [], []
    for fc, uvs, mm in zip(F, UV, MATS):
        for k in range(1, len(fc) - 1):
            tris.append([int(fc[0]), int(fc[k]), int(fc[k + 1])])
            tuv.append([uvs[0], uvs[k], uvs[k + 1]])
            tm.append(mm)
    return tris, tuv, tm


def render(polys, out_path, W=1920, H=1200, eye=(900, -1500, 430), target=(30, -60, 60),
           fov=38.0, mode="day", shadows=True):
    V = np.array(polys["v"], np.float32)
    tris, tuv, tm = build_tris(polys)
    MATDEF = polys["mats"]
    cam = look_at(eye, target)
    aspect = W / H

    if mode == "night":
        sun = np.array([-0.25, 0.42, 0.87], np.float32); sun /= np.linalg.norm(sun)
        sun_col = np.array([0.30, 0.42, 0.75], np.float32)          # قمر بارد
        amb_col = np.array([0.10, 0.13, 0.24], np.float32)
    else:
        # ساعة ذهبية متأخرة: شمس منخفضة (≈20°) من خلف-يسار — كما في المرجع
        sun = np.array([-0.74, 0.42, 0.33], np.float32); sun /= np.linalg.norm(sun)
        sun_col = np.array([1.48, 0.88, 0.46], np.float32)
        amb_col = np.array([0.26, 0.34, 0.52], np.float32)

    # ---------- خريطة الظل ----------
    shadow = None
    if shadows:
        upv = np.array([0, 0, 1.0])
        if abs(np.dot(sun, upv)) > 0.98:
            upv = np.array([0, 1.0, 0])
        sc = look_at(np.array([0, 0, 60.0]) + sun * 900, np.array([0, 0, 60.0]), upv)
        P = (sc @ np.hstack([V, np.ones((len(V), 1))]).T).T
        zs = -P[:, 2]
        th = math.radians(0.75 * 110)
        ex = max(np.abs(P[:, 0]).max(), np.abs(P[:, 1]).max()) / math.tan(th) * 1.05
        sc = look_at(np.array([0, 0, 60.0]) + sun * ex, np.array([0, 0, 60.0]), upv)
        P = (sc @ np.hstack([V, np.ones((len(V), 1))]).T).T
        ex = max(np.abs(P[:, 0]).max(), np.abs(P[:, 1]).max()) * 1.02
        fov_s = 2 * math.degrees(math.atan(ex / ex))
        sxs = (P[:, 0] / ex * 0.5 + 0.5) * SM
        sys_ = (0.5 - P[:, 1] / ex * 0.5) * SM
        zs = -P[:, 2]
        smap = np.full((SM, SM), 1e9, np.float32)
        order = np.argsort([-np.mean(zs[t]) for t in tris])
        for fi in order:
            if tm[fi] in ("mountain", "snow"):      # الجبال لا تُلقي ظلًا على المدينة
                continue
            t = tris[fi]
            xs, ys = sxs[t], sys_[t]
            x0, x1 = int(max(0, xs.min())), int(min(SM - 1, xs.max()))
            y0, y1 = int(max(0, ys.min())), int(min(SM - 1, ys.max()))
            if x1 <= x0 or y1 <= y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            p0, p1, p2 = np.array([xs[0], ys[0]]), np.array([xs[1], ys[1]]), np.array([xs[2], ys[2]])
            den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
            if abs(den) < 1e-9:
                continue
            w0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / den
            w1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / den
            w2 = 1 - w0 - w1
            ins = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
            if not ins.any():
                continue
            z = w0 * zs[t[0]] + w1 * zs[t[1]] + w2 * zs[t[2]]
            sub = smap[y0:y1 + 1, x0:x1 + 1]
            sub[:] = np.where(ins & (z < sub), z, sub)
        shadow = (smap, sc, ex)

    # ---------- السماء ----------
    img = np.zeros((H, W, 3), np.float32)
    if mode == "night":
        top, hor = np.array([0.012, 0.02, 0.055]), np.array([0.05, 0.075, 0.14])
    else:
        top, hor = np.array([0.15, 0.37, 0.74]), np.array([0.96, 0.80, 0.62])
    grad = np.linspace(0, 1, H)[:, None] ** 1.35
    img[:] = top[None, None, :] * (1 - grad[..., None]) + hor[None, None, :] * grad[..., None]
    zbuf = np.full((H, W), 1e12, np.float32)
    cam_pos = np.array(eye, np.float32)

    Pcam = (cam @ np.hstack([V, np.ones((len(V), 1))]).T).T
    Zc = -Pcam[:, 2]

    # أضواء ليلية (مشاعل/فوانيس) — تُستخدم في الوضع الليلي
    lantern_pos = []
    for i, t in enumerate(polys["f"]):
        pass
    lang = polys.get("lanterns", [])

    tex_cache = {}

    def color_fn(t, u, v, w0, w1, w2):
        mm = tm_color(t)
        tex = tex_cache.get(mm)
        if tex is None:
            tid = MATDEF.get(mm, {}).get("tex", mm)
            tex = load_tex(tid)
            tex_cache[mm] = tex
        ts = tex.shape[0]
        tu = (np.mod(u, 1.0) * (ts - 1)).astype(np.int32)
        tv = (np.mod(v, 1.0) * (ts - 1)).astype(np.int32)
        col = tex[tv, tu].copy()
        tint = MATDEF.get(mm, {}).get("color")
        if tint:
            col *= np.array(tint, np.float32) * 1.4

        wp = (w0 * V[t[0]] + w1 * V[t[1]] + w2 * V[t[2]])
        P0, P1, P2 = V[t[0]], V[t[1]], V[t[2]]
        n = np.cross(P1 - P0, P2 - P0)
        nl = np.linalg.norm(n)
        n = n / nl if nl > 1e-9 else np.array([0, 0, 1.0], np.float32)

        sh = 1.0
        if shadow is not None:
            smap, sc, ex = shadow
            Ps = (sc @ np.array([wp[0], wp[1], wp[2], 1.0]))
            sx_ = int((Ps[0] / ex * 0.5 + 0.5) * SM)
            sy_ = int((0.5 - Ps[1] / ex * 0.5) * SM)
            if 1 <= sx_ < SM - 1 and 1 <= sy_ < SM - 1:
                d = -Ps[2]
                win = smap[sy_ - 1:sy_ + 2, sx_ - 1:sx_ + 2]
                sh = 1.0 if d - 1.6 <= win.min() else 0.25      # ظل ناعم مبسّط

        ndl = max(0.0, float(np.dot(n, sun)))
        if mm in ("water",):
            view_dir = cam_pos - wp
            view_dir /= (np.linalg.norm(view_dir) + 1e-9)
            h = sun + view_dir
            h /= (np.linalg.norm(h) + 1e-9)
            spec = max(0.0, float(np.dot(n, h))) ** 90.0
            lum = amb_col * 0.6 + sun_col * (0.35 + 0.5 * ndl) + sun_col * spec * 1.8
        elif mm in ("window_lit",) and mode == "night":
            lum = np.array([1.6, 1.15, 0.62], np.float32)
        elif mm in ("gilded", "copper"):
            lum = amb_col + sun_col * (0.25 + 0.75 * ndl) * sh + 0.25
        else:
            lum = amb_col * (0.55 + 0.45 * (0.5 + 0.5 * n[2])) + sun_col * ndl * sh
        col = col * lum[None, :]
        if mm == "foam":
            col = col * 1.05 + np.array([0.06, 0.07, 0.08], np.float32)
        # ضباب بحري دافئ
        d = float(Zc[t[0]])
        k = 1.0 - math.exp(-max(0.0, d - 700) * 0.00035)
        fcol = np.array([0.86, 0.78, 0.68], np.float32) if mode == "day" else np.array([0.04, 0.06, 0.11], np.float32)
        col = col * (1 - k) + fcol * k
        return col

    def raster():
        order = np.argsort([-np.mean(Zc[t]) for t in tris])
        for fi in order:
            t = tris[fi]
            if Zc[t[0]] <= 0.5 or Zc[t[1]] <= 0.5 or Zc[t[2]] <= 0.5:
                continue
            mm = tm[fi]
            xs = (Pcam[t, 0] / (Zc[t]) * (1 / math.tan(math.radians(fov) / 2)) / aspect * 0.5 + 0.5) * W
            ys = (0.5 - Pcam[t, 1] / (Zc[t]) * (1 / math.tan(math.radians(fov) / 2)) * 0.5) * H
            x0, x1 = int(max(0, xs.min())), int(min(W - 1, xs.max()))
            y0, y1 = int(max(0, ys.min())), int(min(H - 1, ys.max()))
            if x1 <= x0 or y1 <= y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            p0, p1, p2 = np.array([xs[0], ys[0]]), np.array([xs[1], ys[1]]), np.array([xs[2], ys[2]])
            den = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
            if abs(den) < 1e-9:
                continue
            w0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / den
            w1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / den
            w2 = 1 - w0 - w1
            ins = (w0 >= -0.001) & (w1 >= -0.001) & (w2 >= -0.001)
            if not ins.any():
                continue
            z = w0 * Zc[t[0]] + w1 * Zc[t[1]] + w2 * Zc[t[2]]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            vis = ins & (z < sub)
            if not vis.any():
                continue
            uvs = tuv[fi]
            u = w0 * uvs[0][0] + w1 * uvs[1][0] + w2 * uvs[2][0]
            v = w0 * uvs[0][1] + w1 * uvs[1][1] + w2 * uvs[2][1]
            tex = tex_cache.get(mm)
            if tex is None:
                tid = MATDEF.get(mm, {}).get("tex", mm)
                tex = load_tex(tid)
                tex_cache[mm] = tex
            ts = tex.shape[0]
            tu = (np.mod(u, 1.0) * (ts - 1)).astype(np.int32)
            tv = (np.mod(v, 1.0) * (ts - 1)).astype(np.int32)
            col = tex[tv, tu].astype(np.float32).copy()
            tint = MATDEF.get(mm, {}).get("color")
            if tint:
                col *= np.array(tint, np.float32) * 1.45

            # ---- حساب لكل بكسل (مع البثّ الصحيح) ----
            wp = (w0[..., None] * V[t[0]] + w1[..., None] * V[t[1]] + w2[..., None] * V[t[2]]).astype(np.float32)
            P0, P1, P2 = V[t[0]], V[t[1]], V[t[2]]
            n = np.cross(P1 - P0, P2 - P0)
            nl = np.linalg.norm(n)
            n = (n / nl).astype(np.float32) if nl > 1e-9 else np.array([0, 0, 1], np.float32)

            # ---- الظل (لكل بكسل) ----
            sh = np.ones_like(w0, np.float32)
            if shadow is not None:
                smap, sc, ex = shadow
                px_ = sc[0, 0] * wp[..., 0] + sc[0, 1] * wp[..., 1] + sc[0, 2] * wp[..., 2] + sc[0, 3]
                py_ = sc[1, 0] * wp[..., 0] + sc[1, 1] * wp[..., 1] + sc[1, 2] * wp[..., 2] + sc[1, 3]
                pz_ = sc[2, 0] * wp[..., 0] + sc[2, 1] * wp[..., 1] + sc[2, 2] * wp[..., 2] + sc[2, 3]
                sxi = np.clip(((px_ / ex * 0.5 + 0.5) * SM).astype(np.int32), 1, SM - 2)
                syi = np.clip(((0.5 - py_ / ex * 0.5) * SM).astype(np.int32), 1, SM - 2)
                d = -pz_
                taps = np.zeros_like(d)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        taps = np.maximum(taps, smap[syi + dy, sxi + dx])
                sh = np.where(d - 2.4 <= taps, 1.0, 0.30).astype(np.float32)
                # خارج نطاق خريطة الظل: لا ظل (وإلا ظهرت أنماط بلاطات زائفة على البحر)
                inb = (np.abs(px_) <= ex) & (np.abs(py_) <= ex) & (d < ex * 1.6)
                sh = np.where(inb, sh, 1.0).astype(np.float32)

            ndl = max(0.0, float(np.dot(n, sun)))
            if mm == "water":
                # سطح أفقي + موجات دقيقة للّمعان → لا تعريق على حدود البلاطات
                wnx = 0.055 * np.sin(wp[..., 0] * 0.085 + wp[..., 1] * 0.052)
                wny = 0.055 * np.cos(wp[..., 1] * 0.104 - wp[..., 0] * 0.041)
                nw = np.stack([wnx, wny, np.ones_like(wnx)], axis=-1)
                nw = nw / (np.linalg.norm(nw, axis=2, keepdims=True) + 1e-9)
                vd = cam_pos[None, None, :] - wp
                vd = vd / (np.linalg.norm(vd, axis=2, keepdims=True) + 1e-9)
                h = sun[None, None, :] + vd
                h = h / (np.linalg.norm(h, axis=2, keepdims=True) + 1e-9)
                spec = np.maximum(0.0, (h * nw).sum(axis=2)) ** 220.0
                glint = np.maximum(0.0, (nw * sun[None, None, :]).sum(axis=2)) ** 3.0
                lam = np.float32(0.34 + 0.34 * float(max(0.0, float(sun[2]))))
                lum = (amb_col * 0.60)[None, None, :] + sun_col[None, None, :] * lam \
                      + (sun_col[None, None, :] * spec[..., None] * 1.9)
            elif mm == "window_lit" and mode == "night":
                lum = np.array([1.85, 1.25, 0.62], np.float32)[None, None, :] * np.ones(col.shape, np.float32)
            elif mm in ("gilded", "copper"):
                lum = (amb_col + sun_col * (0.30 + 0.70 * ndl) * float(sh.mean()) + 0.20)[None, None, :] * np.ones(col.shape, np.float32)
            elif mm == "window":
                # زجاج: ليلًا قاتم يعكس ضوء القمر، ونهارًا لمعة خفيفة (التوهّج للنوافذ المضيئة فقط)
                lum = (amb_col * (0.9 if mode == "night" else 1.2)
                       + sun_col * (0.35 + 0.65 * ndl) * float(sh.mean()))[None, None, :] * np.ones(col.shape, np.float32)
            else:
                lum = (amb_col * (0.55 + 0.5 * (0.5 + 0.5 * float(n[2]))) + sun_col * ndl * sh[..., None])
            col = col * lum
            if mm == "foam":
                col = col * 1.08 + 0.05
            # عمق لكل بكسل (وإلا ظهرت حدود بلاطات البحر/الأرض كخطوات ضباب)
            dcam = w0 * Zc[t[0]] + w1 * Zc[t[1]] + w2 * Zc[t[2]]
            # ضباب جوي: يبدأ أبكر ليصنع منظورًا هوائيًا للجبال البعيدة
            k = 1.0 - np.exp(-np.maximum(0.0, dcam - 1100) * 0.00038)
            if mode == "day":
                # ضباب بارتفاعين: دافئ عند سطح الماء، بارد أزرق في العلو (منظور هوائي طبيعي)
                hb = np.clip(wp[..., 2] / 210.0, 0.0, 1.0)[..., None]
                warm = np.array([0.90, 0.83, 0.71], np.float32)
                cool = np.array([0.55, 0.66, 0.82], np.float32)
                fcol = warm[None, None, :] * (1 - hb) + cool[None, None, :] * hb
            else:
                fcol = np.array([0.035, 0.05, 0.10], np.float32)[None, None, :]
            col = col * (1 - k[..., None]) + fcol * k[..., None]
            subimg = img[y0:y1 + 1, x0:x1 + 1]
            subimg[:] = np.where(vis[..., None], col, subimg)
            sub[:] = np.where(vis, z, sub)

    raster()

    img = np.clip(img, 0, 1)
    img = img * 0.62 + img * img * 0.38                  # منحنى تباين
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    Image.fromarray((img * 255).astype(np.uint8)).save(out_path)
    print(f"  ✓ {out_path}  ({W}x{H})  [{mode}]")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="build/polys.json")
    ap.add_argument("--out", default="renders/preview.png")
    ap.add_argument("--mode", default="day", choices=["day", "night"])
    ap.add_argument("--w", type=int, default=1920)
    ap.add_argument("--h", type=int, default=1200)
    ap.add_argument("--eye", default="")
    ap.add_argument("--target", default="")
    ap.add_argument("--no-shadow", action="store_true")
    a = ap.parse_args()
    polys = json.load(open(a.inp))
    eye = tuple(float(x) for x in a.eye.split(",")) if a.eye else (760, -1180, 350)
    tgt = tuple(float(x) for x in a.target.split(",")) if a.target else (10, -55, 70)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    render(polys, a.out, W=a.w, H=a.h, eye=eye, target=tgt, mode=a.mode, shadows=not a.no_shadow)
