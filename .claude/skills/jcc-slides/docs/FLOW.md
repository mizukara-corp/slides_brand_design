# jcc-slides スキル フロー解説

JCCブランドのPPTXスライドをテキスト入力から自動生成するスキルの処理フローを説明します。

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

    F5 --> EDIT_GEN[edit / patch 実行]
    EDIT_GEN --> OUT
```

---

## ユーザー状態の検出

スキル起動直後に1問のAsk（4択）でユーザーの準備状況を判定します。  
会話の文脈からすでに状態が明らかな場合（テキストが貼られている等）は質問をスキップします。

| 選択肢 | 状態名 | 進むフロー |
|--------|--------|-----------|
| 1. まだ何も決まっていない | braindump | フロー① |
| 2. テーマは決まっているが内容はこれから | theme-only | フロー③ |
| 3. アジェンダはあるが各スライドの内容がまだ | theme+agenda | フロー② |
| 4. 内容（テキスト・箇条書き）がほぼ揃っている | all-ready | フロー④ |

---

## フロー① ブレインダンプ（状態 1：何も決まっていない）

コンテンツがゼロの状態からClaudeが一緒にアジェンダを設計します。  
完了後はフロー②（アジェンダ貼り付け）へ引き継ぎます。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー①：ブレインダンプ

    Claude->>User: ステップA：前提収集（2問同時）<br/>①対象者は？②DAY番号は？
    User->>Claude: 回答

    Claude->>User: ステップB：伝えたいことを自由記述で
    User->>Claude: 自由記述で入力

    Claude->>User: ステップC：3〜5セクション構成の<br/>アジェンダ案を提示
    User->>Claude: ステップD：「このまま進める」<br/>「修正してから進める」「全部作り直す」

    alt 修正してから進める
        User->>Claude: 修正点を自由記述
        Claude->>User: アジェンダ再提案
    end

    Note over User,Claude: アジェンダ確定 → フロー②ステップBへ
```

---

## フロー② アジェンダ貼り付け（状態 3：アジェンダがある）

章立てはあるがスライド内容がまだの状態。アジェンダを受け取り各セクションの内容を収集します。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー②：アジェンダ貼り付け

    Claude->>User: ステップA：アジェンダを貼り付けてください
    User->>Claude: アジェンダ（箇条書き・メモ書き何でもOK）

    Note over Claude: ステップB：セクション数・タイトル・<br/>スライドタイプ候補を自動解析

    loop セクション数だけ繰り返す
        Claude->>User: ステップC：セクションNの内容を教えてください
        User->>Claude: 箇条書き・メモ・文章（空欄ならsectionのみ）
        Note over Claude: 内容の特徴から最適なスライドタイプを判断<br/>（content_list/card2/card3/table/memo/question）
    end

    Claude->>User: ステップD：全セクション構成サマリーを表示
    Note over User,Claude: 確認 → フロー④ 生成パイプラインへ
```

---

## フロー③ Q&Aフロー（状態 2：テーマのみある）

テーマはあるが内容がゼロの状態。セクションごとに1つずつ質問して内容を収集します。

```mermaid
sequenceDiagram
    actor User
    participant Claude

    Note over User,Claude: フロー③：Q&Aフロー

    Claude->>User: フェーズ1：DAY番号 & セクション数（2問同時）
    User->>Claude: 回答

    loop セクション数だけ繰り返す
        Claude->>User: フェーズ2-A：英語タイトル & 日本語タイトル
        User->>Claude: 回答

        Claude->>User: フェーズ2-B：グリッド画像（9タイプ）を表示<br/>使いたいレイアウトを番号で選択
        User->>Claude: 番号で選択（複数可）

        Claude->>User: フェーズ2-C：選んだタイプ別の内容を入力
        User->>Claude: 各フィールドを入力
    end

    Claude->>User: フェーズ3：締めスライドを入れますか？
    User->>Claude: はい / いいえ

    Claude->>User: フェーズ4：スライド構成まとめを表示<br/>「この構成で生成しますか？」最終確認
    User->>Claude: OK

    Note over User,Claude: 確認 → フロー④ 生成パイプラインへ
