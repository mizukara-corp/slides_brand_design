#!/usr/bin/env python3
"""
org-coaching 生成スクリプト
TEMPLATE.pptx（20枚）をテンプレートとして、YAMLアウトラインから PPTX を生成する。

使い方:
  python generate.py outline.yaml output.pptx [--template /path/to/TEMPLATE.pptx]

TEMPLATE.pptx のスライドインデックス（make_template.py で生成）:
  ── training3 由来 base デザイン（6枚）──
  [0] title          [1] meditation    [2] leader_message
  [3] check_in       [4] rest_time     [5] closing_light

  ── training3 由来 編集可ベース（2枚）──
  [6] question       [7] purpose

  ── training2 由来 編集可（7枚）──
  [ 8] key_point     [ 9] section_divider  [10] notice
  [11] agenda_h0     [12] agenda_h1        [13] agenda_h2    [14] agenda_h3

  ── training2 由来 fillable プリセット（5枚）──
  [15] result_chain  [16] compare_2card  [17] compare_3card
  [18] loop_learning [19] circle_overlap
"""

import sys
import copy
import argparse
import os
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
except ImportError:
    print("python-pptx が見つかりません。pip install python-pptx --break-system-packages でインストール")
    sys.exit(1)

# ──────────────────────────────────────────────
# ブランドカラー
# ──────────────────────────────────────────────
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
DARK_NAVY  = RGBColor(0x0A, 0x25, 0x40)
ACCENT     = RGBColor(0xFF, 0xE8, 0x4B)
HIGHLIGHT  = RGBColor(0x1E, 0x30, 0x56)

# ──────────────────────────────────────────────
# TEMPLATE.pptx のスライドインデックス
# ──────────────────────────────────────────────
AGENDA_VARIANTS = {0: 11, 1: 12, 2: 13, 3: 14}  # highlight番号 → slide index

# テキスト編集可・通常レンダラ用
TEMPLATE_MAP = {
    "title":           0,
    "meditation":      1,
    "leader_message":  2,
    "check_in":        3,
    "rest_time":       4,
    "closing_light":   5,
    "question":        6,
    "purpose":         7,
    "key_point":       8,
    "section_divider": 9,
    "notice":          10,
}

# fillable プリセット（レイアウト固定・指定スロットのみ編集可）
FILLABLE_MAP = {
    "result_chain": {
        "idx": 15,
        # DFS順: 0=結果, 1=行動, 2=感情, 3=信念・価値観, 4=title
        "slots": {
            "box1":  0,
            "box2":  1,
            "box3":  2,
            "box4":  3,
            "title": 4,
        },
    },
    "compare_2card": {
        "idx": 16,
        # DFS順: 0=右ヘッダ帯(空), 1=左ヘッダ帯(空・黄色), 2=左body, 3=右body, 4=title
        "slots": {
            "card1": 2,
            "card2": 3,
            "title": 4,
        },
    },
    "compare_3card": {
        "idx": 17,
        # DFS順: 0=center body, 1=left body, 2=right body, 3=center label, 4=left label, 5=right label
        "slots": {
            "card2_body":  0,
            "card1_body":  1,
            "card3_body":  2,
            "card2_label": 3,
            "card1_label": 4,
            "card3_label": 5,
        },
    },
    "loop_learning": {
        "idx": 18,
        # DFS順: 0=前提, 1=行動, 2=結果, 3=シングルループ, 4=ダブルループ, 5=改革, 6=改善
        "slots": {
            "circle1": 0,
            "circle2": 1,
            "circle3": 2,
            "label1":  3,
            "label2":  4,
            "badge1":  5,
            "badge2":  6,
        },
    },
    "circle_overlap": {
        "idx": 19,
        # DFS順: 0=main(組織GOAL), 1=title, 2=sub1(一致), 3=sub2(合意), 4=sub3(了解)
        "slots": {
            "main_label": 0,
            "title":      1,
            "sub1":       2,
            "sub2":       3,
            "sub3":       4,
        },
    },
}

