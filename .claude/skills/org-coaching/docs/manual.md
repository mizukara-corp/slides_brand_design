# org-coaching 使い方マニュアル

組織コーチング（MIZUKARA ブランド）の PPTX スライドを Claude Code で自動生成するスキルです。
`training3.pptx`（DAY1 新ブランド・ベースデザイン）と `training2.pptx`（図解スライド）から作った
TEMPLATE.pptx（20 枚）のデザインをそのまま引き継いで、テキストから完成資料を作ります。

---

## 1. このスキルでできること

- テキスト・アジェンダ・台本などから組織コーチングの **.pptx** を自動生成
- スライドタイプ（タイトル / 瞑想 / Leader's Message / Check-in / Purpose / Agenda / 各種図解…）を **自動選定**
- `result_chain` / `compare_2card` / `compare_3card` / `loop_learning` / `circle_overlap` の **5 種類の図解プリセット** に流し込み
- 著作権表示は実行年（例：© 2026 Mizukara,Inc.）に自動統一

---

## 2. 起動方法

Claude Code のチャットで以下のいずれかをタイプ：

```
/org-coaching
```

または通常の依頼文でも OK：

> 組織コーチングのスライドを作って
> DAY1 の研修資料を作りたい
> 組織 GOAL 合意モデルのスライドにして

スキルが自動的に起動して、最初に **準備状況を 4 択で聞いてきます**。

---

## 3. 4 つの開始パターン（ユーザー状態）

スキル起動後、最初に下記が問われます。

| 番号 | 状態 | あなたの状況 |
|------|------|-------------|
| 1 | **何も決まっていない** | テーマすら決まっていない。一緒に考えたい |
| 2 | **テーマだけ決まっている** | 「組織 GOAL 合意」など漠然としたテーマだけ |
| 3 | **アジェンダがある** | 章立て・見出しはあるが各スライド中身は未定 |
| 4 | **内容が揃っている** | テキスト・箇条書きを貼り付けるだけ |

→ 選んだ番号に応じて Claude が対話の進め方を切り替えます。

> ✅ **ヒント**：最初のメッセージに **スライドのテキスト・台本を直接貼り付ける** と、Claude が状態 4 と判断して即生成モードに入ります（質問はスキップ）。

---

## 4. もっとも速い使い方（状態 4 / 直接生成）

```
/org-coaching

以下の内容で DAY1 のスライドを作って：

タイトル：Organizational Coaching DAY1

オープニング：
- 瞑想
- Leader's Message
- Check-in（今この瞬間、感じていることは何ですか？）

Purpose：経営チームが共通言語でGOALを定義し心から合意した状態を創る

アジェンダ：
1. 結果を作る原理原則
2. 技術課題と適応課題
3. 一致・合意・了解の意思決定モデル

...
```

Claude が内容を解釈して、**最適なスライドタイプを自動選定** → outline.yaml 生成 → ビルド → QA 画像確認 → ワークスペース保存まで一気通貫で進めます。

---

## 5. 利用できるスライドタイプ（全 20 種）

### base デザイン（training3 由来・6 種）

| type | 見た目 | 主な用途 |
|------|--------|---------|
| `title` | オレンジ／ブルー／ホワイトの斜めグラデ + 大型タイトル | DAY ◯ 表紙 |
| `meditation` | ダーク + 中央「瞑 想」（**固定**） | 瞑想セッションの導入 |
| `leader_message` | ダーク + Leader's Message（**固定**） | 経営層からの一言 |
| `check_in` | グラデ + Check in | 冒頭の問いかけ |
| `rest_time` | カラフルグラデ + Rest Time（**固定**） | 休憩 |
| `closing_light` | ライト背景 + メッセージ | 締めのお礼 |

### プレースホルダ編集可（training3 由来・2 種）

| type | 見た目 | 主な用途 |
|------|--------|---------|
| `question` | ダーク・大きな "Q." + 問い文 | 問いかけ、Q&A |
| `purpose` | ダーク・大きな "Purpose 目的" + 段落本文 | 研修目的の宣言 |

### 編集可（training2 由来・4 種）

| type | 見た目 | 主な用途 |
|------|--------|---------|
| `key_point` | ダーク・"重要な観点" バッジ + フレーム枠メッセージ | 中心メッセージ |
| `section_divider` | ダーク・中央配置の章タイトル | チャプター区切り |
| `notice` | ダーク・"DAY ◯ の告知" ヘッダー + 番号付きリスト | 次回告知・宿題 |
| `agenda` | ライト・"Agenda 論点" + 連番リスト（最大 3 項目） | アジェンダ提示 |

### fillable プリセット（training2 由来・5 種）

| name | 見た目 | 主な用途 |
|------|--------|---------|
| `result_chain` | 4 ボックス連鎖（結果 ← 行動 ← 感情 ← 信念） | 結果を作る原理原則 |
| `compare_2card` | 2 カード比較 | DO/BE、技術課題/適応課題 |
| `compare_3card` | 3 カード比較（中央が黄色枠） | 一致／合意／了解 |
| `loop_learning` | 3 円 + 改革／改善バッジ | シングル／ダブルループ学習 |
| `circle_overlap` | 中央大円 + 3 サテライト円 | 組織 GOAL の合意モデル |

> Claude はプリセット選択時にサムネイルグリッド（`assets/thumbnails/grid.jpg`）を表示するので番号で選べます。
> 詳細フィールドは [docs/yaml-template.md](yaml-template.md) を参照。

---

## 6. 上手に使うコツ

### 入力テキストの書き方

