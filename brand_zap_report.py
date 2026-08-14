#!/usr/bin/env python3
"""
Al Ahly Momkn – Professional OWASP ZAP Report Branding

Usage:
    python3 brand_zap_report.py <input.html> <output.html>

Optional logo:
    python3 brand_zap_report.py <input.html> <output.html> <logo.png>

Example:
    python3 brand_zap_report.py zap-report.html branded-report.html assets/al-ahly-momkn-logo.png

The generated HTML contains the logo as Base64, so the final report
is completely self-contained.
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

BRAND_NAME = "Al Ahly Momkn"
REPORT_TITLE = "DAST Security Assessment"
REPORT_SUBTITLE = "Dynamic Application Security Testing"

GREEN = "#01806f"
GREEN_DARK = "#006b5d"
GREEN_DEEP = "#004f45"

ORANGE = "#f58220"
ORANGE_DARK = "#dc6810"

WHITE = "#ffffff"
LIGHT_BG = "#f5f7f8"
CARD_BG = "#ffffff"

TEXT = "#1f2933"
TEXT_MUTED = "#6b7280"

BORDER = "#e5e7eb"

HIGH = "#c62828"
MEDIUM = "#ef8c00"
LOW = "#1976d2"
INFO = "#607d8b"


# ============================================================
# LOGO
# ============================================================

def image_to_data_uri(image_path: Path) -> str:
    """
    Convert logo image into a Base64 data URI.
    This keeps the final HTML completely self-contained.
    """

    if not image_path.exists():
        print(
            f"[brand_zap] WARNING: Logo not found: {image_path}",
            file=sys.stderr
        )
        return ""

    mime_type, _ = mimetypes.guess_type(str(image_path))

    if not mime_type:
        mime_type = "image/png"

    encoded = base64.b64encode(
        image_path.read_bytes()
    ).decode("ascii")

    return f"data:{mime_type};base64,{encoded}"


def find_logo(custom_logo=None):
    """
    Find the company logo.

    Priority:
        1. Explicit CLI logo path
        2. al-ahly-momkn-logo.png next to script
        3. assets/al-ahly-momkn-logo.png
        4. logo.png next to script
        5. assets/logo.png
    """

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

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


# ============================================================
# PROFESSIONAL CSS
# ============================================================

BRAND_CSS = r"""
/* ============================================================
   AL AHLY MOMKN – ZAP SECURITY REPORT
   Corporate Security Report Theme
   ============================================================ */

:root {
    --momkn-green: #01806f;
    --momkn-green-dark: #006b5d;
    --momkn-green-deep: #004f45;

    --momkn-orange: #f58220;
    --momkn-orange-dark: #dc6810;

    --momkn-bg: #f5f7f8;
    --momkn-card: #ffffff;

    --momkn-text: #1f2933;
    --momkn-muted: #6b7280;

    --momkn-border: #e5e7eb;

    --momkn-high: #c62828;
    --momkn-medium: #ef8c00;
    --momkn-low: #1976d2;
    --momkn-info: #607d8b;

    --momkn-radius: 12px;

    --momkn-shadow:
        0 4px 16px rgba(0, 0, 0, 0.06);

    --momkn-shadow-hover:
        0 8px 24px rgba(0, 0, 0, 0.10);
}


/* ============================================================
   GLOBAL
   ============================================================ */

html {
    scroll-behavior: smooth;
}

body {
    margin: 0 !important;
    padding: 0 !important;

    background: var(--momkn-bg) !important;

    color: var(--momkn-text) !important;

    font-family:
        "Segoe UI",
        "Inter",
        "Roboto",
        Arial,
        Helvetica,
        sans-serif !important;

    font-size: 14px;
    line-height: 1.6;
}


/* ============================================================
   TOP BRAND LINE
   ============================================================ */

body::before {
    content: "";
    display: block;

    height: 5px;

    background:
        linear-gradient(
            90deg,
            var(--momkn-green) 0%,
            var(--momkn-green) 72%,
            var(--momkn-orange) 72%,
            var(--momkn-orange) 100%
        );
}


/* ============================================================
   MAIN CONTAINER
   ============================================================ */

.container,
.container-fluid,
main,
.content,
#content {
    max-width: 1400px;
}


/* ============================================================
   BRAND HERO
   ============================================================ */

