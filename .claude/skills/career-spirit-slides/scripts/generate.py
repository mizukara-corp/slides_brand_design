#!/usr/bin/env python3
"""
career-spirit-slides 生成スクリプト
TEMPLATE.pptx（24枚）をテンプレートとして、YAMLアウトラインから PPTX を生成する。

使い方:
  python generate.py outline.yaml output.pptx [--template /path/to/TEMPLATE.pptx]

TEMPLATE.pptx のスライドインデックス（make_template.py で生成）:
  ── ベース（テキスト編集可・6枚）──
  [3] title_light  [4] question  [5] answer  [6] content_list_4  [7] memo  [8] profile

  ── fixed プリセット（13枚）──
  [0] title         [1] section_dark   [2] section_check
  [9]  be_do_have      [10] iceberg          [11] loop_diagram
  [12] trap_diagram    [13] walls4           [14] goal_brake
  [15] step3_cards     [16] timeline_kpi     [17] group_phases
  [18] case_study

  ── fillable プリセット（5枚）──
  [19] flow4_horizontal  [20] return_card  [21] divided_world
  [22] stats_card        [23] before_after
"""

import sys
import copy
import argparse
import os
import datetime
from lxml import etree

try:
    import yaml
except ImportError:
    print("PyYAML が見つかりません。pip install pyyaml --break-system-packages でインストール")
    sys.exit(1)

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("python-pptx が見つかりません。pip install python-pptx --break-system-packages でインストール")
    sys.exit(1)

# ──────────────────────────────────────────────
# ブランドカラー / フォント
# ──────────────────────────────────────────────
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
ORANGE     = RGBColor(0xEC, 0x6F, 0x1A)   # キャリスピ オレンジ
DARK       = RGBColor(0x1A, 0x1A, 0x1A)
GRAY       = RGBColor(0x88, 0x88, 0x88)
LIGHT_GRAY = RGBColor(0xEC, 0xEC, 0xEC)
LINE_DARK  = RGBColor(0x44, 0x44, 0x44)

JP_FONT = "メイリオ"
EN_FONT = "Helvetica"

# ──────────────────────────────────────────────
# TEMPLATE.pptx のスライドインデックス
# ── ベーステンプレート（テキスト編集可） ──
# ──────────────────────────────────────────────
TEMPLATE_MAP = {
    "title_light":     3,
    "question":        4,
    "answer":          5,
    "content_list_4":  6,
    "memo":            7,
    "profile":         8,
}

# ── fixed プリセット: そのままコピーするだけ ──
PRESET_MAP = {
    # カバー/ディバイダー（テキスト編集なし）
    "title":         0,
    "section_dark":  1,
    "section_check": 2,
    # 図解プリセット
    "be_do_have":    9,
    "iceberg":      10,
    "loop_diagram": 11,
    "trap_diagram": 12,
    "walls4":       13,
    "goal_brake":   14,
    "step3_cards":  15,
    "timeline_kpi": 16,
    "group_phases": 17,
    "case_study":   18,
}

# ── fillable プリセット: レイアウト固定・指定テキストのみ変更 ──
# slots: yaml_key → DFS-flat shape index
FILLABLE_MAP = {
    "flow4_horizontal": {
        "idx": 19,
        "slots": {
            "title":     0,   # 上部タイトル
            "stage":     4,   # 中段ラベル（例: "パターン化されている"）
            "box1":      5,   # 1つ目のBOX
            "box2":      6,   # 2つ目
            "box3":      7,   # 3つ目
            "box4":      8,   # 4つ目
            "footnote":  9,   # 下部注記
        },
    },
    "return_card": {
        "idx": 20,
        "slots": {
            "title":     0,   # 例: "01　時間的リターン"
        },
    },
    "divided_world": {
        "idx": 21,
        "slots": {
            "title":     0,   # 上部タイトル（質問形式可）
        },
    },
    "stats_card": {
        "idx": 22,
        "slots": {
            "title":     0,   # 上部タイトル
            "label":     1,   # 大数値の上ラベル
            "number":    2,   # 大きな数値（例: "+153.8"）
            "unit":      3,   # 単位（例: "万円"）
            "footnote":  4,   # 下部注記
        },
    },
    "before_after": {
        "idx": 23,
        "slots": {
            "title":     0,   # 上部タイトル
            "before":    7,   # 左下"ずっと変われない"等
            "after":     9,   # 右下"人生が変わる"等
        },
    },
}

# ──────────────────────────────────────────────
# テキストスロットのマッピング（テキストシェイプのインデックス → YAML フィールド名）
# 通常レイアウト（TEMPLATE_MAP のタイプ）で使用
# ──────────────────────────────────────────────
SLOT_MAP = {
    "title_light":    {1: "title"},        # [0] はページ番号なのでスキップ
    "question":       {0: "main_text"},
    "answer":         {0: "main_text"},
    "content_list_4": {
        0: "title",
        1: "item1",
        2: "item2",
        3: "item3",
        4: "item4",
    },
    "memo":           {0: "content"},
    "profile": {
        1:  "name",         # 例: "島田 隆則"
        2:  "name_en",      # 例: "/ Takanori Shimada"
        3:  "affiliation",  # 所属（複数行可）
        4:  "role",         # 役割
        6:  "career1",
        7:  "career2",
        8:  "career3",
        9:  "expertise1",
        10: "expertise2",
        11: "expertise3",
    },
}

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R_EMBED = f"{{{NS_R}}}embed"
R_ID    = f"{{{NS_R}}}id"
R_HREF  = f"{{{NS_R}}}href"


# ──────────────────────────────────────────────
# スライド複製（埋め込み画像のリレーションシップも再現）
# ──────────────────────────────────────────────
def duplicate_slide(prs, template_idx):
    template = prs.slides[template_idx]
    new_slide = prs.slides.add_slide(template.slide_layout)

    rId_map = {}
    for rel in template.part.rels.values():
        reltype_short = rel.reltype.split("/")[-1]
        if reltype_short in ("slideLayout", "notesSlide"):
            continue
        if rel.is_external:
            new_rId = new_slide.part.target_ref(rel.reltype, rel.target_ref)
        else:
            new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
        rId_map[rel.rId] = new_rId

    tree_copy = copy.deepcopy(template.shapes._spTree)
    for elem in tree_copy.iter():
        for attr in (R_EMBED, R_ID, R_HREF):
            if attr in elem.attrib and elem.attrib[attr] in rId_map:
                elem.attrib[attr] = rId_map[elem.attrib[attr]]

    dst_tree = new_slide.shapes._spTree
    for child in list(dst_tree):
        dst_tree.remove(child)
    for child in list(tree_copy):
        dst_tree.append(child)

    return new_slide


