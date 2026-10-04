#!/usr/bin/env python3
"""
render_preview.py — مُصيّر سريع (z-buffer + خامات + إضاءة نهارية/ليلية)
يقرأ build/polys.json ويُخرج صورة PNG لمقارنتها بالصورة المرجعية.

الاستخدام:
  python3 tools/render_preview.py --in build/polys.json --out build/preview_day.png --mode day
  python3 tools/render_preview.py --in build/polys.json --out build/preview_night.png --mode night --top
"""

import argparse, json, math, os, sys
import numpy as np
from PIL import Image

TEXDIR = "textures/src"
TEX_CACHE = {}


def load_tex(name, size=128):
    key = (name, size)
    if key in TEX_CACHE:
        return TEX_CACHE[key]
    path = os.path.join(TEXDIR, f"{name}_albedo.png")
    if not os.path.exists(path):
        a = np.ones((size, size, 3), dtype=np.float32) * 0.5
    else:
        im = Image.open(path).convert("RGB").resize((size, size), Image.BILINEAR)
        a = np.asarray(im, dtype=np.float32) / 255.0
    TEX_CACHE[key] = a
    return a


def look_at(eye, target, up=(0, 0, 1)):
    eye, target, up = map(lambda v: np.array(v, dtype=np.float64), (eye, target, up))
    f = target - eye
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    M = np.eye(4)
    M[0, :3], M[1, :3], M[2, :3] = r, u, -f
    M[0, 3], M[1, 3], M[2, 3] = -r @ eye, -u @ eye, f @ eye
    return M


def render(polys, out_path, W=1600, H=1000, eye=(520, -720, 330), target=(-10, 10, 60),
           fov=42.0, mode="day", sun=(-0.55, -0.62, 0.55), fog=0.00003, water_z=0.0):
    V = np.array(polys["v"], dtype=np.float32)
    F = polys["f"]
    UV = polys["uv"]
    MATS = polys["mat"]
    MATDEF = polys.get("mats", {})

    cam = look_at(eye, target)
    aspect = W / H
    fpx = 1.0 / math.tan(math.radians(fov) / 2.0)

    P = (cam @ np.hstack([V, np.ones((len(V), 1), dtype=np.float64)]).T).T
    X, Y, Z = P[:, 0], P[:, 1], -P[:, 2]       # Z أمامي موجب، Y لأعلى
    ok = Z > 1.0
    sx = (X * fpx / aspect / np.maximum(Z, 1e-6) * 0.5 + 0.5) * W
    sy = (0.5 - Y * fpx / np.maximum(Z, 1e-6) * 0.5) * H

    img = np.zeros((H, W, 3), dtype=np.float32)
    # تدرّج سماء
    if mode == "night":
        top = np.array([0.015, 0.025, 0.070]); horizon = np.array([0.05, 0.07, 0.13])
    else:
        top = np.array([0.26, 0.46, 0.78]); horizon = np.array([0.93, 0.82, 0.63])
    grad = np.linspace(0, 1, H)[:, None]
    img[:] = (top[None, None, :] * (1 - grad[..., None]) + horizon[None, None, :] * grad[..., None])

    zbuf = np.full((H, W), 1e12, dtype=np.float32)

    ldir = np.array(sun, dtype=np.float32); ldir /= np.linalg.norm(ldir)
    if mode == "night":
        ldir = np.array([-0.3, 0.35, 0.88], dtype=np.float32); ldir /= np.linalg.norm(ldir)
        amb = 0.15
    else:
        amb = 0.22

    # تفكيك المضلعات إلى مثلثات (شبكة مروحية)
    tris, tri_uv, tri_mat = [], [], []
    for fc, uvs, mm in zip(F, UV, MATS):
        for k in range(1, len(fc) - 1):
            tris.append([fc[0], fc[k], fc[k + 1]])
            tri_uv.append([uvs[0], uvs[k], uvs[k + 1]])
            tri_mat.append(mm)
    F, UV, MATS = tris, tri_uv, tri_mat

    order = np.argsort([-np.mean(Z[f]) for f in F]) if len(F) < 60000 else np.arange(len(F))
    tex_cache = {}

    for fi in order:
        f = F[fi]
        if len(f) < 3:
            continue
        if not all(ok[i] for i in f):
            continue
        xs, ys = sx[f], sy[f]
        x0, x1 = int(max(0, xs.min())), int(min(W - 1, xs.max()))
        y0, y1 = int(max(0, ys.min())), int(min(H - 1, ys.max()))
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
        vis = inside & (z < sub_z)
        if not vis.any():
            continue
        uvs = np.array(UV[fi], dtype=np.float32)
        u = w0 * uvs[0, 0] + w1 * uvs[1, 0] + w2 * uvs[2, 0]
        v = w0 * uvs[0, 1] + w1 * uvs[1, 1] + w2 * uvs[2, 1]
        mname = MATS[fi]
        tex = tex_cache.get(mname)
        if tex is None:
            tid = MATDEF.get(mname, {}).get("tex", mname)
            tex = load_tex(tid)
            tex_cache[mname] = tex
        ts = tex.shape[0]
        tu = (np.mod(u, 1.0) * (ts - 1)).astype(np.int32)
        tv = (np.mod(v, 1.0) * (ts - 1)).astype(np.int32)
        col = tex[tv, tu]
        tint = MATDEF.get(mname, {}).get("color")
        if tint:
            col = col * np.array(tint, dtype=np.float32) * 1.45
        P0, P1, P2 = V[f[0]], V[f[1]], V[f[2]]
        n = np.cross(P1 - P0, P2 - P0)
        nl = np.linalg.norm(n)
        if nl > 1e-9:
            n = n / nl
            ndl = float(np.dot(n, ldir))
            shade = amb + max(0.0, ndl) * (1.05 if mode == "day" else 0.40)
        else:
            shade = amb
        if mode == "night":
            col = col * np.array([0.55, 0.68, 1.0], dtype=np.float32) * (shade + 0.15)
        else:
            col = col * shade
        if fog:
            d = z
            k = 1.0 - np.exp(-fog * d)
            fcol = np.array([0.70, 0.74, 0.80], dtype=np.float32) if mode == "day" else np.array([0.05, 0.07, 0.13], dtype=np.float32)
            col = col * (1 - k[..., None]) + fcol * k[..., None]
        sub = img[y0:y1 + 1, x0:x1 + 1]
        m = vis[..., None]
        sub[:] = np.where(m, col, sub)
        sub_z[:] = np.where(vis, z, sub_z)

    img = np.clip(img, 0, 1)
    img = img * 0.55 + img * img * 0.45          # منحنى تباين بسيط
    out = np.clip(img, 0, 1) ** (1 / 2.2)
    Image.fromarray((out * 255).astype(np.uint8)).save(out_path)
    print(f"  ✓ {out_path}  ({W}x{H})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="build/polys.json")
    ap.add_argument("--out", default="build/preview.png")
    ap.add_argument("--mode", default="day", choices=["day", "night"])
    ap.add_argument("--w", type=int, default=1600)
    ap.add_argument("--h", type=int, default=1000)
    ap.add_argument("--top", action="store_true")
    ap.add_argument("--eye", default="")
    a = ap.parse_args()
    polys = json.load(open(a.inp))
    if a.eye:
        eye = tuple(float(x) for x in a.eye.split(","))
    elif a.top:
        eye = (60, -60, 900)
    else:
        eye = (560, -640, 205)
    render(polys, a.out, W=a.w, H=a.h, eye=eye,
           target=(-10, 10, 55), mode=a.mode, fov=40 if not a.top else 46)
