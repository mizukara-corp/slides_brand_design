#!/usr/bin/env python3
"""
make_grid.py
9枚のサムネイルを 3×3 グリッドに合成して grid.jpg を生成するスクリプト。
各セルに番号とタイプ名のラベルを焼き込む。

使い方:
  python make_grid.py [--output /path/to/grid.jpg]
"""

import os
import argparse
from PIL import Image, ImageDraw, ImageFont

# グリッドの定義（表示順 × タイプ名 × 選択番号）
GRID_ITEMS = [
    (1, "content_list",  "1. 箇条書き"),
    (2, "card2_dark",    "2. 2カラム・ダーク"),
    (3, "card2_light",   "3. 2カラム・ライト"),
    (4, "card3_dark",    "4. 3カラム図解"),
    (5, "table",         "5. テーブル"),
    (6, "memo",          "6. メモ・引用"),
    (7, "question",      "7. 問いかけ"),
    (8, "section",       "8. セクション見出し"),
    (9, "title",         "9. タイトル"),
]

COLS = 3
ROWS = 3

# セル内のサムネイルサイズ（元 1500×844 を縮小）
CELL_W = 540
CELL_H = 304

# ラベル領域の高さ
LABEL_H = 44

# セル間のマージン
MARGIN = 8

# 全体の背景色
BG_COLOR = (18, 28, 58)       # ダークネイビー（JCCブランドカラー）
LABEL_BG  = (18, 28, 58)      # ラベル背景（同色）
LABEL_FG  = (255, 255, 255)   # ラベル文字：白
BORDER_COLOR = (60, 80, 130)  # セル枠線


def get_font(size: int):
    """フォントを取得（日本語対応フォントを優先）。"""
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJKjp-Regular.otf",
        "/usr/share/fonts/opentype/noto/NotoSansCJKjp-Regular.otf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def make_grid(thumb_dir: str, output_path: str):
    cell_total_h = CELL_H + LABEL_H

    canvas_w = COLS * CELL_W + (COLS + 1) * MARGIN
    canvas_h = ROWS * cell_total_h + (ROWS + 1) * MARGIN

    canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    font_label = get_font(19)

    for idx, (num, type_name, label_text) in enumerate(GRID_ITEMS):
        col = idx % COLS
        row = idx // COLS

        x = MARGIN + col * (CELL_W + MARGIN)
        y = MARGIN + row * (cell_total_h + MARGIN)

        # ── サムネイル画像を貼る ──
        img_path = os.path.join(thumb_dir, f"{type_name}.jpg")
        if os.path.exists(img_path):
            thumb = Image.open(img_path).resize((CELL_W, CELL_H), Image.LANCZOS)
        else:
            # 画像がない場合はプレースホルダー
            thumb = Image.new("RGB", (CELL_W, CELL_H), (40, 50, 90))
            ph_draw = ImageDraw.Draw(thumb)
            ph_draw.text((CELL_W // 2, CELL_H // 2), type_name,
                         fill=LABEL_FG, anchor="mm", font=get_font(14))

        # 枠線
        draw.rectangle(
            [x - 1, y - 1, x + CELL_W, y + CELL_H + LABEL_H],
            outline=BORDER_COLOR, width=1
        )
        canvas.paste(thumb, (x, y))

        # ── ラベル帯 ──
        label_y = y + CELL_H
        draw.rectangle(
            [x, label_y, x + CELL_W, label_y + LABEL_H],
            fill=LABEL_BG
        )

        # 番号（左揃え・太めの色）
        num_color = (100, 160, 255)  # ライトブルー
        draw.text((x + 8, label_y + LABEL_H // 2), f"{num}.",
                  fill=num_color, anchor="lm", font=font_label)

        # タイプ名（中央）
        draw.text((x + CELL_W // 2, label_y + LABEL_H // 2), label_text,
                  fill=LABEL_FG, anchor="mm", font=font_label)

    canvas.save(output_path, quality=92)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"保存完了: {output_path} ({size_kb} KB)")
    print(f"サイズ: {canvas_w} × {canvas_h} px")


def main():
    parser = argparse.ArgumentParser(description="スライドタイプのグリッド画像を生成")
    parser.add_argument("--output", default=None, help="出力パス（デフォルト: assets/thumbnails/grid.jpg）")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    thumb_dir  = os.path.join(script_dir, "..", "assets", "thumbnails")
    output     = args.output or os.path.join(thumb_dir, "grid.jpg")

    make_grid(thumb_dir, output)


if __name__ == "__main__":
    main()
