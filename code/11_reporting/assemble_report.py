"""
Assemble the full report from the frozen sections into the IIM template order,
renumbering sub-sections as the frozen skeleton specifies:

    3.x -> 6.x   (Design and Methodology)
    4.x -> 7.x   (Results and Discussion)
    5.x -> 8.x   (Analysis)
    6.x -> 9.x   (Conclusion)

Dataset Description is promoted out of Methodology to become Section 5, matching
the template's contents page.

Writes: Beyond_the_Price_Tag_REPORT.md
"""

# --- repository paths -------------------------------------------------------
# Resolved from this file's location so the script runs from a clean clone,
# from any working directory. See code/repo_paths.py.
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from repo_paths import ROOT, RAW, PROC, OUTPUTS, FIGURES, BRIEFS, find, stage_dir, ensure_dirs
ensure_dirs()
FIG = FIGURES
STAGE_OUT = PROC

import re
from pathlib import Path

DEST = ROOT / "report" / "final" / "Beyond_the_Price_Tag_REPORT.md"


def strip_scaffold(txt):
    """Remove the per-file title block, drafting-status notes and rules."""
    lines = txt.split("\n")
    keep, skipping = [], False
    for ln in lines:
        if ln.startswith("# ") or ln.startswith("### *Beyond"):
            continue                                   # per-file H1 / subtitle
        if ln.startswith("> **Drafting status") or ln.startswith("> **Note.**"):
            skipping = True; continue
        if skipping:
            if ln.strip() == "" or ln.startswith(">"):
                if ln.strip() == "": skipping = False
                continue
            skipping = False
        if ln.strip() == "---" and not keep:
            continue
        keep.append(ln)
    return "\n".join(keep).strip()


def renumber(txt, old, new):
    """
    Shift section numbers, e.g. 3.4 -> 6.4, in HEADINGS and EXPLICIT references
    only.

    An earlier version carried a fourth, unanchored substitution intended to
    catch bare references. It matched any decimal number and silently corrupted
    the data: "odds ratio 4.82" became "odds ratio 7.82" and a distribution skew
    of 3.90 became 6.90. Numbers in prose must never be touched by a
    section-renumbering pass, so that rule is deliberately absent.
    """
    txt = re.sub(rf"(?m)^(#{{2,4}}\s*){old}\.(\d+)", rf"\g<1>{new}.\g<2>", txt)
    txt = re.sub(rf"\b§{old}\.(\d+)", rf"§{new}.\1", txt)
    txt = re.sub(rf"\bSection {old}\.(\d+)", rf"Section {new}.\1", txt)
    return txt


parts = []

# ---- FRONT MATTER ----------------------------------------------------------
parts.append(strip_scaffold(find("report_front_matter_SUBMISSION.md").read_text()))

# ---- SECTIONS 1-4 ----------------------------------------------------------
intro = strip_scaffold(find("report_sections1_2_intro.md").read_text())
# split the bundled Section 2 into template sections 2, 3 and 4
intro = intro.replace("# Section 2 — Problem Statement, Motivation and Novelty", "")
intro = intro.replace("## 2.1 Problem statement", "# 2. Problem Statement\n")
intro = intro.replace("## 2.2 Motivation", "# 3. Motivation\n")
intro = intro.replace("## 2.3 Novelty", "# 4. Novelty of the Project\n")
intro = re.sub(r"(?m)^## 1\.(\d)", r"## 1.\1", intro)
parts.append("\n---\n\n# 1. Introduction\n\n" + intro)

# ---- SECTION 5 (Dataset) + 6 (Methodology) ---------------------------------
meth = strip_scaffold(find("report_section3_methodology.md").read_text())
meth = renumber(meth, 3, 6)
# lift 6.2 (dataset) out as its own top-level Section 5
m = re.search(r"(?ms)^## 6\.2 Dataset and player-season construction\n(.*?)(?=^## 6\.3 )", meth)
dataset = m.group(1).strip() if m else ""
meth = meth.replace(m.group(0), "") if m else meth
parts.append("\n---\n\n# 5. Dataset Description & Details\n\n" + dataset)

expl = renumber(strip_scaffold(find("report_section3_10_explainability.md").read_text()), 3, 6)
genai_m = strip_scaffold(find("report_section6_11_genai.md").read_text())
def splice(txt, heading, body):
    """
    Replace the placeholder line under a stub heading with real content.

    The parent heading is KEPT and the inserted body's own "##" subsections are
    demoted to "###", so the hierarchy stays 6.9 > 6.9.1 rather than leaving
    orphaned 6.9.1 headings with no parent.
    """
    body = re.sub(r"(?m)^## ", "### ", body.strip())
    pat = re.compile(rf"(?ms)^(## {re.escape(heading)})\n+\*Supplied by[^\n]*\n")
    new, n = pat.subn(lambda m: m.group(1) + "\n\n" + body + "\n\n", txt)
    if n != 1:
        raise SystemExit(f"ASSEMBLY ERROR: could not splice '{heading}' "
                         f"({n} matches). Section would be silently omitted.")
    return new

