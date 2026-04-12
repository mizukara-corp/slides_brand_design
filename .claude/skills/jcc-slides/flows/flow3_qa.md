# フロー③：Q&A フロー（状態 2）

テーマはあるが内容がゼロの状態。セクション数から 1 つずつ聞いていく。

## フェーズ 1：基本情報

AskUserQuestion で 2 問同時に聞く：

- Q1 `header: "DAY 番号"` — DAY 1 / DAY 2 / DAY 3 / DAY 4 以降
- Q2 `header: "セクション数"` — 3 / 4 / 5 / 6 以上

## フェーズ 2：各セクションの内容収集

フェーズ 1 のセクション数だけ繰り返す。

**ステップ A：セクション見出し**

```
Q1（header: "セクション X"）英語タイトル: Purpose / Agenda / Summary / その他
Q2（header: "日本語タイトル"）日本語で自由入力
```

**ステップ B：レイアウト選択（グリッド画像 1 枚で表示）**

`present_files` でグリッド画像（grid.jpg）を 1 枚だけ表示してからレイアウトを選ばせる。
9 枚バラバラではなく 1 枚にまとめることでトークン消費を最小化する。

```python
# グリッド画像を 1 枚だけ表示（9 タイプすべてが番号付きで確認できる）
# SKILL_DIR は SKILL.md 冒頭で定義済み
present_files([f"{SKILL_DIR}/assets/thumbnails/grid.jpg"])

# 番号で選択させる
AskUserQuestion(
    header="使いたいレイアウトを番号で選んでください（複数可）",
    options=[
        "1. 箇条書き（content_list）",
        "2. 2カラム・ダーク（card2_dark）",
        "3. 2カラム・ライト（card2_light）",
        "4. 3カラム図解（card3_dark）",
        "5. テーブル（table）",
        "6. メモ・引用（memo）",
        "7. 問いかけ（question）",
        "8. セクション見出し（section）",
        "9. タイトル（title）",
    ],
    multiSelect=True
)
```

**ステップ C：タイプ別の内容入力**

| タイプ | 質問パターン |
|--------|------------|
| `content_list` | Q1: ラベル（PURPOSE/AGENDA/SUMMARY/その他）, Q2: サブタイトル, Q3: 本文（1 行 1 項目）, Q4: 注釈 |
| `card2_dark/light` | Q1: タイトル, Q2: 左カード（1 行目=タイトル/2 行目以降=本文）, Q3: 右カード |
| `card3_dark` | Q1: タイトル, Q2: カラム 1（説明/キーワード）, Q3: カラム 2, Q4: カラム 3 |
| `table` | Q1: タイトル, Q2: 行データ（「左\|右」形式で 1 行ずつ） |
| `memo` | Q1: ラベル（Memo/Point/Key Message/その他）, Q2: 本文 |
| `question` | Q1: 問いかけ文, Q2: 補足注記（なし/その他） |

## フェーズ 3：締めスライド確認

```
Q（header: "締めスライド"）: はい・入れる / いいえ・入れない
```

## フェーズ 4：構成確認と生成

1. スライド構成のまとめをテキストで表示する
2. AskUserQuestion で「この構成で生成しますか？」最終確認
3. OK → YAML 生成 → スクリプト実行 → QA → 保存
