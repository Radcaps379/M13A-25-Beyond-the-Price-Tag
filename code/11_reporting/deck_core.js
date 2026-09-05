/**
 * BEYOND THE PRICE TAG - deck
 *
 * DESIGN IDEA
 * The project's signature is an inversion: what the market assumes versus what
 * the evidence showed. That duality is the visual system.
 *
 *   - A tactical chalkboard ground. Pitch geometry is drawn as hairlines at low
 *     contrast, used as LAYOUT STRUCTURE rather than decoration: the halfway
 *     line at x=6.65 is a real column boundary that content respects.
 *   - Two channels of colour that never mix meaning. CHALK CYAN carries model
 *     and evidence. EMBER carries caution. FLARE appears only for the warning
 *     quadrant and the failed hypothesis.
 *   - Editorial numerals. Figures are set enormous in a serif, because the
 *     numbers are the argument.
 *   - Monospace eyebrows and chips, letterspaced, borrowed from a team sheet.
 *   - Asymmetry. Nothing is centred except the title slide.
 */
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";              // 13.33 x 7.5
pres.author = "Gudladona Venkata Rahul";
pres.title = "Beyond the Price Tag";

// ---------------------------------------------------------------- palette
const PITCH  = "0C1A24";   // chalkboard ground
const PITCH2 = "112532";   // raised panel
const CHALK  = "F2F6F8";   // primary text on dark
const LINE   = "1E3A4C";   // pitch hairlines
const CYAN   = "38C6D9";   // model, evidence, signal
const CYAN_D = "1B7A8C";   // cyan, receded
const EMBER  = "F0A63C";   // caution
const FLARE  = "E2574C";   // warning, failure
const MUTE   = "7C97A8";   // secondary text
const PAPER  = "F4F7F9";   // light slides
const INK    = "0C1A24";

const SER = "Georgia";                    // numerals and headlines
const MON = "Consolas";                   // eyebrows, chips, labels
const SAN = "Trebuchet MS";               // body

const HALF = 6.65;                        // the halfway line: a real column edge

let slideNo = 0;

// ---------------------------------------------------------------- ground
function pitchLines(s, opacity) {
  const c = { color: LINE, transparency: opacity || 0 };
  const ln = (x, y, w, h) => s.addShape(pres.ShapeType.rect,
    { x, y, w, h, fill: c, line: { width: 0 } });
  const T = 0.012;
  ln(0.42, 0.34, 12.49, T);               // touchline top
  ln(0.42, 7.16, 12.49, T);               // touchline bottom
  ln(0.42, 0.34, T, 6.82);                // goal line left
  ln(12.9, 0.34, T, 6.82);                // goal line right
  ln(HALF, 0.34, T, 6.82);                // halfway
  s.addShape(pres.ShapeType.ellipse, {    // centre circle
    x: HALF - 1.15, y: 3.6, w: 2.3, h: 2.3,
    fill: { type: "none" }, line: { color: LINE, width: 1, transparency: opacity || 0 },
  });
  // penalty areas
  ln(0.42, 2.15, 1.75, T); ln(0.42, 5.35, 1.75, T); ln(2.17, 2.15, T, 3.2);
  ln(11.16, 2.15, 1.75, T); ln(11.16, 5.35, 1.75, T); ln(11.16, 2.15, T, 3.2);
  // six-yard boxes
  ln(0.42, 3.05, 0.72, T); ln(0.42, 4.45, 0.72, T); ln(1.14, 3.05, T, 1.4);
  ln(12.19, 3.05, 0.72, T); ln(12.19, 4.45, 0.72, T); ln(12.19, 3.05, T, 1.4);
}

function dark(withPitch) {
  const s = pres.addSlide();
  s.background = { color: PITCH };
  if (withPitch !== false) pitchLines(s, 55);
  return s;
}

function light() {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 0.1, h: 7.5,
    fill: { color: CYAN_D }, line: { width: 0 } });
  return s;
}

// ---------------------------------------------------------------- type
function eyebrow(s, text, onDark) {
  s.addText(text.toUpperCase(), {
    x: 0.75, y: 0.52, w: 11.8, h: 0.26, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 10, bold: true, charSpacing: 3.2,
    color: onDark ? CYAN : CYAN_D,
  });
}

function headline(s, text, onDark, opts) {
  s.addText(text, {
    x: 0.75, y: opts && opts.y ? opts.y : 0.92, w: opts && opts.w ? opts.w : 11.8,
    h: 1.1, isTextBox: true, margin: 0, valign: "top",
    fontFace: SER, fontSize: opts && opts.size ? opts.size : 34, bold: true,
    color: onDark ? CHALK : INK, lineSpacing: opts && opts.ls ? opts.ls : 42,
  });
}

function rule(s, y, color, w) {
  s.addShape(pres.ShapeType.rect, { x: 0.75, y, w: w || 1.6, h: 0.045,
    fill: { color }, line: { width: 0 } });
}

/** monospace chip, like a team-sheet label */
function chip(s, x, y, text, color, w) {
  const width = w || (0.13 * text.length + 0.34);
  s.addShape(pres.ShapeType.rect, { x, y, w: width, h: 0.34,
    fill: { type: "none" }, line: { color, width: 1 } });
  s.addText(text.toUpperCase(), { x, y, w: width, h: 0.34, isTextBox: true,
    margin: 0, align: "center", valign: "middle",
    fontFace: MON, fontSize: 9.5, bold: true, charSpacing: 1.4, color });
  return width;
}

/** the deck's signature element: an enormous serif figure with a mono label */
function figure(s, x, y, value, label, sub, color, size) {
  s.addText(value, { x, y, w: 3.4, h: 1.0, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: size || 54, bold: true, color });
  s.addText(label.toUpperCase(), { x, y: y + (size ? 0.92 : 0.94), w: 3.4, h: 0.28,
    isTextBox: true, margin: 0, fontFace: MON, fontSize: 9.5, bold: true,
    charSpacing: 1.8, color: CHALK });
  if (sub) s.addText(sub, { x, y: y + (size ? 1.2 : 1.22), w: 3.4, h: 0.3,
    isTextBox: true, margin: 0, fontFace: SAN, fontSize: 10, color: MUTE });
}

function panel(s, x, y, w, h, accent) {
  s.addShape(pres.ShapeType.rect, { x, y, w, h,
    fill: { color: PITCH2 }, line: { color: LINE, width: 1 } });
  if (accent) s.addShape(pres.ShapeType.rect, { x, y, w: 0.045, h,
    fill: { color: accent }, line: { width: 0 } });
}

function footer(s, onDark) {
  slideNo += 1;
  const n = String(slideNo).padStart(2, "0");
  s.addText(`${n} / 12`, { x: 12.0, y: 6.95, w: 0.9, h: 0.28, isTextBox: true,
    margin: 0, align: "right", fontFace: MON, fontSize: 9,
    charSpacing: 1.2, color: onDark ? CYAN_D : "9DB2BF" });
  s.addText("BEYOND THE PRICE TAG", { x: 0.75, y: 6.95, w: 4, h: 0.28,
    isTextBox: true, margin: 0, fontFace: MON, fontSize: 8.5,
    charSpacing: 2, color: onDark ? "2C4A5C" : "C2CFD8" });
}

module.exports = {
  pres, PITCH, PITCH2, CHALK, LINE, CYAN, CYAN_D, EMBER, FLARE, MUTE, PAPER, INK,
  SER, MON, SAN, HALF, pitchLines, dark, light, eyebrow, headline, rule, chip,
  figure, panel, footer,
};
