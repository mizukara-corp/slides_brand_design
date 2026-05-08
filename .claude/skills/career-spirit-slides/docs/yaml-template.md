# YAML テンプレート集

career-spirit-slides の `outline.yaml` 用フィールド一覧とサンプル。

---

## 全体構造

```yaml
bookend: true       # 先頭/末尾の自動挿入（デフォルト true）
cover: true         # 先頭 title カバーを挿入（デフォルト true）
closing: true       # 末尾 section_check を挿入（デフォルト true）

slides:
  - type: ...       # スライドタイプ
    ...             # タイプごとのフィールド
```

---

## リッチテンプレート（動的テキスト注入）★最優先で使う

### `cover` — セミナータイトルスライド
```yaml
- type: cover
  seminar: "SEMINAR / 2026"           # 省略可（デフォルト同じ）
  title: "コンフォートゾーンを\n使いこなす技術"
  subtitle: "キャリアに迷う20代・30代のための、脳科学 × 実践ワーク"
```
※ `cover` を先頭に置くと自動 bookend カバーをスキップする。

### `agenda` — ゴール＋4章のアジェンダ
```yaml
- type: agenda
  goal_label: "GOAL — 本日のゴール"     # 省略可
  goal_text: "コンフォートゾーンの仕組みを理解し、\n戦略的に出入りする技術を身につける。"
  chapter_label: "CHAPTERS"            # 省略可
  chapters:
    - "コンフォートゾーンの正体"
    - "自分のゾーンを知る"
    - "使いこなす5つの技術"
    - "習慣化と1週間の設計"
  chapter_icons:                       # 省略可。指定すると "01〜04" の代わりにアイコンを表示
    - search
    - target
    - gear
    - flag
```
※ chapters は最大4件まで。それ以上は無視される。
※ `chapter_icons` の要素数が `chapters` より少ない場合、未指定分は番号バッジで自動補完される。

### `section_rich` — セクション扉（番号＋英語名＋日本語タイトル）
```yaml
- type: section_rich
  section_num: "SECTION 01"
  section_en: "Brain Science"
  section_ja: "コンフォートゾーンの正体"
```

### `card2` — 2カラム比較カード
```yaml
- type: card2
  title: "コンフォートゾーンは敵ではない"
  card1_title: "良い側面"
  card1_icon: "heart"             # 省略可。アイコン名 or 絵文字
  card1_body: |
    ・回復・集中・スキル熟達の場
    ・自信の源泉
  card2_title: "悪い側面"
  card2_icon: "no"                # 省略可
  card2_body: |
    ・成長停滞／自己効力感の低下
    ・環境変化への脆さ
```

### `card3` — 3カラムカード（3ゾーン・3要素・3ステップに）
```yaml
- type: card3
  title: "技術5: ゾーン拡張の記録"
  card1_title: "記録する"
  card1_icon: "pencil"            # 省略可。アイコン名 or 絵文字
  card1_body: "越えられた境界を「拡張ログ」として記録"
  card2_title: "比較する"
  card2_icon: "compare"
  card2_body: "過去の自分のストレッチ＝今のコンフォート"
  card3_title: "効果"
  card3_icon: "growth_chart"
  card3_body: "自己効力感が蓄積／次の挑戦のハードルが下がる"
```
※ `cardN_icon` を **1 つでも指定するとアイコン用レイアウト**（カード上部中央に大きなオレンジ円アイコン）に切り替わる。指定しないカードはアイコン無しで本文だけ表示される。
※ 利用可能なアイコン名は SKILL.md の「アイコン（ピクトグラム）」セクション参照。

---

## ベーステンプレート（テキスト編集可）

### `title_light` — 白背景・中央タイトル
```yaml
- type: title_light
  title: "セッションの価値"
```

### `question` — オレンジ背景・大きな"Q."
```yaml
- type: question
  main_text: "どのようにしたら「情報」が「価値」へと変化していきますか？"
```

