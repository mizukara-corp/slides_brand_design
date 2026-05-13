# フロー⑤：既存PPTXの編集

既存の組織コーチングスライドに差分を加える場合の手順。
新規生成と同じ `generate.py` を使うが、現状の generate.py は edit / patch モード未対応のため、
以下の運用で代替する。

## 運用方針：差分 YAML → 新規 PPTX 生成 → 手動マージ

1. 元の PPTX の構成を確認する：

```bash
python3 - <<'PY'
from pptx import Presentation
prs = Presentation("/path/to/original.pptx")
for i, sl in enumerate(prs.slides):
    texts = [s.text_frame.text[:30] for s in sl.shapes if s.has_text_frame and s.text_frame.text.strip()]
    print(f"  [{i}] {' | '.join(texts[:3])}")
PY
```

2. 追加・置換したいスライドだけを YAML に書く：

```yaml
# /tmp/patch_outline.yaml
bookend: false           # title/closing は元 PPTX 側にあるので追加しない

slides:
  - type: key_point
    main_text: |-
      合意とは、複数の意思が
      理由と理解を通じて納得点に収束する状態

  - type: fillable
    name: compare_3card
    card1_label: "　一致　"
    card1_body: "..."
    # ...
```

3. 差分のみの PPTX を生成：

```bash
SD="/Users/yutakondo/Projects/work/06_design/04_Create_slide/.claude/skills/org-coaching"
python3 "$SD/scripts/generate.py" /tmp/patch_outline.yaml /tmp/patch_output.pptx
```

4. PowerPoint / Keynote で差分 PPTX のスライドをコピーし、元 PPTX の該当箇所に貼り付ける。

5. または `python-pptx` で簡易マージするスクリプトを `scripts/merge_redesign.py` として保持しているので、
   そちらを使うこともできる：

```bash
python3 "$SD/scripts/merge_redesign.py" \
  --base   /path/to/original.pptx \
  --insert /tmp/patch_output.pptx \
  --output /tmp/merged.pptx \
  --at end             # "end" or 0始まりのインデックス
```

---

## 将来：本格的な edit / patch モード

jcc-slides のように `mode: edit` / `mode: patch` を generate.py で対応させる場合の
仕様メモ（実装は別途）：

```yaml
mode: patch
input: "/path/to/original.pptx"

operations:
  - action: delete
    index: 3
  - action: replace
    index: 5
    slide:
      type: key_point
      main_text: "..."
  - action: insert
    before: 7
    slide:
      type: fillable
      name: circle_overlap
      title: "..."
```

`index`/`before` は **操作前の元インデックス**で書き、内部で自動補正する設計とする。
