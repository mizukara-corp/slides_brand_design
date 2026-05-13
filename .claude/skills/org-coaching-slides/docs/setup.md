# org-coaching-slides セットアップ

## 必要パッケージ

```bash
pip install python-pptx PyYAML lxml --break-system-packages
```

QA 用に LibreOffice と poppler-utils も必要：

```bash
# macOS
brew install --cask libreoffice
brew install poppler
```

## 動作確認

```bash
SD="/Users/yutakondo/Projects/work/06_design/04_Create_slide/.claude/skills/org-coaching-slides"

# サンプル YAML で生成
python3 "$SD/scripts/generate.py" "$SD/docs/sample_outline.yaml" /tmp/output.pptx
ls -la /tmp/output.pptx

# PDF 化して目視確認
soffice --headless --convert-to pdf --outdir /tmp/ /tmp/output.pptx
```

## TEMPLATE.pptx 再生成

`training3.pptx`（ベースデザイン）または `training2.pptx`（図解スライド）を編集した後：

```bash
python3 "$SD/scripts/make_template.py"
```

`make_template.py` 冒頭の `EXTRACT_PLAN` リストで
`(source_key, source_idx, slide_type)` の対応を編集して抽出スライドを切り替えできる。

`source_key` は `"training3"` か `"training2"` のいずれか。

## サムネイル再生成（レイアウト選択 UI 用）

```bash
python3 "$SD/scripts/make_grid.py"
```

`assets/thumbnails/` に各スライドの JPG とまとめ画像 `grid.jpg` が出力される。
