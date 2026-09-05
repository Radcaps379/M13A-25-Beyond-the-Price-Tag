/**
 * SUPERSEDED - retained as development history.
 *
 * This produced the first deck design. The submitted presentation is built
 * by build_deck_v2.js with deck_core.js, which replaced it. Running this
 * file would overwrite the submitted deck with the earlier design.
 */

const path = require("path");
// Repository root, derived from this file's location rather than an absolute
// path belonging to the machine the project was built on.
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const P = (...p) => path.join(REPO_ROOT, ...p);

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.3 x 7.5
pres.author = "Beyond the Price Tag";

// ---------------------------------------------------------------- palette
// Committee-room ink with a single restrained teal for model signal and amber
// for caution. Amber appears ONLY where the project counsels caution - it is
// the deck's motif and it carries meaning rather than decoration.
const INK   = "12212E";   // dominant
const SLATE = "2C3E50";
const TEAL  = "2F6F7E";   // model signal
const AMBER = "C4791F";   // caution
const RUST  = "9B3F2E";   // warning
const PAPER = "F7F5F0";
const MUTE  = "7B8794";
const WHITE = "FFFFFF";

const HEAD = "Cambria";   // safe-list serif
const BODY = "Calibri";   // safe-list sans

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}
function lightSlide() {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  return s;
}
function title(s, text, dark) {
  s.addText(text, {
    x: 0.7, y: 0.755, w: 11.9, h: 0.96, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 32, bold: true,
    color: dark ? WHITE : INK, align: "left",
  });
}
function eyebrow(s, text, dark) {
  s.addText(text.toUpperCase(), {
    x: 0.7, y: 0.45, w: 11.9, h: 0.316, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, bold: true, charSpacing: 2.4,
    color: dark ? "5FA8B8" : MUTE,
  });
}
const SY = (y) => 0.45 + (y - 0.18) * 1.13;   // vertical rescale
const SH = (h) => h * 1.13;

function stat(s, x, y0, w, big, label, color, sub) {
  const y = SY(y0);
  s.addText(big, { x, y, w, h: 0.814, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color });
  s.addText(label, { x, y: y + 0.72, w, h: 0.339, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, bold: true, color: SLATE });
  if (sub) s.addText(sub, { x, y: y + 1.0, w, h: 0.339, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 9.5, color: MUTE, italic: true });
}
function cardAbs(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: fill || WHITE },
    line: { color: "DCD8D0", width: 0.75 },
    shadow: { type: "outer", angle: 90, blur: 6, offset: 1, color: "999999", opacity: 0.16 },
  });
}
function card(s, x, y0, w, h0, fill) {
  const y = SY(y0), h = SH(h0);
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: fill || WHITE },
    line: { color: "DCD8D0", width: 0.75 },
    shadow: { type: "outer", angle: 90, blur: 6, offset: 1, color: "999999", opacity: 0.16 },
  });
}

// =============================================================== 1. TITLE
{
  const s = darkSlide();
  s.addText("Beyond the Price Tag", {
    x: 0.9, y: 2.846, w: 11.5, h: 1.299, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 52, bold: true, color: WHITE,
  });
  s.addText("An Explainable AI Decision-Support System for Football Transfer-Budget Allocation", {
    x: 0.9, y: 4.202, w: 10.6, h: 0.847, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 19, color: "C9D4DA",
  });
  s.addShape(pres.ShapeType.rect, { x: 0.9, y: 5.388, w: 1.5, h: 0.04, fill: { color: TEAL }, line: { width: 0 } });
  s.addText("Sports Analytics  |  Working with AI  |  IIM Ranchi", {
    x: 0.9, y: 5.727, w: 9, h: 0.395, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12.5, color: MUTE, charSpacing: 1.1,
  });
  s.addNotes("Beyond the Price Tag. A decision-support system for allocating a football club's transfer budget. The story: we set out to find undervalued players, tested that hypothesis properly, and what we found changed the system we built.");
}

