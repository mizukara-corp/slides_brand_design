---
name: org-coaching-slides
description: >
  組織コーチング（MIZUKARA ブランド）の PPTX スライドをテキスト入力から自動生成するスキル。
  training3.pptx（DAY1 新ブランド・ベースデザイン）と training2.pptx（図解スライド）から作った
  TEMPLATE.pptx（20 枚：base 6 + 編集可 9 + fillable 5）のデザインを完全に踏襲する。
  「組織コーチングのスライドを作って」「DAY1 の研修資料を作りたい」「組織GOAL合意モデルのスライドにして」
  などのリクエストで使う。
  YAML アウトラインさえ渡せば完成まで一気通貫で行う。
---

# org-coaching-slides スキル

組織コーチング研修用 PPTX を生成するスキル。  
ブランドカラー（ダークネイビー＋オレンジグラデ）・ロゴ・フォント・各図解のレイアウトは
すべて元資料を引き継ぐ。著作権表示は自動的に © 2026 Mizukara,Inc. に統一される。

> 👉 **エンドユーザー向け使い方マニュアル**: [docs/manual.md](docs/manual.md)  
> 👉 **フロー図（mermaid）**: [docs/FLOW.md](docs/FLOW.md)

```python
# 以降 {SKILL_DIR} は下記パスを指す（コードブロック内でそのまま使う）
SKILL_DIR = "/Users/yutakondo/Projects/work/06_design/04_Create_slide/.claude/skills/org-coaching-slides"
```

