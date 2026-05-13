# フロー③：Q&A フロー（状態 2）

テーマはあるが内容がゼロの状態。
セクション数から 1 つずつ、組織コーチング向け定型スライドへ落としていく。

## フェーズ 1：基本情報（同時 2 問）

```python
AskUserQuestion(header="DAY 番号", options=["DAY 1", "DAY 2", "DAY 3", "DAY 4 以降"])
AskUserQuestion(header="セクション数", options=["3 セクション", "4 セクション", "5 セクション", "6 以上"])
```

## フェーズ 2：オープニング・スライド選び

```python
AskUserQuestion(
    header="冒頭に入れたいスライドは？（複数選択可）",
    options=[
        "1. タイトル（DAY◯ / 講座名）",
        "2. 瞑想（meditation）",
        "3. リーダーズメッセージ",
        "4. Check-in（参加者への問い）",
        "5. Purpose（本研修の目的）",
        "6. Agenda（論点リスト）",
    ],
    multiSelect=True
)
```

選ばれた項目に応じて：

| 選択 | 続けて聞く内容 |
|------|---------------|
| Check-in | 「最初の問いかけ文を 1 行で」 freeText |
| Purpose | 「研修の目的を 2〜3 行で」 freeText |
| Agenda | 「論点を 1 行 1 項目で（最大 3 項目推奨）」 freeText |

## フェーズ 3：各セクションの中身

フェーズ 1 のセクション数だけ繰り返す。

**ステップ A：セクション題目**

```python
AskUserQuestion(
    header=f"セクション {N} の題目（日本語）",
    freeText=True,
    placeholder="例：結果を作る原理原則"
)
```

**ステップ B：使うレイアウト選び**

`present_files` でグリッド画像を 1 枚表示してから番号で選ばせる。

```python
present_files([f"{SKILL_DIR}/assets/thumbnails/grid.jpg"])

AskUserQuestion(
    header="使いたいレイアウトを選んでください（複数可）",
    options=[
        "1. Q. 問いかけ（question）",
        "2. 重要な観点フレーム（key_point）",
        "3. 章タイトル（section_divider）",
        "4. 結果を作る原理原則（result_chain）",
        "5. 2カード対比 DO/BE（compare_2card）",
        "6. 3カード対比 一致/合意/了解（compare_3card）",
        "7. シングル/ダブルループ学習（loop_learning）",
        "8. 中央円+3サテライト（circle_overlap）",
        "9. 次回告知（notice）",
        "10. 休憩（rest_time）",
    ],
    multiSelect=True
)
```

**ステップ C：レイアウト別の質問パターン**

| レイアウト | 質問 |
|-----------|------|
| `question` | Q1: 問いかけ文（複数行可） |
| `key_point` | Q1: フレーム内に入れるメッセージ（1〜2 行推奨） |
| `section_divider` | Q1: 章タイトル（1 行） |
| `result_chain` | Q1: 図のタイトル / Q2: box1（結果側）→ box4（原因側）4 つを `\|` 区切り or 1 つずつ |
| `compare_2card` | Q1: 図のタイトル / Q2: card1（1行目=ラベル, 2行目以降=本文）/ Q3: card2 |
| `compare_3card` | Q1: card1 label+body / Q2: card2 label+body（中央・黄色）/ Q3: card3 label+body |
| `loop_learning` | Q1: circle1〜3 + badge1〜2 + label1〜2（順に） |
| `circle_overlap` | Q1: タイトル / Q2: 中央円（改行可）/ Q3: サテライト1〜3 |
| `notice` | Q1: ヘッダーラベル / Q2: 番号付きリスト（1 行 1 項目）|
| `rest_time` | 入力なし（デザイン固定） |

## フェーズ 4：クロージング

```python
AskUserQuestion(
    header="末尾の構成は？",
    options=[
        "1. クロージング（ライト・お礼）",
        "2. 次回告知 notice",
        "3. 両方",
        "4. なし",
    ]
)
```

選ばれた項目に応じて：
- クロージング → 「最後のメッセージ（1 行）」を freeText
- notice → 「告知のヘッダー」と「項目（1 行 1 項目）」を freeText

## フェーズ 5：構成確認と生成

1. スライド構成のサマリーをテキストで表示
2. AskUserQuestion で「この構成で生成しますか？」最終確認
3. OK → YAML 生成 → `generate.py` 実行 → QA → 保存
