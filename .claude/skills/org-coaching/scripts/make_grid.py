#!/usr/bin/env python3
"""
make_grid.py
TEMPLATE.pptx を PDF → JPG に変換し、各タイプ別の個別サムネイルと
グリッド画像 (grid.jpg) を assets/thumbnails/ に保存する。

ユーザーが「使いたいレイアウトを選んで」と求められたときに
present_files で 1 枚だけ提示するためのもの。
"""

import os
import sys
import subprocess
import shutil
import tempfile

try:
    from PIL import Image
except ImportError:
    print("Pillow が必要です: pip install pillow --break-system-packages")
    sys.exit(1)


# TEMPLATE.pptx 内のスライド順に対応するラベル
SLIDE_TYPES = [
    "title", "meditation", "leader_message", "check_in", "rest_time", "closing_light",
    "question", "purpose", "key_point", "section_divider", "notice",
    "agenda_h0", "agenda_h1", "agenda_h2", "agenda_h3",
    "result_chain", "compare_2card", "compare_3card", "loop_learning", "circle_overlap",
]


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.abspath(os.path.join(script_dir, ".."))
    template_path = os.path.join(skill_dir, "assets", "TEMPLATE.pptx")
    thumbs_dir = os.path.join(skill_dir, "assets", "thumbnails")

    if not os.path.exists(template_path):
        print(f"エラー: {template_path} が見つかりません。先に make_template.py を実行してください。")
        sys.exit(1)

    os.makedirs(thumbs_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        # PDF 化
        print("LibreOffice で PDF 化中...")
        subprocess.run(
            ["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmpdir, template_path],
            check=True, capture_output=True,
        )
        pdf_path = os.path.join(tmpdir, os.path.splitext(os.path.basename(template_path))[0] + ".pdf")
        if not os.path.exists(pdf_path):
            print(f"エラー: PDF が生成されませんでした: {pdf_path}")
            sys.exit(1)

        # JPG 化
        print("pdftoppm で JPG 化中...")
        out_prefix = os.path.join(tmpdir, "s")
        subprocess.run(
            ["pdftoppm", "-jpeg", "-r", "80", pdf_path, out_prefix],
            check=True, capture_output=True,
        )

        jpgs = sorted(f for f in os.listdir(tmpdir) if f.startswith("s-") and f.endswith(".jpg"))
        if len(jpgs) != len(SLIDE_TYPES):
            print(f"⚠ JPG 数と SLIDE_TYPES が不一致: jpgs={len(jpgs)}, types={len(SLIDE_TYPES)}")

        # 個別サムネイル保存
        for i, (jpg_name, type_name) in enumerate(zip(jpgs, SLIDE_TYPES)):
            src = os.path.join(tmpdir, jpg_name)
            dst = os.path.join(thumbs_dir, f"{type_name}.jpg")
            shutil.copy(src, dst)

        # グリッド画像生成（4 列）
        imgs = [Image.open(os.path.join(tmpdir, j)) for j in jpgs]
        w, h = imgs[0].size
        # サイズを縮小（一辺 250px 程度）
        scale = 250.0 / w
        sw, sh = int(w * scale), int(h * scale)
        cols = 4
        rows = (len(imgs) + cols - 1) // cols
        grid = Image.new("RGB", (sw * cols, sh * rows), "white")
        for idx, img in enumerate(imgs):
            r, c = divmod(idx, cols)
            small = img.resize((sw, sh), Image.LANCZOS)
            grid.paste(small, (c * sw, r * sh))

        grid_path = os.path.join(thumbs_dir, "grid.jpg")
        grid.save(grid_path, quality=78)
        print(f"\n完了:")
        print(f"  個別サムネイル: {thumbs_dir}/{{type}}.jpg ({len(jpgs)} 枚)")
        print(f"  まとめグリッド  : {grid_path}")


if __name__ == "__main__":
    main()
