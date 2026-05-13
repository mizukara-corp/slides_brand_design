#!/usr/bin/env python3
"""
slide.pptx をベースとして、その先頭 1-14 枚を redesign.pptx の 14 枚で置き換える。

戦略：
  1. slide.pptx をコピーして output.pptx を作成
  2. redesign.pptx の 14 枚を output.pptx の末尾に追加（クロスコピー、レイアウト・メディア込み）
  3. 元の 1-14 枚を削除
  4. 新規追加の 14 枚を先頭に並べ替え
"""
import sys, copy, os, shutil
from io import BytesIO
from pptx import Presentation
from lxml import etree

NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_A_DRAWING = "http://schemas.openxmlformats.org/drawingml/2006/main"
R_EMBED = f"{{{NS_R}}}embed"
R_ID = f"{{{NS_R}}}id"
R_HREF = f"{{{NS_R}}}href"


def find_compatible_layout(src_layout, dst_prs):
    """src_layout の name と一致する layout を dst_prs から探す。無ければ first を返す。"""
    src_name = src_layout.name
    for layout in dst_prs.slide_layouts:
        if layout.name == src_name:
            return layout
    # fallback: 最もシンプルそうなレイアウトを探す
    for layout in dst_prs.slide_layouts:
        if layout.name in ("BLANK", "Basic", "TITLE_AND_BODY"):
            return layout
    return dst_prs.slide_layouts[0]


def _transfer_part(rel, pkg, dst_slide_part):
    """1つの relation について、target_part を dst パッケージに移送し、新 rId を返す。
    画像については content（blob）で同一性を判定し、partname の偶発的衝突を避ける。
    """
    reltype_short = rel.reltype.split("/")[-1]
    if rel.is_external:
        return dst_slide_part.target_ref(rel.reltype, rel.target_ref)
    src_part = rel.target_part

    if reltype_short == "image":
        # 画像は blob ベースで dedupe（partname 衝突を避ける）
        target_part = pkg.get_or_add_image_part(BytesIO(src_part.blob))
    else:
        # それ以外は partname ベースで既存検索（同一なら使い回し、違えば src をそのまま）
        partname = src_part.partname
        existing_part = next(
            (p for p in pkg.iter_parts() if p.partname == partname),
            None,
        )
        target_part = existing_part if existing_part is not None else src_part
    return dst_slide_part.relate_to(target_part, rel.reltype)


def _resolve_scheme_colors(spTree, theme_map):
    """spTree 内の <a:schemeClr val="X"/> を、theme_map[X] が定義されていれば
    <a:srgbClr val="..."/> に置換する。
    """
    SCHEME_TAG = f"{{{NS_A_DRAWING}}}schemeClr"
    SRGB_TAG = f"{{{NS_A_DRAWING}}}srgbClr"
    for elem in list(spTree.iter(SCHEME_TAG)):
        val = elem.get("val")
        if val in theme_map:
            new_elem = etree.Element(SRGB_TAG)
            new_elem.set("val", theme_map[val])
            parent = elem.getparent()
            parent.replace(elem, new_elem)


def deep_copy_slide_with_layout(src_prs, src_idx, dst_prs, flatten_layout=False, theme_map=None):
    """src の指定スライドを dst に追加する。
    flatten_layout=True で src スライドのレイアウトの shapes も
    新スライドの spTree に焼き込む（背景・ロゴ・装飾を保持するため）。
    """
    src_slide = src_prs.slides[src_idx]
    target_layout = find_compatible_layout(src_slide.slide_layout, dst_prs)
    new_slide = dst_prs.slides.add_slide(target_layout)

    pkg = dst_prs.part.package

    # Step 1: スライド自身の関連を移送
    rId_map = {}
    for rel in src_slide.part.rels.values():
        reltype_short = rel.reltype.split("/")[-1]
        if reltype_short in ("slideLayout", "notesSlide"):
            continue
        try:
            new_rId = _transfer_part(rel, pkg, new_slide.part)
            rId_map[rel.rId] = new_rId
        except Exception as e:
            print(f"    slide rel skip ({reltype_short}): {e}")

    # Step 2: レイアウト関連を移送（flatten_layout のときだけ）
    layout_shapes_xml = []
    if flatten_layout:
        src_layout = src_slide.slide_layout
        for rel in src_layout.part.rels.values():
            reltype_short = rel.reltype.split("/")[-1]
            if reltype_short in ("slideMaster", "slideLayout"):
                continue
            try:
                new_rId = _transfer_part(rel, pkg, new_slide.part)
                rId_map[rel.rId] = new_rId
            except Exception as e:
                print(f"    layout rel skip ({reltype_short}): {e}")
        # レイアウトの spTree のうち、shape 系を抽出
        layout_spTree = src_layout.shapes._spTree
        for child in layout_spTree:
            tag = etree.QName(child).localname
            if tag in ("sp", "pic", "grpSp", "cxnSp", "graphicFrame"):
                layout_shapes_xml.append(child)

    # Step 3: スライドの spTree を deepcopy して rId を更新
    tree_copy = copy.deepcopy(src_slide.shapes._spTree)
    for elem in tree_copy.iter():
        for attr in (R_EMBED, R_ID, R_HREF):
            if attr in elem.attrib and elem.attrib[attr] in rId_map:
                elem.attrib[attr] = rId_map[elem.attrib[attr]]

    # Step 4: レイアウトの shape を deepcopy して rId を更新
    layout_shape_copies = []
    for shape_elem in layout_shapes_xml:
        shape_copy = copy.deepcopy(shape_elem)
        for elem in shape_copy.iter():
            for attr in (R_EMBED, R_ID, R_HREF):
                if attr in elem.attrib and elem.attrib[attr] in rId_map:
                    elem.attrib[attr] = rId_map[elem.attrib[attr]]
        layout_shape_copies.append(shape_copy)

    # Step 4.5: テーマ色解決（レイアウト切り替えで色が変わるのを防ぐ）
    if theme_map:
        _resolve_scheme_colors(tree_copy, theme_map)
        for shape_copy in layout_shape_copies:
            _resolve_scheme_colors(shape_copy, theme_map)

    # Step 5: 新スライドの spTree に [レイアウト shapes] → [スライド shapes] の順で配置
    dst_tree = new_slide.shapes._spTree
    for child in list(dst_tree):
        dst_tree.remove(child)
    # nvGrpSpPr と grpSpPr は元 spTree のものを保持するため、tree_copy の先頭から取り出す
    header_elements = []
    body_elements = []
    for child in list(tree_copy):
        tag = etree.QName(child).localname
        if tag in ("nvGrpSpPr", "grpSpPr") and not body_elements:
            header_elements.append(child)
        else:
            body_elements.append(child)
    for child in header_elements:
        dst_tree.append(child)
    # レイアウト shape を先に（背景）
    for child in layout_shape_copies:
        dst_tree.append(child)
    # スライド本体の shape を後に（前面）
    for child in body_elements:
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