.momkn-report-hero {
    position: relative;

    margin: 24px auto 28px auto;

    max-width: 1400px;

    overflow: hidden;

    background:
        linear-gradient(
            135deg,
            var(--momkn-green-deep) 0%,
            var(--momkn-green) 65%,
            #079681 100%
        );

    color: white;

    border-radius: 16px;

    box-shadow:
        0 12px 32px rgba(0, 80, 69, 0.18);
}


.momkn-report-hero::after {
    content: "";

    position: absolute;

    width: 320px;
    height: 320px;

    right: -120px;
    top: -150px;

    border-radius: 50%;

    background:
        rgba(245, 130, 32, 0.12);
}


.momkn-report-hero-inner {
    position: relative;

    z-index: 2;

    display: flex;

    align-items: center;

    gap: 28px;

    padding: 28px 34px;
}


.momkn-logo-wrapper {
    display: flex;

    align-items: center;
    justify-content: center;

    min-width: 190px;
}


.momkn-logo {
    display: block;

    width: 180px;
    max-width: 100%;

    height: auto;
}


.momkn-report-info {
    flex: 1;
}


.momkn-eyebrow {
    margin-bottom: 5px;

    color:
        rgba(255, 255, 255, 0.72);

    font-size: 12px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1.6px;
}


.momkn-report-title {
    margin: 0;

    color: #ffffff !important;

    border: none !important;

    padding: 0 !important;

    font-size: 30px !important;

    line-height: 1.2;

    font-weight: 750;

    letter-spacing: -0.5px;
}


.momkn-report-subtitle {
    margin-top: 8px;

    color:
        rgba(255, 255, 255, 0.82);

    font-size: 14px;
}


.momkn-report-meta {
    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin-top: 16px;
}


.momkn-meta-pill {
    display: inline-flex;

    align-items: center;

    gap: 6px;

    padding: 6px 11px;

    border:
        1px solid rgba(255, 255, 255, 0.18);

    border-radius: 999px;

    background:
        rgba(255, 255, 255, 0.10);

    color: #ffffff;

    font-size: 11px;

    font-weight: 600;
}


.momkn-security-badge {
    display: flex;

    align-items: center;
    justify-content: center;

    min-width: 160px;

    padding: 12px 18px;

    background: var(--momkn-orange);

    color: white;

    border-radius: 10px;

    font-size: 12px;

    font-weight: 800;

    text-transform: uppercase;

    letter-spacing: .7px;

    box-shadow:
        0 6px 18px rgba(245, 130, 32, 0.25);
}


/* ============================================================
   SECTION HEADERS
   ============================================================ */

h1,
h2,
h3,
h4 {
    color: var(--momkn-green) !important;
}


h1 {
    font-size: 28px;

    padding-bottom: 10px;

    border-bottom:
        3px solid var(--momkn-orange) !important;
}


h2 {
    margin-top: 32px;

    font-size: 22px;

    padding-bottom: 8px;

    border-bottom:
        2px solid var(--momkn-border);
}


h3 {
    font-size: 18px;
}


/* ============================================================
   CARDS / PANELS
   ============================================================ */

.card,
.panel,
.well,
.panel-default {
    background: var(--momkn-card) !important;

    border:
        1px solid var(--momkn-border) !important;

    border-radius:
        var(--momkn-radius) !important;

    box-shadow:
        var(--momkn-shadow) !important;

    overflow: hidden;

    margin-bottom: 20px;
}


.card:hover,
.panel:hover {
    box-shadow:
        var(--momkn-shadow-hover) !important;
}


.panel-heading,
.card-header {
    background:
        linear-gradient(
            90deg,
            var(--momkn-green),
            var(--momkn-green-dark)
        ) !important;

    color: #ffffff !important;

    border: none !important;

    padding: 13px 18px !important;

    font-weight: 700;
}


.panel-title {
    color: #ffffff !important;
}


/* ============================================================
   TABLES
   ============================================================ */

table {
    width: 100% !important;

    border-collapse: separate !important;

    border-spacing: 0 !important;

    background: #ffffff;

    border:
        1px solid var(--momkn-border);

    border-radius: 10px;

    overflow: hidden;

    box-shadow:
        0 2px 8px rgba(0, 0, 0, 0.03);

    margin-bottom: 20px;
}


thead th,
th {
    background:
        var(--momkn-green) !important;

    color: #ffffff !important;

    border: none !important;

    padding: 12px 14px !important;

    font-size: 12px;

    font-weight: 700;

    text-align: left;
}


