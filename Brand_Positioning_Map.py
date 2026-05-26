import streamlit as st
import streamlit.components.v1 as components
import json
import os

# --- 1. STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Brand Positioning Monitor", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .block-container { padding: 0rem; max-width: 100%; }
        header, #MainMenu, footer {visibility: hidden;}
        iframe { border: none; }
    </style>
""", unsafe_allow_html=True)


# --- 2. OS-AGNOSTIC DATA ROUTING ---
def get_valid_path(*paths):
    for path in paths:
        if os.path.exists(path):
            return path
    return paths[0]


scores_path = get_valid_path("data/scores/final_brand_scores.json", "Data/Scores/final_brand_scores.json",
                             "Data/scores/final_brand_scores.json")
hist_path = get_valid_path("data/scores/historical_scores.json", "Data/Scores/historical_scores.json",
                           "Data/scores/historical_scores.json")
kb_path = get_valid_path("data/knowledge_base/brand_data.json", "Data/Knowledge_base/brand_data.json",
                         "Data/knowledge_base/brand_data.json")

if not os.path.exists(scores_path):
    st.error(f"Cloud Deployment Error: The Linux server cannot find the scores file.")
    st.stop()

with open(scores_path, "r", encoding="utf-8") as f:
    live_scores = json.load(f)

if os.path.exists(hist_path):
    with open(hist_path, "r", encoding="utf-8") as f:
        hist_scores = json.load(f)
else:
    hist_scores = {}

color_map = {
    "Chanel": "#e8e4dc", "Hermès": "#d4a090", "YSL": "#c4a0d4", "Maison Margiela": "#b8a0d4",
    "Jean Paul Gaultier": "#90c0d4", "Viktor & Rolf": "#90d4a8", "Mancera": "#d4d090",
    "Creed": "#d4c490", "Byredo": "#90a8d4", "VARŌ": "#c9a96e", "VARO": "#c9a96e"
}

# THE NEW STRATEGIC INSIGHTS DICTIONARY
drift_insights = {
    "Chanel": "Immovable monument. Near-zero drift over 4 years. Insight: Chanel acts as the category's gravitational anchor, relying on absolute consistency rather than adaptation to maintain unquestioned legacy status.",
    "Hermès": "Minor regression. A slight tightening of its poetic, nature-driven narrative into more structured prestige. Insight: Hermès maintains its core elemental identity while subtly reinforcing its institutional dominance.",
    "YSL": "Massive repositioning. Pivoted from intimate, nocturnal seduction (Black Opium) to hyper-dominant, daytime defiance (Libre). Insight: A deliberate corporate strategy to abandon intimacy and capture a younger, bolder demographic through collective empowerment.",
    "Maison Margiela": "Highly defensible stability. Marginal drift toward the center. Insight: Despite corporate ownership, the brand has fiercely protected its hyper-specific 'memory' whitespace, resisting the urge to build monolithic myths.",
    "Jean Paul Gaultier": "Deepening of the spectacle. Drifted further into collective myth. Insight: JPG is actively doubling down on performative identity and theatrical archetypes, entirely rejecting the modern trend toward vulnerability.",
    "Viktor & Rolf": "Sustained performance. Minor drift toward dominance. Insight: The brand continues to rely on avant-garde fantasy and maximalism, operating purely as an outward-facing spectacle with no attempt at consumer intimacy.",
    "Mancera": "Solidified gatekeeping. Remained anchored in its niche. Insight: Stable positioning relying on absolute exclusivity and raw ingredient prestige rather than attempting broader cultural relevance.",
    "Creed": "Doubling down on dynastic dominance. Further entrenched in historical legacy. Insight: Creed completely ignores modern demands for transparency or vulnerability, relying entirely on royal artisan heritage to justify price premiums.",
    "Byredo": "Indie-to-Corporate Lifecycle. Noticeable drift away from extreme private truth toward the center. Insight: Post-acquisition scaling requires broader cultural appeal; Byredo is slightly diluting its 'founder diary' intimacy to support global mass-market distribution.",
    "VARŌ": "New Entrant. Zero historical drift. Insight: Engineered specifically to capture the extreme Vulnerability/Private Truth whitespace that brands like YSL and Byredo abandoned as they scaled.",
    "VARO": "New Entrant. Zero historical drift. Insight: Engineered specifically to capture the extreme Vulnerability/Private Truth whitespace that brands like YSL and Byredo abandoned as they scaled."
}

js_brands = []
js_scores = {}
js_commentary = {}
js_drift = []

for brand, data in live_scores.items():
    x = data.get("x_score", 5.0)
    y = data.get("y_score", 5.0)

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
            "old": round(hx_raw * 10, 1),
            "curr": round(x * 10, 1),
            "delta": delta_str,
            "dir": dir_str
        })
    else:
        js_drift.append({
            "brand": "VARŌ" if brand == "VARO" else brand,
            "old": None,
            "curr": round(x * 10, 1),
            "delta": "New",
            "dir": ""
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

# --- 3. THE HTML TEMPLATE ---
custom_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Brand Positioning Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=DM+Sans:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --glass-bg: rgba(255,255,255,0.04);
    --glass-border: rgba(255,255,255,0.10);
    --glass-hover: rgba(255,255,255,0.07);
    --blur: blur(24px);
    --gold: #c9a96e;
    --gold-dim: rgba(201,169,110,0.3);
    --white: #f4f0ea;
    --white-dim: rgba(244,240,234,0.45);
    --white-faint: rgba(244,240,234,0.15);
    --bg: #080a0f;
    --text-primary: #f4f0ea;
    --text-secondary: rgba(244,240,234,0.55);
    --text-tertiary: rgba(244,240,234,0.28);
    --radius: 16px;
    --radius-sm: 10px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
  }
  body::before {
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 50% at 20% 10%, rgba(201,169,110,0.06) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 80%, rgba(100,120,180,0.05) 0%, transparent 55%),
      radial-gradient(ellipse 50% 60% at 50% 50%, rgba(255,255,255,0.02) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }
  body > * { position: relative; z-index: 1; }

  nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.25rem 2.5rem;
    background: rgba(8,10,15,0.7);
    backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur);
    border-bottom: 1px solid var(--glass-border);
    position: sticky; top: 0; z-index: 100;
  }
  .nav-brand { display: flex; flex-direction: column; gap: 1px; }
  .nav-brand-name { font-family: 'Cormorant Garamond', serif; font-size: 18px; font-weight: 400; letter-spacing: 0.08em; color: var(--white); }
  .nav-brand-sub { font-size: 9px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--gold); font-weight: 300; }

  .layout {
    display: grid;
    grid-template-columns: 260px 1fr 320px;
    min-height: calc(100vh - 65px);
  }

  .sidebar-left {
    border-right: 1px solid var(--glass-border);
    padding: 1.5rem 1.25rem;
    background: rgba(8,10,15,0.5);
    backdrop-filter: var(--blur);
    display: flex; flex-direction: column; gap: 1.5rem;
    overflow-y: auto;
  }

  .section-label {
    font-size: 9px; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--text-tertiary); margin-bottom: 0.6rem; font-weight: 400;
  }

  .glass-card {
    background: var(--glass-bg); border: 1px solid var(--glass-border);
    border-radius: var(--radius); backdrop-filter: var(--blur);
  }

  .brand-list { display: flex; flex-direction: column; gap: 3px; }
  .brand-item {
    display: flex; align-items: center; gap: 9px;
    padding: 8px 10px; border-radius: var(--radius-sm);
    cursor: pointer; transition: all 0.15s;
    border: 1px solid transparent;
  }
  .brand-item:hover { background: var(--glass-hover); }
  .brand-item.selected-focus { background: rgba(201,169,110,0.06); border-color: var(--gold-dim); }
  .brand-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
  .brand-item-name { font-size: 11.5px; font-weight: 300; color: var(--text-secondary); flex: 1; transition: color 0.15s; }
  .brand-item.selected-focus .brand-item-name { color: var(--gold); }
  .brand-coords { font-size: 9px; color: var(--text-tertiary); font-family: 'Cormorant Garamond', serif; }
  .brand-item.selected-focus .brand-coords { color: var(--gold-dim); }

  .toggle-row { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--glass-border); }
  .toggle-row:last-child { border-bottom: none; }
  .toggle-label { font-size: 11px; font-weight: 300; color: var(--text-secondary); letter-spacing: 0.03em; }
  .toggle { width: 34px; height: 19px; background: rgba(255,255,255,0.08); border-radius: 100px; position: relative; cursor: pointer; border: 1px solid var(--glass-border); transition: all 0.2s; }
  .toggle.on { background: rgba(201,169,110,0.25); border-color: var(--gold-dim); }
  .toggle::after { content: ''; position: absolute; width: 13px; height: 13px; border-radius: 50%; background: rgba(255,255,255,0.4); top: 2px; left: 2px; transition: all 0.2s; }
  .toggle.on::after { left: 17px; background: var(--gold); }

  .axis-block { padding: 12px; border-radius: var(--radius-sm); border: 1px solid var(--glass-border); background: var(--glass-bg); margin-bottom: 7px; }
  .axis-name { font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gold); margin-bottom: 5px; font-weight: 400; }
  .axis-poles { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
  .axis-pole { font-size: 10.5px; color: var(--text-secondary); font-weight: 300; }
  .axis-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--glass-border), var(--gold-dim), var(--glass-border)); margin: 0 8px; }

  .main-map {
    border-right: 1px solid var(--glass-border);
    padding: 1.5rem;
    display: flex; flex-direction: column; gap: 1.25rem;
    overflow-y: auto;
    background: rgba(6,8,13,0.3);
  }

  .map-header { display: flex; align-items: flex-start; justify-content: space-between; }
  .map-title { font-family: 'Cormorant Garamond', serif; font-size: 20px; font-weight: 300; color: var(--white); }
  .map-subtitle { font-size: 10px; color: var(--text-tertiary); margin-top: 2px; letter-spacing: 0.06em; font-weight: 300; }

  .map-container {
    background: var(--glass-bg); border: 1px solid var(--glass-border);
    border-radius: var(--radius); backdrop-filter: var(--blur);
    padding: 1.5rem; position: relative; overflow: hidden;
  }
  .map-canvas { width: 100%; height: 100%; }

  .tooltip {
    position: absolute;
    background: rgba(10,13,20,0.95); backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border); border-radius: var(--radius-sm);
    padding: 11px 13px; pointer-events: none; opacity: 0;
    transition: opacity 0.12s; z-index: 50; min-width: 150px;
  }
  .tooltip.visible { opacity: 1; }
  .tooltip-brand { font-family: 'Cormorant Garamond', serif; font-size: 14px; font-weight: 400; color: var(--white); margin-bottom: 5px; }
  .tooltip-row { display: flex; justify-content: space-between; font-size: 9.5px; color: var(--text-tertiary); margin-bottom: 2px; gap: 12px; }
  .tooltip-val { color: var(--text-secondary); }

  .quadrant-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 7px; }
  .quadrant-card {
    padding: 12px; border-radius: var(--radius-sm);
    border: 1px solid var(--glass-border); background: var(--glass-bg);
  }
  .quadrant-card.highlight { border-color: var(--gold-dim); background: rgba(201,169,110,0.05); }
  .quadrant-name { font-size: 9px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 3px; }
  .quadrant-brands { font-size: 11px; color: var(--text-secondary); font-weight: 300; line-height: 1.5; }

  .drift-section { background: var(--glass-bg); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 1.25rem; }
  .drift-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
  .drift-title { font-size: 9px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--text-tertiary); }
  .drift-legend { display: flex; gap: 1rem; align-items: center; }
  .legend-item { display: flex; align-items: center; gap: 5px; font-size: 9.5px; color: var(--text-tertiary); }
  .legend-dot-old { width: 5px; height: 5px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.25); }
  .legend-dot-new { width: 7px; height: 7px; border-radius: 50%; background: var(--gold); }
  .drift-bars { display: flex; flex-direction: column; gap: 9px; }
  .drift-row { display: grid; grid-template-columns: 100px 1fr 44px; align-items: center; gap: 10px; padding: 4px 6px; border-radius: 6px; transition: background 0.15s; }
  .drift-row.highlighted { background: rgba(201,169,110,0.05); }
  .drift-brand-name { font-size: 10.5px; color: var(--text-secondary); font-weight: 300; }
  .drift-track { height: 3px; background: rgba(255,255,255,0.04); border-radius: 2px; position: relative; }
  .drift-old-marker { position: absolute; height: 9px; width: 1.5px; background: rgba(255,255,255,0.2); top: -3px; border-radius: 1px; }
  .drift-new-marker { position: absolute; height: 9px; width: 2.5px; background: var(--gold); top: -3px; border-radius: 1px; }
  .drift-connector { position: absolute; height: 2px; top: 0.5px; background: linear-gradient(90deg, rgba(255,255,255,0.1), var(--gold-dim)); }
  .drift-delta { font-size: 9.5px; font-family: 'Cormorant Garamond', serif; color: var(--text-tertiary); text-align: right; }
  .drift-delta.up { color: #8fc47a; }
  .drift-delta.down { color: #c47a7a; }

  .whitespace-alert {
    background: linear-gradient(135deg, rgba(201,169,110,0.05) 0%, rgba(201,169,110,0.02) 100%);
    border: 1px solid var(--gold-dim); border-radius: var(--radius);
    padding: 1.1rem 1.25rem; display: flex; gap: 0.9rem; align-items: flex-start;
  }
  .alert-title { font-size: 9px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--gold); margin-bottom: 4px; }
  .alert-text { font-family: 'Cormorant Garamond', serif; font-size: 12.5px; font-style: italic; color: var(--text-secondary); line-height: 1.7; }

  /* RIGHT PANEL */
  .panel-right {
    padding: 1.5rem 1.25rem;
    background: rgba(8,10,15,0.5);
    backdrop-filter: var(--blur);
    display: flex; flex-direction: column; gap: 1.25rem;
    overflow-y: auto;
  }

  .score-block {
    background: var(--glass-bg); border: 1px solid var(--glass-border);
    border-radius: var(--radius); padding: 1.25rem;
  }
  .score-block.has-selection { border-color: var(--gold-dim); }
  .score-block-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
  .score-block-label { font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-tertiary); }
  .selected-brand-pill {
    font-family: 'Cormorant Garamond', serif; font-size: 14px;
    padding: 3px 12px; border-radius: 100px;
    background: rgba(201,169,110,0.1); border: 1px solid var(--gold-dim); color: var(--gold);
  }

  .score-row { display: flex; gap: 1.25rem; margin-bottom: 1rem; }
  .score-item { flex: 1; }
  .score-item-label { font-size: 8.5px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--text-tertiary); margin-bottom: 3px; }
  .score-num { font-family: 'Cormorant Garamond', serif; font-size: 38px; font-weight: 300; color: var(--white); line-height: 1; }
  .score-axis-name { font-size: 9.5px; color: var(--text-tertiary); font-style: italic; font-family: 'Cormorant Garamond', serif; margin-top: 2px; }
  .score-bar-track { width: 100%; height: 2.5px; background: rgba(255,255,255,0.05); border-radius: 2px; overflow: hidden; margin-top: 8px; }
  .score-bar-fill { height: 100%; border-radius: 2px; background: linear-gradient(90deg, var(--gold-dim), var(--gold)); transition: width 0.6s cubic-bezier(0.4,0,0.2,1); }

  .position-insight {
    background: linear-gradient(135deg, rgba(201,169,110,0.05) 0%, rgba(201,169,110,0.02) 100%);
    border: 1px solid rgba(201,169,110,0.15); border-radius: var(--radius-sm);
    padding: 1rem; margin-top: 0.75rem;
  }
  .position-insight-header { font-size: 8.5px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold); margin-bottom: 6px; }
  .position-insight-quadrant { font-family: 'Cormorant Garamond', serif; font-size: 13px; font-style: italic; color: var(--white); margin-bottom: 8px; }
  .position-insight-text { font-size: 11px; color: var(--text-secondary); line-height: 1.65; font-weight: 300; }

  /* NEW DRIFT INSIGHT CARD */
  .drift-insight-block {
    background: var(--glass-bg); border: 1px solid var(--glass-border);
    border-radius: var(--radius); padding: 1.25rem; display: flex; flex-direction: column; gap: 0.9rem;
    position: relative; overflow: hidden;
  }
  .drift-insight-block::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--gold); opacity: 0.7;
  }
  .drift-insight-label { font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-tertiary); }
  .drift-insight-text { font-size: 11px; color: var(--white); line-height: 1.65; font-weight: 300; }

  .commentary-block {
    background: var(--glass-bg); border: 1px solid var(--glass-border);
    border-radius: var(--radius); padding: 1.25rem; display: flex; flex-direction: column; gap: 0.9rem;
  }
  .commentary-label { font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--text-tertiary); }
  .commentary-quote {
    font-family: 'Cormorant Garamond', serif; font-size: 13.5px; font-weight: 300; font-style: italic; color: var(--text-secondary); line-height: 1.75;
    border-left: 1px solid var(--gold-dim); padding-left: 0.9rem;
  }
  .reasoning-list { display: flex; flex-direction: column; gap: 7px; }
  .reasoning-row { display: flex; gap: 8px; align-items: flex-start; }
  .reasoning-tag { font-size: 7.5px; letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; white-space: nowrap; margin-top: 2px; }
  .tag-x { background: rgba(201,169,110,0.1); color: var(--gold); border: 1px solid rgba(201,169,110,0.2); }
  .tag-y { background: rgba(160,185,220,0.1); color: #a0b9dc; border: 1px solid rgba(160,185,220,0.2); }
  .reasoning-text { font-size: 10.5px; color: var(--text-secondary); line-height: 1.6; font-weight: 300; }

  .empty-state { text-align: center; padding: 2rem 1rem; }
  .empty-state-icon { font-size: 28px; color: var(--text-tertiary); margin-bottom: 0.75rem; }
  .empty-state-text { font-family: 'Cormorant Garamond', serif; font-size: 14px; font-style: italic; color: var(--text-tertiary); line-height: 1.6; }
</style>
</head>
<body>

<nav>
  <div class="nav-brand">
    <span class="nav-brand-name">Positioning Monitor</span>
    <span class="nav-brand-sub">Luxury Fragrance Intelligence</span>
  </div>
  <ul class="nav-links">
    <li><a href="#" class="active">Agentic Scoring Map</a></li>
  </ul>
</nav>

<div class="layout">

  <!-- LEFT SIDEBAR -->
  <aside class="sidebar-left">
    <div>
      <div class="section-label">Brands on Map</div>
      <div class="brand-list" id="brand-list"></div>
    </div>
    <div>
      <div class="section-label">Display</div>
      <div class="glass-card" style="padding: 2px 12px;">
        <div class="toggle-row">
          <span class="toggle-label">Drift arrows (2021)</span>
          <div class="toggle on" id="toggle-drift"></div>
        </div>
      </div>
    </div>
    <div>
      <div class="section-label">Axes Matrix</div>
      <div class="axis-block">
        <div class="axis-name">X — Tone of Voice</div>
        <div class="axis-poles"><span class="axis-pole">Dominance</span><div class="axis-line"></div><span class="axis-pole">Vulnerability</span></div>
      </div>
      <div class="axis-block">
        <div class="axis-name">Y — Narrative Scope</div>
        <div class="axis-poles"><span class="axis-pole">Collective</span><div class="axis-line"></div><span class="axis-pole">Private</span></div>
      </div>
    </div>
  </aside>

  <!-- MAIN MAP -->
  <main class="main-map">
    <div class="map-header">
      <div>
        <div class="map-title">Perceptual Map — Luxury Fragrance 2025</div>
        <div class="map-subtitle">Click any brand node to audit Agent 4 execution logic</div>
      </div>
    </div>

    <!-- MAP -->
    <div class="map-container" id="map-container">
      <svg class="map-canvas" viewBox="0 0 760 440" id="map-svg" style="display:block;">
        <defs>
          <pattern id="grid" width="76" height="44" patternUnits="userSpaceOnUse">
            <path d="M 76 0 L 0 0 0 44" fill="none" stroke="rgba(255,255,255,0.028)" stroke-width="0.5"/>
          </pattern>
          <marker id="arrowhead" markerWidth="5" markerHeight="5" refX="4.5" refY="2.5" orient="auto">
            <path d="M0,0 L0,5 L5,2.5 Z" fill="rgba(201,169,110,0.55)"/>
          </marker>
          <filter id="glow-gold"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>

        <rect width="760" height="440" fill="url(#grid)"/>
        <rect x="380" y="0" width="380" height="220" fill="rgba(201,169,110,0.012)"/>

        <!-- Axes -->
        <line x1="0" y1="220" x2="760" y2="220" stroke="rgba(255,255,255,0.1)" stroke-width="0.8"/>
        <line x1="380" y1="0" x2="380" y2="440" stroke="rgba(255,255,255,0.1)" stroke-width="0.8"/>

        <text x="12" y="215" font-family="DM Sans,sans-serif" font-size="8.5" font-weight="300" letter-spacing="2.5" fill="rgba(255,255,255,0.2)" text-anchor="start">DOMINANCE</text>
        <text x="748" y="215" font-family="DM Sans,sans-serif" font-size="8.5" font-weight="300" letter-spacing="2.5" fill="rgba(255,255,255,0.2)" text-anchor="end">VULNERABILITY</text>
        <text x="380" y="14" font-family="DM Sans,sans-serif" font-size="8.5" font-weight="300" letter-spacing="2.5" fill="rgba(255,255,255,0.2)" text-anchor="middle">PRIVATE TRUTH</text>
        <text x="380" y="434" font-family="DM Sans,sans-serif" font-size="8.5" font-weight="300" letter-spacing="2.5" fill="rgba(255,255,255,0.2)" text-anchor="middle">COLLECTIVE MYTH</text>

        <!-- Drift Layer -->
        <g id="drift-layer" style="display: block;">
            <g id="drift-arrows"></g>
            <g id="ghost-positions"></g>
        </g>

        <!-- Brand nodes -->
        <g id="brands-group"></g>

        <!-- Pulse ring -->
        <circle id="pulse-ring" cx="-100" cy="-100" r="14" fill="none" stroke="rgba(201,169,110,0.4)" stroke-width="1.5" opacity="0"/>
      </svg>

      <div class="tooltip" id="tooltip">
        <div class="tooltip-brand" id="tt-brand">—</div>
        <div class="tooltip-row"><span>Voice register</span><span class="tooltip-val" id="tt-x">—</span></div>
        <div class="tooltip-row"><span>Address</span><span class="tooltip-val" id="tt-y">—</span></div>
      </div>
    </div>

    <!-- Quadrant distribution -->
    <div>
      <div class="section-label" style="margin-bottom:0.6rem">Quadrant Summary</div>
      <div class="quadrant-grid">
        <div class="quadrant-card">
          <div class="quadrant-name">Dominant · Private</div>
          <div class="quadrant-brands" id="q-dp">Loading...</div>
        </div>
        <div class="quadrant-card highlight">
          <div class="quadrant-name">Vulnerable · Private ✦</div>
          <div class="quadrant-brands" id="q-vp">Loading...</div>
        </div>
        <div class="quadrant-card">
          <div class="quadrant-name">Dominant · Collective</div>
          <div class="quadrant-brands" id="q-dc">Loading...</div>
        </div>
        <div class="quadrant-card">
          <div class="quadrant-name">Vulnerable · Collective</div>
          <div class="quadrant-brands" id="q-vc">Loading...</div>
        </div>
      </div>
    </div>

    <!-- Drift Bar Chart -->
    <div class="drift-section">
      <div class="drift-header">
        <span class="drift-title">Drift Analysis — X Axis 2021 → 2025</span>
        <div class="drift-legend">
          <div class="legend-item"><div class="legend-dot-old"></div><span>2021</span></div>
          <div class="legend-item"><div class="legend-dot-new"></div><span>2025</span></div>
        </div>
      </div>
      <div class="drift-bars" id="drift-bars"></div>
    </div>

    <div class="whitespace-alert" style="margin-top: 20px;">
      <div class="alert-icon">◈</div>
      <div>
        <div class="alert-title">Agent 4 Verified White Space</div>
        <div class="alert-text">
          VARŌ is successfully positioned in the furthest extreme of the Vulnerable / Private quadrant. Competitors mapped strictly to Dominance, leaving intimacy highly unsaturated.
        </div>
      </div>
    </div>
  </main>

  <!-- RIGHT PANEL -->
  <aside class="panel-right">

    <div class="score-block" id="score-block">
      <div class="score-block-header">
        <span class="score-block-label">Selected Brand</span>
        <span class="selected-brand-pill" id="selected-pill">— Select a brand</span>
      </div>

      <div id="empty-state" class="empty-state">
        <div class="empty-state-icon">◎</div>
        <div class="empty-state-text">Click any brand node on the map to audit the AI execution logic.</div>
      </div>

      <div id="brand-detail" style="display:none;">
        <div class="score-row">
          <div class="score-item">
            <div class="score-item-label">X Score</div>
            <div class="score-num" id="score-x">—</div>
            <div class="score-axis-name" id="score-x-label">—</div>
            <div class="score-bar-track"><div class="score-bar-fill" id="bar-x" style="width:0%"></div></div>
          </div>
          <div class="score-item">
            <div class="score-item-label">Y Score</div>
            <div class="score-num" id="score-y">—</div>
            <div class="score-axis-name" id="score-y-label">—</div>
            <div class="score-bar-track"><div class="score-bar-fill" id="bar-y" style="width:0%"></div></div>
          </div>
        </div>

        <div class="position-insight" id="position-insight">
          <div class="position-insight-header">Position Intelligence</div>
          <div class="position-insight-quadrant" id="pi-quadrant">—</div>
          <div class="position-insight-text" id="pi-text">—</div>
          <div class="insight-stat">
            <span class="insight-stat-icon">→</span>
            <span class="insight-stat-text" id="pi-implication">—</span>
          </div>
        </div>
      </div>
    </div>

    <!-- NEW: STRATEGIC DRIFT INSIGHT CARD -->
    <div class="drift-insight-block" id="drift-insight-block" style="display:none;">
      <div class="drift-insight-label">Historical Drift (2021 → 2025)</div>
      <div class="drift-insight-text" id="drift-insight-text">—</div>
    </div>

    <!-- Commentary -->
    <div class="commentary-block" id="commentary-block">
      <div class="commentary-label">Agent 4 (Critic) Execution Log</div>
      <div id="commentary-empty" style="font-size:11px; color:var(--text-tertiary); font-style:italic; font-family:'Cormorant Garamond',serif; line-height:1.6;">
        Select a brand to read the AI's reasoning for its position.
      </div>
      <div id="commentary-content" style="display:none;">
        <div class="commentary-quote" id="commentary-quote">—</div>
        <div class="reasoning-list" style="margin-top: 15px;">
          <div class="reasoning-row">
            <span class="reasoning-tag tag-x">Agent 3 (X)</span>
            <span class="reasoning-text" id="reasoning-x">—</span>
          </div>
          <div class="reasoning-row">
            <span class="reasoning-tag tag-y">Agent 3 (Y)</span>
            <span class="reasoning-text" id="reasoning-y">—</span>
          </div>
        </div>
      </div>
    </div>

  </aside>
</div>

<script>
// --- INJECTED DYNAMIC DATA FROM PYTHON ---
const brands = __DYNAMIC_BRANDS_PLACEHOLDER__;
const scores = __DYNAMIC_SCORES_PLACEHOLDER__;
const commentary = __DYNAMIC_COMMENTARY_PLACEHOLDER__;
const driftData = __DYNAMIC_DRIFT_PLACEHOLDER__;

// ── RENDER BRAND NODES & DRIFT ARROWS ──
const svg = document.getElementById('brands-group');
const driftArrowsGroup = document.getElementById('drift-arrows');
const ghostPositionsGroup = document.getElementById('ghost-positions');

brands.forEach((b, i) => {
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.setAttribute("class", "brand-node");
  g.setAttribute("data-brand", b.name);
  g.style.cursor = "pointer";

  if (b.isVaro) {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="20" fill="rgba(201,169,110,0.04)"/>
      <circle cx="${b.cx}" cy="${b.cy}" r="13" fill="rgba(201,169,110,0.07)"/>
      <circle cx="${b.cx}" cy="${b.cy}" r="26" fill="none" stroke="rgba(201,169,110,0.1)" stroke-width="1" stroke-dasharray="3,4"/>
      <circle cx="${b.cx}" cy="${b.cy}" r="9" fill="rgba(16,12,6,0.85)" stroke="${b.color}" stroke-width="1.5"/>
      <text x="${b.cx}" y="${b.cy-14}" font-family="Cormorant Garamond,serif" font-size="10.5" font-style="italic" font-weight="400" letter-spacing="2" fill="rgba(201,169,110,0.85)" text-anchor="middle">VARŌ</text>
    `;
  } else {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="9" fill="rgba(18,22,30,0.7)" stroke="${b.color}" stroke-width="1.2" opacity="0.85"/>
      <circle cx="${b.cx}" cy="${b.cy}" r="4" fill="${b.color}" opacity="0.9"/>
      <text x="${b.cx}" y="${b.cy-12}" font-family="DM Sans,sans-serif" font-size="8" font-weight="300" letter-spacing="1.2" fill="rgba(255,255,255,0.45)" text-anchor="middle">${b.name}</text>
    `;
  }

  // Draw Drift Vectors
  if (b.x21 !== null && b.y21 !== null) {
      driftArrowsGroup.innerHTML += `<line x1="${b.x21}" y1="${b.y21}" x2="${b.cx}" y2="${b.cy}" stroke="rgba(201,169,110,0.3)" stroke-width="1.2" stroke-dasharray="3,3" marker-end="url(#arrowhead)"/>`;
      ghostPositionsGroup.innerHTML += `<circle cx="${b.x21}" cy="${b.y21}" r="4.5" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1" stroke-dasharray="2,2"/>`;
  }

  g.addEventListener('mouseenter', (e) => showTooltip(e, b));
  g.addEventListener('mousemove', (e) => moveTooltip(e));
  g.addEventListener('mouseleave', () => hideTooltip());
  g.addEventListener('click', () => selectBrand(b.name));
  svg.appendChild(g);
});

// ── DRIFT TOGGLE ──
const driftToggle = document.getElementById('toggle-drift');
const driftLayer = document.getElementById('drift-layer');
driftToggle.addEventListener('click', function() {
  this.classList.toggle('on');
  driftLayer.style.display = this.classList.contains('on') ? 'block' : 'none';
});

// ── DRIFT BARS ──
const driftEl = document.getElementById('drift-bars');
driftData.forEach(d => {
  const row = document.createElement('div');
  row.className = 'drift-row';
  row.dataset.brand = d.brand;
  const connLeft = d.old !== null ? Math.min(d.old, d.curr) : d.curr;
  const connW = d.old !== null ? Math.abs(d.curr - d.old) : 0;
  row.innerHTML = `
    <span class="drift-brand-name">${d.brand}</span>
    <div class="drift-track">
      ${d.old !== null ? `<div class="drift-old-marker" style="left:${d.old}%"></div>` : ''}
      ${connW > 0 ? `<div class="drift-connector" style="left:${connLeft}%;width:${connW}%"></div>` : ''}
      <div class="drift-new-marker" style="left:${d.curr}%"></div>
    </div>
    <span class="drift-delta ${d.dir}">${d.delta}</span>
  `;
  driftEl.appendChild(row);
});

const quadrantIntelligence = {
  "dominant-collective": {
    label: "Dominant · Collective",
    text: "The most populated territory. Brands here speak with institutional authority toward a broad cultural audience. High collision risk — differentiation is hard when everyone speaks the language of legacy.",
    implication: "Brands drifting deeper here risk commoditisation."
  },
  "dominant-private": {
    label: "Dominant · Private",
    text: "A defensible position. These brands speak with authority but to a personal inner world. The wearer feels selected rather than inducted.",
    implication: "Entry requires credible craft heritage."
  },
  "vulnerable-private": {
    label: "Vulnerable · Private ✦",
    text: "Brands here speak directly to emotional memory without asserting authority. Maison Margiela validated this space. VARŌ targets the deepest corner.",
    implication: "VARŌ's chosen territory. High differentiation."
  },
  "vulnerable-collective": {
    label: "Vulnerable · Collective",
    text: "Unoccupied. No brand speaks with emotional openness toward a shared cultural world simultaneously.",
    implication: "The most interesting structural gap in the category."
  }
};

let qDP = [], qVP = [], qDC = [], qVC = [];
brands.forEach(b => {
    let s = scores[b.name];
    if(s.x < 5 && s.y < 5) qDC.push(b.name);
    else if(s.x < 5 && s.y >= 5) qDP.push(b.name);
    else if(s.x >= 5 && s.y < 5) qVC.push(b.name);
    else qVP.push(b.name);
});
document.getElementById('q-dc').textContent = qDC.join(", ") || "Empty";
document.getElementById('q-dp').textContent = qDP.join(", ") || "Empty";
document.getElementById('q-vc').textContent = qVC.join(", ") || "Empty";
document.getElementById('q-vp').textContent = qVP.join(", ") || "Empty";

const brandListEl = document.getElementById('brand-list');
brands.forEach(b => {
  const s = scores[b.name];
  const item = document.createElement('div');
  item.className = 'brand-item';
  item.dataset.brand = b.name;
  item.innerHTML = `
    <div class="brand-dot" style="background:${b.color}"></div>
    <span class="brand-item-name">${b.name}</span>
    <span class="brand-coords">${s.x} · ${s.y}</span>
  `;
  item.addEventListener('click', () => selectBrand(b.name));
  brandListEl.appendChild(item);
});

const pulseRing = document.getElementById('pulse-ring');

function selectBrand(name) {
  const b = brands.find(br => br.name === name);
  const s = scores[name];
  const c = commentary[name];

  const qKey = (s.x >= 5 ? "vulnerable" : "dominant") + "-" + (s.y >= 5 ? "private" : "collective");
  const qi = quadrantIntelligence[qKey];

  document.querySelectorAll('.brand-item').forEach(el => {
    el.classList.remove('selected-focus');
    if (el.dataset.brand === name) el.classList.add('selected-focus');
  });

  document.querySelectorAll('.brand-node').forEach(node => {
    node.style.opacity = node.dataset.brand === name ? '1' : '0.22';
  });

  pulseRing.setAttribute('cx', b.cx);
  pulseRing.setAttribute('cy', b.cy);
  pulseRing.setAttribute('opacity', '1');

  document.querySelectorAll('.drift-row').forEach(row => {
    const shortName = name === "Maison Margiela" ? "M. Margiela" : name;
    row.classList.toggle('highlighted', row.dataset.brand === shortName || row.dataset.brand === name);
  });

  document.getElementById('selected-pill').textContent = name;
  document.getElementById('score-block').classList.add('has-selection');
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('brand-detail').style.display = 'block';

  document.getElementById('score-x').textContent = s.x;
  document.getElementById('score-y').textContent = s.y;
  document.getElementById('score-x-label').textContent = s.xLabel;
  document.getElementById('score-y-label').textContent = s.yLabel;
  document.getElementById('bar-x').style.width = (s.x * 10) + '%';
  document.getElementById('bar-y').style.width = (s.y * 10) + '%';

  document.getElementById('pi-quadrant').textContent = qi.label;
  document.getElementById('pi-text').textContent = qi.text;
  document.getElementById('pi-implication').textContent = qi.implication;

  // POPULATE THE NEW DRIFT INSIGHT CARD
  document.getElementById('drift-insight-block').style.display = 'flex';
  // Highlight the delta inside the text to make it actionable
  let driftText = c.drift_insight;
  document.getElementById('drift-insight-text').innerHTML = driftText.replace("Insight:", "<br><br><span style='color: var(--gold); font-family: Cormorant Garamond, serif; font-style: italic; font-size: 13px;'>Insight:</span>");

  document.getElementById('commentary-empty').style.display = 'none';
  document.getElementById('commentary-content').style.display = 'block';
  document.getElementById('commentary-quote').textContent = c.quote;
  document.getElementById('reasoning-x').textContent = c.rx;
  document.getElementById('reasoning-y').textContent = c.ry;
}

const tooltip = document.getElementById('tooltip');
const mapContainer = document.getElementById('map-container');

function showTooltip(e, b) {
  const s = scores[b.name];
  document.getElementById('tt-brand').textContent = b.name;
  document.getElementById('tt-x').textContent = s.x + ' / 10';
  document.getElementById('tt-y').textContent = s.y + ' / 10';
  tooltip.classList.add('visible');
}
function moveTooltip(e) {
  const rect = mapContainer.getBoundingClientRect();
  let left = e.clientX - rect.left + 16;
  let top = e.clientY - rect.top - 12;
  if (left + 180 > rect.width) left -= 196;
  tooltip.style.left = left + 'px';
  tooltip.style.top = top + 'px';
}
function hideTooltip() { tooltip.classList.remove('visible'); }

document.getElementById('map-svg').addEventListener('click', (e) => {
  if (e.target.tagName === 'rect' || e.target.tagName === 'line' || e.target.tagName === 'text') {
    document.querySelectorAll('.brand-node').forEach(n => { n.style.opacity = '1'; });
    document.querySelectorAll('.brand-item').forEach(el => el.classList.remove('selected-focus'));
    document.querySelectorAll('.drift-row').forEach(r => r.classList.remove('highlighted'));
    pulseRing.setAttribute('opacity', '0');
    pulseRing.setAttribute('cx', '-100');
    document.getElementById('score-block').classList.remove('has-selection');
    document.getElementById('empty-state').style.display = 'block';
    document.getElementById('brand-detail').style.display = 'none';
    document.getElementById('selected-pill').textContent = '— Select a brand';
    document.getElementById('drift-insight-block').style.display = 'none';
    document.getElementById('commentary-empty').style.display = 'block';
    document.getElementById('commentary-content').style.display = 'none';
  }
});
</script>
</body>
</html>
"""

html_with_live_data = custom_html_template.replace(
    "__DYNAMIC_BRANDS_PLACEHOLDER__", json.dumps(js_brands)
).replace(
    "__DYNAMIC_SCORES_PLACEHOLDER__", json.dumps(js_scores)
).replace(
    "__DYNAMIC_COMMENTARY_PLACEHOLDER__", json.dumps(js_commentary)
).replace(
    "__DYNAMIC_DRIFT_PLACEHOLDER__", json.dumps(js_drift)
)

components.html(html_with_live_data, height=950, scrolling=True)