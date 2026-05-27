import streamlit as st
import json
import os

# --- 1. STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Brand Positioning Monitor", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        header, #MainMenu, footer {visibility: hidden;}
        iframe { border: none; background: transparent; }
    </style>
""", unsafe_allow_html=True)


# --- 2. DATA ROUTING & INJECTION ---
def get_valid_path(*paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[0]


scores_path = get_valid_path("data/scores/final_brand_scores.json", "Data/Scores/final_brand_scores.json",
                             "Data/scores/final_brand_scores.json")
hist_path = get_valid_path("data/scores/historical_scores.json", "Data/Scores/historical_scores.json",
                           "Data/scores/historical_scores.json")

if not os.path.exists(scores_path):
    st.error("Cloud Deployment Error: The server cannot find the scores file.")
    st.stop()

with open(scores_path, "r", encoding="utf-8") as f:
    live_scores = json.load(f)

if os.path.exists(hist_path):
    with open(hist_path, "r", encoding="utf-8") as f:
        hist_scores = json.load(f)
else:
    hist_scores = {}

# Muted, technical color palette to match the PageCoder aesthetic
color_map = {
    "Chanel": "#f8f9fa", "Hermès": "#f97316", "YSL": "#eab308", "Maison Margiela": "#a1a1aa",
    "Jean Paul Gaultier": "#38bdf8", "Viktor & Rolf": "#f472b6", "Mancera": "#d97706",
    "Creed": "#60a5fa", "Byredo": "#818cf8", "VARŌ": "#bef264", "VARO": "#bef264"
}

drift_insights = {
    "Chanel": "Immovable monument. Near-zero drift over 4 years. Chanel acts as the category's gravitational anchor, relying on absolute consistency rather than adaptation to maintain unquestioned legacy status.",
    "Hermès": "Minor regression. A slight tightening of its poetic, nature-driven narrative into more structured prestige. Hermès maintains its core elemental identity while subtly reinforcing its institutional dominance.",
    "YSL": "Massive repositioning. Pivoted from intimate, nocturnal seduction to hyper-dominant, daytime defiance. A deliberate corporate strategy to abandon intimacy and capture a younger, bolder demographic through collective empowerment.",
    "Maison Margiela": "Highly defensible stability. Marginal drift toward the center. Despite corporate ownership, the brand has fiercely protected its hyper-specific memory whitespace, resisting the urge to build monolithic myths.",
    "Jean Paul Gaultier": "Deepening of the spectacle. Drifted further into collective myth. JPG is actively doubling down on performative identity and theatrical archetypes, entirely rejecting the modern trend toward vulnerability.",
    "Viktor & Rolf": "Sustained performance. Minor drift toward dominance. The brand continues to rely on avant-garde fantasy and maximalism, operating purely as an outward-facing spectacle with no attempt at consumer intimacy.",
    "Mancera": "Solidified gatekeeping. Remained anchored in its niche. Stable positioning relying on absolute exclusivity and raw ingredient prestige rather than attempting broader cultural relevance.",
    "Creed": "Doubling down on dynastic dominance. Further entrenched in historical legacy. Creed ignores demands for transparency, relying entirely on royal artisan heritage to justify price premiums.",
    "Byredo": "Indie-to-Corporate Lifecycle. Noticeable drift away from extreme private truth toward the center. Post-acquisition scaling requires broader cultural appeal; Byredo is diluting its founder intimacy to support global mass-market distribution.",
    "VARŌ": "New Entrant. Zero historical drift. Engineered specifically to capture the extreme Vulnerability and Private Truth whitespace that brands like YSL and Byredo abandoned as they scaled.",
    "VARO": "New Entrant. Zero historical drift. Engineered specifically to capture the extreme Vulnerability and Private Truth whitespace that brands like YSL and Byredo abandoned as they scaled."
}

js_brands, js_scores, js_commentary, js_drift = [], {}, {}, []

for brand, data in live_scores.items():
    x = data.get("x_score", 5.0)
    y = data.get("y_score", 5.0)

    # SVG Math mapped to your exact viewBox="0 0 760 440"
    cx = 60 + (x / 10.0) * 640
    cy = 50 + ((10.0 - y) / 10.0) * 340

    hx, hy = None, None
    if brand in hist_scores:
        hx_raw = hist_scores[brand].get("x_score", 5)
        hy_raw = hist_scores[brand].get("y_score", 5)
        hx = 60 + (hx_raw / 10.0) * 640
        hy = 50 + ((10.0 - hy_raw) / 10.0) * 340

        delta = x - hx_raw
        dir_str = "up" if delta > 0 else "down" if delta < 0 else ""
        delta_str = f"{delta:+.1f}" if delta != 0 else "0.0"
        js_drift.append({
            "brand": "M. Margiela" if brand == "Maison Margiela" else brand,
            "old": round(hx_raw * 10, 1), "curr": round(x * 10, 1),
            "delta": delta_str, "dir": dir_str
        })
    else:
        js_drift.append({
            "brand": "VARŌ" if brand == "VARO" else brand,
            "old": None, "curr": round(x * 10, 1),
            "delta": "New", "dir": ""
        })

    js_brands.append({
        "name": brand, "color": color_map.get(brand, "#ffffff"),
        "cx": round(cx, 1), "cy": round(cy, 1),
        "x21": round(hx, 1) if hx is not None else None,
        "y21": round(hy, 1) if hy is not None else None,
        "isVaro": (brand == "VARŌ" or brand == "VARO")
    })

    x_label = "Vulnerability" if x >= 5 else "Dominance"
    y_label = "Private Truth" if y >= 5 else "Collective Myth"

    js_scores[brand] = {
        "x": round(x, 2), "y": round(y, 2), "xLabel": x_label, "yLabel": y_label
    }

    js_commentary[brand] = {
        "quote": f"Agent 4 Audit Log: {data.get('critique', 'No audit log available.')}",
        "rx": data.get("x_reasoning", "No reasoning provided."),
        "ry": data.get("y_reasoning", "No reasoning provided."),
        "drift_insight": drift_insights.get(brand, "No drift data available.")
    }

# --- 3. THE EXACT USER-PROVIDED HTML TEMPLATE ---
# Injected the MBA strategic architecture panel seamlessly under the Drift panel
custom_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Brand Positioning Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">

<style>
:root {
  --bg:#08090d; --panel:#10131a; --panel2:#151923; --line:rgba(255,255,255,.09);
  --text:#f7f7fb; --muted:#9aa3b2; --faint:#626b7c; --gold:#ffcc66;
  --goldSoft:rgba(255,204,102,.14); --green:#7bd88f; --red:#ff8f8f;
  --radius:12px; --shadow:0 24px 80px rgba(0,0,0,.36);
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:Inter,system-ui,sans-serif;color:var(--text);min-height:100vh;overflow-x:hidden;
  background:radial-gradient(circle at 20% -10%,rgba(255,204,102,.13),transparent 32%),
             radial-gradient(circle at 86% 0%,rgba(120,155,255,.1),transparent 30%),var(--bg);
}
.app{min-height:100vh;display:flex;flex-direction:column}
.topbar{
  height:64px;padding:0 22px;display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--line);background:rgba(8,9,13,.76);backdrop-filter:blur(20px);
  position:sticky;top:0;z-index:10;
}
.lockup{display:flex;align-items:center;gap:12px}
.logo{
  width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,var(--gold),#fff0bd);
  color:#111;font-weight:900;display:grid;place-items:center;box-shadow:0 0 28px rgba(255,204,102,.2)
}
.title{font-size:14px;font-weight:800}.sub{font-size:11px;color:var(--muted);margin-top:2px}
.status{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:999px;padding:8px 12px;color:var(--muted);font-size:12px;background:rgba(255,255,255,.04)}
.status-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 16px rgba(123,216,143,.55)}

.workspace{display:grid;grid-template-columns:280px minmax(0,1fr)360px;flex:1}
.rail,.inspector{background:rgba(16,19,26,.86);backdrop-filter:blur(22px);padding:18px;overflow:auto}
.rail{border-right:1px solid var(--line)}.inspector{border-left:1px solid var(--line)}
.stage{padding:20px;overflow:auto;min-width:0}

.panel{background:rgba(16,19,26,.76);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow)}
.panel+ .panel{margin-top:14px}
.panel-head{padding:14px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:12px}
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:.13em;color:var(--faint);font-weight:800}
.panel-title{font-size:13px;font-weight:800;margin-top:4px}.panel-body{padding:14px}

.search{width:100%;height:38px;border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.04);color:var(--text);outline:none;padding:0 12px;margin-bottom:12px}
.search:focus{border-color:rgba(255,204,102,.45);box-shadow:0 0 0 3px rgba(255,204,102,.08)}
.brand-list{display:flex;flex-direction:column;gap:6px}
.brand-item{
  display:grid;grid-template-columns:10px minmax(0,1fr)auto;align-items:center;gap:10px;
  padding:10px;border:1px solid transparent;border-radius:9px;cursor:pointer;color:var(--muted)
}
.brand-item:hover{background:rgba(255,255,255,.04);color:var(--text)}
.brand-item.selected-focus{border-color:rgba(255,204,102,.38);background:var(--goldSoft);color:var(--text)}
.brand-dot{width:8px;height:8px;border-radius:50%;box-shadow:0 0 16px currentColor}
.brand-name{font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.brand-coords{font-size:11px;color:var(--faint);font-variant-numeric:tabular-nums}

.axis-pill{display:grid;grid-template-columns:1fr 1fr;gap:4px;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:11px;padding:4px}
.axis-pill span{height:30px;display:grid;place-items:center;border-radius:8px;color:var(--muted);font-size:12px}
.axis-pill span.active{background:var(--gold);color:#16120a;font-weight:800}

.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
.metric{border:1px solid var(--line);border-radius:var(--radius);background:rgba(255,255,255,.035);padding:14px}
.metric-value{font-size:24px;font-weight:900;letter-spacing:-.04em;line-height:1}.metric-label{font-size:11px;color:var(--muted);margin-top:7px}

.map-panel{overflow:hidden}
.map-toolbar{min-height:58px;padding:13px 16px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:14px}
.map-toolbar h1{font-size:17px;letter-spacing:-.02em}.map-toolbar p{font-size:12px;color:var(--muted);margin-top:4px}
.icon-btn{width:34px;height:34px;border-radius:10px;border:1px solid var(--line);background:rgba(255,255,255,.04);color:var(--text);cursor:pointer;display:grid;place-items:center}
.icon-btn.active{border-color:rgba(255,204,102,.45);background:var(--goldSoft);color:var(--gold)}
.icon-btn svg{width:17px;height:17px;stroke:currentColor}
.canvas-wrap{position:relative;padding:12px}
.map-canvas{display:block;width:100%;aspect-ratio:1.7/1;min-height:360px;max-height:620px;border-radius:10px;background:#0b0d13;border:1px solid var(--line)}
.axis-label{font:800 8.5px Inter,sans-serif;letter-spacing:.18em;fill:rgba(247,247,251,.34)}
.brand-node{transition:opacity .18s,transform .18s;transform-box:fill-box;transform-origin:center}.brand-node:hover{transform:scale(1.08)}
#pulse-ring{animation:pulse 1.8s ease-out infinite}@keyframes pulse{0%{r:12;opacity:.8}100%{r:32;opacity:0}}

.tooltip{position:absolute;z-index:20;min-width:172px;opacity:0;pointer-events:none;transform:translateY(4px);transition:.12s;background:rgba(17,20,28,.94);border:1px solid rgba(255,255,255,.14);border-radius:10px;box-shadow:var(--shadow);padding:10px}
.tooltip.visible{opacity:1;transform:translateY(0)}
.tooltip-brand{font-weight:900;font-size:12px;margin-bottom:8px}.tooltip-row{display:flex;justify-content:space-between;color:var(--muted);font-size:11px;line-height:1.7}.tooltip-val{color:var(--text)}

.quadrants{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:14px}
.quadrant{border:1px solid var(--line);border-radius:var(--radius);background:rgba(255,255,255,.03);padding:12px;min-height:92px}
.quadrant.highlight{border-color:rgba(255,204,102,.34);background:var(--goldSoft)}
.quadrant-name{font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.1em;font-weight:900}
.quadrant-brands{font-size:12px;color:var(--muted);line-height:1.5;margin-top:8px}

.drift-bars{display:flex;flex-direction:column;gap:8px}
.drift-row{display:grid;grid-template-columns:108px minmax(80px,1fr)42px;gap:10px;align-items:center;padding:7px 8px;border-radius:8px;cursor:pointer}
.drift-row.highlighted{background:var(--goldSoft)}
.drift-brand-name{font-size:11px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.drift-track{height:4px;border-radius:999px;background:rgba(255,255,255,.06);position:relative}
.drift-old-marker,.drift-new-marker,.drift-connector{position:absolute;top:50%;transform:translateY(-50%)}
.drift-old-marker{width:2px;height:12px;background:rgba(255,255,255,.28);border-radius:2px}
.drift-new-marker{width:3px;height:14px;background:var(--gold);border-radius:2px;box-shadow:0 0 12px rgba(255,204,102,.38)}
.drift-connector{height:3px;background:linear-gradient(90deg,rgba(255,255,255,.12),rgba(255,204,102,.6));border-radius:999px}
.drift-delta{font-size:11px;text-align:right;color:var(--faint)}.drift-delta.up{color:var(--green)}.drift-delta.down{color:var(--red)}

.selected-pill{color:var(--gold);background:var(--goldSoft);border:1px solid rgba(255,204,102,.28);border-radius:999px;padding:5px 10px;font-size:12px;font-weight:800;max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.empty{min-height:210px;display:grid;place-items:center;text-align:center;color:var(--faint);font-size:13px;line-height:1.6}
.hidden{display:none!important}
.score-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.score-card,.insight{border:1px solid var(--line);border-radius:10px;background:rgba(255,255,255,.03);padding:12px}
.score-label,.insight-title{font-size:10px;color:var(--faint);text-transform:uppercase;letter-spacing:.12em;font-weight:900}
.score-num{font-size:34px;font-weight:900;letter-spacing:-.06em;margin-top:8px}.score-axis-name{font-size:11px;color:var(--muted)}
.score-bar-track{height:5px;border-radius:999px;background:rgba(255,255,255,.06);overflow:hidden;margin-top:12px}.score-bar-fill{height:100%;background:linear-gradient(90deg,#8ab4ff,var(--gold));border-radius:999px;transition:.5s}
.insight{margin-top:12px}.insight.accent{background:var(--goldSoft);border-color:rgba(255,204,102,.26)}
.insight-heading{font-family:"Instrument Serif",serif;font-size:20px;margin:8px 0}.insight-text{font-size:12px;color:var(--muted);line-height:1.7}.implication{font-size:12px;font-weight:800;margin-top:9px}
.quote{font-family:"Instrument Serif",serif;font-size:17px;line-height:1.55;color:#d8dde8}
.reasoning{display:flex;flex-direction:column;gap:8px;margin-top:12px}.reason-row{display:grid;grid-template-columns:74px 1fr;gap:9px}
.tag{border:1px solid var(--line);border-radius:7px;color:var(--muted);padding:4px 6px;font-size:9px;font-weight:900;text-align:center}.reason-text{font-size:11.5px;color:var(--muted);line-height:1.6}

@media(max-width:1180px){.workspace{grid-template-columns:250px 1fr}.inspector{grid-column:1/-1;border-left:0;border-top:1px solid var(--line)}.metrics{grid-template-columns:repeat(2,1fr)}.quadrants{grid-template-columns:repeat(2,1fr)}}
@media(max-width:760px){.workspace{display:block}.rail,.stage,.inspector{padding:14px;border:0}.metrics,.quadrants{grid-template-columns:1fr}.sub,.status{display:none}.map-canvas{min-height:300px}}
</style>
</head>

<body>
<div class="app">
  <header class="topbar">
    <div class="lockup"><div class="logo">P</div><div><div class="title">Brand Positioning Monitor</div><div class="sub">Luxury fragrance intelligence · Agentic scoring map</div></div></div>
    <div style="display:flex;gap:10px;align-items:center"><div class="status"><span class="status-dot"></span>Live dataset</div><button class="icon-btn active" id="toggle-drift" title="Toggle drift vectors"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg></button></div>
  </header>

  <div class="workspace">
    <aside class="rail">
      <section class="panel"><div class="panel-head"><div><div class="eyebrow">Dataset</div><div class="panel-title">Brands</div></div></div><div class="panel-body"><input class="search" id="brand-search" placeholder="Search brands"><div class="brand-list" id="brand-list"></div></div></section>
      <section class="panel"><div class="panel-head"><div><div class="eyebrow">Matrix</div><div class="panel-title">Axis Reading</div></div></div><div class="panel-body"><div class="axis-pill"><span>Dominance</span><span class="active">Vulnerability</span></div><div class="axis-pill" style="margin-top:8px"><span>Collective</span><span class="active">Private</span></div></div></section>
    </aside>

    <main class="stage">
      <section class="metrics"><div class="metric"><div class="metric-value" id="metric-count">0</div><div class="metric-label">Brands mapped</div></div><div class="metric"><div class="metric-value" id="metric-vp">0</div><div class="metric-label">Vulnerable private</div></div><div class="metric"><div class="metric-value" id="metric-drift">0</div><div class="metric-label">Historical vectors</div></div><div class="metric"><div class="metric-value">VARŌ</div><div class="metric-label">Verified whitespace</div></div></section>

      <section class="panel map-panel">
        <div class="map-toolbar"><div><h1>Perceptual Map — Luxury Fragrance 2025</h1><p>Click a node or brand row to inspect scoring logic, drift, and quadrant intelligence.</p></div><button class="icon-btn" id="clear-selection" title="Clear selection"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></button></div>
        <div class="canvas-wrap" id="map-container">
          <svg class="map-canvas" viewBox="0 0 760 440" id="map-svg">
            <defs><pattern id="grid" width="38" height="22" patternUnits="userSpaceOnUse"><path d="M38 0 L0 0 0 22" fill="none" stroke="rgba(255,255,255,.035)" stroke-width=".5"/></pattern><marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 Z" fill="rgba(255,204,102,.74)"/></marker></defs>
            <rect width="760" height="440" fill="#0b0d13"/><rect width="760" height="440" fill="url(#grid)"/><rect x="380" y="0" width="380" height="220" fill="rgba(255,204,102,.035)"/>
            <line x1="0" y1="220" x2="760" y2="220" stroke="rgba(255,255,255,.13)"/><line x1="380" y1="0" x2="380" y2="440" stroke="rgba(255,255,255,.13)"/>
            <text class="axis-label" x="18" y="214">DOMINANCE</text><text class="axis-label" x="742" y="214" text-anchor="end">VULNERABILITY</text><text class="axis-label" x="380" y="18" text-anchor="middle">PRIVATE TRUTH</text><text class="axis-label" x="380" y="427" text-anchor="middle">COLLECTIVE MYTH</text>
            <g id="drift-layer"><g id="drift-arrows"></g><g id="ghost-positions"></g></g><g id="brands-group"></g><circle id="pulse-ring" cx="-100" cy="-100" r="14" fill="none" stroke="rgba(255,204,102,.64)" stroke-width="1.5" opacity="0"/>
          </svg>
          <div class="tooltip" id="tooltip"><div class="tooltip-brand" id="tt-brand">—</div><div class="tooltip-row"><span>Voice</span><span class="tooltip-val" id="tt-x">—</span></div><div class="tooltip-row"><span>Narrative</span><span class="tooltip-val" id="tt-y">—</span></div></div>
        </div>
      </section>

      <section class="quadrants"><div class="quadrant"><div class="quadrant-name">Dominant · Private</div><div class="quadrant-brands" id="q-dp"></div></div><div class="quadrant highlight"><div class="quadrant-name">Vulnerable · Private</div><div class="quadrant-brands" id="q-vp"></div></div><div class="quadrant"><div class="quadrant-name">Dominant · Collective</div><div class="quadrant-brands" id="q-dc"></div></div><div class="quadrant"><div class="quadrant-name">Vulnerable · Collective</div><div class="quadrant-brands" id="q-vc"></div></div></section>

      <section class="panel" style="margin-top:14px"><div class="panel-head"><div><div class="eyebrow">Historical Drift</div><div class="panel-title">X Axis · 2021 to 2025</div></div></div><div class="panel-body"><div class="drift-bars" id="drift-bars"></div></div></section>

      <!-- INJECTED: MBA Strategic Briefing Section -->
      <section class="panel" style="margin-top:14px">
        <div class="panel-head">
          <div><div class="eyebrow">Executive Briefing</div><div class="panel-title">Strategic Architecture</div></div>
        </div>
        <div class="panel-body" style="font-size: 13px; line-height: 1.6; color: var(--muted);">
          <p style="margin-bottom: 16px; color: var(--text);">This analytical environment translates qualitative brand communications into empirical market coordinates. By evaluating ten luxury fragrance houses across two primary vectors, we expose hidden market saturation and isolate lucrative commercial white space.</p>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 16px;">
            <div>
              <strong style="color: var(--text); display: block; margin-bottom: 6px;">Tone of Voice (Dominance vs. Vulnerability)</strong>
              <p>This axis measures how the brand speaks to the consumer. Dominance is the voice of the monument. It relies on authority, legacy, and commands. Creed exemplifies this by projecting power through historical royal commissions. Vulnerability is the voice of the confidant. It strips away the pedestal in favor of intimacy, somatic language, and emotional exposure. Byredo captures this perfectly by exploring the raw fading of memory and the nakedness of skin.</p>
            </div>
            <div>
              <strong style="color: var(--text); display: block; margin-bottom: 6px;">Narrative Scope (Collective Myth vs. Private Truth)</strong>
              <p>This axis measures the world the brand invites you into. Collective Myth constructs a universal, shared cultural religion. Chanel No. 5 operates here, positioning itself not as a personal scent, but as a global institution. Private Truth addresses the hyper-specific inner life of the individual. Maison Margiela's Replica bottles the exact scent of a Brooklyn jazz club, reading like a personal diary entry rather than a public broadcast.</p>
            </div>
          </div>
          <div style="padding-top: 16px; border-top: 1px solid var(--line);">
            <strong style="color: var(--text); display: block; margin-bottom: 6px;">The Commercial Imperative</strong>
            <p>By plotting legacy competitors, a glaring structural void emerges in the High Vulnerability and High Private Truth quadrant. Most luxury houses remain trapped in Dominance and Collective Myth. The VARŌ concept is engineered specifically to exploit this exact whitespace, offering radical intimacy to a modern consumer who has outgrown traditional status signaling.</p>
          </div>
        </div>
      </section>
    </main>

    <aside class="inspector">
      <section class="panel"><div class="panel-head"><div><div class="eyebrow">Inspector</div><div class="panel-title">Selected Brand</div></div><span class="selected-pill" id="selected-pill">Select brand</span></div>
        <div class="panel-body"><div id="empty-state" class="empty">Select a brand to audit the AI reasoning and market position.</div>
          <div id="brand-detail" class="hidden">
            <div class="score-grid"><div class="score-card"><div class="score-label">X Score</div><div class="score-num" id="score-x">—</div><div class="score-axis-name" id="score-x-label">—</div><div class="score-bar-track"><div class="score-bar-fill" id="bar-x"></div></div></div><div class="score-card"><div class="score-label">Y Score</div><div class="score-num" id="score-y">—</div><div class="score-axis-name" id="score-y-label">—</div><div class="score-bar-track"><div class="score-bar-fill" id="bar-y"></div></div></div></div>
            <div class="insight"><div class="insight-title">Position Intelligence</div><div class="insight-heading" id="pi-quadrant">—</div><div class="insight-text" id="pi-text">—</div><div class="implication" id="pi-implication">—</div></div>
            <div class="insight accent"><div class="insight-title">Historical Drift</div><div class="insight-text" id="drift-insight-text">—</div></div>
            <div class="insight"><div class="insight-title">Agent 4 Critic Log</div><div class="quote" id="commentary-quote">—</div><div class="reasoning"><div class="reason-row"><span class="tag">X Axis</span><span class="reason-text" id="reasoning-x">—</span></div><div class="reason-row"><span class="tag">Y Axis</span><span class="reason-text" id="reasoning-y">—</span></div></div></div>
          </div>
        </div>
      </section>
    </aside>
  </div>
</div>

<script>
const brands = __DYNAMIC_BRANDS_PLACEHOLDER__;
const scores = __DYNAMIC_SCORES_PLACEHOLDER__;
const commentary = __DYNAMIC_COMMENTARY_PLACEHOLDER__;
const driftData = __DYNAMIC_DRIFT_PLACEHOLDER__;
const qi = {
 "dominant-collective":{label:"Dominant · Collective",text:"The densest competitive territory. Brands speak with institutional authority toward a broad cultural audience.",implication:"Drift deeper here increases collision risk."},
 "dominant-private":{label:"Dominant · Private",text:"A defensible position. The brand speaks with authority, but the address remains personal and selective.",implication:"Entry requires credible craft heritage."},
 "vulnerable-private":{label:"Vulnerable · Private",text:"The intimacy territory. Brands use memory, softness, and emotional specificity instead of overt authority.",implication:"VARŌ's chosen territory. High differentiation."},
 "vulnerable-collective":{label:"Vulnerable · Collective",text:"A rare structural gap where emotional openness meets shared cultural address.",implication:"Potential future expansion space."}
};
const esc=v=>String(v).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;");
const svg=document.getElementById("brands-group"), driftArrows=document.getElementById("drift-arrows"), ghosts=document.getElementById("ghost-positions"), list=document.getElementById("brand-list"), tooltip=document.getElementById("tooltip"), map=document.getElementById("map-container"), pulse=document.getElementById("pulse-ring");

function renderMap(){brands.forEach(b=>{const g=document.createElementNS("http://www.w3.org/2000/svg","g");g.classList.add("brand-node");g.dataset.brand=b.name;g.style.cursor="pointer";const label=esc(b.name==="VARO"?"VARŌ":b.name);g.innerHTML=b.isVaro?`<circle cx="${b.cx}" cy="${b.cy}" r="24" fill="rgba(255,204,102,.08)"/><circle cx="${b.cx}" cy="${b.cy}" r="15" fill="rgba(255,204,102,.12)"/><circle cx="${b.cx}" cy="${b.cy}" r="8" fill="#11141c" stroke="${b.color}" stroke-width="2"/><text x="${b.cx}" y="${b.cy-17}" font-family="Inter" font-size="10" font-weight="800" letter-spacing="1.4" fill="${b.color}" text-anchor="middle">${label}</text>`:`<circle cx="${b.cx}" cy="${b.cy}" r="9" fill="#11141c" stroke="${b.color}" stroke-width="1.6"/><circle cx="${b.cx}" cy="${b.cy}" r="3.6" fill="${b.color}"/><text x="${b.cx}" y="${b.cy-13}" font-family="Inter" font-size="8.2" font-weight="600" fill="rgba(247,247,251,.56)" text-anchor="middle">${label}</text>`;
if(b.x21!==null&&b.y21!==null){driftArrows.innerHTML+=`<line x1="${b.x21}" y1="${b.y21}" x2="${b.cx}" y2="${b.cy}" stroke="rgba(255,204,102,.36)" stroke-width="1.3" stroke-dasharray="4,4" marker-end="url(#arrowhead)"/>`;ghosts.innerHTML+=`<circle cx="${b.x21}" cy="${b.y21}" r="4.5" fill="none" stroke="rgba(247,247,251,.22)" stroke-dasharray="2,2"/>`}
g.onmouseenter=e=>showTip(e,b);g.onmousemove=moveTip;g.onmouseleave=()=>tooltip.classList.remove("visible");g.onclick=()=>selectBrand(b.name);svg.appendChild(g)})}
function renderList(f=""){list.innerHTML="";brands.filter(b=>b.name.toLowerCase().includes(f.toLowerCase())).forEach(b=>{const s=scores[b.name], el=document.createElement("div");el.className="brand-item";el.dataset.brand=b.name;el.innerHTML=`<div class="brand-dot" style="background:${b.color};color:${b.color}"></div><span class="brand-name">${esc(b.name==="VARO"?"VARŌ":b.name)}</span><span class="brand-coords">${s.x} · ${s.y}</span>`;el.onclick=()=>selectBrand(b.name);list.appendChild(el)})}
function renderDrift(){const el=document.getElementById("drift-bars");driftData.forEach(d=>{const r=document.createElement("div"), l=d.old!==null?Math.min(d.old,d.curr):d.curr,w=d.old!==null?Math.abs(d.curr-d.old):0;r.className="drift-row";r.dataset.brand=d.brand;r.innerHTML=`<span class="drift-brand-name">${esc(d.brand)}</span><div class="drift-track">${d.old!==null?`<div class="drift-old-marker" style="left:${d.old}%"></div>`:""}${w>0?`<div class="drift-connector" style="left:${l}%;width:${w}%"></div>`:""}<div class="drift-new-marker" style="left:${d.curr}%"></div></div><span class="drift-delta ${d.dir}">${esc(d.delta)}</span>`;r.onclick=()=>selectBrand(d.brand==="M. Margiela"?"Maison Margiela":d.brand);el.appendChild(r)})}
function renderQuadrants(){let dp=[],vp=[],dc=[],vc=[];brands.forEach(b=>{const s=scores[b.name],n=b.name==="VARO"?"VARŌ":b.name;if(s.x<5&&s.y<5)dc.push(n);else if(s.x<5&&s.y>=5)dp.push(n);else if(s.x>=5&&s.y<5)vc.push(n);else vp.push(n)});q_dc.textContent=dc.join(", ")||"Empty";q_dp.textContent=dp.join(", ")||"Empty";q_vc.textContent=vc.join(", ")||"Empty";q_vp.textContent=vp.join(", ")||"Empty";document.getElementById("metric-count").textContent=brands.length;document.getElementById("metric-vp").textContent=vp.length;document.getElementById("metric-drift").textContent=driftData.filter(d=>d.old!==null).length}
function selectBrand(name){const b=brands.find(x=>x.name===name),s=scores[name],c=commentary[name];if(!b)return;const key=`${s.x>=5?"vulnerable":"dominant"}-${s.y>=5?"private":"collective"}`,info=qi[key];document.querySelectorAll(".brand-item").forEach(e=>e.classList.toggle("selected-focus",e.dataset.brand===name));document.querySelectorAll(".brand-node").forEach(e=>e.style.opacity=e.dataset.brand===name?"1":".24");document.querySelectorAll(".drift-row").forEach(e=>e.classList.toggle("highlighted",e.dataset.brand===name||e.dataset.brand===(name==="Maison Margiela"?"M. Margiela":name)));pulse.setAttribute("cx",b.cx);pulse.setAttribute("cy",b.cy);pulse.setAttribute("opacity","1");selected_pill.textContent=name==="VARO"?"VARŌ":name;empty_state.classList.add("hidden");brand_detail.classList.remove("hidden");score_x.textContent=s.x;score_y.textContent=s.y;score_x_label.textContent=s.xLabel;score_y_label.textContent=s.yLabel;bar_x.style.width=s.x*10+"%";bar_y.style.width=s.y*10+"%";pi_quadrant.textContent=info.label;pi_text.textContent=info.text;pi_implication.textContent=info.implication;drift_insight_text.innerHTML=esc(c.drift_insight).replace("Insight:","<br><br><strong style='color:var(--gold)'>Insight:</strong>");commentary_quote.textContent=c.quote;reasoning_x.textContent=c.rx;reasoning_y.textContent=c.ry}
function clearSel(){document.querySelectorAll(".brand-node").forEach(e=>e.style.opacity="1");document.querySelectorAll(".brand-item,.drift-row").forEach(e=>e.classList.remove("selected-focus","highlighted"));pulse.setAttribute("opacity","0");selected_pill.textContent="Select brand";empty_state.classList.remove("hidden");brand_detail.classList.add("hidden")}
function showTip(e,b){const s=scores[b.name];tt_brand.textContent=b.name==="VARO"?"VARŌ":b.name;tt_x.textContent=s.x+" / 10";tt_y.textContent=s.y+" / 10";tooltip.classList.add("visible");moveTip(e)}
function moveTip(e){const r=map.getBoundingClientRect();let l=e.clientX-r.left+14,t=e.clientY-r.top+14;if(l+190>r.width)l-=204;tooltip.style.left=l+"px";tooltip.style.top=t+"px"}
document.getElementById("toggle-drift").onclick=function(){this.classList.toggle("active");drift_layer.style.display=this.classList.contains("active")?"block":"none"}
document.getElementById("clear-selection").onclick=clearSel;document.getElementById("brand-search").oninput=e=>renderList(e.target.value);document.getElementById("map-svg").onclick=e=>{if(!e.target.closest(".brand-node"))clearSel()}
const q_dc=document.getElementById("q-dc"),q_dp=document.getElementById("q-dp"),q_vc=document.getElementById("q-vc"),q_vp=document.getElementById("q-vp"),selected_pill=document.getElementById("selected-pill"),empty_state=document.getElementById("empty-state"),brand_detail=document.getElementById("brand-detail"),score_x=document.getElementById("score-x"),score_y=document.getElementById("score-y"),score_x_label=document.getElementById("score-x-label"),score_y_label=document.getElementById("score-y-label"),bar_x=document.getElementById("bar-x"),bar_y=document.getElementById("bar-y"),pi_quadrant=document.getElementById("pi-quadrant"),pi_text=document.getElementById("pi-text"),pi_implication=document.getElementById("pi-implication"),drift_insight_text=document.getElementById("drift-insight-text"),commentary_quote=document.getElementById("commentary-quote"),reasoning_x=document.getElementById("reasoning-x"),reasoning_y=document.getElementById("reasoning-y"),drift_layer=document.getElementById("drift-layer");
renderMap();renderList();renderDrift();renderQuadrants();
</script>
</body>
</html>
"""

st.components.v1.html(
    custom_html_template.replace("__DYNAMIC_BRANDS_PLACEHOLDER__", json.dumps(js_brands))
    .replace("__DYNAMIC_SCORES_PLACEHOLDER__", json.dumps(js_scores))
    .replace("__DYNAMIC_COMMENTARY_PLACEHOLDER__", json.dumps(js_commentary))
    .replace("__DYNAMIC_DRIFT_PLACEHOLDER__", json.dumps(js_drift)),
    height=950,
    scrolling=True
)