# org-coaching YAML テンプレート集

`/tmp/outline.yaml` に書き出して `scripts/generate.py` に渡すための、
全スライドタイプのサンプルとフィールド一覧。

---

## YAML 全体構造

```yaml
# トップレベル（任意 = auto-bookend）
day: "DAY 1 -"                            # title スライドを先頭に自動挿入
title_en: "Organizational\nCoaching"      # title の英文
title_ja: "組織コーチング"                # title の日本語
closing_message: "本日もありがとうございました"  # closing_light を末尾に自動挿入
bookend: true                             # false で自動挿入を無効化

slides:
  - type: <スライドタイプ>
    <フィールド>: <値>
  - type: ...
```

`mode: edit / patch` は現状未対応（create のみ）。差分編集は `flows/flow5_edit.md` 参照。

---

## training3 由来：base デザイン（6 種）

### `title` — タイトルスライド（DAY◯）

```yaml
- type: title
  day: "DAY 1 -"
  title_en: "Organizational\nCoaching"
  title_ja: "組織コーチング"
```

| field | 必須 | 説明 |
|-------|------|------|
| `day` | ✅ | 右下に表示する DAY 表記（例: "DAY 1 -" / "DAY 2"） |
| `title_en` | — | 左上の英タイトル。`\n` で改行（デフォルト "Organizational\nCoaching"） |
| `title_ja` | — | 左下の日本語サブタイトル（デフォルト "組織コーチング"） |

---

### `meditation` — 瞑想セッション（デザイン固定）

```yaml
- type: meditation
```

テキスト編集不可。背景・"瞑 想" の文字はデザインにベイクされている。

---

### `leader_message` — リーダーズメッセージ（デザイン固定）

```yaml
- type: leader_message
```

テキスト編集不可。"Leader's Message / リーダーメッセージ" は固定。

---

### `check_in` — Check-in 問いかけ

```yaml
- type: check_in
  main_text: "今この瞬間、感じていることは何ですか？"
```

| field | 必須 | 説明 |
|-------|------|------|
| `main_text` | ✅ | 問いかけ文（1〜2 行推奨） |

---

### `rest_time` — 休憩（デザイン固定）

```yaml
- type: rest_time
```

テキスト編集不可。"Rest Time" は固定。

---

### `closing_light` — ライト背景クロージング

```yaml
- type: closing_light
  main_text: "本日もありがとうございました"
```

| field | 必須 | 説明 |
|-------|------|------|
| `main_text` | ✅ | 締めメッセージ（1 行推奨） |

---

## training3 由来：プレースホルダ付き編集可（2 種）

### `question` — Q. 質問スライド

```yaml
- type: question
  main_text: |-
    組織コーチングとは
    何を実現するための営みですか？
```

| field | 必須 | 説明 |
|-------|------|------|
| `main_text` | ✅ | 質問文。改行可 |

---

### `purpose` — Purpose 目的スライド

```yaml
- type: purpose
  main_text: |-
    本セッションのゴールは、経営チームが共通言語で
    「現状の外側のGOAL」を定義し、
    心から合意した状態でDay2に臨むことである。
```

| field | 必須 | 説明 |
|-------|------|------|
| `main_text` | ✅ | 段落本文。改行可 |

---

## training2 由来：編集可（4 種）

### `key_point` — 重要な観点フレーム

```yaml
- type: key_point
  main_text: |-
    合意は意志の一致ではない。
    理由と理解を共有した「納得点」である。
```

| field | 必須 | 説明 |
|-------|------|------|
| `main_text` | ✅ | フレーム枠内に表示するメッセージ。改行可 |

---

### `section_divider` — 章タイトル（中央配置）

```yaml
- type: section_divider
  title: "合意の意思決定モデル"
```

| field | 必須 | 説明 |
|-------|------|------|
| `title` | ✅ | 中央配置の章タイトル（1 行推奨） |

---

### `notice` — DAY 告知

```yaml
- type: notice
  title: "DAY2の告知"
  items:
    - "①  脳のカラクリを理解する"
    - "②  ブレイクスルー領域を特定する"
    - "③  GOAL達成し続ける組織を編成する"
```

| field | 必須 | 説明 |
|-------|------|------|
| `title` | ✅ | ヘッダーバッジ文言 |
| `items` | ✅ | 番号付きリスト（最大 3 件推奨。丸数字プレフィックスは自分で付ける） |

---

### `agenda` — アジェンダ（強調モード切替）

```yaml
- type: agenda
  highlight: 0          # 0=強調なし / 1〜3=該当項目を強調
  items:
    - 組織の現状を客観的に観る
    - GOAL設定の原理原則を学ぶ
    - 組織GOAL合意の実践演習
```

| field | 必須 | 説明 |
|-------|------|------|
| `items` | ✅ | 1〜3 件のリスト |
| `highlight` | — | 0/1/2/3。デフォルト 0 |