# 通常レイアウトのスロットマップ
# {slide_type: {shape_idx: yaml_field}}
SLOT_MAP = {
    "title": {
        0: "title_en",   # "Organizational|Coaching"
        1: "day",        # "DAY1"
        2: "title_ja",   # "組織コーチング"
    },
    "check_in":        {0: "main_text"},
    "closing_light":   {0: "main_text"},
    "question":        {0: "main_text"},
    "purpose":         {0: "main_text"},
    "key_point":       {0: "main_text"},
    "section_divider": {0: "title"},
    # notice の DFS: 0=AUTO_SHAPE 大枠(空), 1=TEXT_BOX 番号付きリスト, 2=AUTO_SHAPE ヘッダ帯(空), 3=TEXT_BOX ヘッダラベル
    "notice":          {1: "items", 3: "title"},
}

# テキスト編集不要（design baked-in）な type
FIXED_DESIGN_TYPES = {"meditation", "leader_message", "rest_time"}

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R_EMBED = f"{{{NS_R}}}embed"
R_ID    = f"{{{NS_R}}}id"
R_HREF  = f"{{{NS_R}}}href"


# ──────────────────────────────────────────────
# スライド複製
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


def get_flat_text_shapes(shapes):
    """グループシェイプを再帰的に展開し、全テキストシェイプを DFS 順に返す。"""
    result = []
    for s in shapes:
        if hasattr(s, "shapes"):
            result.extend(get_flat_text_shapes(s.shapes))
        elif s.has_text_frame:
            result.append(s)
    return result


def set_shape_text(shape, new_text):
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    lines = str(new_text).split("\n")
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
# agenda レンダラ（最大3項目・highlightで強調切替）
# ──────────────────────────────────────────────
def _build_bullet_paragraph(text, highlighted, src_para_xml, start_at=None):
    """1 項目分の段落 XML を組み立てる。

    - highlighted: True で濃ネイビー、False で淡グレー
    - start_at: 1 以上の整数を渡すと buAutoNum に startAt 属性を付け、
      段落間に空段落 (buNone) を挟んでもリストがリセットされず
      1. / 2. / 3. のように連番表示される
    """
    p_elem = copy.deepcopy(src_para_xml)
    target_clr_hex = "1E3056" if highlighted else "B0B7C3"
    target_clr_xml = f'<a:srgbClr val="{target_clr_hex}"/>'
    target_clr = etree.fromstring(f'<root xmlns:a="{NS_A}">{target_clr_xml}</root>')[0]

    for clr_parent in p_elem.iter():
        for child in list(clr_parent):
            tag = etree.QName(child).localname
            if tag in ("srgbClr", "schemeClr"):
                clr_parent.remove(child)
                new_child = copy.deepcopy(target_clr)
                clr_parent.append(new_child)

    # 連番リセットを防ぐため buAutoNum に startAt を明示する
    if start_at is not None:
        for bu in p_elem.iter(f"{{{NS_A}}}buAutoNum"):
            bu.set("startAt", str(start_at))

    runs = p_elem.findall(f"{{{NS_A}}}r")
    if runs:
        t_elem = runs[0].find(f"{{{NS_A}}}t")
        if t_elem is not None:
            t_elem.text = f" {text}"
        for r in runs[1:]:
            t = r.find(f"{{{NS_A}}}t")
            if t is not None:
                t.text = ""
    return p_elem


def _build_separator_paragraph(src_para_xml):
    p_elem = copy.deepcopy(src_para_xml)
    for r in p_elem.findall(f"{{{NS_A}}}r"):
        t = r.find(f"{{{NS_A}}}t")
        if t is not None:
            t.text = ""
    return p_elem


