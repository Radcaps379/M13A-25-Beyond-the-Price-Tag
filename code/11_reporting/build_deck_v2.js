const path = require("path");
const REPO_ROOT = path.resolve(__dirname, "..", "..");

const C = require("./deck_core.js");

// ---------------------------------------------------------------------------
// SAFETY: these builders regenerate a SUBMITTED document in place. The author's
// updated table of contents and manual edits live only in the built file, so an
// accidental run would destroy them. Overwriting therefore requires an explicit
// opt-in.
if (!process.env.ALLOW_OVERWRITE_SUBMITTED) {
  console.error(
    "\nRefusing to overwrite a submitted document.\n" +
    "This script regenerates a deliverable in place and would discard the\n" +
    "table of contents and any manual edits it contains.\n\n" +
    "To rebuild deliberately:\n" +
    "    ALLOW_OVERWRITE_SUBMITTED=1 npm run <script>\n");
  process.exit(1);
}

const {
  pres, PITCH, PITCH2, CHALK, LINE, CYAN, CYAN_D, EMBER, FLARE, MUTE, PAPER, INK,
  SER, MON, SAN, HALF, pitchLines, dark, light, eyebrow, headline, rule, chip,
  figure, panel, footer,
} = C;

// ============================================================== 1. TITLE
{
  const s = dark();
  pitchLines(s, 25);                                  // brighter on the opener
  s.addText("Beyond the Price Tag", {
    x: 0.75, y: 2.25, w: 11.8, h: 1.5, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 60, bold: true, color: CHALK,
  });
  s.addText("An explainable AI decision-support system for football transfer-budget allocation", {
    x: 0.75, y: 3.72, w: 8.6, h: 0.8, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 17, color: MUTE, lineSpacing: 26,
  });
  let x = 0.75;
  [["Sports Analytics", CYAN], ["Capital Allocation", CYAN],
   ["Adversarial AI Workflow", EMBER]].forEach(([t, c]) => {
    x += chip(s, x, 4.75, t, c) + 0.22;
  });
  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 5.7, w: 2.6, h: 0.055,
    fill: { color: CYAN }, line: { width: 0 } });
  s.addText("Gudladona Venkata Rahul   ·   M13A-25   ·   MBA Marketing", {
    x: 0.75, y: 5.95, w: 8, h: 0.32, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 11, charSpacing: 1, color: CHALK });
  s.addText("Indian Institute of Management Ranchi   ·   Prof. Yelleti Vivek", {
    x: 0.75, y: 6.28, w: 8, h: 0.3, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 9.5, charSpacing: 1, color: MUTE });
  footer(s, true);
  s.addNotes("Beyond the Price Tag. A decision-support system for allocating a football club's transfer budget. The story: we set out to find undervalued players, tested that hypothesis properly, and what we found changed the system we built.");
}

// ============================================================== 2. PROBLEM
{
  const s = light();
  eyebrow(s, "The managerial problem");
  headline(s, "How should a club allocate a finite transfer budget\nwhen market value is informative but incomplete?", false,
           { size: 30, ls: 40 });
  rule(s, 2.5, CYAN_D);

  const items = [
    ["01", "Irreversible", "A fee is sunk. Wages persist for years. The squad slot is unavailable to anyone else."],
    ["02", "Constrained", "A budget cannot be exceeded, and five wingers do not solve a defensive problem."],
    ["03", "Partly hidden", "Contract, medical, tactical and personal information sit outside public data."],
    ["04", "Heterogeneous", "Performance means different things by position, league and age."],
  ];
  items.forEach((it, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.75 + col * 6.0, y = 3.0 + row * 1.75;
    s.addText(it[0], { x, y, w: 0.7, h: 0.5, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 26, bold: true, color: "C9D8E0" });
    s.addText(it[1], { x: x + 0.75, y: y + 0.04, w: 4.6, h: 0.36, isTextBox: true,
      margin: 0, fontFace: SER, fontSize: 17, bold: true, color: INK });
    s.addText(it[2], { x: x + 0.75, y: y + 0.44, w: 4.7, h: 0.9, isTextBox: true,
      margin: 0, fontFace: SAN, fontSize: 11.5, color: "41525E", lineSpacing: 16 });
  });
  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 6.4, w: 11.8, h: 0.02,
    fill: { color: "D8E2E8" }, line: { width: 0 } });
  s.addText("Recruitment resembles capital budgeting more than shopping, yet clubs decide one player at a time.", {
    x: 0.75, y: 6.5, w: 11.5, h: 0.36, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 14, italic: true, color: CYAN_D });
  footer(s, false);
  s.addNotes("Four properties shape the decision. The key line: recruitment is capital budgeting, but clubs treat the budget as a running balance rather than a portfolio to allocate.");
}

