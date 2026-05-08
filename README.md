# slides_brand_design

ブランド統一されたPowerPoint（.pptx）スライドを **テキスト入力だけ** で自動生成する Claude Code スキル集。

YAML アウトラインや講義テキストを渡すだけで、デザイン・フォント・カラー・ロゴをそのまま引き継いだ完成資料が出来上がります。

---

## 📦 収録スキル

| スキル | ブランド | テンプレート構成 | 用途 |
|---|---|---|---|
| **[jcc-slides](.claude/skills/jcc-slides/)** | JCC（ダークネイビー × ロゴ） | 34枚（ベース9 + fixed 16 + fillable 9） | コーチング講義・DAYxシリーズ |
| **[career-spirit-slides](.claude/skills/career-spirit-slides/)** | キャリスピ（オレンジ × ダーク） | 24枚（base 6 + fixed 13 + fillable 5） | キャリア自己理解講座・セミナー |

両スキルとも：
- スライドタイプ（タイトル / セクション / カード / Q&A / 図解…）を**自動選定**
- 既存PPTXへの**追加・置換・削除**にも対応
- 著作権表示は実行年に**自動統一**（© 2026）

---

## 🚀 クイックスタート

### 1. クローン
```bash
git clone https://github.com/mizukara-corp/slides_brand_design.git
cd slides_brand_design
```

### 2. Python依存をインストール
```bash
pip3 install python-pptx PyYAML lxml Pillow --break-system-packages
```

### 3. Claude Code を起動
```bash
claude
```

### 4. スキルを呼ぶ
Claude Code のチャットで：

```
/jcc-slides
```
または
```
/career-spirit-slides
```

→ スキルが自動的に **ユーザー状態を 4 択で確認** → 対話形式でスライド生成。

> 詳細手順は各スキルのセットアップマニュアルを参照：
> - [jcc-slides セットアップ](.claude/skills/jcc-slides/docs/setup.md)
> - [career-spirit-slides セットアップ](.claude/skills/career-spirit-slides/docs/setup.md)

---

## 💡 使い方の例

最も簡単なパターン — **テキストを貼り付けるだけ**：

> 以下のテキストでJCCスライドを作って：
> タイトル「コーチング基礎講座 DAY1」
> アジェンダ：
>   1. コーチングとは
>   2. 傾聴の3レベル
>   3. 質問のスキル

Claude が自動でスライドタイプを判定し、`output.pptx` を生成します。

---

## 📂 リポジトリ構成

```
slides_brand_design/
├── .gitignore
└── .claude/
    └── skills/
        ├── jcc-slides/                # JCCブランド用スキル
        │   ├── SKILL.md               # スキル本体（Claudeが読む）
        │   ├── docs/
        │   │   ├── setup.md           # セットアップ手順
        │   │   ├── manual.md          # 使い方マニュアル
        │   │   ├── FLOW.md            # 生成フロー
        │   │   ├── yaml-template.md   # YAML仕様
        │   │   └── slide-library.md   # スライド種類カタログ
        │   ├── scripts/               # PPTX 生成スクリプト
        │   └── assets/
        │       └── TEMPLATE.pptx      # デザイン雛形
        └── career-spirit-slides/      # キャリスピブランド用スキル
            ├── SKILL.md
            ├── docs/
            │   ├── setup.md
            │   ├── manual.md
            │   └── yaml-template.md
            ├── scripts/
            └── assets/
                └── TEMPLATE.pptx
```

---

## 🔧 必要環境

| 項目 | バージョン |
|---|---|
| OS | macOS / Linux / Windows (WSL2) |
| Python | 3.9 以上 |
| Claude Code | 最新版 |
| Git | 2.x 以上 |

---

## 📚 ドキュメント

各スキルの詳細は `.claude/skills/<skill>/docs/` 配下に整備しています：

- **setup.md** … 第三者がクローンしてから実行するまでの手順
- **manual.md** … エンドユーザー向け使い方ガイド
- **yaml-template.md** … YAML アウトラインの仕様
- **slide-library.md** … 利用可能なスライドタイプ一覧（jcc-slides のみ）
- **FLOW.md** … 生成フロー図（jcc-slides のみ）

---

## ⚙️ 仕組み（概要）

1. ユーザーがテキスト or YAML をスキルに渡す
2. Claude がスライドタイプを判定し YAML アウトラインを構築
3. `scripts/generate.py` が `assets/TEMPLATE.pptx` を読み込み、各スライドを複製してテキスト注入
4. `output.pptx` として保存（PowerPoint / Keynote / Google Slides で開ける）

テンプレートを差し替えれば**任意のブランドに展開可能**な設計です。

---

## 📝 ライセンス

社内利用を想定したリポジトリです。テンプレートデザインの著作権は各ブランドオーナーに帰属します。
