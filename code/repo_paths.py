"""
Repository path resolution.

Every pipeline script imports this so it works from a clean clone regardless of
the directory it is invoked from. Paths are derived from this file's own
location, never from the current working directory and never from an absolute
path belonging to the machine the project was built on.

Layout this resolves against:

    data/raw/           frozen dataset archives, unpacked in place
    data/processed/     core tables reused across several stages
    outputs/<stage>/    stage-specific results
    figures/            figures used in the report
    briefs/             generative-AI recruitment briefs

Artifacts are looked up by name across data/processed and every outputs/
subdirectory, so a script does not need to know which stage produced its input.
Writes go to the stage directory the calling script declares.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "figures"
BRIEFS = ROOT / "briefs"
REPORT = ROOT / "report"

STAGES = ["eda", "valuation", "backtest", "exit_risk", "optimizer",
          "shap", "genai", "audit"]


def find(name):
    """
    Locate an artifact by filename anywhere in the repository's data or output
    directories. Raises with a clear message rather than a bare
    FileNotFoundError, because a missing artifact usually means an earlier
    pipeline stage has not been run.
    """
    name = Path(name).name
    # Stage outputs are searched FIRST. A file with the same name in
    # data/processed must never shadow the current stage artifact: that is the
    # silent stale-artifact selection this project exists to prevent.
    for base in ([OUTPUTS / s for s in STAGES] + [PROC, RAW, FIGURES, BRIEFS]
                 + [REPORT / "development", REPORT / "final",
                    REPORT / "prompt_logbook"]):
        candidate = base / name
        if candidate.exists():
            return candidate
    searched = ", ".join(str(p.relative_to(ROOT)) for p in
                         [PROC, REPORT / "development"]
                         + [OUTPUTS / s for s in STAGES])
    raise FileNotFoundError(
        f"'{name}' not found in the repository.\n"
        f"Searched: {searched}\n"
        f"If this is a pipeline artifact, run the earlier stages first "
        f"(see README, 'Reproducing the analysis'). If it is raw data, unpack "
        f"the archives in data/raw/ first."
    )


def stage_dir(stage):
    """Return an outputs/<stage> directory, creating it if needed."""
    d = OUTPUTS / stage
    d.mkdir(parents=True, exist_ok=True)
    return d


def ensure_dirs():
    """Create the write targets a script may need."""
    for d in [PROC, OUTPUTS, FIGURES, BRIEFS]:
        d.mkdir(parents=True, exist_ok=True)
