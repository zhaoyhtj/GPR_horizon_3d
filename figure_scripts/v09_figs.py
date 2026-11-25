# -*- coding: utf-8 -*-
"""在 _v09_draft.docx 上继续：表格减列、图题重排并插入图 3、替换图件、文献增删。"""
import copy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph

ROOT = Path(r"C:/Users/hanxj/WorkBuddy AI/2026-09-21-08-33-17/gpr-cg-paper")
FIGS = ROOT / "out" / "figs"
SRC = ROOT / "manuscript" / "_v09_draft.docx"
OUT = ROOT / "manuscript" / "_v09_draft2.docx"

doc = Document(str(SRC))


def rewrite(p, segments):
    tmpl = None
    for r in p.runs:
        rpr = r._r.find(qn("w:rPr"))
        if rpr is not None and r.font.bold is not True:
            tmpl = copy.deepcopy(rpr)
            break
    if tmpl is None:
        for r in p.runs:
            rpr = r._r.find(qn("w:rPr"))
            if rpr is not None:
                tmpl = copy.deepcopy(rpr)
                break
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    for text, bold in segments:
        run = p.add_run(text)
        if tmpl is not None:
            run._r.insert(0, copy.deepcopy(tmpl))
        if bold is not None:
            run.font.bold = bold


# ================= 1. 表格 =================
def delete_col(table, idx):
    tbl = table._tbl
    grid = tbl.find(qn("w:tblGrid"))
    if grid is not None:
        cols = grid.findall(qn("w:gridCol"))
        if idx < len(cols):
            grid.remove(cols[idx])
    for row in table.rows:
        tcs = row._tr.findall(qn("w:tc"))
        if idx < len(tcs):
            row._tr.remove(tcs[idx])


# 表 4：删 ±2σ 列（3）与"相当于几倍标准差"列（1），重建为 3 列
t4 = doc.tables[3]
delete_col(t4, 3)
delete_col(t4, 1)
vals = [["k", "±kσ 覆盖率", "同倍数高斯参照"],
        ["1", "52.5%", "57.6%"],
        ["2", "98.6%", "89.0%"]]
for r, row in enumerate(t4.rows):
    for c, cell in enumerate(row.cells):
        cell.text = vals[r][c]

# 表 5：删 ×1.2533 后 ±2σ（6）与 ±1σ（5）
t5 = doc.tables[4]
delete_col(t5, 6)
delete_col(t5, 5)

# 表 7：删 ×1.2533 后（5）
t7 = doc.tables[6]
delete_col(t7, 5)

# 表 4 题注补口径说明
for p in doc.paragraphs:
    if p.text.startswith("表 4 留一残差对 σ 的经验覆盖率"):
        rewrite(p, [("表 4", True),
                    (" 留一残差对 σ 的经验覆盖率（n = 4691；σ 为 MAD 型尺度，"
                     "高斯参照按 k × 0.80 倍标准差计）。", None)])
        break

# ================= 2. 图题重排 =================
CAP = {
    1: ("1", "Schillerslage 试验场的 GPR 测线与 RF4 拾取。(a) 18 条 x 向剖面（垂距 10.000 m）与 6 条 y 向剖面"
              "（垂距 50.000 m），4990 个拾取点按界面深度着色。(b) 各网格节点的支撑状态，灰色为到最近拾取点距离"
              "超过 9 m 掩膜阈值、不参与层面构建的区域；测线按族着色并以实线、虚线区分（x 向蓝实线，y 向橙虚线）。"),
    2: ("4", "空间项 σ(x, y)。(a) 由 24 次逐线留一反演得到，仅在有效区内绘制（7739 个节点）；白线为测线，"
              "红圈为全局最大值 0.669 m（−72.5, 62.5）。(b) 各方位分区与最北端（y ≥ 110 m）的 σ 中位，"
              "横轴为 MAD 尺度。五个方位分区的差别不超过 0.03 m；最北端 0.403 m。"),
    3: ("6", "留一残差按测线族的分布。(a) 两族残差的密度直方图（组距 0.04 m）。(b) 残差绝对值中位数与留一缺口"
              "的关系。x 向族的缺口越大、残差越小，y 向族基本持平。"),
    4: ("7", "逐线系统偏移。(a) 18 条 x 向剖面各自的平均残差，横轴为该线的中位 y，标准差 0.1935 m，量程 0.745 m。"
              "(b) 6 条 y 向剖面，横轴为该线的中位 x，两族横轴各用本族坐标。(c) 用 18 条 x 向剖面构建层面、"
              "检验 6 条 y 向剖面的 899 个拾取点；RMSE 0.3598 m，与该族自身的留一 RMSE 相同，属插值器自检。"),
    5: ("8", "正交测线交点处的深度差。(a) 直方图比较精确内插（66 对）与交点 ±0.5 m 内最近拾取点（81 对）的深度差。"
              "精确内插差值的中位数为 0.310 m、P90 为 0.593 m、最大值为 0.895 m。(b) 66 个可精确内插交点的平面位置，"
              "颜色表示 |Δz|。"),
    6: ("9", "三项误差的量级与空间性质。(a) 三项误差与沿线重复性对照的量级（对数横轴，竖线为 P90）。"
              "(b) y = 0 m 剖面上空间项（±2 倍 MAD 尺度，浅蓝）与时深项（±0.30 m，浅橙）的分布，"
              "两者共用同一夸大倍数。图例写作 ±2×MAD scale，以免与标准差混淆。"),
    7: ("5", "到最近交点的距离与误差尺度的空间对应。(a) 4691 个残差点的 |r|，白色十字为 90 个真实交点。"
              "(b) 7739 个有效节点的 σ，色标为 MAD 尺度。(b) 中 σ 的高值呈沿 y 向剖面的条带状，并在最北端稀疏区成片升高。"),
    8: ("2", "正交测线交点处的深度内插。(a) 24 条测线与 90 个真实交点；另有 18 个延长线交点位于实际覆盖范围之外。"
              "x 向测线以蓝色实线表示，y 向测线以橙色虚线表示。(b) 将交点两侧拾取深度分别沿 x 向和 y 向测线"
              "线性内插至交点坐标，读取同一位置上的深度差。"),
}
CAP3 = ("3", "RF4 顶界的三维重建成果。(a) 归一化卷积插值所得地层曲面，按深度着色；灰色半透明面为上下各 2σ(x, y) "
             "的包络，只含空间项。(b) 同一曲面按 σ 着色，高值带沿 y 向剖面分布。两幅采用同一透视视角，"
             "垂向比例经放大以便观察包络厚度；曲面上叠加等间距参考网格，仅用于判读起伏，不代表数据点位置。")