// =============================================================== 2. PROBLEM
{
  const s = lightSlide();
  eyebrow(s, "The managerial problem");
  s.addText("How should a club allocate a finite transfer budget\nwhen market value is informative but incomplete?", {
    x: 0.7, y: 0.868, w: 11.9, h: 1.469, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 29, bold: true, color: INK, lineSpacing: 36,
  });

  const items = [
    ["Irreversible", "A fee is sunk. Wages persist for years. The squad slot is unavailable to anyone else."],
    ["Constrained", "A budget cannot be exceeded, and five wingers do not solve a defensive problem."],
    ["Partially observable", "Contract, medical, tactical and personal information sit outside public data."],
    ["Heterogeneous", "Performance means different things by position, league and age."],
  ];
  items.forEach((it, i) => {
    const x = 0.7 + i * 3.02;
    card(s, x, 2.35, 2.75, 2.5);
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.28, y: 3.207, w: 0.4, h: 0.452,
      fill: { color: TEAL }, line: { width: 0 } });
    s.addText(String(i + 1), { x: x + 0.28, y: 3.207, w: 0.4, h: 0.452, isTextBox: true,
      margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: WHITE });
    s.addText(it[0], { x: x + 0.28, y: 3.795, w: 2.2, h: 0.407, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 15, bold: true, color: INK });
    s.addText(it[1], { x: x + 0.28, y: 4.258, w: 2.2, h: 1.356, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 11, color: SLATE, lineSpacing: 15 });
  });

  s.addText("Recruitment resembles capital budgeting more than shopping — yet clubs decide one player at a time.", {
    x: 0.7, y: 6.179, w: 11.9, h: 0.452, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, italic: true, color: AMBER,
  });
  s.addNotes("Four properties shape the decision. The key line: recruitment is capital budgeting, but clubs treat the budget as a running balance rather than a portfolio to allocate.");
}

// =============================================================== 3. HYPOTHESIS
{
  const s = lightSlide();
  eyebrow(s, "Where the project started");
  title(s, "The original hypothesis");

  const chain = ["Performance\nAge · Position\nTrajectory", "Model-implied\nvaluation",
                 "Valuation gap\nvs market", "Recruitment\nopportunity?"];
  chain.forEach((t, i) => {
    const x = 0.7 + i * 3.05;
    const isLast = i === 3;
    card(s, x, 1.85, 2.5, 1.5, isLast ? "FFF4E0" : WHITE);
    s.addText(t, { x: x + 0.12, y: 2.45, w: 2.26, h: 1.469, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: BODY, fontSize: 12.5,
      bold: isLast, color: isLast ? AMBER : SLATE, lineSpacing: 16 });
    if (i < 3) s.addText("→", { x: x + 2.55, y: 2.846, w: 0.45, h: 0.565, isTextBox: true,
      margin: 0, align: "center", fontFace: BODY, fontSize: 20, color: MUTE });
  });

  card(s, 0.7, 3.75, 11.9, 1.55, "FFFFFF");
  s.addText("Is the gap actually an opportunity?", {
    x: 1.1, y: 4.744, w: 11.1, h: 0.565, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 26, bold: true, color: INK });
  s.addText("If the market is wrong, the discrepancy is an opportunity. If the model is missing something, the same discrepancy is a warning.\nThe two have opposite managerial implications — so we treated the claim as a hypothesis to test, not a premise to build on.", {
    x: 1.1, y: 5.332, w: 11.1, h: 0.791, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12.5, color: SLATE, lineSpacing: 17 });
  s.addNotes("This is the logic the project began with. It is plausible and widely held. The critical question is whether the gap is opportunity or model error — and those point in opposite directions.");
}

// =============================================================== 4. DATA & DESIGN
{
  const s = lightSlide();
  eyebrow(s, "Data and analytical design");
  title(s, "What the system was built on");

  stat(s, 0.7, 1.75, 2.7, "15,925", "PLAYER-SEASONS", TEAL, "4,961 unique players");
  stat(s, 3.65, 1.75, 2.7, "10", "SEASONS", TEAL, "2015/16 – 2024/25");
  stat(s, 6.6, 1.75, 2.7, "5", "LEAGUES", TEAL, "England, Spain, Germany,\nItaly, France");
  stat(s, 9.55, 1.75, 3.0, "1,508", "HELD-OUT PLAYERS", AMBER, "2024/25, examined once");

  const flow = ["Data", "Model 0\ncontext", "Model 1\nfundamentals", "Model 2\nmarket-informed", "Back-test"];
  flow.forEach((t, i) => {
    const x = 0.7 + i * 2.45;
    const hero = i === 2;
    card(s, x, 4.15, 2.1, 1.0, hero ? "E4EDEF" : WHITE);
    s.addText(t, { x: x + 0.08, y: 4.993, w: 1.94, h: 1.017, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: BODY, fontSize: 11.5,
      bold: hero, color: hero ? TEAL : SLATE, lineSpacing: 14 });
    if (i < 4) s.addText("→", { x: x + 2.12, y: 5.275, w: 0.35, h: 0.452, isTextBox: true,
      margin: 0, align: "center", fontFace: BODY, fontSize: 16, color: MUTE });
  });

  s.addText("Train 2015/16–2021/22   ·   Validate 2022/23–2023/24   ·   Test 2024/25, once. Strictly time-based throughout.", {
    x: 0.7, y: 6.349, w: 11.9, h: 0.395, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, color: MUTE, italic: true });
  s.addNotes("One dataset, every join on integer IDs, no name matching anywhere. Strict time-based validation: no feature, threshold or constant was ever fitted using validation or test information.");
}

