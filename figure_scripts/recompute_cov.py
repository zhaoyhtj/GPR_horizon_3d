# -*- coding: utf-8 -*-
"""复算表 4 / 表 5 的经验覆盖率：σ 双线性采样到残差点。"""
import numpy as np
d = np.load("data/rf4_grid.npz")
g = np.load("data/rf4_inter.npz")
gx, gy, sig = d["gx"], d["gy"], d["sig_field"]
rx, ry, rr = d["rx"], d["ry"], d["rr"]
real = g["real"]

def bilin(x, y):
    i = np.clip(np.searchsorted(gx, x) - 1, 0, len(gx) - 2)
    j = np.clip(np.searchsorted(gy, y) - 1, 0, len(gy) - 2)
    tx = (x - gx[i]) / (gx[i + 1] - gx[i])
    ty = (y - gy[j]) / (gy[j + 1] - gy[j])
    s = ((1 - tx) * (1 - ty) * sig[j, i] + tx * (1 - ty) * sig[j, i + 1]
         + (1 - tx) * ty * sig[j + 1, i] + tx * ty * sig[j + 1, i + 1])
    return s

s = bilin(rx, ry)
a = np.abs(rr)
print("总体: ±1σ %.1f%%  ±2σ %.1f%%" % (100 * (a <= s).mean(), 100 * (a <= 2 * s).mean()))
dr = np.array([np.min(np.hypot(real[:, 0] - x, real[:, 1] - y)) for x, y in zip(rx, ry)])
for lo, hi in [(0, 2), (2, 5), (5, 10), (10, 100)]:
    m = (dr >= lo) & (dr < hi)
    print("%3d-%3d m  n=%4d  ±1σ %5.1f%%  ±2σ %5.1f%%" % (
        lo, hi, m.sum(), 100 * (a[m] <= s[m]).mean(), 100 * (a[m] <= 2 * s[m]).mean()))
print("mean(|r|)/std(r) = %.4f" % (a.mean() / rr.std()))
