import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
Full Flow Demo – Quality Intelligence Platform
Shows Risk Selection → Execution simulation → Flaky detection → Evidence → Quality Gate → Self-healing
"""

from qi.core.risk_selector import RiskSelector
from qi.core.flaky_detector import FlakyDetector
from qi.core.evidence_collector import EvidenceCollector
from qi.core.quality_gate import QualityGate
from qi.core.self_healing import SelfHealing


def main():
    print("\n" + "="*70)
    print("  QUALITY INTELLIGENCE PLATFORM – FULL FLOW DEMO")
    print("="*70)

    # 1. Risk-based Test Selection
    print("\n[1] RISK-BASED TEST SELECTION")
    selector = RiskSelector()
    changed_files = ["src/payment/transfer.py", "src/auth/login.py"]
    all_tests = [
        {"name": "test_transfer_success", "file": "tests/api/test_transfer.py", "criticality": "critical"},
        {"name": "test_transfer_limit", "file": "tests/api/test_transfer.py", "criticality": "critical"},
        {"name": "test_login", "file": "tests/ui/test_login.py", "criticality": "high"},
        {"name": "test_profile", "file": "tests/ui/test_profile.py", "criticality": "low"},
        {"name": "test_dashboard", "file": "tests/ui/test_dashboard.py", "criticality": "medium"},
    ]
    selected = selector.select_tests(changed_files, all_tests)
    print(f"Changed files: {changed_files}")
    print("Selected tests (ranked by risk):")
    for t in selected:
        print(f"  → {t['name']} (score: {t['risk_score']})")

    # 2. Simulate test execution results
    print("\n[2] SIMULATED TEST RESULTS")
    results = [
        {"name": "test_transfer_success", "status": "passed", "criticality": "critical", "is_flaky": False},
        {"name": "test_transfer_limit", "status": "failed", "criticality": "critical", "is_flaky": False},
        {"name": "test_login", "status": "passed", "criticality": "high", "is_flaky": False},
        {"name": "test_profile", "status": "passed", "criticality": "low", "is_flaky": True},
    ]
    for r in results:
        print(f"  {r['name']}: {r['status'].upper()}")

    # 3. Flaky Detection
    print("\n[3] FLAKY-TEST INTELLIGENCE")
    detector = FlakyDetector(threshold=0.2)
    flaky_analysis = detector.analyze_runs("test_profile", ["passed", "failed", "passed", "failed", "passed"])
    print(f"  test_profile → Flaky: {flaky_analysis['is_flaky']} (rate: {flaky_analysis['failure_rate']})")

    # 4. Failure Evidence
    print("\n[4] FAILURE EVIDENCE ENGINE")
    collector = EvidenceCollector()
    report = collector.create_report(
        test_name="test_transfer_limit",
        status="failed",
        error_message="AssertionError: Transfer limit exceeded unexpectedly",
        stack_trace="File test_transfer.py, line 67",
        api_response={"status": 400, "error": "LIMIT_EXCEEDED"},
        logs=["Transfer initiated", "Limit check failed", "Transaction rolled back"],
    )
    collector.print_summary(report)

    # 5. Quality Gate
    print("\n[5] RELEASE QUALITY GATE")
    gate = QualityGate()
    decision = gate.evaluate(results)
    print(f"  Decision: {decision['decision']}")
    print(f"  Can release: {decision['can_release']}")
    for reason in decision["reasons"]:
        print(f"  Reason: {reason}")

    # 6. Self-Healing suggestion
    print("\n[6] SELF-HEALING (with Guardrails)")
    healer = SelfHealing()
    repair = healer.suggest_locator_fix(
        original_locator="css=.transfer-submit-btn",
        error_message="Locator not found after UI change",
    )
    print(f"  Status: {repair['status']}")
    print(f"  Requires verification: {repair['requires_verification']}")
    print(f"  Warning: {repair['warning']}")

    print("\n" + "="*70)
    print("  DEMO COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()