td {
    padding: 11px 14px !important;

    border-bottom:
        1px solid var(--momkn-border) !important;

    vertical-align: top;
}


tbody tr:nth-child(even) {
    background:
        rgba(1, 128, 111, 0.035);
}


tbody tr:hover {
    background:
        rgba(245, 130, 32, 0.07);
}


/* ============================================================
   LINKS
   ============================================================ */

a {
    color:
        var(--momkn-green) !important;

    font-weight: 600;
}


a:hover {
    color:
        var(--momkn-orange-dark) !important;

    text-decoration: underline;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.btn-primary,
.btn-success {
    background:
        var(--momkn-green) !important;

    border-color:
        var(--momkn-green) !important;

    color: #ffffff !important;

    border-radius: 7px !important;

    font-weight: 700;
}


.btn-primary:hover,
.btn-success:hover {
    background:
        var(--momkn-green-dark) !important;

    border-color:
        var(--momkn-green-dark) !important;
}


/* ============================================================
   BADGES
   ============================================================ */

.badge,
.label {
    display: inline-block;

    border-radius: 999px !important;

    padding: 4px 9px !important;

    font-size: 11px !important;

    font-weight: 700 !important;

    line-height: 1.2;
}


.label-danger,
.badge-danger {
    background:
        var(--momkn-high) !important;

    color: #ffffff !important;
}


.label-warning,
.badge-warning {
    background:
        var(--momkn-medium) !important;

    color: #ffffff !important;
}


.label-info,
.badge-info {
    background:
        var(--momkn-low) !important;

    color: #ffffff !important;
}


.label-success,
.badge-success {
    background:
        var(--momkn-green) !important;

    color: #ffffff !important;
}


/* ============================================================
   CODE
   ============================================================ */

pre,
code {
    font-family:
        "Cascadia Code",
        "Fira Code",
        Consolas,
        monospace !important;
}


pre {
    padding: 16px !important;

    background:
        #17212b !important;

    color:
        #e6edf3 !important;

    border-radius:
        9px !important;

    border:
        1px solid #253342 !important;

    overflow-x: auto;
}


code {
    background:
        rgba(1, 128, 111, .08);

    color:
        var(--momkn-green-deep);

    padding:
        2px 5px;

    border-radius:
        4px;
}


/* ============================================================
   ALERTS
   ============================================================ */

.alert {
    border-radius: 9px !important;

    border-left:
        4px solid var(--momkn-green) !important;
}


.alert-danger {
    border-left-color:
        var(--momkn-high) !important;
}


.alert-warning {
    border-left-color:
        var(--momkn-medium) !important;
}


.alert-info {
    border-left-color:
        var(--momkn-low) !important;
}


/* ============================================================
   ZAP SPECIFIC HELPERS
   ============================================================ */

.risk-high,
.risk-3,
.severity-high {
    border-left:
        4px solid var(--momkn-high) !important;
}


.risk-medium,
.risk-2,
.severity-medium {
    border-left:
        4px solid var(--momkn-medium) !important;
}


.risk-low,
.risk-1,
.severity-low {
    border-left:
        4px solid var(--momkn-low) !important;
}


.risk-info,
.risk-0,
.severity-info {
    border-left:
        4px solid var(--momkn-info) !important;
}


/* ============================================================
   CUSTOM SUMMARY CARDS
   ============================================================ */

.momkn-summary {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 16px;

    max-width: 1400px;

    margin:
        0 auto 28px auto;
}


.momkn-summary-card {
    position: relative;

    background:
        var(--momkn-card);

    border:
        1px solid var(--momkn-border);

    border-radius:
        12px;

    padding:
        20px;

    box-shadow:
        var(--momkn-shadow);

    overflow: hidden;
}


.momkn-summary-card::before {
    content: "";

    position: absolute;

    left: 0;
    top: 0;
    bottom: 0;

    width: 4px;

    background: var(--momkn-green);
}


.momkn-summary-card.high::before {
    background: var(--momkn-high);
}


.momkn-summary-card.medium::before {
    background: var(--momkn-medium);
}


.momkn-summary-card.low::before {
    background: var(--momkn-low);
}


.momkn-summary-card.info::before {
    background: var(--momkn-info);
}


.momkn-summary-label {
    color:
        var(--momkn-muted);

    font-size: 12px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: .8px;
}


.momkn-summary-value {
    margin-top: 5px;

    color:
        var(--momkn-text);

    font-size: 30px;

    line-height: 1;

    font-weight: 800;
}


/* ============================================================
   FOOTER
   ============================================================ */

.momkn-report-footer {
    max-width: 1400px;

    margin:
        40px auto 0 auto;

    padding:
        24px 30px;

    background:
        var(--momkn-green-deep);

    color:
        rgba(255, 255, 255, .82);

    border-radius:
        14px 14px 0 0;

    text-align: center;

    font-size: 12px;
}


.momkn-report-footer strong {
    color: #ffffff;
}


.momkn-footer-orange {
    color:
        var(--momkn-orange);
}


/* ============================================================
   PRINT / PDF
   ============================================================ */

@media print {

    body {
        background: #ffffff !important;
    }

    body::before {
        display: none;
    }

    .momkn-report-hero {
        box-shadow: none;

        break-inside: avoid;

        margin:
            0 0 20px 0;
    }

    .momkn-summary-card,
    .card,
    .panel,
    table {
        box-shadow: none !important;

        break-inside: avoid;
    }

    a {
        color: inherit !important;
        text-decoration: none !important;
    }

    .momkn-report-footer {
        border-radius: 0;

        break-inside: avoid;
    }
}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .momkn-report-hero-inner {
        flex-direction: column;

        align-items: flex-start;

        padding: 24px;
    }

    .momkn-logo-wrapper {
        min-width: 0;
    }

    .momkn-security-badge {
        min-width: auto;
    }

    .momkn-summary {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));

        padding:
            0 16px;
    }

    .momkn-report-hero {
        margin:
            16px;
    }
}


