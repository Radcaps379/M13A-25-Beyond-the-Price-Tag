const path = require("path");
// Repository root, derived from this file's location rather than an absolute
// path belonging to the machine the project was built on.
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const P = (...p) => path.join(REPO_ROOT, ...p);

/**
 * Build the Prompt Logbook as a properly formatted .docx.
 *
 * Typography matches the main report (Times New Roman, A4, justified, 1.5
 * spacing) so the two documents read as one submission. Restraint is
 * deliberate: a single dark rule under section headings, bordered tables with a
 * light header band, and a left rule on quoted passages. No colour beyond a
 * near-black and two greys.
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
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, Footer,
  PageNumber, convertInchesToTwip, TabStopType,
} = require("docx");

const SRC = P("report", "prompt_logbook", "M13A-25_Prompt_Logbook.md");
const OUT = P("report", "prompt_logbook", "M13A-25_Prompt_Logbook.docx");

const FONT = "Times New Roman";
const MONO = "Consolas";
const INK = "1A1A1A";
const GREY = "595959";
const LIGHT = "BFBFBF";
const BAND = "ECECEC";

const children = [];
const B = (n = 1) => Array.from({ length: n }, () =>
  new Paragraph({ spacing: { after: 0, line: 240 }, children: [new TextRun("")] }));

/** inline markdown -> runs */
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last)
      out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: 22, color: INK, ...base }));
    const t = m[0];
    if (t.startsWith("**"))
      out.push(new TextRun({ text: t.slice(2, -2), font: FONT, size: 22, bold: true, color: INK, ...base }));
    else if (t.startsWith("`"))
      out.push(new TextRun({ text: t.slice(1, -1), font: MONO,
                             size: (base.size === 21 ? 16 : 19), color: INK, ...base }));
    else
      out.push(new TextRun({ text: t.slice(1, -1), font: FONT, size: 22, italics: true, color: INK, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length)
    out.push(new TextRun({ text: text.slice(last), font: FONT, size: 22, color: INK, ...base }));
  return out.length ? out : [new TextRun({ text, font: FONT, size: 22, color: INK, ...base })];
}

const body = (t, opts = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED,
  spacing: { after: opts.after ?? 150, line: 300 },
  indent: opts.indent,
  children: runs(t),
});

// ---------------------------------------------------------------- title block
children.push(new Paragraph({
  spacing: { after: 60 },
  children: [new TextRun({ text: "PROMPT LOGBOOK", font: FONT, size: 20, bold: true,
                           color: GREY, characterSpacing: 60 })],
}));
children.push(new Paragraph({
  spacing: { after: 120 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: INK, space: 6 } },
  children: [new TextRun({ text: "Beyond the Price Tag", font: FONT, size: 40, bold: true, color: INK })],
}));
children.push(new Paragraph({
  spacing: { after: 300 },
  children: [new TextRun({ text: "How I directed, verified and adjudicated the AI systems used to build this project",
                           font: FONT, size: 24, italics: true, color: GREY })],
}));

[["Author", "Gudladona Venkata Rahul"],
 ["Registration ID", "M13A-25"],
 ["Programme", "MBA (Marketing), Indian Institute of Management Ranchi"],
 ["Subject", "Sports Analytics"],
 ["Subject Guide", "Prof. Yelleti Vivek"],
 ["Date", "5th September 2026"]].forEach(([k, v]) => {
  children.push(new Paragraph({
    spacing: { after: 40, line: 260 },
    tabStops: [{ type: TabStopType.LEFT, position: convertInchesToTwip(1.9) }],
    children: [
      new TextRun({ text: k, font: FONT, size: 20, color: GREY }),
      new TextRun({ text: "\t", font: FONT, size: 20 }),
      new TextRun({ text: v, font: FONT, size: 22, bold: true, color: INK }),
    ],
  }));
});
children.push(...B(1));
children.push(new Paragraph({
  spacing: { before: 200, after: 0 },
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: LIGHT, space: 8 } },
  children: [new TextRun("")],
}));
children.push(new Paragraph({ children: [new PageBreak()] }));

