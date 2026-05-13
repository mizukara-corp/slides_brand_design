# org-coaching スキル フロー解説

組織コーチング（MIZUKARA ブランド）の PPTX スライドをテキスト入力から自動生成するスキルの処理フローを説明します。

---

## 全体フロー概要

```mermaid
flowchart TD
    START([スキル起動]) --> DETECT{ユーザー状態の検出\n4択で確認}

    DETECT -->|1. 何も決まっていない| F1[フロー① ブレインダンプ]
    DETECT -->|2. テーマのみある| F3[フロー③ Q&Aフロー]
    DETECT -->|3. アジェンダがある| F2[フロー② アジェンダ貼り付け]
    DETECT -->|4. 内容が揃っている| F4[フロー④ 直接生成モード]
    DETECT -->|既存PPTXを編集したい| F5[フロー⑤ 既存PPTX編集]

    F1 --> |アジェンダ確定後| F2
    F3 --> |構成確定後| GEN
    F2 --> |内容収集後| GEN
    F4 --> GEN

    GEN[生成パイプライン\nSTEP 1〜5]
    GEN --> OUT([.pptx 完成・保存])

    F5 --> EDIT_GEN[差分 YAML → 部分生成 → 手動マージ]
    EDIT_GEN --> OUT
```

---

## ユーザー状態の検出

スキル起動直後に 1 問の Ask（4 択）でユーザーの準備状況を判定します。
会話の文脈からすでに状態が明らかな場合（テキストが貼られている等）は質問をスキップします。

| 選択肢 | 状態名 | 進むフロー |
|--------|--------|-----------|
| 1. まだ何も決まっていない | braindump | フロー① |
| 2. テーマは決まっているが内容はこれから | theme-only | フロー③ |
| 3. アジェンダはあるが各スライドの内容がまだ | theme+agenda | フロー② |
| 4. 内容（テキスト・箇条書き）がほぼ揃っている | all-ready | フロー④ |

---

## フロー① ブレインダンプ（状態 1：何も決まっていない）

コンテンツがゼロの状態から Claude が一緒にアジェンダを設計します。
完了後はフロー②（アジェンダ貼り付け）へ引き継ぎます。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー①：ブレインダンプ

    Claude->>User: ステップA：前提収集（2問同時）<br/>①対象者は？（経営層／リーダー／メンバー／1on1）<br/>②DAY番号は？
    User->>Claude: 回答

    Claude->>User: ステップB：受け取ってほしいことを自由記述で
    User->>Claude: 自由記述で入力

    Claude->>User: ステップC：3〜5セクションのアジェンダ案を提示<br/>(Purpose → 認知 → 行動 → 合意 → 次のアクション)
    User->>Claude: ステップD：「このまま進める」<br/>「修正してから進める」「全部作り直す」

    alt 修正してから進める
        User->>Claude: 修正点を自由記述
        Claude->>User: アジェンダ再提案
    end

    Note over User,Claude: アジェンダ確定 → フロー②ステップBへ
```

---

## フロー② アジェンダ貼り付け（状態 3：アジェンダがある）

章立てはあるがスライド内容がまだの状態。アジェンダを受け取り、
オープニング（title / meditation / leader_message / check_in / purpose）の構成と
各セクションの内容を収集します。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー②：アジェンダ貼り付け

    Claude->>User: ステップA：アジェンダを貼り付けてください
    User->>Claude: アジェンダ（箇条書き・メモ書き何でもOK）

    Note over Claude: ステップB：セクション数・タイトル・<br/>スライドタイプ候補を自動解析

    Claude->>User: ステップC：冒頭スライド構成を選ぶ<br/>(title / meditation / leader_message / check_in / purpose / agenda)
    User->>Claude: 複数選択（check_in/purpose選択時は本文を続けて入力）

    loop セクション数だけ繰り返す
        Claude->>User: ステップD：セクションNの内容を教えてください
        User->>Claude: 箇条書き・メモ・文章（空欄ならsection_dividerのみ）
        Note over Claude: 内容の特徴から最適なスライドタイプを判断<br/>(result_chain / compare_2card / compare_3card /<br/>loop_learning / circle_overlap / key_point / question…)
    end

    Claude->>User: ステップE：クロージング構成を選ぶ<br/>(closing_light / notice / 両方 / なし)
    User->>Claude: 回答

    Claude->>User: ステップF：全構成サマリーを表示
    Note over User,Claude: 確認 → 生成パイプラインへ
```

