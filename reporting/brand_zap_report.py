#!/usr/bin/env python3
"""
Al Ahly Momkn – Unified DevSecOps Security Report

Creates a single, self-contained HTML security report from:
  1) OWASP ZAP HTML report
  2) Syft SBOM JSON
  3) Grype JSON vulnerability report

Usage:
    python3 brand_zap_report.py <zap_input.html> <output.html>

The script intentionally has no third-party Python dependencies.
It is designed to run directly inside the existing ZAP Jenkins container.
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

GREEN = "#00856f"
GREEN_DARK = "#005f51"
GREEN_DEEP = "#073f38"
ORANGE = "#f58220"
BG = "#f5f7f8"
TEXT = "#1d2b2a"
MUTED = "#667572"
BORDER = "#e4e9e8"
WHITE = "#ffffff"

SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Negligible", "Unknown"]

SEVERITY_COLORS = {
    "Critical": "#b42318",
    "High": "#d84b20",
    "Medium": ORANGE,
    "Low": "#0f766e",
    "Negligible": "#64748b",
    "Unknown": "#7c3aed",
}

ZAP_RISK_MAP = {
    "3": "High",
    "2": "Medium",
    "1": "Low",
    "0": "Informational",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
    "informational": "Informational",
    "info": "Informational",
    "warn": "Medium",
    "warning": "Medium",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text


def first_nonempty(*values: Any, default: str = "-") -> str:
    for value in values:
        if value is not None and clean_text(value):
            return clean_text(value)
    return default


def short(value: Any, limit: int = 110) -> str:
    text = clean_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def fmt_int(value: int) -> str:
    return f"{int(value):,}"


def fmt_date() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def severity_badge(severity: str) -> str:
    sev = clean_text(severity) or "Unknown"
    color = SEVERITY_COLORS.get(sev, "#64748b")
    return (
        f'<span class="severity" style="--sev:{color}">'
        f'<span class="sev-dot"></span>{esc(sev.upper())}</span>'
    )


def safe_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            return json.load(fh)
    except Exception:
        return default


# ---------------------------------------------------------------------------
# ZAP HTML parser
# ---------------------------------------------------------------------------

class TableParser(HTMLParser):
    """Small dependency-free HTML table extractor."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._table = []
        elif self._depth == 1 and tag == "tr":
            self._row = []
        elif self._depth == 1 and tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._depth == 1 and tag in ("td", "th") and self._cell is not None:
            self._row.append(clean_text(" ".join(self._cell)))
            self._cell = None
        elif self._depth == 1 and tag == "tr" and self._row is not None:
            if any(self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._depth:
            if self._depth == 1 and self._table is not None:
                self.tables.append(self._table)
                self._table = None
            self._depth -= 1


def parse_zap(zap_path: Path) -> tuple[list[dict[str, str]], Counter]:
    findings: list[dict[str, str]] = []
    counts: Counter = Counter()

    if not zap_path.exists():
        return findings, counts

    raw = zap_path.read_text(encoding="utf-8", errors="replace")
    parser = TableParser()
    try:
        parser.feed(raw)
    except Exception:
        pass

    for table in parser.tables:
        if not table:
            continue

        # Find a likely ZAP findings table.
        header_idx = None
        normalized: list[str] = []
        for idx, cell in enumerate(table[0]):
            normalized.append(clean_text(cell).lower())
        header_text = " | ".join(normalized)

        if (
            ("risk" in header_text or "riskcode" in header_text)
            and ("url" in header_text or "name" in header_text)
        ):
            header_idx = 0
        else:
            for idx, row in enumerate(table[:5]):
                text = " | ".join(clean_text(x).lower() for x in row)
                if ("risk" in text and "url" in text) or (
                    "confidence" in text and "url" in text
                ):
                    header_idx = idx
                    normalized = [clean_text(x).lower() for x in row]
                    break

        if header_idx is None:
            continue

        headers = normalized
        if not headers:
            continue

        for row in table[header_idx + 1:]:
            if not row:
                continue
            cells = row + [""] * max(0, len(headers) - len(row))
            item = {}
            for i, key in enumerate(headers):
                item[key] = clean_text(cells[i])

            name = first_nonempty(
                item.get("name"),
                item.get("alert"),
                item.get("alert name"),
                item.get("finding"),
                default="ZAP Alert",
            )

            # Avoid summary/navigation rows.
            if name.lower() in {"name", "alert", "risk", "total"}:
                continue

            risk_raw = first_nonempty(
                item.get("risk"),
                item.get("risk code"),
                item.get("riskcode"),
                default="Informational",
            )
            risk_key = risk_raw.lower().strip()
            severity = ZAP_RISK_MAP.get(risk_key, risk_raw.title())

            url = first_nonempty(item.get("url"), item.get("uri"))
            description = first_nonempty(
                item.get("description"),
                item.get("desc"),
                item.get("details"),
            )
            solution = first_nonempty(
                item.get("solution"),
                item.get("recommendation"),
                item.get("fix"),
            )
            confidence = first_nonempty(item.get("confidence"))
            parameter = first_nonempty(item.get("parameter"))
            cwe = first_nonempty(item.get("cwe id"), item.get("cwe"))

            findings.append({
                "severity": severity,
                "name": name,
                "url": url,
                "parameter": parameter,
                "confidence": confidence,
                "description": description,
                "solution": solution,
                "cwe": cwe,
            })

    # Fallback: extract alert names and risk counts from visible text if the
    # exact table layout changed. This keeps the report useful across ZAP
    # report versions without adding a dependency.
    if not findings:
        text = re.sub(r"<[^>]+>", " ", raw)
        text = clean_text(text)
        for match in re.finditer(
            r"(HIGH|MEDIUM|LOW|INFORMATIONAL)\s*[:\-]?\s+(.{8,120}?)(?=\s+(?:HIGH|MEDIUM|LOW|INFORMATIONAL)\b|$)",
            text,
            re.I,
        ):
            severity = match.group(1).title()
            name = short(match.group(2), 120)
            findings.append({
                "severity": severity,
                "name": name,
                "url": "-",
                "parameter": "-",
                "confidence": "-",
                "description": "-",
                "solution": "-",
                "cwe": "-",
            })

    for finding in findings:
        counts[finding["severity"]] += 1

    # De-duplicate identical findings.
    unique: list[dict[str, str]] = []
    seen = set()
    for finding in findings:
        key = tuple(finding.values())
        if key not in seen:
            seen.add(key)
            unique.append(finding)

    return unique, counts


# ---------------------------------------------------------------------------
# SBOM
# ---------------------------------------------------------------------------

def parse_sbom(path: Path) -> dict[str, Any]:
    data = safe_json(path, {})
    artifacts = data.get("artifacts") or []

    type_counts = Counter()
    language_counts = Counter()
    licenses = set()

    rows = []
    for artifact in artifacts:
        name = first_nonempty(artifact.get("name"))
        version = first_nonempty(artifact.get("version"))
        typ = first_nonempty(artifact.get("type"))
        language = clean_text(artifact.get("language"))
        locations = artifact.get("locations") or []
        location = "-"
        if locations and isinstance(locations[0], dict):
            location = first_nonempty(locations[0].get("path"))

        for lic in artifact.get("licenses") or []:
            if isinstance(lic, dict):
                value = first_nonempty(lic.get("spdxExpression"), lic.get("value"), default="")
                if value:
                    licenses.add(value)

        type_counts[typ] += 1
        if language:
            language_counts[language] += 1

        rows.append({
            "name": name,
            "version": version,
            "type": typ,
            "language": language or "-",
            "location": location,
            "purl": first_nonempty(artifact.get("purl")),
        })

    source = data.get("source") or {}
    distro = data.get("distro") or {}
    descriptor = data.get("descriptor") or {}

    return {
        "artifacts": rows,
        "count": len(rows),
        "types": type_counts,
        "languages": language_counts,
        "licenses": licenses,
        "image": first_nonempty(
            source.get("metadata", {}).get("userInput"),
            f"{source.get('name', '')}:{source.get('version', '')}".strip(":"),
        ),
        "distro": first_nonempty(distro.get("prettyName"), distro.get("name")),
        "syft_version": first_nonempty(descriptor.get("version")),
    }


# ---------------------------------------------------------------------------
# Grype
# ---------------------------------------------------------------------------

def parse_grype(path: Path) -> dict[str, Any]:
    data = safe_json(path, {})
    matches = data.get("matches") or []

    rows = []
    severity_counts = Counter()
    fixed_count = 0
    known_exploited = 0
    max_risk = 0.0

    for match in matches:
        vuln = match.get("vulnerability") or {}
        artifact = match.get("artifact") or {}

        severity = clean_text(vuln.get("severity")).title() or "Unknown"
        severity_counts[severity] += 1

        fix = vuln.get("fix") or {}
        fixed_versions = fix.get("versions") or []
        fix_state = clean_text(fix.get("state"))
        if fixed_versions or fix_state == "fixed":
            fixed_count += 1

        kev = vuln.get("knownExploited") or []
        if kev:
            known_exploited += 1

        risk = vuln.get("risk")
        try:
            max_risk = max(max_risk, float(risk))
        except (TypeError, ValueError):
            pass

        cve = vuln.get("id") or ""
        related = vuln.get("relatedVulnerabilities") or []
        if cve.startswith("GHSA-") and related:
            cve = first_nonempty(related[0].get("id"), cve)

        cvss_score = "-"
        cvss = vuln.get("cvss") or []
        if cvss:
            metrics = cvss[0].get("metrics") or {}
            score = metrics.get("baseScore")
            if score is not None:
                cvss_score = f"{float(score):.1f}"

        epss_score = "-"
        epss = vuln.get("epss") or []
        if epss:
            try:
                epss_score = f"{float(epss[0].get('epss', 0)) * 100:.1f}%"
            except (TypeError, ValueError):
                pass

        cwes = vuln.get("cwes") or []
        cwe = "-"
        if cwes:
            cwe = first_nonempty(cwes[0].get("cwe"), default="-")

        fixed = ", ".join(str(x) for x in fixed_versions) if fixed_versions else (
            "No fix available" if fix_state in {"not-fixed", "wont-fix"} else "-"
        )

        rows.append({
            "severity": severity,
            "package": first_nonempty(artifact.get("name")),
            "installed": first_nonempty(artifact.get("version")),
            "fixed": fixed,
            "cve": cve or "-",
            "cvss": cvss_score,
            "epss": epss_score,
            "cwe": cwe,
            "description": first_nonempty(vuln.get("description")),
            "known_exploited": bool(kev),
            "risk": risk if risk is not None else "-",
        })

    return {
        "rows": rows,
        "count": len(rows),
        "severity_counts": severity_counts,
        "fixed_count": fixed_count,
        "known_exploited": known_exploited,
        "max_risk": max_risk,
        "image": first_nonempty(
            (data.get("source") or {}).get("target"),
            (data.get("source") or {}).get("name"),
        ),
        "distro": first_nonempty(
            (data.get("distro") or {}).get("prettyName"),
            (data.get("distro") or {}).get("name"),
        ),
        "grype_version": first_nonempty((data.get("descriptor") or {}).get("version")),
    }


# ---------------------------------------------------------------------------
# HTML components
# ---------------------------------------------------------------------------

def stat_card(label: str, value: Any, subtitle: str = "", accent: str = GREEN) -> str:
    return f"""
    <div class="stat-card">
      <div class="stat-accent" style="background:{accent}"></div>
      <div class="stat-label">{esc(label)}</div>
      <div class="stat-value">{esc(value)}</div>
      <div class="stat-sub">{esc(subtitle)}</div>
    </div>
    """


def tool_card(name: str, tag: str, status: str, detail: str, tone: str) -> str:
    return f"""
    <div class="tool-card">
      <div class="tool-top">
        <span class="tool-tag">{esc(tag)}</span>
        <span class="status-pill {tone}">{esc(status)}</span>
      </div>
      <div class="tool-name">{esc(name)}</div>
      <div class="tool-detail">{esc(detail)}</div>
    </div>
    """


def score_posture(grype: dict[str, Any], zap_counts: Counter) -> tuple[str, str]:
    critical = grype["severity_counts"].get("Critical", 0)
    high = grype["severity_counts"].get("High", 0)

    if critical:
        return "ACTION REQUIRED", "danger"
    if high:
        return "HIGH RISK", "danger"
    if grype["severity_counts"].get("Medium", 0) or zap_counts.get("Medium", 0):
        return "NEEDS ATTENTION", "warning"
    return "HEALTHY", "success"


def render_zap_rows(findings: list[dict[str, str]]) -> str:
    if not findings:
        return """
        <tr><td colspan="6" class="empty">No structured ZAP findings were extracted from the report.</td></tr>
        """

    order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3, "Unknown": 4}
    findings = sorted(findings, key=lambda x: (order.get(x["severity"], 9), x["name"]))

    rows = []
    for f in findings:
        rows.append(f"""
        <tr>
          <td>{severity_badge(f["severity"])}</td>
          <td>
            <div class="finding-name">{esc(short(f["name"], 90))}</div>
            <div class="muted">{esc(short(f["description"], 150))}</div>
          </td>
          <td>{esc(short(f["url"], 80))}</td>
          <td>{esc(short(f["parameter"], 35))}</td>
          <td>{esc(f["confidence"])}</td>
          <td>{esc(f["cwe"])}</td>
        </tr>
        """)
    return "".join(rows)