# ──────────────────────────────────────────────
# スライドコピー（別 prs 間の移送）
# ──────────────────────────────────────────────
def copy_slide_from(src_prs, src_idx, dst_prs):
    src_slide = src_prs.slides[src_idx]
    new_slide = dst_prs.slides.add_slide(dst_prs.slide_layouts[0])

    rId_map = {}
    for rel in src_slide.part.rels.values():
        reltype_short = rel.reltype.split("/")[-1]
        if reltype_short in ("slideLayout", "notesSlide"):
            continue
        if rel.is_external:
            new_rId = new_slide.part.target_ref(rel.reltype, rel.target_ref)
        else:
            partname = rel.target_part.partname
            existing_part = next(
                (p for p in dst_prs.part.package.iter_parts() if p.partname == partname),
                None,
            )
            if existing_part is not None:
                target_part = existing_part
            else:
                target_part = copy.deepcopy(rel.target_part)
                dst_prs.part.package._parts[partname] = target_part
            new_rId = new_slide.part.relate_to(target_part, rel.reltype)
        rId_map[rel.rId] = new_rId

    tree_copy = copy.deepcopy(src_slide.shapes._spTree)
    for elem in tree_copy.iter():
        for attr in (R_EMBED, R_ID, R_HREF):
            if attr in elem.attrib and elem.attrib[attr] in rId_map:
                elem.attrib[attr] = rId_map[elem.attrib[attr]]

    dst_tree = new_slide.shapes._spTree
    for child in list(dst_tree):
        dst_tree.remove(child)
    for child in list(tree_copy):
        dst_tree.append(child)

    return new_slide


def move_slide_to(prs, from_idx, to_idx):
    sldIdLst = prs.slides._sldIdLst
    items = list(sldIdLst)
    item = items.pop(from_idx)
    items.insert(to_idx, item)
    for el in list(sldIdLst):
        sldIdLst.remove(el)
    for el in items:
        sldIdLst.append(el)


def get_text_shapes(slide):
    return [s for s in slide.shapes if s.has_text_frame]


def get_flat_text_shapes(shapes):
    """グループシェイプを再帰的に展開し、全テキストシェイプをDFS順に返す。"""
    result = []
    for s in shapes:
        if hasattr(s, 'shapes'):
            result.extend(get_flat_text_shapes(s.shapes))
        elif s.has_text_frame:
            result.append(s)
    return result


# ──────────────────────────────────────────────
# テキストシェイプの文字列を置換（既存の書式を保持）
# ──────────────────────────────────────────────
def set_shape_text(shape, new_text):
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    lines = str(new_text).strip().split("\n")
    existing_paras = tf.paragraphs
    n_existing = len(existing_paras)
    n_lines = len(lines)

    if n_lines > n_existing and n_existing > 0:
        last_p_xml = copy.deepcopy(existing_paras[-1]._p)
        txBody = tf._txBody
        for _ in range(n_lines - n_existing):
            txBody.append(copy.deepcopy(last_p_xml))

    paras = tf.paragraphs
    for i, para in enumerate(paras):
        if i < n_lines:
            line = lines[i]
            runs = para.runs
            if runs:
                runs[0].text = line
                for run in runs[1:]:
                    run.text = ""
            else:
                p_elem = para._p
                existing_r = p_elem.find(f"{{{NS_A}}}r")
                if existing_r is None:
                    r_elem = etree.SubElement(p_elem, f"{{{NS_A}}}r")
                    t_elem = etree.SubElement(r_elem, f"{{{NS_A}}}t")
                    t_elem.text = line
                else:
                    t_elem = existing_r.find(f"{{{NS_A}}}t")
                    if t_elem is not None:
                        t_elem.text = line
        else:
            runs = para.runs
            if runs:
                runs[0].text = ""
                for run in runs[1:]:
                    run.text = ""


# ──────────────────────────────────────────────
# 新タイプ用：テキスト枠の動的追加ヘルパー
# ──────────────────────────────────────────────
def _add_textbox(slide, text, x_in, y_in, w_in, h_in, font_size, color,
                 bold=False, align=PP_ALIGN.LEFT, font_name=JP_FONT):
    """指定位置・サイズ・フォントスタイルでテキストボックスを追加。\n は段落区切り。"""
    if text is None:
        return None
    tx = slide.shapes.add_textbox(Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in))
    tf = tx.text_frame
    tf.word_wrap = True
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.color.rgb = color
        run.font.bold = bold
        run.font.name = font_name
    return tx


def _add_hline(slide, x1_in, y_in, x2_in, color, thickness_pt=0.7):
    line = slide.shapes.add_connector(1, Inches(x1_in), Inches(y_in), Inches(x2_in), Inches(y_in))
    line.line.color.rgb = color
    line.line.width = Pt(thickness_pt)
    return line


def _clear_text_shape(slide, contains_text):
    """slide 内のテキストシェイプで contains_text を含むものを空にする。"""
    for shp in slide.shapes:
        if shp.has_text_frame and contains_text in shp.text_frame.text:
            set_shape_text(shp, " ")


# ──────────────────────────────────────────────
# アイコンライブラリ
# ──────────────────────────────────────────────
# card2 / card3 / content_list_4 / agenda などに `*_icon` フィールドで指定する。
# 値の解決順:
#   1. 名前が _SIMPLE_SHAPE_ICONS にあれば → MSO_SHAPE 図形を 1 個描画
#   2. 名前が _COMPOSITE_ICONS にあれば → 複数図形を組み合わせた複合アイコンを描画
#   3. 名前が _GLYPH_MAP にあれば → そのグリフを大きなテキストで描画
#   4. それ以外 → 値そのものを文字（絵文字想定）として描画
# 全アイコンは「オレンジの円 + 中に白い形/グリフ」というトンマナで統一される。