// ============================================================== 3. HYPOTHESIS
{
  const s = dark();
  eyebrow(s, "Where the project started", true);
  headline(s, "The original hypothesis", true);
  rule(s, 2.34, CYAN);

  const chain = ["Performance\nAge · Position\nTrajectory", "Model-implied\nvaluation",
                 "Valuation gap\nvs market", "Recruitment\nopportunity?"];
  chain.forEach((t, i) => {
    const x = 0.75 + i * 3.0;
    const last = i === 3;
    panel(s, x, 2.65, 2.5, 1.5, last ? EMBER : CYAN_D);
    s.addText(t, { x: x + 0.18, y: 2.72, w: 2.2, h: 1.36, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: SAN, fontSize: 12,
      bold: last, color: last ? EMBER : CHALK, lineSpacing: 16 });
    if (i < 3) s.addText("→", { x: x + 2.52, y: 3.18, w: 0.46, h: 0.45,
      isTextBox: true, margin: 0, align: "center", fontFace: SAN,
      fontSize: 18, color: CYAN_D });
  });

  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 4.72, w: 11.8, h: 1.6,
    fill: { color: PITCH2 }, line: { color: EMBER, width: 1 } });
  s.addText("Is the gap actually an opportunity?", {
    x: 1.15, y: 4.95, w: 11, h: 0.5, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 27, bold: true, color: CHALK });
  s.addText("If the market is wrong, the discrepancy is an opportunity. If the model is missing something, the same discrepancy is a warning. The two have opposite managerial implications, so we treated the claim as a hypothesis to test, not a premise to build on.", {
    x: 1.15, y: 5.5, w: 11, h: 0.7, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 12, color: "AFC4CF", lineSpacing: 17 });
  footer(s, true);
  s.addNotes("This is the logic the project began with. It is plausible and widely held. The critical question is whether the gap is opportunity or model error, and those point in opposite directions.");
}

// ============================================================== 4. DATA
{
  const s = light();
  eyebrow(s, "Data and analytical design");
  headline(s, "What the system was built on", false);
  rule(s, 2.34, CYAN_D);

  const stats = [["15,925", "PLAYER-SEASONS", "4,961 unique players"],
                 ["10", "SEASONS", "2015/16 to 2024/25"],
                 ["5", "LEAGUES", "England, Spain, Germany, Italy, France"],
                 ["1,508", "HELD-OUT PLAYERS", "2024/25, examined once"]];
  stats.forEach((st, i) => {
    const x = 0.75 + i * 3.05;
    s.addText(st[0], { x, y: 2.6, w: 2.9, h: 0.9, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 46, bold: true, color: i === 3 ? EMBER : INK });
    s.addText(st[1], { x, y: 3.5, w: 2.9, h: 0.28, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9.5, bold: true, charSpacing: 1.6, color: CYAN_D });
    s.addText(st[2], { x, y: 3.8, w: 2.8, h: 0.5, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 10.5, color: "5A6E7B", lineSpacing: 14 });
  });

  const flow = ["Data", "Model 0\ncontext", "Model 1\nfundamentals", "Model 2\nmarket-informed", "Back-test"];
  flow.forEach((t, i) => {
    const x = 0.75 + i * 2.42;
    const hero = i === 2;
    s.addShape(pres.ShapeType.rect, { x, y: 4.85, w: 2.05, h: 1.0,
      fill: { color: hero ? "E1F1F4" : "FFFFFF" },
      line: { color: hero ? CYAN_D : "D3DFE6", width: hero ? 1.5 : 1 } });
    s.addText(t, { x: x + 0.08, y: 4.9, w: 1.89, h: 0.9, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: SAN, fontSize: 11,
      bold: hero, color: hero ? CYAN_D : "41525E", lineSpacing: 14 });
    if (i < 4) s.addText("→", { x: x + 2.06, y: 5.12, w: 0.35, h: 0.4,
      isTextBox: true, margin: 0, align: "center", fontFace: SAN, fontSize: 15, color: "9DB2BF" });
  });
  s.addText("Train 2015/16 to 2021/22   ·   Validate 2022/23 to 2023/24   ·   Test 2024/25, once. Strictly time-based throughout.", {
    x: 0.75, y: 6.15, w: 11.8, h: 0.34, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 10, color: "6D8492" });
  footer(s, false);
  s.addNotes("One dataset, every join on integer IDs, no name matching anywhere. Strict time-based validation: no feature, threshold or constant was ever fitted using validation or test information.");
}

