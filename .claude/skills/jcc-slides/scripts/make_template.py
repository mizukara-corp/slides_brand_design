#!/usr/bin/env python3
"""
make_template.py
DAY1.pptx (100枚) から テンプレートスライド＋fixed プリセットスライドを抽出して
TEMPLATE.pptx を生成するスクリプト。

【アルゴリズム】
  1. DAY1.pptx を1インスタンスだけ開く
  2. 対象スライドを同一 prs 内で末尾に複製（メディア重複を防ぐ）
  3. 元の100枚を後ろから削除
  → メディアファイルは共有されるためファイルサイズが大幅に削減される

使い方:
  python make_template.py \
    --input  /path/to/DAY1.pptx \
    --output /path/to/TEMPLATE.pptx

生成後のインデックス対応:
  ── ベーステンプレート（9枚）──
  [0] title          [1] section       [2] card2_dark   [3] memo
  [4] card3_dark     [5] content_list  [6] card2_light  [7] question  [8] table

  ── fixed プリセット（16枚）──
  [9]  belief_system      [10] market_structure   [11] be_do_have_v1
  [12] be_do_have_v2      [13] be_do_have_v3      [14] coaching_matrix_v1
  [15] be_do_have_v4      [16] be_do_have_v5      [17] be_do_have_v6
  [18] belief_bubbles     [19] coaching_matrix_v2 [20] goal_matrix_blank
  [21] goal_matrix_filled [22] logic3_highlight   [23] nonverbal_table
  [24] context3_table

  ── fillable プリセット（7枚）──
  [25] member_autonomy    [26] genjo_wave         [27] genjo_wave_labeled
  [28] principle_comparison
  [29] mvv_orange         [30] mvv_gray           [31] mvv_pink
"""

import sys
import copy
import argparse
import os

try:
    from pptx import Presentation
    from lxml import etree
except ImportError:
    print("python-pptx / lxml が必要です: pip install python-pptx lxml --break-system-packages")
    sys.exit(1)

# 抽出対象: (元インデックス, slide_type)
# ── ベーステンプレート（9枚） ──
EXTRACT_SLIDES = [
    (0,  "title"),
    (2,  "section"),
    (4,  "card2_dark"),
    (5,  "memo"),
    (6,  "card3_dark"),
    (9,  "content_list"),
    (17, "card2_light"),
    (18, "question"),
    (80, "table"),
    # ── fixed プリセット（16枚） ──
    (7,  "belief_system"),

    (22, "market_structure"),
    (42, "be_do_have_v1"),
    (43, "be_do_have_v2"),
    (44, "be_do_have_v3"),
    (51, "coaching_matrix_v1"),
    (53, "be_do_have_v4"),
    (54, "be_do_have_v5"),
    (55, "be_do_have_v6"),
    (56, "belief_bubbles"),
    (58, "coaching_matrix_v2"),
    (61, "goal_matrix_blank"),
    (62, "goal_matrix_filled"),
    (74, "logic3_highlight"),
    (75, "nonverbal_table"),
    (78, "context3_table"),
    # ── fillable プリセット（7枚）──
    (27, "member_autonomy"),       # なぜメンバーの主体性が生まれないのか
    (32, "genjo_wave"),            # 現状（波形・下部テキストのみ変更）
    (33, "genjo_wave_labeled"),    # 現状＋ラベル（波形・オーバーレイ付き）
    (34, "principle_comparison"),  # 原理比較（2列・フッタ付き）
    (45, "mvv_orange"),            # MVV・GOALフレーム（オレンジBOX）
    (50, "mvv_gray"),              # MVV・GOALフレーム（グレーBOX）
    (60, "mvv_pink"),              # MVV・GOALフレーム（ピンクBOX）
]

NS_R    = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R_EMBED = f"{{{NS_R}}}embed"
R_ID    = f"{{{NS_R}}}id"
R_HREF  = f"{{{NS_R}}}href"


def duplicate_within(prs, src_idx):
    """prs の src_idx 番スライドを同一 prs 内で複製して末尾に追加する。"""
    template = prs.slides[src_idx]
    new_slide = prs.slides.add_slide(template.slide_layout)

    # リレーションシップをコピー（埋め込み画像など）
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

    # shape ツリーをコピー、rId 参照を更新
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


def delete_slide(prs, idx):
    sldIdLst = prs.slides._sldIdLst
    sldIdLst.remove(sldIdLst[idx])


def main():
    parser = argparse.ArgumentParser(description="DAY1.pptx からテンプレートスライドを抽出")
    parser.add_argument("--input",  default=None, help="入力 PPTX パス（デフォルト: assets/DAY1.pptx）")
    parser.add_argument("--output", default=None, help="出力 PPTX パス（デフォルト: assets/TEMPLATE.pptx）")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "..", "assets")

    input_path  = args.input  or os.path.join(assets_dir, "DAY1.pptx")
    output_path = args.output or os.path.join(assets_dir, "TEMPLATE.pptx")

    if not os.path.exists(input_path):
        print(f"エラー: 入力ファイルが見つかりません: {input_path}")
        sys.exit(1)

    print(f"入力: {input_path}")
    print(f"出力: {output_path}")

    # 1 インスタンスで開く（メディア重複を防ぐ）
    prs = Presentation(input_path)
    original_count = len(prs.slides)
    print(f"元スライド数: {original_count}")

    extract_indices = [idx for idx, _ in EXTRACT_SLIDES]
    print(f"抽出するスライド（0始まり）: {extract_indices}\n")

    # STEP 1: 対象スライドを末尾に複製
    for orig_idx, slide_type in EXTRACT_SLIDES:
        print(f"  複製: slide[{orig_idx:2d}] → {slide_type}")
        duplicate_within(prs, orig_idx)

    # STEP 2: 元の100枚を削除（後ろから）
    print(f"\n元の {original_count} 枚を削除中...")
    for i in range(original_count - 1, -1, -1):
        delete_slide(prs, i)

    prs.save(output_path)

    # ファイルサイズ表示
    src_size  = os.path.getsize(input_path)  / 1024 / 1024
    dst_size  = os.path.getsize(output_path) / 1024 / 1024
    final_count = len(Presentation(output_path).slides)

    print(f"\n完了: {output_path}")
    print(f"最終スライド数: {final_count} 枚")
    print(f"ファイルサイズ: {src_size:.1f} MB → {dst_size:.1f} MB")

    print("\n── 新インデックス対応表 ──")
    for new_idx, (orig_idx, slide_type) in enumerate(EXTRACT_SLIDES):
        print(f"  [{new_idx}] {slide_type:15s}  ← 元[{orig_idx}]")


if __name__ == "__main__":
    main()