_SIMPLE_SHAPE_ICONS = {
    # 形そのものをアイコンとして使うケース
    "star":          MSO_SHAPE.STAR_5_POINT,
    "star4":         MSO_SHAPE.STAR_4_POINT,
    "star8":         MSO_SHAPE.STAR_8_POINT,
    "heart":         MSO_SHAPE.HEART,
    "lightning":     MSO_SHAPE.LIGHTNING_BOLT,
    "flash":         MSO_SHAPE.LIGHTNING_BOLT,
    "sun":           MSO_SHAPE.SUN,
    "moon":          MSO_SHAPE.MOON,
    "diamond":       MSO_SHAPE.DIAMOND,
    "hexagon":       MSO_SHAPE.HEXAGON,
    "pentagon":      MSO_SHAPE.PENTAGON,
    "octagon":       MSO_SHAPE.OCTAGON,
    "decagon":       MSO_SHAPE.DECAGON,
    "cloud":         MSO_SHAPE.CLOUD,
    "explosion":     MSO_SHAPE.EXPLOSION1,
    "burst":         MSO_SHAPE.EXPLOSION2,
    "smiley":        MSO_SHAPE.SMILEY_FACE,
    "donut":         MSO_SHAPE.DONUT,
    "wave":          MSO_SHAPE.WAVE,
    "tear":          MSO_SHAPE.TEAR,
    # 矢印
    "arrow_right":   MSO_SHAPE.RIGHT_ARROW,
    "arrow_up":      MSO_SHAPE.UP_ARROW,
    "arrow_down":    MSO_SHAPE.DOWN_ARROW,
    "arrow_left":    MSO_SHAPE.LEFT_ARROW,
    "arrow_lr":      MSO_SHAPE.LEFT_RIGHT_ARROW,
    "arrow_ud":      MSO_SHAPE.UP_DOWN_ARROW,
    "growth":        MSO_SHAPE.UP_ARROW,
    "uturn":         MSO_SHAPE.U_TURN_ARROW,
    "chevron":       MSO_SHAPE.CHEVRON,
    # 機能/概念
    "gear":          MSO_SHAPE.GEAR_6,
    "gear9":         MSO_SHAPE.GEAR_9,
    "plus":          MSO_SHAPE.MATH_PLUS,
    "minus":         MSO_SHAPE.MATH_MINUS,
    "multiply":      MSO_SHAPE.MATH_MULTIPLY,
    "divide":        MSO_SHAPE.MATH_DIVIDE,
    "equal":         MSO_SHAPE.MATH_EQUAL,
    "not_equal":     MSO_SHAPE.MATH_NOT_EQUAL,
    "no":            MSO_SHAPE.NO_SYMBOL,
    "block":         MSO_SHAPE.NO_SYMBOL,
}


def _add_oval(slide, x_in, y_in, w_in, h_in, color, line_color=None):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    if line_color is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line_color
        s.line.width = Pt(1)
    return s


def _add_rect(slide, x_in, y_in, w_in, h_in, color, rotation=0, rounded=False):
    shp_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(shp_type, Inches(x_in), Inches(y_in), Inches(w_in), Inches(h_in))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    if rotation:
        s.rotation = rotation
    return s


# ── 複合アイコン（複数図形でアイコンを構成） ──

def _icon_pencil(slide, cx, cy, size, fg, bg):
    """鉛筆: 斜めの長方形の本体 + 三角形の先端"""
    # 本体（45度回転した長方形）
    body_w, body_h = size * 0.95, size * 0.22
    body_x = cx - body_w / 2
    body_y = cy - body_h / 2
    body = _add_rect(slide, body_x, body_y, body_w, body_h, fg, rotation=-35)
    # 先端のキャップ（白い三角形を本体の上に被せる）
    cap_w, cap_h = size * 0.22, size * 0.22
    cap = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(cx + size * 0.18), Inches(cy - size * 0.32),
        Inches(cap_w), Inches(cap_h),
    )
    cap.fill.solid(); cap.fill.fore_color.rgb = bg; cap.line.fill.background()
    cap.rotation = -35


def _icon_chart(slide, cx, cy, size, fg, bg):
    """棒グラフ: 高さの違う 3 本のバー"""
    bar_w = size * 0.18
    gap = size * 0.07
    total_w = bar_w * 3 + gap * 2
    start_x = cx - total_w / 2
    base_y = cy + size * 0.4
    heights = [0.35, 0.6, 0.85]
    for i, h_ratio in enumerate(heights):
        h = size * h_ratio
        x = start_x + i * (bar_w + gap)
        _add_rect(slide, x, base_y - h, bar_w, h, fg)


def _icon_target(slide, cx, cy, size, fg, bg):
    """ターゲット: 同心円 3 つ"""
    for i, ratio in enumerate([1.0, 0.66, 0.33]):
        d = size * ratio
        h = d / 2
        c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - h), Inches(cy - h), Inches(d), Inches(d))
        c.fill.solid()
        c.fill.fore_color.rgb = fg if i % 2 == 0 else bg
        c.line.fill.background()


def _icon_check(slide, cx, cy, size, fg, bg):
    """チェックマーク: 2 つの細長い長方形を組んで描く"""
    # 短い棒（左下から中央へ）
    s1 = _add_rect(slide, cx - size * 0.30, cy + size * 0.05, size * 0.32, size * 0.13, fg, rotation=45)
    # 長い棒（中央から右上へ）
    s2 = _add_rect(slide, cx - size * 0.05, cy - size * 0.10, size * 0.55, size * 0.13, fg, rotation=-45)


def _icon_lightbulb(slide, cx, cy, size, fg, bg):
    """電球: 円（バルブ）+ 細長い長方形（フィラメント根本）"""
    bulb_d = size * 0.7
    bulb_h = bulb_d / 2
    _add_oval(slide, cx - bulb_h, cy - bulb_h - size * 0.05, bulb_d, bulb_d, fg)
    # 根元
    _add_rect(slide, cx - size * 0.13, cy + size * 0.30, size * 0.26, size * 0.10, fg)
    _add_rect(slide, cx - size * 0.10, cy + size * 0.42, size * 0.20, size * 0.07, fg)


def _icon_clock(slide, cx, cy, size, fg, bg):
    """時計: 円 + 中央の点 + 2 本の針"""
    d = size * 0.95
    h = d / 2
    # 外円
    outer = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - h), Inches(cy - h), Inches(d), Inches(d))
    outer.fill.solid(); outer.fill.fore_color.rgb = fg; outer.line.fill.background()
    # 内側を背景色で空洞化（リング状にする）
    d2 = size * 0.78
    h2 = d2 / 2
    inner = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - h2), Inches(cy - h2), Inches(d2), Inches(d2))
    inner.fill.solid(); inner.fill.fore_color.rgb = bg; inner.line.fill.background()
    # 針（短針・長針）
    _add_rect(slide, cx - size * 0.04, cy - size * 0.22, size * 0.08, size * 0.28, fg)  # 縦針
    _add_rect(slide, cx - size * 0.04, cy - size * 0.04, size * 0.30, size * 0.08, fg)  # 横針
    # 中央の点
    _add_oval(slide, cx - size * 0.06, cy - size * 0.06, size * 0.12, size * 0.12, fg)


