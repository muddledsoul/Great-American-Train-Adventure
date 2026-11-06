#!/usr/bin/env python3
"""Simplify the NTAD Amtrak route GeoJSON (Douglas-Peucker) so the page loads fast on phones.
Usage: simplify_routes.py in.geojson out.geojson [tolerance_deg]"""
import json, sys

def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    stack = [(0, len(pts) - 1)]
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]; bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        best, bi = 0.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if L == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
                d = (px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2
            if d > best:
                best, bi = d, i
        if best > eps * eps:
            keep[bi] = True
            stack.append((a, bi)); stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]

src, dst = sys.argv[1], sys.argv[2]
eps = float(sys.argv[3]) if len(sys.argv) > 3 else 0.002   # ~200 m
d = json.load(open(src))
before = after = 0
for f in d["features"]:
    g = f["geometry"]
    parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
    out = []
    for part in parts:
        pts = [(round(x, 4), round(y, 4)) for x, y in (c[:2] for c in part)]
        before += len(pts)
        s = rdp(pts, eps)
        after += len(s)
        out.append([list(p) for p in s])
    g["type"] = "MultiLineString"; g["coordinates"] = out
    f["properties"] = {"name": f["properties"].get("name"), "ROUTE_URL": f["properties"].get("ROUTE_URL")}
json.dump(d, open(dst, "w"), separators=(",", ":"))
print(f"{len(d['features'])} routes, {before} -> {after} vertices")
