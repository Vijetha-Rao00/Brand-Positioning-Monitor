import streamlit as st
import streamlit.components.v1 as components
import json
import os

# --- 1. STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Brand Positioning Monitor", layout="wide", initial_sidebar_state="collapsed")

# Hide Streamlit's default UI and force iframe to absolute fullscreen
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; margin: 0 !important; }
        header, footer { display: none !important; }
        iframe {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9999 !important;
            border: none !important;
        }
        body { overflow: hidden; } 
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
    st.error("Cloud Deployment Error: The server cannot find the scores file.")
    st.stop()

with open(scores_path, "r", encoding="utf-8") as f:
    live_scores = json.load(f)

if os.path.exists(hist_path):
    with open(hist_path, "r", encoding="utf-8") as f:
        hist_scores = json.load(f)
else:
    hist_scores = {}

# PageCoder Palette
color_map = {
    "Chanel": "#ffffff", "Hermès": "#fca5a5", "YSL": "#fcd34d", "Maison Margiela": "#c4b5fd",
    "Jean Paul Gaultier": "#93c5fd", "Viktor & Rolf": "#f9a8d4", "Mancera": "#fdba74",
    "Creed": "#cbd5e1", "Byredo": "#a7f3d0", "VARŌ": "#00e599", "VARO": "#00e599"
}

drift_insights = {
    "Chanel": "Immovable monument. Near-zero drift over 4 years. Chanel acts as the category's gravitational anchor, relying on absolute consistency rather than adaptation.",
    "Hermès": "Minor regression. A slight tightening of its poetic, nature-driven narrative into more structured prestige, subtly reinforcing its institutional dominance.",
    "YSL": "Massive repositioning. Pivoted from intimate, nocturnal seduction to hyper-dominant, daytime defiance to capture a younger, bolder demographic.",
    "Maison Margiela": "Highly defensible stability. Despite corporate ownership, the brand has fiercely protected its hyper-specific memory whitespace.",
    "Jean Paul Gaultier": "Deepening of the spectacle. JPG is actively doubling down on performative identity and theatrical archetypes, rejecting modern vulnerability.",
    "Viktor & Rolf": "Sustained performance. The brand continues to rely on avant-garde fantasy, operating purely as an outward-facing spectacle.",
    "Mancera": "Solidified gatekeeping. Stable positioning relying on absolute exclusivity and raw ingredient prestige.",
    "Creed": "Doubling down on dynastic dominance. Creed ignores demands for transparency, relying entirely on royal artisan heritage.",
    "Byredo": "Indie-to-Corporate Lifecycle. Noticeable drift away from extreme private truth. Byredo is diluting its founder intimacy to support mass-market distribution.",
    "VARŌ": "New Entrant. Zero historical drift. Engineered specifically to capture the extreme Vulnerability and Private Truth whitespace abandoned by competitors.",
    "VARO": "New Entrant. Zero historical drift. Engineered specifically to capture the extreme Vulnerability and Private Truth whitespace abandoned by competitors."
}

js_brands, js_scores, js_commentary, js_drift = [], {}, {}, []