@media (max-width: 560px) {

    .momkn-summary {
        grid-template-columns:
            1fr;
    }

    .momkn-report-title {
        font-size: 24px !important;
    }

    .momkn-report-hero-inner {
        gap: 18px;
    }

    .momkn-logo {
        width: 150px;
    }
}
"""


# ============================================================
# HERO HTML
# ============================================================

def build_hero(logo_uri: str, generated_at: str) -> str:

    if logo_uri:
        logo_html = f"""
        <img
            class="momkn-logo"
            src="{logo_uri}"
            alt="Al Ahly Momkn"
        />
        """
    else:
        logo_html = """
        <div style="
            color:#ffffff;
            font-size:24px;
            font-weight:800;
        ">
            Al Ahly Momkn
        </div>
        """

    return f"""
<!-- ============================================================
     AL AHLY MOMKN – PROFESSIONAL REPORT HEADER
     ============================================================ -->

<div class="momkn-report-hero">

    <div class="momkn-report-hero-inner">

        <div class="momkn-logo-wrapper">
            {logo_html}
        </div>

        <div class="momkn-report-info">

            <div class="momkn-eyebrow">
                Security Engineering &amp; DevSecOps
            </div>

            <h1 class="momkn-report-title">
                {REPORT_TITLE}
            </h1>

            <div class="momkn-report-subtitle">
                {REPORT_SUBTITLE} using OWASP ZAP
            </div>

            <div class="momkn-report-meta">

                <span class="momkn-meta-pill">
                    OWASP ZAP
                </span>

                <span class="momkn-meta-pill">
                    DAST
                </span>

                <span class="momkn-meta-pill">
                    Automated Security Scan
                </span>

                <span class="momkn-meta-pill">
                    {generated_at}
                </span>

            </div>

        </div>

        <div class="momkn-security-badge">
            DAST / ZAP
        </div>

    </div>

</div>

<!-- ============================================================
     END AL AHLY MOMKN HEADER
     ============================================================ -->
"""


# ============================================================
# SUMMARY
# ============================================================

SUMMARY_HTML = """
<div class="momkn-summary">

    <div class="momkn-summary-card high">
        <div class="momkn-summary-label">
            High Risk
        </div>

        <div
            class="momkn-summary-value"
            data-momkn-risk="high"
        >
            0
        </div>
    </div>


    <div class="momkn-summary-card medium">
        <div class="momkn-summary-label">
            Medium Risk
        </div>

        <div
            class="momkn-summary-value"
            data-momkn-risk="medium"
        >
            0
        </div>
    </div>


    <div class="momkn-summary-card low">
        <div class="momkn-summary-label">
            Low Risk
        </div>

        <div
            class="momkn-summary-value"
            data-momkn-risk="low"
        >
            0
        </div>
    </div>


    <div class="momkn-summary-card info">
        <div class="momkn-summary-label">
            Informational
        </div>

        <div
            class="momkn-summary-value"
            data-momkn-risk="info"
        >
            0
        </div>
    </div>