---

## フロー③ Q&Aフロー（状態 2：テーマのみある）

テーマはあるが内容がゼロの状態。セクションごとに 1 つずつ質問して内容を収集します。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー③：Q&Aフロー

    Claude->>User: フェーズ1：DAY番号 & セクション数（2問同時）
    User->>Claude: 回答

    Claude->>User: フェーズ2：冒頭スライド選び<br/>(title / meditation / leader_message / check_in / purpose / agenda)
    User->>Claude: 複数選択 → 必要な本文を続けて入力

    loop セクション数だけ繰り返す
        Claude->>User: フェーズ3-A：セクション題目を入力
        User->>Claude: 回答

        Claude->>User: フェーズ3-B：grid.jpg を表示<br/>使いたいレイアウトを番号で選択
        User->>Claude: 番号で選択（複数可）

        Claude->>User: フェーズ3-C：選んだタイプ別の内容を入力
        User->>Claude: 各フィールドを入力
    end

    Claude->>User: フェーズ4：クロージングは？<br/>(closing_light / notice / 両方 / なし)
    User->>Claude: 回答

    Claude->>User: フェーズ5：構成サマリーを表示「この構成で生成しますか？」
    User->>Claude: OK

    Note over User,Claude: 確認 → 生成パイプラインへ
```

---

## フロー④ 直接生成モード（状態 4：内容が揃っている）＆ 生成パイプライン

すべてのフローの最終段階。YAML を作成してスクリプトを実行し、QA を行って保存します。

```mermaid
sequenceDiagram
    actor User
    participant Claude
    participant generate.py
    participant soffice/pdftoppm

    Note over User,Claude: 生成パイプライン（STEP 1〜5）

    Note over Claude: STEP 1：アウトライン設計<br/>コンテンツを各スライドタイプにマッピング

    Note over Claude: STEP 2：/tmp/outline.yaml を作成<br/>（必要なら docs/yaml-template.md を参照）

    Claude->>generate.py: STEP 3：generate.py を実行<br/>outline.yaml + TEMPLATE.pptx → output.pptx
    generate.py-->>Claude: /tmp/output.pptx 生成完了

    Claude->>soffice/pdftoppm: STEP 4：PDF変換 → JPEG変換（QA用画像生成）
    soffice/pdftoppm-->>Claude: /tmp/qa/s-*.jpg

    Note over Claude: STEP 4 QAチェック<br/>・テキストが枠内に収まっているか<br/>・compare_2card 1行目がラベルか<br/>・compare_3card で黄色が中央(card2)に出ているか<br/>・丸数字が文字化けしていないか<br/>・agenda の連番(1.2.3) と highlight が正しいか

    alt QAで問題あり
        Note over Claude: outline.yaml を修正してSTEP 3から再実行
    end

    Claude->>User: STEP 5：ワークスペースに.pptxを保存
    User-->>Claude: 完了確認
