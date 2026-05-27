import streamlit as st
import json
import os

# --- 1. STREAMLIT PAGE CONFIG ---
st.set_page_config(page_title="Brand Positioning Monitor", layout="wide", initial_sidebar_state="collapsed")

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


# --- 2. DATA ROUTING ---
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
    "Jean Paul Gaultier": "#38bdf8", "Viktor & Rolf": "#f9a8d4", "Mancera": "#fdba74",
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

# --- 3. THE HTML TEMPLATE ---
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
:root {
  --bg: #090a0f;
  --panel: #13151a;
  --border: #1e212b;
  --text-main: #f8f9fa;
  --text-muted: #8b949e;
  --accent: #00e599; 
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg);
  color: var(--text-main);
  margin: 0;
  height: 200vh; 
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { display: none; }

.serif { font-family: 'Instrument Serif', serif; font-weight: normal; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* FIXED NAV */
nav {
  position: fixed; top: 0; left: 0; width: 100vw; z-index: 1000;
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 40px;
  background: linear-gradient(to bottom, rgba(9,10,15,1) 0%, rgba(9,10,15,0) 100%);
  pointer-events: none;
}
nav > * { pointer-events: auto; }
.logo { display: flex; align-items: center; font-weight: 600; font-size: 15px; letter-spacing: -0.02em; }
.nav-links { display: flex; gap: 32px; font-size: 13px; color: var(--text-muted); }
.nav-btn {
  border: 1px solid var(--accent); color: var(--accent);
  padding: 8px 16px; border-radius: 4px; font-size: 13px; cursor: pointer;
  background: rgba(0, 229, 153, 0.05); transition: 0.2s;
}
.nav-btn:hover { background: rgba(0, 229, 153, 0.15); }

/* FIXED HERO */
.hero-section {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  z-index: 1; text-align: center;
  background: radial-gradient(circle at 50% 40%, rgba(0, 229, 153, 0.05), transparent 50%), var(--bg);
}
.eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); letter-spacing: 0.3em; text-transform: uppercase; margin-bottom: 24px; }
.hero-section h1 { font-size: 72px; line-height: 1.1; margin-bottom: 16px; letter-spacing: -0.02em; margin-top: 0; color: #fff; }
.hero-section p { font-size: 16px; color: var(--text-muted); max-width: 600px; margin: 0 auto; line-height: 1.6; }

/* THE SCROLLING DASHBOARD WRAPPER */
.dashboard-wrapper {
  position: absolute;
  top: 100vh; 
  left: 0; width: 100vw; height: 100vh; 
  background-color: var(--bg);
  border-top: 1px solid rgba(255,255,255,0.05);
  z-index: 10;
  display: flex;
  padding: 80px 40px 40px 40px; 
  gap: 40px;
  overflow: hidden; 
  box-shadow: 0 -30px 80px rgba(0, 0, 0, 0.95);
}

/* LEFT COLUMN: CONTROLS */
.left-col {
  width: 280px; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 24px;
}

/* CUSTOM DROPDOWN */
.custom-dropdown { position: relative; width: 100%; z-index: 50; }
.dd-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; font-weight: 600; }
.dd-header {
  padding: 14px 16px; background: var(--panel); border: 1px solid var(--border);
  border-radius: 8px; cursor: pointer; color: var(--text-main); font-weight: 500; font-size: 14px;
  display: flex; justify-content: space-between; align-items: center; transition: 0.2s;
}
.dd-header:hover { border-color: rgba(255,255,255,0.2); }
.dd-list {
  position: absolute; top: 100%; left: 0; width: 100%;
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 8px; margin-top: 8px; opacity: 0; pointer-events: none;
  transform: translateY(-10px); transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  max-height: 300px; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}
.dd-list.show { opacity: 1; pointer-events: auto; transform: translateY(0); }
.dd-item { padding: 12px 16px; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: 0.1s; }
.dd-item:hover { background: rgba(255,255,255,0.05); }
.item-dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
.item-name { font-size: 13px; font-weight: 500; color: var(--text-main); }