def _icon_book(slide, cx, cy, size, fg, bg):
    """本: 角丸長方形のカバー + 中央の縦線（背表紙）+ ページ罫線"""
    # カバー
    cover_w, cover_h = size * 0.95, size * 0.78
    _add_rect(slide, cx - cover_w / 2, cy - cover_h / 2, cover_w, cover_h, fg)
    # 中央の背表紙（背景色の縦線）
    _add_rect(slide, cx - size * 0.04, cy - cover_h / 2, size * 0.08, cover_h, bg)
    # ページ罫線（左右に短い背景色の横線）
    line_h = size * 0.05
    line_w = size * 0.32
    for dy in [-0.20, -0.05, 0.10]:
        _add_rect(slide, cx - cover_w / 2 + size * 0.07, cy + size * dy - line_h / 2, line_w, line_h, bg)
        _add_rect(slide, cx + size * 0.10,                cy + size * dy - line_h / 2, line_w, line_h, bg)


def _icon_flag(slide, cx, cy, size, fg, bg):
    """旗: 縦のポール + 三角形の旗"""
    # ポール
    _add_rect(slide, cx - size * 0.35, cy - size * 0.45, size * 0.08, size * 0.9, fg)
    # 旗（直角三角形）
    flag = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(cx - size * 0.27), Inches(cy - size * 0.45),
        Inches(size * 0.55), Inches(size * 0.40),
    )
    flag.fill.solid(); flag.fill.fore_color.rgb = fg; flag.line.fill.background()


def _icon_search(slide, cx, cy, size, fg, bg):
    """虫眼鏡: 円リング + 斜めの取っ手"""
    d = size * 0.65
    h = d / 2
    cx_ring = cx - size * 0.10
    cy_ring = cy - size * 0.10
    # 外円
    outer = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx_ring - h), Inches(cy_ring - h), Inches(d), Inches(d))
    outer.fill.solid(); outer.fill.fore_color.rgb = fg; outer.line.fill.background()
    # 内側（背景色）
    d2 = size * 0.45
    h2 = d2 / 2
    inner = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx_ring - h2), Inches(cy_ring - h2), Inches(d2), Inches(d2))
    inner.fill.solid(); inner.fill.fore_color.rgb = bg; inner.line.fill.background()
    # 取っ手
    _add_rect(slide, cx + size * 0.10, cy + size * 0.10, size * 0.45, size * 0.13, fg, rotation=-45)


def _icon_key(slide, cx, cy, size, fg, bg):
    """鍵: 円（頭）+ 横棒（軸）+ ギザギザ（小さい矩形2つ）"""
    head_d = size * 0.45
    hh = head_d / 2
    # 頭
    head = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - size * 0.45), Inches(cy - hh), Inches(head_d), Inches(head_d))
    head.fill.solid(); head.fill.fore_color.rgb = fg; head.line.fill.background()
    # 中をくり抜く
    inner_d = size * 0.20
    ih = inner_d / 2
    inner = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(cx - size * 0.45 + (head_d - inner_d) / 2), Inches(cy - ih), Inches(inner_d), Inches(inner_d))
    inner.fill.solid(); inner.fill.fore_color.rgb = bg; inner.line.fill.background()
    # 軸
    _add_rect(slide, cx - size * 0.05, cy - size * 0.07, size * 0.50, size * 0.14, fg)
    # ギザギザ
    _add_rect(slide, cx + size * 0.30, cy + size * 0.07, size * 0.10, size * 0.16, fg)
    _add_rect(slide, cx + size * 0.13, cy + size * 0.07, size * 0.10, size * 0.16, fg)


def _icon_note(slide, cx, cy, size, fg, bg):
    """ノート/書類: 角丸長方形 + 中の横線 3 本"""
    # ベース
    base = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(cx - size * 0.40), Inches(cy - size * 0.45),
        Inches(size * 0.80), Inches(size * 0.90),
    )
    base.fill.solid(); base.fill.fore_color.rgb = fg; base.line.fill.background()
    # 中身（背景色の横線）
    line_w = size * 0.50
    line_x = cx - line_w / 2
    for i, dy in enumerate([-0.20, 0.0, 0.20]):
        _add_rect(slide, line_x, cy + size * dy - size * 0.04, line_w, size * 0.08, bg)


def _icon_record(slide, cx, cy, size, fg, bg):
    """記録: ノートと同じ"""
    _icon_note(slide, cx, cy, size, fg, bg)


def _icon_brain(slide, cx, cy, size, fg, bg):
    """脳: 円 + 横方向のしわ 3 本（簡略化シルエット）"""
    d = size * 0.90
    h = d / 2
    _add_oval(slide, cx - h, cy - h, d, d, fg)
    # 横向きのしわ（背景色の細い楕円を3本）
    for dy, ow in [(-0.25, 0.50), (-0.05, 0.60), (0.18, 0.50)]:
        oh = size * 0.06
        ow_in = size * ow
        _add_oval(slide, cx - ow_in / 2, cy + size * dy - oh / 2, ow_in, oh, bg)


def _icon_heart_fill(slide, cx, cy, size, fg, bg):
    """ハート: MSO_SHAPE.HEART"""
    s = size * 0.85
    h = s / 2
    shp = slide.shapes.add_shape(MSO_SHAPE.HEART, Inches(cx - h), Inches(cy - h), Inches(s), Inches(s))
    shp.fill.solid(); shp.fill.fore_color.rgb = fg; shp.line.fill.background()


def _icon_people(slide, cx, cy, size, fg, bg):
    """人 3 人: 円（頭）+ 半円（胴体）"""
    positions = [
        (cx - size * 0.30, cy - size * 0.05),
        (cx,                cy - size * 0.15),
        (cx + size * 0.30, cy - size * 0.05),
    ]
    for px, py in positions:
        # 頭
        head_d = size * 0.22
        hh = head_d / 2
        _add_oval(slide, px - hh, py - hh, head_d, head_d, fg)
        # 胴（半円 = 楕円の下半分を使うため、楕円を描いて上を切らずにそのまま大きめ楕円で表現）
        body_d = size * 0.30
        _add_oval(slide, px - body_d / 2, py + size * 0.07, body_d, size * 0.24, fg)


def _icon_arrows_lr(slide, cx, cy, size, fg, bg):
    """左右矢印: 比較を示す双方向矢印（横長の LEFT_RIGHT_ARROW を強制）"""
    s = size * 0.95
    shp = slide.shapes.add_shape(
        MSO_SHAPE.LEFT_RIGHT_ARROW,
        Inches(cx - s / 2), Inches(cy - size * 0.20),
        Inches(s), Inches(size * 0.40),
    )
    shp.fill.solid(); shp.fill.fore_color.rgb = fg; shp.line.fill.background()


