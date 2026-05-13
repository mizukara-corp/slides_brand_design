# フロー②：アジェンダ貼り付け（状態 3）

章立てはあるが各スライドの中身がまだの状態。
アジェンダを受け取って各セクションの内容を収集する。

## ステップ A：アジェンダを受け取る

```python
AskUserQuestion(
    header="アジェンダを貼り付けてください（箇条書き・章立て・メモで OK）",
    freeText=True,
    placeholder="例：\n1. Purpose / 目的\n2. 結果を作る原理原則\n3. 技術課題と適応課題\n4. 合意のモデル"
)
```

## ステップ B：Claude がアジェンダを解析

受け取ったアジェンダを解析して以下を確定する：

- セクション数とタイトル
- 各セクションで使いたい組織コーチング系スライドタイプの候補

確認なしに次へ進む。

## ステップ C：オープニング構成を確認

組織コーチング研修は冒頭が決まったフォーマットになりがち。
**title / meditation / leader_message / check_in** の挿入をまとめて確認する。

```python
AskUserQuestion(
    header="冒頭に入れるスライドを選んでください（複数選択可）",
    options=[
        "1. タイトル（DAY◯ / 講座名）",
        "2. 瞑想（瞑想セッションの導入）",
        "3. リーダーズメッセージ（経営層からの一言）",
        "4. Check-in（参加者への問いかけ）",
        "5. Purpose（本研修の目的）",
        "6. Agenda（論点リスト）",
    ],
    multiSelect=True
)
```

選ばれたものに応じて：
- Check-in 選択時 → 「最初の問いかけは？」を freeText で 1 問
- Purpose 選択時 → 「研修の目的を 2〜3 行で」を freeText で 1 問
- Agenda 選択時 → ステップ A のアジェンダ項目をそのまま反映

## ステップ D：各セクションの内容収集

セクション数だけ繰り返す。

```python
# セクション N の内容収集
AskUserQuestion(
    header=f"セクション {N}「{title}」の内容（自由記述）",
    freeText=True,
    placeholder="箇条書き・メモ・文章 何でも OK。空白なら section_divider のみ生成します。"
)
```

入力された内容から Claude が適切なスライドタイプを判断して YAML に変換する。

**スライドタイプの自動判断ルール：**

| 内容の特徴 | 使うタイプ |
|-----------|-----------|
| 「結果 ← 行動 ← 感情 ← 信念」のような連鎖 | `fillable: result_chain` |
| 2 つの概念の対比（DO/BE、技術/適応 等） | `fillable: compare_2card` |
| 3 つの段階（一致/合意/了解、感情/思考/行動 等） | `fillable: compare_3card` |
| 学習ループ・PDCA・前提-行動-結果 | `fillable: loop_learning` |
| 中心概念 + 3 サテライト | `fillable: circle_overlap` |
| 中心メッセージ・キーフレーズ | `key_point` |
| 問いかけ・ワーク | `question` |
| 次回告知・宿題リスト | `notice` |
| 章間休憩 | `rest_time` |
| 章間題目 | `section_divider` |
| 何も入力なし | `section_divider` のみ |

## ステップ E：クロージングを確認

```python
AskUserQuestion(
    header="末尾に入れるスライドを選んでください",
    options=[
        "1. クロージング（ライト背景・お礼）",
        "2. 次回告知 notice（次の DAY 内容）",
        "3. 両方",
        "4. 何もなし",
    ]
)
```

## ステップ F：構成確認と生成

1. 全セクションの構成サマリーをテキストで表示
2. 確認 → YAML 生成 → `generate.py` 実行 → QA → 保存
