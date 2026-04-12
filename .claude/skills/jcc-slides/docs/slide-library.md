# JCC Slide Library — 開発者リファレンス

> **⚠️ これはスキル開発者向けのドキュメントです。Claude が自動的に Read するファイルではありません。**  
> Claude が参照する実行時ファイルは以下です：
> - `docs/preset-fixed.md` — fixed プリセット一覧（name・用途）
> - `docs/preset-fillable.md` — fillable プリセット一覧（スロット仕様）
> - `docs/yaml-template.md` — 全タイプ YAML サンプル
> - `flows/` — 各フローの詳細手順
>
> TEMPLATE.pptx は 34 枚構成（ベース 9 + fixed 16 + fillable 9）。

---

## 目次

1. [TEMPLATE.pptx インデックス一覧](#template-index)
2. [ベーステンプレート（9 種）](#base-templates)
3. [fixed プリセット（16 種）](#fixed-presets) → 詳細は `docs/preset-fixed.md`
4. [fillable プリセット（9 種）](#fillable-presets) → 詳細は `docs/preset-fillable.md`
5. [共通記法ルール](#common-rules)
6. [bundle / swap / auto-bookend / 完全 YAML サンプル](#yaml-options) → 詳細は `docs/yaml-template.md`

---

<a name="template-index"></a>
## 1. TEMPLATE.pptx インデックス一覧

| idx | type / name | カテゴリ |
|-----|-------------|----------|
| 0 | `title` | ベース |
| 1 | `section` | ベース |
| 2 | `card2_dark` | ベース |
| 3 | `memo` | ベース |
| 4 | `card3_dark` | ベース |
| 5 | `content_list` | ベース |
| 6 | `card2_light` | ベース |
| 7 | `question` | ベース |
| 8 | `table` | ベース |
| 9 | `belief_system` | fixed |
| 10 | `market_structure` | fixed |
| 11 | `be_do_have_v1` | fixed |
| 12 | `be_do_have_v2` | fixed |
| 13 | `be_do_have_v3` | fixed |
| 14 | `coaching_matrix_v1` | fixed |
| 15 | `be_do_have_v4` | fixed |
| 16 | `be_do_have_v5` | fixed |
| 17 | `be_do_have_v6` | fixed |
| 18 | `belief_bubbles` | fixed |
| 19 | `coaching_matrix_v2` | fixed |
| 20 | `goal_matrix_blank` | fixed |
| 21 | `goal_matrix_filled` | fixed |
| 22 | `logic3_highlight` | fixed |
| 23 | `nonverbal_table` | fixed |
| 24 | `context3_table` | fixed |
| 25 | `member_autonomy` | fillable |
| 26 | `genjo_wave` | fillable |
| 27 | `genjo_wave_labeled` | fillable |
| 28 | `principle_comparison` | fillable |
| 29 | `mvv_orange` | fillable |
| 30 | `mvv_gray` | fillable |
| 31 | `mvv_pink` | fillable |
| 32 | `fbff_6col` | fillable |
| 33 | `fbff_7col` | fillable |

---

<a name="base-templates"></a>
## 2. ベーステンプレート（9 種）

テキストを自由に差し込めるレイアウト。`type` フィールドで指定する。

---

### `title` — タイトルスライド

**外観:** ダーク背景・中央大テキスト。デッキの冒頭に置くタイトルページ。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `day` | ◎ | DAY 番号テキスト（例: `"DAY 2 -"`） |

```yaml
- type: title
  day: "DAY 2 -"
```

---

### `section` — セクション見出し

**外観:** ダーク背景・2 行テキスト（英語大 + 日本語小）。章の区切りに使う。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `title_en` | ◎ | 英語タイトル（大文字推奨、例: `"PURPOSE"`） |
| `title_ja` | — | 日本語サブタイトル（例: `"このセクションの目的"`） |

```yaml
- type: section
  title_en: "LEADERSHIP"
  title_ja: "リーダーシップの原則"
```

---

### `content_list` — 箇条書きリスト

**外観:** ダーク背景・左上にラベル＋本文箇条書き。最もよく使うレイアウト。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `section_label` | ◎ | 左上ラベル（例: `"PURPOSE"` / `"AGENDA"` / `"SUMMARY"`） |
| `subtitle` | — | サブタイトル（1 行） |
| `body` | ◎ | 箇条書き本文。YAML `\|` 記法推奨。1 行 = 1 項目 |
| `footnote` | — | 下部注釈。不要なら `" "` でテンプレートテキストをクリア |

```yaml
- type: content_list
  section_label: "AGENDA"
  subtitle: "本日のプログラム"
  body: |
    1. チェックイン（15分）
    2. 前回の振り返り（20分）
    3. 新しいフレームワーク（40分）
    4. ペアワーク（30分）
    5. まとめ・宿題（15分）
  footnote: " "
```

> **注意:** `body` は 6〜7 行程度が上限。超えるとテキストが枠外に溢れる。

---

### `card2_dark` — 2 カラムカード（ダーク）

**外観:** ダーク背景・左右 2 枚のカード（枠線あり）。概念の対比・比較に。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `title` | ◎ | スライドタイトル |
| `card1` | ◎ | 左カード。1 行目 = カードタイトル、2 行目以降 = 本文 |
| `card2` | ◎ | 右カード。同上 |

```yaml
- type: card2_dark
  title: "コーチングの 2 つのアプローチ"
  card1: "ディレクティブ\n指示・指導により\nすぐに行動を変える"
  card2: "ノンディレクティブ\n問いかけにより\n自発的な気づきを促す"
```

---

### `card2_light` — 2 カラムカード（ライト）

**外観:** 白背景・左右 2 枚のカード。`card2_dark` と内容は同じだがカラーが異なる。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `title` | ◎ | スライドタイトル |
| `card1` | ◎ | 左カード（1 行目 = カードタイトル） |
| `card2` | ◎ | 右カード（1 行目 = カードタイトル） |

```yaml
- type: card2_light
  title: "目標設定の比較"
  card1: "ストレッチゴール\n現在の能力より\n少し高い目標"
  card2: "ムーンショット\n10 倍の成果を狙う\n非連続な目標"
```

> **注意:** `card2_light` はシェイプインデックスが `card2_dark` と異なる（card1→idx 0, card2→idx 1, title→idx 2）。generate.py の `SLOT_MAP` で正しく定義済み。

---

### `card3_dark` — 3 カラム図解

**外観:** ダーク背景・3 列の番号付き図解。三角・ツリー・矢印などの説明図。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `title` | ◎ | スライドタイトル |
| `col1_desc` | ◎ | 1 列目の説明文 |
| `col1_keyword` | ◎ | 1 列目のキーワード（強調表示） |
| `col2_desc` | ◎ | 2 列目の説明文 |
| `col2_keyword` | ◎ | 2 列目のキーワード |
| `col3_desc` | ◎ | 3 列目の説明文 |
| `col3_keyword` | ◎ | 3 列目のキーワード |

```yaml
- type: card3_dark
  title: "成長の 3 ステージ"
  col1_desc: "まず行動して\n経験から学ぶ段階"
  col1_keyword: "経験学習"
  col2_desc: "パターンを抽象化して\n原則を掴む段階"
  col2_keyword: "概念化"
  col3_desc: "原則を新しい\n状況に応用する段階"
  col3_keyword: "応用実践"
```

---

### `table` — 2 列テーブル

**外観:** ダーク背景・見出し行 + データ行の 2 列テーブル。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `title` | ◎ | スライドタイトル |
| `rows` | ◎ | 行データ。各行は `["左セル", "右セル"]` のリスト |

```yaml
- type: table
  title: "コーチングとティーチングの違い"
  rows:
    - ["観点", "内容"]
    - ["目的", "自発的な気づきを促す"]
    - ["方法", "問いかけ中心"]
    - ["主体", "クライアント"]
    - ["効果", "長期的な変容"]
```

> **注意:** 行数の上限は実用的に 5〜6 行。ヘッダ行を含むとテーブルが見やすくなる。

---

### `memo` — メモ・引用

**外観:** ライト背景・左側にラベル＋右側に本文。名言・補足説明・Key Message に。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `label` | ◎ | 左ラベル（例: `"Memo"` / `"Point"` / `"Key Message"`） |
| `content` | ◎ | 本文テキスト。YAML `\|` 記法推奨 |

```yaml
- type: memo
  label: "Key Message"
  content: |
    リーダーシップとは
    「結果に対して責任を持つ」こと。
    地位や肩書きではなく、
    行動によって示される。
```

---

### `question` — 問いかけ

**外観:** ダーク背景・中央に大きな問いかけテキスト。考える時間を作るスライド。

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `main_text` | ◎ | 問いかけ本文（複数行可） |
| `category` | — | 右上ラベル（例: `"Question"` / `"Check-in"`） |

```yaml
- type: question
  category: "Question"
  main_text: "あなたが「理想のリーダー」と感じる人は\n誰ですか？\nその人のどんな行動がそう感じさせますか？"
```

---

<a name="fixed-presets"></a>
## 3. fixed プリセット（16 種）

詳細仕様（name・説明・用途）は `docs/preset-fixed.md` を参照。

サムネイル一覧 → `assets/thumbnails/fixed_grid.jpg`

```yaml
- type: preset
  name: be_do_have_v1   # 全16種は docs/preset-fixed.md で確認
```

---

<a name="fillable-presets"></a>
## 4. fillable プリセット（9 種）

詳細仕様（name・スロット名・サンプル）は `docs/preset-fillable.md` を参照。

サムネイル一覧 → `assets/thumbnails/fillable_grid.jpg`

```yaml
- type: fillable
  name: mvv_orange       # 全9種・スロット名は docs/preset-fillable.md で確認
  content: "テキスト"
```

---

## 5. 共通記法ルール

### 改行

- YAML 内で `\n` を使う（ダブルクォート文字列の場合）
- 段落の区切り（空行）は `\n\n`
- 複数行のベース本文は YAML の `|` ブロック記法を推奨（`body`, `content`）

```yaml
# ダブルクォート + \n
content: "1 行目\n2 行目\n3 行目"

# | ブロック記法（body などに推奨）
body: |
  1 行目
  2 行目
  3 行目
```

### 禁止文字

| 文字 | 代替 | 理由 |
|------|------|------|
| ①②③ | 1. 2. 3. | 游ゴシックで文字化けする |
| ● ◆ ▶ | - または 文章 | フォント依存で表示が崩れる場合がある |

### footnote のクリア

`content_list` スライドで `footnote` を省略するとテンプレートの残存テキストが表示される。
不要な場合は必ず空白文字でクリアする：

```yaml
footnote: " "
```

### スロット省略

fillable プリセットでスロットを省略すると、テンプレートのデフォルトテキストがそのまま残る。
完全に空にしたい場合は `" "` を渡す：

```yaml
- type: fillable
  name: genjo_wave
  bottom_text: " "   # 空にしたい場合
```

### 著作権表示

generate.py が保存直前に `fix_copyright_year(prs)` を自動実行し、
スライドレイアウト・マスターを含むすべての `© 20xx` を実行時の西暦年に統一する。
手動で変更する必要はない。

---

## 6. bundle / swap / auto-bookend / 完全 YAML サンプル

> これらのリファレンスは `docs/yaml-template.md` に一本化されています。
> SKILL.md の「YAMLオプション」セクションも参照してください。

---

## 7. 開発者向け拡張手順

スキルを拡張・保守する際の手順をタイプ別に記載する。

---

### A. ベーステンプレートを新規追加する

1. **TEMPLATE.pptx にスライドを追加する**（PowerPoint で直接編集）
2. **`generate.py` の `process_slide` 関数**に新タイプの分岐を追加する
3. **SKILL.md のスライドタイプ一覧テーブル**に行を追加する
4. **`docs/yaml-template.md`** にサンプル YAML を追加する
5. **`docs/slide-library.md §2`**（ベーステンプレート一覧）を更新する
6. サムネイル画像を `assets/thumbnails/<type>.jpg` として追加する

---

### B. fixed プリセットを新規追加する

1. **TEMPLATE.pptx にスライドを追加する**（末尾に追記）
2. **`generate.py` の `PRESET_SLIDES` 辞書**に `"<name>": <idx>` を追加する
3. **`docs/preset-fixed.md`** に name・説明・用途を追記する
4. サムネイル画像を `assets/thumbnails/fixed/<name>.jpg` として追加する
5. **グリッド画像を再生成する**（下記コマンド）
6. **`docs/slide-library.md §1`** のインデックス表に行を追加する

```bash
SD="/sessions/stoic-modest-hamilton/mnt/03_Create_slide/.claude/skills/jcc-slides"
python "$SD/scripts/make_grid.py" --type fixed --output "$SD/assets/thumbnails/fixed_grid.jpg"
```

---

### C. fillable プリセットを新規追加する

1. **TEMPLATE.pptx にスライドを追加する**（末尾に追記）
2. **`generate.py` の `FILLABLE_SLIDES` 辞書**に定義を追加する（スロット名・shape idx のマッピング）
3. **`docs/preset-fillable.md`** に name・スロット仕様・サンプル YAML を追記する
4. サムネイル画像を `assets/thumbnails/fillable/<name>.jpg` として追加する
5. **グリッド画像を再生成する**（下記コマンド）
6. **`docs/slide-library.md §1`** のインデックス表に行を追加する

```bash
SD="/sessions/stoic-modest-hamilton/mnt/03_Create_slide/.claude/skills/jcc-slides"
python "$SD/scripts/make_grid.py" --type fillable --output "$SD/assets/thumbnails/fillable_grid.jpg"
```

---

### D. swap alias を新規追加する

1. **`generate.py` の `resolve_swaps` 関数**に alias → type/name のマッピングを追加する
2. **SKILL.md の swap エイリアステーブル**に行を追加する
3. **`docs/yaml-template.md`** に使用例を追記する

---

### E. bundle タイプを新規追加する

1. **`generate.py` の `expand_bundles` 関数**に新タイプの展開ロジックを追加する
2. **SKILL.md の bundle セクション**のテーブルに行を追加する
3. **`docs/yaml-template.md`** にサンプルを追記する

---

### F. QA・確認方法

変更後は必ず以下で動作確認する：

```bash
SD="/sessions/stoic-modest-hamilton/mnt/03_Create_slide/.claude/skills/jcc-slides"

# テスト生成（サンプル YAML を使う）
python "$SD/scripts/generate.py" /tmp/test.yaml /tmp/test.pptx --template "$SD/assets/TEMPLATE.pptx"

# PDF変換 → サムネイル確認
python /sessions/stoic-modest-hamilton/mnt/.claude/skills/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf /tmp/test.pptx
pdftoppm -jpeg -r 80 /tmp/test.pdf /tmp/test_qa
ls /tmp/test_qa-*.jpg
```

---

## 更新履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-04-11 | 初版作成。ベース 9 + fixed 16 + fillable 9 の全 34 種を収録 |
| 2026-04-11 | §6 auto-bookend を追加。§7 完全 YAML サンプルを bookend 対応に更新 |
| 2026-04-11 | §6 bundle（section_start）を追加。auto-bookend を §7 に繰り下げ |
| 2026-04-12 | §3/§4 を preset-fixed.md / preset-fillable.md に分離。§6〜§9 を yaml-template.md へ集約。§7 開発者向け拡張手順を追加 |
| 2026-04-11 | §7 swap（type alias + variant）を追加。auto-bookend を §8、完全サンプルを §9 に繰り下げ |
