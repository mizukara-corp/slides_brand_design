# career-spirit-slides セットアップマニュアル

GitHubからクローンしてClaude Codeでスキルを実行できるようになるまでの手順です。
所要時間：**約10分**（Claude Code・Pythonがインストール済みなら3分）

---

## 0. 前提条件

| 項目 | 必要バージョン | 確認コマンド |
|---|---|---|
| OS | macOS / Linux / Windows (WSL2) | — |
| Python | 3.9以上 | `python3 --version` |
| Git | 2.x以上 | `git --version` |
| Claude Code | 最新版 | `claude --version` |

> ⚠️ Windows ネイティブ（PowerShell/cmd）は未検証です。**WSL2 (Ubuntu) の使用を推奨**します。

---

## 1. Claude Code をインストール（未導入の場合のみ）

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

インストール後、初回ログイン：

```bash
claude
```

ブラウザでAnthropicアカウント認証を済ませてください。

> 詳細は公式ドキュメント: https://docs.claude.com/claude-code

---

## 2. リポジトリをクローン

任意のディレクトリで：

```bash
git clone https://github.com/mizukara-corp/slides_brand_design.git
cd slides_brand_design
```

---

## 3. Python依存パッケージをインストール

このスキルは以下の Python ライブラリを使います：

| パッケージ | 用途 |
|---|---|
| `python-pptx` | PPTX ファイルの生成・編集 |
| `PyYAML` | YAML アウトラインの読み込み |
| `lxml` | XML 操作（python-pptx の依存） |
| `Pillow` | サムネイル・画像処理 |

**まとめてインストール：**

```bash
pip3 install python-pptx PyYAML lxml Pillow --break-system-packages
```

> `--break-system-packages` は macOS / Ubuntu の system Python で必要。
> **venv 派の場合：**
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate
> pip install python-pptx PyYAML lxml Pillow
> ```

**インストール確認：**

```bash
python3 -c "import pptx, yaml, lxml, PIL; print('OK')"
```

`OK` と表示されれば成功。

---

## 4. Claude Code でスキルを認識させる

このリポジトリは `.claude/skills/career-spirit-slides/` にスキル定義が入っているため、
**プロジェクトルート（`slides_brand_design/`）から `claude` を起動するだけ**でスキルが自動的にロードされます。

```bash
cd slides_brand_design   # プロジェクトルートに居ること
claude
```

Claude Code 起動後、スキルが認識されたか確認：

```
/help
```

スキル一覧に `career-spirit-slides` が出ていればOK。

---

## 5. 動作確認（Hello World）

Claude Code のチャットで：

```
/career-spirit-slides
```

または自然文で：

> キャリスピのスライドを作って

スキルが起動し、**4つの開始パターンの選択肢**が表示されれば成功です。

最小サンプルで生成テストしたい場合は以下を貼り付け：

> 以下のテキストでキャリスピスライドを作って：
> タイトル「自己理解ワークショップ」
> アジェンダ：1. 価値観の棚卸し  2. 強みの発見  3. キャリアビジョン

→ `output.pptx`（または同等のファイル名）が生成されれば動作OK。

---

## 6. ディレクトリ構造（参考）

```
slides_brand_design/
├── .claude/
│   └── skills/
│       └── career-spirit-slides/
│           ├── SKILL.md              # スキル本体（Claude が読む）
│           ├── docs/
│           │   ├── manual.md         # 使い方マニュアル
│           │   ├── yaml-template.md  # YAML 仕様
│           │   └── setup.md          # 本ファイル
│           ├── scripts/
│           │   ├── generate.py       # PPTX 生成スクリプト
│           │   └── make_template.py  # TEMPLATE.pptx 再生成用
│           └── assets/
│               ├── TEMPLATE.pptx     # デザイン雛形（必須）
│               ├── SOURCE.pptx       # 元デッキ
│               └── thumbnails/       # スライドサムネ
└── .gitignore
```

> `assets/TEMPLATE.pptx` は **必ず存在する必要があります**（生成スクリプトの土台）。
> 紛失した場合は `python3 scripts/make_template.py` で再構築できます。

---

## 7. よくあるトラブル

### `command not found: claude`
Claude Code がインストールされていないか、PATH が通っていません。
→ 手順 1 を再実行、またはターミナルを再起動。

### `ModuleNotFoundError: No module named 'pptx'`
依存パッケージが入っていません。
→ 手順 3 を再実行。venv を使っている場合は `source .venv/bin/activate` を忘れずに。

### スキルが `/help` 一覧に出てこない
- プロジェクトルート（`.claude/` のある階層）から `claude` を起動していますか？
- `.claude/skills/career-spirit-slides/SKILL.md` が存在しますか？
  ```bash
  ls .claude/skills/career-spirit-slides/SKILL.md
  ```

### `TEMPLATE.pptx not found`
`assets/TEMPLATE.pptx` が欠落しています。
→ 再生成：
```bash
python3 .claude/skills/career-spirit-slides/scripts/make_template.py
```

### 生成された pptx が文字化けする
日本語フォントが OS にないと PowerPoint で代替表示されます。
→ macOS は標準で問題なし。Linux は `fonts-noto-cjk` を導入：
```bash
sudo apt install fonts-noto-cjk
```

---

## 8. 次のステップ

- 使い方の詳細 → [manual.md](manual.md)
- YAML 仕様 → [yaml-template.md](yaml-template.md)
- スキル本体の挙動 → `../SKILL.md`

セットアップ完了です。`claude` を起動して `/career-spirit-slides` を試してください。
