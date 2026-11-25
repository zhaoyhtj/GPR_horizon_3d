# -*- coding: utf-8 -*-
"""
v5（按赵老师最终口径重画）：右侧界面正确不动；左侧段原拾取不正确，
按赵老师手绘黄虚线原样画出。黄线即正确答案，不做平滑、不简化为直线。

赵老师原话："在勾画这个界面时，右侧的正确，但左侧段拾取的不正确。
现在左侧我已用黄虚线画出来了，你现在完完整整地重新画，右侧的不变，左侧的按我黄虚线画。"

做法：
- 黄虚线顶点从《界面重新绘制.docx》矢量标注精确提取（PDF 贝塞尔 -> 图数据坐标），
  共 35 点，x=-99.96..0.52 m、TWT=80.95..128.14 ns，逐点插值保留真实形态。
- 左段 x<=0 严格按黄线原样画；右段 x>0 保持原追踪线完全不变；
  黄线终点 x=0.52/t=128.14 ns 与原线 x=0/t=128.04 ns 天然吻合。
- 其余要素（TWT 0-300 ns、ENG35 竖线、RF4=5.69 m 标注、图例、无标题/色标/口径行）保持不变。
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import hilbert, medfilt
from scipy.ndimage import gaussian_filter1d

BASE = r"C:/Users/hanxj/WorkBuddy AI/2026-09-21-08-33-17/validation-public/data/x_schill"
OUT = r"D:/workspace/workbuddy/赵老师/剖面图审核_20261124/fig_RTA100_0019_RF4_TWT_v5.png"

NS, NT, DI = 928, 5058, 0.049634
DT = 602.444515 / NS
V, TG = 0.1008, 44.8  # 反推速度、地表零点（仅作追踪引导，不画深度轴）

# 赵老师手绘黄虚线的矢量顶点（local x, TWT ns），从 界面重新绘制.docx 精确提取
YELLOW = np.array([
    [-99.96,  80.95], [-95.65,  84.80], [-90.02,  96.36], [-84.87, 100.53],
    [-81.63, 101.82], [-79.00, 101.49], [-76.61, 104.38], [-74.81, 102.78],
    [-72.05, 105.02], [-69.18, 102.78], [-67.38, 102.46], [-64.75, 101.17],
    [-61.15, 105.02], [-57.80, 105.35], [-52.77, 108.56], [-49.54, 109.84],
    [-45.47, 109.20], [-42.35, 110.17], [-41.15, 105.35], [-39.00, 105.02],
    [-36.72, 109.52], [-33.85, 108.88], [-31.93, 114.34], [-28.82, 118.83],
    [-27.50, 116.91], [-25.35, 120.44], [-22.59, 119.80], [-19.36, 116.91],
    [-16.49, 122.68], [-13.61, 123.32], [-10.14, 122.68], [ -7.02, 122.37],
    [ -5.11, 121.72], [ -2.35, 124.29], [  0.52, 128.14],
])

# 拾取埋深（仅作右段追踪引导）
rows = []
with open(BASE + "/GPR/3D-GPR-array/RF4.pck", encoding="latin-1") as fh:
    for line in fh:
        p = line.split()
        if len(p) >= 7 and p[6].startswith("RTA100_0019"):
            try:
                rows.append((float(p[0]), float(p[5])))
            except ValueError:
                pass
rx = np.array([r[0] for r in rows]); rd = np.array([r[1] for r in rows])
x = np.arange(NT) * DI - 100.0
guide_d = np.interp(x, rx, rd, left=rd[0], right=rd[-1])
guide_t = TG + 2 * guide_d / V

# 剖面
A = np.fromfile(BASE + "/GPR/2D-GPR-profile/RTA100_0019_A1.rd3",
                dtype="<i2").reshape(NT, NS).astype(float)
F = np.fft.rfft(A - A.mean(axis=1, keepdims=True), axis=1)
fq = np.fft.rfftfreq(NS, d=DT)
F[:, (fq < 0.025) | (fq > 0.350)] = 0
T = np.fft.irfft(F, NS, axis=1)
tau = np.arange(NS) * DT
ENV = np.abs(hilbert(T - T.mean(axis=0)))

# 右段（x>=0）原同相轴追踪，与 v4 完全一致
trk = np.zeros(NT)
for k in range(NT):
    gt = guide_t[k]
    lo = max(0, int((gt - 12) / DT)); hi = min(NS - 1, int((gt + 12) / DT))
    seg = ENV[k, lo:hi + 1]
    pk = np.where((seg[1:-1] > seg[:-2]) & (seg[1:-1] >= seg[2:]))[0] + 1
    trk[k] = (lo + pk[np.argmax(seg[pk])]) * DT if len(pk) else gt
trk = gaussian_filter1d(medfilt(trk, kernel_size=101), sigma=25)
k0 = int(round((113.2 + 100) / DI))
trk[k0] = 153.2

# 左段：严格按赵老师手绘黄虚线的原始顶点画出，不做平滑、不简化为直线。
# 赵老师明确："左侧段拾取的不正确，我已用黄虚线画出来了，左侧按我黄虚线画。"
# 黄线顶点即正确答案，逐点插值保留其真实形态（含局部起伏）。
left_x = YELLOW[:, 0]; left_t = YELLOW[:, 1]
ix0 = int(round((0.0 + 100) / DI))            # x=0 对应的道号
final = trk.copy()
# x<=0 用黄线原样插值；x>0 保持原追踪线完全不变
final[:ix0 + 1] = np.interp(x[:ix0 + 1], left_x, left_t,
                            left=left_t[0], right=left_t[-1])
final[x > 0] = trk[x > 0]
final[k0] = 153.2                            # ENG35 锚点不动

# 作图：0-300 ns 完整时窗（其余与 v4 完全一致）
plt.rcParams.update({"font.size": 10, "axes.labelsize": 11})
fig, ax = plt.subplots(figsize=(13.2, 6.6), dpi=160)
vmax = np.percentile(np.abs(T), 98)
im = ax.imshow(T.T, extent=[x.min(), x.max(), tau.max(), tau.min()],
               aspect="auto", cmap="gray", vmin=-vmax, vmax=vmax,
               interpolation="nearest", zorder=1)
ax.plot(x, final, color="#e53935", lw=1.5, ls=(0, (5, 4)), zorder=4,
        label="RF4 (traced reflection)")
ax.axvline(113.2, color="#ffd54f", ls="--", lw=1.3, zorder=3, label="ENG35 borehole")
ax.plot(113.2, 153.2, marker="o", color="#ffd54f", ms=5.5, zorder=5)
ax.annotate("RF4 = 5.69 m", xy=(113.2, 153.2), xytext=(92, 172),
            color="#ffb300", fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8),
            arrowprops=dict(arrowstyle="->", color="#ffb300", lw=1.6), zorder=6)
ax.set_xlim(-100, 150)
ax.set_ylim(300, 0)
ax.set_xlabel("Local x along profile (m)")
ax.set_ylabel("Two-way time (ns)")
ax.legend(loc="lower right", framealpha=0.9, fontsize=10)
fig.subplots_adjust(left=0.075, right=0.975, top=0.97, bottom=0.13)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, dpi=160)

print("yellow span: x %.1f..%.1f, t %.1f..%.1f ns" %
      (left_x.min(), left_x.max(), left_t.min(), left_t.max()))
for xt in (-100, -80, -60, -40, -20, 0, 20, 113.2, 150):
    k = int(round((xt + 100) / DI))
    print("  x=%7.1f  final t=%7.2f ns (v4 %.2f)" % (xt, final[k], trk[k]))
print("saved:", OUT, os.path.getsize(OUT), "bytes")