def _icon_compare(slide, cx, cy, size, fg, bg):
    """比較: 上下に左右逆向きの矢印 2 本"""
    arrow_w = size * 0.85
    arrow_h = size * 0.30
    # 上: 右向き
    a1 = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        Inches(cx - arrow_w / 2), Inches(cy - size * 0.36),
        Inches(arrow_w), Inches(arrow_h),
    )
    a1.fill.solid(); a1.fill.fore_color.rgb = fg; a1.line.fill.background()
    # 下: 左向き
    a2 = slide.shapes.add_shape(
        MSO_SHAPE.LEFT_ARROW,
        Inches(cx - arrow_w / 2), Inches(cy + size * 0.06),
        Inches(arrow_w), Inches(arrow_h),
    )
    a2.fill.solid(); a2.fill.fore_color.rgb = fg; a2.line.fill.background()


def _icon_growth_chart(slide, cx, cy, size, fg, bg):
    """右肩上がり: 上昇する 3 本のバー + 矢印"""
    bar_w = size * 0.13
    gap = size * 0.06
    total_w = bar_w * 3 + gap * 2
    start_x = cx - total_w / 2 - size * 0.05
    base_y = cy + size * 0.35
    for i, h_ratio in enumerate([0.30, 0.50, 0.70]):
        h = size * h_ratio
        x = start_x + i * (bar_w + gap)
        _add_rect(slide, x, base_y - h, bar_w, h, fg)
    # 上向き矢印（右上）
    arr = slide.shapes.add_shape(
        MSO_SHAPE.UP_ARROW,
        Inches(cx + size * 0.20), Inches(cy - size * 0.45),
        Inches(size * 0.25), Inches(size * 0.42),
    )
    arr.fill.solid(); arr.fill.fore_color.rgb = fg; arr.line.fill.background()


def _icon_loop(slide, cx, cy, size, fg, bg):
    """ループ: ドーナツ（リング）+ 上方向の小さな三角形（矢印先端）"""
    # 外円
    d_outer = size * 0.95
    h_outer = d_outer / 2
    _add_oval(slide, cx - h_outer, cy - h_outer, d_outer, d_outer, fg)
    # 内側を背景色でくり抜き → リング
    d_inner = size * 0.55
    h_inner = d_inner / 2
    _add_oval(slide, cx - h_inner, cy - h_inner, d_inner, d_inner, bg)
    # 矢印先端（リング右上に配置・回転）
    tri_w = size * 0.30
    tri_h = size * 0.28
    tri = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_TRIANGLE,
        Inches(cx + size * 0.10), Inches(cy - size * 0.55),
        Inches(tri_w), Inches(tri_h),
    )
    tri.fill.solid(); tri.fill.fore_color.rgb = fg; tri.line.fill.background()
    tri.rotation = 30
    # リングの一部を背景色で消す（矢印部分のギャップ表現）
    gap = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(cx + size * 0.20), Inches(cy - size * 0.55),
        Inches(size * 0.30), Inches(size * 0.28),
    )
    gap.fill.solid(); gap.fill.fore_color.rgb = bg; gap.line.fill.background()
    gap.rotation = 30


_COMPOSITE_ICONS = {
    "compare":  _icon_compare,
    "vs":       _icon_compare,
    "balance":  _icon_compare,
    "loop":     _icon_loop,
    "circular": _icon_loop,
    "cycle":    _icon_loop,
    "repeat":   _icon_loop,
    "pencil":   _icon_pencil,
    "edit":     _icon_pencil,
    "write":    _icon_pencil,
    "chart":    _icon_chart,
    "bar":      _icon_chart,
    "target":   _icon_target,
    "goal":     _icon_target,
    "check":    _icon_check,
    "ok":       _icon_check,
    "tick":     _icon_check,
    "lightbulb": _icon_lightbulb,
    "idea":     _icon_lightbulb,
    "clock":    _icon_clock,
    "time":     _icon_clock,
    "book":     _icon_book,
    "study":    _icon_book,
    "flag":     _icon_flag,
    "milestone": _icon_flag,
    "search":   _icon_search,
    "magnifier": _icon_search,
    "explore":  _icon_search,
    "key":      _icon_key,
    "important": _icon_key,
    "note":     _icon_note,
    "record":   _icon_record,
    "memo":     _icon_note,
    "document": _icon_note,
    "brain":    _icon_brain,
    "think":    _icon_brain,
    "people":   _icon_people,
    "team":     _icon_people,
    "growth_chart": _icon_growth_chart,
    "trend":    _icon_growth_chart,
}


# 名前 → Unicode グリフ（フォント描画フォールバック）
_GLYPH_MAP = {
    "right":    "→",
    "left":     "←",
    "up":       "↑",
    "down":     "↓",
    "infinity": "∞",
    "yen":      "¥",
    "dollar":   "$",
    "percent":  "%",
    "question": "?",
    "exclam":   "!",
}


def _add_icon(slide, icon_spec, cx_in, cy_in, button_size_in,
              bg_color=None, fg_color=None):
    """
    アイコンを (cx, cy) を中心に描画する。

    icon_spec の解釈:
      - None / "" / falsy → 何も描かない
      - "pencil" 等の名前 → ライブラリから検索
      - "📝" / "→" 等 → グリフとしてテキスト描画

    トンマナ: 背景はオレンジの円、前景は白。
    """
    if not icon_spec:
        return None

    bg_color = bg_color if bg_color is not None else ORANGE
    fg_color = fg_color if fg_color is not None else WHITE

    # 1) 背景の円
    half = button_size_in / 2
    bg = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(cx_in - half), Inches(cy_in - half),
        Inches(button_size_in), Inches(button_size_in),
    )
    bg.fill.solid()
    bg.fill.fore_color.rgb = bg_color
    bg.line.fill.background()

    key = str(icon_spec).strip().lower()

    # 2) 単純 MSO_SHAPE
    if key in _SIMPLE_SHAPE_ICONS:
        inner = button_size_in * 0.55
        ih = inner / 2
        shp = slide.shapes.add_shape(
            _SIMPLE_SHAPE_ICONS[key],
            Inches(cx_in - ih), Inches(cy_in - ih),
            Inches(inner), Inches(inner),
        )
        shp.fill.solid()
        shp.fill.fore_color.rgb = fg_color
        shp.line.fill.background()
        return bg

    # 3) 複合アイコン
    if key in _COMPOSITE_ICONS:
        _COMPOSITE_ICONS[key](slide, cx_in, cy_in, button_size_in * 0.55, fg_color, bg_color)
        return bg

    # 4) Glyph マップ
    glyph = _GLYPH_MAP.get(key, str(icon_spec))

    # 5) フォールバック: テキスト描画
    tf = bg.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = glyph
    r.font.size = Pt(int(button_size_in * 32))
    r.font.color.rgb = fg_color
    r.font.bold = True
    r.font.name = JP_FONT
    return bg


