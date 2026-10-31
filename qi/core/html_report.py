"""
Simple HTML Evidence Report Generator
"""

from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any


def generate_html_report(report: Dict[str, Any], output_dir: str = "reports/html") -> str:
    """Generate a clean HTML investigation report from an evidence dict."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    safe_name = (
        report.get("test_name", "unknown")
        .replace("/", "_")
        .replace("::", "_")
        .replace(" ", "_")
    )
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{ts}.html"
    filepath = Path(output_dir) / filename

    status_color = "#e74c3c" if report.get("status") == "failed" else "#27ae60"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Failure Evidence – {report.get('test_name')}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; background: #f8f9fa; color: #333; }}
    .card {{ background: white; border-radius: 12px; padding: 28px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); max-width: 900px; margin: auto; }}
    h1 {{ margin-top: 0; }}
    .status {{ display: inline-block; padding: 6px 14px; border-radius: 20px; color: white; background: {status_color}; font-weight: 600; }}
    .meta {{ color: #666; margin: 12px 0 24px; }}
    .section {{ margin-bottom: 24px; }}
    .section h3 {{ border-bottom: 2px solid #eee; padding-bottom: 6px; }}
    pre {{ background: #f1f3f5; padding: 14px; border-radius: 8px; overflow-x: auto; font-size: 13px; }}
    img {{ max-width: 100%; border-radius: 8px; border: 1px solid #ddd; }}
    .label {{ font-weight: 600; color: #555; }}
  </style>
</head>
<body>
  <div class="card">
    <h1>Failure Evidence Report</h1>
    <div class="status">{report.get('status', 'unknown').upper()}</div>
    <div class="meta">
      <div><span class="label">Test:</span> {report.get('test_name')}</div>
      <div><span class="label">Timestamp:</span> {report.get('timestamp')}</div>
    </div>

    <div class="section">
      <h3>Error Message</h3>
      <pre>{report.get('error_message') or 'No error message'}</pre>
    </div>

    <div class="section">
      <h3>Stack Trace</h3>
      <pre>{report.get('stack_trace') or 'No stack trace'}</pre>
    </div>

    <div class="section">
      <h3>Screenshot</h3>
      {"<img src='" + report['screenshot'] + "' alt='screenshot'>" if report.get('screenshot') and not str(report['screenshot']).startswith('screenshot_failed') else "<p>No screenshot available</p>"}
    </div>

    <div class="section">
      <h3>Logs</h3>
      <pre>{chr(10).join(report.get('logs') or ['No logs collected'])}</pre>
    </div>

    <div class="section">
      <h3>Extra Info</h3>
      <pre>{report.get('extra') or {}}</pre>
    </div>
  </div>
</body>
</html>
"""

    filepath.write_text(html, encoding="utf-8")
    return str(filepath)