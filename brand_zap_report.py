#!/usr/bin/env python3
"""
Al Ahly Momkn – Professional OWASP ZAP Report Branding v2
Enhanced design matching Al Ahly Momkn website aesthetic.

Usage:
    python3 brand_zap_report_v2.py <input.html> <output.html>

Optional logo:
    python3 brand_zap_report_v2.py <input.html> <output.html> <logo.png>

Example:
    python3 brand_zap_report_v2.py zap-report.html branded-report.html assets/al-ahly-momkn-logo.png
"""

import sys
import re
import base64
import mimetypes
from pathlib import Path
from datetime import datetime


# ============================================================
# BRAND CONFIGURATION
# ============================================================

BRAND_NAME    = "Al Ahly Momkn"
REPORT_TITLE  = "DAST Security Assessment"
REPORT_SUBTITLE = "Dynamic Application Security Testing"


# ============================================================
# LOGO HELPERS
# ============================================================

def image_to_data_uri(image_path: Path) -> str:
    if not image_path.exists():
        print(f"[brand_zap] WARNING: Logo not found: {image_path}", file=sys.stderr)
        return ""
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type:
        mime_type = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def find_logo(custom_logo=None):
    if custom_logo:
        path = Path(custom_logo)
        if path.exists():
            return path
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "al-ahly-momkn-logo.png",
        script_dir / "assets" / "al-ahly-momkn-logo.png",
        script_dir / "logo.png",
        script_dir / "assets" / "logo.png",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ============================================================
# CSS — Momkn-branded, clean, no ZAP chrome
# ============================================================

