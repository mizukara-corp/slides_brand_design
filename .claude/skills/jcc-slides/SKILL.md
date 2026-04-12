---
name: jcc-slides
description: >
  JCCブランドのPPTXスライドをテキスト入力から自動生成するスキル。
  TEMPLATE.pptx（34枚：ベース9枚 + fixedプリセット16枚 + fillable9枚）のデザインを完全に踏襲したまま新しいスライドデッキを作る。
  「JCCのスライドを作って」「DAY2の資料を作りたい」「講義スライドを新しく作って」
  などのリクエストで使う。YAMLアウトラインさえ渡せば完成まで一気通貫で行う。
---

# jcc-slides スキル

TEMPLATE.pptx（34枚）をテンプレートとして新しいPPTXを生成するスキル。  
背景・ロゴ・フォント・カラーはすべて元資料を引き継ぐ。著作権表示は自動的に © 2026 に統一される。

```python
# 以降 {SKILL_DIR} は下記パスを指す（コードブロック内でそのまま使う）
SKILL_DIR = "/sessions/stoic-modest-hamilton/mnt/03_Create_slide/.claude/skills/jcc-slides"
```

**スキル起動後の最初のアクションは必ず [ユーザー状態の検出（4 段階）](#user-state) から始めること。**  
会話の文脈からすでに状態が明らかな場合（テキストが貼り付けられている等）は検出をスキップし、該当フローへ直接進む。

---

## スライドタイプ一覧

### ベーステンプレート（テキスト変更可）

| type | 見た目 | 必須フィールド | 任意 |
|------|--------|----------------|------|
| `title` | ダーク・中央タイトル | `day` | — |
| `section` | ダーク・大見出し（2行） | `title_en` | `title_ja` |
| `content_list` | ダーク・左タイトル＋箇条書き | `section_label`, `body` | `subtitle`, `footnote` |
| `card2_dark` | ダーク・2カラムカード（枠） | `title`, `card1`, `card2` | — |
| `card2_light` | ライト・2カラムカード（白） | `title`, `card1`, `card2` | — |
| `card3_dark` | ダーク・3カラム図解（番号付き） | `title`, `col1_desc`, `col1_keyword`, `col2_desc`, `col2_keyword`, `col3_desc`, `col3_keyword` | — |
| `table` | ダーク・2列テーブル | `title`, `rows` | — |
| `memo` | ライト・左タイトル＋テキスト | `label`, `content` | — |
| `question` | ダーク・中央Question | `main_text` | `category` |

### fixedプリセット（図解・フレームワーク図をそのまま挿入）

図形・色・テキストすべてが固定。`type: preset` + `name` で指定する。
プリセット選択時はグリッド画像を表示して番号で選ばせる。name 一覧は `docs/preset-fixed.md` 参照。

```python
present_files([f"{SKILL_DIR}/assets/thumbnails/fixed_grid.jpg"])
Read(f"{SKILL_DIR}/docs/preset-fixed.md")   # name 確認が必要なとき
```

```yaml
- type: preset
  name: be_do_have_v1   # name は docs/preset-fixed.md で確認
```

### fillableプリセット（レイアウト固定・テキスト変更可）

`type: fillable` + `name` + スロット名で指定する。
プリセット選択時はグリッド画像を表示して選ばせる。name・スロット一覧は `docs/preset-fillable.md` 参照。
改行は `\n`、スロット省略時はテンプレートのデフォルトテキストが残る点に注意。

```python
present_files([f"{SKILL_DIR}/assets/thumbnails/fillable_grid.jpg"])
Read(f"{SKILL_DIR}/docs/preset-fillable.md")  # スロット確認が必要なとき
```

```yaml
- type: fillable
  name: mvv_orange       # name・スロット名は docs/preset-fillable.md で確認
  content: "組織コーチングとは\nコレクティブエフィカシーを最大限高めること"
```

---

## YAMLオプション

### auto-bookend（タイトル・クロージングの自動挿入）

outline.yaml のトップレベルフィールドを使って、先頭・末尾スライドを自動挿入できる。

| フィールド | デフォルト | 説明 |
|-----------|-----------|------|
| `day` | — | `title` スライドのテキスト（例: `"DAY 2 -"`）。指定時のみ先頭に挿入 |
| `bookend` | `true` | `false` にすると自動挿入を無効化 |
| `closing_en` | `"Thank You"` | 末尾 closing スライドの英語テキスト |
| `closing_ja` | `""` | 末尾 closing スライドの日本語テキスト |

```yaml
day: "DAY 2 -"
closing_en: "Thank You"
closing_ja: "本日もありがとうございました"

slides:
  - type: section
    title_en: "BE-DO-HAVE"
    title_ja: "マインドと行動の循環"
  # → 先頭に title（DAY 2 -）、末尾に closing が自動挿入される
```

**注意:** `day` 指定済みでも先頭に `type: title` があれば重複挿入しない。無効化は `bookend: false`。`closing_ja` 省略で日本語行は自動クリア。

### bundle（1エントリ→複数スライドへの展開）

`type: section_start` を使うと、**セクション見出し + AGENDA の 2 枚を 1 エントリで生成**できる。

| type | 展開後のスライド | 用途 |
|------|----------------|------|
| `section_start` | `section` + `content_list(AGENDA)` | 各チャプターの冒頭 |

```yaml
# ── section_start の使い方 ──
- type: section_start
  title_en: "BE-DO-HAVE"          # section の英語タイトル
  title_ja: "マインドと行動の循環"  # section の日本語タイトル（省略可）
  agenda_label: "AGENDA"          # ラベル（省略時 "AGENDA"）
  agenda_items: |                 # AGENDA 本文（content_list の body 相当）
    1. Be-Do-Have フレームワーク（30分）
    2. ビリーフシステムの仕組み（30分）
    3. 個人ワーク（20分）
  subtitle: ""                    # サブタイトル（省略時は自動クリア）
  footnote: " "                   # 注釈（省略時は " " でクリア）
```

↓ 上記 1 エントリが `section` + `content_list(AGENDA)` の 2 枚に展開される。

**注意:** `agenda_items` 省略時は空の content_list が生成される。`subtitle` は省略で自動クリア。

### swap（type alias + variant で見た目を切り替え）

`type` に alias 名を、`variant` にバリアント名を書くと、対応する実際の type/name に自動解決される。  
コンテンツを書き直さずに**ダーク↔ライト、カラー変更**を試せる。

| alias | variant | 解決先 |
|-------|---------|--------|
| `card2` | `dark`（default）/ `light` | `card2_dark` / `card2_light` |
| `mvv` | `orange`（default）/ `gray` / `pink` | `fillable` mvv\_orange/gray/pink |
| `be_do_have` | `v1`（default）〜 `v6` | `preset` be\_do\_have\_v1〜v6 |
| `coaching_matrix` | `v1`（default）/ `v2` | `preset` coaching\_matrix\_v1/v2 |
| `goal_matrix` | `blank`（default）/ `filled` | `preset` goal\_matrix\_blank/filled |
| `genjo_wave` | `plain`（default）/ `labeled` | `fillable` genjo\_wave / genjo\_wave\_labeled |

```yaml
# variant を切り替えるだけでデザインが変わる（省略時はデフォルト）
- type: card2
  variant: light        # dark（default）/ light
  title: "タイトル"
  card1: "左カード\n本文"
  card2: "右カード\n本文"

- type: mvv
  variant: gray         # orange（default）/ gray / pink
  content: "組織コーチングとは\nコレクティブエフィカシーを最大限高めること"
```

**注意:** `preset` 解決（`be_do_have` 等）はコンテンツフィールド不要。`genjo_wave` / `be_do_have` など他の alias の詳細サンプルは、STEP 2 で `docs/yaml-template.md` を Read して確認すること。

---

<a name="user-state"></a>
## ユーザー状態の検出（4 段階）

スキル起動時にまず下記の 1 問でユーザーの準備状況を把握する。
**会話の文脈からすでに状態が明らかな場合は質問をスキップしてよい。**

```python
AskUserQuestion(
    header="スライドの準備状況を教えてください",
    options=[
        "1. まだ何も決まっていない（テーマから一緒に考えたい）",
        "2. テーマは決まっているが内容はこれから",
        "3. アジェンダ（章立て）はあるが各スライドの内容がまだ",
        "4. 内容（テキスト・箇条書き）がほぼ揃っている",
    ]
)
```

| 選択 | 状態名 | 進むフロー |
|------|--------|-----------|
| 1 | **braindump** | → [ブレインダンプフロー](#braindump) でゼロから一緒に考える |
| 2 | **theme-only** | → [Q&A フロー](#qa-flow)（フェーズ 1 から） |
| 3 | **theme+agenda** | → [アジェンダ貼り付けフロー](#agenda-flow) でアジェンダを受け取りフェーズ 2 へ |
| 4 | **all-ready** | → [直接生成モード](#direct-mode)（STEP 1 から） |

---

<a name="braindump"></a>
## フロー①：ブレインダンプ（状態 1）

コンテンツがゼロの状態。Claude がアジェンダを一緒に設計し、フロー②へ引き継ぐ。

```python
Read(f"{SKILL_DIR}/flows/flow1_braindump.md")  # このフローに入ったら実行
```

---

<a name="agenda-flow"></a>
## フロー②：アジェンダ貼り付け（状態 3）

章立てはあるがスライド内容がまだの状態。アジェンダを受け取って各セクションの内容を収集する。

```python
Read(f"{SKILL_DIR}/flows/flow2_agenda.md")  # このフローに入ったら実行
```

---

<a name="qa-flow"></a>
## フロー③：Q&A フロー（状態 2）

テーマはあるが内容がゼロの状態。セクション数から 1 つずつ聞いていく。

```python
Read(f"{SKILL_DIR}/flows/flow3_qa.md")  # このフローに入ったら実行
```

---

<a name="direct-mode"></a>
## フロー④：直接生成モード（状態 4）
<!-- flow4.md は存在しない。このフローの手順は以下の STEP 1〜5 に直接記述されている -->


### STEP 1：アウトライン設計

| 使いたい表現 | type |
|------------|------|
| ダーク・中央大タイトル | `section` |
| 左ラベル＋箇条書き | `content_list` |
| 2つのキーワードを対比 | `card2_dark` / `card2_light` |
| 3概念を番号付き図解 | `card3_dark` |
| 2列対応表 | `table` |
| 本文・引用・名言 | `memo` |
| 問いかけ | `question` |

**注意点（必ず守ること）：**
- 丸数字（①②③）はフォントで文字化けするため `1.` `2.` など半角に変換する
- `footnote` を設定しないスライドには `footnote: " "` を入れてテンプレートの残存テキストを消す
- `body` の各行が箇条書きの1項目になる（YAML の `|` 記法を使う）
- `card1/card2` は1行目がカードタイトル、2行目以降が本文

### STEP 2：outline.yaml を作成する

`/tmp/outline.yaml` に書き出す。全タイプのフィールド一覧・bundle/swap/preset/fillable のサンプルが必要なら読み込む：

```python
Read(f"{SKILL_DIR}/docs/yaml-template.md")
```

### STEP 3：スクリプトを実行する

> ⚠️ **generate.py は Read しないこと。** 1,100行超のため Read するとトークンを大量消費する。
> エラー調査が必要な場合も `grep` や `offset/limit` 付きの Read で必要な箇所だけ参照すること。

```bash
SD="/sessions/stoic-modest-hamilton/mnt/03_Create_slide/.claude/skills/jcc-slides"
python "$SD/scripts/generate.py" /tmp/outline.yaml /tmp/output.pptx --template "$SD/assets/TEMPLATE.pptx"
```

### STEP 4：QAする

```bash
python /sessions/stoic-modest-hamilton/mnt/.claude/skills/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf /tmp/output.pptx
rm -f /tmp/slide_qa-*.jpg
pdftoppm -jpeg -r 80 /tmp/output.pdf /tmp/slide_qa
ls -1 /tmp/slide_qa-*.jpg
```

Read ツールで各スライドの画像を確認する。**チェックポイント：**
- テキストが枠内に収まっているか（溢れる場合は文を短くする）
- table の行が画面下で切れていないか（推奨: 5行以下）
- card3_dark の図解（三角・ツリー・矢印）が正しく表示されているか
- 丸数字が文字化けしていないか
- `footnote` に不要なテンプレートテキストが残っていないか

問題があれば `outline.yaml` を修正して STEP 3 から再実行。

### STEP 5：ワークスペースに保存する

```bash
cp /tmp/output.pptx "/sessions/stoic-modest-hamilton/mnt/03_Create_slide/<ファイル名>.pptx"
```

---

<a name="edit-existing"></a>
## フロー⑤：既存PPTXの編集（mode: edit / patch）

既存 PPTX へのスライド追加・置換・削除。YAML に `mode: edit` または `mode: patch` を指定して generate.py を実行する。

```python
Read(f"{SKILL_DIR}/flows/flow5_edit.md")  # このフローに入ったら実行
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| テキストが溢れる | body の行数を減らすか短い文に書き換える |
| table の行が切れる | rows を5行以下に絞る |
| 丸数字が文字化けする | ①②③ を 1. 2. 3. に変換する |
| footnote に不要テキストが残る | `footnote: " "` でクリアする |
| スライドが空白 | type 名のスペルを確認 |
| エラー: template not found | `--template` で TEMPLATE.pptx のパスを明示する |
| patch で全スライドが同じ内容になる | **旧バージョンのバグ**。generate.py を最新版に更新する |
| patch の index がずれる | `index`/`before` は**操作前の元のインデックス**で書く（自動補正される） |
| edit で既存スライドが消える | `mode: edit` は追記専用。削除は `mode: patch` の `delete` を使う |