def render_agenda(prs, slide_def):
    highlight = int(slide_def.get("highlight", 0))
    items = slide_def.get("items", [])
    if not isinstance(items, list):
        items = [str(items)]
    items = [str(x) for x in items if str(x).strip() != ""]
    n = len(items)
    if n == 0:
        return None

    slide = duplicate_slide(prs, AGENDA_VARIANTS[0])
    text_shapes = get_flat_text_shapes(slide.shapes)
    if not text_shapes:
        return slide
    main_shape = text_shapes[0]

    tf = main_shape.text_frame
    txBody = tf._txBody
    existing_paras = txBody.findall(f"{{{NS_A}}}p")
    if len(existing_paras) < 3:
        return slide

    bullet_template = existing_paras[0]
    sep_template = existing_paras[1]

    for p in existing_paras:
        txBody.remove(p)

    for i, item in enumerate(items):
        is_highlighted = (highlight == 0) or (highlight == i + 1)
        new_p = _build_bullet_paragraph(item, is_highlighted, bullet_template, start_at=i + 1)
        txBody.append(new_p)
        if i < n - 1:
            txBody.append(_build_separator_paragraph(sep_template))

    if n > 3:
        main_shape.top = Inches(1.30)
        main_shape.height = Inches(4.10)
        if n >= 7:   new_size = "1600"
        elif n == 6: new_size = "1800"
        elif n == 5: new_size = "2100"
        else:        new_size = "2400"
        for p in txBody.findall(f"{{{NS_A}}}p"):
            for elem in p.iter():
                if elem.tag.endswith("}rPr") or elem.tag.endswith("}endParaRPr"):
                    if "sz" in elem.attrib:
                        elem.attrib["sz"] = new_size
                if elem.tag.endswith("}buSzPts"):
                    elem.attrib["val"] = new_size
        for p in txBody.findall(f"{{{NS_A}}}p"):
            for lnSpc in p.iter(f"{{{NS_A}}}lnSpc"):
                for child in list(lnSpc):
                    child.tag = f"{{{NS_A}}}spcPct"
                    child.attrib["val"] = "100000"

    # 区切り線を再配置
    sp_tree = slide.shapes._spTree
    cxn_elements = []
    for child in list(sp_tree):
        tag = etree.QName(child).localname
        if tag == "cxnSp":
            cxn_elements.append(child)

    if cxn_elements and n > 1:
        line_template_xml = copy.deepcopy(cxn_elements[0])
        for cxn in cxn_elements:
            sp_tree.remove(cxn)
        tf_top_in = (main_shape.top or 0) / 914400.0
        tf_height_in = (main_shape.height or 0) / 914400.0
        for i in range(n - 1):
            y_in = tf_top_in + ((2 * i + 1) / (2 * n - 1)) * tf_height_in
            new_line = copy.deepcopy(line_template_xml)
            for xfrm in new_line.iter():
                tag = etree.QName(xfrm).localname
                if tag == "off":
                    xfrm.attrib["y"] = str(int(y_in * 914400))
            sp_tree.append(new_line)

    return slide


# ──────────────────────────────────────────────
# 通常レンダラ
# ──────────────────────────────────────────────
def render_simple_slot(prs, slide_def, slide_type):
    """title/check_in/closing_light/question/purpose/key_point/section_divider/notice 等。
    fixed design (meditation/leader_message/rest_time) も同経路で複製のみ。"""
    template_idx = TEMPLATE_MAP[slide_type]
    slide = duplicate_slide(prs, template_idx)

    if slide_type in FIXED_DESIGN_TYPES:
        return slide  # design baked-in, テキスト編集なし

    text_shapes = get_flat_text_shapes(slide.shapes)
    slot_map = SLOT_MAP.get(slide_type, {})

    for shape_idx, field in slot_map.items():
        if shape_idx >= len(text_shapes):
            continue
        if slide_type == "notice" and field == "items":
            items = slide_def.get("items", [])
            if isinstance(items, list):
                content = "\n".join(items)
                set_shape_text(text_shapes[shape_idx], content)
            continue
        if field in slide_def:
            set_shape_text(text_shapes[shape_idx], slide_def[field])

    return slide