BRAND_CSS = r"""
/* ============================================================
   AL AHLY MOMKN – ZAP SECURITY REPORT  v2
   ============================================================ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --green:        #01806f;
    --green-dark:   #006b5d;
    --green-deep:   #004f45;
    --green-light:  #e8f5f3;

    --orange:       #f58220;
    --orange-dark:  #dc6810;
    --orange-light: #fff4ea;

    --bg:           #f4f6f8;
    --card:         #ffffff;
    --text:         #1a2332;
    --muted:        #64748b;
    --border:       #e2e8f0;

    --high:         #dc2626;
    --high-bg:      #fef2f2;
    --medium:       #d97706;
    --medium-bg:    #fffbeb;
    --low:          #2563eb;
    --low-bg:       #eff6ff;
    --info:         #475569;
    --info-bg:      #f8fafc;

    --radius:       14px;
    --radius-sm:    8px;
    --shadow:       0 1px 4px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.06);
    --shadow-md:    0 4px 12px rgba(0,0,0,.08), 0 12px 32px rgba(0,0,0,.08);
}

/* ── Reset ────────────────────────────────────────── */
html { scroll-behavior: smooth; }

body {
    margin: 0 !important;
    padding: 0 !important;
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif !important;
    font-size: 14px;
    line-height: 1.65;
}

/* ── Top accent stripe ────────────────────────────── */
body::before {
    content: "";
    display: block;
    height: 4px;
    background: linear-gradient(90deg, var(--green) 0%, var(--green) 75%, var(--orange) 75%, var(--orange) 100%);
}

/* ── Page wrapper ─────────────────────────────────── */
.container, .container-fluid, main, .content, #content {
    max-width: 1320px;
    margin-left: auto !important;
    margin-right: auto !important;
}

/* ── Headings ─────────────────────────────────────── */
h1, h2, h3, h4 { color: var(--green) !important; font-weight: 700; }

h1 {
    font-size: 26px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--orange) !important;
}

h2 {
    margin-top: 30px;
    font-size: 20px;
    padding-bottom: 7px;
    border-bottom: 1px solid var(--border);
}

h3 { font-size: 17px; }

/* ── Cards / panels ───────────────────────────────── */
.card, .panel, .well, .panel-default {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
    overflow: hidden;
    margin-bottom: 20px;
}
.card:hover, .panel:hover { box-shadow: var(--shadow-md) !important; }

.panel-heading, .card-header {
    background: linear-gradient(90deg, var(--green), var(--green-dark)) !important;
    color: #fff !important;
    border: none !important;
    padding: 13px 18px !important;
    font-weight: 700;
}
.panel-title { color: #fff !important; }

/* ── Tables ───────────────────────────────────────── */
table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    background: #fff;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
    margin-bottom: 20px;
}
thead th, th {
    background: var(--green) !important;
    color: #fff !important;
    border: none !important;
    padding: 12px 16px !important;
    font-size: 12px;
    font-weight: 700;
    text-align: left;
    letter-spacing: .4px;
    text-transform: uppercase;
}
td {
    padding: 11px 16px !important;
    border-bottom: 1px solid var(--border) !important;
    vertical-align: top;
}
tbody tr:nth-child(even) { background: rgba(1,128,111,.03); }
tbody tr:hover           { background: rgba(245,130,32,.06); }

/* ── Links ────────────────────────────────────────── */
a { color: var(--green) !important; font-weight: 600; }
a:hover { color: var(--orange-dark) !important; text-decoration: underline; }

/* ── Buttons ──────────────────────────────────────── */
.btn-primary, .btn-success {
    background: var(--green) !important;
    border-color: var(--green) !important;
    color: #fff !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 700;
}
.btn-primary:hover, .btn-success:hover {
    background: var(--green-dark) !important;
    border-color: var(--green-dark) !important;
}

/* ── Badges ───────────────────────────────────────── */
.badge, .label {
    display: inline-block;
    border-radius: 999px !important;
    padding: 4px 10px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    line-height: 1.2;
}
.label-danger,  .badge-danger  { background: var(--high)   !important; color: #fff !important; }
.label-warning, .badge-warning { background: var(--medium) !important; color: #fff !important; }
.label-info,    .badge-info    { background: var(--low)    !important; color: #fff !important; }
.label-success, .badge-success { background: var(--green)  !important; color: #fff !important; }

/* ── Code ─────────────────────────────────────────── */
pre, code { font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace !important; }

pre {
    padding: 16px !important;
    background: #0f1923 !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    border: 1px solid #1e2d3d !important;
    overflow-x: auto;
}
code {
    background: rgba(1,128,111,.08);
    color: var(--green-deep);
    padding: 2px 6px;
    border-radius: 4px;
}

/* ── Alerts ───────────────────────────────────────── */
.alert { border-radius: 9px !important; border-left: 4px solid var(--green) !important; }
.alert-danger  { border-left-color: var(--high)   !important; }
.alert-warning { border-left-color: var(--medium) !important; }
.alert-info    { border-left-color: var(--low)    !important; }

/* ── Severity helpers ─────────────────────────────── */
.risk-high,   .risk-3, .severity-high   { border-left: 4px solid var(--high)   !important; }
.risk-medium, .risk-2, .severity-medium { border-left: 4px solid var(--medium) !important; }
.risk-low,    .risk-1, .severity-low    { border-left: 4px solid var(--low)    !important; }
.risk-info,   .risk-0, .severity-info   { border-left: 4px solid var(--info)   !important; }

/* ── Severity text badges ─────────────────────────── */
.severity-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .5px;
}
.severity-badge.high   { background: var(--high-bg);   color: var(--high);   }
.severity-badge.medium { background: var(--medium-bg); color: var(--medium); }
.severity-badge.low    { background: var(--low-bg);    color: var(--low);    }
.severity-badge.info   { background: var(--info-bg);   color: var(--info);   }

/* ── Footer ───────────────────────────────────────── */
.momkn-footer {
    max-width: 1320px;
    margin: 48px auto 0;
    padding: 28px 32px;
    background: var(--green-deep);
    color: rgba(255,255,255,.75);
    border-radius: 16px 16px 0 0;
    text-align: center;
    font-size: 12px;
    line-height: 1.8;
}
.momkn-footer strong { color: #fff; }
.momkn-footer-accent { color: var(--orange); font-weight: 700; }
.momkn-footer-divider {
    display: inline-block;
    width: 1px; height: 12px;
    background: rgba(255,255,255,.25);
    margin: 0 10px;
    vertical-align: middle;
}

/* ── Print ────────────────────────────────────────── */
@media print {
    body { background: #fff !important; }
    body::before { display: none; }
    .momkn-hero, .card, .panel, table { box-shadow: none !important; break-inside: avoid; }
    a { color: inherit !important; text-decoration: none !important; }
    .momkn-footer { border-radius: 0; break-inside: avoid; }
}

/* ── Responsive ───────────────────────────────────── */
@media (max-width: 900px) {
    .momkn-hero-inner { flex-direction: column; align-items: flex-start; padding: 24px; }
    .momkn-hero-logo  { min-width: 0; }
    .momkn-scan-info  { grid-template-columns: 1fr 1fr; padding: 0 16px; }
    .momkn-hero       { margin: 16px; }
}
@media (max-width: 560px) {
    .momkn-scan-info  { grid-template-columns: 1fr; }
    .momkn-hero-title { font-size: 22px !important; }
}
"""


# ============================================================
# HERO HTML — clean, no summary cards, no ZAP branding
# ============================================================