// =============================================================== 5. WHAT EXPLAINS VALUE
{
  const s = lightSlide();
  eyebrow(s, "Evidence 1");
  title(s, "What explains market value?");

  s.addChart(pres.ChartType.bar, [{
    name: "Test R²", labels: ["Model 0\ncontext only", "Model 1\n+ fundamentals", "Model 2\n+ prior market value"],
    values: [0.383, 0.678, 0.884],
  }], {
    x: 0.7, y: 2.168, w: 7.3, h: 3.955, barDir: "col",
    chartColors: [MUTE, TEAL, AMBER],
    showTitle: false, showLegend: false,
    showValue: true, dataLabelPosition: "outEnd",
    dataLabelFormatCode: "0.000", dataLabelFontSize: 13,
    dataLabelColor: INK, dataLabelFontFace: BODY,
    valAxisMaxVal: 1.0, valAxisMinVal: 0,
    catAxisLabelColor: SLATE, valAxisLabelColor: MUTE,
    catAxisLabelFontFace: BODY, catAxisLabelFontSize: 11,
    valGridLine: { color: "E4E0D8", size: 0.75 },
    catGridLine: { style: "none" },
  });

  card(s, 8.3, 1.7, 4.3, 3.5);
  s.addText("Observable fundamentals carry real valuation signal", {
    x: 8.6, y: 2.45, w: 3.7, h: 0.847, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 16, bold: true, color: INK, lineSpacing: 20 });
  s.addText("Performance, age, position, league and career trajectory raise explanatory power from 0.383 to 0.678.", {
    x: 8.6, y: 3.354, w: 3.7, h: 0.904, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, color: SLATE, lineSpacing: 16 });
  s.addText("But prior market beliefs explain considerably more", {
    x: 8.6, y: 4.315, w: 3.7, h: 0.621, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: AMBER, lineSpacing: 19 });
  s.addText("Two market-derived variables add 0.206 — more than twenty-nine performance features contributed.", {
    x: 8.6, y: 4.993, w: 3.7, h: 0.904, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, color: SLATE, lineSpacing: 16 });

  s.addText("Predicting the market is easier than explaining it — and the two are not the same objective.", {
    x: 0.7, y: 6.349, w: 11.9, h: 0.452, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, italic: true, color: AMBER });
  s.addNotes("Held-out 2024/25, n=1,508, identical rows for all three models. Model 2 is not 'better' — its residual is deviation from Transfermarkt's own persistence, which has no economic meaning. That is why Model 1 stays primary despite lower accuracy.");
}