meth = splice(meth, "6.10 Explainable AI", expl)
meth = splice(meth, "6.11 Generative-AI recruitment briefs", genai_m)
# Promoting the dataset section out of Methodology left a hole at 6.2, which in
# a finished report reads as an omitted subsection rather than a design choice.
# Close the gap by shifting every subsection from 6.3 upward down by one, at both
# two and three heading levels, and update cross-references to match.
def close_gap(txt):
    for n in range(3, 13):                       # descending would collide; 3..12 ascending is safe
        pass
    for n in range(3, 13):
        txt = txt.replace(f"@@{n}@@", "")        # no-op guard
    # headings: 6.N and 6.N.M  ->  6.(N-1) and 6.(N-1).M
    for n in range(3, 13):
        txt = re.sub(rf"(?m)^(#{{2,4}}\s*)6\.{n}\.(\d+)", rf"\g<1>6.{n-1}.\2", txt)
        txt = re.sub(rf"(?m)^(#{{2,4}}\s*)6\.{n}(?!\d)", rf"\g<1>6.{n-1}", txt)
    # cross-references
    for n in range(3, 13):
        txt = re.sub(rf"\bSection 6\.{n}\.(\d+)", rf"Section 6.{n-1}.\1", txt)
        txt = re.sub(rf"\bSection 6\.{n}(?!\.?\d)", rf"Section 6.{n-1}", txt)
    return txt

meth = close_gap(meth)
parts.append("\n---\n\n# 6. Design and Methodology\n\n" + meth)

# ---- SECTION 7 (Results) ---------------------------------------------------
res = renumber(strip_scaffold(find("report_section4_results.md").read_text()), 4, 7)
res8 = renumber(strip_scaffold(find("report_section4_8_explainability.md").read_text()), 4, 7)
res9 = strip_scaffold(find("report_section7_9_genai.md").read_text())
parts.append("\n---\n\n# 7. Results and Discussion\n\n" + res + "\n\n" + res8 + "\n\n" + res9)

# ---- SECTION 8 (Analysis) --------------------------------------------------
ana = renumber(strip_scaffold(find("report_section5_analysis.md").read_text()), 5, 8)
parts.append("\n---\n\n# 8. Analysis\n\n" + ana)

# ---- SECTIONS 9-10 ---------------------------------------------------------
con = renumber(strip_scaffold(find("report_section6_conclusion.md").read_text()), 6, 9)
m = re.search(r"(?ms)^## 9\.6 Limitations and future work\n(.*)$", con)
if m:
    lim = m.group(1).strip()
    con = con.replace(m.group(0), "")
    parts.append("\n---\n\n# 9. Conclusion\n\n" + con.strip())
    parts.append("\n---\n\n# 10. Limitations and Future Work\n\n" + lim)
else:
    parts.append("\n---\n\n# 9. Conclusion\n\n" + con)

doc = "\n\n".join(parts)

# ---- CROSS-REFERENCE PASS ---------------------------------------------------
# Per-file renumbering fixes a file's own headings but not references it makes
# to OTHER sections. Section 8 still pointed at "Section 4.5" and so on. These
# are remapped explicitly; 6.2 becomes Section 5 because Dataset Description was
# promoted out of Methodology.
# NOTE: these targets are POST-gap-close. Methodology subsections from 3.3
# onward shift down by one because 3.2 (Dataset) was promoted to Section 5.
# An earlier version used pre-gap-close targets and sent every methodology
# cross-reference one section too high.
XREF = {
    "3.1": "6.1", "3.2": "5", "3.3": "6.2", "3.4": "6.3", "3.5": "6.4",
    "3.6": "6.5", "3.7": "6.6", "3.8": "6.7", "3.9": "6.8",
    # sections written natively against pre-gap-close methodology numbering
    "6.11.6": "6.10.6", "6.11.5": "6.10.5", "6.11.4": "6.10.4",
    "6.11.3": "6.10.3", "6.11.2": "6.10.2", "6.11.1": "6.10.1",
    "4.1": "7.1", "4.2": "7.2", "4.3": "7.3", "4.4": "7.4", "4.5": "7.5",
    "4.6": "7.6", "4.7": "7.7", "4.8": "7.8",
    "5.1": "8.1", "5.2": "8.2", "5.3": "8.3", "5.4": "8.4", "5.5": "8.5",
    "5.6": "8.6", "5.7": "8.7", "5.8": "8.8", "5.9": "8.9",
    "6.2": "5",
}
for old, new in sorted(XREF.items(), key=lambda kv: -len(kv[0])):
    # (?![\d.]) was blocked by a sentence-ending period, so any cross-reference
    # closing a sentence ("...in Section 5.7.") was silently skipped.
    # (?!\.?\d) excludes only a genuine deeper level such as 5.7.1.
    doc = re.sub(rf"\bSection {re.escape(old)}(?!\.?\d)", f"Section {new}", doc)
    doc = re.sub(rf"§{re.escape(old)}(?!\.?\d)", f"§{new}", doc)

doc = re.sub(r"\n{4,}", "\n\n\n", doc)
DEST.write_text(doc)

print(f"assembled -> {DEST.name}")
print(f"  {len(doc.split()):,} words, {len(doc.split(chr(10))):,} lines")
print("\nTop-level sections:")
for ln in doc.split("\n"):
    if re.match(r"^# \d+\.", ln) or ln.startswith("# Front") :
        print("  ", ln)
