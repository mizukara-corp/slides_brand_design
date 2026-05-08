---
name: career-spirit-slides
description: >
  キャリスピブランドのPPTXスライドをテキスト入力から自動生成するスキル。
  TEMPLATE.pptx（24枚：base 6枚 + fixed 13枚 + fillable 5枚）のデザインを完全に踏襲したまま新しいスライドデッキを作る。
  「キャリスピのスライドを作って」「DSの講義資料を作りたい」「キャリア・自己理解講座のスライドにして」
  などのリクエストで使う。YAMLアウトラインさえ渡せば完成まで一気通貫で行う。
---

# career-spirit-slides スキル

TEMPLATE.pptx（24枚）をテンプレートとして新しいPPTXを生成するスキル。
背景・ロゴ・フォント・カラーはすべて元資料を引き継ぐ。著作権表示は自動的に © 2026 に統一される。

```python
SKILL_DIR = "/Users/yutakondo/Projects/personal/education/03_Create_slide/.claude/skills/career-spirit-slides"
```

---

## スライドタイプ一覧

### リッチテンプレート（動的テキスト注入・5枚）★おすすめ

セミナーの **オープニング・章扉・比較構図** で使う。動的にテキスト枠を生成するためレイアウトはコードベース。

| type | 見た目 | 必須フィールド | 任意 |
|------|--------|----------------|------|
| `cover` | ダーク・オレンジ光彩・SEMINAR/2026 + 大タイトル + サブタイトル | `title` | `seminar`（デフォルト `"SEMINAR / 2026"`）, `subtitle` |
| `agenda` | オレンジ×ダーク斜め分割・GOAL + CHAPTERS（01-04） | `goal_text`, `chapters`（最大4件のリスト） | `goal_label`, `chapter_label`, `chapter_icons`（リスト） |
| `section_rich` | 黒/白分割・SECTION xx + 英語名 + 日本語タイトル | `section_num`, `section_en`, `section_ja` | — |
| `card2` | 白背景・2つの角丸グレーカード（番号バッジ付き） | `title`, `card1_title`, `card1_body`, `card2_title`, `card2_body` | `card1_icon`, `card2_icon` |
| `card3` | 白背景・3つの角丸グレーカード（番号バッジ付き） | `title`, `card1_title`〜`card3_title`, `card1_body`〜`card3_body` | `card1_icon`〜`card3_icon` |

### ベーステンプレート（テキスト編集可・6枚）

| type | 見た目 | 必須フィールド | 任意 |
|------|--------|----------------|------|
| `title_light` | 白背景・中央タイトル＋ロゴ | `title` | — |
| `question` | オレンジ背景・大きな"Q." | `main_text` | — |
| `answer` | 白背景・大きな"A." | `main_text` | — |
| `content_list_4` | 白背景・4つの番号付きボックス（多用注意） | `title`, `item1`, `item2`, `item3`, `item4` | `item1_icon`〜`item4_icon` |
| `memo` | 白背景・大きな1行メッセージ | `content` | — |
| `profile` | プロフィール（写真＋肩書きリスト） | `name` | `name_en`, `affiliation`, `role`, `career1〜3`, `expertise1〜3` |

> ⚠️ **`content_list_4` の使いすぎに注意。** 同じレイアウトが連続するとデッキが単調になるため、内容に応じて `card2` / `card3` / `memo` / `answer` / preset (be_do_have / walls4 / step3_cards / iceberg 等) を交互に使い分けること。

### fixed プリセット（テキスト編集なし・13枚）

`type: preset` + `name` で指定。背景・図形・既存テキストすべてが固定。

| name | 用途 |
|------|------|
| `title` | ダーク・ブランドカバー（先頭自動挿入） |
| `section_dark` | オレンジ×ダーク "Agenda" ディバイダー |
| `section_check` | ダーク "Check in" ディバイダー（末尾自動挿入） |
| `be_do_have` | Be-Do-Have 3階層フレーム |
| `iceberg` | 意識/無意識ピラミッド（5%/95%） |
| `loop_diagram` | 人間の原理原則ループ |
| `trap_diagram` | 「手段の目的化」シルエット図 |
| `walls4` | 知識/理解/行動/変化の4つの壁 |
| `goal_brake` | 理想の未来 vs 現状（ブレーキ図） |
| `step3_cards` | 学習/実践/継続の3カード |
| `timeline_kpi` | 「知る→変わる」タイムライン |
| `group_phases` | グループセッション6フェーズ |
| `case_study` | 受講生事例（緑パネル） |