// =============================================================== 6. THE TEST
{
  const s = darkSlide();
  eyebrow(s, "Evidence 2 — the hypothesis test", true);
  s.addText("Potential valuation discrepancy\n≠ proven market inefficiency", {
    x: 0.7, y: 1.546, w: 11.9, h: 1.808, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 36, bold: true, color: WHITE, lineSpacing: 46 });

  const tests = [
    ["Raw residual", "Pre-registered", "p = 0.094", "no advantage"],
    ["Calibrated + screened", "Same procedure", "p = 0.307", "no advantage"],
  ];
  tests.forEach((t, i) => {
    const y = SY(3.15 + i * 1.05);
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 8.0, h: 0.96, rectRadius: 0.05,
      fill: { color: "1C3040" }, line: { color: "2A4356", width: 0.75 } });
    s.addText(t[0], { x: 1.0, y: y + 0.06, w: 3.0, h: 0.407, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 14, bold: true, color: WHITE });
    s.addText(t[1], { x: 1.0, y: y + 0.44, w: 3.0, h: 0.339, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 10.5, color: MUTE });
    s.addText(t[2], { x: 4.6, y: y + 0.2, w: 1.9, h: 0.508, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 20, bold: true, color: AMBER });
    s.addText(t[3], { x: 6.6, y: y + 0.26, w: 1.9, h: 0.395, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, color: "C9D4DA" });
  });

  s.addShape(pres.ShapeType.roundRect, { x: 9.0, y: 3.806, w: 3.6, h: 2.203, rectRadius: 0.05,
    fill: { color: "1C3040" }, line: { color: TEAL, width: 1 } });
  s.addText("Two specifications tested.\nThen we stopped.", {
    x: 9.3, y: 4.089, w: 3.0, h: 0.847, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: WHITE, lineSpacing: 20 });
  s.addText("Thresholds fixed on validation, applied once to the held-out season. Iterating until significance appeared would have invalidated the test.", {
    x: 9.3, y: 4.936, w: 3.0, h: 0.96, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: "C9D4DA", lineSpacing: 14 });

  s.addText("The out-of-sample evidence did not support the hypothesis that the valuation residual identifies exploitable mispricing.", {
    x: 0.7, y: 6.518, w: 11.9, h: 0.508, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13.5, color: AMBER, italic: true });
  s.addNotes("This is the pivot of the project. A promising validation differential did not replicate on test — the signature of a signal that was noise. The discipline of stopping is what makes the negative result informative.");
}

// =============================================================== 7. EXIT RISK
{
  const s = lightSlide();
  eyebrow(s, "Evidence 3 — the discovery");
  title(s, "The residual was a risk signal, not an arbitrage signal");

  stat(s, 0.7, 1.85, 3.0, "3.7×", "THE EXIT RATE", RUST, "30.1% vs 8.2% benchmark");
  stat(s, 3.9, 1.85, 3.0, "0.732", "EXIT MODEL AUC", TEAL, "held-out 2024/25, n = 1,508");
  stat(s, 7.1, 1.85, 3.0, "9.5×", "OBSERVED DECILE SPREAD", TEAL, "7.3% lowest vs 69.5% highest");

  card(s, 10.3, 1.85, 2.3, 1.5, "F6E3DE");
  s.addText("p = 2.6 × 10⁻¹¹", { x: 10.5, y: 2.676, w: 1.9, h: 0.452, isTextBox: true,
    margin: 0, align: "center", fontFace: HEAD, fontSize: 17, bold: true, color: RUST });
  s.addText("Fisher exact · OR 4.82", { x: 10.5, y: 3.185, w: 1.9, h: 0.339, isTextBox: true,
    margin: 0, align: "center", fontFace: BODY, fontSize: 10.5, color: SLATE });

  s.addChart(pres.ChartType.line, [
    { name: "Predicted", labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
      values: [5.2, 10.4, 15.5, 19.4, 23.0, 29.1, 35.4, 43.6, 53.7, 69.6] },
    { name: "Actual", labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
      values: [7.3, 11.3, 17.9, 23.8, 30.5, 25.8, 36.0, 39.1, 55.0, 69.5] },
  ], {
    x: 0.7, y: 4.315, w: 7.6, h: 2.373, chartColors: [TEAL, AMBER],
    showTitle: false, showLegend: true, legendPos: "t", legendFontSize: 10,
    lineSize: 2.5, lineDataSymbolSize: 5,
    catAxisTitle: "Risk decile", showCatAxisTitle: true, catAxisTitleFontSize: 10,
    valAxisTitle: "Exit rate (%)", showValAxisTitle: true, valAxisTitleFontSize: 10,
    catAxisLabelColor: SLATE, valAxisLabelColor: MUTE,
    valGridLine: { color: "E4E0D8", size: 0.75 }, catGridLine: { style: "none" },
  });

  card(s, 8.6, 3.6, 4.0, 2.1);
  s.addText("Where a model disagrees with the market, the market is usually right", {
    x: 8.85, y: 4.541, w: 3.5, h: 0.96, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 15, bold: true, color: INK, lineSpacing: 19 });
  s.addText("A large unexplained gap more often signals information the market holds and public match data does not — contract, injury, role — than an error to exploit.", {
    x: 8.85, y: 5.558, w: 3.5, h: 1.017, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11.5, color: SLATE, lineSpacing: 15 });
  s.addNotes("The same diagnostic that invalidated the mispricing reading revealed a far stronger relationship running the other way. Calibration matters as much as discrimination: predicted and actual converge closely at both extremes, so these can be used as probabilities in a decision rule.");
}

