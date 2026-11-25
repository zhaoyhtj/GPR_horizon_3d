# -*- coding: utf-8 -*-
"""解析 Schillerslage 的 Reflexw picked-reflector 文本表，抽出 3D 层位真值。

文件是 tab 分隔文本，列名见表头：
  RF4.pck:        profile | Easting | Northing | Elevation/m asl | notused | depth/m b. ground | <原始文件名>
  RF1_x-profiles: y/m (local) | Easting | Northing | Elevation | x/m | depth/m below ground

这些是**人工拾取的反射层深度**，是层位追踪算法唯一的 3D ground truth。
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"


def find_dir() -> Path:
    """Directory holding RF4.pck, RF1_x-profiles.PCK and RF1_y-profiles.PCK.

    Set SCHILL_DIR to the unzipped `x_schill/GPR/3D-GPR-array` folder; if it is
    not set, ./raw/ is tried.  Nothing is downloaded automatically.
    """
    env = os.environ.get("SCHILL_DIR")
    cands = [Path(env)] if env else []
    cands.append(ROOT / "raw")
    for c in cands:
        if (c / "RF4.pck").is_file():
            return c
    sys.exit("RF4.pck not found. Download doi:10.5281/zenodo.2686824 and set "
             "SCHILL_DIR to .../x_schill/GPR/3D-GPR-array")


SRC = find_dir()


def read_pck(p: Path) -> tuple[list[str], np.ndarray, list[str]]:
    raw = p.read_bytes().decode("latin-1").replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln for ln in raw.split("\n") if ln.strip()]
    header = lines[0].split("\t")
    header = [h.strip() for h in header if h.strip()]
    rows = []
    origin = []
    for ln in lines[1:]:
        # keep the fields positional: a few rows carry a blank column, and
        # dropping empty fields shifts every index after it
        parts = [x.strip() for x in ln.split("\t")]
        if len(parts) < 6 or not _isnum(parts[0]):
            continue
        try:
            vals = [float(parts[0]), float(parts[1]), float(parts[2]),
                    float(parts[3]), float("nan"), float(parts[5])]
        except ValueError:
            continue
        rows.append(vals)
        # RF4.pck carries the source profile name in a seventh column;
        # RF1_*-profiles.PCK has six columns and no name
        origin.append(parts[6] if len(parts) > 6 else "")
    return header, np.array(rows, dtype=np.float64), origin


def _isnum(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def main() -> None:
    # ---- RF4：主 3D 阵列（4991 点）
    h, arr, origin = read_pck(SRC / "RF4.pck")
    print(f"RF4.pck 表头: {h}")
    print(f"  {arr.shape[0]} 行 × {arr.shape[1]} 列")
    # 列: profile(y) | Easting | Northing | Elevation | notused | depth
    y = arr[:, 0]
    e, n, el = arr[:, 1], arr[:, 2], arr[:, 3]
    depth = arr[:, 5]
    print(f"  y(测线) 范围 {y.min():.1f} → {y.max():.1f} m（{(len(np.unique(y)))} 条不同测线）")
    print(f"  深度范围 {depth.min():.2f} → {depth.max():.2f} m")
    print(f"  高程范围 {el.min():.2f} → {el.max():.2f} m asl")
    print(f"  原始剖面文件 {len(set(origin))} 个，例：{sorted(set(origin))[:2]}")

    # 每条测线的点数
    cnt = {}
    for v in y:
        cnt[v] = cnt.get(v, 0) + 1
    print(f"  每条测线点数: min={min(cnt.values())} max={max(cnt.values())} 中位={int(np.median(list(cnt.values())))}")

    np.savez_compressed(
        OUT / "schill_rf4_3d.npz",
        y=y, easting=e, northing=n, elev=el, depth=depth,
        origin=np.array(origin),
    )
    print(f"  → data/schill_rf4_3d.npz")

    # ---- RF1_x / RF1_y 横切纵切
    for fn in ["RF1_x-profiles.PCK", "RF1_y-profiles.PCK"]:
        h2, a2, o2 = read_pck(SRC / fn)
        print(f"\n{fn} 表头: {h2}")
        print(f"  {a2.shape[0]} 行")
        if a2.shape[1] >= 6:
            print(f"  col0 {a2[:,0].min():.1f}→{a2[:,0].max():.1f}｜"
                  f"深度 {a2[:,5].min():.2f}→{a2[:,5].max():.2f} m")
        np.savez_compressed(OUT / (fn.split(".")[0].lower() + ".npz"), data=a2,
                            header=np.array(h2))
        print(f"  → data/{fn.split('.')[0].lower()}.npz")


if __name__ == "__main__":
    main()
