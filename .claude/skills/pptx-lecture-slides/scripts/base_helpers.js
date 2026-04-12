/**
 * base_helpers.js
 * ─────────────────────────────────────────────────────────────────────────────
 * pptx-lecture-slides スキル用 デザインシステム & ヘルパー関数
 *
 * このファイルは create_slides_<topic>.js の先頭で require して使う。
 * カラー定数・シャドウ・全ヘルパー関数を提供する。
 *
 * 使い方:
 *   const { pres, C, S, sectionSlide, contentHeader,
 *           threeCards, handsOnIntro, stepSlides } = require('./base_helpers');
 *
 *   // スライドを追加していく ...
 *
 *   pres.writeFile({ fileName: '/path/to/output.pptx' })
 *     .then(() => console.log('Done'))
 *     .catch(err => { console.error(err); process.exit(1); });
 * ─────────────────────────────────────────────────────────────────────────────
 */

const pptxgen = require('/usr/local/lib/node_modules_global/lib/node_modules/pptxgenjs');

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
// pres.title は呼び出し側で設定すること:  pres.title = '...';

// ============================================================
// カラーパレット（16x9 ダーク×パープル基調）
// ============================================================
const C = {
  dark:        '0F172A',   // タイトル・セクション背景
  darkMid:     '1E293B',   // やや明るいダーク
  darkRow:     '263347',   // ダーク行背景
  purple:      '7C3AED',   // メインアクセント
  purpleMid:   'A78BFA',   // 中間パープル
  purpleLight: 'C4B5FD',   // 薄パープル
  white:       'FFFFFF',
  cardBg:      'F1F5F9',   // カード背景（明るいグレー）
  textDark:    '1E293B',   // メインテキスト
  textMuted:   '64748B',   // サブテキスト
  border:      'E2E8F0',   // ボーダー
  green:       '10B981',   // ハンズオン・達成系
  greenLight:  'DCFCE7',
  greenBorder: 'A7F3D0',
  greenDone:   'F0FDF4',
  amber:       'F59E0B',   // 宿題・注意系
  amberLight:  'FFF8E7',
  amberBorder: 'FDE68A',
  red:         'EF4444',   // 警告・欠点系
};

// ドロップシャドウファクトリ（オブジェクトを使い回すと pptxgenjs がクラッシュするため必ず関数で生成）
const S = () => ({ type: 'outer', blur: 8, offset: 3, angle: 135, color: '000000', opacity: 0.10 });

// ============================================================
// sectionSlide(num, title, subtitle)
//   セクション区切りスライド（ダーク背景 + パープルデコ）
//
//   num      : '01' '02' ...
//   title    : セクションタイトル（改行は \n で可）
//   subtitle : 1行のサブタイトル
// ============================================================
function sectionSlide(num, title, subtitle) {
  const sl = pres.addSlide();
  sl.background = { color: C.darkMid };
  sl.addShape(pres.shapes.OVAL, { x: 6.8, y: -0.8, w: 5.0, h: 5.0, fill: { color: C.purple, transparency: 85 }, line: { color: C.purple, transparency: 85 } });
  sl.addShape(pres.shapes.OVAL, { x: 7.8, y: 2.2,  w: 3.0, h: 3.0, fill: { color: C.purple, transparency: 78 }, line: { color: C.purple, transparency: 78 } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addText('SECTION ' + num, { x: 0.5, y: 1.0, w: 5, h: 0.4, fontSize: 11, color: C.purpleLight, bold: true, fontFace: 'Calibri', align: 'left', charSpacing: 5 });
  sl.addText(title,    { x: 0.5, y: 1.5, w: 7.8, h: 1.9, fontSize: 40, color: C.white,      bold: true, fontFace: 'Calibri', align: 'left' });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.5, w: 1.8, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addText(subtitle, { x: 0.5, y: 3.7, w: 8.5, h: 0.55, fontSize: 15, color: C.purpleLight, fontFace: 'Calibri', align: 'left' });
}

// ============================================================
// contentHeader(sl, sectionLabel, title, titleFontSize?)
//   コンテンツスライド共通ヘッダー
//   左バー + セクションラベル + タイトル + 区切り線
//   コンテンツ開始 Y 座標は 1.32"
// ============================================================
function contentHeader(sl, sectionLabel, title, titleFontSize) {
  const fs = titleFontSize || 28;
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.purple }, line: { color: C.purple } });
  sl.addText(sectionLabel, { x: 0.3, y: 0.18, w: 7, h: 0.32, fontSize: 10, color: C.purple, bold: true, fontFace: 'Calibri', align: 'left', charSpacing: 3 });
  sl.addText(title,        { x: 0.3, y: 0.5,  w: 9.3, h: 0.62, fontSize: fs, color: C.textDark, bold: true, fontFace: 'Calibri', align: 'left' });
  sl.addShape(pres.shapes.LINE, { x: 0.3, y: 1.2, w: 9.3, h: 0, line: { color: C.border, width: 0.8 } });
}