// =============================================================== 8. EXPLAINABILITY
{
  const s = lightSlide();
  eyebrow(s, "Explainable AI");
  title(s, "Two different questions, two different answers");

  // Buonanotte - the lead example
  card(s, 0.7, 1.75, 5.75, 3.5);
  s.addText("Facundo Buonanotte", { x: 1.0, y: 2.45, w: 5.2, h: 0.429, isTextBox: true,
    margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: INK });
  s.addText("Midfield · Premier League · age 20 · market €20.0M · model-implied €20.3M", {
    x: 1.0, y: 2.902, w: 5.2, h: 0.362, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: MUTE });

  s.addText("WHY THE MODEL VALUES HIM THIS WAY", { x: 1.0, y: 3.411, w: 5.2, h: 0.316,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, bold: true,
    charSpacing: 1.2, color: TEAL });
  s.addText([
    { text: "age +0.764  ·  goal contributions +0.137  ·  league context +0.344", options: { breakLine: true } },
    { text: "minutes −0.143  ·  squad rotation −0.082", options: {} },
  ], { x: 1.0, y: 3.75, w: 5.2, h: 0.734, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: SLATE, lineSpacing: 15 });

  s.addText("WHY THE OPTIMIZER SELECTED HIM", { x: 1.0, y: 4.597, w: 5.2, h: 0.316,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, bold: true,
    charSpacing: 1.2, color: AMBER });
  s.addText("Quality 86th percentile · potential 0.77 · value efficiency 0.57", {
    x: 1.0, y: 4.936, w: 5.2, h: 0.395, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: SLATE });
  s.addText("His valuation gap is essentially zero. He was selected on quality and development potential — not on a bargain.", {
    x: 1.0, y: 5.388, w: 5.2, h: 0.678, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, italic: true, color: AMBER, lineSpacing: 14 });

  // Coppola - secondary
  card(s, 6.85, 1.75, 5.75, 3.5);
  s.addText("Diego Coppola", { x: 7.15, y: 2.45, w: 5.2, h: 0.429, isTextBox: true,
    margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: INK });
  s.addText("Defender · Serie A · age 21 · market €10.0M · model-implied €27.1M", {
    x: 7.15, y: 2.902, w: 5.2, h: 0.362, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10.5, color: MUTE });

  s.addText("WHY THE MODEL VALUES HIM THIS WAY", { x: 7.15, y: 3.411, w: 5.2, h: 0.316,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, bold: true,
    charSpacing: 1.2, color: TEAL });
  s.addText([
    { text: "age +0.955  ·  league minutes +0.336  ·  height +0.138", options: { breakLine: true } },
    { text: "goal contributions −0.179  ·  Serie A −0.155", options: {} },
  ], { x: 7.15, y: 3.75, w: 5.2, h: 0.734, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: SLATE, lineSpacing: 15 });

  s.addText("WHAT THE MODEL DOES NOT KNOW", { x: 7.15, y: 4.597, w: 5.2, h: 0.316,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 9.5, bold: true,
    charSpacing: 1.2, color: RUST });
  s.addText("No contract length, injury history, scouting assessment, or willingness to move. Exit probability 12.9%.", {
    x: 7.15, y: 4.936, w: 5.2, h: 0.678, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: SLATE, lineSpacing: 14 });
  s.addText("Goal contributions LOWER a defender's implied value — the model reasons by position.", {
    x: 7.15, y: 5.614, w: 5.2, h: 0.508, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, italic: true, color: TEAL, lineSpacing: 14 });

  s.addText("SHAP explains a number. The optimizer explains a choice. Conflating them would let a persuasive valuation stand in for a selection rationale.", {
    x: 0.7, y: 6.405, w: 11.9, h: 0.452, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12.5, italic: true, color: MUTE });
  s.addNotes("Buonanotte is the important example: model and market agree on his price, and he was still selected. That is the clearest proof the system is no longer a bargain-finder. Coppola shows position-appropriate reasoning — attacking output reduces a defender's implied value.");
}

