"""
Controlled Experiment: Full Regression vs Risk-based Selection
More realistic version with clearer metrics for interviews.
"""

import time
import json
from pathlib import Path
from datetime import datetime, timezone
from qi.core.risk_selector import RiskSelector


HISTORICAL_SCENARIOS = [
    {
        "commit": "a1b2c3d",
        "changed_files": ["src/payment/transfer.py", "src/payment/limits.py"],
        "known_failing_tests": ["test_transfer_limit", "test_transfer_success"],
        "description": "Payment limit bug",
        "full_suite_size": 42,          # simulated real suite size
    },
    {
        "commit": "e4f5g6h",
        "changed_files": ["src/auth/login.py", "src/auth/session.py"],
        "known_failing_tests": ["test_login", "test_session_timeout"],
        "description": "Login + session validation change",
        "full_suite_size": 42,
    },
    {
        "commit": "i7j8k9l",
        "changed_files": ["src/ui/dashboard.js", "src/api/user.py"],
        "known_failing_tests": ["test_dashboard", "test_profile"],
        "description": "Dashboard + profile regression",
        "full_suite_size": 42,
    },
    {
        "commit": "m1n2o3p",
        "changed_files": ["src/payment/refund.py"],
        "known_failing_tests": ["test_refund_flow"],
        "description": "Refund flow change",
        "full_suite_size": 42,
    },
]

# Expanded test catalog (simulates a real medium-sized suite)
ALL_TESTS = [
    {"name": "test_transfer_success", "file": "tests/api/test_transfer.py", "criticality": "critical"},
    {"name": "test_transfer_limit",   "file": "tests/api/test_transfer.py", "criticality": "critical"},
    {"name": "test_refund_flow",      "file": "tests/api/test_refund.py",   "criticality": "critical"},
    {"name": "test_login",            "file": "tests/ui/test_login.py",     "criticality": "high"},
    {"name": "test_session_timeout",  "file": "tests/ui/test_session.py",   "criticality": "high"},
    {"name": "test_profile",          "file": "tests/ui/test_profile.py",   "criticality": "medium"},
    {"name": "test_dashboard",        "file": "tests/ui/test_dashboard.py", "criticality": "medium"},
    {"name": "test_health",           "file": "tests/api/test_health.py",   "criticality": "low"},
    {"name": "test_settings",         "file": "tests/ui/test_settings.py",  "criticality": "low"},
    {"name": "test_notifications",    "file": "tests/ui/test_notifications.py", "criticality": "low"},
]

HISTORICAL_FAILURES = {
    "test_transfer_limit": 0.35,
    "test_profile": 0.22,
    "test_login": 0.10,
    "test_refund_flow": 0.18,
    "test_session_timeout": 0.15,
}


def simulate_execution(selected_tests, known_failing, full_suite_size=None):
    """Simulate execution time proportional to number of tests."""
    num_tests = len(selected_tests)
    # Simulate ~1.8 seconds per test on average (realistic for UI+API mix)
    duration = round(num_tests * 1.8, 2)

    selected_names = {t["name"] for t in selected_tests}
    caught = [t for t in known_failing if t in selected_names]
    missed = [t for t in known_failing if t not in selected_names]

    return {
        "tests_run": num_tests,
        "duration_sec": duration,
        "caught": caught,
        "missed": missed,
        "detection_rate": len(caught) / len(known_failing) if known_failing else 1.0,
    }


def run_experiment():
    selector = RiskSelector()
    results = []

    print("\n" + "=" * 72)
    print("  CONTROLLED EXPERIMENT: Full Regression vs Risk-based Selection")
    print("=" * 72)

    for scenario in HISTORICAL_SCENARIOS:
        print(f"\nScenario: {scenario['description']}")
        print(f"Commit  : {scenario['commit']}")
        print(f"Changed : {scenario['changed_files']}")

        # Full regression (use the simulated larger suite size for timing)
        full_result = simulate_execution(ALL_TESTS, scenario["known_failing_tests"])
        full_result["tests_run"] = scenario["full_suite_size"]
        full_result["duration_sec"] = round(scenario["full_suite_size"] * 1.8, 2)

        # Risk-based
        risk_selected = selector.select_tests(
            changed_files=scenario["changed_files"],
            all_tests=ALL_TESTS,
            historical_failures=HISTORICAL_FAILURES,
            min_score=0.15,
        )
        risk_result = simulate_execution(risk_selected, scenario["known_failing_tests"])

        reduction = 1 - (risk_result["tests_run"] / full_result["tests_run"])
        time_saved = full_result["duration_sec"] - risk_result["duration_sec"]

        print(f"  Full regression : {full_result['tests_run']:3d} tests  |  {full_result['duration_sec']:6.1f}s  |  detected {full_result['detection_rate']:.0%}")
        print(f"  Risk-based      : {risk_result['tests_run']:3d} tests  |  {risk_result['duration_sec']:6.1f}s  |  detected {risk_result['detection_rate']:.0%}")
        print(f"  Reduction       : {reduction:.1%} fewer tests  |  {time_saved:.1f}s saved  |  missed {risk_result['missed']}")

        results.append({
            "scenario": scenario["description"],
            "commit": scenario["commit"],
            "full": full_result,
            "risk": risk_result,
            "test_reduction": round(reduction, 3),
            "time_saved_sec": round(time_saved, 1),
        })

    # Summary
    print("\n" + "-" * 72)
    print("SUMMARY")
    avg_reduction = sum(r["test_reduction"] for r in results) / len(results)
    avg_detection = sum(r["risk"]["detection_rate"] for r in results) / len(results)
    total_time_saved = sum(r["time_saved_sec"] for r in results)
    total_missed = sum(len(r["risk"]["missed"]) for r in results)

    print(f"Average test reduction     : {avg_reduction:.1%}")
    print(f"Average failure detection  : {avg_detection:.1%}")
    print(f"Total time saved (all runs): {total_time_saved:.1f}s")
    print(f"Missed failures            : {total_missed}")

    out_dir = Path("experiments/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"experiment_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nRaw results saved to: {out_file}")
    print("=" * 72 + "\n")
    return results


if __name__ == "__main__":
    run_experiment()