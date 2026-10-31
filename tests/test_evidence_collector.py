from qi.core.evidence_collector import EvidenceCollector
import os


def test_evidence_report_creation():
    collector = EvidenceCollector(report_dir="reports")

    report = collector.create_report(
        test_name="test_transfer_limit",
        status="failed",
        error_message="AssertionError: Expected balance 1000, got 900",
        stack_trace="File test_transfer.py, line 45, in test_transfer_limit",
        api_response={"status": 200, "balance": 900},
        logs=["Starting transfer", "API called", "Balance mismatch detected"],
    )

    assert report["status"] == "failed"
    assert "report_path" in report
    assert os.path.exists(report["report_path"])
    print("Evidence report created successfully!")
    collector.print_summary(report)