def build_hero(logo_uri: str, generated_at: str) -> str:

    if logo_uri:
        logo_html = f'<img class="momkn-logo-img" src="{logo_uri}" alt="Al Ahly Momkn" />'
    else:
        logo_html = '<span class="momkn-logo-text">Al Ahly Momkn</span>'

    return f"""
<!-- ============================================================
     AL AHLY MOMKN – REPORT HEADER v2
     ============================================================ -->
<style>
/* ── Hero ─────────────────────────────────────────── */
.momkn-hero {{
    position: relative;
    margin: 24px auto 0;
    max-width: 1320px;
    overflow: hidden;
    background: linear-gradient(130deg, #004f45 0%, #01806f 60%, #079681 100%);
    color: #fff;
    border-radius: 18px;
    box-shadow: 0 12px 40px rgba(0,80,69,.2);
}}
.momkn-hero::after {{
    content: "";
    position: absolute;
    width: 340px; height: 340px;
    right: -100px; top: -160px;
    border-radius: 50%;
    background: rgba(245,130,32,.1);
    pointer-events: none;
}}
.momkn-hero::before {{
    content: "";
    position: absolute;
    width: 200px; height: 200px;
    left: -60px; bottom: -80px;
    border-radius: 50%;
    background: rgba(255,255,255,.04);
    pointer-events: none;
}}
.momkn-hero-inner {{
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    gap: 32px;
    padding: 32px 40px;
}}

/* ── Logo area ────────────────────────────────────── */
.momkn-hero-logo {{
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 200px;
    padding: 16px 20px;
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 14px;
    backdrop-filter: blur(8px);
}}
.momkn-logo-img  {{ display: block; width: 170px; max-width: 100%; height: auto; }}
.momkn-logo-text {{
    color: #fff;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -.5px;
}}

/* ── Title area ───────────────────────────────────── */
.momkn-hero-info {{ flex: 1; }}

.momkn-eyebrow {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(255,255,255,.65);
    margin-bottom: 8px;
}}
.momkn-hero-title {{
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    color: #fff !important;
    font-size: 32px !important;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -.6px;
}}
.momkn-hero-subtitle {{
    margin-top: 10px;
    color: rgba(255,255,255,.78);
    font-size: 15px;
    font-weight: 400;
}}

/* ── Meta pills ───────────────────────────────────── */
.momkn-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 18px;
}}
.momkn-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 13px;
    border: 1px solid rgba(255,255,255,.2);
    border-radius: 999px;
    background: rgba(255,255,255,.1);
    color: #fff;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .3px;
}}
.momkn-pill-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--orange, #f58220);
    flex-shrink: 0;
}}

/* ── Security badge ───────────────────────────────── */
.momkn-badge {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-width: 130px;
    padding: 18px 20px;
    background: var(--orange, #f58220);
    border-radius: 14px;
    font-weight: 800;
    text-align: center;
    box-shadow: 0 8px 24px rgba(245,130,32,.3);
    gap: 4px;
}}
.momkn-badge-top {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: .85;
    color: #fff;
}}
.momkn-badge-main {{
    font-size: 18px;
    font-weight: 900;
    color: #fff;
    letter-spacing: .5px;
}}

/* ── Scan info strip ──────────────────────────────── */
.momkn-scan-strip {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    max-width: 1320px;
    margin: 16px auto 32px;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
}}
.momkn-scan-item {{
    padding: 16px 24px;
    border-right: 1px solid #e2e8f0;
}}
.momkn-scan-item:last-child {{ border-right: none; }}
.momkn-scan-label {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .8px;
    color: #64748b;
    margin-bottom: 4px;
}}
.momkn-scan-value {{
    font-size: 14px;
    font-weight: 600;
    color: #1a2332;
    word-break: break-all;
}}
.momkn-scan-value a {{
    color: var(--green, #01806f) !important;
    font-weight: 600;
}}

/* ── All-clear banner ─────────────────────────────── */
.momkn-all-clear {{
    display: flex;
    align-items: center;
    gap: 18px;
    max-width: 1320px;
    margin: 0 auto 32px;
    padding: 20px 28px;
    background: linear-gradient(90deg, #e8f5f3 0%, #f0fdf9 100%);
    border: 1px solid #a7f3d0;
    border-left: 5px solid #01806f;
    border-radius: 12px;
}}
.momkn-all-clear-icon {{
    font-size: 36px;
    line-height: 1;
    flex-shrink: 0;
}}
.momkn-all-clear-title {{
    font-size: 17px;
    font-weight: 800;
    color: #004f45;
    margin-bottom: 3px;
}}
.momkn-all-clear-desc {{
    font-size: 13px;
    color: #006b5d;
}}
</style>

<div class="momkn-hero">
    <div class="momkn-hero-inner">

        <div class="momkn-hero-logo">
            {logo_html}
        </div>

        <div class="momkn-hero-info">
            <div class="momkn-eyebrow">&amp; DevSecOps Team </div>
            <h1 class="momkn-hero-title">{REPORT_TITLE}</h1>
            <div class="momkn-hero-subtitle">{REPORT_SUBTITLE} using OWASP ZAP</div>
            <div class="momkn-pills">
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>OWASP ZAP</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>DAST</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>Automated Security Scan</span>
                <span class="momkn-pill"><span class="momkn-pill-dot"></span>{generated_at}</span>
            </div>
        </div>

        <div class="momkn-badge">
            <span class="momkn-badge-top">Scan Type</span>
            <span class="momkn-badge-main">DAST</span>
        </div>

    </div>
</div>

<!-- ============================================================
     END AL AHLY MOMKN HEADER
     ============================================================ -->
"""


