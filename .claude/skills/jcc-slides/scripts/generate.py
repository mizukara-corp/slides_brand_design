#!/usr/bin/env python3
"""
JCC スライド生成スクリプト
TEMPLATE.pptx（9枚）をテンプレートとして、YAMLアウトラインから PPTX を生成します。

使い方:
  python generate.py outline.yaml output.pptx [--template /path/to/TEMPLATE.pptx]

TEMPLATE.pptx のスライドインデックス（make_template.py で生成）:
  [0] title  [1] section  [2] card2_dark  [3] memo  [4] card3_dark
  [5] content_list  [6] card2_light  [7] question  [8] table
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
except ImportError:
    print("python-pptx が見つかりません。pip install python-pptx --break-system-packages でインストール")
    sys.exit(1)

# ──────────────────────────────────────────────
# TEMPLATE.pptx のスライドインデックス（25枚版）
# ── ベーステンプレート（9枚） ──
# ──────────────────────────────────────────────
TEMPLATE_MAP = {
    "title":        0,
    "section":      1,
    "card2_dark":   2,
    "memo":         3,
    "card3_dark":   4,
    "content_list": 5,
    "card2_light":  6,
    "question":     7,
    "table":        8,
}

# ── fixed プリセット（16枚）: そのままコピーするだけ ──
# ── fillable プリセット（7枚）: レイアウト固定・指定テキストのみ変更 ──
# FILLABLE_MAP: name → { "idx": TEMPLATE index, "slots": { yaml_key: flat_shape_index } }
# flat_shape_index はグループを含むすべてのテキストシェイプをDFS順に並べた連番
FILLABLE_MAP = {
    "member_autonomy": {
        "idx": 25,
        "slots": {
            "title":      15,   # スライドタイトル
            "exec_desc":   2,   # 経営層の説明文
            "mgmt_desc":   5,   # マネジメント層の説明文
            "field_desc":  7,   # 現場層の説明文
        },
    },
    "genjo_wave": {
        "idx": 26,
        "slots": {
            "bottom_text": 5,   # 下部メッセージテキスト
        },
    },
    "genjo_wave_labeled": {
        "idx": 27,
        "slots": {
            "overlay_label": 6,  # 波形オーバーレイラベル（例: 「原則」）
            "bottom_text":   7,  # 下部メッセージテキスト
        },
    },
    "principle_comparison": {
        "idx": 28,
        "slots": {
            "title":        9,   # スライドタイトル
            "left_header":  4,   # 左列ヘッダ（例: 「原理の不在」）
            "right_header": 5,   # 右列ヘッダ（例: 「原則の存在」）
            "left_items":   6,   # 左列本文（改行区切り）
            "right_items":  7,   # 右列本文（改行区切り）
            "bottom_text":  8,   # 下部ハイライトテキスト
        },
    },
    "mvv_orange": {
        "idx": 29,
        "slots": {
            "content": 4,   # オレンジBOX内テキスト（改行可）
        },
    },
    "mvv_gray": {
        "idx": 30,
        "slots": {
            "content": 4,   # グレーBOX内テキスト（改行可）
        },
    },
    "mvv_pink": {
        "idx": 31,
        "slots": {
            "content": 4,   # ピンクBOX内テキスト（改行可）
        },
    },
    # ── FB-FF マトリクス（テーブルセル書き込み型）──
    "fbff_6col": {
        "idx": 32,
        "slots": {},
        # table_slots: { yaml_key: (table_index_in_slide, row_index, col_index) }
        "table_slots": {
            "problem": (0, 1, 0),
            "fact":    (0, 1, 1),
            "what":    (0, 1, 2),
            "goal":    (0, 1, 3),
            "plan":    (0, 1, 4),
            "action":  (0, 1, 5),
        },
    },
    "fbff_7col": {
        "idx": 33,
        "slots": {},
        "table_slots": {
            "why":     (0, 1, 0),
            "problem": (0, 1, 1),
            "fact":    (0, 1, 2),
            "what":    (0, 1, 3),
            "goal":    (0, 1, 4),
            "plan":    (0, 1, 5),
            "action":  (0, 1, 6),
        },
    },
}

PRESET_MAP = {
    "belief_system":      9,
    "market_structure":  10,
    "be_do_have_v1":     11,
    "be_do_have_v2":     12,
    "be_do_have_v3":     13,
    "coaching_matrix_v1": 14,
    "be_do_have_v4":     15,
    "be_do_have_v5":     16,
    "be_do_have_v6":     17,
    "belief_bubbles":    18,
    "coaching_matrix_v2": 19,
    "goal_matrix_blank": 20,
    "goal_matrix_filled": 21,
    "logic3_highlight":  22,
    "nonverbal_table":   23,
    "context3_table":    24,
}

# ──────────────────────────────────────────────
# テキストスロットのマッピング（テキストシェイプのインデックス → YAML フィールド名）
# ──────────────────────────────────────────────
SLOT_MAP = {
    "title":        {0: "day"},
    "section":      {0: "title_en", 1: "title_ja"},
    "card2_dark":   {0: "title", 1: "card1", 2: "card2"},
    "memo":         {0: "label", 1: "content"},
    "content_list": {0: "section_label", 1: "subtitle", 2: "body", 3: "footnote"},
    "question":     {0: "main_text", 1: "category"},
    "card2_light":  {0: "card1", 1: "card2", 2: "title"},
    # card3_dark: テキストシェイプ構成
    #   [0] title, [1] col1_desc, [2] col1_keyword,
    #   [3] col2_desc, [4] col2_keyword, [5] col3_desc, [6] col3_keyword
    #   ※ 図形内テキスト（抽象/具体/全体/部分/結果/原因 など）は固定
    "card3_dark":   {
        0: "title",
        1: "col1_desc", 2: "col1_keyword",
        3: "col2_desc", 4: "col2_keyword",
        5: "col3_desc", 6: "col3_keyword",
    },
    # table: テキストシェイプは title のみ（インデックス0）、行データは set_table_data() で別処理
    "table":        {0: "title"},
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

    tmpl_sp_tree_copy = copy.deepcopy(template.shapes._spTree)
    for elem in tmpl_sp_tree_copy.iter():
        for attr in (R_EMBED, R_ID, R_HREF):
            if attr in elem.attrib and elem.attrib[attr] in rId_map:
                elem.attrib[attr] = rId_map[elem.attrib[attr]]

    new_sp_tree = new_slide.shapes._spTree
    for child in list(new_sp_tree):
        new_sp_tree.remove(child)
    for child in list(tmpl_sp_tree_copy):
        new_sp_tree.append(child)

    return new_slide


# ──────────────────────────────────────────────
# クロスプレゼン スライドコピー（edit/patch 用）
# ──────────────────────────────────────────────
def copy_slide_from(src_prs, src_idx, dst_prs):
    """
    src_prs の src_idx 番スライドを dst_prs の末尾にコピーして追加する。
    リレーションシップ（画像等）も再マッピングする。
    """
    src_slide = src_prs.slides[src_idx]

    # dst_prs の先頭レイアウトを仮に使って空スライドを作成
    blank_layout = dst_prs.slide_layouts[0]
    new_slide = dst_prs.slides.add_slide(blank_layout)

    # リレーションシップを dst_prs にコピー
    rId_map = {}
    for rel in src_slide.part.rels.values():
        reltype_short = rel.reltype.split("/")[-1]
        if reltype_short in ("slideLayout", "notesSlide"):
            continue
        if rel.is_external:
            new_rId = new_slide.part.target_ref(rel.reltype, rel.target_ref)
        else:
            new_rId = new_slide.part.relate_to(rel.target_part, rel.reltype)
        rId_map[rel.rId] = new_rId

    # シェイプツリーをディープコピーして rId を再マッピング
    sp_tree = copy.deepcopy(src_slide.shapes._spTree)
    for elem in sp_tree.iter():
        for attr in (R_EMBED, R_ID, R_HREF):
            if attr in elem.attrib and elem.attrib[attr] in rId_map:
                elem.attrib[attr] = rId_map[elem.attrib[attr]]

    new_sp_tree = new_slide.shapes._spTree
    for child in list(new_sp_tree):
        new_sp_tree.remove(child)
    for child in list(sp_tree):
        new_sp_tree.append(child)

    return new_slide


def move_slide_to(prs, from_idx, to_idx):
    """prs 内のスライドを from_idx から to_idx に移動する（in-place）。"""
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
# テキストシェイプの文字列を置換
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
# テーブルスライドの行データを差し替える
# ──────────────────────────────────────────────
def set_table_data(slide, rows_data):
    """
    slide 内のテーブルシェイプを探し、rows_data の内容で行を差し替える。
    rows_data: [["左セル", "右セル"], ...] のリスト
    既存の行数より多い場合は最終行を複製して追加、少ない場合は余分な行を空にする。
    """
    tbl_shape = next((s for s in slide.shapes if s.has_table), None)
    if tbl_shape is None:
        print("  [警告] テーブルシェイプが見つかりません", file=sys.stderr)
        return

    tbl_xml = tbl_shape.table._tbl
    n_existing = len(tbl_shape.table.rows)
    n_needed   = len(rows_data)

    # 行が足りない場合：最終行の XML をコピーして追加
    if n_needed > n_existing:
        tr_elements = tbl_xml.findall(f"{{{NS_A}}}tr")
        last_tr = tr_elements[-1]
        for _ in range(n_needed - n_existing):
            tbl_xml.append(copy.deepcopy(last_tr))

    # 行データを書き込む
    tbl_rows = tbl_xml.findall(f"{{{NS_A}}}tr")
    for r_idx, row_data in enumerate(rows_data):
        if r_idx >= len(tbl_rows):
            break
        tr = tbl_rows[r_idx]
        td_elements = tr.findall(f"{{{NS_A}}}tc")
        for c_idx, cell_text in enumerate(row_data):
            if c_idx >= len(td_elements):
                break
            tc = td_elements[c_idx]
            tx_body = tc.find(f"{{{NS_A}}}txBody")
            if tx_body is None:
                continue
            paras = tx_body.findall(f"{{{NS_A}}}p")
            lines = str(cell_text).split("\n")

            if len(lines) > len(paras) and len(paras) > 0:
                last_p = paras[-1]
                for _ in range(len(lines) - len(paras)):
                    tx_body.append(copy.deepcopy(last_p))
                paras = tx_body.findall(f"{{{NS_A}}}p")

            for p_idx, para in enumerate(paras):
                line = lines[p_idx] if p_idx < len(lines) else ""
                r_elems = para.findall(f"{{{NS_A}}}r")
                if r_elems:
                    t_elem = r_elems[0].find(f"{{{NS_A}}}t")
                    if t_elem is not None:
                        t_elem.text = line
                    for r_extra in r_elems[1:]:
                        t_extra = r_extra.find(f"{{{NS_A}}}t")
                        if t_extra is not None:
                            t_extra.text = ""
                else:
                    r_new = etree.SubElement(para, f"{{{NS_A}}}r")
                    t_new = etree.SubElement(r_new, f"{{{NS_A}}}t")
                    t_new.text = line

    # 余分な行を空にする
    tbl_rows_after = tbl_xml.findall(f"{{{NS_A}}}tr")
    for r_idx in range(n_needed, len(tbl_rows_after)):
        tr = tbl_rows_after[r_idx]
        for tc in tr.findall(f"{{{NS_A}}}tc"):
            tx_body = tc.find(f"{{{NS_A}}}txBody")
            if tx_body is None:
                continue
            for para in tx_body.findall(f"{{{NS_A}}}p"):
                for r_elem in para.findall(f"{{{NS_A}}}r"):
                    t = r_elem.find(f"{{{NS_A}}}t")
                    if t is not None:
                        t.text = ""


# ──────────────────────────────────────────────
# スライド生成メイン処理
# ──────────────────────────────────────────────
def process_slide(prs, slide_spec):
    slide_type = slide_spec.get("type")

    # ── type: fillable（レイアウト固定・テキスト変更可）──
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

        # テーブルセル書き込み（table_slots が定義されている場合）
        table_slots = spec.get("table_slots", {})
        if table_slots:
            tables = [s for s in new_slide.shapes if s.has_table]
            for yaml_key, (tbl_idx, row_idx, col_idx) in table_slots.items():
                value = slide_spec.get(yaml_key)
                if value is None:
                    continue
                if tbl_idx >= len(tables):
                    print(f"  [警告] {fillable_name}: table[{tbl_idx}] が範囲外", file=sys.stderr)
                    continue
                tbl = tables[tbl_idx].table
                if row_idx >= len(tbl.rows) or col_idx >= len(tbl.columns):
                    print(f"  [警告] {fillable_name}: cell[{row_idx},{col_idx}] が範囲外", file=sys.stderr)
                    continue
                cell = tbl.cell(row_idx, col_idx)
                tf = cell.text_frame
                lines = str(value).split("\n")
                paras = tf.paragraphs
                # 必要なら段落を追加
                if len(lines) > len(paras) and len(paras) > 0:
                    last_p = paras[-1]._p
                    for _ in range(len(lines) - len(paras)):
                        tf._txBody.append(copy.deepcopy(last_p))
                    paras = tf.paragraphs
                for p_idx, para in enumerate(paras):
                    line = lines[p_idx] if p_idx < len(lines) else ""
                    runs = para.runs
                    if runs:
                        runs[0].text = line
                        for r in runs[1:]:
                            r.text = ""
                    else:
                        r_elem = etree.SubElement(para._p, f"{{{NS_A}}}r")
                        t_elem = etree.SubElement(r_elem, f"{{{NS_A}}}t")
                        t_elem.text = line

        return new_slide

    # ── type: preset（fixed）──
    if slide_type == "preset":
        preset_name = slide_spec.get("name")
        if preset_name not in PRESET_MAP:
            print(
                f"  [警告] 不明なプリセット名: {preset_name}  "
                f"(利用可能: {list(PRESET_MAP.keys())})",
                file=sys.stderr,
            )
            return None
        template_idx = PRESET_MAP[preset_name]
        return duplicate_slide(prs, template_idx)

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

    # table タイプ：行データを差し替える
    if slide_type == "table":
        rows_data = slide_spec.get("rows", [])
        if rows_data:
            set_table_data(new_slide, rows_data)

    return new_slide


def delete_slide(prs, idx):
    sldIdLst = prs.slides._sldIdLst
    sldIdLst.remove(sldIdLst[idx])


# ──────────────────────────────────────────────
# 著作権表示の年号を一括更新
# ──────────────────────────────────────────────
def fix_copyright_year(prs, target_year=None):
    """著作権テキスト（© 20xx）を target_year に統一する。
    target_year 省略時は実行時の西暦年を自動取得する。
    スライド本体・レイアウト・マスターをすべて対象とする。"""
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

    # スライド本体
    for slide in prs.slides:
        _replace_in_shapes(slide.shapes)

    # スライドレイアウト（重複しても問題なし）
    seen_layouts = set()
    for slide in prs.slides:
        layout = slide.slide_layout
        if id(layout) not in seen_layouts:
            seen_layouts.add(id(layout))
            _replace_in_shapes(layout.shapes)

    # スライドマスター
    seen_masters = set()
    for layout in prs.slide_layouts:
        master = layout.slide_master
        if id(master) not in seen_masters:
            seen_masters.add(id(master))
            _replace_in_shapes(master.shapes)


# ──────────────────────────────────────────────
# swap: type alias + variant → 実際の type/name に解決
# ──────────────────────────────────────────────
#
# 書き方:
#   type: <alias>          (例: card2 / mvv / be_do_have)
#   variant: <variant>     (省略時はデフォルト variant を使う)
#   <content fields>...    (type/variant 以外のフィールドはそのまま引き継ぐ)
#
# alias グループ一覧:
#   card2          dark(default) / light
#   mvv            orange(default) / gray / pink
#   be_do_have     v1(default) / v2 / v3 / v4 / v5 / v6
#   coaching_matrix  v1(default) / v2
#   goal_matrix    blank(default) / filled
#   genjo_wave     plain(default) / labeled
# ──────────────────────────────────────────────
SWAP_ALIASES = {
    "card2": {
        "_default": "dark",
        "dark":     {"type": "card2_dark"},
        "light":    {"type": "card2_light"},
    },
    "mvv": {
        "_default": "orange",
        "orange":   {"type": "fillable", "name": "mvv_orange"},
        "gray":     {"type": "fillable", "name": "mvv_gray"},
        "pink":     {"type": "fillable", "name": "mvv_pink"},
    },
    "be_do_have": {
        "_default": "v1",
        "v1":  {"type": "preset", "name": "be_do_have_v1"},
        "v2":  {"type": "preset", "name": "be_do_have_v2"},
        "v3":  {"type": "preset", "name": "be_do_have_v3"},
        "v4":  {"type": "preset", "name": "be_do_have_v4"},
        "v5":  {"type": "preset", "name": "be_do_have_v5"},
        "v6":  {"type": "preset", "name": "be_do_have_v6"},
    },
    "coaching_matrix": {
        "_default": "v1",
        "v1": {"type": "preset", "name": "coaching_matrix_v1"},
        "v2": {"type": "preset", "name": "coaching_matrix_v2"},
    },
    "goal_matrix": {
        "_default": "blank",
        "blank":  {"type": "preset", "name": "goal_matrix_blank"},
        "filled": {"type": "preset", "name": "goal_matrix_filled"},
    },
    "genjo_wave": {
        "_default": "plain",
        "plain":   {"type": "fillable", "name": "genjo_wave"},
        "labeled": {"type": "fillable", "name": "genjo_wave_labeled"},
    },
}


def resolve_swaps(slides_spec):
    """
    slides_spec 内の type alias + variant を実際の type/name に解決して返す。

    解決ルール:
      1. type が SWAP_ALIASES のキーであれば alias として扱う
      2. variant フィールドが指定されていれば対応する resolved を使う（省略時はデフォルト）
      3. type / variant 以外のすべてのフィールドをそのまま引き継ぐ
      4. resolved の type / name が spec の同名フィールドより優先される
    """
    result = []
    for spec in slides_spec:
        slide_type = spec.get("type", "")

        if slide_type not in SWAP_ALIASES:
            result.append(spec)
            continue

        aliases = SWAP_ALIASES[slide_type]
        variant = str(spec.get("variant", aliases["_default"]))

        if variant not in aliases or variant == "_default":
            print(
                f"  [警告] swap: 不明な variant '{variant}' for type '{slide_type}' "
                f"(利用可能: {[k for k in aliases if k != '_default']})",
                file=sys.stderr,
            )
            variant = aliases["_default"]

        # type / variant 以外のフィールドをコピーし、resolved で上書き
        merged = {k: v for k, v in spec.items() if k not in ("type", "variant")}
        merged.update(aliases[variant])   # type と name（あれば）を上書き

        resolved_type = merged.get("type", "?")
        resolved_name = merged.get("name", "")
        label = f"{resolved_type}/{resolved_name}" if resolved_name else resolved_type
        print(f"  [swap] {slide_type}({variant}) → {label}")

        result.append(merged)

    return result


# ──────────────────────────────────────────────
# bundle 展開: 1エントリ → 複数スライドに展開
# ──────────────────────────────────────────────
# 現在サポートするバンドル:
#
#   section_start — section ヘッダー + AGENDA（content_list）の 2 枚
#     フィールド:
#       title_en     : セクション英語タイトル（必須）
#       title_ja     : セクション日本語タイトル（任意）
#       agenda_label : AGENDA スライドのラベル（デフォルト "AGENDA"）
#       agenda_items : AGENDA の本文（content_list の body 相当。| 記法推奨）
#       subtitle     : AGENDA スライドのサブタイトル（任意）
#       footnote     : AGENDA スライドの注釈（省略時 " " でクリア）
#
# 将来拡張の例（未実装）:
#   section_end  — summary（content_list） + question の 2 枚
#   card_pair    — card2_dark × 2 の連続スライド
# ──────────────────────────────────────────────
BUNDLE_TYPES = {"section_start", "section_end"}  # 現在実装: section_start のみ


def expand_bundles(slides_spec):
    """
    slides_spec 内の bundle タイプを通常スライドのリストに展開して返す。
    bundle 以外のスペックはそのまま通す。
    """
    result = []
    for spec in slides_spec:
        slide_type = spec.get("type", "")

        # ── section_start: section + content_list(AGENDA) ──
        if slide_type == "section_start":
            title_en     = spec.get("title_en", "")
            title_ja     = spec.get("title_ja", "")
            agenda_label = spec.get("agenda_label", "AGENDA")
            agenda_items = spec.get("agenda_items", spec.get("body", ""))
            subtitle     = spec.get("subtitle", "")
            footnote     = spec.get("footnote", " ")

            # 1枚目: section ヘッダー
            section_spec = {"type": "section", "title_en": title_en}
            if title_ja:
                section_spec["title_ja"] = title_ja
            else:
                section_spec["title_ja"] = " "   # デフォルトテキストをクリア
            result.append(section_spec)
            print(f"  [bundle:section_start] → section({title_en!r})")

            # 2枚目: AGENDA スライド（agenda_items が空でも生成する）
            agenda_spec = {
                "type":          "content_list",
                "section_label": agenda_label,
                "body":          agenda_items or " ",
                "footnote":      footnote,
            }
            # subtitle 未指定時は " " でテンプレートデフォルトをクリア
            agenda_spec["subtitle"] = subtitle if subtitle else " "
            result.append(agenda_spec)
            print(f"  [bundle:section_start] → content_list({agenda_label!r})")

        else:
            result.append(spec)

    return result


# ──────────────────────────────────────────────
# auto-bookend: title / closing スライドの自動挿入
# ──────────────────────────────────────────────
def apply_bookend(slides_spec, outline):
    """
    outline のトップレベルフィールドを参照して先頭・末尾にスライドを自動挿入する。

    対象フィールド（すべて省略可）:
      day         : title スライドの DAY テキスト（例: "DAY 2 -"）
      bookend     : true（デフォルト）で自動挿入を有効化
      closing_en  : 末尾スライドの英語テキスト（デフォルト: "Thank You"）
      closing_ja  : 末尾スライドの日本語テキスト（デフォルト: ""）

    動作:
      - bookend が false のときは何もしない
      - 先頭: すでに type=title のスライドがあれば挿入しない（重複防止）
        day が指定されていれば title スライドを prepend
      - 末尾: section スライド（closing）を append
        closing_en / closing_ja が未指定のとき "Thank You" / "" を使う
    """
    bookend = outline.get("bookend", True)
    if not bookend:
        return slides_spec

    result = list(slides_spec)

    # ── 先頭: title スライド ──
    day = outline.get("day", "").strip()
    if day:
        first_type = result[0].get("type") if result else None
        if first_type != "title":
            title_slide = {"type": "title", "day": day}
            result.insert(0, title_slide)
            print(f"  [bookend] 先頭に title スライドを挿入 (day={day!r})")

    # ── 末尾: closing スライド（section タイプを流用）──
    closing_en = outline.get("closing_en", "Thank You").strip()
    closing_ja = outline.get("closing_ja", "").strip()
    # closing_ja が空のときは " " でテンプレートのデフォルトテキストをクリア
    closing_slide = {
        "type": "section",
        "title_en": closing_en,
        "title_ja": closing_ja if closing_ja else " ",
    }
    result.append(closing_slide)
    print(f"  [bookend] 末尾に closing スライドを挿入 "
          f"(en={closing_en!r}, ja={closing_ja!r})")

    return result


# ──────────────────────────────────────────────
# 新規スライド生成（共通サブルーチン）
# ──────────────────────────────────────────────
def _generate_slides_into(prs, outline, template_path):
    """
    outline の slides を TEMPLATE から生成して prs に追加する。
    追加されたスライドのインデックスリスト（prs 内）を返す。
    """
    slides_spec = outline.get("slides", [])
    if not slides_spec and outline.get("mode") not in ("patch",):
        print("エラー: outline.yaml に 'slides' セクションがありません")
        sys.exit(1)

    slides_spec = resolve_swaps(slides_spec)
    slides_spec = expand_bundles(slides_spec)
    slides_spec = apply_bookend(slides_spec, outline)

    template_prs = Presentation(template_path)
    template_count = len(template_prs.slides)
    before_count = len(prs.slides)

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

    # template_prs の新スライド（template_count 以降）を prs にコピー
    new_indices_in_prs = []
    for src_idx in range(template_count, len(template_prs.slides)):
        copy_slide_from(template_prs, src_idx, prs)
        new_indices_in_prs.append(len(prs.slides) - 1)

    return new_indices_in_prs


# ──────────────────────────────────────────────
# mode: edit — 既存 PPTX の末尾（または指定位置）にスライドを追加
# ──────────────────────────────────────────────
def run_edit_mode(outline, template_path, output_path):
    """
    既存 PPTX にスライドを追加する。

    YAML フィールド:
      mode    : "edit"（必須）
      input   : 入力 PPTX のパス（必須）
      position: 挿入位置。"end"（デフォルト）または 0 始まりのスライド番号
      slides  : 追加するスライドのリスト
      bookend : false 推奨（既存ファイルへの追記なので）
    """
    input_path = outline.get("input")
    if not input_path or not os.path.exists(input_path):
        print(f"エラー: input ファイルが見つかりません: {input_path}")
        sys.exit(1)

    print(f"[edit] 入力: {input_path}")
    dst_prs = Presentation(input_path)
    original_count = len(dst_prs.slides)
    print(f"[edit] 既存スライド数: {original_count}")

    # 新スライドを生成して dst_prs に追加
    new_indices = _generate_slides_into(dst_prs, outline, template_path)

    # position 指定があれば末尾からその位置に移動
    position = outline.get("position", "end")
    if isinstance(position, int) and 0 <= position < original_count:
        # new_indices は末尾に追加されている。position の直前に移動する。
        n_new = len(new_indices)
        total = len(dst_prs.slides)
        # 末尾 n_new 枚を position の直前に移動（逆順で繰り返す）
        for k in range(n_new - 1, -1, -1):
            move_slide_to(dst_prs, total - (n_new - k), position + k)
        print(f"[edit] スライドを位置 {position} に挿入しました")
    else:
        print(f"[edit] スライドを末尾に追加しました")

    fix_copyright_year(dst_prs)
    dst_prs.save(output_path)
    print(f"[edit] 保存完了: {output_path}")
    print(f"[edit] 最終スライド数: {len(dst_prs.slides)}")


# ──────────────────────────────────────────────
# mode: patch — 既存 PPTX に delete / replace / insert 操作を適用
# ──────────────────────────────────────────────
def run_patch_mode(outline, template_path, output_path):
    """
    既存 PPTX に外科的な編集操作を適用する。

    YAML フィールド:
      mode      : "patch"（必須）
      input     : 入力 PPTX のパス（必須）
      operations: 操作のリスト（順番に適用）

    operations の各エントリ:
      action: delete
        index : 削除するスライドの 0 始まりインデックス

      action: replace
        index : 置き換えるスライドの 0 始まりインデックス
        slide : 新しいスライドのスペック（通常スライドと同じ書き方）

      action: insert
        before: この 0 始まりインデックスの直前に挿入
        slide : 挿入するスライドのスペック

    ※ 複数操作を指定する場合、index は「操作適用前」の元のインデックスを基準とする。
       内部で offset を自動調整する。
    """
    input_path = outline.get("input")
    if not input_path or not os.path.exists(input_path):
        print(f"エラー: input ファイルが見つかりません: {input_path}")
        sys.exit(1)

    operations = outline.get("operations", [])
    if not operations:
        print("エラー: operations が空です")
        sys.exit(1)

    print(f"[patch] 入力: {input_path}")
    dst_prs = Presentation(input_path)
    print(f"[patch] 既存スライド数: {len(dst_prs.slides)}")

    # operations を mutable なコピーに（後続インデックスの動的補正のため）
    ops = [dict(op) for op in operations]

    # ── Phase 1: 全 replace/insert スライドを 1 つの template_prs に生成 ──
    # 別々の Presentation から copy すると同一 part 名が衝突して ZIP 破損するため、
    # 必ず 1 インスタンスにまとめて生成すること。
    template_prs = Presentation(template_path)
    op_gen_idx = {}  # op_num → template_prs 内スライドインデックス

    for op_num, op in enumerate(ops):
        if op.get("action") in ("replace", "insert"):
            slide_spec = op.get("slide")
            if not slide_spec:
                continue
            spec = resolve_swaps([slide_spec])[0]
            new_slide = process_slide(template_prs, spec)
            if new_slide:
                op_gen_idx[op_num] = len(template_prs.slides) - 1
                stype = spec.get("type", "?")
                print(f"  [gen] op{op_num} ({op.get('action')}) type={stype} → tmpl[{op_gen_idx[op_num]}]")

    # ── Phase 2: 生成スライドを dst_prs の末尾に一括コピー ──
    # copy_slide_from は 1 つの template_prs から行うのでパート名が衝突しない。
    op_dst_idx = {}  # op_num → dst_prs 内の現在インデックス（操作で変化）

    for op_num in sorted(op_gen_idx.keys()):
        tmpl_idx = op_gen_idx[op_num]
        copy_slide_from(template_prs, tmpl_idx, dst_prs)
        op_dst_idx[op_num] = len(dst_prs.slides) - 1

    print(f"[patch] 生成スライドをコピー後のスライド数: {len(dst_prs.slides)}")

    # ── Phase 3: 操作を順番に適用 ──

    def _shift_gen(action, pivot):
        """delete/insert 後に op_dst_idx を補正する。"""
        for onum in op_dst_idx:
            v = op_dst_idx[onum]
            if action == "delete" and v > pivot:
                op_dst_idx[onum] -= 1
            elif action == "insert" and v >= pivot:
                op_dst_idx[onum] += 1

    def _shift_ops(ops_tail, action, pivot):
        """delete/insert 後に残り操作の index/before を補正する。"""
        for op in ops_tail:
            for field in ("index", "before"):
                if field not in op:
                    continue
                v = op[field]
                if action == "delete" and v > pivot:
                    op[field] -= 1
                elif action == "insert" and v >= pivot:
                    op[field] += 1

    def _update_after_move(from_idx, to_idx):
        """move_slide_to(from_idx → to_idx) 後に op_dst_idx を補正する。
        from_idx > to_idx を前提（末尾 append したスライドを前方に移動するパターン）。"""
        for onum in op_dst_idx:
            v = op_dst_idx[onum]
            if v == from_idx:
                op_dst_idx[onum] = to_idx
            elif to_idx <= v < from_idx:
                op_dst_idx[onum] = v + 1

    for op_num, op in enumerate(ops):
        action = op.get("action", "")
        idx = op.get("index", op.get("before", 0))

        print(f"\n  [{op_num+1}/{len(ops)}] action={action} index={idx}")

        if action == "delete":
            if idx < 0 or idx >= len(dst_prs.slides):
                print(f"  [警告] index {idx} は範囲外 (スライド数: {len(dst_prs.slides)})")
                continue
            delete_slide(dst_prs, idx)
            _shift_gen("delete", idx)
            _shift_ops(ops[op_num + 1:], "delete", idx)
            print(f"  → スライド {idx} を削除しました")

        elif action == "replace":
            if op_num not in op_dst_idx:
                print(f"  [警告] replace に生成スライドがありません (op{op_num})")
                continue
            if idx < 0 or idx >= len(dst_prs.slides):
                print(f"  [警告] index {idx} は範囲外 (スライド数: {len(dst_prs.slides)})")
                continue

            # 旧スライドを削除（これにより生成スライドのインデックスが 1 つ前にずれる）
            delete_slide(dst_prs, idx)
            _shift_gen("delete", idx)
            # replace は前後スライドの絶対位置を変えないので残り op のインデックスは補正不要

            # 生成スライドを idx に移動
            gen_idx = op_dst_idx[op_num]
            move_slide_to(dst_prs, gen_idx, idx)
            _update_after_move(gen_idx, idx)
            print(f"  → スライド {idx} を置き換えました (gen[{gen_idx}]→[{idx}])")

        elif action == "insert":
            if op_num not in op_dst_idx:
                print(f"  [警告] insert に生成スライドがありません (op{op_num})")
                continue

            gen_idx = op_dst_idx[op_num]
            move_slide_to(dst_prs, gen_idx, idx)
            _update_after_move(gen_idx, idx)
            _shift_ops(ops[op_num + 1:], "insert", idx)
            print(f"  → スライド {idx} の直前に挿入しました (gen[{gen_idx}]→[{idx}])")

        else:
            print(f"  [警告] 不明な action: {action!r}  (delete / replace / insert のみ有効)")

    print(f"\n[patch] 操作完了: {len(dst_prs.slides)} スライド")
    fix_copyright_year(dst_prs)
    dst_prs.save(output_path)
    print(f"[patch] 保存完了: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="JCC スライド生成")
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

    # ── mode による分岐 ──
    mode = outline.get("mode", "new")

    if mode == "edit":
        run_edit_mode(outline, template_path, args.output)
        return

    if mode == "patch":
        run_patch_mode(outline, template_path, args.output)
        return

    # ── mode: new（デフォルト）——通常生成 ──
    slides_spec = outline.get("slides", [])
    if not slides_spec:
        print("エラー: outline.yaml に 'slides' セクションがありません")
        sys.exit(1)

    slides_spec = resolve_swaps(slides_spec)
    slides_spec = expand_bundles(slides_spec)
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
