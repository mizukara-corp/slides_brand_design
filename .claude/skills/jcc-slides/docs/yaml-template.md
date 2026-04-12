# outline.yaml 全タイプサンプル

フロー④ STEP 2 で `/tmp/outline.yaml` に書き出す際の全タイプリファレンス。
必要なタイプだけ抜き出して使う。

---

## 基本構造（auto-bookend あり）

```yaml
day: "DAY X -"           # 先頭に title スライドを自動挿入
closing_en: "Thank You"  # 末尾に closing スライドを自動挿入
closing_ja: "ありがとうございました"

slides:
  # ── ベーステンプレート ──────────────────────────

  - type: section
    title_en: "Section Title"
    title_ja: "セクション日本語タイトル"

  - type: content_list
    section_label: "AGENDA"      # PURPOSE / SUMMARY / KEY MESSAGE / その他
    subtitle: "サブタイトル"      # 省略可
    body: |
      項目1
      項目2
      項目3
    footnote: " "                # 省略するとテンプレートのデフォルトが残る → " " でクリア

  - type: card2_dark
    title: "スライドタイトル"
    card1: "左カードタイトル\n本文テキスト"
    card2: "右カードタイトル\n本文テキスト"

  - type: card2_light
    title: "スライドタイトル"
    card1: "左カードタイトル\n本文テキスト"
    card2: "右カードタイトル\n本文テキスト"

  - type: card3_dark
    title: "スライドタイトル"
    col1_desc: "1列目の説明"
    col1_keyword: "キーワード1"
    col2_desc: "2列目の説明"
    col2_keyword: "キーワード2"
    col3_desc: "3列目の説明"
    col3_keyword: "キーワード3"

  - type: table
    title: "テーブルタイトル"
    rows:
      - ["左セル1", "右セル1"]
      - ["左セル2", "右セル2"]
      - ["左セル3", "右セル3"]

  - type: memo
    label: "Key Message"        # Memo / Point / Key Message / その他
    content: |
      本文テキスト
      2行目テキスト

  - type: question
    category: "Question"
    main_text: "問いかけの文章をここに書く"

  # ── section_start（bundle）─────────────────────

  - type: section_start
    title_en: "BE-DO-HAVE"
    title_ja: "マインドと行動の循環"
    agenda_label: "AGENDA"
    agenda_items: |
      1. Be-Do-Have フレームワーク（30分）
      2. ビリーフシステムの仕組み（30分）
      3. 個人ワーク（20分）
    footnote: " "
  # ↑ section + content_list(AGENDA) の2枚に展開される

  # ── swap（alias + variant）────────────────────

  - type: card2           # variant: dark（default）/ light
    variant: light
    title: "スライドタイトル"
    card1: "左カード\n本文"
    card2: "右カード\n本文"

  - type: be_do_have      # variant: v1（default）〜 v6
    variant: v2

  - type: mvv             # variant: orange（default）/ gray / pink
    variant: gray
    content: "組織コーチングとは\nコレクティブエフィカシーを最大限高めること"

  - type: genjo_wave      # variant: plain（default）/ labeled
    variant: labeled
    overlay_label: "原則"
    bottom_text: "原則があるチームは変化に強い"

  # ── fixedプリセット ──────────────────────────

  - type: preset
    name: be_do_have_v1
  # name 一覧: docs/preset-fixed.md

  # ── fillableプリセット ────────────────────────

  - type: fillable
    name: mvv_orange
    content: "組織コーチングとは\nコレクティブエフィカシーを最大限高めること"
  # name・スロット一覧: docs/preset-fillable.md
```

---

## 注意点チェックリスト

- 丸数字（①②③）→ `1.` `2.` に変換（フォントで文字化けする）
- `footnote` を省略すると前スライドのデフォルトテキストが残る → 必ず `footnote: " "` を入れる
- `body` は YAML `|` 記法で1行1項目
- `card1/card2` は1行目がカードタイトル、2行目以降が本文
- `rows` の推奨は5行以下（それ以上は画面下で切れる）
