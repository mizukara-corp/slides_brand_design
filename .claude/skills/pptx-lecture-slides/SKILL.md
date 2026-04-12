---
name: pptx-lecture-slides
description: >
  講義・ハンズオン・勉強会のテキスト内容から、統一デザインのPowerPoint（.pptx）スライドを自動生成するスキル。
  ユーザーが「スライドを作って」「pptxにまとめて」「講義資料を作成して」「セットアップ会のスライドにして」
  などと言ったとき、または講義テキスト・台本・アウトラインを渡してスライド化を依頼してきたときに必ず使う。
  テキストさえあればスライドが完成するよう、コード生成からビルド・QAまで一気通貫で行う。
---

# pptx-lecture-slides スキル

非エンジニア向け講義・ハンズオン資料を、パープル×ダーク基調の統一デザインで
**テキスト入力 → PPTX 自動生成** するスキル。

## このスキルが提供するもの

1. **デザインシステム**（カラー・ヘルパー関数）が `scripts/base_helpers.js` にバンドル済み
2. **スライド構成テンプレート**（概念解説→なぜやるか→事例→ライブデモ→ハンズオン）
3. **ビルドパイプライン**（Node.js → LibreOffice PDF → pdftoppm で画像化 → 目視 QA）

---

## 作業の流れ

### STEP 1: 講義内容を理解する

ユーザーから渡された内容（テキスト・台本・箇条書き・ファイル）を読み、以下を把握する：

| 項目 | 内容 |
|------|------|
| **タイトル** | 講義・イベント名 |
| **サブタイトル** | 短い説明文 |
| **対象者・所要時間** | タイトルスライドに掲載 |
| **アジェンダ** | セクション名と概要（3〜5項目） |
| **GOALの3つの柱** | 講義で達成する3つのこと |
| **TO BE（達成チェックリスト）** | 講義終了後に「できている」状態のリスト |
| **各セクション** | 概念スライド群 or ハンズオン手順 |
| **完了チェックリスト** | 参加者が自己確認するリスト |
| **次回への導線・宿題** | 手順リスト（最後の行をハイライト） |

不明な項目があれば、作業開始前にユーザーに確認する（ただし作業できる範囲は先に進めてよい）。

### STEP 2: スライド構成を決める

`references/slide_structure.md` を読み、講義内容に合わせてスライド順を設計する。
標準テンプレートを基に、セクション数・ハンズオン手順の枚数を決める。

**概念セクション**（例：「〇〇とは？」）に必要なスライドセット:
```
sectionSlide → 概念の解説（図解） → なぜ必要なのか？ → 利点・欠点 → 事例紹介 → ライブデモ
→ handsOnIntro → stepSlides × N
```

**ハンズオンセクション**（例：「〇〇をインストールする」）:
```
全体像スライド（必要なら） → sectionSlide → なぜやるか → handsOnIntro → stepSlides × N
（サブ作業が複数あれば handsOnIntro → stepSlides を繰り返す）
```

### STEP 3: JS スクリプトを生成する

以下のテンプレートに従い、`create_slides_<topic>.js` を `/sessions/` 以下（作業ディレクトリ）に生成する。

```javascript
// create_slides_<topic>.js
const { pres, C, S, sectionSlide, contentHeader,
        threeCards, handsOnIntro, stepSlides } = require('<スキルpath>/scripts/base_helpers');

pres.title = '<講義タイトル>';

// ============================================================
// SLIDE 1: タイトル
// ============================================================
{
  const sl = pres.addSlide();
  sl.background = { color: C.dark };
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.07, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addShape(pres.shapes.OVAL, { x: 6.5, y: -1.0, w: 5.5, h: 5.5, fill: { color: C.purple, transparency: 88 }, line: { color: C.purple, transparency: 88 } });
  sl.addShape(pres.shapes.OVAL, { x: 7.8, y: 2.5,  w: 3.0, h: 3.0, fill: { color: C.purple, transparency: 80 }, line: { color: C.purple, transparency: 80 } });
  sl.addText('<シリーズラベル>', { x: 0.7, y: 0.6, w: 6, h: 0.4, fontSize: 12, color: C.purpleLight, fontFace: 'Calibri' });
  sl.addText([{ text: '<タイトル行1>', options: { breakLine: true } }, { text: '<タイトル行2>' }], {
    x: 0.7, y: 1.1, w: 8.5, h: 2.1, fontSize: 46, color: C.white, bold: true, fontFace: 'Calibri'
  });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 3.3, w: 1.6, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addText('<サブタイトル>', { x: 0.7, y: 3.5, w: 8.5, h: 0.5, fontSize: 16, color: C.purpleLight, fontFace: 'Calibri' });
  sl.addText('<対象・所要時間テキスト>', { x: 0.7, y: 4.9, w: 8.5, h: 0.4, fontSize: 11, color: C.textMuted, fontFace: 'Calibri' });
}

// SLIDE 2: アジェンダ
// SLIDE 3: 本講義のGOAL
// SLIDE 4: 本講義のTO BE
// ...（以下、全スライド）...

pres.writeFile({ fileName: '/sessions/<作業dir>/<出力ファイル名>.pptx' })
  .then(() => console.log('Done'))
  .catch(err => { console.error(err); process.exit(1); });
```

