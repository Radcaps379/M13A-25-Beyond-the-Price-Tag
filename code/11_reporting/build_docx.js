const path = require("path");
// Repository root, derived from this file's location rather than an absolute
// path belonging to the machine the project was built on.
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const repoPath = (...p) => path.join(REPO_ROOT, ...p);

/**
 * Build the final IIM Ranchi project report as a .docx.
 *
 * Source of truth: Beyond_the_Price_Tag_REPORT.md (assembled + audited).
 * Front matter is laid out to match the institute's supplied template:
 * title page, declaration, certificate, abstract, contents, then Sections 1-10.
 */
const fs = require("fs");

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
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  PageBreak, Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  TableOfContents, Header, Footer, PageNumber, convertInchesToTwip,
} = require("docx");

const SRC = repoPath("report", "final", "Beyond_the_Price_Tag_REPORT.md");
const OUT = repoPath("report", "final", "M13A-25_Beyond_the_Price_Tag_Report.docx");

const NAME = "Gudladona Venkata Rahul";
const REGN = "M13A-25";
const SPEC = "Marketing";
const PLACE = "Ranchi";
const DATE = "5th September 2026";
const TITLE =
  "Beyond the Price Tag: An Explainable AI Decision-Support System for " +
  "Identifying Undervalued Talent and Optimizing Football Transfer Budgets";

const FONT = "Times New Roman";
const children = [];

// ---------------------------------------------------------------- helpers
const P = (text, opts = {}) =>
  new Paragraph({
    alignment: opts.align || AlignmentType.JUSTIFIED,
    spacing: { after: opts.after ?? 160, line: opts.line ?? 300 },
    indent: opts.indent,
    children: [new TextRun({
      text, font: FONT, size: opts.size || 22,
      bold: opts.bold, italics: opts.italics, allCaps: opts.caps,
    })],
  });

const CENTER = (text, opts = {}) => P(text, { ...opts, align: AlignmentType.CENTER });
const BLANK = (n = 1) => Array.from({ length: n }, () => P(""));
const BREAK = () => new Paragraph({ children: [new PageBreak()] });

/** Inline markdown (**bold**, *italic*, `code`) -> TextRuns */
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: 22, ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), font: FONT, size: 22, bold: true, ...base }));
    else if (t.startsWith("`")) out.push(new TextRun({ text: t.slice(1, -1), font: "Consolas", size: 20, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), font: FONT, size: 22, italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: 22, ...base }));
  return out.length ? out : [new TextRun({ text, font: FONT, size: 22, ...base })];
}

const body = (text, opts = {}) =>
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { after: 160, line: 300 },
    indent: opts.indent,
    children: runs(text),
  });

// ================================================================ TITLE PAGE
children.push(...BLANK(2));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { after: 400, line: 340 },
  children: [new TextRun({ text: TITLE, font: FONT, size: 32, bold: true })],
}));
children.push(...BLANK(2));
children.push(CENTER("Project Submitted to the", { size: 24 }));
children.push(CENTER("Indian Institute of Management Ranchi", { size: 26, bold: true }));
children.push(...BLANK(1));
children.push(CENTER("Masters of Business Administration", { size: 24 }));
children.push(CENTER("in", { size: 24, italics: true }));
children.push(CENTER(SPEC, { size: 24, bold: true }));
children.push(...BLANK(1));
children.push(CENTER("submitted by", { size: 24 }));
children.push(CENTER(`${NAME}, ${REGN}`, { size: 24, bold: true }));
children.push(...BLANK(1));
children.push(CENTER("Under the Guidance of", { size: 24 }));
children.push(CENTER("Prof. Yelleti Vivek", { size: 24, bold: true }));
children.push(...BLANK(3));
children.push(CENTER("Area of Information Systems and Business Analytics", { size: 22 }));
children.push(CENTER("Indian Institute of Management Ranchi,", { size: 22 }));
children.push(CENTER("Ranchi, Jharkhand - 835 303", { size: 22 }));
children.push(...BLANK(1));
children.push(CENTER("September 2026", { size: 24, bold: true }));
children.push(BREAK());

// ================================================================ DECLARATION
children.push(...BLANK(1));
children.push(CENTER("DECLARATION", { size: 28, bold: true, after: 360 }));
children.push(body(
  `I undersigned hereby declare that the project report entitled "${TITLE}" ` +
  `submitted as part of the requirements for the Sports Analytics subject at ` +
  `IIM Ranchi, is a bonafide work carried out by me under the supervision of ` +
  `Dr. Vivek Yelleti.`));
children.push(body(
  "In the preparation of this report, I have responsibly leveraged Artificial " +
  "Intelligence tools and techniques to support analysis, modeling, and drafting. " +
  "The use of AI was restricted to augmenting my own effort, and the intellectual " +
  "contributions, interpretations, and conclusions presented herein are my own. " +
  "Where ideas, words, or outputs generated by AI or other sources have been " +
  "included, I have adequately and accurately cited and referenced the original " +
  "sources."));
