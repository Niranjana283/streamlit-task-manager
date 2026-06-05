"""
Shared theme / CSS injector for TaskFlow Pro.
Import and call inject_theme() at the top of every page.
"""
import streamlit as st


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base reset ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #0d1117 !important; }

/* ── Block container padding ── */
.block-container { padding: 2rem 2.5rem !important; }

/* ── Inputs ── */
input, textarea {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
}
input:focus, textarea:focus { border-color: #58a6ff !important; box-shadow: 0 0 0 3px rgba(88,166,255,.15) !important; }
div[data-baseweb="select"] > div {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}
div[data-baseweb="popover"] li { background: #161b22 !important; color: #e6edf3 !important; }
div[data-baseweb="popover"] li:hover { background: #21262d !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1f6feb 0%, #388bfd 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.45rem 1.2rem !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(56,139,253,.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover { box-shadow: 0 6px 20px rgba(46,160,67,.4) !important; }

/* ── Forms ── */
[data-testid="stForm"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    padding: 24px !important;
}

/* ── Labels ── */
label, .stTextInput label, .stSelectbox label, .stDateInput label {
    color: #8b949e !important;
    font-size: .82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: .6px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
.dvn-scroller { background: #0d1117 !important; }

/* ── Alerts ── */
.stSuccess { background: #0d1f17 !important; border-left: 4px solid #3fb950 !important; border-radius: 8px !important; color: #3fb950 !important; }
.stError   { background: #1f0d0d !important; border-left: 4px solid #f85149 !important; border-radius: 8px !important; color: #f85149 !important; }
.stInfo    { background: #0d1929 !important; border-left: 4px solid #58a6ff !important; border-radius: 8px !important; color: #58a6ff !important; }
.stWarning { background: #1f1700 !important; border-left: 4px solid #d29922 !important; border-radius: 8px !important; color: #d29922 !important; }

/* ── Divider ── */
hr { border-color: #21262d !important; margin: 1rem 0 !important; }

/* ── Metrics ── */
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size:.75rem !important; }
[data-testid="stMetricValue"] { color: #e6edf3 !important; font-weight: 700 !important; }

/* ── Checkbox ── */
[data-testid="stCheckbox"] span { color: #c9d1d9 !important; }

/* ── Page title override ── */
h1 { color: #e6edf3 !important; font-weight: 800 !important; }
h2, h3 { color: #c9d1d9 !important; font-weight: 700 !important; }
p, li { color: #8b949e !important; }
</style>
"""


def inject_theme():
    """Call this at the top of every page after set_page_config."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    """Renders a consistent dark page header card."""
    sub_html = f'<p style="color:#8b949e;font-size:.88rem;margin:6px 0 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="
        background:linear-gradient(135deg,#161b22 0%,#0d1117 100%);
        border:1px solid #30363d;
        border-radius:14px;
        padding:24px 28px;
        margin-bottom:24px;
        display:flex; align-items:center; gap:18px;
    ">
        <span style="font-size:2.2rem;line-height:1;">{icon}</span>
        <div>
            <h1 style="color:#e6edf3;font-size:1.55rem;font-weight:800;margin:0;">{title}</h1>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(label: str):
    """A subtle section label."""
    st.markdown(f"""
    <p style="color:#8b949e;font-size:.75rem;font-weight:600;
              text-transform:uppercase;letter-spacing:1.4px;margin:20px 0 10px;">
        {label}
    </p>""", unsafe_allow_html=True)


def badge(text: str, color: str = "#58a6ff") -> str:
    """Returns HTML for an inline badge."""
    return (
        f'<span style="background:{color}22;color:{color};'
        f'border:1px solid {color}44;border-radius:20px;'
        f'padding:2px 10px;font-size:.75rem;font-weight:600;">{text}</span>'
    )


PRIORITY_COLOR = {"High": "#f85149", "Medium": "#d29922", "Low": "#3fb950"}
STATUS_COLOR   = {"Present": "#3fb950", "Leave": "#f85149", "Partial": "#d29922", "Not Working Day": "#8b949e"}
