from flask import Flask, request, jsonify
from pipeline import run_search_agent_pipeline
import os

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nexus Research</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'DM Sans',sans-serif; background:#07020f; color:#fff; min-height:100vh; overflow-x:hidden; }

  .orb { position:fixed; border-radius:50%; pointer-events:none; z-index:0; }
  .orb1 { width:500px;height:500px;background:radial-gradient(circle,rgba(120,40,200,0.35),transparent 70%);top:-150px;left:-100px; }
  .orb2 { width:400px;height:400px;background:radial-gradient(circle,rgba(80,60,210,0.25),transparent 70%);top:0;right:-80px; }
  .orb3 { width:450px;height:450px;background:radial-gradient(circle,rgba(180,50,220,0.2),transparent 70%);bottom:-100px;right:10%; }

  .wrap { position:relative;z-index:2;max-width:780px;margin:0 auto;padding:0 28px 80px; }

  /* NAV */
  nav { display:flex;align-items:center;justify-content:space-between;padding:26px 0 0; }
  .logo { font-family:'Syne',sans-serif;font-weight:800;font-size:16px;display:flex;align-items:center;gap:7px;letter-spacing:-0.3px; }
  .logo-dot { width:7px;height:7px;border-radius:50%;background:linear-gradient(135deg,#c084fc,#818cf8);box-shadow:0 0 10px rgba(168,85,247,0.8);animation:glow 2s ease infinite; }
  @keyframes glow { 0%,100%{opacity:1}50%{opacity:0.5} }
  .nav-links { display:flex;gap:24px;font-size:13px;color:rgba(255,255,255,0.42); }
  .nav-links span { cursor:pointer;transition:color 0.2s; }
  .nav-links span:hover { color:#fff; }
  .nav-btn { background:rgba(168,85,247,0.12);border:1px solid rgba(168,85,247,0.3);border-radius:20px;padding:6px 16px;font-size:13px;color:#c084fc;font-weight:500;cursor:pointer;transition:background 0.2s;font-family:'DM Sans',sans-serif; }
  .nav-btn:hover { background:rgba(168,85,247,0.22); }

  /* HERO */
  .hero { text-align:center;padding:52px 0 40px; }
  .eyebrow { display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:99px;padding:5px 14px;font-size:11px;letter-spacing:0.09em;color:rgba(255,255,255,0.45);text-transform:uppercase;margin-bottom:24px; }
  .edot { width:5px;height:5px;border-radius:50%;background:#34d399;box-shadow:0 0 6px #34d399;animation:glow 2s ease infinite; }
  h1 { font-family:'Syne',sans-serif;font-size:clamp(36px,5.5vw,54px);font-weight:800;line-height:1.08;letter-spacing:-1.5px;margin-bottom:18px; }
  .grad { background:linear-gradient(90deg,#e879f9,#a78bfa 55%,#60a5fa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
  .sub { font-size:15px;line-height:1.7;color:rgba(255,255,255,0.42);max-width:480px;margin:0 auto;font-weight:300; }

  /* SEARCH */
  .search-box { margin:32px auto 0;max-width:620px;background:rgba(255,255,255,0.045);border:1px solid rgba(255,255,255,0.1);border-radius:18px;padding:5px 5px 5px 18px;display:flex;align-items:center;gap:10px;backdrop-filter:blur(16px);transition:border-color 0.3s,box-shadow 0.3s; }
  .search-box:focus-within { border-color:rgba(168,85,247,0.5);box-shadow:0 0 0 3px rgba(168,85,247,0.09); }
  .search-icon { color:rgba(255,255,255,0.28);flex-shrink:0; }
  .search-input { flex:1;background:transparent;border:none;outline:none;color:#fff;font-family:'DM Sans',sans-serif;font-size:15px;font-weight:300;padding:13px 0;caret-color:#a855f7;min-width:0; }
  .search-input::placeholder { color:rgba(255,255,255,0.22); }
  .search-btn { flex-shrink:0;background:linear-gradient(135deg,#a855f7,#6366f1);border:none;border-radius:14px;padding:12px 22px;color:#fff;font-family:'DM Sans',sans-serif;font-size:14px;font-weight:500;cursor:pointer;white-space:nowrap;display:flex;align-items:center;gap:7px;transition:opacity 0.2s,transform 0.15s; }
  .search-btn:hover { opacity:0.88;transform:scale(1.02); }
  .search-btn:active { transform:scale(0.97); }
  .btn-icon { font-size:14px;animation:spin 4s linear infinite; }
  @keyframes spin { to{transform:rotate(360deg)} }

  /* CHIPS */
  .chips { display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:14px auto 0;max-width:620px; }
  .chip { background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:99px;padding:5px 13px;font-size:12px;color:rgba(255,255,255,0.38);cursor:pointer;transition:all 0.2s;font-family:'DM Sans',sans-serif;white-space:nowrap; }
  .chip:hover { background:rgba(168,85,247,0.12);border-color:rgba(168,85,247,0.3);color:#c084fc; }

  /* DIVIDER */
  .divider { display:flex;align-items:center;gap:16px;margin:52px 0 28px; }
  .dline { flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.07),transparent); }
  .dlabel { font-size:11px;letter-spacing:0.1em;color:rgba(255,255,255,0.2);text-transform:uppercase;white-space:nowrap; }

  /* FEATURE CARDS */
  .feats { display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:36px; }
  .feat { background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:22px 18px;transition:all 0.25s;position:relative;overflow:hidden; }
  .feat::after { content:'';position:absolute;inset:0;border-radius:16px;opacity:0;transition:opacity 0.25s; }
  .feat.p::after { background:radial-gradient(circle at 0 0,rgba(168,85,247,0.13),transparent 60%); }
  .feat.b::after { background:radial-gradient(circle at 0 0,rgba(99,102,241,0.13),transparent 60%); }
  .feat.k::after { background:radial-gradient(circle at 0 0,rgba(232,121,249,0.13),transparent 60%); }
  .feat:hover { transform:translateY(-3px);border-color:rgba(255,255,255,0.12); }
  .feat:hover::after { opacity:1; }
  .ficon { width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:15px;margin-bottom:14px; }
  .feat.p .ficon { background:rgba(168,85,247,0.15); }
  .feat.b .ficon { background:rgba(99,102,241,0.15); }
  .feat.k .ficon { background:rgba(232,121,249,0.15); }
  .ftitle { font-family:'Syne',sans-serif;font-size:13px;font-weight:700;margin-bottom:6px;letter-spacing:-0.2px; }
  .fbody { font-size:12px;line-height:1.6;color:rgba(255,255,255,0.35);font-weight:300; }

  /* PIPELINE */
  .pipeline { background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 22px;display:flex;align-items:center;overflow-x:auto; }
  .step { display:flex;align-items:center;gap:9px;flex:1;min-width:100px; }
  .snum { width:28px;height:28px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;font-family:'Syne',sans-serif; }
  .step:nth-child(1) .snum { background:rgba(168,85,247,0.2);color:#c084fc; }
  .step:nth-child(3) .snum { background:rgba(99,102,241,0.2);color:#818cf8; }
  .step:nth-child(5) .snum { background:rgba(232,121,249,0.2);color:#e879f9; }
  .step:nth-child(7) .snum { background:rgba(52,211,153,0.2);color:#34d399; }
  .sname { font-size:12px;font-weight:500;margin-bottom:1px; }
  .sdesc { font-size:10px;color:rgba(255,255,255,0.3);line-height:1.3; }
  .sarr { color:rgba(255,255,255,0.14);font-size:14px;padding:0 6px;flex-shrink:0; }

  /* RESULTS */
  #panel { display:none;margin-top:40px; }
  #panel.show { display:block; }
  .panel-title { font-family:'Syne',sans-serif;font-size:18px;font-weight:800;letter-spacing:-0.5px;margin-bottom:5px; }
  .panel-topic { font-size:13px;color:rgba(255,255,255,0.35);margin-bottom:20px; }
  .progress-bar { height:2px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;margin-bottom:20px; }
  .progress-inner { height:100%;background:linear-gradient(90deg,#a855f7,#6366f1,#e879f9);background-size:200% 100%;animation:shimmer 1.4s linear infinite;border-radius:99px;width:100%; }
  @keyframes shimmer { 0%{background-position:200% 0}100%{background-position:-200% 0} }
  .agents-row { display:flex;flex-wrap:wrap;gap:8px;margin-bottom:24px; }
  .apill { display:flex;align-items:center;gap:6px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:99px;padding:5px 12px;font-size:11.5px;color:rgba(255,255,255,0.4);transition:all 0.3s; }
  .apill.active { background:rgba(168,85,247,0.1);border-color:rgba(168,85,247,0.35);color:#c084fc; }
  .apill.done { background:rgba(52,211,153,0.07);border-color:rgba(52,211,153,0.3);color:#34d399; }
  .adot { width:5px;height:5px;border-radius:50%;background:currentColor; }
  .adot.spin { animation:glow 0.7s ease infinite; }

  /* REPORT CARD */
  .report-wrap { background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:20px;overflow:hidden; }
  .report-topbar { display:flex;align-items:center;justify-content:space-between;padding:16px 22px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(255,255,255,0.02); }
  .report-topbar-left { display:flex;align-items:center;gap:10px; }
  .report-title-text { font-family:'Syne',sans-serif;font-size:13px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase;color:rgba(255,255,255,0.45); }
  .dl-btn { display:flex;align-items:center;gap:6px;background:rgba(168,85,247,0.12);border:1px solid rgba(168,85,247,0.28);border-radius:10px;padding:6px 14px;font-size:12px;color:#c084fc;font-weight:500;cursor:pointer;transition:all 0.2s;font-family:'DM Sans',sans-serif;white-space:nowrap; }
  .dl-btn:hover { background:rgba(168,85,247,0.22);border-color:rgba(168,85,247,0.5); }
  .report-body { padding:24px 26px; }

  /* Markdown styles */
  .report-body h2 { font-family:'Syne',sans-serif;font-size:17px;font-weight:800;letter-spacing:-0.3px;color:#fff;margin:28px 0 10px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.07); }
  .report-body h2:first-child { margin-top:0; }
  .report-body h3 { font-family:'Syne',sans-serif;font-size:14px;font-weight:700;color:rgba(255,255,255,0.85);margin:20px 0 7px; }
  .report-body p { font-size:14px;line-height:1.8;color:rgba(255,255,255,0.62);font-weight:300;margin-bottom:12px; }
  .report-body ul { padding-left:0;margin-bottom:14px;list-style:none; }
  .report-body ul li { font-size:14px;line-height:1.75;color:rgba(255,255,255,0.62);font-weight:300;margin-bottom:8px;padding-left:18px;position:relative; }
  .report-body ul li::before { content:'–';position:absolute;left:0;color:rgba(168,85,247,0.6); }
  .report-body ol { padding-left:20px;margin-bottom:14px; }
  .report-body ol li { font-size:14px;line-height:1.75;color:rgba(255,255,255,0.62);font-weight:300;margin-bottom:8px; }
  .report-body strong { color:rgba(255,255,255,0.88);font-weight:500; }
  .report-body em { color:rgba(200,180,255,0.75);font-style:italic; }
  .report-body a { color:#a78bfa;text-decoration:none; }
  .report-body a:hover { text-decoration:underline; }
  .report-body code { background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.2);border-radius:4px;padding:1px 6px;font-size:12px;color:#c084fc; }

  /* Sources block */
  .sources-block { margin-top:24px;padding:16px 18px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:12px; }
  .sources-label { font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:rgba(255,255,255,0.25);margin-bottom:10px; }
  .source-item { display:flex;align-items:flex-start;gap:8px;margin-bottom:7px; }
  .source-num { font-size:11px;color:rgba(168,85,247,0.5);font-weight:500;flex-shrink:0;padding-top:1px;min-width:18px; }
  .source-link { font-size:12px;color:rgba(168,85,247,0.75);text-decoration:none;word-break:break-all;transition:color 0.2s;line-height:1.5; }
  .source-link:hover { color:#c084fc; }

  .err { color:rgba(255,100,100,0.7);font-size:13px;padding:20px; }
</style>
</head>
<body>

<div class="orb orb1"></div>
<div class="orb orb2"></div>
<div class="orb orb3"></div>

<div class="wrap">
  <nav>
    <div class="logo"><div class="logo-dot"></div>Nexus Research</div>
    <div class="nav-links">
      <span>How it works</span><span>Agents</span><span>Pricing</span>
    </div>
    <button class="nav-btn">Dashboard →</button>
  </nav>

  <div class="hero">
    <div class="eyebrow"><div class="edot"></div>5 agents · live search · instant synthesis</div>
    <h1>Research anything<br>with <span class="grad">AI agent swarms</span></h1>
    <p class="sub">Multiple AI agents explore different angles simultaneously — then a synthesis agent transforms findings into clear, actionable intelligence.</p>
  </div>

  <div class="search-box">
    <svg class="search-icon" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
      <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
    </svg>
    <input class="search-input" id="q" placeholder="What do you want to research?" autocomplete="off"/>
    <button class="search-btn" onclick="go()">
      <span class="btn-icon">✦</span> Generate Report
    </button>
  </div>

  <div class="chips">
    <div class="chip" onclick="fill(this)">AI in healthcare 2025</div>
    <div class="chip" onclick="fill(this)">Climate tech investment trends</div>
    <div class="chip" onclick="fill(this)">Notion vs Linear deep dive</div>
    <div class="chip" onclick="fill(this)">Quantum computing breakthroughs</div>
    <div class="chip" onclick="fill(this)">Remote work productivity</div>
  </div>

  <div class="divider">
    <div class="dline"></div><div class="dlabel">How the pipeline works</div><div class="dline"></div>
  </div>

  <div class="feats">
    <div class="feat p"><div class="ficon">🔍</div><div class="ftitle">Multi-Agent Search</div><div class="fbody">5 specialized agents scan academic, news, market, forum and primary sources simultaneously.</div></div>
    <div class="feat b"><div class="ficon">🧠</div><div class="ftitle">Synthesis Intelligence</div><div class="fbody">A writing agent cross-references all findings and structures insights by relevance.</div></div>
    <div class="feat k"><div class="ficon">✦</div><div class="ftitle">Quality Review Loop</div><div class="fbody">A critic agent audits accuracy, gaps and bias — so you get reliable intelligence every time.</div></div>
  </div>

  <div class="dlabel" style="margin-bottom:12px;">Agent pipeline</div>
  <div class="pipeline">
    <div class="step"><div class="snum">1</div><div><div class="sname">Query Planner</div><div class="sdesc">Decomposes topic</div></div></div>
    <div class="sarr">→</div>
    <div class="step"><div class="snum">2</div><div><div class="sname">Search Swarm</div><div class="sdesc">5 agents parallel</div></div></div>
    <div class="sarr">→</div>
    <div class="step"><div class="snum">3</div><div><div class="sname">Synthesis Agent</div><div class="sdesc">Merges findings</div></div></div>
    <div class="sarr">→</div>
    <div class="step"><div class="snum">4</div><div><div class="sname">Critic Agent</div><div class="sdesc">Quality review</div></div></div>
  </div>

  <div id="panel">
    <div class="panel-title" id="ptitle"></div>
    <div class="panel-topic" id="ptopic"></div>
    <div class="progress-bar" id="pbar"><div class="progress-inner"></div></div>
    <div class="agents-row" id="arow"></div>
    <div id="result-area"></div>
  </div>
</div>

<script>
const AGENTS = [
  {id:'planner',  name:'Query Planner'},
  {id:'news',     name:'News Agent'},
  {id:'academic', name:'Academic Agent'},
  {id:'market',   name:'Market Agent'},
  {id:'synthesis',name:'Synthesis Agent'},
  {id:'critic',   name:'Critic Agent'},
];

function fill(el){ document.getElementById('q').value=el.textContent; document.getElementById('q').focus(); }
document.getElementById('q').addEventListener('keydown',e=>{ if(e.key==='Enter') go(); });
const delay = ms => new Promise(r=>setTimeout(r,ms));

function setPill(id,state){
  const el=document.getElementById('p-'+id);
  el.className='apill '+state;
  const dot=el.querySelector('.adot');
  dot.className='adot'+(state==='active'?' spin':'');
  if(state==='done') el.innerHTML=`<span class="adot"></span>${AGENTS.find(a=>a.id===id).name} ✓`;
}

/* ── Clean report text: strip internal IDs and the trailing Sources section ──
   lc_run--- IDs are LangChain internal trace IDs, not real sources.
   The Sources paragraph is extracted separately and rendered cleanly below. */
function cleanReport(text){
  // Cut everything from any Sources/References heading onwards —
  // real URLs are extracted separately and shown in the sources block.
  const cutRe = /^#{0,3}\s*(Sources|References|Bibliography)\s*$/im;
  const cutMatch = cutRe.exec(text);
  if(cutMatch) text = text.slice(0, cutMatch.index);

  return text
    // remove lc_run lines (LangChain internal trace IDs)
    .replace(/^\*?\s*lc_run[-\w]+.*$/gm, '')
    // remove [Source N] placeholder lines (fake sources the LLM hallucinates)
    .replace(/^[^\n]*\[Source\s*\d+\][^\n]*/gim, '')
    // remove "URL not provided" / "inaccessible" placeholder lines
    .replace(/^[^\n]*(URL not provided|inaccessible|not provided in the research)[^\n]*/gim, '')
    // remove numbered refs [1] ...
    .replace(/^\[\d+\]\s*\S+/gm, '')
    // collapse extra blank lines
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

/* ── Extract only real https:// URLs, deduplicated ── */
function extractSources(text){
  const seen = new Set();
  const urls = [];
  const re = /https?:\/\/[^\s\)\]\",<>]+/g;
  let m;
  while((m=re.exec(text))!==null){
    let url = m[0].replace(/[.,;:]+$/, ''); // strip trailing punctuation
    if(!seen.has(url)){
      seen.add(url);
      urls.push(url);
    }
  }
  return urls;
}

/* ── Simple markdown → HTML ── */
function renderMd(text){
  text = text.trim();
  text = text.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  text = text.replace(/^## (.+)$/gm,  '<h2>$1</h2>');
  text = text.replace(/^# (.+)$/gm,   '<h2>$1</h2>');
  text = text.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  text = text.replace(/\*\*(.+?)\*\*/g,      '<strong>$1</strong>');
  text = text.replace(/\*([^*\n]+?)\*/g,      '<em>$1</em>');
  text = text.replace(/`(.+?)`/g, '<code>$1</code>');

  // unordered list items
  text = text.replace(/^[-*•]\s+(.+)$/gm, '<li class="ul-item">$1</li>');
  // ordered list items
  text = text.replace(/^\d+\.\s+(.+)$/gm, '<li class="ol-item">$1</li>');

  // wrap consecutive ul-items in <ul>, ol-items in <ol>
  text = text.replace(/(<li class="ul-item">[\s\S]*?<\/li>)(?!\s*<li class="ul-item">)/g, '$1</ul-end>');
  text = text.replace(/(<li class="ul-item">)/g, (m,p,o,s) => {
    const before = s.slice(Math.max(0,o-10),o);
    return before.includes('</ul-end>') || o===0 ? '<ul>'+m : m;
  });
  text = text.replace(/<\/ul-end>/g, '</ul>');
  text = text.replace(/class="ul-item"/g, '');

  text = text.replace(/(<li class="ol-item">[\s\S]*?<\/li>)(?!\s*<li class="ol-item">)/g, '$1</ol-end>');
  text = text.replace(/(<li class="ol-item">)/g, (m,p,o,s) => {
    const before = s.slice(Math.max(0,o-10),o);
    return before.includes('</ol-end>') || o===0 ? '<ol>'+m : m;
  });
  text = text.replace(/<\/ol-end>/g, '</ol>');
  text = text.replace(/class="ol-item"/g, '');

  // paragraphs
  const blocks = text.split(/\n{2,}/);
  text = blocks.map(b=>{
    b = b.trim();
    if(!b) return '';
    if(/^<(h[123]|ul|ol|li)/.test(b)) return b;
    return '<p>'+b.replace(/\n/g,' ')+'</p>';
  }).join('');

  return text;
}

/* ── Download as PDF (exact UI styling) ── */
function downloadReport(topic, renderedHtml, sourcesHtml){

  const win = window.open('', '_blank');

  win.document.write(`
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">

    <title>Nexus Research — ${topic}</title>

    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">

    <style>

      body{
        font-family:'DM Sans',sans-serif;
        background:#07020f;
        color:white;
        padding:48px;
      }

      .report{
        background:rgba(255,255,255,0.03);
        border:1px solid rgba(255,255,255,0.08);
        border-radius:20px;
        padding:32px;
      }

      h1,h2,h3{
        font-family:'Syne',sans-serif;
      }

      p, li{
        color:rgba(255,255,255,0.72);
        line-height:1.8;
      }

      a{
        color:#a78bfa;
      }

      .sources{
        margin-top:30px;
        padding-top:20px;
        border-top:1px solid rgba(255,255,255,0.08);
      }

      @media print{
        body{
          -webkit-print-color-adjust: exact;
          print-color-adjust: exact;
        }
      }

    </style>

  </head>

  <body>

    <h1>Nexus Research</h1>

    <p>
      Generated:
      ${new Date().toLocaleString()}
    </p>

    <div class="report">
      ${renderedHtml}
      ${sourcesHtml}
    </div>

    <script>
      window.onload = () => {
        setTimeout(() => {
          window.print();
        }, 500);
      }
    <\/script>

  </body>
  </html>
  `);

  win.document.close();
}

let lastTopic='', lastReport='';

async function go(){
  const q = document.getElementById('q').value.trim();
  if(!q){ document.getElementById('q').focus(); return; }
  lastTopic = q;

  const panel = document.getElementById('panel');
  const pbar  = document.getElementById('pbar');
  const arow  = document.getElementById('arow');
  const area  = document.getElementById('result-area');

  panel.className='show';
  document.getElementById('ptitle').textContent='Researching…';
  document.getElementById('ptopic').textContent='"'+q+'"';
  pbar.style.display='block';
  arow.innerHTML='';
  area.innerHTML='';
  panel.scrollIntoView({behavior:'smooth',block:'nearest'});

  AGENTS.forEach(a=>{
    const el=document.createElement('div');
    el.className='apill'; el.id='p-'+a.id;
    el.innerHTML=`<span class="adot"></span>${a.name}`;
    arow.appendChild(el);
  });

  // fire pipeline request immediately while pills animate
  const pipelinePromise = fetch('/research',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({topic:q})
  });

  setPill('planner','active');   await delay(800);  setPill('planner','done');
  setPill('news','active'); setPill('academic','active'); setPill('market','active');
  await delay(1300);
  setPill('news','done'); setPill('academic','done'); setPill('market','done');
  setPill('synthesis','active'); await delay(900);  setPill('synthesis','done');
  setPill('critic','active');    await delay(700);  setPill('critic','done');

  try {
    const res  = await pipelinePromise;
    const data = await res.json();
    if(data.error) throw new Error(data.error);

    // clean the report — remove lc_run IDs and duplicate Sources section
    const cleaned = cleanReport(data.report || '');
    lastReport = cleaned;

    // extract real URLs from the ORIGINAL text (before cleaning) for the sources block
    const sources = extractSources(data.report || '');

    pbar.style.display='none';
    document.getElementById('ptitle').textContent='Research Report';

    const sourcesHtml = sources.length ? `
      <div class="sources-block">
        <div class="sources-label">Sources</div>
        ${sources.map((u,i)=>`
          <div class="source-item">
            <span class="source-num">[${i+1}]</span>
            <a class="source-link" href="${u}" target="_blank" rel="noopener">${u}</a>
          </div>`).join('')}
      </div>` : '';

    area.innerHTML = `
      <div class="report-wrap">
        <div class="report-topbar">
          <div class="report-topbar-left">
            <span style="font-size:15px;">📄</span>
            <span class="report-title-text">Report</span>
          </div>
          <button class="dl-btn" onclick="downloadReport(lastTopic, lastReport, renderMd(cleaned),sourcesHtml)">
            ↓ Download
          </button>
        </div>
        <div class="report-body">
          ${renderMd(cleaned)}
          ${sourcesHtml}
        </div>
      </div>
    `;

  } catch(e){
    pbar.style.display='none';
    area.innerHTML=`<div class="err">Error: ${e.message}</div>`;
  }
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return HTML


@app.route("/research", methods=["POST"])
def research():
    body  = request.get_json(force=True)
    topic = body.get("topic", "").strip()
    if not topic:
        return jsonify({"error": "No topic provided"}), 400
    try:
        result = run_search_agent_pipeline(topic)
        return jsonify({
            "report":   result.get("report",   ""),
            "feedback": result.get("feedback", ""),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)