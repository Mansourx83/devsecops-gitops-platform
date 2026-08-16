#!/usr/bin/env python3
"""
Al Ahly Momkn – OWASP ZAP Report Branding v3
Professional DevSecOps report with enhanced findings tables.

Usage:
    python3 brand_zap_report.py <input.html> <output.html> [logo.png]
"""

import sys, re, base64, mimetypes
from pathlib import Path
from datetime import datetime

BRAND_NAME    = "Al Ahly Momkn"
REPORT_TITLE  = "DAST Security Assessment"
REPORT_SUBTITLE = "Dynamic Application Security Testing"


# ── Logo helpers ──────────────────────────────────────────────

def image_to_data_uri(p: Path) -> str:
    if not p.exists():
        print(f"[brand_zap] WARNING: Logo not found: {p}", file=sys.stderr)
        return ""
    mime, _ = mimetypes.guess_type(str(p))
    return f"data:{mime or 'image/png'};base64,{base64.b64encode(p.read_bytes()).decode()}"

def find_logo(custom=None):
    if custom:
        p = Path(custom)
        if p.exists(): return p
    base = Path(__file__).resolve().parent
    for c in [base/"al-ahly-momkn-logo.png", base/"assets/al-ahly-momkn-logo.png",
              base/"logo.png", base/"Logo.png", base/"assets/logo.png"]:
        if c.exists(): return c
    return None


# ── CSS ───────────────────────────────────────────────────────

BRAND_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --green:       #01806f;
    --green-dk:    #006b5d;
    --green-deep:  #004f45;
    --green-lt:    #e6f4f2;
    --orange:      #f58220;
    --orange-dk:   #dc6810;
    --bg:          #f0f2f5;
    --card:        #ffffff;
    --text:        #111827;
    --muted:       #6b7280;
    --border:      #e5e7eb;
    --border-dk:   #d1d5db;
    --warn:        #b45309;
    --warn-bg:     #fffbeb;
    --warn-border: #fde68a;
    --info-c:      #1d4ed8;
    --info-bg:     #eff6ff;
    --info-border: #bfdbfe;
    --pass:        #065f46;
    --pass-bg:     #ecfdf5;
    --radius:      10px;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.08);
    --shadow:      0 2px 8px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
}

html { scroll-behavior: smooth; }

body {
    margin: 0 !important; padding: 0 !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif !important;
    font-size: 13.5px; line-height: 1.6;
}

/* top stripe */
body::before {
    content: ""; display: block; height: 3px;
    background: linear-gradient(90deg, var(--green) 0%, var(--green) 78%, var(--orange) 78%);
}

/* page wrapper */
.container, .container-fluid, main, .content, #content {
    max-width: 1280px; margin-left: auto !important; margin-right: auto !important;
    padding: 0 24px;
}