// =============================================================== 9. HERO - THE INVERSION
{
  const s = darkSlide();
  eyebrow(s, "The central inversion", true);
  s.addText("A large gap is only interesting when the risk is low", {
    x: 0.7, y: 0.834, w: 11.9, h: 0.791, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: WHITE });

  const QX = 2.6, QY = 2.11, QW = 8.1, QH = 4.4;
  const quads = [
    [QX, QY, "High gap · Low risk", "POTENTIAL OPPORTUNITY", "investigate", "5FA8B8", "1C3040"],
    [QX + QW / 2, QY, "High gap · High risk", "WARNING", "the market likely knows something", "D9705C", "3A2320"],
    [QX, QY + QH / 2, "Low gap · Low risk", "BROADLY ALIGNED", "no action indicated", "AEBDC7", "1C3040"],
    [QX + QW / 2, QY + QH / 2, "Low gap · High risk", "RISK CAUTION", "retention concern", AMBER, "352B1C"],
  ];
  // note: x axis = risk (left low, right high); y axis = gap (top high)
  quads.forEach(q => {
    s.addShape(pres.ShapeType.rect, { x: q[0], y: q[1], w: QW / 2, h: QH / 2,
      fill: { color: q[6] }, line: { color: "2A4356", width: 1 } });
    s.addText(q[2], { x: q[0] + 0.25, y: q[1] + 0.28, w: QW / 2 - 0.5, h: 0.316,
      isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10, color: MUTE, charSpacing: 1 });
    s.addText(q[3], { x: q[0] + 0.25, y: q[1] + 0.62, w: QW / 2 - 0.5, h: 0.508,
      isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 19, bold: true, color: q[5] });
    s.addText(q[4], { x: q[0] + 0.25, y: q[1] + 1.12, w: QW / 2 - 0.5, h: 0.452,
      isTextBox: true, margin: 0, fontFace: BODY, fontSize: 11, color: "C9D4DA" });
  });

  s.addText("VALUATION GAP  →", { x: 0.75, y: QY + QH / 2 - 0.3, w: 1.75, h: 0.395,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 10, bold: true,
    color: MUTE, charSpacing: 1, align: "right" });
  s.addText("high  ↑", { x: 0.75, y: QY + 0.1, w: 1.75, h: 0.339, isTextBox: true,
    margin: 0, align: "right", fontFace: BODY, fontSize: 10, color: MUTE });
  s.addText("↓  low", { x: 0.75, y: QY + QH - 0.4, w: 1.75, h: 0.339, isTextBox: true,
    margin: 0, align: "right", fontFace: BODY, fontSize: 10, color: MUTE });
  s.addText("←  lower exit risk                    EXIT RISK                    higher exit risk  →", {
    x: QX, y: QY + QH + 0.15, w: QW, h: 0.362, isTextBox: true, margin: 0,
    align: "center", fontFace: BODY, fontSize: 10.5, bold: true, color: MUTE, charSpacing: 1 });

  s.addText("The system never labels a player “undervalued”. It says: potential valuation discrepancy — investigate.", {
    x: 0.7, y: 6.857, w: 11.9, h: 0.452, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, italic: true, color: "5FA8B8" });
  s.addNotes("This is the hero slide. Read the top-right quadrant carefully: a large valuation gap combined with high exit risk is the profile the naive approach would rank FIRST, and it is the one this system flags as a warning.");
}