def render_fillable(prs, slide_def):
    name = slide_def.get("name")
    if name not in FILLABLE_MAP:
        print(f"⚠ unknown fillable preset: {name}")
        return None

    spec = FILLABLE_MAP[name]
    template_idx = spec["idx"]
    slots = spec["slots"]
    slide = duplicate_slide(prs, template_idx)
    text_shapes = get_flat_text_shapes(slide.shapes)

    for slot_name, shape_idx in slots.items():
        if shape_idx >= len(text_shapes):
            continue
        if slot_name in slide_def:
            value = slide_def[slot_name]
            # compare_2card は先頭がスペーサー段落のため改行を補う
            if name == "compare_2card" and slot_name in ("card1", "card2"):
                value = " \n" + str(value)
            set_shape_text(text_shapes[shape_idx], value)

    return slide


# ──────────────────────────────────────────────
# 後始末
# ──────────────────────────────────────────────
def delete_slide(prs, idx):
    sldIdLst = prs.slides._sldIdLst
    items = list(sldIdLst)
    target = items[idx]
    rId = target.rId
    prs.part.drop_rel(rId)
    sldIdLst.remove(target)


# ──────────────────────────────────────────────
# auto-bookend（title/closing_light 自動挿入）
# ──────────────────────────────────────────────
def apply_bookend(outline):
    """day / closing_message を outline に持たせると、先頭/末尾に title/closing_light を挿入する。"""
    if not outline.get("bookend", True):
        return outline.get("slides", [])

    slides_def = list(outline.get("slides", []))
    day = outline.get("day")
    closing_message = outline.get("closing_message")

    # 先頭が title 以外なら day 指定で title を追加
    if day and (not slides_def or slides_def[0].get("type") != "title"):
        slides_def.insert(0, {
            "type": "title",
            "day": day,
            "title_en": outline.get("title_en", "Organizational\nCoaching"),
            "title_ja": outline.get("title_ja", "組織コーチング"),
        })
    # 末尾が closing_light 以外なら closing_message 指定で closing_light を追加
    if closing_message and (not slides_def or slides_def[-1].get("type") != "closing_light"):
        slides_def.append({
            "type": "closing_light",
            "main_text": closing_message,
        })
    return slides_def


# ──────────────────────────────────────────────
# メイン
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="org-coaching スライド生成")
    parser.add_argument("yaml_path", help="入力YAML")
    parser.add_argument("output_path", help="出力PPTX")
    parser.add_argument("--template", default=None, help="テンプレートPPTXのパス")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(script_dir, "..", "assets", "TEMPLATE.pptx")

    if not os.path.exists(template_path):
        print(f"エラー: テンプレートが見つかりません: {template_path}")
        sys.exit(1)
    if not os.path.exists(args.yaml_path):
        print(f"エラー: YAML が見つかりません: {args.yaml_path}")
        sys.exit(1)

    with open(args.yaml_path, "r", encoding="utf-8") as f:
        outline = yaml.safe_load(f)

    slides_def = apply_bookend(outline)

    prs = Presentation(template_path)
    original_count = len(prs.slides)
    print(f"テンプレート読み込み: {template_path} ({original_count}枚)")

    rendered_count = 0
    for i, slide_def in enumerate(slides_def):
        stype = slide_def.get("type")
        if stype == "agenda":
            render_agenda(prs, slide_def)
        elif stype in TEMPLATE_MAP:
            render_simple_slot(prs, slide_def, stype)
        elif stype == "fillable":
            render_fillable(prs, slide_def)
        else:
            print(f"  ⚠ slide[{i}]: unknown type {stype!r} — スキップ")
            continue
        rendered_count += 1
        print(f"  生成: slide[{i}] type={stype} name={slide_def.get('name','-')}")

    # 元のテンプレートスライド（先頭の original_count 枚）を削除
    for i in range(original_count - 1, -1, -1):
        delete_slide(prs, i)

    prs.save(args.output_path)
    final_count = len(Presentation(args.output_path).slides)
    print(f"\n完了: {args.output_path} ({final_count}枚)")


if __name__ == "__main__":
    main()