// ============================================================== 5. WHAT EXPLAINS VALUE
{
  const s = light();
  eyebrow(s, "Evidence 1");
  headline(s, "What explains market value?", false);
  rule(s, 2.34, CYAN_D);

  const bars = [["Model 0", "context only", 0.383, "9DB2BF"],
                ["Model 1", "+ fundamentals", 0.678, CYAN_D],
                ["Model 2", "+ prior market value", 0.884, EMBER]];
  bars.forEach((b, i) => {
    const y = 2.75 + i * 1.15;
    s.addText(b[0], { x: 0.75, y, w: 1.5, h: 0.32, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 16, bold: true, color: INK });
    s.addText(b[1], { x: 0.75, y: y + 0.34, w: 2.1, h: 0.28, isTextBox: true,
      margin: 0, fontFace: MON, fontSize: 9, color: "7C8F9B" });
    s.addShape(pres.ShapeType.rect, { x: 3.0, y: y + 0.02, w: 5.6, h: 0.5,
      fill: { color: "E6EDF1" }, line: { width: 0 } });
    s.addShape(pres.ShapeType.rect, { x: 3.0, y: y + 0.02, w: 5.6 * b[2], h: 0.5,
      fill: { color: b[3] }, line: { width: 0 } });
    s.addText(b[2].toFixed(3), { x: 8.75, y: y - 0.02, w: 1.2, h: 0.55,
      isTextBox: true, margin: 0, valign: "middle", fontFace: SER,
      fontSize: 24, bold: true, color: b[3] });
  });
  s.addText("TEST R²", { x: 3.0, y: 2.42, w: 2, h: 0.26, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.6, color: "8FA5B2" });

  s.addShape(pres.ShapeType.rect, { x: 10.2, y: 2.6, w: 2.35, h: 3.35,
    fill: { color: "FFFFFF" }, line: { color: "D3DFE6", width: 1 } });
  s.addShape(pres.ShapeType.rect, { x: 10.2, y: 2.6, w: 0.045, h: 3.35,
    fill: { color: EMBER }, line: { width: 0 } });
  s.addText("Two market-derived variables add 0.206, more than twenty-nine performance features contributed.", {
    x: 10.45, y: 2.85, w: 1.95, h: 1.5, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 11.5, color: "41525E", lineSpacing: 16 });
  s.addText("Model 2 is a benchmark, not the recruitment model.", {
    x: 10.45, y: 4.85, w: 1.95, h: 0.9, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 12.5, italic: true, bold: true, color: EMBER, lineSpacing: 16 });

  s.addText("Predicting the market is easier than explaining it, and the two are not the same objective.", {
    x: 0.75, y: 6.3, w: 11.8, h: 0.4, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 15, italic: true, color: CYAN_D });
  footer(s, false);
  s.addNotes("Held-out 2024/25, n=1,508, identical rows for all three models. Model 2 is not 'better': its residual is deviation from Transfermarkt's own persistence, which has no economic meaning. That is why Model 1 stays primary despite lower accuracy.");
}

// ============================================================== 6. THE TEST
{
  const s = dark();
  eyebrow(s, "Evidence 2, the hypothesis test", true);
  s.addText("Potential valuation discrepancy\n≠ proven market inefficiency", {
    x: 0.75, y: 1.35, w: 11.8, h: 1.7, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 38, bold: true, color: CHALK, lineSpacing: 50 });
  rule(s, 3.2, FLARE, 2.2);

  [["Raw residual", "Pre-registered", "p = 0.094"],
   ["Calibrated + screened", "Same procedure", "p = 0.307"]].forEach((t, i) => {
    const y = 3.7 + i * 1.15;
    panel(s, 0.75, y, 7.4, 0.95, FLARE);
    s.addText(t[0], { x: 1.1, y: y + 0.1, w: 3.2, h: 0.36, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 14, bold: true, color: CHALK });
    s.addText(t[1], { x: 1.1, y: y + 0.5, w: 3.2, h: 0.3, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9.5, color: MUTE });
    s.addText(t[2], { x: 4.6, y: y + 0.2, w: 2.0, h: 0.5, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 22, bold: true, color: EMBER });
    chip(s, 6.6, y + 0.28, "no advantage", MUTE, 1.4);
  });

  panel(s, 8.55, 3.7, 4.0, 2.4, CYAN);
  s.addText("Two specifications tested.\nThen we stopped.", {
    x: 8.9, y: 3.95, w: 3.4, h: 0.8, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 17, bold: true, color: CHALK, lineSpacing: 24 });
  s.addText("Thresholds fixed on validation, applied once to the held-out season. Iterating until significance appeared would have invalidated the test.", {
    x: 8.9, y: 4.85, w: 3.4, h: 1.1, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 11, color: "AFC4CF", lineSpacing: 15 });

  s.addText("The out-of-sample evidence did not support the hypothesis that the valuation residual identifies exploitable mispricing.", {
    x: 0.75, y: 6.4, w: 11.8, h: 0.45, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 14, italic: true, color: EMBER });
  footer(s, true);
  s.addNotes("This is the pivot of the project. A promising validation differential did not replicate on test, the signature of a signal that was noise. The discipline of stopping is what makes the negative result informative.");
}