### `answer` — 白背景・大きな"A."
```yaml
- type: answer
  main_text: "自己適用＝体現"
```

### `content_list_4` — 4つの番号付きボックス
```yaml
- type: content_list_4
  title: "心理的安全性を奪う4つの不安"
  item1: "「無知」な人物と評価される事への不安"
  item1_icon: "search"            # 省略可。番号バッジをアイコンに置換
  item2: "「無能」な人物と評価される事への不安"
  item2_icon: "brain"
  item3: "「否定的」な人物と評価される事への不安"
  item3_icon: "no"
  item4: "「邪魔」な人物と評価される事への不安"
  item4_icon: "people"
```
※ 必ず4項目想定。3項目以下にしたい場合は空欄を渡すか、別のtypeを検討。
※ `itemN_icon` を指定したアイテムだけ番号がアイコンに置換される。指定しないアイテムは元の番号バッジのまま。

### `memo` — 大きな1行メッセージ
```yaml
- type: memo
  content: "GOAL ＞ 手段"
```

### `profile` — プロフィール（写真は元のまま）
```yaml
- type: profile
  name: "山田 太郎"
  name_en: "/ Taro Yamada"
  affiliation: |
    株式会社サンプル CEO
    一般社団法人 〇〇協会 理事
  role: "戦略講座 メイン講師"
  career1: "起業: SaaS スタートアップ立ち上げ"
  career2: "前職: メガベンチャー PdM"
  career3: "新卒: 大手コンサル"
  expertise1: "メイン講師（〇〇講座）"
  expertise2: "個別メンタリング 累計300名"
  expertise3: "セミナー登壇 累計5,000名"
```
※ 顔写真は SOURCE.pptx の画像のまま。差し替えるには PowerPoint で開いて手動置換。

---

## fixed プリセット（テキスト編集なし）

すべて `type: preset` + `name` で指定。

```yaml
- type: preset
  name: be_do_have      # Be-Do-Have 3階層フレーム

- type: preset
  name: iceberg         # 意識/無意識ピラミッド（5%/95%）

- type: preset
  name: walls4          # 4つの壁（知識/理解/行動/変化）

- type: preset
  name: step3_cards     # 学習/実践/継続の3カード

- type: preset
  name: trap_diagram    # 「手段の目的化」シルエット図

- type: preset
  name: goal_brake      # 理想の未来 vs 現状（ブレーキ図）

- type: preset
  name: loop_diagram    # 人間の原理原則ループ

- type: preset
  name: timeline_kpi    # 「知る→変わる」タイムライン

- type: preset
  name: group_phases    # グループセッション6フェーズ

- type: preset
  name: case_study      # 受講生事例（緑パネル）

# ── ディバイダー（通常は bookend で自動挿入）──
- type: preset
  name: title           # ダーク・ブランドカバー

- type: preset
  name: section_dark    # オレンジ "Agenda" ディバイダー

- type: preset
  name: section_check   # ダーク "Check in" ディバイダー
```

---

## fillable プリセット（指定スロット編集可）

### `flow4_horizontal` — 4ステップ横フロー
```yaml
- type: fillable
  name: flow4_horizontal
  title: "成果を作る原理原則"
  stage: "パターン化されている"   # 中段ラベル
  box1: "信念\n価値観"
  box2: "感情"
  box3: "行動"
  box4: "成果\n（結果）"
  footnote: "このパターン自体がコンフォートゾーンであり、現実そのもの。"
```

### `return_card` — リターン種別タイトル
```yaml
- type: fillable
  name: return_card
  title: "01　時間的リターン"
```
※ 中身のイラスト・カードは固定。タイトルのみ編集可。

### `divided_world` — 内的世界 vs 外的世界
```yaml
- type: fillable
  name: divided_world
  title: "なぜ、やりたいこと探しは終着点にたどり着かないのか？"
```
※ 図中の「内的世界」「外的世界」「勤め先」などのラベルは固定。