/* DRIFT TOGGLE */
.toggle-panel { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 16px; display: flex; justify-content: space-between; align-items: center; }
.toggle-label { font-size: 13px; font-weight: 500; color: var(--text-main); }
.toggle-btn {
  width: 44px; height: 24px; background: var(--bg); border: 1px solid var(--border);
  border-radius: 100px; position: relative; cursor: pointer; transition: 0.3s;
}
.toggle-btn.active { background: rgba(0, 229, 153, 0.2); border-color: var(--accent); }
.toggle-btn::after {
  content: ''; position: absolute; width: 16px; height: 16px; border-radius: 50%;
  background: var(--text-muted); top: 3px; left: 3px; transition: 0.3s;
}
.toggle-btn.active::after { left: 23px; background: var(--accent); }

/* QUADRANT SUMMARY (Left Col) */
.quadrant-summary { display: flex; flex-direction: column; gap: 8px; }
.q-card { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 14px; transition: 0.3s; }
.q-card.active-glow { border-color: rgba(0, 229, 153, 0.5); background: rgba(0, 229, 153, 0.05); box-shadow: 0 4px 20px rgba(0, 229, 153, 0.1); }
.q-title { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--text-muted); letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px; }
.q-card.active-glow .q-title { color: var(--accent); }
.q-desc { font-size: 12px; color: var(--text-main); line-height: 1.5; opacity: 0.6; }
.q-card.active-glow .q-desc { opacity: 1; }