// ============================================================== 7. EXIT RISK
{
  const s = light();
  eyebrow(s, "Evidence 3, the discovery");
  headline(s, "The residual was a risk signal, not an arbitrage signal", false, { size: 27, w: 11.0 });
  rule(s, 2.34, CYAN_D);

  [["3.7×", "THE EXIT RATE", "30.1% vs 8.2% benchmark", FLARE],
   ["0.732", "EXIT MODEL AUC", "held-out 2024/25, n = 1,508", CYAN_D],
   ["9.5×", "OBSERVED DECILE SPREAD", "7.3% lowest vs 69.5% highest", CYAN_D]].forEach((f, i) => {
    const x = 0.75 + i * 3.05;
    s.addText(f[0], { x, y: 2.55, w: 2.9, h: 0.95, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 46, bold: true, color: f[3] });
    s.addText(f[1], { x, y: 3.46, w: 2.9, h: 0.28, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.4, color: INK });
    s.addText(f[2], { x, y: 3.74, w: 2.85, h: 0.4, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 10.5, italic: true, color: "5A6E7B" });
  });
  s.addShape(pres.ShapeType.rect, { x: 9.95, y: 2.55, w: 2.6, h: 1.55,
    fill: { color: "FBECEA" }, line: { color: FLARE, width: 1 } });
  s.addText("p = 2.6 × 10⁻¹¹", { x: 10.1, y: 2.9, w: 2.3, h: 0.45, isTextBox: true,
    margin: 0, align: "center", fontFace: SER, fontSize: 19, bold: true, color: FLARE });
  s.addText("Fisher exact  ·  OR 4.82", { x: 10.1, y: 3.38, w: 2.3, h: 0.3,
    isTextBox: true, margin: 0, align: "center", fontFace: MON, fontSize: 9.5, color: "8A5049" });

  s.addChart(pres.ChartType.line, [
    { name: "Predicted", labels: ["1","2","3","4","5","6","7","8","9","10"],
      values: [5.2,10.4,15.5,19.4,23.0,29.1,35.4,43.6,53.7,69.6] },
    { name: "Actual", labels: ["1","2","3","4","5","6","7","8","9","10"],
      values: [7.3,11.3,17.9,23.8,30.5,25.8,36.0,39.1,55.0,69.5] },
  ], { x: 0.6, y: 4.35, w: 7.9, h: 1.95, chartColors: [CYAN_D, EMBER],
       showTitle: false, showLegend: true, legendPos: "t", legendFontSize: 10,
       lineSize: 2.5, lineDataSymbolSize: 5,
       catAxisTitle: "Risk decile", showCatAxisTitle: true, catAxisTitleFontSize: 9,
       valAxisTitle: "Exit rate (%)", showValAxisTitle: true, valAxisTitleFontSize: 9,
       catAxisLabelColor: "41525E", valAxisLabelColor: "7C8F9B",
       valGridLine: { color: "E6EDF1", size: 0.75 }, catGridLine: { style: "none" } });

  s.addShape(pres.ShapeType.rect, { x: 8.8, y: 4.35, w: 3.75, h: 1.95,
    fill: { color: "FFFFFF" }, line: { color: "D3DFE6", width: 1 } });
  s.addShape(pres.ShapeType.rect, { x: 8.8, y: 4.35, w: 0.045, h: 1.95,
    fill: { color: CYAN_D }, line: { width: 0 } });
  s.addText("Where a model disagrees with the market, the market is usually right", {
    x: 9.05, y: 4.55, w: 3.35, h: 0.75, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 14.5, bold: true, color: INK, lineSpacing: 19 });
  s.addText("A large unexplained gap more often signals information the market holds and public match data does not: contract, injury, role.", {
    x: 9.05, y: 5.35, w: 3.35, h: 0.85, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 11, color: "41525E", lineSpacing: 15 });
  footer(s, false);
  s.addNotes("The same diagnostic that invalidated the mispricing reading revealed a far stronger relationship running the other way. Calibration matters as much as discrimination: predicted and actual converge closely at both extremes.");
}