# ── 新タイプ: cover ──
def _build_cover(slide, spec):
    seminar  = spec.get("seminar",  "SEMINAR / 2026")
    title    = spec.get("title",    "")
    subtitle = spec.get("subtitle", "")
    _add_textbox(slide, seminar, 0.5, 1.95, 4.0, 0.3, 13, WHITE, bold=True, font_name=EN_FONT)
    if title:
        _add_textbox(slide, title, 0.5, 2.35, 8.5, 1.7, 44, WHITE, bold=True)
    if subtitle:
        _add_textbox(slide, subtitle, 0.5, 4.45, 8.5, 0.5, 15, WHITE)


# ── 新タイプ: agenda ──
def _build_agenda(slide, spec):
    goal_label    = spec.get("goal_label",    "GOAL — 本日のゴール")
    goal_text     = spec.get("goal_text",     "")
    chapter_label = spec.get("chapter_label", "CHAPTERS")
    chapters      = spec.get("chapters", []) or []
    chapter_icons = spec.get("chapter_icons", []) or []   # 任意。アイコン名 or 絵文字のリスト

    # 右側（黒エリア）GOAL
    _add_textbox(slide, goal_label, 4.7, 0.45, 4.5, 0.3, 11, ORANGE, bold=True, font_name=EN_FONT)
    if goal_text:
        _add_textbox(slide, goal_text, 4.7, 0.85, 4.7, 1.4, 17, WHITE, bold=True)

    # CHAPTERS
    _add_textbox(slide, chapter_label, 4.7, 2.55, 4.5, 0.3, 10, ORANGE, bold=True, font_name=EN_FONT)
    n = min(4, len(chapters))
    has_icons = any(chapter_icons[i] if i < len(chapter_icons) else None for i in range(n))
    for i in range(n):
        y = 2.95 + i * 0.55
        ic = chapter_icons[i] if i < len(chapter_icons) else None
        if ic:
            # アイコン円（オレンジ）+ 番号は省略してアイコンのみ
            _add_icon(slide, ic, 4.95, y + 0.22, 0.42, bg_color=ORANGE, fg_color=WHITE)
            text_x = 5.45
        elif has_icons:
            # 同じスライド内で他のチャプターにアイコンがあるなら、番号を円ベースで表示して揃える
            _add_icon(slide, str(i + 1), 4.95, y + 0.22, 0.42, bg_color=ORANGE, fg_color=WHITE)
            text_x = 5.45
        else:
            _add_textbox(slide, f"0{i+1}", 4.7, y, 0.6, 0.4, 16, ORANGE, bold=True, font_name=EN_FONT)
            text_x = 5.4
        _add_textbox(slide, str(chapters[i]), text_x, y + 0.04, 4.0, 0.4, 13, WHITE, bold=True)
        if i < n - 1:
            _add_hline(slide, 4.7, y + 0.5, 9.5, LINE_DARK, thickness_pt=0.5)


# ── 新タイプ: section_rich （title_light を再利用）──
def _build_section_rich(slide, spec):
    section_num = spec.get("section_num", "SECTION 01")
    section_en  = spec.get("section_en",  "")
    section_ja  = spec.get("section_ja",  "")

    # 既存の "セッションの価値" タイトルを消す
    _clear_text_shape(slide, "セッションの価値")

    _add_textbox(slide, section_num, 4.4, 1.55, 3.0, 0.3, 13, ORANGE, bold=True, font_name=EN_FONT)
    if section_en:
        _add_textbox(slide, section_en, 4.4, 1.95, 5.0, 0.4, 21, GRAY, bold=True, font_name=EN_FONT)
    # 区切り線
    _add_hline(slide, 4.4, 2.55, 5.0, ORANGE, thickness_pt=2.5)
    if section_ja:
        _add_textbox(slide, section_ja, 4.4, 2.8, 5.4, 1.5, 32, DARK, bold=True)


# ── 新タイプ: card2 / card3（memo を白背景ベースとして再利用）──
def _build_card_n(slide, spec, n_cards):
    """n_cards: 2 or 3。横並びカード。

    icon オプション:
      - cardN_icon: アイコン名（pencil, target, chart など）または絵文字
        指定するとカード上部中央に大きなオレンジ円アイコンが表示される。
        左上の小さな番号バッジは併存する。
    """
    title = spec.get("title", "")

    # memo の元テキストを消す
    _clear_text_shape(slide, "GOAL ＞ 手段")

    if title:
        _add_textbox(slide, title, 0.45, 0.35, 9.0, 0.5, 22, DARK, bold=True)

    # カード配置
    margin_x  = 0.5
    gap       = 0.25
    available = 10.0 - 2 * margin_x - gap * (n_cards - 1)
    card_w    = available / n_cards
    card_y    = 1.3
    card_h    = 3.7

    # 何かアイコンが指定されているか判定（指定があるカードに合わせて全体レイアウトを調整）
    has_any_icon = any(spec.get(f"card{i+1}_icon") for i in range(n_cards))

    for i in range(n_cards):
        x = margin_x + i * (card_w + gap)
        head = spec.get(f"card{i+1}_title", "")
        body = spec.get(f"card{i+1}_body",  "")
        icon = spec.get(f"card{i+1}_icon")

        # カード背景（角丸・薄グレー）
        rect = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(x), Inches(card_y), Inches(card_w), Inches(card_h),
        )
        rect.fill.solid()
        rect.fill.fore_color.rgb = LIGHT_GRAY
        rect.line.fill.background()

        # 番号バッジ（オレンジ円）
        badge_d = 0.55
        badge = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x + 0.3), Inches(card_y + 0.3),
            Inches(badge_d), Inches(badge_d),
        )
        badge.fill.solid()
        badge.fill.fore_color.rgb = ORANGE
        badge.line.fill.background()
        btf = badge.text_frame
        btf.margin_left = btf.margin_right = btf.margin_top = btf.margin_bottom = 0
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        br = bp.add_run()
        br.text = str(i + 1)
        br.font.size = Pt(18)
        br.font.color.rgb = WHITE
        br.font.bold = True
        br.font.name = EN_FONT

        # カードタイトル（badgeの右）
        if head:
            _add_textbox(slide, head, x + 1.0, card_y + 0.32, card_w - 1.2, 0.5, 16, ORANGE, bold=True)

        # 大きなアイコン（カード中央上部・タイトル下）
        if has_any_icon:
            icon_size = min(1.25, card_w * 0.4)
            icon_cx = x + card_w / 2
            icon_cy = card_y + 1.0 + icon_size / 2
            if icon:
                _add_icon(slide, icon, icon_cx, icon_cy, icon_size,
                          bg_color=ORANGE, fg_color=WHITE)
            # 本文はアイコンの下から
            body_y = icon_cy + icon_size / 2 + 0.20
            body_h = card_y + card_h - body_y - 0.20
        else:
            # アイコン無しの場合は従来レイアウト
            body_y = card_y + 1.05
            body_h = card_h - 1.3

        # カード本文
        if body:
            _add_textbox(slide, body, x + 0.3, body_y, card_w - 0.6, body_h, 13, DARK)