```yaml
- type: preset
  name: be_do_have
```

### fillable プリセット（レイアウト固定・指定スロット編集可・5枚）

`type: fillable` + `name` + スロット名で指定。改行は `\n`。

| name | 編集可スロット |
|------|----------------|
| `flow4_horizontal` | `title`, `stage`, `box1`, `box2`, `box3`, `box4`, `footnote` |
| `return_card` | `title`（例: `"01　時間的リターン"`） |
| `divided_world` | `title`（質問形式可） |
| `stats_card` | `title`, `label`, `number`, `unit`, `footnote` |
| `before_after` | `title`, `before`, `after` |

```yaml
- type: fillable
  name: stats_card
  title: "受講生の成果"
  label: "平均満足度"
  number: "94.2"
  unit: "%"
  footnote: "※2026年4月時点・回答者N=150"
```

---

## アイコン（ピクトグラム）

`card2` / `card3` / `content_list_4` / `agenda` ではテキスト要素にアイコンを差し込むことで質素なレイアウトに視覚的アクセントを加えられる。
背景はオレンジ（`#EC6F1A`）の円、前景は白で統一される。

### 使い方

```yaml
- type: card3
  title: "技術5: ゾーン拡張の記録"
  card1_title: "記録する"
  card1_icon: "pencil"          # ← アイコン名を指定するだけ
  card1_body: "越えられた境界を「拡張ログ」として記録"
  card2_title: "比較する"
  card2_icon: "compare"
  card2_body: "過去の自分のストレッチ＝今のコンフォート"
  card3_title: "効果"
  card3_icon: "growth_chart"
  card3_body: "自己効力感が蓄積／次の挑戦のハードルが下がる"
```

### 利用可能なアイコン名

**記録・分析・思考系**
- `pencil` / `edit` / `write` — 鉛筆（記録・編集）
- `note` / `record` / `memo` / `document` — ノート/書類
- `book` / `study` — 本（学習）
- `chart` / `bar` — 棒グラフ
- `growth_chart` / `trend` — 右肩上がりグラフ
- `target` / `goal` — 同心円ターゲット
- `lightbulb` / `idea` — 電球
- `brain` / `think` — 脳
- `search` / `magnifier` / `explore` — 虫眼鏡
- `key` / `important` — 鍵
- `clock` / `time` — 時計
- `gear` / `gear9` — 歯車（仕組み）
- `flag` / `milestone` — 旗（マイルストーン）

**動き・関係性**
- `compare` / `vs` / `balance` — 双方向矢印（比較）
- `loop` / `circular` / `cycle` / `repeat` — 循環矢印
- `arrow_right` / `arrow_up` / `arrow_down` / `arrow_left` — 単方向矢印
- `arrow_lr` / `arrow_ud` — 双方向矢印
- `chevron` / `growth` — シェブロン/上昇

**強調・装飾**
- `star` / `star4` / `star8` — 星
- `heart` — ハート
- `lightning` / `flash` — 雷（行動・ひらめき）
- `check` / `ok` / `tick` — チェックマーク
- `sun` / `moon` / `cloud` / `tear` / `donut` — 自然/形状
- `diamond` / `hexagon` / `pentagon` / `octagon` / `decagon` — 多角形
- `explosion` / `burst` — 爆発（インパクト）
- `wave` / `smiley` — 波/スマイリー

**人・チーム・記号**
- `people` / `team` — 3人のシルエット
- `plus` / `minus` / `multiply` / `divide` / `equal` / `not_equal` — 数学記号
- `no` / `block` — 禁止マーク

**直接指定（フォールバック）**
名前にマッチしなければ、その文字列がそのまま絵文字/グリフとして描画される。
```yaml
card1_icon: "📝"      # 絵文字（環境依存）
card1_icon: "→"       # Unicode 記号
card1_icon: "Q"       # 単純な英字（円の中央に表示）
```

### スライドタイプ別の挙動