// ============================================================== 8. EXPLAINABILITY
{
  const s = light();
  eyebrow(s, "Explainable AI");
  headline(s, "Two different questions, two different answers", false, { size: 28 });
  rule(s, 2.34, CYAN_D);

  const card = (x, name, meta, q1, l1, q2, l2, note, noteCol) => {
    s.addShape(pres.ShapeType.rect, { x, y: 2.55, w: 5.75, h: 3.55,
      fill: { color: "FFFFFF" }, line: { color: "D3DFE6", width: 1 } });
    s.addText(name, { x: x + 0.3, y: 2.75, w: 5.2, h: 0.4, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 19, bold: true, color: INK });
    s.addText(meta, { x: x + 0.3, y: 3.15, w: 5.2, h: 0.3, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9.5, color: "7C8F9B" });
    s.addText(q1, { x: x + 0.3, y: 3.58, w: 5.2, h: 0.28, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.2, color: CYAN_D });
    s.addText(l1, { x: x + 0.3, y: 3.86, w: 5.2, h: 0.62, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 11, color: "41525E", lineSpacing: 15 });
    s.addText(q2, { x: x + 0.3, y: 4.56, w: 5.2, h: 0.28, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.2, color: EMBER });
    s.addText(l2, { x: x + 0.3, y: 4.84, w: 5.2, h: 0.42, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 11, color: "41525E" });
    s.addText(note, { x: x + 0.3, y: 5.3, w: 5.2, h: 0.65, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 11.5, italic: true, color: noteCol, lineSpacing: 15 });
  };
  card(0.75, "Facundo Buonanotte",
       "Midfield · Premier League · age 20 · market €20.0M · model €20.3M",
       "Why the model values him this way",
       "age +0.764  ·  goal contributions +0.137  ·  league context +0.344\nminutes −0.143  ·  squad rotation −0.082",
       "Why the optimizer selected him",
       "Quality 86th percentile · potential 0.77 · value efficiency 0.57",
       "His valuation gap is essentially zero. He was selected on quality and development potential, not on a bargain.",
       EMBER);
  card(6.8, "Diego Coppola",
       "Defender · Serie A · age 21 · market €10.0M · model €27.1M",
       "Why the model values him this way",
       "age +0.955  ·  league minutes +0.336  ·  height +0.138\ngoal contributions −0.179  ·  Serie A −0.155",
       "What the model does not know",
       "No contract length, injury history, scouting view. Exit probability 12.9%.",
       "Goal contributions LOWER a defender's implied value: the model reasons by position.",
       CYAN_D);

  s.addText("SHAP explains a number. The optimizer explains a choice.", {
    x: 0.75, y: 6.32, w: 11.8, h: 0.4, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 14, italic: true, color: "6D8492" });
  footer(s, false);
  s.addNotes("Buonanotte is the important example: model and market agree on his price, and he was still selected. That is the clearest proof the system is no longer a bargain-finder. Coppola shows position-appropriate reasoning.");
}

