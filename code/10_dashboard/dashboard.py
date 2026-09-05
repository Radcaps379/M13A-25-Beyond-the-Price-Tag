"""
==============================================================================
RECRUITMENT DECISION-SUPPORT DASHBOARD
Project: Beyond the Price Tag
==============================================================================

RUN WITH:
    pip install streamlit pandas numpy pulp
    streamlit run dashboard.py

THE RULE THIS INTERFACE ENFORCES
--------------------------------
No player is ever labelled "Undervalued". Phase 7 tested that claim
out-of-sample and rejected it (p = 0.307), and found instead that large
unexplained valuation gaps predict EXIT from top-5 football (odds ratio 4.82,
p = 2.6e-11).

The interface therefore says "Potential valuation discrepancy - investigate",
and pairs every valuation gap with its exit risk so that a large gap can never
be read as a buy signal in isolation.
==============================================================================
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


import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path


st.set_page_config(page_title="Beyond the Price Tag",
                   page_icon="⬡", layout="wide",
                   initial_sidebar_state="expanded")

# -----------------------------------------------------------------------------
# Design tokens
# Palette: committee-room ink and paper, with signal colours reserved strictly
# for meaning - amber = caution, slate-teal = model signal. Nothing decorative.
# -----------------------------------------------------------------------------
INK = "#12212E"
PAPER = "#F7F5F0"
TEAL = "#2F6F7E"
AMBER = "#C4791F"
RUST = "#9B3F2E"
MUTED = "#7B8794"

st.markdown(f"""<style>
    .stApp {{ background:{PAPER}; }}
    html, body, [class*="css"] {{ font-family:'IBM Plex Sans',-apple-system,sans-serif; }}
    h1,h2,h3 {{ font-family:'IBM Plex Sans',sans-serif; letter-spacing:-.02em; color:{INK}; }}
    .eyebrow {{ font-size:.7rem; letter-spacing:.16em; text-transform:uppercase;
                color:{MUTED}; font-weight:600; margin-bottom:.2rem; }}
    .verdict {{ border-left:3px solid {AMBER}; background:#FFF8EC; padding:.85rem 1.1rem;
                margin:.6rem 0; font-size:.92rem; color:{INK}; }}
    .known {{ border-left:3px solid {MUTED}; background:#EFEFEC; padding:.85rem 1.1rem;
              margin:.6rem 0; font-size:.88rem; color:#3C4A57; }}
    .metric-big {{ font-size:2.1rem; font-weight:700; color:{INK}; line-height:1; }}
    .metric-lab {{ font-size:.72rem; letter-spacing:.1em; text-transform:uppercase;
                   color:{MUTED}; font-weight:600; }}
    .pill {{ display:inline-block; padding:.18rem .6rem; border-radius:2px;
             font-size:.72rem; font-weight:600; letter-spacing:.04em; }}
    .pill-hi {{ background:#F6E3DE; color:{RUST}; }}
    .pill-md {{ background:#FBEFD9; color:{AMBER}; }}
    .pill-lo {{ background:#DFEAEC; color:{TEAL}; }}
    .rule {{ border-top:1px solid #DCD8D0; margin:1.4rem 0 1rem; }}
    [data-testid="stSidebar"] {{ background:{INK}; }}
    [data-testid="stSidebar"] * {{ color:#DDE4E8 !important; }}
</style>""", unsafe_allow_html=True)


# =============================================================================
# DATA
# =============================================================================
@st.cache_data
def load():
    players = pd.read_csv(find("optimizer_input_2024_25.csv"))
    shap_all = pd.read_csv(find("shap_all_players.csv"))
    seg = pd.read_csv(find("pretest_segment_uncertainty.csv"))[
        ["position", "league", "seg_unc"]]
    consts = pd.read_csv(find("pretest_constants.csv"), index_col=0)["value"]
    players = players.merge(shap_all, on="player_id", how="left")
    players = players.merge(seg, on=["position", "league"], how="left")
    players["seg_unc"] = players.seg_unc.fillna(float(consts["global_uncertainty"]))
    players["uncertainty"] = players.seg_unc.rank(pct=True)

    # score components - identical definitions to optimizer.py
    players["quality_raw"] = np.where(
        players.position.isin(["Attack", "Midfield"]),
        players.goal_contributions_per90,
        players.minutes / players.minutes.max())
    players["quality"] = players.groupby("position").quality_raw.rank(pct=True)
    players["potential"] = np.clip((30 - players.age) / (30 - 17), 0, 1)
    cap = float(consts["value_efficiency_cap_p90"])
    players["value_efficiency"] = players.groupby("position")[
        "mispricing_ratio"].transform(lambda s: s.clip(upper=cap).rank(pct=True))
    players["risk"] = 0.7 * players.exit_prob + 0.3 * players.uncertainty
    players["gap_pct"] = 100 * (players.pred_eur / players.market_value_eur - 1)
    return players


players = load()


def risk_pill(p):
    if p >= 0.40:
        return f'<span class="pill pill-hi">HIGH RISK {100*p:.0f}%</span>'
    if p >= 0.20:
        return f'<span class="pill pill-md">MODERATE {100*p:.0f}%</span>'
    return f'<span class="pill pill-lo">LOWER RISK {100*p:.0f}%</span>'


def gap_label(gap, exit_p):
    """Never says 'undervalued'. The gap is a question, not a verdict."""
    if gap <= 5:
        return "Model and market broadly agree"
    if exit_p >= 0.40:
        return "Discrepancy with high exit risk — treat as a warning"
    return "Potential valuation discrepancy — investigate"


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown('<div class="eyebrow">Beyond the Price Tag</div>',
                unsafe_allow_html=True)
    st.markdown("### Recruitment decision support")
    st.caption("End of 2024/25 season · top-5 European leagues · 1,508 players")
    st.markdown("---")
    view = st.radio("View", ["Executive transfer window", "Player explorer",
                             "Why this player?", "Committee brief",
                             "How to read this"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("The system recommends **investigation**, never a transaction. "
               "Its own back-test found valuation gaps do not identify "
               "exploitable opportunities.")

# =============================================================================
# 1. EXECUTIVE TRANSFER WINDOW
# =============================================================================
if view == "Executive transfer window":
    st.markdown('<div class="eyebrow">Capital allocation</div>',
                unsafe_allow_html=True)
    st.title("Executive transfer window")

    c1, c2, c3 = st.columns([1.1, 1.4, 1])
    with c1:
        budget = st.slider("Transfer budget (€M)", 10, 150, 50, 5) * 1e6
    with c2:
        st.write("Positional requirements")
        p1, p2, p3 = st.columns(3)
        n_def = p1.number_input("Defenders", 0, 4, 1)
        n_mid = p2.number_input("Midfielders", 0, 4, 1)
        n_att = p3.number_input("Attackers", 0, 4, 1)
    with c3:
        tol = st.select_slider("Risk tolerance",
                               ["Conservative", "Balanced", "Open"],
                               value="Balanced")

    max_exit = {"Conservative": 0.25, "Balanced": 0.40, "Open": 0.60}[tol]
    needs = {k: v for k, v in
             [("Defender", n_def), ("Midfield", n_mid), ("Attack", n_att)] if v > 0}

    W = dict(q=0.35, p=0.25, v=0.20, r=0.20)
    d = players.copy()
    d["score"] = (W["q"] * d.quality + W["p"] * d.potential
                  + W["v"] * d.value_efficiency - W["r"] * d.risk)
    unc_cut = d.uncertainty.quantile(0.80)
    elig = d[(d.age <= 27) & (d.market_value_eur >= 1e6) & (d.quality >= 0.40)
             & (d.exit_prob <= max_exit) & (d.uncertainty <= unc_cut)
             & (d.position.isin(needs))]

    def solve(pool, budget, needs):
        try:
            import pulp
            pr = pulp.LpProblem("r", pulp.LpMaximize)
            x = {i: pulp.LpVariable(f"x{i}", cat="Binary") for i in pool.index}
            pr += pulp.lpSum(pool.loc[i, "score"] * x[i] for i in pool.index)
            pr += pulp.lpSum(pool.loc[i, "market_value_eur"] * x[i]
                             for i in pool.index) <= budget
            for pos, n in needs.items():
                pr += pulp.lpSum(x[i] for i in pool.index[pool.position == pos]) == n
            pr.solve(pulp.PULP_CBC_CMD(msg=0))
            if pulp.LpStatus[pr.status] == "Optimal":
                return pool.loc[[i for i in pool.index
                                 if x[i].value() and x[i].value() > .5]]
        except Exception:
            pass
        picks, spend = [], 0.0
        for pos, n in needs.items():
            for _, r in pool[pool.position == pos].sort_values(
                    "score", ascending=False).iterrows():
                if sum(1 for p in picks if p.position == pos) >= n:
                    break
                if spend + r.market_value_eur <= budget:
                    picks.append(r); spend += r.market_value_eur
        return pd.DataFrame(picks)

    if not needs:
        st.info("Set at least one positional requirement.")
    elif elig.empty:
        st.warning("No players meet these constraints. Widen the risk tolerance "
                   "or the positional requirements.")
    else:
        port = solve(elig, budget, needs)
        if port.empty:
            st.warning("No feasible portfolio within this budget.")
        else:
            spend = port.market_value_eur.sum()
            st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
            m = st.columns(4)
            for col, lab, val in [
                    (m[0], "Committed", f"€{spend/1e6:.1f}M"),
                    (m[1], "Remaining", f"€{(budget-spend)/1e6:.1f}M"),
                    (m[2], "Mean quality percentile", f"{100*port.quality.mean():.0f}"),
                    (m[3], "Mean exit risk", f"{100*port.exit_prob.mean():.0f}%")]:
                col.markdown(f'<div class="metric-lab">{lab}</div>'
                             f'<div class="metric-big">{val}</div>',
                             unsafe_allow_html=True)

            st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
            st.subheader("Shortlist for investigation")
            for _, r in port.sort_values("score", ascending=False).iterrows():
                a, b = st.columns([3, 2])
                with a:
                    st.markdown(f"**{r['name']}** · {r.position} · {r.club_name} "
                                f"· {r.league.split(' - ')[0]} · age {r.age:.0f}")
                    st.markdown(f"Market €{r.market_value_eur/1e6:.1f}M · "
                                f"model-implied €{r.pred_eur/1e6:.1f}M · "
                                f"gap {r.gap_pct:+.0f}%")
                    st.caption(gap_label(r.gap_pct, r.exit_prob))
                with b:
                    st.markdown(risk_pill(r.exit_prob), unsafe_allow_html=True)
                    st.progress(float(r.quality), text=f"quality {100*r.quality:.0f}th pctl")
                st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

            st.markdown('<div class="verdict"><b>This is a shortlist for '
                        'investigation, not a bid list.</b> The system cannot '
                        'establish that any of these transactions would '
                        'represent value. Each name requires contract, medical '
                        'and scouting review before any approach.</div>',
                        unsafe_allow_html=True)

# =============================================================================
# 2. PLAYER EXPLORER
# =============================================================================
elif view == "Player explorer":
    st.markdown('<div class="eyebrow">Any player, 2024/25</div>',
                unsafe_allow_html=True)
    st.title("Player explorer")

    f1, f2, f3 = st.columns(3)
    lg = f1.multiselect("League", sorted(players.league.unique()))
    ps = f2.multiselect("Position", sorted(players.position.unique()))
    ages = f3.slider("Age", 16, 40, (16, 40))

    v = players.copy()
    if lg: v = v[v.league.isin(lg)]
    if ps: v = v[v.position.isin(ps)]
    v = v[v.age.between(*ages)]

    st.caption(f"{len(v):,} players")

    # Signature view: the gap-versus-risk quadrant. A large gap on the right is
    # only interesting if it sits low on the risk axis - which is the entire
    # lesson of Phase 7 rendered as a chart.
    st.subheader("Valuation gap against exit risk")
    st.caption("A large gap paired with high exit risk is a warning, not a bargain. "
               "The model's residual predicts departure, not appreciation.")
    plot = v[v.gap_pct.between(-100, 400)]
    st.scatter_chart(plot.rename(columns={"gap_pct": "valuation gap %",
                                          "exit_prob": "exit risk"}),
                     x="valuation gap %", y="exit risk", color="position",
                     height=380)

    sel = st.selectbox("Select a player",
                       v.sort_values("name")["name"].tolist() or ["—"])
    if sel and sel != "—":
        r = v[v.name == sel].iloc[0]
        st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
        st.markdown(f"### {r['name']}")
        st.caption(f"{r.position} · {r.club_name} · {r.league} · age {r.age:.1f} "
                   f"· {int(r.minutes):,} league minutes")

        m = st.columns(5)
        for col, lab, val in [
                (m[0], "Market value", f"€{r.market_value_eur/1e6:.1f}M"),
                (m[1], "Model-implied", f"€{r.pred_eur/1e6:.1f}M"),
                (m[2], "Gap", f"{r.gap_pct:+.0f}%"),
                (m[3], "Quality pctl", f"{100*r.quality:.0f}"),
                (m[4], "Exit risk", f"{100*r.exit_prob:.0f}%")]:
            col.markdown(f'<div class="metric-lab">{lab}</div>'
                         f'<div class="metric-big">{val}</div>',
                         unsafe_allow_html=True)

        st.markdown(f'<div class="verdict"><b>{gap_label(r.gap_pct, r.exit_prob)}</b>'
                    f'</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.markdown("**Raises the model's valuation**")
        for d in str(r.positive_drivers).split(";"):
            if d.strip(): c1.markdown(f"- {d.strip()}")
        c2.markdown("**Lowers the model's valuation**")
        for d in str(r.negative_drivers).split(";"):
            if d.strip(): c2.markdown(f"- {d.strip()}")

# =============================================================================
# 3. WHY THIS PLAYER?
# =============================================================================
elif view == "Why this player?":
    st.markdown('<div class="eyebrow">Two different questions</div>',
                unsafe_allow_html=True)
    st.title("Why this player?")
    st.caption("A valuation and a recommendation are explained by different "
               "things. The interface keeps them apart.")

    port = pd.read_csv(find("recommended_portfolio.csv"))
    who = st.selectbox("Recommended player", port.name.tolist())
    r = port[port.name == who].iloc[0]
    pr = players[players.player_id == r.player_id].iloc[0]

    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    a, b = st.columns(2)

    with a:
        st.markdown('<div class="eyebrow">Prediction explanation</div>',
                    unsafe_allow_html=True)
        st.markdown("#### Why the model values him this way")
        st.caption("SHAP decomposition of the valuation model")
        st.markdown(f"Model-implied **€{pr.pred_eur/1e6:.1f}M** against a market "
                    f"value of €{pr.market_value_eur/1e6:.1f}M")
        st.markdown("**Raises the valuation**")
        for d in str(pr.positive_drivers).split(";"):
            if d.strip(): st.markdown(f"- {d.strip()}")
        st.markdown("**Lowers the valuation**")
        for d in str(pr.negative_drivers).split(";"):
            if d.strip(): st.markdown(f"- {d.strip()}")

    with b:
        st.markdown('<div class="eyebrow">Selection explanation</div>',
                    unsafe_allow_html=True)
        st.markdown("#### Why the optimizer selected him")
        st.caption("Score components and binding constraints")
        for lab, val, cap_ in [
                ("Quality percentile", r.quality, "position-appropriate performance"),
                ("Development potential", r.potential, "resale runway to age 30"),
                ("Value efficiency", r.value_efficiency, "capped, deliberately not dominant"),
                ("Risk component", r.risk, "exit probability and model uncertainty")]:
            st.markdown(f"**{lab}** — {val:.2f}")
            st.progress(float(min(max(val, 0), 1)))
            st.caption(cap_)

    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">The third question</div>',
                unsafe_allow_html=True)
    st.markdown("#### What the model does not know")
    st.markdown(f"""<div class="known">
    This system observes match statistics, age, position, league and valuation
    history. It has <b>no information</b> on contract length or expiry, injury
    history or current fitness, scouting and tactical assessment, off-field
    circumstances, or the player's willingness to move.<br><br>
    Predicted probability of falling below 900 top-5 league minutes next season:
    <b>{100*pr.exit_prob:.0f}%</b>. The valuation model carries a median error of
    43.9% on held-out data, and systematically under-values players aged 21 and
    under — a pattern that replicates across three consecutive seasons.
    </div>""", unsafe_allow_html=True)

# =============================================================================
# 4. COMMITTEE BRIEF
# =============================================================================
elif view == "Committee brief":
    st.markdown('<div class="eyebrow">Generated document</div>',
                unsafe_allow_html=True)
    st.title("Recruitment committee brief")

    port = pd.read_csv(find("recommended_portfolio.csv"))
    who = st.selectbox("Player", port.name.tolist())
    slug = who.lower().replace(" ", "_")

    llm_path = BRIEFS / f"llm_brief_{slug}.md"
    ctrl_path = BRIEFS / f"brief_{slug}.md"

    if llm_path.exists():
        st.success("Source: live language-model generation, validated against "
                   "the fidelity checks.")
        st.markdown(llm_path.read_text())
    elif ctrl_path.exists():
        st.warning("**Template control / demonstration.** This brief was produced "
                   "by the deterministic template, not a language model. The "
                   "live generation has not been run in this session.")
        st.markdown(ctrl_path.read_text())
    else:
        st.info("No brief found. Run `python genai_briefs.py --offline` first.")

    st.markdown('<div class="known">Every brief is checked against six rules: '
                'numerical fidelity, no unsupported claims, no speculative '
                'causal inference, decision consistency, and uncertainty '
                'disclosure. A brief failing any check is rejected.</div>',
                unsafe_allow_html=True)

# =============================================================================
# 5. HOW TO READ THIS
# =============================================================================
else:
    st.markdown('<div class="eyebrow">Before you use this</div>',
                unsafe_allow_html=True)
    st.title("How to read this system")

    st.markdown("""
#### What it does
Estimates what a player's market value *would be* if it followed observable
performance, age, position, league and career trajectory. It then compares that
estimate to the actual market value, and separately estimates the probability
that the player drops below 900 top-5 league minutes next season.

#### What it does not do
It does not find bargains. That claim was tested and rejected.
""")

    st.markdown('<div class="verdict"><b>The founding hypothesis failed, and '
                'that shaped this interface.</b><br><br>'
                'Players flagged as undervalued by the valuation residual showed '
                '<b>no</b> subsequent relative appreciation (p = 0.307). They were '
                '<b>3.7× the benchmark rate of disappearing from top-5 football entirely</b> '
                '(30.1% against 8.2%, p = 2.6 × 10⁻¹¹).<br><br>'
                'A large unexplained valuation gap is therefore better read as a '
                'sign that the market knows something the model does not — '
                'contract, injury, role, attitude — than as an error to exploit.'
                '</div>', unsafe_allow_html=True)

    st.markdown("""
#### Why no player is ever labelled "undervalued"
The interface says **"potential valuation discrepancy — investigate"**. That is
not hedging. It is the most the evidence supports.

#### The one habit this system is designed to build
Do not ask *"is this player cheap?"* Ask *"why is he cheap, and how confident
are we that the model knows enough to call it an opportunity?"*
""")

    st.markdown('<div class="rule"></div>', unsafe_allow_html=True)
    c = st.columns(3)
    for col, lab, val, cap_ in [
            (c[0], "Valuation model", "R² 0.678",
             "held-out 2024/25, season-normalised"),
            (c[1], "Exit-risk model", "AUC 0.732",
             "logistic, held-out 2024/25"),
            (c[2], "Mispricing hypothesis", "Rejected",
             "p = 0.307, out-of-sample")]:
        col.markdown(f'<div class="metric-lab">{lab}</div>'
                     f'<div class="metric-big">{val}</div>', unsafe_allow_html=True)
        col.caption(cap_)