// =============================================================== 10. SCENARIO
{
  const s = lightSlide();
  eyebrow(s, "Recruitment committee scenario");
  title(s, "€50M, one defender, one midfielder, one attacker");

  const picks = [
    ["Lucas Stassin", "Attack · Ligue 1 · 20", "€18.0M", "€31.1M", "90th", "14%"],
    ["Diego Coppola", "Defender · Serie A · 21", "€10.0M", "€27.1M", "89th", "13%"],
    ["Facundo Buonanotte", "Midfield · Premier League · 20", "€20.0M", "€20.3M", "86th", "25%"],
  ];
  s.addText(["PLAYER", "MARKET", "MODEL-IMPLIED", "QUALITY", "EXIT RISK"].join("          "), {
    x: 0.95, y: 2.224, w: 7.6, h: 0.282, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 8.5, bold: true, color: MUTE, charSpacing: 1 });
  picks.forEach((p, i) => {
    const y = SY(2.1 + i * 1.02);
    cardAbs(s, 0.7, y, 8.1, SH(0.88));
    s.addText(p[0], { x: 0.95, y: y + 0.12, w: 2.7, h: 0.362, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 14.5, bold: true, color: INK });
    s.addText(p[1], { x: 0.95, y: y + 0.46, w: 2.7, h: 0.316, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 9.5, color: MUTE });
    s.addText(p[2], { x: 3.8, y: y + 0.26, w: 1.2, h: 0.407, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, color: SLATE });
    s.addText(p[3], { x: 5.1, y: y + 0.26, w: 1.3, h: 0.407, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, bold: true, color: TEAL });
    s.addText(p[4], { x: 6.6, y: y + 0.26, w: 1.0, h: 0.407, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, color: SLATE });
    s.addText(p[5], { x: 7.7, y: y + 0.26, w: 0.9, h: 0.407, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, bold: true, color: TEAL });
  });

  card(s, 9.1, 2.1, 3.5, 3.6, "E4EDEF");
  s.addText("€48.0M", { x: 9.35, y: 2.868, w: 3.0, h: 0.678, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 34, bold: true, color: TEAL });
  s.addText("COMMITTED OF €50M", { x: 9.35, y: 3.546, w: 3.0, h: 0.316, isTextBox: true,
    margin: 0, fontFace: BODY, fontSize: 10, bold: true, color: SLATE, charSpacing: 1 });
  s.addText([
    { text: "Mean quality percentile        88.3", options: { breakLine: true } },
    { text: "Mean predicted exit risk     17.1%", options: { breakLine: true } },
    { text: "Mean age                              20.4", options: {} },
  ], { x: 9.35, y: 4.089, w: 3.0, h: 1.13, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11.5, color: SLATE, lineSpacing: 18 });
  s.addText("Solved as an integer linear program under declared weights and constraints.", {
    x: 9.35, y: 5.219, w: 3.0, h: 0.565, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 10, italic: true, color: MUTE, lineSpacing: 13 });

  s.addShape(pres.ShapeType.roundRect, { x: 0.7, y: 6.236, w: 11.9, h: 0.701, rectRadius: 0.05,
    fill: { color: "FFF4E0" }, line: { color: AMBER, width: 1 } });
  s.addText("Illustrative application of a validated risk model — NOT optimizer validation. Three players cannot establish effectiveness.", {
    x: 1.0, y: 6.394, w: 11.3, h: 0.407, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12.5, bold: true, color: AMBER });
  s.addNotes("Say the caveat out loud. The exit-risk model is validated at population level, n=1,508. This three-player portfolio demonstrates the method; it does not prove the method works. Do not let anyone read this slide as a back-test result.");
}

// =============================================================== 11. ROBUSTNESS
{
  const s = lightSlide();
  eyebrow(s, "Robustness and sensitivity");
  title(s, "Would different assumptions change the answer?");

  s.addText("SELECTION STABILITY ACROSS SIX WEIGHT CONFIGURATIONS", {
    x: 0.7, y: 2.168, w: 6.0, h: 0.316, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 9.5, bold: true, charSpacing: 1.1, color: MUTE });
  const stab = [["Lucas Stassin", 6, TEAL], ["Diego Coppola", 4, TEAL], ["Facundo Buonanotte", 3, AMBER]];
  stab.forEach((p, i) => {
    const y = SY(2.1 + i * 0.72);
    s.addText(p[0], { x: 0.7, y, w: 2.5, h: 0.395, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12.5, color: SLATE });
    for (let k = 0; k < 6; k++) {
      s.addShape(pres.ShapeType.rect, { x: 3.35 + k * 0.42, y: y + 0.04, w: 0.32, h: 0.316,
        fill: { color: k < p[1] ? p[2] : "E4E0D8" }, line: { width: 0 } });
    }
    s.addText(`${p[1]} of 6`, { x: 6.0, y, w: 1.2, h: 0.395, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 12, bold: true, color: p[2] });
  });

  s.addText("Meaningful stability — not complete invariance. The core recommendation persists; the remainder shifts with managerial priorities.", {
    x: 0.7, y: 5.162, w: 6.5, h: 0.678, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 12, italic: true, color: SLATE, lineSpacing: 16 });

  s.addChart(pres.ChartType.line, [{
    name: "Committed (€M)", labels: ["€20M", "€35M", "€50M", "€75M", "€100M"],
    values: [20, 34, 48, 52, 52],
  }], {
    x: 7.4, y: 2.45, w: 5.2, h: 3.051, chartColors: [TEAL],
    showTitle: true, title: "Spend plateaus as constraints bind",
    titleFontSize: 12, titleColor: INK, titleFontFace: BODY,
    showLegend: false, showValue: true, dataLabelPosition: "t",
    dataLabelFontSize: 10, dataLabelColor: SLATE,
    lineSize: 2.5, lineDataSymbolSize: 6,
    catAxisLabelColor: SLATE, valAxisLabelColor: MUTE,
    valGridLine: { color: "E4E0D8", size: 0.75 }, catGridLine: { style: "none" },
  });
  s.addText("Beyond ~€75M more budget buys nothing: the quality, age, risk and confidence constraints bind before the money does. Relaxing a constraint may be worth more than raising the budget.", {
    x: 7.4, y: 5.614, w: 5.2, h: 0.847, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11, color: SLATE, lineSpacing: 15 });

  s.addText("A property of the model's eligible universe — not evidence of a €52M optimum in the real transfer market.", {
    x: 0.7, y: 6.575, w: 11.9, h: 0.395, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 11.5, italic: true, color: MUTE });
  s.addNotes("Honesty here is more persuasive than claiming robustness. Stassin survives every weighting; the other two do not. The budget plateau is a real managerial insight — it tells a director to examine their constraints before asking for more money.");
}

