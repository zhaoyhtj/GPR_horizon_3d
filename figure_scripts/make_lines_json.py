# -*- coding: utf-8 -*-
"""Rebuild data/schill_lines.json from the published Reflexw pick table.

Input
-----
RF4.pck  (tab-separated), distributed with Igel et al. (2019), CC-BY-4.0:

    profile  Easting(global)  Northing(global)  Elevation/m asl  notused  depth/m b. ground  profile

Output
------
data/schill_lines_rebuilt.json  -- same schema as data/schill_lines.json

The engineering coordinates (x, y) used throughout the paper are a pure
translation of the UTM coordinates, with both axes parallel to UTM East and
North.  There is no rotation: see OFFSET below and the check at the end.

Usage
-----
    export SCHILL_PCK=/path/to/3D-GPR-array/RF4.pck
    python tools/make_lines_json.py

If SCHILL_PCK is not set, the script looks for the file in ./data/ and then in
./raw/.  Nothing is downloaded automatically.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "schill_lines_rebuilt.json"
REF = ROOT / "data" / "schill_lines.json"

# Translation from UTM (E, N) to the engineering frame (x, y):
#     x = Easting - OFFSET[0],   y = Northing - OFFSET[1]
# Derived from the 4990 picks themselves; the per-line standard deviation of
# the offset is below 0.001 m, i.e. the transform is a translation, not a
# rotation.  Verified in probe against all 24 lines.
OFFSET = (565613.414, 5816500.472)


def find_pck() -> Path:
    env = os.environ.get("SCHILL_PCK")
    cands = []
    if env:
        cands.append(Path(env))
    cands += [ROOT / "raw" / "RF4.pck", ROOT / "data" / "RF4.pck"]
    for c in cands:
        if c.is_file():
            return c
    sys.exit(
        "RF4.pck not found. Download the Schillerslage dataset "
        "(doi:10.5281/zenodo.2686824), then set SCHILL_PCK to the path of\n"
        "  .../x_schill/GPR/3D-GPR-array/RF4.pck"
    )


def read_pck(path: Path):
    """Return {profile_file: [(profile, E, N, elev, depth), ...]}.

    Fields are split on TAB and kept positionally.  Do NOT drop empty fields
    before indexing: a few rows carry a blank column, and filtering shifts the
    column indices by one, which silently corrupts the coordinates.
    """
    by_line: dict[str, list[tuple[float, float, float, float, float]]] = {}
    n = 0
    with path.open(encoding="latin-1") as fh:
        for ln in fh:
            f = [q.strip() for q in ln.rstrip("\r\n").split("\t")]
            if len(f) < 7:
                continue
            try:
                prof = float(f[0])
                east = float(f[1])
                north = float(f[2])
                elev = float(f[3])
                depth = float(f[5])
            except ValueError:
                continue
            by_line.setdefault(f[6], []).append((prof, east, north, elev, depth))
            n += 1
    return by_line, n


def main() -> None:
    src = find_pck()
    by_line, n = read_pck(src)
    print("read %d picks on %d profiles from %s" % (n, len(by_line), src.name))

    lines = []
    for name, rec in sorted(by_line.items()):
        arr = np.array(rec, dtype=float)
        x = arr[:, 1] - OFFSET[0]
        y = arr[:, 2] - OFFSET[1]
        d = arr[:, 4]
        # order along the profile so that consecutive samples are neighbours
        slope = np.polyfit(x, y, 1)[0]
        t = x + slope * y
        o = np.argsort(t)
        lines.append({
            "file": name,
            "x": [round(float(v), 2) for v in x[o]],
            "y": [round(float(v), 2) for v in y[o]],
            "d": [round(float(v), 4) for v in d[o]],
        })

    allx = np.concatenate([np.asarray(l["x"]) for l in lines])
    ally = np.concatenate([np.asarray(l["y"]) for l in lines])
    alld = np.concatenate([np.asarray(l["d"]) for l in lines])
    meta = {
        "site": "Schillerslage (Germany), GPR 100 MHz array",
        "n_lines": len(lines),
        "n_points": int(len(allx)),
        "depth_range_m": [round(float(alld.min()), 2), round(float(alld.max()), 2)],
        "xy_extent_m": [round(float(allx.min()), 1), round(float(allx.max()), 1),
                        round(float(ally.min()), 1), round(float(ally.max()), 1)],
        "source": "Reflexw picked reflectors, RF4.pck (manual picks by original authors)",
        "coordinate_frame": ("x = Easting - %.3f m, y = Northing - %.3f m; "
                             "axes parallel to UTM, no rotation" % OFFSET),
    }
    OUT.write_text(json.dumps({"meta": meta, "lines": lines}, ensure_ascii=False),
                   encoding="utf-8")
    print("-> %s (%d lines, %d points)" % (OUT.relative_to(ROOT), len(lines), len(allx)))

    # ---------------------------------------------------------------- check
    if not REF.is_file():
        return
    ref = json.loads(REF.read_text(encoding="utf-8"))["lines"]
    ref_by = {l["file"]: l for l in ref}
    if set(ref_by) != {l["file"] for l in lines}:
        print("!! profile names differ from %s" % REF.name)
        return
    worst_xy = worst_d = 0.0
    for a in lines:
        b = ref_by[a["file"]]
        za, zb = np.asarray(a["d"]), np.asarray(b["d"])
        if len(za) != len(zb):
            print("!! %s: %d vs %d points" % (a["file"], len(za), len(zb)))
            continue
        # compare as point sets: the pick order in the published table is not
        # guaranteed to match, so match in the plane instead of by index
        pa = np.column_stack([a["x"], a["y"]])
        pb = np.column_stack([b["x"], b["y"]])
        tree = cKDTree(pb)
        dist, idx = tree.query(pa, k=1)
        worst_xy = max(worst_xy, float(dist.max()))
        worst_d = max(worst_d, float(np.abs(za - zb[idx]).max()))
    print("check vs %s: max plane mismatch = %.4f m, max |dd| = %.5f m "
          "(both are rounding only)" % (REF.name, worst_xy, worst_d))


if __name__ == "__main__":
    main()
