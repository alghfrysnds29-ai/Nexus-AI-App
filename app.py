<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{
  --bg: #f6f8fb;
  --card: #ffffff;
  --muted: #6b7280;
  --primary: #0f172a;
  --accent: #2563eb;
  --accent-2: #3b82f6;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --radius:14px;
  --shadow: 0 8px 30px rgba(15,23,42,0.06);
  --metric-height:110px;
}

/* Global */
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; background: var(--bg); color: var(--primary); }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,255,255,0.95)); border-left: 1px solid rgba(15,23,42,0.04); padding: 20px; }

/* Top header */
.app-header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  background: linear-gradient(90deg, rgba(37,99,235,0.06), rgba(59,130,246,0.03));
  padding: 14px 20px;
  border-radius: 12px;
  margin-bottom: 18px;
  box-shadow: var(--shadow);
}
.app-brand { display:flex; align-items:center; gap:12px; }
.app-logo { width:48px; height:48px; border-radius:10px; background: linear-gradient(135deg, var(--accent-2), var(--accent)); display:flex; align-items:center; justify-content:center; color:white; font-weight:700; box-shadow: 0 8px 20px rgba(37,99,235,0.12); }
.app-title { font-size:18px; font-weight:700; color:var(--primary); }
.app-actions { display:flex; gap:8px; align-items:center; }

/* Metric cards */
.metric-card { background: var(--card); border-radius: 12px; padding: 14px; box-shadow: var(--shadow); height: var(--metric-height); display:flex; align-items:center; gap:12px; border-left: 4px solid rgba(59,130,246,0.06); }
.metric-icon { width:56px; height:56px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-size:20px; flex-shrink:0; }
.metric-body { flex:1; }
.metric-label { font-size:13px; color:var(--muted); margin-bottom:6px; }
.metric-value { font-size:20px; font-weight:700; color:var(--primary); }

/* Colored icons */
.icon-primary { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.icon-success { background: linear-gradient(135deg, #10b981, #059669); }
.icon-warning { background: linear-gradient(135deg, #f59e0b, #f97316); }

/* Cards grid responsive */
.cards-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; margin-bottom:18px; }
@media (max-width: 1000px) { .cards-grid { grid-template-columns: repeat(1, 1fr); } }

/* Section card */
.section-card { background: var(--card); border-radius: 12px; padding: 18px; box-shadow: var(--shadow); margin-bottom: 18px; }

/* Sidebar controls styling */
.sidebar-section-title { font-weight:700; color:var(--primary); margin-bottom:8px; }
.small-muted { color:var(--muted); font-size:13px; }

/* Buttons */
.stButton>button { border-radius: 10px; padding: 10px 14px; font-weight:600; }
.primary-btn { background: linear-gradient(90deg, var(--accent-2), var(--accent)); color:white; border:none; }

/* Table tweaks */
[data-testid="stDataFrameContainer"] { border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }
</style>