// ============================================================== 9. HERO
{
  const s = dark(false);
  pitchLines(s, 40);
  eyebrow(s, "The central inversion", true);
  s.addText("A large gap is only interesting when the risk is low", {
    x: 0.75, y: 0.86, w: 11.8, h: 0.6, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 29, bold: true, color: CHALK });
  rule(s, 1.52, CYAN, 2.2);

  const QX = 2.75, QY = 1.95, QW = 8.6, QH = 4.05;
  [[QX, QY, "High gap · Low risk", "POTENTIAL OPPORTUNITY", "investigate", CYAN, "0F2733"],
   [QX + QW/2, QY, "High gap · High risk", "WARNING", "the market likely knows something", FLARE, "2B1A1C"],
   [QX, QY + QH/2, "Low gap · Low risk", "BROADLY ALIGNED", "no action indicated", "AFC4CF", "0F2733"],
   [QX + QW/2, QY + QH/2, "Low gap · High risk", "RISK CAUTION", "retention concern", EMBER, "2B2318"],
  ].forEach(q => {
    s.addShape(pres.ShapeType.rect, { x: q[0], y: q[1], w: QW/2, h: QH/2,
      fill: { color: q[6] }, line: { color: LINE, width: 1 } });
    s.addText(q[2], { x: q[0] + 0.3, y: q[1] + 0.3, w: QW/2 - 0.6, h: 0.28,
      isTextBox: true, margin: 0, fontFace: MON, fontSize: 9.5, charSpacing: 1.2, color: MUTE });
    s.addText(q[3], { x: q[0] + 0.3, y: q[1] + 0.66, w: QW/2 - 0.6, h: 0.5,
      isTextBox: true, margin: 0, fontFace: SER, fontSize: 21, bold: true, color: q[5] });
    s.addText(q[4], { x: q[0] + 0.3, y: q[1] + 1.2, w: QW/2 - 0.6, h: 0.4,
      isTextBox: true, margin: 0, fontFace: SAN, fontSize: 11.5, color: "AFC4CF" });
  });
  s.addText("VALUATION GAP", { x: 0.85, y: QY + QH/2 - 0.18, w: 1.8, h: 0.3,
    isTextBox: true, margin: 0, align: "right", fontFace: MON, fontSize: 9.5,
    bold: true, charSpacing: 1.4, color: MUTE });
  s.addText("high ↑", { x: 0.85, y: QY + 0.15, w: 1.8, h: 0.28, isTextBox: true,
    margin: 0, align: "right", fontFace: MON, fontSize: 9, color: "44637A" });
  s.addText("↓ low", { x: 0.85, y: QY + QH - 0.42, w: 1.8, h: 0.28, isTextBox: true,
    margin: 0, align: "right", fontFace: MON, fontSize: 9, color: "44637A" });
  s.addText("←  lower exit risk                    EXIT RISK                    higher exit risk  →", {
    x: QX, y: QY + QH + 0.16, w: QW, h: 0.3, isTextBox: true, margin: 0,
    align: "center", fontFace: MON, fontSize: 9.5, bold: true, charSpacing: 1.2, color: MUTE });
  s.addText("The system never labels a player \u201cundervalued\u201d. It says: potential valuation discrepancy, investigate.", {
    x: 0.75, y: 6.55, w: 11.1, h: 0.36, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 13, italic: true, color: CYAN });
  footer(s, true);
  s.addNotes("This is the hero slide. Read the top-right quadrant carefully: a large valuation gap combined with high exit risk is the profile the naive approach would rank FIRST, and it is the one this system flags as a warning.");
}