for brand, data in live_scores.items():
    x = data.get("x_score", 5.0)
    y = data.get("y_score", 5.0)

    cx = 50 + (x / 10.0) * 700
    cy = 40 + ((10.0 - y) / 10.0) * 320

    hx, hy = None, None
    if brand in hist_scores:
        hx_raw = hist_scores[brand].get("x_score", 5)
        hy_raw = hist_scores[brand].get("y_score", 5)
        hx = 50 + (hx_raw / 10.0) * 700
        hy = 40 + ((10.0 - hy_raw) / 10.0) * 320

        delta = x - hx_raw
        dir_str = "up" if delta > 0 else "down" if delta < 0 else ""
        delta_str = f"{delta:+.1f}" if delta != 0 else "0.0"
        js_drift.append({"brand": "M. Margiela" if brand == "Maison Margiela" else brand, "old": round(hx_raw * 10, 1),
                         "curr": round(x * 10, 1), "delta": delta_str, "dir": dir_str})
    else:
        js_drift.append(
            {"brand": "VARŌ" if brand == "VARO" else brand, "old": None, "curr": round(x * 10, 1), "delta": "New",
             "dir": ""})

    js_brands.append({
        "name": brand, "color": color_map.get(brand, "#ffffff"),
        "cx": round(cx, 1), "cy": round(cy, 1),
        "x21": round(hx, 1) if hx is not None else None,
        "y21": round(hy, 1) if hy is not None else None,
        "isVaro": (brand == "VARŌ" or brand == "VARO")
    })

    js_scores[brand] = {"x": round(x, 2), "y": round(y, 2)}
    js_commentary[brand] = {
        "philosophy": kb_path if not os.path.exists(kb_path) else json.load(open(kb_path, "r", encoding="utf-8")).get(
            brand, "No data"),
        "quote": f"{data.get('critique', 'No audit log available.')}",
        "rx": data.get("x_reasoning", "No reasoning provided."),
        "ry": data.get("y_reasoning", "No reasoning provided."),
        "drift": drift_insights.get(brand, "No drift data.")
    }

# --- 3. THE HTML TEMPLATE WITH CINEMATIC SCROLL ---
custom_html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Brand Positioning Monitor</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">

<style>
/* SCOPED VARIABLES */
:root {
  --bpm-bg: #090a0f;
  --bpm-panel: #13151a;
  --bpm-border: #1e212b;
  --bpm-text: #f8f9fa;
  --bpm-muted: #8b949e;
  --bpm-accent: #00e599; 
}

/* RESET & SCOPE */
.bpm-app {
  background-color: var(--bpm-bg);
  color: var(--bpm-text);
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  margin: 0; padding: 0;
  -webkit-font-smoothing: antialiased;
}

.bpm-app * { box-sizing: border-box; }
.bpm-serif { font-family: 'Instrument Serif', serif; font-weight: normal; }
.bpm-mono { font-family: 'JetBrains Mono', monospace; }

/* NAV - PINNED TO TOP */
.bpm-nav {
  position: fixed; top: 0; left: 0; width: 100vw; z-index: 1000;
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 40px;
  background: linear-gradient(to bottom, rgba(9,10,15,1) 0%, rgba(9,10,15,0) 100%);
  pointer-events: none; /* Let scroll pass through */
}
.bpm-nav > * { pointer-events: auto; } /* Keep buttons clickable */

.bpm-logo { display: flex; align-items: center; font-weight: 600; font-size: 15px; letter-spacing: -0.02em; }
.bpm-nav-links { display: flex; gap: 32px; font-size: 13px; color: var(--bpm-muted); }
.bpm-nav-btn {
  border: 1px solid var(--bpm-accent); color: var(--bpm-accent);
  padding: 8px 16px; border-radius: 4px; font-size: 13px; cursor: pointer;
  background: rgba(0, 229, 153, 0.05); transition: 0.2s;
}
.bpm-nav-btn:hover { background: rgba(0, 229, 153, 0.15); }