/* CENTER COLUMN: MAP */
.map-col {
  flex-grow: 1; position: relative;
  display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.02), transparent 70%);
  border: 1px solid var(--border); border-radius: 12px; padding: 20px;
}
#bpm-svg { width: 100%; height: 100%; max-height: 100%; overflow: visible; }
.axis-line { stroke: #2a2e38; stroke-width: 1; }
.axis-label { fill: #4a505e; font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; }

/* FIX: PERFECT BRAND HOVER (No scale, soft glow) */
.brand-node { cursor: pointer; transition: filter 0.2s ease, opacity 0.3s ease; transform-origin: center; }
.brand-node:hover { filter: brightness(1.3) drop-shadow(0 0 6px rgba(255,255,255,0.3)); }

/* BULLETPROOF TOOLTIP */
.tooltip {
  position: absolute; background: rgba(13, 15, 20, 0.95); border: 1px solid var(--border);
  padding: 12px; border-radius: 8px; opacity: 0;
  transition: opacity 0.15s ease; z-index: 9999; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  pointer-events: none !important; /* CRITICAL: Prevents flicker loop */
}
.tt-title { font-weight: 600; font-size: 13px; margin-bottom: 8px; color: var(--text-main); border-bottom: 1px solid var(--border); padding-bottom: 6px; }
.tt-row { display: flex; justify-content: space-between; gap: 20px; margin-bottom: 4px; font-size: 12px; color: var(--text-muted); }
.tt-val { font-family: 'JetBrains Mono', monospace; color: var(--accent); }

/* RIGHT COLUMN: SLIDING INSIGHT CARD */
.insight-card {
  position: absolute; right: 40px; top: 80px;
  width: 380px; height: calc(100vh - 120px);
  background: rgba(19, 21, 26, 0.85); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border); border-radius: 16px; padding: 30px;
  transform: translateX(120%); transition: transform 0.5s cubic-bezier(0.16, 1, 0.3, 1);
  z-index: 100; overflow-y: auto; box-shadow: -20px 0 50px rgba(0,0,0,0.5);
  display: flex; flex-direction: column; gap: 24px;
}
.insight-card.open { transform: translateX(0); }
.close-btn {
  position: absolute; top: 20px; right: 20px; width: 30px; height: 30px;
  border-radius: 50%; background: var(--panel); border: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center; cursor: pointer;
  color: var(--text-muted); font-size: 12px; transition: 0.2s;
}
.close-btn:hover { background: rgba(255,255,255,0.1); color: #fff; }

.insight-brand { font-size: 42px; line-height: 1; margin-bottom: 4px; margin-top:0; }
.insight-coords { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: var(--accent); margin-bottom: 24px; }
.info-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; font-weight: 600; }
.info-quote { font-size: 17px; line-height: 1.5; color: var(--text-muted); border-left: 2px solid var(--border); padding-left: 16px; font-style: italic; }
.code-box { background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'JetBrains Mono', monospace; font-size: 11px; line-height: 1.6; color: var(--text-muted); }
.code-box span { color: var(--accent); }
.info-text { font-size: 14px; line-height: 1.6; color: var(--text-main); }

/* MOBILE RESPONSIVE */
@media (max-width: 900px) {
  body { height: auto; overflow-y: auto; }
  .dashboard-wrapper { position: relative; top: 0; margin-top: 0; height: auto; flex-direction: column; padding: 100px 20px 20px 20px; overflow: visible; }
  .hero-section { position: relative; height: 100vh; }
  .left-col { width: 100%; flex-direction: row; flex-wrap: wrap; }
  .custom-dropdown { width: 100%; flex: 1; }
  .map-col { min-height: 400px; }
  .insight-card { 
      position: fixed; right: 0; top: auto; bottom: 0; width: 100%; height: 85vh; 
      transform: translateY(110%); border-radius: 24px 24px 0 0; z-index: 9999;
  }
  .insight-card.open { transform: translateY(0); }
  .nav-links, .nav-btn { display: none; }
  .hero-section h1 { font-size: 44px; }
}
</style>
</head>
<body>

<nav>
  <div class="logo">
    <svg viewBox="0 0 24 24" style="width:20px; height:20px; fill:var(--text-main); margin-right:8px;"><path d="M12 2L2 22h20L12 2z"/></svg>
    <span style="color:var(--text-main);">Positioning Monitor</span>
    <span style="color:var(--text-muted); font-weight:400; margin-left:8px;">| Luxury Intelligence</span>
  </div>
  <div class="nav-links">
    <span>Dashboard</span>
    <span>Methodology</span>
  </div>
  <div class="nav-btn">Export Matrix</div>
</nav>

<!-- FIXED HERO -->
<header class="hero-section" id="hero">
  <div class="hero-content" id="hero-content">
    <div class="eyebrow">A G E N T &nbsp; 0 4 &nbsp; A U D I T</div>
    <h1 class="serif">Your Linguistic DNA</h1>
    <p>Every time a brand communicates, it leaves a unique semantic trace.<br>Scroll to reveal the luxury landscape fingerprint.</p>
  </div>
</header>

<!-- DASHBOARD -->
<div class="dashboard-wrapper">

  <!-- LEFT COLUMN -->
  <div class="left-col">
    <div class="custom-dropdown">
      <div class="dd-label">Target Entity</div>
      <div class="dd-header" id="dd-header">Select a Brand... <span style="color:var(--text-muted)">▼</span></div>
      <div class="dd-list" id="dd-list"></div>
    </div>

    <div class="toggle-panel">
      <span class="toggle-label">Drift Vectors (2021)</span>
      <div class="toggle-btn" id="btn-drift"></div>
    </div>

    <div class="quadrant-summary">
      <div class="dd-label" style="margin-top:8px;">Quadrant Intel</div>
      <div class="q-card" id="quad-dominant-private">
        <div class="q-title">Dominant · Private</div>
        <div class="q-desc">Authority meets a personal inner world. Defensible.</div>
      </div>
      <div class="q-card" id="quad-vulnerable-private">
        <div class="q-title">Vulnerable · Private ✦</div>
        <div class="q-desc">Memory and emotional specificity. Highly differentiated.</div>
      </div>
      <div class="q-card" id="quad-dominant-collective">
        <div class="q-title">Dominant · Collective</div>
        <div class="q-desc">Institutional authority. Highest collision risk.</div>
      </div>
      <div class="q-card" id="quad-vulnerable-collective">
        <div class="q-title">Vulnerable · Collective</div>
        <div class="q-desc">Structural whitespace. Openness meets shared culture.</div>
      </div>
    </div>
  </div>

  <!-- CENTER COLUMN: MAP -->
  <div class="map-col">
    <svg viewBox="0 0 800 400" id="bpm-svg">
      <line x1="0" y1="200" x2="800" y2="200" class="axis-line" />
      <line x1="400" y1="0" x2="400" y2="400" class="axis-line" />

      <text x="0" y="190" class="axis-label" text-anchor="start">DOMINANCE</text>
      <text x="800" y="190" class="axis-label" text-anchor="end">VULNERABILITY</text>
      <text x="410" y="15" class="axis-label" text-anchor="start">PRIVATE TRUTH</text>
      <text x="410" y="390" class="axis-label" text-anchor="start">COLLECTIVE MYTH</text>

      <g id="drift-layer" style="display:none;"></g>
      <g id="brands-layer"></g>
    </svg>
  </div>

  <!-- RIGHT COLUMN: HIDDEN INSIGHTS CARD -->
  <div class="insight-card" id="insight-card">
    <div class="close-btn" onclick="closeInsight()">✕</div>

    <div>
      <h2 class="serif insight-brand" id="detail-brand">Brand</h2>
      <div class="insight-coords" id="detail-coords">[ X: 0.0, Y: 0.0 ]</div>
    </div>

    <div>
      <div class="info-label">Primary Source Extract</div>
      <div class="info-quote serif" id="detail-philosophy">"Philosophy."</div>
    </div>

    <div>
      <div class="info-label">Agent 4 Execution Log</div>
      <div class="code-box">
        <div style="color:var(--text-main); margin-bottom:8px;">> Auditing Agent 3 baseline...</div>
        <div id="detail-audit">Log.</div>
      </div>
      <div class="code-box">
        <span>[X_AXIS]</span> <span id="detail-rx" style="color:var(--text-muted)">Reasoning</span>
      </div>
      <div class="code-box">
        <span>[Y_AXIS]</span> <span id="detail-ry" style="color:var(--text-muted)">Reasoning</span>
      </div>
    </div>

    <div>
      <div class="info-label">Historical Drift Insight</div>
      <div class="info-text" id="detail-drift">Drift.</div>
    </div>
  </div>

</div>

<!-- BULLETPROOF TOOLTIP -->
<div class="tooltip" id="bpm-tooltip">
  <div class="tt-title" id="tt-brand">Brand</div>
  <div class="tt-row"><span>X Score</span><span class="tt-val" id="tt-x">0.0</span></div>
  <div class="tt-row"><span>Y Score</span><span class="tt-val" id="tt-y">0.0</span></div>
</div>

<script>
const brands = __DYNAMIC_BRANDS_PLACEHOLDER__;
const scores = __DYNAMIC_SCORES_PLACEHOLDER__;
const commentary = __DYNAMIC_COMMENTARY_PLACEHOLDER__;

const svgBrands = document.getElementById('brands-layer');
const svgDrift = document.getElementById('drift-layer');
const tooltip = document.getElementById('bpm-tooltip');
const heroContent = document.getElementById('hero-content');
const ddHeader = document.getElementById('dd-header');
const ddList = document.getElementById('dd-list');
const insightCard = document.getElementById('insight-card');

// --- CINEMATIC SCROLL LOGIC ---
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  const vh = window.innerHeight;
  heroContent.style.opacity = Math.max(1 - (scrollY / (vh * 0.6)), 0);
  heroContent.style.transform = `translateY(${scrollY * 0.2}px)`;
});