# ──────────────────────────────────────────────
# スライド生成メイン処理
# ──────────────────────────────────────────────
def process_slide(prs, slide_spec):
    slide_type = slide_spec.get("type")

    # ── type: cover （title スライド + テキスト動的注入）──
    if slide_type == "cover":
        new_slide = duplicate_slide(prs, PRESET_MAP["title"])
        _build_cover(new_slide, slide_spec)
        return new_slide

    # ── type: agenda （section_dark + GOAL/CHAPTERS テキスト注入）──
    if slide_type == "agenda":
        new_slide = duplicate_slide(prs, PRESET_MAP["section_dark"])
        _build_agenda(new_slide, slide_spec)
        return new_slide

    # ── type: section_rich （title_light + SECTION/EN/JA テキスト注入）──
    if slide_type == "section_rich":
        new_slide = duplicate_slide(prs, TEMPLATE_MAP["title_light"])
        _build_section_rich(new_slide, slide_spec)
        return new_slide

    # ── type: card2 / card3 （memo を白背景ベースに角丸カードを動的構築）──
    if slide_type == "card2":
        new_slide = duplicate_slide(prs, TEMPLATE_MAP["memo"])
        _build_card_n(new_slide, slide_spec, 2)
        return new_slide
    if slide_type == "card3":
        new_slide = duplicate_slide(prs, TEMPLATE_MAP["memo"])
        _build_card_n(new_slide, slide_spec, 3)
        return new_slide

    # ── type: fillable ──
    if slide_type == "fillable":
        fillable_name = slide_spec.get("name")
        if fillable_name not in FILLABLE_MAP:
            print(
                f"  [警告] 不明なfillable名: {fillable_name}  "
                f"(利用可能: {list(FILLABLE_MAP.keys())})",
                file=sys.stderr,
            )
            return None
        spec = FILLABLE_MAP[fillable_name]
        new_slide = duplicate_slide(prs, spec["idx"])
        flat_shapes = get_flat_text_shapes(new_slide.shapes)
        for yaml_key, flat_idx in spec["slots"].items():
            value = slide_spec.get(yaml_key)
            if value is None:
                continue
            if flat_idx < len(flat_shapes):
                set_shape_text(flat_shapes[flat_idx], str(value))
            else:
                print(
                    f"  [警告] {fillable_name}: flat_shape[{flat_idx}] が範囲外 "
                    f"(利用可能: {len(flat_shapes)}個)",
                    file=sys.stderr,
                )
        return new_slide

    # ── type: preset (fixed) ──
    if slide_type == "preset":
        preset_name = slide_spec.get("name")
        if preset_name not in PRESET_MAP:
            print(
                f"  [警告] 不明なプリセット名: {preset_name}  "
                f"(利用可能: {list(PRESET_MAP.keys())})",
                file=sys.stderr,
            )
            return None
        return duplicate_slide(prs, PRESET_MAP[preset_name])

    # ── 通常レイアウト ──
    if slide_type not in TEMPLATE_MAP:
        print(f"  [警告] 不明なスライドタイプ: {slide_type}", file=sys.stderr)
        return None

    template_idx = TEMPLATE_MAP[slide_type]
    new_slide = duplicate_slide(prs, template_idx)

    slot_map = SLOT_MAP.get(slide_type, {})
    text_shapes = get_text_shapes(new_slide)

    for shape_idx, slot_name in slot_map.items():
        value = slide_spec.get(slot_name)
        if value is None:
            continue
        if shape_idx < len(text_shapes):
            set_shape_text(text_shapes[shape_idx], str(value))
        else:
            print(
                f"  [警告] {slide_type}: shape[{shape_idx}] が範囲外 "
                f"(利用可能: {len(text_shapes)}個)",
                file=sys.stderr,
            )

    # content_list_4 のアイコン対応
    if slide_type == "content_list_4":
        _apply_content_list_4_icons(new_slide, slide_spec)

    return new_slide


# ──────────────────────────────────────────────
# content_list_4 のアイコン処理
# ──────────────────────────────────────────────
def _apply_content_list_4_icons(slide, spec):
    """テンプレートの番号バッジ（番号 1〜4 の小さい円）をアイコンに置換する。

    YAML側で item1_icon〜item4_icon が指定されていたら:
      1. 元の番号バッジのテキスト("1","2","3","4")を空にする
      2. 同じ位置・同じサイズに新しいアイコン円を重ねる
      3. アイコンが指定されていない場合は元のままの番号表示
    """
    icons = [spec.get(f"item{i+1}_icon") for i in range(4)]
    if not any(icons):
        return

    # テンプレート上、番号バッジは "1","2","3","4" のテキストを持つ AUTO_SHAPE
    badge_shapes = []
    for shp in list(slide.shapes):
        if not shp.has_text_frame:
            continue
        txt = shp.text_frame.text.strip()
        if txt in ("1", "2", "3", "4"):
            try:
                num = int(txt)
                if 1 <= num <= 4:
                    badge_shapes.append((num, shp))
            except ValueError:
                pass

    badge_shapes.sort(key=lambda p: p[0])

    for num, badge_shape in badge_shapes:
        icon = icons[num - 1]
        # 位置・サイズを取得
        left_in = badge_shape.left / 914400
        top_in = badge_shape.top / 914400
        w_in = badge_shape.width / 914400
        h_in = badge_shape.height / 914400
        cx = left_in + w_in / 2
        cy = top_in + h_in / 2
        # 元のバッジは 0.40 inch 程度。複合アイコンが小さすぎて潰れるため
        # 大きめ（0.75 inch 以上）にして視認性を確保。
        size = max(max(w_in, h_in) * 1.8, 0.75)
        # 元のバッジを削除（重なり防止）
        sp_elem = badge_shape._element
        sp_elem.getparent().remove(sp_elem)
        # アイコンが指定されていればそれを使い、未指定なら番号テキスト
        # （見た目の統一感のため、いずれにせよオレンジ円バッジに置き換える）
        icon_to_use = icon if icon else str(num)
        _add_icon(slide, icon_to_use, cx, cy, size, bg_color=ORANGE, fg_color=WHITE)


def delete_slide(prs, idx):
    """Remove from sldIdLst AND drop the rel (avoids orphan parts on save)."""
    sldIdLst = prs.slides._sldIdLst
    items = list(sldIdLst)
    target = items[idx]
    rId = target.rId
    prs.part.drop_rel(rId)
    sldIdLst.remove(target)