```

---

## フロー④ 直接生成モード（状態 4：内容が揃っている）＆ 生成パイプライン

すべてのフローの最終段階。YAMLを作成してスクリプトを実行し、QAを行って保存します。

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
    soffice/pdftoppm-->>Claude: slide_qa-*.jpg

    Note over Claude: STEP 4 QAチェック<br/>・テキストが枠内に収まっているか<br/>・table行が切れていないか<br/>・丸数字が文字化けしていないか<br/>・footnote残存テキストがないか

    alt QAで問題あり
        Note over Claude: outline.yaml を修正してSTEP 3から再実行
    end

    Claude->>User: STEP 5：ワークスペースに.pptxを保存
    User-->>Claude: 完了確認
```

---

## フロー⑤ 既存PPTXの編集（mode: edit / patch）

生成済みのPPTXへのスライド追加・置換・削除。

```mermaid
sequenceDiagram
    actor User
    participant Claude
    participant generate.py

    Note over User,Claude: フロー⑤：既存PPTX編集

    User->>Claude: 「既存PPTXの〇〇を変えたい」と要望

    Note over Claude: 対象PPTXのスライド一覧を取得<br/>（インデックスとテキストを確認）

    Claude->>User: スライド一覧を提示<br/>変更箇所のインデックスを確認
    User->>Claude: 変更内容を指定

    alt スライドを追加（mode: edit）
        Note over Claude: mode: edit の YAML を作成<br/>position: end（末尾）or インデックス指定
    else スライドを置換・削除・挿入（mode: patch）
        Note over Claude: mode: patch の YAML を作成<br/>operations: delete / replace / insert
    end

    Claude->>generate.py: patch_outline.yaml + 元PPTX → output.pptx
    generate.py-->>Claude: 編集済み .pptx 生成完了

    Note over Claude: QA → ワークスペースに保存
```

---

## スライドタイプ一覧

スキルが扱えるスライドの種類は大きく3カテゴリに分かれます。

```mermaid
mindmap
  root((スライドタイプ))
    ベーステンプレート
      title\nダーク・中央大タイトル
      section\nダーク・大見出し
      content_list\n箇条書き
      card2_dark / card2_light\n2カラムカード
      card3_dark\n3カラム図解
      table\n2列テーブル
      memo\n本文・引用
      question\n問いかけ
    fixedプリセット
      type: preset\n図解・フレームワーク図\n全固定
    fillableプリセット
      type: fillable\nレイアウト固定\nテキスト変更可
```

---

## YAML オプション早見表

```mermaid
flowchart LR
    YAML[outline.yaml] --> AB[auto-bookend\nday / bookend / closing_en / closing_ja]
    YAML --> BU[bundle\ntype: section_start\n→ section + content_list に展開]
    YAML --> SW[swap\ntype alias + variant\nで見た目を切り替え]

    SW --> EX1["card2 + variant: light → card2_light"]
    SW --> EX2["mvv + variant: gray → fillable mvv_gray"]
    SW --> EX3["be_do_have + variant: v3 → preset be_do_have_v3"]
```

---

## ファイル構成

```
.claude/skills/jcc-slides/
├── SKILL.md                  # スキル本体（フロー分岐・STEP定義）
├── assets/
│   ├── TEMPLATE.pptx         # デザインテンプレート（34枚）
│   └── thumbnails/
│       ├── grid.jpg          # ベース9タイプのグリッド画像
│       ├── fixed_grid.jpg    # fixedプリセットのグリッド画像
│       └── fillable_grid.jpg # fillableプリセットのグリッド画像
├── scripts/
│   └── generate.py           # PPTX生成スクリプト（1,100行超）
├── flows/
│   ├── flow1_braindump.md    # フロー①の詳細手順
│   ├── flow2_agenda.md       # フロー②の詳細手順
│   ├── flow3_qa.md           # フロー③の詳細手順
│   └── flow5_edit.md         # フロー⑤の詳細手順
└── docs/
    ├── yaml-template.md      # 全タイプのYAMLフィールド一覧・サンプル
    ├── preset-fixed.md       # fixedプリセットのname一覧
    ├── preset-fillable.md    # fillableプリセットのname・スロット一覧
    └── slide-library.md      # スライドライブラリ
```