---

## training2 由来：fillable プリセット（5 種）

### `result_chain` — 4 ボックス連鎖

```yaml
- type: fillable
  name: result_chain
  title: "結果を作る原理原則"
  box1: "結果"              # 左端
  box2: "行動"
  box3: "感情"
  box4: "信念・価値観"      # 右端
```

> 矢印が右→左に流れる構成。box4 → box3 → box2 → box1 の順に「原因→結果」を表現する。

---

### `compare_2card` — 2 カード比較

```yaml
- type: fillable
  name: compare_2card
  title: "技術課題と適応課題"
  card1: |-
    技術課題（DO）
    ある課題に対して
    新たな知識やスキルを
    身につけることにより
    特定の「正解」を導き出すことが
    できる課題のこと
  card2: |-
    適応課題（BE）
    自分や組織の価値観や
    考え方に根ざしており
    そのままの価値観では
    対応が難しいような課題のこと
```

> `card1` / `card2` の **1 行目がラベル**、2 行目以降が本文。

---

### `compare_3card` — 3 カード比較

```yaml
- type: fillable
  name: compare_3card
  card1_label: "　一致　"
  card1_body: |-
    一人一人の意志と
    表現する言葉が
    一語一句ピタッと
    揃っている状態。
  card2_label: "　合意　"
  card2_body: |-
    意思を合わせること。
    複数の意思が
    理由と理解を通じて
    "納得点"に
    収束する状態。
  card3_label: "　了解　"
  card3_body: |-
    自分の意志は関係なく
    相手の内容・意図を
    理解し受け取った状態。
```

> 中央 (card2) のラベルは **黄色枠で強調** される（元テンプレ固定）。

---

### `loop_learning` — シングル/ダブルループ学習図

```yaml
- type: fillable
  name: loop_learning
  circle1: "前提"
  circle2: "行動"
  circle3: "結果"
  badge1: "改革"
  badge2: "改善"
  label1: "シングルループ学習"
  label2: "ダブルループ学習"
```

---

### `circle_overlap` — 中央円 ＋ 3 サテライト円

```yaml
- type: fillable
  name: circle_overlap
  title: "一致・合意・了解の区別"
  main_label: "\n組織\nGOAL"
  sub1: "一致"
  sub2: "合意"
  sub3: "了解"
```

> `main_label` の先頭に空行を入れると中央円の中心に文字が来やすい。

---

## 完全サンプル（DAY1 講義デッキ）

```yaml
day: "DAY 1 -"
title_en: "Organizational\nCoaching"
title_ja: "組織コーチング"
closing_message: "本日もありがとうございました"

slides:
  - type: meditation

  - type: leader_message

  - type: check_in
    main_text: "今この瞬間、感じていることは何ですか？"

  - type: purpose
    main_text: |-
      組織の全員が原理原則に則ったGOAL設定を心から合意し、
      オーナーシップを獲得している状態を共に創る

  - type: agenda
    highlight: 0
    items:
      - 脳のカラクリを理解する
      - ブレイクスルー領域を特定する
      - GOAL達成し続ける組織を編成する

  - type: question
    main_text: |-
      変わり続ける人と変わらない人の
      決定的な違いは何ですか？

  - type: fillable
    name: result_chain
    title: "結果を作る原理原則"
    box1: "結果"
    box2: "行動"
    box3: "感情"
    box4: "信念・価値観"

  - type: fillable
    name: compare_2card
    title: "技術課題と適応課題"
    card1: "技術課題（DO）\nスキル習得で\n対応できる課題"
    card2: "適応課題（BE）\n価値観の変容が\n求められる課題"

  - type: key_point
    main_text: |-
      自分が獲得したい「成果」や「GOAL」は
      自ら機会をつくり獲得する

  - type: fillable
    name: loop_learning
    circle1: "前提"
    circle2: "行動"
    circle3: "結果"
    badge1: "改革"
    badge2: "改善"
    label1: "シングルループ学習"
    label2: "ダブルループ学習"

  - type: section_divider
    title: "合意の意思決定モデル"

  - type: fillable
    name: compare_3card
    card1_label: "　一致　"
    card1_body: "一人一人の意志と\n言葉が一致している状態"
    card2_label: "　合意　"
    card2_body: "理由と理解を通じて\n納得点に収束する状態"
    card3_label: "　了解　"
    card3_body: "自分の意志は関係なく\n相手の内容を受け取った状態"

  - type: fillable
    name: circle_overlap
    title: "一致・合意・了解の区別"
    main_label: "\n組織\nGOAL"
    sub1: "一致"
    sub2: "合意"
    sub3: "了解"

  - type: rest_time

  - type: notice
    title: "DAY2の告知"
    items:
      - "①  脳のカラクリを理解する"
      - "②  ブレイクスルー領域を特定する"
      - "③  GOAL達成し続ける組織を編成する"
```