### `stats_card` — 大数値カード
```yaml
- type: fillable
  name: stats_card
  title: "受講生の圧倒的な実績"
  label: "平均年収増加幅"     # 大数値の上ラベル
  number: "+153.8"            # 大きな数値
  unit: "万円"                # 単位
  footnote: "※2025年8月1日〜2026年3月31日までに卒業した顧客N=62/115"
```
※ 円グラフ部分は固定。

### `before_after` — Before/After対比
```yaml
- type: fillable
  name: before_after
  title: "「パーソナルセッション」担当コーチによるマンツーマン"
  before: "ずっと\n変われない"
  after: "人生が変わる"
```

---

## 完全サンプル

```yaml
bookend: true

slides:
  - type: title_light
    title: "DS講義 - キャリアの本質"

  - type: question
    main_text: "あなたが心から望むキャリアとは何ですか？"

  - type: answer
    main_text: "自己理解の延長にある選択"

  - type: content_list_4
    title: "成長を阻む4つの壁"
    item1: "知識の壁: 知らない"
    item2: "理解の壁: 分からない"
    item3: "行動の壁: やらない"
    item4: "変化の壁: 続かない"

  - type: preset
    name: be_do_have

  - type: preset
    name: walls4

  - type: fillable
    name: stats_card
    title: "受講生の成果"
    label: "平均満足度"
    number: "94.2"
    unit: "%"
    footnote: "※2026年4月時点・回答者N=150"

  - type: memo
    content: "GOAL ＞ 手段"
```

→ 自動的に `[title カバー] + 上記8枚 + [section_check]` の **10枚デッキ** が生成される。

---

## アイコン名の早見表

`card2` / `card3` / `content_list_4` / `agenda` の `*_icon` フィールドで使用可能。

| カテゴリ | 名前 | 見た目 |
|----------|------|--------|
| **記録/学習** | `pencil`, `edit`, `write` | 鉛筆 |
| | `note`, `record`, `memo`, `document` | ノート/書類 |
| | `book`, `study` | 本 |
| **分析/思考** | `chart`, `bar` | 棒グラフ |
| | `growth_chart`, `trend` | 右肩上がりグラフ |
| | `target`, `goal` | 同心円ターゲット |
| | `lightbulb`, `idea` | 電球 |
| | `brain`, `think` | 脳 |
| | `search`, `magnifier`, `explore` | 虫眼鏡 |
| | `key`, `important` | 鍵 |
| | `clock`, `time` | 時計 |
| | `gear`, `gear9` | 歯車 |
| | `flag`, `milestone` | 旗 |
| **動き/関係** | `compare`, `vs`, `balance` | 双方向矢印 |
| | `loop`, `circular`, `cycle`, `repeat` | 循環矢印 |
| | `arrow_right`/`up`/`down`/`left` | 単方向矢印 |
| | `arrow_lr`, `arrow_ud` | 双方向矢印 |
| | `chevron`, `growth` | 上昇シェブロン |
| **強調** | `star`, `star4`, `star8` | 星 |
| | `heart` | ハート |
| | `lightning`, `flash` | 雷 |
| | `check`, `ok`, `tick` | チェック |
| | `sun`, `moon`, `cloud`, `tear`, `donut` | 自然/形 |
| | `diamond`, `hexagon`, `pentagon`, `octagon`, `decagon` | 多角形 |
| | `explosion`, `burst` | 爆発 |
| | `wave`, `smiley` | 波/笑顔 |
| **人/記号** | `people`, `team` | 3人のシルエット |
| | `plus`, `minus`, `multiply`, `divide`, `equal`, `not_equal` | 数学記号 |
| | `no`, `block` | 禁止マーク |

**フォールバック**: 上記に無い文字列は絵文字/グリフとしてそのまま描画。
```yaml
card1_icon: "📝"   # 絵文字
card1_icon: "→"    # Unicode 記号
card1_icon: "Q"    # 単純な英字
```