```

---

## フロー⑤ 既存 PPTX の編集

生成済みの PPTX へのスライド追加・置換・削除。
（現状の `generate.py` は edit/patch モード未対応のため、差分 PPTX を作って手動マージする運用）

```mermaid
sequenceDiagram
    actor User
    participant Claude
    participant generate.py
    participant merge_redesign.py

    Note over User,Claude: フロー⑤：既存PPTX編集

    User->>Claude: 「既存PPTXの〇〇を変えたい」と要望

    Note over Claude: 元PPTXのスライド一覧を取得<br/>（インデックスとテキストを確認）

    Claude->>User: スライド一覧を提示<br/>変更箇所のインデックスを確認
    User->>Claude: 変更内容を指定

    Note over Claude: 差分用 YAML を作成（bookend: false）

    Claude->>generate.py: 差分 YAML → /tmp/patch_output.pptx
    generate.py-->>Claude: 差分 PPTX 生成完了

    alt 手動マージ
        Note over User: PowerPoint/Keynote で<br/>該当スライドをコピー＆貼り付け
    else スクリプトマージ
        Claude->>merge_redesign.py: 元PPTX + 差分PPTX + 挿入位置
        merge_redesign.py-->>Claude: /tmp/merged.pptx
    end

    Note over Claude: QA → ワークスペースに保存
```

---

## スライドタイプ一覧

スキルが扱えるスライドの種類は大きく 3 カテゴリに分かれます。

```mermaid
mindmap
  root((スライドタイプ\n全20枚))
    base デザイン\n(training3 由来)
      title\nDAY番号付き表紙
      meditation\n瞑想（固定）
      leader_message\nリーダーズメッセージ（固定）
      check_in\n問いかけで始める
      rest_time\n休憩（固定）
      closing_light\nライト背景クロージング
    プレースホルダ編集可\n(training3 由来)
      question\nQ. + 本文
      purpose\nPurpose 目的 + 本文
    編集可\n(training2 由来)
      key_point\n重要な観点フレーム
      section_divider\n章タイトル
      notice\n次回告知
      agenda\n論点リスト + highlight
    fillable プリセット\n(training2 由来)
      result_chain\n結果を作る原理原則
      compare_2card\nDO/BE 対比
      compare_3card\n一致/合意/了解
      loop_learning\nシングル/ダブルループ
      circle_overlap\n中央円+3サテライト
```

---

## YAML オプション早見表

```mermaid
flowchart LR
    YAML[outline.yaml] --> AB[auto-bookend\nday / title_en / title_ja\n/ closing_message / bookend]
    YAML --> AG[agenda\nitems + highlight 0〜3]
    YAML --> FI[fillable\nname + 各スロット]

    AB --> EX1["day: 'DAY 1 -' → 先頭に title"]
    AB --> EX2["closing_message: '...' → 末尾に closing_light"]
    AG --> EX3["highlight: 2 → item2 を強調"]
    FI --> EX4["name: result_chain → box1〜4 + title"]
```

---

## ファイル構成

```
.claude/skills/org-coaching/
├── SKILL.md                  # スキル本体（フロー分岐・STEP定義）
├── assets/
│   ├── TEMPLATE.pptx         # デザインテンプレート（20枚）
│   └── thumbnails/
│       ├── grid.jpg          # 全20タイプのグリッド画像
│       └── {type}.jpg        # 個別サムネ
├── scripts/
│   ├── generate.py           # PPTX生成スクリプト
│   ├── make_template.py      # training3 + training2 → TEMPLATE.pptx
│   ├── make_grid.py          # サムネ生成
│   └── merge_redesign.py     # 既存PPTXへのマージ補助
├── flows/
│   ├── flow1_braindump.md    # フロー①の詳細手順
│   ├── flow2_agenda.md       # フロー②の詳細手順
│   ├── flow3_qa.md           # フロー③の詳細手順
│   └── flow5_edit.md         # フロー⑤の詳細手順
└── docs/
    ├── FLOW.md               # 本ドキュメント（フロー全体図）
    ├── manual.md             # エンドユーザー向け使い方マニュアル
    ├── yaml-template.md      # 全タイプのYAMLフィールド一覧・サンプル
    ├── sample_outline.yaml   # 動作確認用デッキ
    └── setup.md              # セットアップ手順
```