// ============================================================
// threeCards(sl, cards, startY)
//   3カラムカードレイアウト
//
//   cards: [{ num: '01', title: '...', items: ['...', '...'] }, ...]
//   startY: カード開始 Y 座標（通常 2.3〜2.5 あたり）
// ============================================================
function threeCards(sl, cards, startY) {
  cards.forEach((c, i) => {
    const x = 0.3 + i * 3.2;
    const cardH = 5.625 - startY - 0.3;
    sl.addShape(pres.shapes.RECTANGLE, { x, y: startY, w: 3.0, h: cardH, fill: { color: C.white }, line: { color: C.border }, shadow: S() });
    sl.addShape(pres.shapes.RECTANGLE, { x, y: startY, w: 3.0, h: 0.06, fill: { color: C.purple }, line: { color: C.purple } });
    sl.addShape(pres.shapes.OVAL, { x: x + 1.1, y: startY + 0.12, w: 0.8, h: 0.8, fill: { color: C.purple }, line: { color: C.purple } });
    sl.addText(c.num,   { x: x + 1.1, y: startY + 0.12, w: 0.8, h: 0.8, fontSize: 18, color: C.white, bold: true, fontFace: 'Calibri', align: 'center', valign: 'middle' });
    sl.addText(c.title, { x: x + 0.1, y: startY + 1.05, w: 2.8, h: 0.45, fontSize: 13, color: C.purple, bold: true, fontFace: 'Calibri', align: 'center' });
    c.items.forEach((item, j) => {
      sl.addText('・  ' + item, { x: x + 0.15, y: startY + 1.58 + j * 0.52, w: 2.7, h: 0.48, fontSize: 11, color: C.textMuted, fontFace: 'Calibri' });
    });
  });
}

// ============================================================
// handsOnIntro(sectionLabel, subtitle, stepCount)
//   「一緒にやってみよう！」シリーズ冒頭のサブセクション表紙スライド
//   緑テーマのダーク背景
//
//   sectionLabel : 'SECTION 01' など
//   subtitle     : 作業名 '拡張機能 ＋ ログイン' など
//   stepCount    : 続くステップ数（整数）
// ============================================================
function handsOnIntro(sectionLabel, subtitle, stepCount) {
  const sl = pres.addSlide();
  sl.background = { color: C.darkMid };
  sl.addShape(pres.shapes.OVAL, { x: 6.5, y: -0.5, w: 4.5, h: 4.5, fill: { color: C.green, transparency: 88 }, line: { color: C.green, transparency: 88 } });
  sl.addShape(pres.shapes.OVAL, { x: 7.5, y: 2.8,  w: 2.8, h: 2.8, fill: { color: C.green, transparency: 82 }, line: { color: C.green, transparency: 82 } });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.green }, line: { color: C.green } });
  sl.addText(sectionLabel, { x: 0.5, y: 1.05, w: 6, h: 0.36, fontSize: 11, color: C.green, bold: true, fontFace: 'Calibri', align: 'left', charSpacing: 4 });
  sl.addText('一緒にやってみよう！', { x: 0.5, y: 1.5, w: 8, h: 0.82, fontSize: 38, color: C.white, bold: true, fontFace: 'Calibri', align: 'left' });
  if (subtitle) {
    sl.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.42, w: 0.06, h: 0.52, fill: { color: C.green }, line: { color: C.green } });
    sl.addText(subtitle, { x: 0.7, y: 2.42, w: 8, h: 0.52, fontSize: 20, color: C.green, bold: true, fontFace: 'Calibri', align: 'left', valign: 'middle' });
  }
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.0, w: 1.6, h: 0.05, fill: { color: C.green }, line: { color: C.green } });
  if (stepCount) {
    sl.addText('全 ' + stepCount + ' ステップ', { x: 0.5, y: 3.2, w: 4, h: 0.38, fontSize: 13, color: C.purpleLight, fontFace: 'Calibri' });
  }
}