// ---------------------------------------------------------------- table build
function makeTable(rows) {
  const clean = rows.filter(r => !/^\|[\s:|-]+\|$/.test(r.trim()));
  const cells = clean.map(r => r.trim().replace(/^\||\|$/g, "").split("|").map(c => c.trim()));
  const nCol = Math.max(...cells.map(c => c.length));
  const TOTAL = 9200;
  // first column a little wider: it usually carries the label
  const w = [];
  if (nCol === 5) {
    // decision-ownership table: last column carries artifact filenames
    [0.17, 0.18, 0.17, 0.23, 0.25].forEach(f => w.push(Math.round(TOTAL * f)));
  } else if (nCol >= 3) {
    w.push(Math.round(TOTAL * 0.22));
    const rest = Math.floor((TOTAL - w[0]) / (nCol - 1));
    for (let i = 1; i < nCol; i++) w.push(rest);
  } else {
    const each = Math.floor(TOTAL / nCol);
    for (let i = 0; i < nCol; i++) w.push(each);
  }
  w[nCol - 1] = TOTAL - w.slice(0, nCol - 1).reduce((a, b) => a + b, 0);

  const edge = { style: BorderStyle.SINGLE, size: 4, color: LIGHT };
  const head = { style: BorderStyle.SINGLE, size: 10, color: INK };

  return new Table({
    width: { size: TOTAL, type: WidthType.DXA },
    columnWidths: w,
    borders: { top: head, bottom: head, left: edge, right: edge,
               insideHorizontal: edge, insideVertical: edge },
    rows: cells.map((row, ri) => new TableRow({
      tableHeader: ri === 0,
      children: Array.from({ length: nCol }, (_, ci) => new TableCell({
        width: { size: w[ci], type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: BAND } : undefined,
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        borders: ri === 0 ? { bottom: head } : undefined,
        children: [new Paragraph({
          spacing: { after: 0, line: 250 },
          children: runs(row[ci] || "", ri === 0 ? { bold: true, size: 21 } : { size: 21 }),
        })],
      })),
    })),
  });
}

// ---------------------------------------------------------------- parse body
const md = fs.readFileSync(SRC, "utf8");
const start = md.indexOf("## 1. My role and project-control philosophy");
const lines = md.slice(start).split("\n");
let tbl = null;

const flush = () => {
  if (tbl && tbl.length >= 2) {
    children.push(makeTable(tbl));
    children.push(new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }));
  }
  tbl = null;
};

for (let i = 0; i < lines.length; i++) {
  const ln = lines[i].trim();

  if (ln.startsWith("|")) { (tbl ||= []).push(ln); continue; }
  if (tbl) flush();
  if (!ln || ln === "---") continue;

  let m;
  if ((m = ln.match(/^##\s+(.*)$/))) {
    // major section: rule above, generous space
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_1,
      spacing: { before: 480, after: 200 },
      keepNext: true,
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: INK, space: 6 } },
      children: [new TextRun({ text: m[1].replace(/\*\*/g, ""), font: FONT, size: 28, bold: true, color: INK })],
    }));
  } else if ((m = ln.match(/^###\s+(.*)$/))) {
    children.push(new Paragraph({
      heading: HeadingLevel.HEADING_2,
      spacing: { before: 320, after: 140 },
      keepNext: true,
      children: [new TextRun({ text: m[1].replace(/\*\*/g, ""), font: FONT, size: 24, bold: true, color: INK })],
    }));
  } else if (ln.startsWith("```")) {
    // flow diagram: monospace inside a shaded, ruled block
    const buf = [];
    while (i + 1 < lines.length && !lines[i + 1].trim().startsWith("```")) buf.push(lines[++i]);
    i++;
    buf.forEach((t, k) => children.push(new Paragraph({
      spacing: { after: 0, line: 240, before: k === 0 ? 120 : 0 },
      indent: { left: convertInchesToTwip(0.5) },
      shading: { type: ShadingType.CLEAR, fill: "F5F5F5" },
      border: { left: { style: BorderStyle.SINGLE, size: 10, color: LIGHT, space: 10 } },
      children: [new TextRun({ text: t.replace(/^ {0,4}/, ""), font: MONO, size: 18, color: INK })],
    })));
    children.push(new Paragraph({ spacing: { after: 200 }, children: [new TextRun("")] }));
  } else if (ln.startsWith(">")) {
    children.push(new Paragraph({
      alignment: AlignmentType.LEFT,
      spacing: { before: 140, after: 180, line: 290 },
      indent: { left: convertInchesToTwip(0.45), right: convertInchesToTwip(0.35) },
      border: { left: { style: BorderStyle.SINGLE, size: 14, color: GREY, space: 14 } },
      children: runs(ln.replace(/^>\s?/, ""), { italics: true }),
    }));
  } else if ((m = ln.match(/^[-*]\s+(.*)$/))) {
    children.push(new Paragraph({
      bullet: { level: 0 },
      spacing: { after: 80, line: 280 },
      indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.22) },
      children: runs(m[1]),
    }));
  } else if ((m = ln.match(/^(\d+)\.\s+(.*)$/))) {
    children.push(new Paragraph({
      spacing: { after: 80, line: 280 },
      indent: { left: convertInchesToTwip(0.5), hanging: convertInchesToTwip(0.28) },
      children: runs(`${m[1]}.  ${m[2]}`),
    }));
  } else {
    children.push(body(ln));
  }
}
flush();

// ---------------------------------------------------------------- document
const doc = new Document({
  creator: "Gudladona Venkata Rahul",
  title: "Prompt Logbook - Beyond the Price Tag",
  styles: {
    default: { document: { run: { font: FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 28, bold: true, color: INK },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 24, bold: true, color: INK },
        paragraph: { spacing: { before: 300, after: 140 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1700 },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 120 },
          children: [
            new TextRun({ text: "Prompt Logbook   ·   ", font: FONT, size: 17, color: GREY }),
            new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 17, color: GREY }),
          ],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync(OUT, b);
  console.log("wrote", OUT, (b.length / 1024).toFixed(0) + " KB");
});