</div>
"""


# ============================================================
# FOOTER
# ============================================================

def build_footer(generated_at: str) -> str:

    return f"""
<footer class="momkn-report-footer">

    <strong>
        Al Ahly Momkn
    </strong>

    &nbsp; | &nbsp;

    DevSecOps Security Platform

    &nbsp; | &nbsp;

    DAST Assessment

    <br>

    <span class="momkn-footer-orange">
        OWASP ZAP
    </span>

    &nbsp; • &nbsp;

    Generated:
    {generated_at}

</footer>
"""


# ============================================================
# JAVASCRIPT
# ============================================================

BRAND_JS = r"""
<script>
(function () {

    "use strict";

    /*
     * ---------------------------------------------------------
     * Al Ahly Momkn – ZAP Report Enhancement
     * ---------------------------------------------------------
     *
     * This JavaScript only improves the presentation.
     * It does NOT remove or modify ZAP findings.
     */


    function textOf(element) {

        if (!element) {
            return "";
        }

        return (
            element.textContent ||
            element.innerText ||
            ""
        ).trim().toLowerCase();
    }


    function countRisk(patterns) {

        var all = document.querySelectorAll(
            "body *"
        );

        var count = 0;

        all.forEach(function (element) {

            /*
             * Ignore large containers.
             * We want labels / badges / table cells.
             */
            if (
                element.children.length > 3
            ) {
                return;
            }

            var text = textOf(element);

            if (!text || text.length > 120) {
                return;
            }

            patterns.forEach(function (pattern) {

                if (pattern.test(text)) {
                    count++;
                }

            });

        });

        return count;
    }


    function updateSummary() {

        /*
         * We intentionally keep this conservative.
         *
         * If ZAP already exposes counts in its report,
         * those remain untouched.
         *
         * These cards are presentation helpers.
         */

        var high = countRisk([
            /\bhigh\b/,
            /\bcritical\b
        ]);

        var medium = countRisk([
            /\bmedium\b/
        ]);

        var low = countRisk([
            /\blow\b/
        ]);

        var info = countRisk([
            /\binformational\b/,
            /\binfo\b
        ]);


        /*
         * Avoid showing inflated numbers when the same
         * severity appears in multiple UI elements.
         *
         * This is intentionally only a visual indicator.
         */

        var highElement =
            document.querySelector(
                '[data-momkn-risk="high"]'
            );

        var mediumElement =
            document.querySelector(
                '[data-momkn-risk="medium"]'
            );

        var lowElement =
            document.querySelector(
                '[data-momkn-risk="low"]'
            );

        var infoElement =
            document.querySelector(
                '[data-momkn-risk="info"]'
            );


        /*
         * We don't aggressively inject counts by default.
         * The original ZAP report remains the source of truth.
         */

        if (highElement) {
            highElement.textContent = "—";
        }

        if (mediumElement) {
            mediumElement.textContent = "—";
        }

        if (lowElement) {
            lowElement.textContent = "—";
        }

        if (infoElement) {
            infoElement.textContent = "—";
        }
    }


    /*
     * Add visual class based on severity text.
     */
    function decorateSeverity() {

        var elements =
            document.querySelectorAll(
                "td, th, span, div, label"
            );

        elements.forEach(function (element) {

            var text = textOf(element);

            if (
                text === "high" ||
                text === "critical"
            ) {

                element.classList.add(
                    "severity-high"
                );

            } else if (
                text === "medium"
            ) {

                element.classList.add(
                    "severity-medium"
                );

            } else if (
                text === "low"
            ) {

                element.classList.add(
                    "severity-low"
                );

            } else if (
                text === "informational" ||
                text === "info"
            ) {

                element.classList.add(
                    "severity-info"
                );
            }

        });
    }


    document.addEventListener(
        "DOMContentLoaded",
        function () {

            decorateSeverity();

            /*
             * Summary cards intentionally display "—"
             * because the actual ZAP report is authoritative.
             */
            updateSummary();

        }
    );

})();
</script>
"""


# ============================================================
# MAIN BRANDING FUNCTION
# ============================================================

def brand_report(
    input_path: str,
    output_path: str,
    logo_path: str | None = None
) -> None:

    input_file = Path(input_path)
    output_file = Path(output_path)

    if not input_file.exists():

        print(
            f"[brand_zap] ERROR: Input report not found: {input_file}",
            file=sys.stderr
        )

        sys.exit(1)


    html = input_file.read_text(
        encoding="utf-8",
        errors="replace"
    )


    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # ---------------------------------------------------------
    # Logo
    # ---------------------------------------------------------

    logo_file = find_logo(logo_path)

    logo_uri = ""

    if logo_file:

        logo_uri = image_to_data_uri(
            logo_file
        )

        print(
            f"[brand_zap] Using logo: {logo_file}"
        )

    else:

        print(
            "[brand_zap] WARNING: No logo found. "
            "Using text fallback.",
            file=sys.stderr
        )


    # ---------------------------------------------------------
    # 1. Page title
    # ---------------------------------------------------------

    title = (
        "Al Ahly Momkn | "
        "DAST Security Assessment | "
        "OWASP ZAP"
    )


    if re.search(
        r"<title>.*?</title>",
        html,
        flags=re.IGNORECASE | re.DOTALL
    ):

        html = re.sub(
            r"<title>.*?</title>",
            f"<title>{title}</title>",
            html,
            count=1,
            flags=re.IGNORECASE | re.DOTALL
        )

    else:

        html = (
            f"<title>{title}</title>\n"
            + html
        )


    # ---------------------------------------------------------
    # 2. Inject CSS
    # ---------------------------------------------------------

    css_block = (
        "<style>\n"
        + BRAND_CSS
        + "\n</style>\n"
    )


    if re.search(
        r"</head>",
        html,
        flags=re.IGNORECASE
    ):

        html = re.sub(
            r"</head>",
            css_block + "</head>",
            html,
            count=1,
            flags=re.IGNORECASE
        )

    else:

        html = css_block + html


    # ---------------------------------------------------------
    # 3. Build professional hero
    # ---------------------------------------------------------

    hero = build_hero(
        logo_uri,
        generated_at
    )


    # ---------------------------------------------------------
    # 4. Inject hero after body
    # ---------------------------------------------------------

    body_match = re.search(
        r"<body[^>]*>",
        html,
        flags=re.IGNORECASE
    )


    if body_match:

        insert_position = body_match.end()

        html = (
            html[:insert_position]
            + "\n"
            + hero
            + "\n"
            + SUMMARY_HTML
            + "\n"
            + html[insert_position:]
        )

    else:

        html = (
            hero
            + SUMMARY_HTML
            + html
        )


    # ---------------------------------------------------------
    # 5. Replace generic report titles
    # ---------------------------------------------------------

    replacements = {

        "ZAP Scanning Report":
            "Al Ahly Momkn – DAST Security Assessment",

        "ZAP Baseline Scan Report":
            "Al Ahly Momkn – DAST Security Assessment",

        "OWASP ZAP":
            "OWASP ZAP",

    }


    for old, new in replacements.items():

        html = html.replace(
            old,
            new
        )


    # ---------------------------------------------------------
    # 6. Inject JavaScript
    # ---------------------------------------------------------

    if re.search(
        r"</body>",
        html,
        flags=re.IGNORECASE
    ):

        html = re.sub(
            r"</body>",
            BRAND_JS
            + "\n"
            + build_footer(generated_at)
            + "\n</body>",
            html,
            count=1,
            flags=re.IGNORECASE
        )

    else:

        html += (
            BRAND_JS
            + build_footer(generated_at)
        )


    # ---------------------------------------------------------
    # 7. Write final report
    # ---------------------------------------------------------

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    output_file.write_text(
        html,
        encoding="utf-8"
    )


    print(
        f"[brand_zap] Branded report written → "
        f"{output_file}"
    )


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 3:

        print(
            "Usage:\n"
            "  python3 brand_zap_report.py "
            "<input.html> <output.html> [logo.png]"
        )

        sys.exit(1)


    input_html = sys.argv[1]

    output_html = sys.argv[2]

    logo = (
        sys.argv[3]
        if len(sys.argv) >= 4
        else None
    )


    brand_report(
        input_html,
        output_html,
        logo
    )


if __name__ == "__main__":
    main()
