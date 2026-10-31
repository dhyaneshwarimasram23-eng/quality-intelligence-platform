"""
Failure Evidence Engine
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import json
from pathlib import Path


class EvidenceCollector:
    def __init__(self, report_dir: str = "reports/evidence"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def create_report(
        self,
        test_name: str,
        status: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        video_path: Optional[str] = None,
        trace_path: Optional[str] = None,
        api_response: Optional[Dict] = None,
        logs: Optional[List[str]] = None,
        extra: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        ts = datetime.now(timezone.utc)
        report = {
            "test_name": test_name,
            "status": status,
            "timestamp": ts.isoformat(),
            "error_message": error_message,
            "stack_trace": stack_trace,
            "screenshot": screenshot_path,
            "video": video_path,
            "trace": trace_path,
            "api_response": api_response,
            "logs": logs or [],
            "extra": extra or {},
        }

        safe_name = test_name.replace("/", "_").replace("\\", "_").replace("::", "_").replace(" ", "_")
        filename = f"{safe_name}_{ts.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.report_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        report["report_path"] = str(filepath)
        return report

    def capture_playwright_failure(
        self,
        page,
        test_name: str,
        error_message: str,
        stack_trace: Optional[str] = None,
    ) -> Dict[str, Any]:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        safe = test_name.replace("::", "_").replace("/", "_")
        screenshot_path = str(self.report_dir / f"{safe}_{ts}.png")

        try:
            page.screenshot(path=screenshot_path, full_page=True)
        except Exception as e:
            screenshot_path = f"screenshot_failed: {e}"

        logs = []
        try:
            logs.append(f"Page URL at failure: {page.url}")
            logs.append(f"Page title: {page.title()}")
        except Exception:
            pass

        return self.create_report(
            test_name=test_name,
            status="failed",
            error_message=error_message,
            stack_trace=stack_trace,
            screenshot_path=screenshot_path,
            logs=logs,
            extra={"page_url": getattr(page, "url", None)},
        )

    def print_summary(self, report: Dict):
        print("\n" + "=" * 60)
        print(f"FAILURE EVIDENCE REPORT: {report['test_name']}")
        print("=" * 60)
        print(f"Status      : {report['status']}")
        print(f"Timestamp   : {report['timestamp']}")
        if report.get("error_message"):
            print(f"Error       : {report['error_message']}")
        if report.get("screenshot"):
            print(f"Screenshot  : {report['screenshot']}")
        if report.get("logs"):
            print(f"Logs        : {len(report['logs'])} lines collected")
        print(f"Report saved: {report.get('report_path')}")
        print("=" * 60 + "\n")