// =============================================================== 12. TAKEAWAY
{
  const s = darkSlide();
  eyebrow(s, "The managerial takeaway", true);
  s.addText("Where analytics ends and judgement begins", {
    x: 0.7, y: 0.834, w: 11.9, h: 0.791, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 30, bold: true, color: WHITE });

  const steps = [
    ["Analytics screening", TEAL], ["Model explanation", TEAL],
    ["Risk assessment", TEAL], ["Portfolio optimisation", TEAL],
  ];
  const human = [["Scouting", AMBER], ["Medical · contract · tactical", AMBER],
                 ["Transfer committee decision", AMBER]];

  steps.forEach((st, i) => {
    const y = SY(1.6 + i * 0.62);
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 5.4, h: 0.565, rectRadius: 0.04,
      fill: { color: "1C3040" }, line: { color: "2A4356", width: 0.75 } });
    s.addText(st[0], { x: 1.0, y: y + 0.09, w: 4.8, h: 0.384, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, color: WHITE });
  });
  s.addShape(pres.ShapeType.rect, { x: 0.7, y: 4.97, w: 5.4, h: 0.023,
    fill: { color: AMBER }, line: { width: 0 } });
  s.addText("analytics ends here", { x: 0.7, y: 5.038, w: 5.4, h: 0.316, isTextBox: true,
    margin: 0, align: "center", fontFace: BODY, fontSize: 10, italic: true, color: AMBER });

  human.forEach((st, i) => {
    const y = SY(4.6 + i * 0.62);
    s.addShape(pres.ShapeType.roundRect, { x: 0.7, y, w: 5.4, h: 0.565, rectRadius: 0.04,
      fill: { color: "352B1C" }, line: { color: "5A4526", width: 0.75 } });
    s.addText(st[0], { x: 1.0, y: y + 0.09, w: 4.8, h: 0.384, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, color: "F0DFC4" });
  });

  s.addText("AI does not replace the recruitment committee.\nIt helps the committee investigate the right players for the right reasons.", {
    x: 6.7, y: 2.733, w: 5.9, h: 2.147, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 23, bold: true, color: WHITE, lineSpacing: 32 });
  s.addText("The project began by asking whether AI could find undervalued footballers. It ends with a more useful answer: a valuation model's disagreement with the market is a question to investigate, not an opportunity to exploit.", {
    x: 6.7, y: 5.106, w: 5.9, h: 1.469, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, color: "C9D4DA", lineSpacing: 19 });
  s.addNotes("Close on the line. Everything above the amber rule is reproducible, auditable and explicitly uncertain. Everything below requires information the system cannot obtain from public data — and saying so is what makes the tool trustworthy.");
}

pres.writeFile({ fileName: P("presentation", "M13A-25_Beyond_the_Price_Tag_Presentation.pptx") })
  .then(f => console.log("wrote", f));