i_cap = next(i for i, p in enumerate(doc.paragraphs) if p.text.strip() == "图题")
els = []
for k in range(1, 9):
    img_p = doc.paragraphs[i_cap + 2 * k - 1]
    cap_p = doc.paragraphs[i_cap + 2 * k]
    els.append((img_p._p, cap_p._p, cap_p))

# 先按原图号改题注文字
for k in range(1, 9):
    num, text = CAP[k]
    rewrite(els[k - 1][2], [(f"图 {num}", True), (" " + text, None)])

anchor = doc.paragraphs[i_cap]._p
for img, cap, _ in els:
    img.getparent().remove(img)
    cap.getparent().remove(cap)

order = [1, 8, None, 2, 7, 3, 4, 5, 6]
cur = anchor
for k in order:
    if k is None:
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.add_run().add_picture(str(FIGS / "fig03_surface.png"), width=Cm(13.97))
        cur.addnext(p_img._p)
        cur = p_img._p
        cap_el = copy.deepcopy(els[0][1])
        cur.addnext(cap_el)
        para = Paragraph(cap_el, doc.paragraphs[0]._parent)
        rewrite(para, [(f"图 {CAP3[0]}", True), (" " + CAP3[1], None)])
        cur = cap_el
    else:
        img, cap, _ = els[k - 1]
        cur.addnext(img)
        cur = img
        cur.addnext(cap)
        cur = cap

# ================= 3. 替换图件 =================
MAP = {"/word/media/image1.png": "fig01_layout.png",
       "/word/media/image2.png": "fig04_sigma.png",
       "/word/media/image3.png": "fig06_loo.png",
       "/word/media/image4.png": "fig07_bias.png",
       "/word/media/image5.png": "fig08_cross.png",
       "/word/media/image6.png": "fig09_terms.png",
       "/word/media/image7.png": "fig05_interdist.png",
       "/word/media/image8.png": "fig02_grid.png"}
n_rep = 0
for rel in doc.part.rels.values():
    if rel.reltype.endswith("/image"):
        key = str(rel.target_part.partname)
        if key in MAP:
            rel.target_part._blob = (FIGS / MAP[key]).read_bytes()
            n_rep += 1
print("替换图件", n_rep, "张")

# ================= 4. 文献 =================
paras = doc.paragraphs
i_lang = next(i for i, p in enumerate(paras) if p.text.startswith("Lang, J., & Winsemann"))
i_mull = next(i for i, p in enumerate(paras) if p.text.startswith("Müller-Petke"))

# 插 Patriarca（在 Müller-Petke 之后）
pat_el = copy.deepcopy(paras[i_mull]._p)
paras[i_mull]._p.addnext(pat_el)
para = Paragraph(pat_el, paras[0]._parent)
rewrite(para, [("Patriarca, C., Miorali, M., Slob, E., & Lambot, S. (2013). Uncertainty quantification in "
                "off-ground monostatic ground penetrating radar. IEEE Transactions on Antennas and Propagation, "
                "61(6), 3334–3344. doi:10.1109/TAP.2013.2251597", None)])

# 删 Lang & Winsemann
paras[i_lang]._p.getparent().remove(paras[i_lang]._p)

doc.save(str(OUT))
print("已保存", OUT, OUT.stat().st_size)
