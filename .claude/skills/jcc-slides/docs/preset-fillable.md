# fillable プリセット一覧（9 種）

レイアウト・デザインは固定で、指定したスロットのテキストだけを差し替える。

```yaml
- type: fillable
  name: <プリセット名>
  <スロット名>: "テキスト"
```

サムネイル一覧 → `assets/thumbnails/fillable_grid.jpg`（3×3 グリッド）

**スロット省略時の挙動:** 省略されたスロットはテンプレートのデフォルトテキストがそのまま残る。完全に空にしたい場合は `" "` を渡す。

---

### `member_autonomy` — なぜメンバーの主体性が生まれないのか

**外観:** 組織階層（経営層 / マネジメント層 / 現場層）の 3 段図。各層の状態を説明するテキストを差し込む。

| スロット | 説明 |
|---------|------|
| `title` | スライドタイトル |
| `exec_desc` | 経営層の説明文 |
| `mgmt_desc` | マネジメント層の説明文 |
| `field_desc` | 現場層の説明文 |

```yaml
- type: fillable
  name: member_autonomy
  title: "なぜ現場の主体性が失われるのか"
  exec_desc: "短期的な数字を追い\n現場への指示が増える"
  mgmt_desc: "板挟みになり\n伝言ゲームに徹する"
  field_desc: "考える余地がなく\n指示待ちになる"
```

---

### `genjo_wave` — 現状（波形グラフィック）

**外観:** 波形のビジュアル＋下部にメッセージテキスト。

| スロット | 説明 |
|---------|------|
| `bottom_text` | 下部メッセージテキスト（複数行可） |

```yaml
- type: fillable
  name: genjo_wave
  bottom_text: "変化の激しい時代において\n正解は一つではない"
```

---

### `genjo_wave_labeled` — 現状＋ラベル波形

**外観:** `genjo_wave` にオーバーレイラベルを追加したバージョン。

| スロット | 説明 |
|---------|------|
| `overlay_label` | 波形上のラベル（例: `"原則"`） |
| `bottom_text` | 下部メッセージテキスト |

```yaml
- type: fillable
  name: genjo_wave_labeled
  overlay_label: "原則"
  bottom_text: "原則を持つチームは\n変化の中でも軸がブレない"
```

---

### `principle_comparison` — 原理比較（2 列比較表）

**外観:** 左右に対比する 2 列レイアウト。

| スロット | 説明 |
|---------|------|
| `title` | スライドタイトル |
| `left_header` | 左列ヘッダ |
| `right_header` | 右列ヘッダ |
| `left_items` | 左列本文（`\n\n` で視覚的グループ分け可） |
| `right_items` | 右列本文 |
| `bottom_text` | 下部ハイライトテキスト |

```yaml
- type: fillable
  name: principle_comparison
  title: "原則の有無による組織の違い"
  left_header: "原則のない組織"
  right_header: "原則のある組織"
  left_items: "場当たり的な判断\n\n意思決定に時間がかかる\n\n人によって基準がバラバラ"
  right_items: "迷わず判断できる\n\n権限委譲が進む\n\n組織全体で一貫した行動"
  bottom_text: "原則は「判断の基準」であり「行動の軸」である"
```

---

### MVV フレーム（3 色バリアント）

Mission / Vision / Value や Goal など「定義文を入れるフレーム」として使う。

| name | 背景色 | 用途例 |
|------|--------|--------|
| `mvv_orange` | オレンジBOX | Mission / 最重要目標 |
| `mvv_gray` | グレーBOX | Vision / 方向性 |
| `mvv_pink` | ピンクBOX | Value / 行動指針 |

共通スロット: `content`（BOX 内テキスト、複数行可）

```yaml
- type: fillable
  name: mvv_orange
  content: "組織コーチングとは\nコレクティブエフィカシーを\n最大限高めること"
```

swap alias `mvv` を使えば variant だけ変えて色を切り替えられる（`orange` / `gray` / `pink`）。

---

### `fbff_6col` — FB/FF マトリクス 6 列

**外観:** フィードバック/フィードフォワードマトリクス。「なぜ（why）」列なしの 6 列版。

| スロット | 列の内容 |
|---------|----------|
| `problem` | 課題 |
| `fact` | 事実 |
| `what` | 何が問題か |
| `goal` | 目標 |
| `plan` | 計画 |
| `action` | 行動 |

```yaml
- type: fillable
  name: fbff_6col
  problem: "売上が目標の 70%"
  fact: "新規顧客獲得数\n先月比 -30%"
  what: "新規開拓の\nアクション不足"
  goal: "来月末までに\n新規顧客 10 社獲得"
  plan: "テレアポリストを整備する（今週）"
  action: "架電 20 件/日\nを 3 週間継続する"
```

---

### `fbff_7col` — FB/FF マトリクス 7 列

**外観:** `fbff_6col` に「なぜ（why）」列を追加した 7 列版。感情・背景まで掘り下げる場合に。

| スロット | 列の内容 |
|---------|----------|
| `why` | なぜ（感情・背景） |
| `problem` | 課題 |
| `fact` | 事実 |
| `what` | 何が問題か |
| `goal` | 目標 |
| `plan` | 計画 |
| `action` | 行動 |

```yaml
- type: fillable
  name: fbff_7col
  why: "なんで退職したの？\n▼\nお前の指導不足だろ"
  problem: "10 人退職"
  fact: "入社 1 年以内\n9 名退職"
  what: "採用面談時の\n擦り合わせが不十分"
  goal: "1 年以内の\n離職率を 0% にする"
  plan: "採用ファネルをアップデートする（10 月 30 日）"
  action: "書類選考 → 課長の 1 次面談 → 内定承諾"
```