// ============================================================== 10. SCENARIO
{
  const s = light();
  eyebrow(s, "Recruitment committee scenario");
  headline(s, "€50M, one defender, one midfielder, one attacker", false, { size: 28 });
  rule(s, 2.34, CYAN_D);

  s.addText(["PLAYER", "MARKET", "MODEL-IMPLIED", "QUALITY", "EXIT RISK"].join("      "), {
    x: 0.95, y: 2.5, w: 7.9, h: 0.26, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 8.5, bold: true, charSpacing: 1, color: "9DB2BF" });
  [["Lucas Stassin", "Attack · Ligue 1 · 20", "€18.0M", "€31.1M", "90th", "14%"],
   ["Diego Coppola", "Defender · Serie A · 21", "€10.0M", "€27.1M", "89th", "13%"],
   ["Facundo Buonanotte", "Midfield · Premier League · 20", "€20.0M", "€20.3M", "86th", "25%"],
  ].forEach((p, i) => {
    const y = 2.85 + i * 1.05;
    s.addShape(pres.ShapeType.rect, { x: 0.75, y, w: 8.4, h: 0.9,
      fill: { color: "FFFFFF" }, line: { color: "D3DFE6", width: 1 } });
    s.addShape(pres.ShapeType.rect, { x: 0.75, y, w: 0.04, h: 0.9,
      fill: { color: CYAN_D }, line: { width: 0 } });
    s.addText(p[0], { x: 1.0, y: y + 0.12, w: 2.8, h: 0.34, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 15, bold: true, color: INK });
    s.addText(p[1], { x: 1.0, y: y + 0.48, w: 2.9, h: 0.28, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 8.5, color: "7C8F9B" });
    s.addText(p[2], { x: 4.0, y: y + 0.26, w: 1.2, h: 0.38, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 13, color: "41525E" });
    s.addText(p[3], { x: 5.3, y: y + 0.26, w: 1.3, h: 0.38, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 15, bold: true, color: CYAN_D });
    s.addText(p[4], { x: 6.85, y: y + 0.26, w: 1.0, h: 0.38, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 13, color: "41525E" });
    s.addText(p[5], { x: 8.0, y: y + 0.26, w: 0.9, h: 0.38, isTextBox: true, margin: 0,
      fontFace: SER, fontSize: 15, bold: true, color: EMBER });
  });

  s.addShape(pres.ShapeType.rect, { x: 9.5, y: 2.85, w: 3.05, h: 3.1,
    fill: { color: "E1F1F4" }, line: { color: CYAN_D, width: 1 } });
  s.addText("€48.0M", { x: 9.75, y: 3.1, w: 2.6, h: 0.7, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 38, bold: true, color: CYAN_D });
  s.addText("COMMITTED OF €50M", { x: 9.75, y: 3.8, w: 2.6, h: 0.28, isTextBox: true,
    margin: 0, fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.2, color: "2A5966" });
  [["Mean quality percentile", "88.3"], ["Mean predicted exit risk", "17.1%"],
   ["Mean age", "20.4"]].forEach((r, i) => {
    s.addText(r[0], { x: 9.75, y: 4.3 + i * 0.36, w: 2.0, h: 0.3, isTextBox: true,
      margin: 0, fontFace: SAN, fontSize: 10.5, color: "3E5C66" });
    s.addText(r[1], { x: 11.6, y: 4.3 + i * 0.36, w: 0.8, h: 0.3, isTextBox: true,
      margin: 0, align: "right", fontFace: SER, fontSize: 12.5, bold: true, color: INK });
  });
  s.addText("Solved as an integer linear program under declared weights and constraints.", {
    x: 9.75, y: 5.42, w: 2.6, h: 0.45, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 9.5, italic: true, color: "5E7A85", lineSpacing: 12 });

  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 6.15, w: 11.8, h: 0.62,
    fill: { color: "FEF4E4" }, line: { color: EMBER, width: 1 } });
  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 6.15, w: 0.05, h: 0.62,
    fill: { color: EMBER }, line: { width: 0 } });
  s.addText("Illustrative application of a validated risk model, NOT optimizer validation. Three players cannot establish effectiveness.", {
    x: 1.1, y: 6.29, w: 11.2, h: 0.36, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 12.5, bold: true, color: "8A5F17" });
  footer(s, false);
  s.addNotes("Say the caveat out loud. The exit-risk model is validated at population level, n=1,508. This three-player portfolio demonstrates the method; it does not prove the method works.");
}

// ============================================================== 11. ROBUSTNESS
{
  const s = light();
  eyebrow(s, "Robustness and sensitivity");
  headline(s, "Would different assumptions change the answer?", false, { size: 28 });
  rule(s, 2.34, CYAN_D);

  s.addText("SELECTION STABILITY ACROSS SIX WEIGHT CONFIGURATIONS", {
    x: 0.75, y: 2.5, w: 6.2, h: 0.28, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 9, bold: true, charSpacing: 1.3, color: "8FA5B2" });
  [["Lucas Stassin", 6, CYAN_D], ["Diego Coppola", 4, CYAN_D],
   ["Facundo Buonanotte", 3, EMBER]].forEach((p, i) => {
    const y = 2.95 + i * 0.75;
    s.addText(p[0], { x: 0.75, y, w: 2.5, h: 0.35, isTextBox: true, margin: 0,
      fontFace: SAN, fontSize: 12.5, color: "41525E" });
    for (let k = 0; k < 6; k++) {
      s.addShape(pres.ShapeType.rect, { x: 3.4 + k * 0.44, y: y + 0.04, w: 0.34, h: 0.29,
        fill: { color: k < p[1] ? p[2] : "E6EDF1" }, line: { width: 0 } });
    }
    s.addText(`${p[1]} of 6`, { x: 6.15, y, w: 1.0, h: 0.35, isTextBox: true, margin: 0,
      fontFace: MON, fontSize: 11, bold: true, color: p[2] });
  });
  s.addText("Meaningful stability, not complete invariance. The core recommendation persists; the remainder shifts with managerial priorities.", {
    x: 0.75, y: 5.3, w: 6.3, h: 0.6, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 12.5, italic: true, color: "41525E", lineSpacing: 17 });

  s.addChart(pres.ChartType.line, [{ name: "Committed (€M)",
    labels: ["€20M", "€35M", "€50M", "€75M", "€100M"], values: [20, 34, 48, 52, 52] }],
    { x: 7.3, y: 2.6, w: 5.25, h: 2.6, chartColors: [CYAN_D],
      showTitle: true, title: "Spend plateaus as constraints bind",
      titleFontSize: 12, titleColor: INK, titleFontFace: SAN,
      showLegend: false, showValue: true, dataLabelPosition: "t",
      dataLabelFontSize: 10, dataLabelColor: "41525E",
      lineSize: 2.5, lineDataSymbolSize: 6,
      catAxisLabelColor: "41525E", valAxisLabelColor: "7C8F9B",
      valGridLine: { color: "E6EDF1", size: 0.75 }, catGridLine: { style: "none" } });
  s.addText("Beyond about €75M more budget buys nothing: the quality, age, risk and confidence constraints bind before the money does. Relaxing a constraint may be worth more than raising the budget.", {
    x: 7.3, y: 5.3, w: 5.25, h: 0.8, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 11, color: "41525E", lineSpacing: 15 });

  s.addText("A property of the model's eligible universe, not evidence of a €52M optimum in the real transfer market.", {
    x: 0.75, y: 6.4, w: 11.8, h: 0.36, isTextBox: true, margin: 0,
    fontFace: MON, fontSize: 10, color: "8FA5B2" });
  footer(s, false);
  s.addNotes("Honesty here is more persuasive than claiming robustness. Stassin survives every weighting; the other two do not. The budget plateau tells a director to examine their constraints before asking for more money.");
}