**コーディング規則（守らないとビルドが壊れる）：**

- シャドウは `shadow: S()` で毎回生成（使い回し禁止）
- カラーは必ず6桁 RGB（8桁 = エラー）。透明度は `transparency: 数値(0-100)` で別指定
- 絵文字（U+1F000以上）は使わない → `✓` `✗` `→` `↓` `★` のみ使用可
- テキスト内改行は `[{ text:'...', options:{ breakLine:true }}, ...]` の配列形式
- 長いタイトルは fontSize を下げるか文字数を減らす（26pt で 20文字超は折り返し注意）

### STEP 4: ビルドして QA する

```bash
# 1. PPTX 生成
node create_slides_<topic>.js

# 2. PDF 変換（LibreOffice）
python /sessions/<workdir>/mnt/.claude/skills/pptx/scripts/office/soffice.py \
  --headless --convert-to pdf "<出力ファイル>.pptx" --outdir /sessions/<workdir>/

# 3. スライド画像化
rm -f slide-*.jpg
pdftoppm -jpeg -r 110 "<出力ファイル>.pdf" slide

# 4. スライド枚数確認
ls slide-*.jpg | wc -l
```

**ビルドエラーが出た場合：**
- `is not a valid scheme color` → 8桁カラーを使っている。`transparency` に分離する
- `Cannot read properties of undefined` → `require` パスを確認、`pres` が正しく export されているか確認

### STEP 5: スライドを目視確認する

`Read` ツールで重要スライドの `.jpg` 画像を確認する。最低限チェックすべきスライド：

1. タイトル（#1）
2. アジェンダ（#2）
3. 概念の解説スライド（図解）
4. 事例紹介スライド（テキスト溢れがないか）
5. 一緒にやってみよう！ イントロ（緑デザイン）
6. stepSlides のステップ 1枚目と最終枚
7. 最後のスライド（次回への導線）

**よくある問題と修正：**

| 問題 | 修正方法 |
|------|---------|
| テキストが枠外にはみ出る | fontSize を下げる、テキストを短縮、h を増やす |
| 「?」ボックスが表示される | 絵文字を使っている → テキストラベルに置換 |
| 事例カードの After テキストが見切れる | カード高さを増やすか fontSize を下げる |
| stepSlides で余白が大きい/小さい | stepH・gap を手動調整（5ステップ: 0.72/0.06） |

問題があれば JS を修正して再ビルド → 再確認を繰り返す。

### STEP 6: ワークスペースに保存する

```bash
cp /sessions/<workdir>/<出力ファイル>.pptx "/sessions/<workdir>/mnt/<ユーザーフォルダ>/<出力ファイル>.pptx"
```

ユーザーにリンクを提供する:
```
[スライドを開く](computer:///sessions/<workdir>/mnt/<ユーザーフォルダ>/<出力ファイル>.pptx)
```

---

## スライドタイプ別コードサンプル

詳細は `references/slide_structure.md` を参照。よく使うパターンを以下に示す。

### アジェンダ行
```javascript
const agendaItems = [
  { num: '01', title: '本講義のGOAL / TO BE', desc: '今回の講義で獲得できることを確認' },
  { num: '02', title: '〇〇とは？', desc: '概念理解からライブデモまで' },
  // ...
];
agendaItems.forEach((item, i) => {
  const y = 1.3 + i * 0.83;
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 9.4, h: 0.73, fill: { color: i%2===0 ? C.cardBg : C.white }, line: { color: C.border } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 0.7, h: 0.73, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addText(item.num,   { x: 0.3, y, w: 0.7, h: 0.73, fontSize: 13, color: C.white, bold: true, fontFace: 'Calibri', align: 'center', valign: 'middle' });
  sl.addText(item.title, { x: 1.2, y: y+0.07, w: 7.0, h: 0.33, fontSize: 14, color: C.textDark, bold: true, fontFace: 'Calibri' });
  sl.addText(item.desc,  { x: 1.2, y: y+0.40, w: 8.3, h: 0.26, fontSize: 11, color: C.textMuted, fontFace: 'Calibri' });
});
```