# ============================================================
# SCAN INFO STRIP — replaces the old zero-filled summary cards
# ============================================================

def build_scan_strip(generated_at: str) -> str:
    return f"""
<div class="momkn-scan-strip">
    <div class="momkn-scan-item">
        <div class="momkn-scan-label">Target</div>
        <div class="momkn-scan-value" id="momkn-target">—</div>
    </div>
    <div class="momkn-scan-item">
        <div class="momkn-scan-label">Generated</div>
        <div class="momkn-scan-value">{generated_at}</div>
    </div>
    <div class="momkn-scan-item">
        <div class="momkn-scan-label">Tool</div>
        <div class="momkn-scan-value">OWASP ZAP 2.x — Automated DAST</div>
    </div>
</div>
"""


# ============================================================
# FOOTER
# ============================================================

def build_footer(generated_at: str) -> str:
    return f"""
<div class="momkn-footer">
    <strong>Al Ahly Momkn</strong>
    <span class="momkn-footer-divider"></span>
    DAST Security Assessment Report
    <span class="momkn-footer-divider"></span>
    Generated <span class="momkn-footer-accent">{generated_at}</span>
    <br>
    Automated Dynamic Application Security Testing &nbsp;·&nbsp; OWASP ZAP
</div>
"""


# ============================================================
# JAVASCRIPT — extracts target from original ZAP report,
#              hides the old ZAP summary tables with zeroes,
#              and decorates severity cells
# ============================================================

BRAND_JS = r"""
<script>
(function () {
    "use strict";

    /* ── Populate target from ZAP report content ─── */
    function extractTarget() {
        var el = document.getElementById("momkn-target");
        if (!el) return;

        /* ZAP writes something like:
           <p>Site: http://...</p>  or  <td>http://...</td>  */
        var patterns = [
            /Site:\s*(https?:\/\/[^\s<"]+)/i,
            /Target:\s*(https?:\/\/[^\s<"]+)/i,
        ];

        var bodyText = document.body.innerHTML;
        for (var i = 0; i < patterns.length; i++) {
            var m = bodyText.match(patterns[i]);
            if (m && m[1]) {
                el.innerHTML =
                    '<a href="' + m[1] + '" target="_blank">' +
                    m[1] + '</a>';
                return;
            }
        }
    }

    /* ── Hide ZAP's own zero-filled summary table ── */
    function hideZapSummaryTable() {
        /*
         * ZAP wraps the 0/0/0/0 summary in a <table> whose
         * first row contains "High", "Medium", "Low", "Informational".
         * We find it and collapse it — the page already has the
         * al-clear banner instead.
         */
        var tables = document.querySelectorAll("table");
        tables.forEach(function (tbl) {
            var text = tbl.textContent || "";
            var lower = text.toLowerCase();
            if (
                lower.indexOf("high") !== -1 &&
                lower.indexOf("medium") !== -1 &&
                lower.indexOf("informational") !== -1 &&
                lower.indexOf("low") !== -1
            ) {
                var cells = tbl.querySelectorAll("td");
                var allZero = true;
                cells.forEach(function (td) {
                    var n = parseInt(td.textContent.trim(), 10);
                    if (!isNaN(n) && n > 0) allZero = false;
                });
                if (allZero) {
                    tbl.style.display = "none";
                }
            }
        });
    }

    /* ── Hide "ZAP by Checkmarx" branding ────────── */
    function hideZapBranding() {
        /* Images with ZAP/Checkmarx alt text */
        document.querySelectorAll("img").forEach(function (img) {
            var alt = (img.alt || "").toLowerCase();
            if (alt.indexOf("zap") !== -1 || alt.indexOf("checkmarx") !== -1) {
                img.style.display = "none";
            }
        });

        /* Any element whose text is exactly "ZAP by Checkmarx" */
        document.querySelectorAll("a, span, p, div, h1, h2, h3").forEach(function (el) {
            var t = (el.textContent || "").trim().toLowerCase();
            if (t === "zap by checkmarx" || t.indexOf("zap by checkmarx") !== -1) {
                el.style.display = "none";
            }
        });
    }

    /* ── Add severity colour classes ─────────────── */
    function decorateSeverity() {
        var map = {
            "high":          "severity-high",
            "critical":      "severity-high",
            "medium":        "severity-medium",
            "low":           "severity-low",
            "informational": "severity-info",
            "info":          "severity-info",
        };
        document.querySelectorAll("td, th, span, div, label").forEach(function (el) {
            var t = (el.textContent || "").trim().toLowerCase();
            if (map[t]) el.classList.add(map[t]);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        extractTarget();
        hideZapSummaryTable();
        hideZapBranding();
        decorateSeverity();
    });
})();
</script>
"""