// ============================================================== 12. TAKEAWAY
{
  const s = dark();
  eyebrow(s, "The managerial takeaway", true);
  s.addText("Where analytics ends and judgement begins", {
    x: 0.75, y: 0.9, w: 11.8, h: 0.75, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 32, bold: true, color: CHALK });
  rule(s, 1.82, CYAN, 2.2);

  ["Analytics screening", "Model explanation", "Risk assessment", "Portfolio optimisation"]
    .forEach((t, i) => {
      const y = 2.25 + i * 0.66;
      panel(s, 0.75, y, 5.3, 0.54, CYAN_D);
      s.addText(t, { x: 1.1, y: y + 0.11, w: 4.7, h: 0.34, isTextBox: true, margin: 0,
        fontFace: SAN, fontSize: 13, color: CHALK });
    });
  s.addShape(pres.ShapeType.rect, { x: 0.75, y: 5.0, w: 5.3, h: 0.025,
    fill: { color: EMBER }, line: { width: 0 } });
  s.addText("ANALYTICS ENDS HERE", { x: 0.75, y: 5.09, w: 5.3, h: 0.3, isTextBox: true,
    margin: 0, align: "center", fontFace: MON, fontSize: 9, bold: true,
    charSpacing: 2, color: EMBER });
  ["Scouting", "Medical · contract · tactical", "Transfer committee decision"]
    .forEach((t, i) => {
      const y = 5.5 + i * 0.55;
      s.addShape(pres.ShapeType.rect, { x: 0.75, y, w: 5.3, h: 0.45,
        fill: { color: "2B2318" }, line: { color: "5A4526", width: 1 } });
      s.addShape(pres.ShapeType.rect, { x: 0.75, y, w: 0.045, h: 0.45,
        fill: { color: EMBER }, line: { width: 0 } });
      s.addText(t, { x: 1.1, y: y + 0.07, w: 4.7, h: 0.32, isTextBox: true, margin: 0,
        fontFace: SAN, fontSize: 12.5, color: "F0DFC4" });
    });

  s.addText("AI does not replace the recruitment committee.\nIt helps the committee investigate the right players for the right reasons.", {
    x: 6.95, y: 2.6, w: 5.6, h: 2.0, isTextBox: true, margin: 0,
    fontFace: SER, fontSize: 23, bold: true, color: CHALK, lineSpacing: 33 });
  s.addShape(pres.ShapeType.rect, { x: 6.95, y: 4.85, w: 2.0, h: 0.045,
    fill: { color: CYAN }, line: { width: 0 } });
  s.addText("The project began by asking whether AI could find undervalued footballers. It ends with a more useful answer: a valuation model's disagreement with the market is a question to investigate, not an opportunity to exploit.", {
    x: 6.95, y: 5.1, w: 5.6, h: 1.4, isTextBox: true, margin: 0,
    fontFace: SAN, fontSize: 12.5, color: "AFC4CF", lineSpacing: 19 });
  footer(s, true);
  s.addNotes("Close on the line. Everything above the amber rule is reproducible, auditable and explicitly uncertain. Everything below requires information the system cannot obtain from public data, and saying so is what makes the tool trustworthy.");
}

pres.writeFile({ fileName: path.join(REPO_ROOT, "presentation",
                                    "M13A-25_Beyond_the_Price_Tag_Presentation.pptx") })
  .then(f => console.log("wrote", f));