### TO BE チェックリスト行
```javascript
const goals = [
  { label: 'DONE', text: '〇〇が完了している', dotBg: C.green, bg: C.greenLight, border: C.greenBorder },
  { label: '宿題', text: '〇〇を自分で行う',   dotBg: C.amber, bg: C.amberLight, border: C.amberBorder },
];
goals.forEach((g, i) => {
  const y = 1.28 + i * 0.67;
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 9.4, h: 0.57, fill: { color: g.bg }, line: { color: g.border } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 0.9, h: 0.57, fill: { color: g.dotBg }, line: { color: g.dotBg } });
  sl.addText(g.label, { x: 0.3, y, w: 0.9, h: 0.57, fontSize: 9, color: C.white, bold: true, fontFace: 'Calibri', align: 'center', valign: 'middle' });
  sl.addText(g.text,  { x: 1.35, y, w: 8.25, h: 0.57, fontSize: 13, color: C.textDark, fontFace: 'Calibri', valign: 'middle' });
});
```

### 次回への導線 ＆ 宿題（ダーク背景）
```javascript
const sl = pres.addSlide();
sl.background = { color: C.dark };
sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.07, fill: { color: C.purple }, line: { color: C.purple } });
sl.addShape(pres.shapes.OVAL, { x: 6.5, y: -0.8, w: 5.0, h: 5.0, fill: { color: C.purple, transparency: 88 }, line: { color: C.purple, transparency: 88 } });
sl.addText('次回への導線  ＆  宿題', { x: 0.5, y: 0.22, w: 9, h: 0.6, fontSize: 30, color: C.white, bold: true, fontFace: 'Calibri' });
// 宿題ボックス
sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.0, w: 9.4, h: 1.55, fill: { color: C.darkMid }, line: { color: C.purple }, shadow: S() });
sl.addText('[ 宿題 ]  <宿題タイトル>', { x: 0.55, y: 1.08, w: 8.8, h: 0.45, fontSize: 16, color: C.purpleLight, bold: true, fontFace: 'Calibri' });
sl.addText('<宿題の説明文>', { x: 0.55, y: 1.55, w: 8.8, h: 0.85, fontSize: 12, color: C.purpleLight, fontFace: 'Calibri' });
// 手順リスト（1〜N-1: darkRow背景+白テキスト、最終: purple+amberドット）
const nextSteps = [
  { num: '1', text: '<手順1>',  highlight: false },
  { num: '4', text: '<最終手順>', highlight: true  },
];
nextSteps.forEach((s, i) => {
  const y = 2.72 + i * 0.6;
  const rowBg = s.highlight ? C.purple  : C.darkRow;
  const dotBg = s.highlight ? C.amber   : C.purple;
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 9.4, h: 0.52, fill: { color: rowBg }, line: { color: rowBg } });
  sl.addShape(pres.shapes.OVAL, { x: 0.44, y: y+0.06, w: 0.4, h: 0.4, fill: { color: dotBg }, line: { color: dotBg } });
  sl.addText(s.num, { x: 0.44, y: y+0.06, w: 0.4, h: 0.4, fontSize: 12, color: C.white, bold: true, fontFace: 'Calibri', align: 'center', valign: 'middle' });
  sl.addText(s.text, { x: 1.02, y, w: 8.58, h: 0.52, fontSize: 12, color: C.white, bold: s.highlight, fontFace: 'Calibri', valign: 'middle' });
});
sl.addText('TIPS：〈補足メッセージ〉', { x: 0.3, y: 5.22, w: 9.4, h: 0.35, fontSize: 10, color: C.textMuted, fontFace: 'Calibri', align: 'center' });
```

---

## 既存スライドの修正

ユーザーが「〇〇スライドを直して」と言った場合：

1. 該当スライドのコードを特定し JS を修正
2. `node create_slides_<topic>.js` で再ビルド
3. soffice → pdftoppm で画像化
4. 修正箇所の `.jpg` を `Read` で確認
5. 問題なければ workspace にコピー