def render_grype_rows(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return '<tr><td colspan="7" class="empty">No Grype vulnerabilities found.</td></tr>'

    rank = {sev: i for i, sev in enumerate(SEVERITY_ORDER)}
    rows = sorted(rows, key=lambda x: (rank.get(x["severity"], 99), x["package"], x["cve"]))

    output = []
    for item in rows:
        kev = '<span class="kev">KEV</span>' if item["known_exploited"] else ""
        output.append(f"""
        <tr>
          <td>{severity_badge(item["severity"])} {kev}</td>
          <td><strong>{esc(short(item["package"], 45))}</strong><div class="muted">{esc(item["installed"])}</div></td>
          <td>{esc(short(item["cve"], 32))}</td>
          <td><strong>{esc(item["cvss"])}</strong></td>
          <td>{esc(item["epss"])}</td>
          <td>{esc(short(item["fixed"], 42))}</td>
          <td>{esc(item["cwe"])}</td>
        </tr>
        """)
    return "".join(output)


def render_sbom_rows(rows: list[dict[str, str]]) -> str:
    if not rows:
        return '<tr><td colspan="5" class="empty">SBOM data is unavailable.</td></tr>'

    output = []
    for item in sorted(rows, key=lambda x: (x["type"], x["name"].lower())):
        output.append(f"""
        <tr>
          <td><strong>{esc(short(item["name"], 48))}</strong></td>
          <td>{esc(item["version"])}</td>
          <td>{esc(item["type"])}</td>
          <td>{esc(item["language"])}</td>
          <td>{esc(short(item["location"], 75))}</td>
        </tr>
        """)
    return "".join(output)


def render_type_breakdown(type_counts: Counter) -> str:
    if not type_counts:
        return '<div class="empty">No SBOM component types available.</div>'

    parts = []
    for name, count in type_counts.most_common(6):
        parts.append(
            f'<span class="mini-chip"><strong>{fmt_int(count)}</strong> {esc(name)}</span>'
        )
    return "".join(parts)


def build_html(
    zap_findings: list[dict[str, str]],
    zap_counts: Counter,
    sbom: dict[str, Any],
    grype: dict[str, Any],
) -> str:
    generated = fmt_date()
    posture, posture_tone = score_posture(grype, zap_counts)

    critical = grype["severity_counts"].get("Critical", 0)
    high = grype["severity_counts"].get("High", 0)
    medium = grype["severity_counts"].get("Medium", 0)
    low = grype["severity_counts"].get("Low", 0)

    total_findings = sum(grype["severity_counts"].values()) + sum(zap_counts.values())

    zap_total = sum(zap_counts.values())
    grype_total = grype["count"]

    # A transparent posture indicator, not a fabricated numeric security score.
    risk_label = "Critical" if critical else ("High" if high else ("Medium" if medium else "Low"))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Al Ahly Momkn — DevSecOps Security Assessment</title>
<style>
:root {{
  --green:{GREEN};
  --green-dark:{GREEN_DARK};
  --green-deep:{GREEN_DEEP};
  --orange:{ORANGE};
  --bg:{BG};
  --text:{TEXT};
  --muted:{MUTED};
  --border:{BORDER};
  --white:{WHITE};
  --shadow:0 12px 32px rgba(9,55,48,.08);
  --radius:16px;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{
  margin:0;
  background:var(--bg);
  color:var(--text);
  font-family:Inter,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
  line-height:1.5;
}}
a{{color:var(--green);text-decoration:none}}
.shell{{max-width:1500px;margin:0 auto;padding:28px}}
.hero{{
  position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--green-deep),var(--green-dark) 58%,var(--green));
  color:white;border-radius:22px;padding:34px 38px;box-shadow:var(--shadow);
}}
.hero:after{{
  content:"";position:absolute;width:380px;height:380px;border-radius:50%;
  right:-130px;top:-180px;background:rgba(245,130,32,.15);
}}
.hero-inner{{position:relative;z-index:1;display:flex;justify-content:space-between;gap:30px;align-items:center}}
.brand{{display:flex;align-items:center;gap:18px}}
.logo{{
  width:70px;height:70px;border-radius:18px;background:var(--orange);
  display:grid;place-items:center;font-weight:900;font-size:24px;letter-spacing:-1px;
  box-shadow:0 8px 22px rgba(0,0,0,.18);
}}
.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:2px;opacity:.72;font-weight:700}}
h1{{margin:4px 0 5px;font-size:30px;line-height:1.15;letter-spacing:-.7px}}
.hero-sub{{margin:0;color:rgba(255,255,255,.75);font-size:14px}}
.hero-meta{{display:flex;flex-wrap:wrap;gap:9px;margin-top:16px}}
.meta-pill{{border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.08);padding:7px 11px;border-radius:999px;font-size:12px}}
.posture{{min-width:205px;text-align:right}}
.posture-label{{font-size:11px;text-transform:uppercase;letter-spacing:1.8px;opacity:.65}}
.posture-value{{font-size:22px;font-weight:800;margin-top:5px}}
.posture-value.warning{{color:#ffd08a}}
.posture-value.danger{{color:#ffb2a8}}
.posture-value.success{{color:#a7f3d0}}

.nav{{
  position:sticky;top:0;z-index:10;margin:18px 0;padding:8px;
  background:rgba(255,255,255,.92);backdrop-filter:blur(10px);
  border:1px solid var(--border);border-radius:14px;box-shadow:0 5px 20px rgba(0,0,0,.04);
  display:flex;gap:5px;overflow:auto;
}}
.nav a{{white-space:nowrap;padding:9px 14px;border-radius:9px;color:#52635f;font-size:13px;font-weight:700}}
.nav a:hover{{background:#edf5f3;color:var(--green)}}

.section{{margin-top:26px}}
.section-head{{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:13px}}
.section-title{{margin:0;font-size:20px;letter-spacing:-.2px}}
.section-kicker{{font-size:11px;color:var(--green);text-transform:uppercase;letter-spacing:1.5px;font-weight:800}}
.section-desc{{margin:4px 0 0;color:var(--muted);font-size:13px}}

.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}}
.stat-card{{background:white;border:1px solid var(--border);border-radius:14px;padding:18px;position:relative;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,.035)}}
.stat-accent{{position:absolute;left:0;top:0;bottom:0;width:4px}}
.stat-label{{font-size:11px;text-transform:uppercase;letter-spacing:1.1px;color:var(--muted);font-weight:800}}
.stat-value{{font-size:30px;font-weight:850;letter-spacing:-1px;margin-top:5px}}
.stat-sub{{font-size:12px;color:var(--muted);margin-top:2px}}

.grid-2{{display:grid;grid-template-columns:1.2fr .8fr;gap:16px}}
.panel{{background:white;border:1px solid var(--border);border-radius:var(--radius);box-shadow:0 5px 20px rgba(0,0,0,.035);overflow:hidden}}
.panel-body{{padding:20px}}
.tool-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:11px}}
.tool-card{{border:1px solid var(--border);border-radius:13px;padding:15px;background:#fbfcfc}}
.tool-top{{display:flex;justify-content:space-between;align-items:center}}
.tool-tag{{font-size:10px;letter-spacing:1.1px;font-weight:800;color:var(--green)}}
.status-pill{{font-size:10px;font-weight:800;padding:4px 8px;border-radius:999px}}
.status-pill.success{{background:#e8f7f1;color:#08735e}}
.status-pill.warning{{background:#fff3df;color:#9a5600}}
.status-pill.danger{{background:#fdebea;color:#a62c20}}
.tool-name{{font-size:16px;font-weight:800;margin-top:8px}}
.tool-detail{{font-size:12px;color:var(--muted);margin-top:2px}}

.posture-box{{display:flex;align-items:center;gap:20px}}
.ring{{width:112px;height:112px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--orange) 0 28%,#e8efed 28% 100%);flex:none}}
.ring:before{{content:"";width:84px;height:84px;border-radius:50%;background:white;position:absolute}}
.ring-inner{{position:relative;text-align:center}}
.ring-number{{font-size:25px;font-weight:900}}
.ring-label{{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}}
.posture-copy h3{{margin:0;font-size:17px}}
.posture-copy p{{margin:5px 0;color:var(--muted);font-size:12px}}

.table-wrap{{overflow:auto}}
table{{width:100%;border-collapse:collapse;min-width:900px}}
th{{background:#f7faf9;color:#5d6d69;text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:.9px;padding:12px 14px;border-bottom:1px solid var(--border);white-space:nowrap}}
td{{padding:12px 14px;border-bottom:1px solid #edf1f0;font-size:12px;vertical-align:top}}
tr:hover td{{background:#fbfdfc}}
.finding-name{{font-weight:800;color:#22322f}}
.muted{{font-size:11px;color:var(--muted);margin-top:3px;max-width:360px}}
.severity{{display:inline-flex;align-items:center;gap:6px;padding:5px 8px;border-radius:7px;background:color-mix(in srgb,var(--sev) 9%,white);color:var(--sev);font-size:10px;font-weight:900;letter-spacing:.5px;white-space:nowrap}}
.sev-dot{{width:6px;height:6px;border-radius:50%;background:var(--sev)}}
.kev{{display:inline-block;background:#5b1f1f;color:white;border-radius:5px;padding:3px 5px;font-size:8px;font-weight:900;margin-left:4px;vertical-align:middle}}
.empty{{text-align:center;color:var(--muted);padding:30px!important}}

.chips{{display:flex;flex-wrap:wrap;gap:7px}}
.mini-chip{{border:1px solid var(--border);background:#f8faf9;border-radius:999px;padding:7px 10px;font-size:11px;color:#52635f}}
.mini-chip strong{{color:var(--green);margin-right:3px}}

.search{{width:260px;max-width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:9px;outline:none;font-size:12px}}
.search:focus{{border-color:var(--green);box-shadow:0 0 0 3px rgba(0,133,111,.08)}}

.footer{{margin:36px 0 12px;background:var(--green-deep);color:white;border-radius:18px;padding:22px 25px;display:flex;justify-content:space-between;gap:20px;align-items:center}}
.footer strong{{font-size:13px}}
.footer small{{display:block;color:rgba(255,255,255,.62);margin-top:4px}}
.footer-right{{text-align:right;color:rgba(255,255,255,.65);font-size:11px}}

@media(max-width:900px){{
  .shell{{padding:14px}}
  .hero{{padding:25px}}
  .hero-inner{{align-items:flex-start;flex-direction:column}}
  .posture{{text-align:left}}
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .grid-2{{grid-template-columns:1fr}}
}}
@media(max-width:520px){{
  .stats,.tool-grid{{grid-template-columns:1fr}}
  h1{{font-size:24px}}
  .logo{{width:58px;height:58px}}
}}
@media print{{
  .nav,.search{{display:none!important}}
  body{{background:white}}
  .hero,.panel,.stat-card{{box-shadow:none}}
  .section{{break-inside:avoid}}
}}
</style>
</head>
<body>
<div class="shell">

<header class="hero">
  <div class="hero-inner">
    <div>
      <div class="brand">
        <div class="logo">AM</div>
        <div>
          <div class="eyebrow">Al Ahly Momkn</div>
          <h1>DevSecOps Security Assessment</h1>
          <p class="hero-sub">Unified application, software supply-chain and runtime security report</p>
        </div>
      </div>
      <div class="hero-meta">
        <span class="meta-pill">Build: {esc(sbom["image"])}</span>
        <span class="meta-pill">Target: {esc(sbom["distro"])}</span>
        <span class="meta-pill">Generated: {esc(generated)}</span>
      </div>
    </div>
    <div class="posture">
      <div class="posture-label">Security Posture</div>
      <div class="posture-value {posture_tone}">{esc(posture)}</div>
      <div class="hero-sub">Highest observed risk: {esc(risk_label)}</div>
    </div>
  </div>
</header>

<nav class="nav">
  <a href="#overview">Overview</a>
  <a href="#dast">ZAP / DAST</a>
  <a href="#sca">Grype / SCA</a>
  <a href="#sbom">SBOM</a>
</nav>

<section id="overview" class="section">
  <div class="section-head">
    <div>
      <div class="section-kicker">01 · Executive Overview</div>
      <h2 class="section-title">Security posture at a glance</h2>
      <p class="section-desc">A consolidated view of the artifacts produced by the DevSecOps security stages.</p>
    </div>
  </div>

  <div class="stats">
    {stat_card("Critical", fmt_int(critical), "Grype vulnerabilities", SEVERITY_COLORS["Critical"])}
    {stat_card("High", fmt_int(high), "Grype vulnerabilities", SEVERITY_COLORS["High"])}
    {stat_card("Medium", fmt_int(medium), "Grype vulnerabilities", SEVERITY_COLORS["Medium"])}
    {stat_card("Components", fmt_int(sbom["count"]), "SBOM inventory", GREEN)}
  </div>

  <div class="grid-2" style="margin-top:16px">
    <div class="panel">
      <div class="panel-body">
        <div class="section-kicker">Security Pipeline</div>
        <h3 style="margin:4px 0 15px">Control coverage</h3>
        <div class="tool-grid">
          {tool_card("Syft", "SBOM", "GENERATED", f'{fmt_int(sbom["count"])} components inventoried', "success")}
          {tool_card("Grype", "SCA", "FINDINGS", f'{fmt_int(grype_total)} vulnerability matches', "danger" if critical or high else "warning")}
          {tool_card("OWASP ZAP", "DAST", "SCANNED", f'{fmt_int(zap_total)} findings extracted', "warning" if zap_total else "success")}
          {tool_card("Security Report", "REPORTING", "READY", "Unified self-contained HTML", "success")}
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-body posture-box">
        <div class="ring">
          <div class="ring-inner">
            <div class="ring-number">{fmt_int(total_findings)}</div>
            <div class="ring-label">Findings</div>
          </div>
        </div>
        <div class="posture-copy">
          <div class="section-kicker">Risk Summary</div>
          <h3>{esc(posture)}</h3>
          <p>Grype reports {fmt_int(grype_total)} SCA matches. ZAP contributes {fmt_int(zap_total)} extracted DAST findings.</p>
          <p><strong>{fmt_int(grype["known_exploited"])}</strong> Grype matches are marked as known exploited.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section id="dast" class="section">
  <div class="section-head">
    <div>
      <div class="section-kicker">02 · Dynamic Application Security Testing</div>
      <h2 class="section-title">OWASP ZAP findings</h2>
      <p class="section-desc">Findings extracted from the raw ZAP HTML report generated by the baseline scan.</p>
    </div>
    <input class="search" data-table="zap-table" placeholder="Filter ZAP findings…" oninput="filterTable(this)">
  </div>

  <div class="panel">
    <div class="panel-body">
      <div class="chips" style="margin-bottom:14px">
        {stat_card("High", fmt_int(zap_counts.get("High", 0)), "ZAP", SEVERITY_COLORS["High"])}
        {stat_card("Medium", fmt_int(zap_counts.get("Medium", 0)), "ZAP", SEVERITY_COLORS["Medium"])}
        {stat_card("Low", fmt_int(zap_counts.get("Low", 0)), "ZAP", SEVERITY_COLORS["Low"])}
        {stat_card("Info", fmt_int(zap_counts.get("Informational", 0)), "ZAP", "#64748b")}
      </div>
      <div class="table-wrap">
        <table id="zap-table">
          <thead><tr>
            <th>Severity</th><th>Finding</th><th>URL</th><th>Parameter</th><th>Confidence</th><th>CWE</th>
          </tr></thead>
          <tbody>{render_zap_rows(zap_findings)}</tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<section id="sca" class="section">
  <div class="section-head">
    <div>
      <div class="section-kicker">03 · Software Composition Analysis</div>
      <h2 class="section-title">Grype vulnerability intelligence</h2>
      <p class="section-desc">Package-level vulnerabilities with remediation, CVSS, EPSS and known-exploitation context when supplied by Grype.</p>
    </div>
    <input class="search" data-table="grype-table" placeholder="Filter vulnerabilities…" oninput="filterTable(this)">
  </div>

  <div class="panel">
    <div class="panel-body">
      <div class="stats" style="margin-bottom:18px">
        {stat_card("Critical", fmt_int(critical), "Grype", SEVERITY_COLORS["Critical"])}
        {stat_card("High", fmt_int(high), "Grype", SEVERITY_COLORS["High"])}
        {stat_card("Medium", fmt_int(medium), "Grype", SEVERITY_COLORS["Medium"])}
        {stat_card("Low", fmt_int(low), "Grype", SEVERITY_COLORS["Low"])}
      </div>
      <div class="chips" style="margin-bottom:18px">
        <span class="mini-chip"><strong>{fmt_int(grype["fixed_count"])}</strong> matches with fix data</span>
        <span class="mini-chip"><strong>{fmt_int(grype["known_exploited"])}</strong> known exploited</span>
        <span class="mini-chip"><strong>{esc(grype["grype_version"])}</strong> Grype</span>
        <span class="mini-chip"><strong>{esc(grype["distro"])}</strong></span>
      </div>
      <div class="table-wrap">
        <table id="grype-table">
          <thead><tr>
            <th>Severity</th><th>Package</th><th>CVE / Advisory</th><th>CVSS</th><th>EPSS</th><th>Fix</th><th>CWE</th>
          </tr></thead>
          <tbody>{render_grype_rows(grype["rows"])}</tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<section id="sbom" class="section">
  <div class="section-head">
    <div>
      <div class="section-kicker">04 · Software Bill of Materials</div>
      <h2 class="section-title">SBOM inventory</h2>
      <p class="section-desc">Software components discovered across all image layers by Syft.</p>
    </div>
    <input class="search" data-table="sbom-table" placeholder="Filter components…" oninput="filterTable(this)">
  </div>

  <div class="panel">
    <div class="panel-body">
      <div class="stats" style="margin-bottom:18px">
        {stat_card("Components", fmt_int(sbom["count"]), "Syft inventory", GREEN)}
        {stat_card("Types", fmt_int(len(sbom["types"])), "Component types", GREEN)}
        {stat_card("Licenses", fmt_int(len(sbom["licenses"])), "Distinct identifiers", GREEN)}
        {stat_card("Languages", fmt_int(len(sbom["languages"])), "Detected", GREEN)}
      </div>

      <div class="chips" style="margin-bottom:18px">
        {render_type_breakdown(sbom["types"])}
      </div>

      <div class="table-wrap">
        <table id="sbom-table">
          <thead><tr>
            <th>Component</th><th>Version</th><th>Type</th><th>Language</th><th>Location</th>
          </tr></thead>
          <tbody>{render_sbom_rows(sbom["artifacts"])}</tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<footer class="footer">
  <div>
    <strong>Al Ahly Momkn · DevSecOps Engineering</strong>
    <small>Confidential &amp; Proprietary · Unified Security Assessment</small>
  </div>
  <div class="footer-right">
    Generated {esc(generated)}<br>
    Syft {esc(sbom["syft_version"])} · Grype {esc(grype["grype_version"])}
  </div>
</footer>

</div>

<script>
function filterTable(input) {{
  const id = input.getAttribute('data-table');
  const table = document.getElementById(id);
  const query = input.value.toLowerCase().trim();
  if (!table) return;
  table.querySelectorAll('tbody tr').forEach(row => {{
    row.style.display = row.innerText.toLowerCase().includes(query) ? '' : 'none';
  }});
}}
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def brand_report(input_path: str, output_path: str) -> None:
    zap_path = Path(input_path)
    output = Path(output_path)

    # Jenkins workspace is the parent of the output report.
    workspace = output.parent

    sbom_path = workspace / "sbom.json"
    grype_path = workspace / "grype-report.json"

    zap_findings, zap_counts = parse_zap(zap_path)
    sbom = parse_sbom(sbom_path)
    grype = parse_grype(grype_path)

    report = build_html(zap_findings, zap_counts, sbom, grype)
    output.write_text(report, encoding="utf-8")

    print(f"[brand_zap] Unified report written -> {output}")
    print(f"[brand_zap] ZAP findings: {sum(zap_counts.values())}")
    print(f"[brand_zap] SBOM components: {sbom['count']}")
    print(f"[brand_zap] Grype matches: {grype['count']}")
    print(
        "[brand_zap] Grype severity: "
        + ", ".join(
            f"{sev}={grype['severity_counts'].get(sev, 0)}"
            for sev in SEVERITY_ORDER
            if grype["severity_counts"].get(sev, 0)
        )
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 brand_zap_report.py <input.html> <output.html>")
        sys.exit(2)

    try:
        brand_report(sys.argv[1], sys.argv[2])
    except Exception as exc:
        print(f"[brand_zap] ERROR: {exc}", file=sys.stderr)
        sys.exit(1)