/* headings */
h1, h2, h3, h4 { color: var(--green) !important; font-weight: 700; margin-top: 0; }
h1 { font-size: 22px; padding-bottom: 10px; border-bottom: 2px solid var(--orange) !important; }
h2 { font-size: 17px; margin-top: 32px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
h3 { font-size: 14px; font-weight: 700; }

/* panels */
.card, .panel, .well, .panel-default {
    background: var(--card) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; box-shadow: var(--shadow) !important;
    overflow: hidden; margin-bottom: 16px;
}
.panel-heading, .card-header {
    background: #f8fafb !important; border-bottom: 1px solid var(--border) !important;
    padding: 12px 18px !important; color: var(--text) !important;
}
.panel-title, .panel-heading h3 { color: var(--text) !important; font-size: 13.5px !important; font-weight: 700 !important; }

/* ── TABLES — the main upgrade ── */
table {
    width: 100% !important;
    border-collapse: collapse !important;
    background: var(--card);
    border: 1px solid var(--border-dk);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 20px;
    font-size: 13px;
}

/* header row */
thead th, table > tbody > tr:first-child th {
    background: var(--green-deep) !important;
    color: #fff !important;
    border: none !important;
    padding: 10px 16px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: .6px !important;
    white-space: nowrap;
}

/* data cells */
td {
    padding: 10px 16px !important;
    border: none !important;
    border-bottom: 1px solid var(--border) !important;
    vertical-align: top;
    line-height: 1.5;
}

/* label column (first td in detail tables) */
tr > td:first-child {
    font-weight: 600;
    color: var(--muted);
    width: 160px;
    white-space: nowrap;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: .3px;
    background: #fafafa;
    border-right: 1px solid var(--border) !important;
}

/* row striping */
tbody tr:nth-child(even) > td { background: #fafbfc; }
tbody tr:nth-child(even) > td:first-child { background: #f5f6f7; }
tbody tr:hover > td { background: #f0fdf8 !important; }
tbody tr:last-child > td { border-bottom: none !important; }

/* links */
a { color: var(--green) !important; font-weight: 500; text-decoration: none; }
a:hover { color: var(--orange-dk) !important; text-decoration: underline; }

/* buttons */
.btn-primary, .btn-success {
    background: var(--green) !important; border-color: var(--green) !important;
    color: #fff !important; border-radius: 6px !important; font-weight: 600;
}

/* badges */
.badge, .label {
    display: inline-flex; align-items: center;
    border-radius: 5px !important;
    padding: 3px 9px !important;
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase; letter-spacing: .4px;
}
.label-danger,  .badge-danger  { background: #fee2e2 !important; color: #b91c1c !important; }
.label-warning, .badge-warning { background: var(--warn-bg) !important; color: var(--warn) !important; border: 1px solid var(--warn-border) !important; }
.label-info,    .badge-info    { background: var(--info-bg) !important; color: var(--info-c) !important; border: 1px solid var(--info-border) !important; }
.label-success, .badge-success { background: var(--pass-bg) !important; color: var(--pass) !important; }

/* severity inline badges (injected by JS) */
.zap-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 5px;
    font-size: 11px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .5px;
}
.zap-badge::before { content: ""; width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.zap-badge-warn   { background: var(--warn-bg);  color: var(--warn);   border: 1px solid var(--warn-border); }
.zap-badge-warn::before   { background: var(--warn); }
.zap-badge-info   { background: var(--info-bg);  color: var(--info-c); border: 1px solid var(--info-border); }
.zap-badge-info::before   { background: var(--info-c); }
.zap-badge-pass   { background: var(--pass-bg);  color: var(--pass); }
.zap-badge-pass::before   { background: var(--pass); }

/* code */
pre, code { font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace !important; }
pre {
    padding: 14px !important; background: #0d1117 !important;
    color: #e6edf3 !important; border-radius: 8px !important;
    border: 1px solid #21262d !important; overflow-x: auto; font-size: 12.5px;
}
code { background: rgba(1,128,111,.08); color: var(--green-deep); padding: 2px 5px; border-radius: 4px; }

/* alerts */
.alert { border-radius: 8px !important; border-left: 3px solid var(--green) !important; }
.alert-warning { border-left-color: var(--warn) !important; }
.alert-info    { border-left-color: var(--info-c) !important; }

/* ── findings header (injected) */
.momkn-section-header {
    display: flex; align-items: center; gap: 12px;
    margin: 32px 0 6px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--border-dk);
}
.momkn-section-header h2 {
    margin: 0 !important; padding: 0 !important; border: none !important;
    font-size: 16px !important;
}
.momkn-count-pill {
    padding: 2px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 700;
    background: var(--warn-bg); color: var(--warn);
    border: 1px solid var(--warn-border);
}

/* ── footer */
.momkn-footer {
    max-width: 1280px; margin: 48px auto 0;
    padding: 22px 32px;
    background: var(--green-deep);
    color: rgba(255,255,255,.7);
    border-radius: 12px 12px 0 0;
    text-align: center; font-size: 12px; line-height: 1.8;
}
.momkn-footer strong { color: #fff; }
.momkn-footer-accent { color: var(--orange); font-weight: 700; }
.momkn-footer-sep { display: inline-block; width: 1px; height: 11px; background: rgba(255,255,255,.2); margin: 0 10px; vertical-align: middle; }

/* print */
@media print {
    body { background: #fff !important; }
    body::before { display: none; }
    .momkn-hero, table { break-inside: avoid; box-shadow: none !important; }
    a { color: inherit !important; text-decoration: none !important; }
}

/* responsive */
@media (max-width: 860px) {
    .momkn-hero-inner { flex-direction: column; padding: 22px; }
    tr > td:first-child { width: auto; white-space: normal; }
}
"""


# ── Hero ──────────────────────────────────────────────────────

def build_hero(logo_uri: str, generated_at: str) -> str:
    logo_html = (
        f'<img class="momkn-logo-img" src="{logo_uri}" alt="Al Ahly Momkn" />'
        if logo_uri else
        '<span style="color:#fff;font-size:20px;font-weight:800;">Al Ahly Momkn</span>'
    )
    return f"""
<style>
.momkn-hero {{
    position: relative; overflow: hidden;
    margin: 20px auto 0; max-width: 1280px;
    background: linear-gradient(128deg, #004f45 0%, #017060 55%, #01806f 100%);
    border-radius: 14px; color: #fff;
    box-shadow: 0 8px 32px rgba(0,79,69,.18);
}}
.momkn-hero::after {{
    content: ""; position: absolute;
    width: 300px; height: 300px; right: -80px; top: -130px;
    border-radius: 50%; background: rgba(245,130,32,.09);
    pointer-events: none;
}}
.momkn-hero-inner {{
    position: relative; z-index: 2;
    display: flex; align-items: center; gap: 28px;
    padding: 28px 36px;
}}
.momkn-hero-logo {{
    display: flex; align-items: center; justify-content: center;
    min-width: 180px; padding: 14px 18px;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 12px;
}}
.momkn-logo-img {{ display: block; width: 160px; height: auto; }}
.momkn-hero-info {{ flex: 1; }}
.momkn-eyebrow {{
    font-size: 10.5px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 2px;
    color: rgba(255,255,255,.6); margin-bottom: 7px;
}}
.momkn-hero-title {{
    margin: 0 !important; padding: 0 !important; border: none !important;
    color: #fff !important; font-size: 28px !important;
    font-weight: 800; line-height: 1.15; letter-spacing: -.5px;
}}
.momkn-hero-sub {{
    margin-top: 8px; color: rgba(255,255,255,.72); font-size: 14px;
}}
.momkn-pills {{
    display: flex; flex-wrap: wrap; gap: 7px; margin-top: 16px;
}}
.momkn-pill {{
    display: inline-flex; align-items: center; gap: 5px;
    padding: 5px 12px;
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 999px;
    background: rgba(255,255,255,.09);
    color: #fff; font-size: 11px; font-weight: 600;
}}
.momkn-pill-dot {{
    width: 5px; height: 5px; border-radius: 50%;
    background: #f58220; flex-shrink: 0;
}}
.momkn-badge {{
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; min-width: 110px;
    padding: 16px 18px;
    background: #f58220; border-radius: 12px;
    box-shadow: 0 6px 20px rgba(245,130,32,.28);
    gap: 3px; text-align: center;
}}
.momkn-badge-top {{ font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,.85); }}
.momkn-badge-main {{ font-size: 17px; font-weight: 900; color: #fff; }}

/* scan info strip */
.momkn-strip {{
    display: grid; grid-template-columns: repeat(3,1fr);
    max-width: 1280px; margin: 14px auto 28px;
    background: #fff; border: 1px solid #e5e7eb;
    border-radius: 10px; overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,.05);
}}
.momkn-strip-item {{
    padding: 14px 22px;
    border-right: 1px solid #e5e7eb;
}}
.momkn-strip-item:last-child {{ border-right: none; }}
.momkn-strip-label {{
    font-size: 10.5px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .8px;
    color: #6b7280; margin-bottom: 3px;
}}
.momkn-strip-value {{
    font-size: 13px; font-weight: 600; color: #111827;
    word-break: break-all;
}}
.momkn-strip-value a {{ color: #01806f !important; font-weight: 600; }}
</style>

<div class="momkn-hero">
    <div class="momkn-hero-inner">
        <div class="momkn-hero-logo">{logo_html}</div>
        <div class="momkn-hero-info">
            <div class="momkn-eyebrow">Security Engineering &amp; DevSecOps</div>
            <h1 class="momkn-hero-title">{REPORT_TITLE}</h1>
            <div class="momkn-hero-sub">{REPORT_SUBTITLE} — OWASP ZAP Baseline Scan</div>
            <div class="momkn-pills">
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>OWASP ZAP</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>DAST</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>Baseline Scan</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>{generated_at}</span>
            </div>
        </div>
        <div class="momkn-badge">
            <span class="momkn-badge-top">Scan Type</span>
            <span class="momkn-badge-main">DAST</span>
        </div>
    </div>
</div>

<div class="momkn-strip">
    <div class="momkn-strip-item">
        <div class="momkn-strip-label">Target</div>
        <div class="momkn-strip-value" id="momkn-target">—</div>
    </div>
    <div class="momkn-strip-item">
        <div class="momkn-strip-label">Scan Date</div>
        <div class="momkn-strip-value">{generated_at}</div>
    </div>
    <div class="momkn-strip-item">
        <div class="momkn-strip-label">Tool</div>
        <div class="momkn-strip-value">OWASP ZAP — Automated DAST</div>
    </div>
</div>
"""


# ── Footer ────────────────────────────────────────────────────

def build_footer(generated_at: str) -> str:
    return f"""
<div class="momkn-footer">
    <strong>Al Ahly Momkn</strong>
    <span class="momkn-footer-sep"></span>
    DAST Security Assessment
    <span class="momkn-footer-sep"></span>
    Generated <span class="momkn-footer-accent">{generated_at}</span>
    <br>
    Automated Dynamic Application Security Testing &nbsp;·&nbsp; OWASP ZAP
</div>
"""


# ── JavaScript ────────────────────────────────────────────────

BRAND_JS = r"""
<script>
(function () {
    "use strict";

    /* populate target URL from ZAP output */
    function extractTarget() {
        var el = document.getElementById("momkn-target");
        if (!el) return;
        var html = document.body.innerHTML;
        var m = html.match(/Site:\s*(https?:\/\/[^\s<"]+)/i)
             || html.match(/Target:\s*(https?:\/\/[^\s<"]+)/i);
        if (m) el.innerHTML = '<a href="' + m[1] + '" target="_blank">' + m[1] + '</a>';
    }

    /* hide ZAP's zero-only summary table */
    function hideZeroTable() {
        document.querySelectorAll("table").forEach(function (tbl) {
            var txt = (tbl.textContent || "").toLowerCase();
            if (txt.indexOf("high") < 0 || txt.indexOf("informational") < 0) return;
            var cells = tbl.querySelectorAll("td");
            var allZero = cells.length > 0;
            cells.forEach(function (td) {
                var n = parseInt(td.textContent.trim(), 10);
                if (!isNaN(n) && n > 0) allZero = false;
            });
            if (allZero) tbl.style.display = "none";
        });
    }

    /* hide ZAP / Checkmarx branding elements */
    function hideZapBranding() {
        document.querySelectorAll("img").forEach(function (img) {
            var a = (img.alt || "").toLowerCase();
            if (a.indexOf("zap") >= 0 || a.indexOf("checkmarx") >= 0)
                img.style.display = "none";
        });
        document.querySelectorAll("a,span,p,div,h1,h2,h3,td").forEach(function (el) {
            if (el.children.length > 0) return;
            var t = (el.textContent || "").trim().toLowerCase();
            if (t.indexOf("zap by checkmarx") >= 0) el.style.display = "none";
        });
    }

    /* replace plain "Warning" / "Informational" text in td cells with badges */
    function decorateFindings() {
        document.querySelectorAll("td").forEach(function (td) {
            if (td.children.length > 0) return;
            var t = (td.textContent || "").trim();
            var lower = t.toLowerCase();
            if (lower === "warning" || lower === "warn") {
                td.innerHTML = '<span class="zap-badge zap-badge-warn">Warning</span>';
            } else if (lower === "informational" || lower === "info") {
                td.innerHTML = '<span class="zap-badge zap-badge-info">Informational</span>';
            } else if (lower === "pass" || lower === "passed") {
                td.innerHTML = '<span class="zap-badge zap-badge-pass">Pass</span>';
            }
        });
    }

    /* add finding count next to "Summary of Alerts" heading */
    function addFindingCount() {
        document.querySelectorAll("h2").forEach(function (h2) {
            var t = (h2.textContent || "").toLowerCase();
            if (t.indexOf("summary") < 0 && t.indexOf("alert") < 0) return;
            /* count warning rows in the nearest table */
            var tbl = h2.nextElementSibling;
            while (tbl && tbl.tagName !== "TABLE") tbl = tbl.nextElementSibling;
            if (!tbl) return;
            var rows = tbl.querySelectorAll("tbody tr");
            if (rows.length === 0) return;
            var wrap = document.createElement("div");
            wrap.className = "momkn-section-header";
            h2.parentNode.insertBefore(wrap, h2);
            wrap.appendChild(h2);
            var pill = document.createElement("span");
            pill.className = "momkn-count-pill";
            pill.textContent = rows.length + " finding" + (rows.length !== 1 ? "s" : "");
            wrap.appendChild(pill);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        extractTarget();
        hideZeroTable();
        hideZapBranding();
        decorateFindings();
        addFindingCount();
    });
})();
</script>
"""


# ── Main ──────────────────────────────────────────────────────

def brand_report(input_path: str, output_path: str, logo_path=None) -> None:
    inp = Path(input_path)
    out = Path(output_path)
    if not inp.exists():
        print(f"[brand_zap] ERROR: not found: {inp}", file=sys.stderr); sys.exit(1)

    html = inp.read_text(encoding="utf-8", errors="replace")
    ts   = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    logo_file = find_logo(logo_path)
    logo_uri  = image_to_data_uri(logo_file) if logo_file else ""
    if logo_file: print(f"[brand_zap] Using logo: {logo_file}")
    else: print("[brand_zap] WARNING: No logo — using text fallback.", file=sys.stderr)

    # title
    title = f"Al Ahly Momkn | {REPORT_TITLE} | OWASP ZAP"
    if re.search(r"<title>.*?</title>", html, re.I|re.S):
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, 1, re.I|re.S)
    else:
        html = f"<title>{title}</title>\n" + html

    # CSS
    css = f"<style>\n{BRAND_CSS}\n</style>\n"
    if re.search(r"</head>", html, re.I):
        html = re.sub(r"</head>", css + "</head>", html, 1, re.I)
    else:
        html = css + html

    # hero
    hero = build_hero(logo_uri, ts)
    m = re.search(r"<body[^>]*>", html, re.I)
    if m:
        html = html[:m.end()] + "\n" + hero + "\n" + html[m.end():]
    else:
        html = hero + html

    # title replacements
    for old, new in {
        "ZAP Scanning Report":      "Al Ahly Momkn – DAST Security Assessment",
        "ZAP Baseline Scan Report": "Al Ahly Momkn – DAST Security Assessment",
    }.items():
        html = html.replace(old, new)

    # JS + footer
    footer = build_footer(ts)
    if re.search(r"</body>", html, re.I):
        html = re.sub(r"</body>", lambda _: BRAND_JS + "\n" + footer + "\n</body>", html, 1, re.I)
    else:
        html += BRAND_JS + footer

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[brand_zap] Report → {out}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 brand_zap_report.py <input.html> <output.html> [logo.png]")
        sys.exit(1)
    brand_report(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else None)

if __name__ == "__main__":
    main()