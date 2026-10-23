# Uncertainty-aware 3D visualization of a GPR horizon

A single-file, dependency-free interactive viewer for a ground-penetrating radar (GPR)
reflection horizon reconstructed from sparse profiles. The horizon surface is coloured by a
leave-one-line-out **repeatability scale σ(x, y)**, so that the parts of the surface that
should be doubted are visible on the same screen as the surface itself.

Companion software to the manuscript *Spatial uncertainty quantification and visualization of
GPR horizon reconstruction under sparse profile coverage* (in preparation; target journal
*Computers & Geosciences*).

**No installation, no build step, no server, no network access.** Download
[`horizon3d.html`](horizon3d.html) and open it in any current browser (Chrome, Edge, Firefox,
Safari). The file is fully self-contained — about 0.46 MB, with the derived fields embedded as
base64 arrays and no external requests of any kind. It also works directly from GitHub Pages.

![preview](preview.png)

---

## 1. What the viewer shows

The horizon is interface **RF4** at the Schillerslage multi-method hydrogeophysical test site
(northern Germany), picked on **24 profiles** (18 inline + 6 crossline) at **4 990 points**.
The surface is reconstructed on a 2.5 m grid (108 × 94 = 10 152 nodes; **7 739 nodes** remain
after a 9 m distance-to-nearest-pick mask), giving 14 884 rendered triangles.

The viewer deliberately keeps **three error terms apart** instead of collapsing them into one
"±x m" figure:

| Term | How it is measured | Value |
|:--|:--|:--|
| ① Pick | Two profiles crossing at the same (x, y), depth compared | median **0.310 m** (exact-interpolation set: P90 0.593 m, max 0.895 m; nearest-pick set: P90 0.570 m, max 0.890 m). 90 true crossings out of 108 extended-line intersections (18 fall outside actual coverage); 66 pairs qualify for exact interpolation, 81 for the nearest-pick variant |
| ② Spatial σ(x, y) | 24-fold leave-one-line-out; residuals inverted by normalized convolution with a 10 m kernel | per-family RMSE **0.252 / 0.360 m**; σ median **0.200 m**, P90 0.348 m, range 0.075–0.669 m |
| ③ Time-to-depth | CMP layered velocity model vs. cores, as reported in the original study | **≤ 0.30 m**, a global constant |

The three are **reported separately and never summed**. σ already contains part of the pick
discrepancy (crossing mismatches leak into the leave-one-out residuals), so adding the pick
term again would double-count it; and the time-to-depth term does not vary with position, so
it cannot be folded into a spatial field.

Two consequences are worth stating explicitly, because they run against intuition:

- **The time-to-depth term dominates absolute depth uncertainty.** 0.30 m is larger than the
  median spatial term of 0.200 m, and densifying the profile grid does not reduce it.
- **"Distance to the nearest profile" is not what drives the error.** The profile family with
  a 3.4× smaller gap has residuals **43 % larger**. The quantity that tracks the error is the
  distance to the nearest *crossing* (Spearman ρ = −0.333; binned median |r| falls from
  0.285 m to 0.128 m). The mechanism is that points close to a crossline are also close to a
  crossing, and crossings are where two independently interpreted profiles disagree most.

## 2. How to read ±kσ

**σ is not a standard deviation.** It is a local mean absolute residual — a MAD-type scale,
obtained by convolving |r| with a normalized kernel. It carries units of metres and means
"local average absolute repeatability", nothing more.

Empirical coverage of the ±kσ band is **52.5 % at ±1σ and 98.6 % at ±2σ**, which does not
match the 68 % / 95 % pair. Multiplying by √(π/2) ≈ 1.2533 (the Gaussian conversion) gives
70.0 % / 99.8 % — still not a match, and the deviations point in opposite directions. The
band should therefore be read as a **relative indicator of where the reconstruction is weak**,
not as a confidence interval. If nominal coverage is what you need, the right object is a
quantile field, not this scale field; that is a different deliverable and is not attempted here.

## 3. Controls

| Group | What it does |
|:--|:--|
| **Render mode** | `surface` (smooth horizon), `band` (uncertainty band ±kσ), `profiles` (the 24 picked lines), `LOO residuals` (vertical sticks from the interpolated surface to the measured pick) |
| **Colour by** | horizon depth *d*, or uncertainty σ |
| **Spatial term σ(x, y)** | band multiplier *k* (0–3), display exaggeration (1–10×, **display only**), vertical exaggeration (1–40×), contour wall, vertical error whiskers |
| **Time-to-depth term** | show/hide the ±0.30 m global envelope |
| **Leave-one-out** | pick one of the 24 lines; the other 23 rebuild its surface and the residuals are drawn on it, with RMSE and max deviation reported |
| **Overlay** | profile positions, survey extent box, reset view |
| **Profile query** (bottom left) | any single profile, with the ±kσ band, the ±0.30 m global envelope and the along-profile repeatability bound drawn separately and to a common vertical scale |
| **Plan view** (bottom right) | map of σ(x, y) |

Mouse: drag to rotate, wheel to zoom, right-drag or Shift+drag to pan, hover the surface to
read depth and σ at that point.