// ============================================================
// stepSlides(sectionLabel, slideTitle, steps, subtitleLabel?)
//   ハンズオン手順スライド群（1ステップ = 1スライド、プログレッシブ緑ハイライト）
//
//   steps: [{ text: '手順テキスト', note: 'サブノート（省略可）' }, ...]
//     text  : メインの操作手順
//     note  : 補足説明（省略可。アクティブステップのみ表示）
//   subtitleLabel: タイトルに追加する副題（省略可）
//
//   スタイルルール:
//     - 現在ステップ → 緑ハイライト、数字ドット
//     - 完了ステップ → 薄緑、✓ドット
//     - 未来ステップ → グレー、数字ドット（note は非表示）
//   注意: note に絵文字（U+1F000以上）は使わないこと（LibreOffice で文字化け）
// ============================================================
function stepSlides(sectionLabel, slideTitle, steps, subtitleLabel) {
  const n = steps.length;
  const stepH = n <= 3 ? 1.0 : (n === 4 ? 0.85 : 0.72);
  const gap   = n <= 3 ? 0.10 : 0.06;

  steps.forEach((_, currentIdx) => {
    const sl = pres.addSlide();
    sl.background = { color: C.white };

    sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.08, h: 5.625, fill: { color: C.purple }, line: { color: C.purple } });
    sl.addText(sectionLabel, { x: 0.3, y: 0.18, w: 7.5, h: 0.32, fontSize: 10, color: C.purple, bold: true, fontFace: 'Calibri', align: 'left', charSpacing: 3 });
    sl.addText('STEP ' + (currentIdx + 1) + ' / ' + n, { x: 7.8, y: 0.18, w: 1.8, h: 0.32, fontSize: 10, color: C.textMuted, fontFace: 'Calibri', align: 'right' });

    const titleText = subtitleLabel ? slideTitle + '　' + subtitleLabel : slideTitle;
    sl.addText(titleText, { x: 0.3, y: 0.5, w: 9.3, h: 0.62, fontSize: 26, color: C.textDark, bold: true, fontFace: 'Calibri', align: 'left' });
    sl.addShape(pres.shapes.LINE, { x: 0.3, y: 1.2, w: 9.3, h: 0, line: { color: C.border, width: 0.8 } });

    const startY = 1.32;
    steps.forEach((s, i) => {
      const y = startY + i * (stepH + gap);
      const isActive = i === currentIdx;
      const isDone   = i < currentIdx;

      const bg     = isActive ? C.greenLight : (isDone ? C.greenDone : (i % 2 === 0 ? C.cardBg : C.white));
      const border = isActive ? C.green      : (isDone ? C.greenBorder : C.border);
      const dotBg  = (isActive || isDone) ? C.green : C.purple;

      sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y, w: 9.4, h: stepH, fill: { color: bg }, line: { color: border } });
      sl.addShape(pres.shapes.OVAL, { x: 0.43, y: y + (stepH - 0.46) / 2, w: 0.46, h: 0.46, fill: { color: dotBg }, line: { color: dotBg } });
      sl.addText(isDone ? '✓' : String(i + 1), {
        x: 0.43, y: y + (stepH - 0.46) / 2, w: 0.46, h: 0.46,
        fontSize: 13, color: C.white, bold: true, fontFace: 'Calibri', align: 'center', valign: 'middle'
      });

      if (s.note && stepH >= 0.80) {
        sl.addText(s.text, { x: 1.06, y: y + 0.07, w: 8.44, h: 0.35, fontSize: 13, color: C.textDark, bold: isActive, fontFace: 'Calibri' });
        sl.addText(s.note, { x: 1.06, y: y + 0.46, w: 8.44, h: 0.28, fontSize: 10, color: C.textMuted, fontFace: 'Calibri' });
      } else if (s.note) {
        sl.addText(s.text, { x: 1.06, y: y + 0.06, w: 8.44, h: 0.30, fontSize: 12, color: C.textDark, bold: isActive, fontFace: 'Calibri' });
        if (isActive) {
          sl.addText(s.note, { x: 1.06, y: y + 0.38, w: 8.44, h: 0.25, fontSize: 9, color: C.textMuted, fontFace: 'Calibri' });
        }
      } else {
        sl.addText(s.text, { x: 1.06, y: y + (stepH - 0.38) / 2, w: 8.44, h: 0.38, fontSize: 13, color: C.textDark, bold: isActive, fontFace: 'Calibri', valign: 'middle' });
      }
    });
  });
}

module.exports = { pres, C, S, sectionSlide, contentHeader, threeCards, handsOnIntro, stepSlides };