# ──────────────────────────────────────────────
# 著作権表示の年号を一括更新
# ──────────────────────────────────────────────
def fix_copyright_year(prs, target_year=None):
    if target_year is None:
        target_year = str(datetime.date.today().year)
    import re
    pattern = re.compile(r"©\s*20\d{2}")

    def _replace_in_shapes(shapes):
        for shape in shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if pattern.search(run.text):
                        run.text = pattern.sub(f"© {target_year}", run.text)

    for slide in prs.slides:
        _replace_in_shapes(slide.shapes)
    seen_layouts = set()
    for slide in prs.slides:
        layout = slide.slide_layout
        if id(layout) not in seen_layouts:
            seen_layouts.add(id(layout))
            _replace_in_shapes(layout.shapes)
    seen_masters = set()
    for layout in prs.slide_layouts:
        master = layout.slide_master
        if id(master) not in seen_masters:
            seen_masters.add(id(master))
            _replace_in_shapes(master.shapes)


# ──────────────────────────────────────────────
# auto-bookend: title / closing スライドの自動挿入
# ──────────────────────────────────────────────
def apply_bookend(slides_spec, outline):
    """
    outline のトップレベルフィールドを参照して先頭・末尾にスライドを自動挿入する。

    対象フィールド:
      bookend       : true（デフォルト）で自動挿入を有効化
      cover         : true（デフォルト）で先頭に title カバーを挿入
      closing       : true（デフォルト）で末尾に section_check を挿入
    """
    if not outline.get("bookend", True):
        return slides_spec

    result = list(slides_spec)

    # 先頭: cover/title 系が無ければデフォルトカバーを挿入
    if outline.get("cover", True):
        first_type = result[0].get("type") if result else None
        first_name = result[0].get("name") if result else None
        is_cover_already = (
            first_type == "cover"
            or (first_type == "preset" and first_name == "title")
        )
        if not is_cover_already:
            result.insert(0, {"type": "preset", "name": "title"})
            print("  [bookend] 先頭に title カバーを挿入")

    # 末尾: closing が true なら section_check を挿入
    if outline.get("closing", True):
        result.append({"type": "preset", "name": "section_check"})
        print("  [bookend] 末尾に section_check を挿入")

    return result


# ──────────────────────────────────────────────
# 新規スライド生成（共通サブルーチン）
# ──────────────────────────────────────────────
def _generate_slides_into(prs, outline, template_path):
    slides_spec = outline.get("slides", [])
    if not slides_spec:
        print("エラー: outline.yaml に 'slides' セクションがありません")
        sys.exit(1)

    slides_spec = apply_bookend(slides_spec, outline)

    template_prs = Presentation(template_path)
    template_count = len(template_prs.slides)

    print(f"  生成するスライド数: {len(slides_spec)}")
    generated_count = 0
    for i, slide_spec in enumerate(slides_spec):
        stype = slide_spec.get("type", "不明")
        sname = slide_spec.get("name", "")
        label = f"{stype}/{sname}" if sname else stype
        print(f"  [{i+1}/{len(slides_spec)}] type={label}")
        slide = process_slide(template_prs, slide_spec)
        if slide:
            generated_count += 1

    print(f"\n  生成完了: {generated_count} スライド")

    new_indices_in_prs = []
    for src_idx in range(template_count, len(template_prs.slides)):
        copy_slide_from(template_prs, src_idx, prs)
        new_indices_in_prs.append(len(prs.slides) - 1)
    return new_indices_in_prs


# ──────────────────────────────────────────────
# mode: edit — 既存 PPTX に追加
# ──────────────────────────────────────────────
def run_edit_mode(outline, template_path, output_path):
    input_path = outline.get("input")
    if not input_path or not os.path.exists(input_path):
        print(f"エラー: input ファイルが見つかりません: {input_path}")
        sys.exit(1)

    print(f"[edit] 入力: {input_path}")
    dst_prs = Presentation(input_path)
    original_count = len(dst_prs.slides)
    print(f"[edit] 既存スライド数: {original_count}")

    new_indices = _generate_slides_into(dst_prs, outline, template_path)

    position = outline.get("position", "end")
    if isinstance(position, int) and 0 <= position < original_count:
        n_new = len(new_indices)
        total = len(dst_prs.slides)
        for k in range(n_new - 1, -1, -1):
            move_slide_to(dst_prs, total - (n_new - k), position + k)
        print(f"[edit] スライドを位置 {position} に挿入しました")
    else:
        print(f"[edit] スライドを末尾に追加しました")

    fix_copyright_year(dst_prs)
    dst_prs.save(output_path)
    print(f"[edit] 保存完了: {output_path}")


# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="career-spirit-slides 生成")
    parser.add_argument("outline", help="YAMLアウトラインファイルのパス")
    parser.add_argument("output", help="出力PPTXファイルのパス")
    parser.add_argument("--template", default=None, help="テンプレートPPTXのパス")
    args = parser.parse_args()

    template_path = args.template
    if not template_path:
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(skill_dir, "assets", "TEMPLATE.pptx")

    if not os.path.exists(template_path):
        print(f"エラー: テンプレートが見つかりません: {template_path}")
        sys.exit(1)

    with open(args.outline, "r", encoding="utf-8") as f:
        outline = yaml.safe_load(f)

    mode = outline.get("mode", "new")
    if mode == "edit":
        run_edit_mode(outline, template_path, args.output)
        return

    # ── mode: new ──
    slides_spec = outline.get("slides", [])
    if not slides_spec:
        print("エラー: outline.yaml に 'slides' セクションがありません")
        sys.exit(1)

    slides_spec = apply_bookend(slides_spec, outline)

    prs = Presentation(template_path)
    original_slide_count = len(prs.slides)

    print(f"テンプレート: {template_path}")
    print(f"  元スライド数: {original_slide_count}")
    print(f"  生成するスライド数: {len(slides_spec)}")
    print()

    generated_count = 0
    for i, slide_spec in enumerate(slides_spec):
        stype = slide_spec.get("type", "不明")
        sname = slide_spec.get("name", "")
        label = f"{stype}/{sname}" if sname else stype
        print(f"  [{i+1}/{len(slides_spec)}] type={label}")
        slide = process_slide(prs, slide_spec)
        if slide:
            generated_count += 1

    print()
    print(f"生成完了: {generated_count} スライド")
    print(f"テンプレートスライド {original_slide_count} 枚を削除中...")
    for i in range(original_slide_count - 1, -1, -1):
        delete_slide(prs, i)

    fix_copyright_year(prs)
    prs.save(args.output)
    print(f"保存完了: {args.output}")
    print(f"最終スライド数: {len(prs.slides)}")


if __name__ == "__main__":
    main()
