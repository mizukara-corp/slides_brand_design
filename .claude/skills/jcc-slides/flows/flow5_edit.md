# フロー⑤：既存PPTXの編集（mode: edit / patch）

すでに生成済みの PPTX に対してスライドを**追加・置換・削除**したいときに使う。
新規生成（`mode: new`）と同じ generate.py を使うが、YAML に `mode` と `input` を追加する。

---

## mode: edit — スライドを追加

既存 PPTX の末尾（または指定位置）に新しいスライドを追記する。

```yaml
mode: edit
input: "/sessions/stoic-modest-hamilton/mnt/03_Create_slide/DAY2.pptx"
bookend: false          # 追記なので title/closing は通常 false に
position: end           # "end"（デフォルト）or 0始まりのインデックス番号

slides:
  - type: section
    title_en: "NEW SECTION"
    title_ja: "追加セクション"

  - type: content_list
    section_label: "AGENDA"
    body: |
      追加した項目1
      追加した項目2
    footnote: " "
```

| フィールド | デフォルト | 説明 |
|-----------|-----------|------|
| `mode` | — | `"edit"` を明示 |
| `input` | — | 入力 PPTX の絶対パス（必須） |
| `bookend` | `true` | 追記の場合は `false` 推奨 |
| `position` | `"end"` | `"end"` = 末尾追加 / 整数 = そのインデックスの直前に挿入 |
| `slides` | — | 追加するスライドリスト（通常モードと同じ書き方） |

---

## mode: patch — スライドを外科的に置換・削除・挿入

既存 PPTX に対して `delete` / `replace` / `insert` を組み合わせて適用する。
**`index` は操作前の元の位置**を基準に書く（内部で自動補正される）。

```yaml
mode: patch
input: "/sessions/stoic-modest-hamilton/mnt/03_Create_slide/DAY2.pptx"

operations:
  # ── スライドを削除 ──
  - action: delete
    index: 3            # 元インデックス 3 のスライドを削除

  # ── スライドを置き換え ──
  - action: replace
    index: 5            # 元インデックス 5 を以下の内容で置き換え
    slide:
      type: content_list
      section_label: "KEY MESSAGE"
      subtitle: "Be を変えることがすべての出発点"
      body: |
        1. Be（在り方）が先
        2. Do（行動）が変わる
        3. Have（結果）がついてくる
      footnote: " "

  # ── スライドを挿入 ──
  - action: insert
    before: 7           # 元インデックス 7 の直前に挿入
    slide:
      type: preset
      name: be_do_have_v1

  # ── swap 記法も使える ──
  - action: replace
    index: 10
    slide:
      type: be_do_have
      variant: v3
```

**operations フィールド一覧:**

| フィールド | 対象 action | 説明 |
|-----------|-----------|------|
| `action` | 全 | `"delete"` / `"replace"` / `"insert"` |
| `index` | delete / replace | 削除・置換するスライドの元インデックス（0始まり） |
| `before` | insert | この元インデックスの直前に挿入 |
| `slide` | replace / insert | 新しいスライドのスペック（通常スライドと同じ書き方） |

**複数操作の index 基準:**

```
元の PPTX:  [0:title] [1:section_A] [2:CL_A1] [3:CL_A2] [4:section_B] [5:CL_B1]

操作例:
  - action: delete
    index: 2          ← 元インデックス 2（CL_A1）を削除

  - action: replace
    index: 5          ← 元インデックス 5（CL_B1）を置き換え
    slide: ...        ← delete で1つずれても内部で自動補正される

  - action: insert
    before: 4         ← 元インデックス 4（section_B）の直前に挿入
    slide: ...        ← delete で1つずれても内部で自動補正される
```

> **注意：** `index`/`before` は**操作前の元のインデックス**で書く。
> 複数操作を指定した場合、前の操作によるインデックスのずれは内部で自動的に補正される。

---

## 共通フロー

1. ユーザーから「既存 PPTX の〇〇を変えたい」と要望を受ける
2. 対象 PPTX のスライド一覧を確認する:

```bash
python - <<'EOF'
from pptx import Presentation
prs = Presentation("/path/to/target.pptx")
for i, sl in enumerate(prs.slides):
    texts = [s.text_frame.text[:30] for s in sl.shapes if s.has_text_frame and s.text_frame.text.strip()]
    print(f"  [{i}] {' | '.join(texts[:3])}")
EOF
```

3. 変更箇所のインデックスをユーザーと確認する
4. `mode: edit` または `mode: patch` の YAML を `/tmp/patch_outline.yaml` に書き出す
5. generate.py を実行（フロー④ STEP 3 と同じコマンド。入力ファイル名だけ変える）
6. QA → 保存