- **card2 / card3**: タイトル下のカード中央に大型アイコン（約 1.25 inch）を配置。番号バッジは左上に併存。指定がなければ従来レイアウト（テキストのみ）。
- **content_list_4**: 元テンプレートの番号バッジ（小さい円）を約 0.75 inch のアイコン円に置換。`itemN_icon` を指定したアイテムだけ置換され、無指定のアイテムは従来通り番号表示。
- **agenda**: `chapter_icons` を渡すとチャプター番号（01〜04）の代わりにアイコンを表示。リスト要素は対応するチャプターの位置に1対1で適用。

---

## YAMLオプション

### auto-bookend（カバー・クロージングの自動挿入）

| フィールド | デフォルト | 説明 |
|-----------|-----------|------|
| `bookend` | `true` | `false` で自動挿入を無効化 |
| `cover` | `true` | `false` で先頭 `title` カバーをスキップ |
| `closing` | `true` | `false` で末尾 `section_check` をスキップ |

```yaml
bookend: true   # デフォルトで title + section_check が前後に自動挿入される

slides:
  - type: title_light
    title: "セッションの価値"
  # → 自動的に [title] → [title_light] → [section_check] の3枚構成になる
```

---

## 使い方フロー

### STEP 1：アウトライン設計

ユーザーから講義テキスト・台本・アジェンダなどを受け取り、各セクションを上記のスライドタイプに割り当てる。

**注意点:**
- 丸数字（①②③）はフォントで文字化けする可能性があるため `1.` `2.` など半角に変換する
- 不要なスロットを設定しないと元テンプレートのテキストが残る点に注意
- `content_list_4` の `item1〜4` は1行ずつ。改行を含めたい場合は `\n` を使う
- 改行を含むフィールドは YAML の `|` 記法を使うと書きやすい

### STEP 2：outline.yaml を作成する

`/tmp/outline.yaml` に書き出す。サンプル・全フィールドの詳細は：

```python
Read(f"{SKILL_DIR}/docs/yaml-template.md")
```

### STEP 3：スクリプトを実行する

```bash
SD="/Users/yutakondo/Projects/personal/education/03_Create_slide/.claude/skills/career-spirit-slides"
python3 "$SD/scripts/generate.py" /tmp/outline.yaml /tmp/output.pptx
```

`--template` で別パスのテンプレートを指定可能（デフォルトは `assets/TEMPLATE.pptx`）。

### STEP 4：QAする（PDF化して目視確認）

```bash
soffice --headless --convert-to pdf --outdir /tmp/ /tmp/output.pptx
mkdir -p /tmp/qa && rm -f /tmp/qa/*.jpg 2>/dev/null
pdftoppm -jpeg -r 80 /tmp/output.pdf /tmp/qa/s
ls /tmp/qa/
```

Read ツールで各スライド画像を確認する。**チェックポイント：**
- テキストが枠内に収まっているか（溢れる場合は文を短くする）
- `content_list_4` の各 item が長すぎないか
- 丸数字が文字化けしていないか
- fillable のスロットが正しく置換されているか

問題があれば `outline.yaml` を修正して STEP 3 から再実行。

### STEP 5：ワークスペースに保存する

```bash
cp /tmp/output.pptx "/Users/yutakondo/Projects/personal/education/03_Create_slide/<ファイル名>.pptx"
```

---

## 既存PPTXの編集（mode: edit）

既存 PPTX の末尾または指定位置にスライドを追加する。

```yaml
mode: edit
input: /path/to/existing.pptx
position: end           # "end" または整数（0始まり）
bookend: false          # 既存ファイルへの追記なので false 推奨

slides:
  - type: question
    main_text: "追加する問いかけ"
```

---

## トラブルシューティング

| 症状 | 対処 |
|------|------|
| テキストが溢れる | フィールドの行数を減らすか短い文に書き換える |
| 丸数字が文字化けする | ①②③ を 1. 2. 3. に変換する |
| fillable のスロットが範囲外と警告 | `docs/yaml-template.md` でスロット名を再確認 |
| スライドが空白 | `type` 名のスペルを確認 |
| エラー: template not found | `--template` で TEMPLATE.pptx のパスを明示する |
| soffice 変換失敗 | TEMPLATE.pptx を make_template.py で再生成（orphan slide を除去） |

---

## テンプレートを更新したいとき

`assets/SOURCE.pptx`（元の `cw_DS_source.pptx` のコピー）を編集後、再生成：

```bash
python3 "$SD/scripts/make_template.py"
```

抽出するスライドの選択は `make_template.py` 冒頭の `EXTRACT_SLIDES` リストで定義されている。