children.push(body(
  "I further declare that I have adhered to the ethics of academic honesty and " +
  "integrity, and have not misrepresented or fabricated any data, idea, fact, or " +
  "source in my submission. I understand that any violation of the above will be " +
  "a cause for disciplinary action by the Institute, and may also evoke penal " +
  "action from the sources which have not been properly cited or from whom proper " +
  "permission has not been obtained."));
children.push(body(
  "This report has not previously formed the basis for the completion of any " +
  "other subject or project in any other institution."));
children.push(...BLANK(2));
children.push(new Paragraph({
  spacing: { after: 300 },
  children: [new TextRun({ text: `Place : ${PLACE}`, font: FONT, size: 22 }),
             new TextRun({ text: "\t\t\t\t", font: FONT, size: 22 }),
             new TextRun({ text: `Date : ${DATE}`, font: FONT, size: 22 })],
}));
children.push(...BLANK(2));
children.push(new Paragraph({
  spacing: { after: 200 },
  children: [new TextRun({ text: `Name of student : ${NAME}`, font: FONT, size: 22 }),
             new TextRun({ text: "\t\t", font: FONT, size: 22 }),
             new TextRun({ text: "Signature : ..................", font: FONT, size: 22 })],
}));
children.push(BREAK());

// ================================================================ CERTIFICATE
children.push(...BLANK(1));
children.push(CENTER("Area of Information Systems and Business Analytics", { size: 22 }));
children.push(CENTER("Indian Institute of Management Ranchi,", { size: 22 }));
children.push(CENTER("Ranchi, Jharkhand - 835 303", { size: 22, after: 400 }));
children.push(CENTER("CERTIFICATE", { size: 28, bold: true, after: 360 }));
children.push(body(
  `This is to certify that the report entitled "${TITLE}" submitted by ${NAME} ` +
  `for the Sports Analytics Subject to the Indian Institute of Management Ranchi ` +
  `is a bonafide record of the project work carried out under my/our guidance and ` +
  `supervision. This report in any form has not been submitted to any other ` +
  `University or Institute for any purpose.`));
children.push(...BLANK(3));
children.push(P("Subject Guide", { align: AlignmentType.RIGHT, after: 200 }));
children.push(P("Name: Dr. Vivek Yelleti", { align: AlignmentType.RIGHT, after: 200 }));
children.push(P("Signature: .......................", { align: AlignmentType.RIGHT }));
children.push(BREAK());

// ================================================================ ABSTRACT
children.push(...BLANK(1));
children.push(CENTER("ABSTRACT", { size: 28, bold: true, after: 360 }));
[
  "Football clubs commit substantial and largely irreversible capital to the transfer market under conditions of imperfect information. This project asked whether observable performance data could support a defensible valuation framework, and whether the gap between a fundamentals-based valuation and the market's own price could identify recruitment opportunities a club could act on. That question was treated as a hypothesis to be tested rather than a premise to be assumed.",
  "Using 15,925 player-seasons across five major European leagues from 2015/16 to 2024/25, a valuation model combining performance, age, position, league and career trajectory achieved an R-squared of 0.678 on a held-out season in a season-normalised framework, against 0.383 for a context-only benchmark. Observable football carries substantial valuation signal. However, the study did not find sufficient out-of-sample evidence to support the hypothesis that the resulting valuation residual represents systematically exploitable market mispricing: two pre-specified signal definitions were tested under strict time-based discipline and neither produced a significant subsequent appreciation advantage.",
  "The same residual instead proved strongly associated with subsequent exit from top-five football. Flagged players left at 3.7 times the benchmark rate, and a dedicated exit-risk model achieved an out-of-sample AUC of 0.732 with strong calibration. The system was accordingly redesigned around this evidence: a risk-aware constrained optimizer allocates a transfer budget on position-appropriate quality, development potential and value efficiency, penalised by validated exit risk and model uncertainty. Explainability separates why the model produced a valuation from why the optimizer selected a player, and a guarded generative-AI layer converts validated outputs into committee briefs subject to automated fidelity checks.",
  "The contribution is the evidence-driven transition from player valuation to risk-aware recruitment decision support. The residual proved to be a warning signal rather than an arbitrage signal: a model's disagreement with the market is shown to be a question warranting investigation rather than an opportunity to exploit, and the resulting system is positioned as a screening and investigation tool rather than an autonomous decision-maker.",
].forEach(t => children.push(body(t)));
children.push(...BLANK(1));
children.push(new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 160, line: 300 },
  children: [new TextRun({ text: "Keywords: ", font: FONT, size: 22, bold: true }),
             new TextRun({ text: "player valuation, transfer market, explainable AI, SHAP, constrained optimisation, decision support, market efficiency, sports analytics", font: FONT, size: 22, italics: true })],
}));
children.push(BREAK());