# ============================================================
# MAIN BRANDING FUNCTION
# ============================================================

def brand_report(input_path: str, output_path: str, logo_path: str | None = None) -> None:

    input_file  = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():
        print(f"[brand_zap] ERROR: Input report not found: {input_file}", file=sys.stderr)
        sys.exit(1)

    html = input_file.read_text(encoding="utf-8", errors="replace")
    generated_at = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

    # ── Logo ──────────────────────────────────────────────────
    logo_file = find_logo(logo_path)
    logo_uri  = ""
    if logo_file:
        logo_uri = image_to_data_uri(logo_file)
        print(f"[brand_zap] Using logo: {logo_file}")
    else:
        print("[brand_zap] WARNING: No logo found. Using text fallback.", file=sys.stderr)

    # ── 1. Page title ──────────────────────────────────────────
    title = f"Al Ahly Momkn | {REPORT_TITLE} | OWASP ZAP"
    if re.search(r"<title>.*?</title>", html, re.IGNORECASE | re.DOTALL):
        html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html,
                      count=1, flags=re.IGNORECASE | re.DOTALL)
    else:
        html = f"<title>{title}</title>\n" + html

    # ── 2. Inject CSS ──────────────────────────────────────────
    css_block = f"<style>\n{BRAND_CSS}\n</style>\n"
    if re.search(r"</head>", html, re.IGNORECASE):
        html = re.sub(r"</head>", css_block + "</head>", html, count=1, flags=re.IGNORECASE)
    else:
        html = css_block + html

    # ── 3. Build hero + scan strip + all-clear banner ──────────
    hero       = build_hero(logo_uri, generated_at)
    scan_strip = build_scan_strip(generated_at)
    banner     = build_all_clear_banner()

    # ── 4. Inject after <body> ─────────────────────────────────
    body_match = re.search(r"<body[^>]*>", html, re.IGNORECASE)
    if body_match:
        pos  = body_match.end()
        html = html[:pos] + "\n" + hero + "\n" + scan_strip + "\n" + banner + "\n" + html[pos:]
    else:
        html = hero + scan_strip + banner + html

    # ── 5. Replace generic ZAP titles ─────────────────────────
    replacements = {
        "ZAP Scanning Report":       "Al Ahly Momkn – DAST Security Assessment",
        "ZAP Baseline Scan Report":  "Al Ahly Momkn – DAST Security Assessment",
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    # ── 6. Inject JS + footer ──────────────────────────────────
    footer = build_footer(generated_at)
    if re.search(r"</body>", html, re.IGNORECASE):
        html = re.sub(r"</body>", lambda m: BRAND_JS + "\n" + footer + "\n</body>",
                      html, count=1, flags=re.IGNORECASE)
    else:
        html += BRAND_JS + footer

    # ── 7. Write output ────────────────────────────────────────
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(html, encoding="utf-8")
    print(f"[brand_zap] Branded report → {output_file}")


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  python3 brand_zap_report_v2.py <input.html> <output.html> [logo.png]"
        )
        sys.exit(1)

    brand_report(
        input_html  := sys.argv[1],
        output_html := sys.argv[2],
        logo        := sys.argv[3] if len(sys.argv) >= 4 else None,
    )


if __name__ == "__main__":
    main()