def delete_slide(prs, idx):
    sldIdLst = prs.slides._sldIdLst
    items = list(sldIdLst)
    target = items[idx]
    rId = target.rId
    prs.part.drop_rel(rId)
    sldIdLst.remove(target)


def main():
    redesign_path = "/tmp/redesign.pptx"
    slide_path = "/tmp/slide.pptx"
    output_path = "/tmp/output.pptx"

    # slide.pptx をベースとしてコピー
    shutil.copy(slide_path, output_path)

    # redesign.pptx を読み込み（14 枚を末尾に追加）
    src_prs = Presentation(redesign_path)
    dst_prs = Presentation(output_path)

    original_count = len(dst_prs.slides)
    print(f"slide.pptx: {original_count} slides; appending 14 redesigned slides")

    # redesign.pptx のテーマ色を実 RGB に解決するためのマップ
    # （元 PPT のテーマでは dk1=白, lt1=ダークネイビーだが、
    #   ホスト pptx のテーマで再評価されると色が変わるため固定する）
    theme_map = {
        "dk1": "FFFFFF",   # ダーク背景上の白文字
        "lt1": "0A2540",   # 明るい要素は元のダークネイビー
        # accent はソースを保ったほうが安全なので置換しない
    }
    # ただし、agenda（slides 0-3）は明るい背景・濃い文字なので theme_map を逆に
    # テーマ色そのまま（dk1=黒系）扱いになるよう個別マップを使う
    agenda_theme_map = {
        # agenda の dk1 は濃い色（ホストでもデフォルトで暗色になるため
        # 明示的にネイビーへ置換）
        "dk1": "1E3056",
    }

    for i in range(len(src_prs.slides)):
        try:
            current_map = agenda_theme_map if i < 4 else theme_map
            deep_copy_slide_with_layout(src_prs, i, dst_prs, flatten_layout=True, theme_map=current_map)
            print(f"  appended: redesign[{i+1}]")
        except Exception as e:
            print(f"  FAILED redesign[{i+1}]: {e}")

    # 元の 1-14 枚を削除（先頭から削除すると index がずれるので後ろから）
    for i in range(13, -1, -1):
        delete_slide(dst_prs, i)

    # 末尾に追加した 14 枚（現在は先頭からの位置 = 残った original_count - 14 + 0..13）
    # 削除後の総数 = original_count - 14 + 14 = original_count
    # 残ったスライドは [元15-27] [追加 redesign 14枚] の順
    # 順序を [追加 14枚] [元15-27] に並べ替え
    final_count = len(list(dst_prs.slides._sldIdLst))
    n_orig_kept = original_count - 14  # 13 (元 15-27)
    # redesign 枚は現在 index n_orig_kept..n_orig_kept+13
    # 先頭に持ってくる
    for i in range(14):
        # 移動元 = n_orig_kept + i
        # 移動先 = i
        move_slide_to(dst_prs, n_orig_kept + i, i)

    dst_prs.save(output_path)
    final = Presentation(output_path)
    print(f"\n完了: {output_path} → {len(final.slides)} 枚")


if __name__ == "__main__":
    main()