// ================================================================ CONTENTS
children.push(...BLANK(1));
children.push(CENTER("CONTENTS", { size: 28, bold: true, after: 300 }));
children.push(new Paragraph({
  spacing: { after: 200 },
  children: [new TextRun({ text: "Right-click and select \"Update Field\" to populate page numbers.", font: FONT, size: 18, italics: true, color: "666666" })],
}));
children.push(new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-3" }));
children.push(BREAK());

// ================================================================ BODY
const md = fs.readFileSync(SRC, "utf8");
// Skip the front matter already laid out above; start at Section 1.
const start = md.indexOf("# 1. Introduction");
const lines = md.slice(start).split("\n");

let i = 0, tableBuf = null;

function flushTable() {
  if (!tableBuf || tableBuf.length < 2) { tableBuf = null; return; }
  const rows = tableBuf.filter(r => !/^\|[\s:|-]+\|$/.test(r.trim()));
  const cells = rows.map(r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim()));
  const nCol = Math.max(...cells.map(c => c.length));
  const TOTAL = 9360;                                   // 6.5" usable width
  const colW = Math.floor(TOTAL / nCol);
  const widths = Array(nCol).fill(colW);
  widths[nCol - 1] = TOTAL - colW * (nCol - 1);

  children.push(new Table({
    width: { size: TOTAL, type: WidthType.DXA },
    columnWidths: widths,
    rows: cells.map((row, ri) => new TableRow({
      tableHeader: ri === 0,
      children: Array.from({ length: nCol }, (_, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: "E8E8E8" } : undefined,
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({
          spacing: { after: 0, line: 260 },
          children: runs((row[ci] || "").replace(/<br>/g, " "), { bold: ri === 0 }),
        })],
      })),
    })),
  }));
  children.push(P("", { after: 160 }));
  tableBuf = null;
}

for (; i < lines.length; i++) {
  const raw = lines[i];
  const ln = raw.trim();

  if (ln.startsWith("|")) { (tableBuf ||= []).push(ln); continue; }
  if (tableBuf) flushTable();

  if (!ln || ln === "---") continue;

  let m;
  if ((m = ln.match(/^#\s+(.*)$/))) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_1, pageBreakBefore: true,
      spacing: { before: 240, after: 240 },
      children: [new TextRun({ text: m[1].replace(/\*\*/g, ""), font: FONT, size: 30, bold: true })],
    }));
  } else if ((m = ln.match(/^##\s+(.*)$/))) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 },
      children: [new TextRun({ text: m[1].replace(/\*\*/g, ""), font: FONT, size: 26, bold: true })],
    }));
  } else if ((m = ln.match(/^###\s+(.*)$/))) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_3, spacing: { before: 240, after: 140 },
      children: [new TextRun({ text: m[1].replace(/\*\*/g, ""), font: FONT, size: 24, bold: true })],
    }));
  } else if (ln.startsWith(">")) {
    children.push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      spacing: { before: 120, after: 180, line: 300 },
      indent: { left: convertInchesToTwip(0.4), right: convertInchesToTwip(0.3) },
      border: { left: { style: BorderStyle.SINGLE, size: 12, color: "888888", space: 12 } },
      children: runs(ln.replace(/^>\s?/, ""), { italics: true }),
    }));
  } else if ((m = ln.match(/^[-*]\s+(.*)$/))) {
    children.push(new Paragraph({
      bullet: { level: 0 },
      spacing: { after: 90, line: 280 },
      indent: { left: convertInchesToTwip(0.45), hanging: convertInchesToTwip(0.2) },
      children: runs(m[1]),
    }));
  } else if ((m = ln.match(/^(\d+)\.\s+(.*)$/))) {
    children.push(new Paragraph({
      spacing: { after: 90, line: 280 },
      indent: { left: convertInchesToTwip(0.45), hanging: convertInchesToTwip(0.25) },
      children: runs(`${m[1]}.  ${m[2]}`),
    }));
  } else if (ln.startsWith("```")) {
    while (i + 1 < lines.length && !lines[i + 1].trim().startsWith("```")) {
      i++;
      children.push(new Paragraph({
        spacing: { after: 0, line: 240 },
        indent: { left: convertInchesToTwip(0.35) },
        children: [new TextRun({ text: lines[i], font: "Consolas", size: 18 })],
      }));
    }
    i++;
    children.push(P("", { after: 140 }));
  } else {
    children.push(body(ln));
  }
}
if (tableBuf) flushTable();

// ================================================================ DOCUMENT
const doc = new Document({
  creator: NAME, title: TITLE, description: "IIM Ranchi Sports Analytics project report",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 30, bold: true, color: "000000" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: "000000" },
        paragraph: { spacing: { before: 280, after: 160 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: "000000" },
        paragraph: { spacing: { before: 240, after: 140 }, outlineLevel: 2 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },                 // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1700 },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("wrote", OUT, (buf.length / 1024).toFixed(0) + " KB");
});