/* FIXED HERO BACKGROUND (THE PARALLAX TRICK) */
.bpm-hero-bg {
  position: fixed; 
  top: 0; left: 0; 
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  z-index: 1; /* Lowest layer */
  background: radial-gradient(circle at 50% 40%, rgba(0, 229, 153, 0.06), transparent 50%), var(--bpm-bg);
}
.bpm-hero-text {
  text-align: center;
  padding: 0 20px;
}
.bpm-eyebrow {
  font-family: 'JetBrains Mono', monospace; font-size: 11px;
  color: var(--bpm-muted); letter-spacing: 0.3em; text-transform: uppercase;
  margin-bottom: 24px;
}
.bpm-hero-text h1 { font-size: 72px; line-height: 1.1; margin-bottom: 16px; letter-spacing: -0.02em; margin-top: 0; color: #fff; }
.bpm-hero-text p { font-size: 16px; color: var(--bpm-muted); max-width: 600px; margin: 0 auto; line-height: 1.6; }

/* CONTENT WRAPPER - SLIDES UP OVER HERO */
.bpm-content-wrapper {
  position: relative;
  z-index: 10;
  margin-top: 100vh; /* Pushes content precisely one screen down initially */
  background-color: var(--bpm-bg); /* Opaque background covers the hero */
  border-top: 1px solid rgba(255,255,255,0.05);
  padding-top: 60px; padding-bottom: 100px;
  box-shadow: 0 -30px 80px rgba(0, 0, 0, 0.95);
}

/* TOGGLE CONTROLS */
.bpm-controls { display: flex; justify-content: center; margin-bottom: 60px; }
.bpm-pill-container {
  background: var(--bpm-panel); border: 1px solid var(--bpm-border);
  border-radius: 100px; display: flex; padding: 4px; gap: 4px;
}
.bpm-pill-btn {
  padding: 8px 24px; font-size: 13px; border-radius: 100px;
  cursor: pointer; color: var(--bpm-muted); transition: 0.2s; font-weight: 500;
}
.bpm-pill-btn.active { background: rgba(0, 229, 153, 0.1); color: var(--bpm-accent); }

/* MAP CONTAINER */
.bpm-map-section { max-width: 1000px; margin: 0 auto; position: relative; padding: 0 20px; }
#bpm-svg { width: 100%; height: auto; display: block; overflow: visible; }
.bpm-axis-line { stroke: #2a2e38; stroke-width: 1; }
.bpm-axis-label { fill: #4a505e; font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; }
.bpm-node { cursor: pointer; transition: transform 0.2s ease, opacity 0.3s ease; transform-origin: center; }
.bpm-node:hover { transform: scale(1.15); }

/* CUSTOM TOOLTIP */
.bpm-tooltip {
  position: absolute; background: rgba(13, 15, 20, 0.95); border: 1px solid var(--bpm-border);
  padding: 12px; border-radius: 8px; pointer-events: none; opacity: 0;
  transition: opacity 0.2s ease; z-index: 9999; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.bpm-tt-title { font-weight: 600; font-size: 13px; margin-bottom: 8px; color: var(--bpm-text); border-bottom: 1px solid var(--bpm-border); padding-bottom: 6px; }
.bpm-tt-row { display: flex; justify-content: space-between; gap: 20px; margin-bottom: 4px; font-size: 12px; color: var(--bpm-muted); }
.bpm-tt-val { font-family: 'JetBrains Mono', monospace; color: var(--bpm-accent); }

/* GLOWING QUADRANTS GRID */
.bpm-quadrants {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
  max-width: 1000px; margin: 40px auto 60px; padding: 0 20px;
}
.bpm-q-card {
  background: var(--bpm-panel); border: 1px solid var(--bpm-border);
  border-radius: 12px; padding: 20px; transition: all 0.3s ease;
}
.bpm-q-title { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--bpm-muted); margin-bottom: 8px; letter-spacing: 0.05em; text-transform: uppercase; transition: color 0.3s; }
.bpm-q-desc { font-size: 13px; color: var(--bpm-text); line-height: 1.5; opacity: 0.6; transition: opacity 0.3s; }

.bpm-q-card.active-glow {
  border-color: rgba(0, 229, 153, 0.5); background: rgba(0, 229, 153, 0.05);
  box-shadow: 0 10px 30px rgba(0, 229, 153, 0.1); transform: translateY(-4px);
}
.bpm-q-card.active-glow .bpm-q-title { color: var(--bpm-accent); }
.bpm-q-card.active-glow .bpm-q-desc { opacity: 1; }

/* DATA GRID */
.bpm-data-grid {
  max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: 280px 1fr; gap: 60px;
  border-top: 1px solid var(--bpm-border); padding: 60px 20px;
}

/* LIST */
.bpm-list-title { font-size: 12px; color: var(--bpm-muted); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600; }
.bpm-brand-list { display: flex; flex-direction: column; gap: 4px; }
.bpm-list-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; border-radius: 8px; cursor: pointer; border: 1px solid transparent; transition: 0.2s;
}
.bpm-list-item:hover { background: var(--bpm-panel); }
.bpm-list-item.active { background: var(--bpm-panel); border-color: var(--bpm-border); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.bpm-item-left { display: flex; align-items: center; gap: 12px; }
.bpm-item-dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
.bpm-item-name { font-size: 14px; font-weight: 500; }
.bpm-item-score { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--bpm-muted); }

/* INSIGHTS */
.bpm-insight-panel { display: none; animation: bpmFadeIn 0.4s ease; }
@keyframes bpmFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.bpm-empty-state { text-align: center; color: var(--bpm-muted); margin-top: 60px; font-size: 15px; }
.bpm-insight-header { margin-bottom: 24px; }
.bpm-insight-brand { font-size: 48px; line-height: 1; margin-bottom: 8px; margin-top: 0; }
.bpm-insight-coords { font-family: 'JetBrains Mono', monospace; font-size: 14px; color: var(--bpm-accent); }

.bpm-info-block { margin-bottom: 32px; }
.bpm-info-label { font-size: 11px; color: var(--bpm-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; font-weight: 600; }
.bpm-info-text { font-size: 15px; line-height: 1.6; color: var(--bpm-text); }
.bpm-info-quote { font-size: 20px; line-height: 1.5; color: var(--bpm-muted); border-left: 2px solid var(--bpm-border); padding-left: 20px; font-style: italic; }

.bpm-code-box {
  background: var(--bpm-panel); border: 1px solid var(--bpm-border);
  border-radius: 8px; padding: 16px; margin-bottom: 12px;
  font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.6; color: var(--bpm-muted);
}
.bpm-code-box span { color: var(--bpm-accent); }

/* BRIEFING */
.bpm-briefing {
  max-width: 1000px; margin: 40px auto 80px; border-top: 1px solid var(--bpm-border); padding: 60px 20px;
}
.bpm-briefing h2 { font-size: 40px; margin-bottom: 40px; text-align: center; margin-top: 0; color: #fff;}
.bpm-b-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-bottom: 40px; }
.bpm-b-col h3 { font-size: 16px; font-weight: 600; margin-bottom: 12px; color: var(--bpm-text); margin-top:0;}
.bpm-b-col p { font-size: 15px; color: var(--bpm-muted); line-height: 1.7; margin:0;}
.bpm-b-full { background: var(--bpm-panel); border: 1px solid var(--bpm-border); padding: 32px; border-radius: 12px; }
.bpm-b-full h3 { font-size: 18px; margin-bottom: 12px; color: var(--bpm-accent); margin-top:0;}
.bpm-b-full p { font-size: 15px; color: var(--bpm-text); line-height: 1.7; margin:0;}

/* MOBILE RESPONSIVE */
@media (max-width: 900px) {
  .bpm-nav { padding: 20px; }
  .bpm-nav-links, .bpm-nav-btn { display: none; }
  .bpm-hero-text h1 { font-size: 40px; }
  .bpm-quadrants { grid-template-columns: 1fr 1fr; }
  .bpm-data-grid { grid-template-columns: 1fr; gap: 40px; }
  .bpm-b-grid { grid-template-columns: 1fr; }
  .bpm-insight-brand { font-size: 36px; }
}
@media (max-width: 500px) {
  .bpm-quadrants { grid-template-columns: 1fr; }
}
</style>
</head>
<body>

<div class="bpm-app">

  <nav class="bpm-nav">
    <div class="bpm-logo">
      <svg viewBox="0 0 24 24" style="width:20px; height:20px; fill:var(--bpm-text); margin-right:8px;"><path d="M12 2L2 22h20L12 2z"/></svg>
      <span style="color:var(--bpm-text);">Positioning Monitor</span>
      <span style="color:var(--bpm-muted); font-weight:400; margin-left:8px;">| Luxury Intelligence</span>
    </div>
    <div class="bpm-nav-links">
      <span>Map</span>
      <span>Methodology</span>
      <span>Audit Logs</span>
    </div>
    <div class="bpm-nav-btn">Export Matrix</div>
  </nav>

  <!-- FIXED PARALLAX HERO -->
  <div class="bpm-hero-bg" id="bpm-hero">
    <div class="bpm-hero-text" id="bpm-hero-text">
      <div class="bpm-eyebrow">A G E N T &nbsp; 0 4 &nbsp; A U D I T</div>
      <h1 class="bpm-serif">Your Linguistic DNA</h1>
      <p>Every time a brand communicates, it leaves a unique semantic trace.<br>This is what the luxury landscape fingerprint looks like.</p>
    </div>
  </div>

  <!-- SCROLLING CONTENT WRAPPER -->
  <div class="bpm-content-wrapper">

    <div class="bpm-controls">
      <div class="bpm-pill-container">
        <div class="bpm-pill-btn active" id="btn-current">Current Matrix</div>
        <div class="bpm-pill-btn" id="btn-drift">Drift Vectors</div>
      </div>
    </div>

    <section class="bpm-map-section">
      <svg viewBox="0 0 800 400" id="bpm-svg">
        <line x1="0" y1="200" x2="800" y2="200" class="bpm-axis-line" />
        <line x1="400" y1="0" x2="400" y2="400" class="bpm-axis-line" />

        <text x="0" y="190" class="bpm-axis-label" text-anchor="start">DOMINANCE</text>
        <text x="800" y="190" class="bpm-axis-label" text-anchor="end">VULNERABILITY</text>
        <text x="410" y="15" class="bpm-axis-label" text-anchor="start">PRIVATE TRUTH</text>
        <text x="410" y="390" class="bpm-axis-label" text-anchor="start">COLLECTIVE MYTH</text>

        <g id="drift-layer" style="display:none;"></g>
        <g id="brands-layer"></g>
      </svg>
    </section>

    <section class="bpm-quadrants">
      <div class="bpm-q-card" id="quad-dominant-private">
        <div class="bpm-q-title">Dominant · Private</div>
        <div class="bpm-q-desc">A defensible position. Authority meets a personal inner world.</div>
      </div>
      <div class="bpm-q-card" id="quad-vulnerable-private">
        <div class="bpm-q-title">Vulnerable · Private ✦</div>
        <div class="bpm-q-desc">The intimacy territory. Memory and emotional specificity.</div>
      </div>
      <div class="bpm-q-card" id="quad-dominant-collective">
        <div class="bpm-q-title">Dominant · Collective</div>
        <div class="bpm-q-desc">The densest territory. Institutional authority and broad culture.</div>
      </div>
      <div class="bpm-q-card" id="quad-vulnerable-collective">
        <div class="bpm-q-title">Vulnerable · Collective</div>
        <div class="bpm-q-desc">A rare structural gap. Openness meets shared cultural address.</div>
      </div>
    </section>

    <section class="bpm-data-grid">
      <div>
        <div class="bpm-list-title">Entities Mapped</div>
        <div class="bpm-brand-list" id="brand-list"></div>
      </div>

      <div>
        <div class="bpm-empty-state" id="empty-state">
          Select a brand from the map or list to inspect the AI audit logs.
        </div>

        <div class="bpm-insight-panel" id="insight-panel">
          <div class="bpm-insight-header">
            <div>
              <h2 class="bpm-serif bpm-insight-brand" id="detail-brand">Brand</h2>
              <div class="bpm-insight-coords" id="detail-coords">[ X: 0.0, Y: 0.0 ]</div>
            </div>
          </div>

          <div class="bpm-info-block">
            <div class="bpm-info-label">Extracted Primary Source</div>
            <div class="bpm-info-quote bpm-serif" id="detail-philosophy">"Philosophy goes here."</div>
          </div>

          <div class="bpm-info-block">
            <div class="bpm-info-label">Agent 4 Execution Log</div>
            <div class="bpm-code-box">
              <div style="color:var(--bpm-text); margin-bottom:8px;">> Auditing Agent 3 baseline...</div>
              <div id="detail-audit">Audit log text.</div>
            </div>
            <div class="bpm-code-box">
              <span>[X_AXIS]</span> <span id="detail-rx" style="color:var(--bpm-muted)">Reasoning</span>
            </div>
            <div class="bpm-code-box">
              <span>[Y_AXIS]</span> <span id="detail-ry" style="color:var(--bpm-muted)">Reasoning</span>
            </div>
          </div>

          <div class="bpm-info-block">
            <div class="bpm-info-label">Historical Drift Insight</div>
            <div class="bpm-info-text" id="detail-drift">Drift text.</div>
          </div>
        </div>
      </div>
    </section>

    <section class="bpm-briefing">
      <h2 class="bpm-serif">Strategic Architecture</h2>
      <div class="bpm-b-grid">
        <div class="bpm-b-col">
          <h3>Tone of Voice (X-Axis)</h3>
          <p>Dominance is the voice of the monument, relying on authority, legacy, and commands (e.g., Creed). Vulnerability is the voice of the confidant, stripping away the pedestal in favor of intimacy, somatic language, and emotional exposure (e.g., Byredo).</p>
        </div>
        <div class="bpm-b-col">
          <h3>Narrative Scope (Y-Axis)</h3>
          <p>Collective Myth constructs a universal, shared cultural religion positioning itself as a global institution (e.g., Chanel). Private Truth addresses the hyper-specific inner life of the individual, reading like a personal diary entry (e.g., Maison Margiela).</p>
        </div>
      </div>
      <div class="bpm-b-full">
        <h3>The Commercial Imperative</h3>
        <p>By plotting legacy competitors, a glaring structural void emerges in the High Vulnerability / High Private Truth quadrant. Most luxury houses remain trapped in Dominance and Collective Myth. The VARŌ concept is engineered specifically to exploit this exact whitespace, offering radical intimacy to a modern consumer who has outgrown traditional status signaling.</p>
      </div>
    </section>
  </div>
</div>

<div class="bpm-tooltip" id="bpm-tooltip">
  <div class="bpm-tt-title" id="tt-brand">Brand</div>
  <div class="bpm-tt-row"><span>X Score</span><span class="bpm-tt-val" id="tt-x">0.0</span></div>
  <div class="bpm-tt-row"><span>Y Score</span><span class="bpm-tt-val" id="tt-y">0.0</span></div>
</div>

<script>
const brands = __DYNAMIC_BRANDS_PLACEHOLDER__;
const scores = __DYNAMIC_SCORES_PLACEHOLDER__;
const commentary = __DYNAMIC_COMMENTARY_PLACEHOLDER__;

// --- CINEMATIC SCROLL LOGIC ---
const heroText = document.getElementById('bpm-hero-text');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const vh = window.innerHeight;
  // Fade text to 0 opacity
  heroText.style.opacity = Math.max(1 - (scrollY / (vh * 0.5)), 0);
  // Slight parallax push down on the text
  heroText.style.transform = `translateY(${scrollY * 0.3}px)`;
});

const svgBrands = document.getElementById('brands-layer');
const svgDrift = document.getElementById('drift-layer');
const listEl = document.getElementById('brand-list');
const tooltip = document.getElementById('bpm-tooltip');

brands.forEach(b => {
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.setAttribute("class", "bpm-node");
  g.setAttribute("data-name", b.name);

  if(b.isVaro) {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="14" fill="rgba(0, 229, 153, 0.15)" />
      <circle cx="${b.cx}" cy="${b.cy}" r="7" fill="${b.color}" />
      <text x="${b.cx}" y="${b.cy - 18}" fill="${b.color}" font-family="JetBrains Mono" font-size="10" text-anchor="middle">VARŌ</text>
    `;
  } else {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="5" fill="${b.color}" />
      <text x="${b.cx}" y="${b.cy - 12}" fill="${b.color}" font-family="Inter" font-size="11" text-anchor="middle" opacity="0.8">${b.name}</text>
    `;
  }

  if (b.x21 !== null) {
    svgDrift.innerHTML += `
      <line x1="${b.x21}" y1="${b.y21}" x2="${b.cx}" y2="${b.cy}" stroke="${b.color}" stroke-width="1.5" stroke-dasharray="2,3" opacity="0.4" />
      <circle cx="${b.x21}" cy="${b.y21}" r="3" fill="none" stroke="${b.color}" opacity="0.5" />
    `;
  }

  g.addEventListener('mouseenter', (e) => {
    document.getElementById('tt-brand').textContent = b.name;
    document.getElementById('tt-x').textContent = scores[b.name].x;
    document.getElementById('tt-y').textContent = scores[b.name].y;
    tooltip.style.opacity = 1;
    moveTT(e);
  });

  g.addEventListener('mousemove', moveTT);
  g.addEventListener('mouseleave', () => { tooltip.style.opacity = 0; });
  g.addEventListener('click', () => selectBrand(b.name));

  svgBrands.appendChild(g);
});

function moveTT(e) {
  tooltip.style.left = (e.pageX + 15) + 'px';
  tooltip.style.top = (e.pageY + 15) + 'px';
}

brands.forEach(b => {
  const item = document.createElement('div');
  item.className = 'bpm-list-item';
  item.id = 'list-' + b.name.replace(/\\s+/g, '');
  item.innerHTML = `
    <div class="bpm-item-left">
      <div class="bpm-item-dot" style="background: ${b.color}; box-shadow: 0 0 8px ${b.color};"></div>
      <div class="bpm-item-name">${b.name}</div>
    </div>
    <div class="bpm-item-score">${scores[b.name].x} · ${scores[b.name].y}</div>
  `;
  item.onclick = () => selectBrand(b.name);
  listEl.appendChild(item);
});

function selectBrand(name) {
  document.getElementById('empty-state').style.display = 'none';
  document.getElementById('insight-panel').style.display = 'block';

  document.querySelectorAll('.bpm-list-item').forEach(el => el.classList.remove('active'));
  document.getElementById('list-' + name.replace(/\\s+/g, '')).classList.add('active');

  // DIMMING EFFECT
  document.querySelectorAll('.bpm-node').forEach(node => {
    node.style.opacity = node.getAttribute('data-name') === name ? '1' : '0.15';
  });

  const b = brands.find(x => x.name === name);
  const c = commentary[name];
  const s = scores[name];

  document.getElementById('detail-brand').textContent = b.name;
  document.getElementById('detail-brand').style.color = b.color;
  document.getElementById('detail-coords').textContent = `[ X: ${s.x}, Y: ${s.y} ]`;

  let rawPhil = typeof c.philosophy === 'object' ? c.philosophy[name] : c.philosophy;
  document.getElementById('detail-philosophy').textContent = `"${rawPhil}"`;

  document.getElementById('detail-audit').textContent = c.quote;
  document.getElementById('detail-rx').textContent = c.rx;
  document.getElementById('detail-ry').textContent = c.ry;
  document.getElementById('detail-drift').innerHTML = c.drift.replace("Insight:", "<br><br><span style='color:var(--bpm-accent); font-family:JetBrains Mono, monospace; font-size:11px; text-transform:uppercase;'>System Insight:</span>");

  // QUADRANT GLOW
  const qKey = (s.x >= 5 ? "vulnerable" : "dominant") + "-" + (s.y >= 5 ? "private" : "collective");
  document.querySelectorAll('.bpm-q-card').forEach(q => q.classList.remove('active-glow'));
  const targetQ = document.getElementById('quad-' + qKey);
  if(targetQ) targetQ.classList.add('active-glow');
}

const btnCurr = document.getElementById('btn-current');
const btnDrift = document.getElementById('btn-drift');

btnCurr.onclick = () => {
  btnCurr.classList.add('active'); btnDrift.classList.remove('active');
  svgDrift.style.display = 'none';
};
btnDrift.onclick = () => {
  btnDrift.classList.add('active'); btnCurr.classList.remove('active');
  svgDrift.style.display = 'block';
};
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
)

components.html(html_with_live_data, height=1800, scrolling=True)