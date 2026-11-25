# GPR-CG 论文数据发布包（Data availability 承诺项）

对应稿件 `Data availability` 段承诺：24 line-coordinate files / leave-one-out residuals / scale field / all figure scripts。

| 文件 | 字节 | sha256(16) | 说明 |
|---|---|---|---|
| schill_lines.json | 119233 | 6d962563517c7c91 | 24 条测线坐标（原始） |
| schill_lines_rebuilt.json | 114789 | 628a5b945fd8d4c0 | 24 条测线坐标（重建核对） |
| rf4_grid.npz | 271725 | d31c9d70a636b6d5 | 拾取点/留一残差/σ 场/网格（含 4691 残差、7739 有效节点） |
| figure_scripts\v09_figs.py | 8805 | 8900ca83ae698b58 | 图件生成脚本 |
| figure_scripts\parse_picks.py | 4327 | bc0f90953be32ff7 | 图件生成脚本 |
| figure_scripts\make_lines_json.py | 5917 | 970373f84c93be89 | 图件生成脚本 |
| figure_scripts\recompute_cov.py | 1188 | 6261ea85ad1839e6 | 图件生成脚本 |
| figure_scripts\plot_radar_profile_RTA100_0019_v5.py | 6011 | e543ff378d6534be | 新 Fig.2 / fig10 雷达剖面生成脚本；黄线顶点已内嵌，原始 rd3/RF4.pck 需从 Zenodo 下载 |
| figures\fig01_layout.png | 474872 | 8f3887db1522fd64 | 成品图件 |
| figures\fig01_layout.pdf | 80587 | c139144f92346ed0 | 成品图件 |
| figures\fig02_grid.png | 198286 | 4dcd6835d2d897ab | 成品图件 |
| figures\fig02_grid.pdf | 23659 | b6fe4414a2181979 | 成品图件 |
| figures\fig03_surface.png | 611075 | 25fb99c4cff67309 | 成品图件 |
| figures\fig03_surface.pdf | 498583 | 4302d8a3835f062b | 成品图件 |
| figures\fig04_sigma.png | 253715 | f3a9cc2d30996120 | 成品图件 |
| figures\fig04_sigma.pdf | 48505 | 4543f03bbc6217e8 | 成品图件 |
| figures\fig05_interdist.png | 382338 | bd8c314732d943cd | 成品图件 |
| figures\fig05_interdist.pdf | 275821 | c140421221873ad7 | 成品图件 |
| figures\fig06_loo.png | 132516 | a7f93dc801c039bd | 成品图件 |
| figures\fig06_loo.pdf | 27961 | 6abc906b1fe81469 | 成品图件 |
| figures\fig07_bias.png | 164573 | a6d898a516958bbb | 成品图件 |
| figures\fig07_bias.pdf | 38286 | 90142976661468fe | 成品图件 |
| figures\fig08_cross.png | 213105 | f8cf40a82c091183 | 成品图件 |
| figures\fig08_cross.pdf | 39076 | ef6cd6e28fbd28fe | 成品图件 |
| figures\fig09_terms.png | 165143 | 2b2d0318db531887 | 成品图件 |
| figures\fig09_terms.pdf | 28440 | d2605668acffbea9 | 成品图件 |
| figures\fig10_radar_profile_RTA100_0019.png | 701252 | 1148b5f09b300053 | 成品图件 |

## 口径说明

- 残差与 σ 场来自 24 次留一交叉验证，σ 在有效区（7739 节点）计算，有效区中位 0.200 m、P90 0.348 m。
- `fig10_radar_profile_RTA100_0019.png` 为本次新增的剖面图（图 2），纵轴双程旅行时 0–300 ns；生成脚本为 `figure_scripts\plot_radar_profile_RTA100_0019_v5.py`。
- 24 条测线坐标以单一 JSON 交付：`schill_lines.json` 的 `lines` 数组含 24 条线（meta.n_lines=24，4990 个拾取点），每条保留原始线名与 x/y/z；`schill_lines_rebuilt.json` 为独立重建核对版，两者逐点一致。
- 原始数据（Schillerslage Zenodo DOI 10.5281/zenodo.2686824）不在本包内，需读者自行下载。