// --- RENDER MAP & DRIFT ---
brands.forEach(b => {
  const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
  g.setAttribute("class", "brand-node");
  g.setAttribute("data-name", b.name);

  // FIX: Added a large transparent hit-area circle so you can click anywhere near the dot/text
  if(b.isVaro) {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="25" fill="transparent"/>
      <circle cx="${b.cx}" cy="${b.cy}" r="14" fill="rgba(0, 229, 153, 0.15)" />
      <circle cx="${b.cx}" cy="${b.cy}" r="7" fill="${b.color}" />
      <text x="${b.cx}" y="${b.cy - 18}" fill="${b.color}" font-family="JetBrains Mono" font-size="10" text-anchor="middle">VARŌ</text>
    `;
  } else {
    g.innerHTML = `
      <circle cx="${b.cx}" cy="${b.cy}" r="25" fill="transparent"/>
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

  // BULLETPROOF HOVER FIX
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

// --- RENDER DROPDOWN ---
brands.forEach(b => {
  const item = document.createElement('div');
  item.className = 'dd-item';
  item.innerHTML = `
    <div class="item-dot" style="background: ${b.color}; box-shadow: 0 0 8px ${b.color};"></div>
    <div class="item-name">${b.name}</div>
  `;
  item.onclick = (e) => {
    e.stopPropagation();
    selectBrand(b.name);
    ddList.classList.remove('show');
  };
  ddList.appendChild(item);
});

// Dropdown Toggle Logic
ddHeader.onclick = (e) => {
    e.stopPropagation();
    ddList.classList.toggle('show');
};

// --- SELECTION LOGIC ---
function selectBrand(name) {
  ddHeader.innerHTML = `${name} <span style="color:var(--text-muted)">▼</span>`;

  // Deep dim unselected nodes (keeps selected brand standing still but highlighted)
  document.querySelectorAll('.brand-node').forEach(node => {
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
  document.getElementById('detail-drift').innerHTML = c.drift.replace("Insight:", "<br><br><span style='color:var(--accent); font-family:JetBrains Mono, monospace; font-size:11px; text-transform:uppercase;'>System Insight:</span>");

  // Slide In Right Panel
  insightCard.classList.add('open');

  // Highlight Quadrant Card
  const qKey = (s.x >= 5 ? "vulnerable" : "dominant") + "-" + (s.y >= 5 ? "private" : "collective");
  document.querySelectorAll('.q-card').forEach(q => q.classList.remove('active-glow'));
  const targetQ = document.getElementById('quad-' + qKey);
  if(targetQ) targetQ.classList.add('active-glow');
}

// --- GLOBAL DISMISS LOGIC ---
function closeInsight() {
    insightCard.classList.remove('open');
    document.querySelectorAll('.brand-node').forEach(node => { node.style.opacity = '1'; });
    document.querySelectorAll('.q-card').forEach(q => q.classList.remove('active-glow'));
    ddHeader.innerHTML = `Select a Brand... <span style="color:var(--text-muted)">▼</span>`;
}

// Click anywhere to dismiss, unless clicking inside the card, dropdown, or toggle
document.addEventListener('click', (e) => {
    if (
        e.target.closest('.brand-node') || 
        e.target.closest('.custom-dropdown') || 
        e.target.closest('.insight-card') || 
        e.target.closest('.toggle-panel') ||
        e.target.closest('.bpm-nav')
    ) {
        return;
    }

    // Close dropdown if open
    ddList.classList.remove('show');

    // Close insight card
    if (insightCard.classList.contains('open')) {
        closeInsight();
    }
});

// --- DRIFT TOGGLE LOGIC ---
const btnDrift = document.getElementById('btn-drift');
btnDrift.onclick = function(e) {
  e.stopPropagation();
  this.classList.toggle('active');
  svgDrift.style.display = this.classList.contains('active') ? 'block' : 'none';
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

st.components.v1.html(html_with_live_data, height=2000, scrolling=True)