**スキル起動後の最初のアクションは必ず [ユーザー状態の検出（4 段階）](#user-state) から始めること。**  
会話の文脈からすでに状態が明らかな場合（テキストが貼り付けられている等）は検出をスキップして該当フローへ進む。

---

## ブランド設計

| 項目 | 値 |
|------|----|
| サイズ | 10.00 × 5.625 inch（16:9） |
| 主要背景 | ダークネイビー（一部スライドはオレンジ/ブルー/ホワイトグラデ・ライトグレー） |
| フォント | システム既定（BIZ UDPMincho 系 / Noto Serif Tamil Light） |
| ロゴ | MIZUKARA（右下） |
| アクセント | 黄色（合意の枠／重要観点） |
| 著作権 | ©︎2026 Mizukara,Inc.（左下） |

---

## スライドタイプ一覧

### training3 由来：base デザイン（6 枚）

| type | 見た目 | フィールド |
|------|--------|-----------|
| `title` | オレンジ/ブルー/ホワイト斜めグラデ + 大型タイトル | `day`（"DAY 1 -" など右下）, `title_en`（左上 2 行）, `title_ja`（小さい日本語） |
| `meditation` | ダークネイビー + 中央「瞑 想」 | **編集不可**（デザイン固定） |
| `leader_message` | 暗いシルエット背景 + Leader's Message | **編集不可** |
| `check_in` | オレンジグラデ角 + "Check in" | `main_text`（問いかけ） |
| `rest_time` | カラフルグラデ + Rest Time | **編集不可** |
| `closing_light` | ライトブルー/グレーのライト背景 | `main_text`（締めメッセージ） |

### training3 由来：プレースホルダ付き編集可（2 枚）

| type | 見た目 | 必須 |
|------|--------|------|
| `question` | ダーク・大きな "Q." + 問い文 | `main_text` |
| `purpose` | ダーク・大きな "Purpose 目的" + 段落本文 | `main_text` |

### training2 由来：編集可（7 枚）

| type | 見た目 | 必須 / 任意 |
|------|--------|------------|
| `key_point` | ダーク・"重要な観点" バッジ + フレーム枠内メッセージ | `main_text` |
| `section_divider` | ダーク・中央配置の章タイトル | `title` |
| `notice` | ダーク・"DAY◯の告知" ヘッダー + 番号付きリスト | `title`, `items`（list） |
| `agenda` | ライト・"Agenda 論点" + 番号付きリスト（最大 3 項目） | `items`, `highlight`（0/1/2/3） |

#### `agenda` の `highlight` 値

- `0` 全項目を等しく濃色（初回提示用）
- `1`〜`3` その番号の項目だけ濃色、他は薄グレー（順番に注目を引きたいとき）

> 番号付きリストは元テンプレが「1.」「1.」「1.」のように同じ番号を表示するデザイン仕様。

### training2 由来：fillable プリセット（5 枚）

`type: fillable` + `name` + スロット名で指定。改行は `\n`。

| name | 用途 / 編集可スロット |
|------|----------------------|
| `result_chain` | 結果を作る原理原則の 4 ボックス連鎖。`title`, `box1`（左端＝結果）〜`box4`（右端＝原因/信念） |
| `compare_2card` | 2 カード比較（DO/BE 等）。`title`, `card1`（1 行目＝ラベル）, `card2` |
| `compare_3card` | 3 カード比較（一致/合意/了解）。`card1_label`+`card1_body`, `card2_label`+`card2_body`（中央＝黄色）, `card3_label`+`card3_body` |
| `loop_learning` | シングル/ダブルループ学習図。`circle1`（前提）, `circle2`（行動）, `circle3`（結果）, `badge1`（改革）, `badge2`（改善）, `label1`/`label2` |
| `circle_overlap` | 中央円＋3 サテライト円。`title`, `main_label`（中央円本文・改行可）, `sub1`/`sub2`/`sub3` |

---

## YAML オプション

### auto-bookend（タイトル・クロージングの自動挿入）

outline のトップレベルに以下を書くと、先頭・末尾スライドを自動挿入できる。

| フィールド | デフォルト | 説明 |
|-----------|-----------|------|
| `day` | — | 指定すると先頭に `title` スライドを追加（"DAY 1 -" など） |
| `title_en` | `"Organizational\nCoaching"` | title スライドの英文 |
| `title_ja` | `"組織コーチング"` | title スライドの日本語 |
| `closing_message` | — | 指定すると末尾に `closing_light` スライドを追加 |
| `bookend` | `true` | `false` で自動挿入を無効化 |

```yaml
day: "DAY 1 -"
title_en: "Organizational\nCoaching"
title_ja: "組織コーチング"
closing_message: "本日もありがとうございました"

slides:
  - type: purpose
    main_text: "本日の目的..."
```

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
| 1 | **braindump** | → [ブレインダンプフロー](#braindump) |
| 2 | **theme-only** | → [Q&A フロー](#qa-flow) |
| 3 | **theme+agenda** | → [アジェンダ貼り付けフロー](#agenda-flow) |
| 4 | **all-ready** | → [直接生成モード](#direct-mode) |

---

<a name="braindump"></a>
## フロー①：ブレインダンプ（状態 1）

```python
Read(f"{SKILL_DIR}/flows/flow1_braindump.md")
```

---

<a name="agenda-flow"></a>
## フロー②：アジェンダ貼り付け（状態 3）

```python
Read(f"{SKILL_DIR}/flows/flow2_agenda.md")
```

---

<a name="qa-flow"></a>
## フロー③：Q&A フロー（状態 2）

```python
Read(f"{SKILL_DIR}/flows/flow3_qa.md")
```

---

<a name="direct-mode"></a>
## フロー④：直接生成モード（状態 4）

### STEP 1：アウトライン設計

| 使いたい表現 | type |
|------------|------|
| DAY◯ のタイトル | `title` |
| 瞑想セッション | `meditation` |
| リーダーメッセージ | `leader_message` |
| 参加者への問い（冒頭） | `check_in` |
| 研修目的の宣言 | `purpose` |
| 論点リスト | `agenda` |
| 問いかけ・ワーク | `question` |
| 章タイトル | `section_divider` |
| 中心メッセージ | `key_point` |
| 4 段の原因連鎖 | `fillable: result_chain` |
| 2 概念対比 | `fillable: compare_2card` |
| 3 概念対比 | `fillable: compare_3card` |
| ループ学習図 | `fillable: loop_learning` |
| 中央 + 3 サテライト円 | `fillable: circle_overlap` |
| 次回告知 | `notice` |
| 休憩 | `rest_time` |
| 締めメッセージ | `closing_light` |

**注意点（必ず守ること）：**

- 丸数字（①②③）はフォントで文字化けする可能性があるため必要なら `1.` `2.` などに変換する  
  ただし `notice` の元テンプレは丸数字を使うので、揃えるなら `①` `②` のままで OK。
- `compare_2card` の `card1` / `card2` は 1 行目をラベル、2 行目以降を本文として渡す
- `compare_3card` のラベルは元テンプレ同様に前後にスペースを入れると見栄えが整う（例：`"　合意　"`）
- 改行を含むフィールドは YAML の `|-` 記法を使うと書きやすい
- `meditation` / `leader_message` / `rest_time` は **デザイン固定**。テキスト編集なし

### STEP 2：outline.yaml を作成する

`/tmp/outline.yaml` に書き出す。全フィールド・サンプルは：

```python
Read(f"{SKILL_DIR}/docs/yaml-template.md")
```

### STEP 3：スクリプトを実行する

```bash
SD="/Users/yutakondo/Projects/work/06_design/04_Create_slide/.claude/skills/org-coaching-slides"
python3 "$SD/scripts/generate.py" /tmp/outline.yaml /tmp/output.pptx
```

`--template` で別パスのテンプレートを指定可能（デフォルトは `assets/TEMPLATE.pptx`）。

### STEP 4：QA する（PDF化して目視確認）

```bash
soffice --headless --convert-to pdf --outdir /tmp/ /tmp/output.pptx
mkdir -p /tmp/qa && rm -f /tmp/qa/*.jpg
pdftoppm -jpeg -r 80 /tmp/output.pdf /tmp/qa/s
ls /tmp/qa/
```

Read ツールで各画像を確認。**チェックポイント：**

- テキストが枠内に収まっているか（溢れる場合は文を短くする）
- `compare_2card` のラベル/本文の改行位置が正しいか（1 行目がラベル）
- `compare_3card` で意図したカードに黄色アクセントが入っているか（中央 = card2 が固定で黄色）
- 丸数字が文字化けしていないか
- `agenda` の `highlight` が指定したインデックスに合致しているか

問題があれば `outline.yaml` を修正して STEP 3 から再実行。

### STEP 5：ワークスペースに保存する

```bash
cp /tmp/output.pptx "/Users/yutakondo/Projects/work/06_design/04_Create_slide/<ファイル名>.pptx"
```

---

<a name="edit-existing"></a>
## フロー⑤：既存 PPTX の編集

```python
Read(f"{SKILL_DIR}/flows/flow5_edit.md")
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| テキストが溢れる | フィールドの行数を減らすか短い文に書き換える |
| 丸数字が文字化けする | ①②③ を 1. 2. 3. に変換するか、フォントを確認 |
| compare_2card のラベルが小さく出る | 1 行目にラベル文字列を記述しているか確認（自動的に先頭スペース行を補う） |
| compare_3card の黄色枠を別カードに付けたい | 元テンプレでは中央(card2)に固定。デザイン変更は `make_template.py` で別 SOURCE を抽出する |
| `meditation` / `rest_time` の文字を変えたい | 元テンプレが画像背景にベイクしているため不可。再生成するなら SOURCE 側を編集 |
| スライドが空白 | `type` 名のスペルを確認 |
| エラー: template not found | `--template` で TEMPLATE.pptx のパスを明示する |
| soffice 変換失敗 | TEMPLATE.pptx を make_template.py で再生成 |

---

## テンプレートを更新したいとき

`training3.pptx`（ベースデザイン）と `training2.pptx`（図解スライド）を編集後、再生成：

```bash
python3 "$SD/scripts/make_template.py"
```

抽出するスライドの選択は `make_template.py` 冒頭の `EXTRACT_PLAN` リストで定義されている
（`(source_key, source_idx, slide_type)` のタプル）。

---

## TEMPLATE.pptx インデックス対応表

| 新 idx | type | source | src idx | 役割 |
|------|------|--------|---------|------|
| 0 | title | training3 | 0 | Organizational Coaching / DAY◯ |
| 1 | meditation | training3 | 1 | 瞑想（センター） |
| 2 | leader_message | training3 | 2 | Leader's Message |
| 3 | check_in | training3 | 3 | Check in + 問いかけ |
| 4 | rest_time | training3 | 9 | Rest Time |
| 5 | closing_light | training3 | 11 | ライト背景クロージング |
| 6 | question | training3 | 4 | Q. + 問い本文 |
| 7 | purpose | training3 | 6 | Purpose + 段落本文 |
| 8 | key_point | training2 | 12 | 重要な観点フレーム |
| 9 | section_divider | training2 | 19 | 章タイトル（中央配置） |
| 10 | notice | training2 | 20 | DAY告知 |
| 11 | agenda_h0 | training2 | 0 | アジェンダ（強調なし） |
| 12 | agenda_h1 | training2 | 1 | アジェンダ（1 番目強調） |
| 13 | agenda_h2 | training2 | 2 | アジェンダ（2 番目強調） |
| 14 | agenda_h3 | training2 | 3 | アジェンダ（3 番目強調） |
| 15 | result_chain | training2 | 9 | 4 ボックス連鎖 |
| 16 | compare_2card | training2 | 11 | 2 カード比較（DO/BE） |
| 17 | compare_3card | training2 | 17 | 3 カード比較（一致/合意/了解） |
| 18 | loop_learning | training2 | 15 | 3 円ループ図 |
| 19 | circle_overlap | training2 | 18 | 中央大円＋3 サテライト円 |