The spatial band and the global envelope **must be drawn at the same exaggeration factor**,
otherwise the true ratio between 0.200 m and 0.300 m is inverted on screen. This is hard-coded
in the viewer, and the current factor is printed in the legend.

## 4. Data

The dataset is the publicly released Schillerslage joint hydrogeophysical data set:

> Igel, J., Günther, T., Müller-Petke, M., Dlugosch, R., & Jiang, C. (2019).
> *Hydrogeophysical data Schillerslage test site, joint MRT ERT GPR* (Version 1.0) [Data set].
> Zenodo. <https://doi.org/10.5281/zenodo.2686824> — licensed **CC-BY-4.0**.

Field site, acquisition and the coupling of the four methods (GPR, ERT, MRT, boreholes) are
described in:

> Jiang, C., Igel, J., Dlugosch, R., Müller-Petke, M., Günther, T., Helms, J., Lang, J., &
> Winsemann, J. (2020). Magnetic resonance tomography constrained by ground-penetrating radar
> for improved hydrogeophysical characterization. *Geophysics*, 85(6), JM13–JM26.
> <https://doi.org/10.1190/GEO2020-0052.1>

Only the GPR picks of interface RF4 (`RF4.pck`) are used here; ERT, MRT and the cores serve as
independent checks and background. Time-to-depth conversion keeps the original **CMP layered
velocity model (0.125 / 0.085 / 0.065 m/ns)** rather than a single velocity — the 0.30 m maximum
deviation from the cores is quoted from the original study and is **not** re-calibrated here.

Interpolation is normalized convolution (Knutsson & Westin, 1993,
<https://doi.org/10.1109/CVPR.1993.341081>); the surface does not pass through the picks. The
fit residual against the 4 990 picks is RMSE 0.116 m (median 0.057 m, max 0.519 m). That number
measures how closely the surface hugs the picks, **not** how far it is from the true interface,
and is therefore not used as an error term anywhere in the analysis.

## 5. Computing environment

The viewer itself has **no dependencies** — plain HTML5 canvas and vanilla JavaScript.

The fields embedded in it were produced by the accompanying analysis pipeline, which ran on
Python 3.13.14 with NumPy 2.5.3 and SciPy 1.18.1. Normalized convolution is self-implemented
on top of `scipy.ndimage.gaussian_filter`; no third-party geophysics package is involved.

## 6. Repository contents

```
horizon3d.html   the interactive viewer (single self-contained file)
preview.png      screenshot used in this README
README.md        this file
LICENSE          MIT licence for the code
```

The analysis pipeline (pick parsing, normalized-convolution interpolation, 24-fold
leave-one-out, σ inversion, variance decomposition, figure scripts), the machine-readable
profile coordinates, the leave-one-out residuals and the σ field are released separately with
the manuscript; they are **not** included in this repository.

## 7. Citation

If you use this viewer or the fields it displays, please cite the manuscript once it is
published. Until then:

```bibtex
@misc{gpr_horizon_uncertainty_viz,
  title  = {Uncertainty-aware 3D visualization of a {GPR} horizon under sparse profile coverage},
  author = {The Authors},
  year   = {2026},
  note   = {Interactive viewer, companion to a manuscript in preparation},
  url    = {https://github.com/<owner>/<repo>}
}
```

Please also cite the data set (Igel et al., 2019) and the original field study (Jiang et al.,
2020) listed in §4.

## 8. License

The **code** (HTML, CSS, JavaScript) is released under the **MIT License** — see
[`LICENSE`](LICENSE).

The **derived geophysical fields embedded in `horizon3d.html`** (horizon depths, σ field,
leave-one-out residuals, pick coordinates) are derived from the Schillerslage data set and are
redistributed under **CC-BY-4.0**, inherited from the source. Attribution is given in §4. If
you reuse these fields, keep the attribution to Igel et al. (2019) and to the accompanying
manuscript.

---

## 中文说明

这是一个单文件、零依赖的交互式可视化原型，用来展示稀疏测线约束下 GPR 层位重建的**空间不确定度**。

**怎么打开**：下载 `horizon3d.html`，双击即可，不需要安装任何东西、不需要起服务、不联网。
文件约 0.46 MB，全部数据已内嵌，无任何外部请求。

**它想说明的一件事**：一张光滑曲面交付出去，使用者不知道哪一段该怀疑。所以这里把
σ(x, y) 场和曲面画在同一屏上，并**把三项误差分开报、不合成**——拾取项（中位 0.310 m）、
空间项（中位 0.200 m）、时深项（≤ 0.30 m）。其中时深项是个全局常数，比空间项中位还大，
绝对埋深的不确定度由它主导，加密测线也降不下来。

**一个必须注意的读法**：σ 是局部平均绝对残差尺度（MAD 型），**不是标准差**。±kσ 带的
经验覆盖率是 52.5 % / 98.6 %，不对应 68 % / 95 %，只能当"哪一段结论薄"的相对指标读，
不能当置信区间。

**数据来源**：Schillerslage 多手段水文地球物理试验场公开数据集（Igel et al., 2019,
Zenodo, CC-BY-4.0），原始野外与解释见 Jiang et al. (2020)。本文只用了其中的 GPR 人工拾取
界面 RF4。