- **見出しと本文を区切る**（「スライド 1：〜」「タイトル：〜」など）
- 箇条書きは行頭の `-` `1.` `・` どれでも OK
- 丸数字（①②③）は通常本文では使わない → 半角の `1.` `2.` `3.` に
  - `notice`（DAY 告知）の元テンプレは丸数字を使うのでそこは `①` のままで OK
- 1 スライドに詰め込みすぎない → **箇条書きは 3 項目** が agenda の上限

### スライド枚数の目安

- 半日セッション：15〜25 枚
- 1 日研修：30〜45 枚
- 連続 DAY（DAY1〜DAY3）：1 DAY あたり 20〜30 枚

### デザインのコントロール

- 「Q. のスライド」「Purpose のスライド」と type 名で直接指示できる
- 「2 つを比較したい」 → `compare_2card`、「3 つの段階」 → `compare_3card` を提案
- 「結果に至る連鎖を見せたい」 → `result_chain`、「ループ学習の図」 → `loop_learning`
- 「組織 GOAL の合意モデル」 → `circle_overlap`

---

## 7. 出力の流れ

スキル起動後、Claude は以下を自動で行います：

1. **outline.yaml 作成**（`/tmp/outline.yaml` に書き出し）
2. **generate.py 実行** → `/tmp/output.pptx`
3. **PDF → JPEG 変換で QA**：各スライドを画像化して目視確認
4. **問題があれば修正して再生成**
5. **ワークスペース（プロジェクト直下）に保存**
6. （依頼があれば）`~/Downloads/` にコピー

---

## 8. 既存 PPTX の編集

「DAY1.pptx の 5 枚目を差し替えて」「末尾に Check-out を 1 枚追加して」のような依頼にも対応します。

- **現状**：差分 YAML を `generate.py` で部分生成し、PowerPoint / Keynote で手動マージ、
  もしくは `scripts/merge_redesign.py` で結合
- **将来**：`mode: edit` / `mode: patch` を `generate.py` 本体に取り込む予定

> 詳細手順は [flows/flow5_edit.md](../flows/flow5_edit.md) を参照。

---

## 9. よくある質問・トラブル

| 症状 | 対処 |
|------|------|
| テキストが枠から溢れる | 行数を減らすか短い文に書き換える |
| 丸数字が文字化け | ①②③ を `1.` `2.` `3.` に変換 |
| `compare_2card` のラベルが小さく出る | 1 行目にラベル、2 行目以降を本文として書く（自動でスペーサー段落を補う） |
| `compare_3card` の黄色枠を別カードに付けたい | 元テンプレでは中央(card2)固定。デザイン変更は `make_template.py` で別ソースを抽出 |
| `meditation` / `leader_message` / `rest_time` のテキストを変えたい | 元テンプレが画像背景にベイクしているため不可。再生成は SOURCE 側を編集 |
| `agenda` の連番が全て「1.」になる | 既知の修正済み挙動（startAt 明示でリセット防止）。古い generate.py の場合は最新版に差し替え |
| 生成 PPTX が LibreOffice で開けない | `python -c "from pptx import Presentation; p=Presentation('out.pptx'); p.save('clean.pptx')"` で再保存 |

---

## 10. 関連ドキュメント

| ファイル | 内容 |
|---------|------|
| [SKILL.md](../SKILL.md) | スキル本体（Claude が読む内部仕様） |
| [docs/FLOW.md](FLOW.md) | フロー全体図（mermaid 付き） |
| [docs/yaml-template.md](yaml-template.md) | outline.yaml の全タイプサンプル |
| [docs/sample_outline.yaml](sample_outline.yaml) | 動作確認用デッキ |
| [docs/setup.md](setup.md) | セットアップ手順（依存パッケージ等） |
| [flows/flow1_braindump.md](../flows/flow1_braindump.md) | ブレインダンプフローの詳細 |
| [flows/flow2_agenda.md](../flows/flow2_agenda.md) | アジェンダ貼り付けフロー |
| [flows/flow3_qa.md](../flows/flow3_qa.md) | Q&A フロー |
| [flows/flow5_edit.md](../flows/flow5_edit.md) | 既存 PPTX 編集フロー |

---

## 11. 例：DAY1 講義デッキを作る

```
/org-coaching

DAY1 用に組織コーチング研修のスライドを 20 枚で作って

タイトル：Organizational Coaching DAY1

オープニング：
- 瞑想
- Leader's Message
- Check-in：「今この瞬間、感じていることは何ですか？」
- Purpose：経営チームが共通言語でGOALを定義し心から合意した状態を創る

論点（agenda）：
1. 結果を作る原理原則
2. 技術課題と適応課題
3. 一致・合意・了解の意思決定モデル

第1章「結果を作る原理原則」
- Q: 変わり続ける人と変わらない人の決定的な違いは何ですか？
- 図解: 結果 ← 行動 ← 感情 ← 信念・価値観
- Key Point: 自分が獲得したい成果やGOALは、自ら機会をつくり獲得する

第2章「技術課題と適応課題」
- 図解: DO/BE の2カード対比
- 学習ループの図（前提・行動・結果 + 改革/改善）

第3章「一致・合意・了解」
- 3カード対比（中央は「合意」を黄色強調）
- 組織GOALを中心とした円の重なり図

休憩

DAY2の告知：
① 脳のカラクリを理解する
② ブレイクスルー領域を特定する
③ GOAL達成し続ける組織を編成する

クロージング：本日もありがとうございました
```

→ Claude が自動で type 選定 → 生成 → QA → 保存。完成した PPTX のパスがチャットに表示されます。
