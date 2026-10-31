"""
Controlled Experiment: Full Regression vs Risk-based Selection
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
    },
    {
        "commit": "e4f5g6h",
        "changed_files": ["src/auth/login.py"],
        "known_failing_tests": ["test_login"],
        "description": "Login validation change",
    },
    {
        "commit": "i7j8k9l",
        "changed_files": ["src/ui/dashboard.js", "src/api/user.py"],
        "known_failing_tests": ["test_dashboard", "test_profile"],
        "description": "Dashboard + profile regression",
    },
]

ALL_TESTS = [
    {"name": "test_transfer_success", "file": "tests/api/test_transfer.py", "criticality": "critical"},
    {"name": "test_transfer_limit",   "file": "tests/api/test_transfer.py", "criticality": "critical"},
    {"name": "test_login",            "file": "tests/ui/test_login.py",     "criticality": "high"},
    {"name": "test_profile",          "file": "tests/ui/test_profile.py",   "criticality": "medium"},
    {"name": "test_dashboard",        "file": "tests/ui/test_dashboard.py", "criticality": "medium"},
    {"name": "test_health",           "file": "tests/api/test_health.py",   "criticality": "low"},
    {"name": "test_settings",         "file": "tests/ui/test_settings.py",  "criticality": "low"},
]

HISTORICAL_FAILURES = {
    "test_transfer_limit": 0.35,
    "test_profile": 0.22,
    "test_login": 0.10,
}


def simulate_execution(selected_tests, known_failing):
    start = time.perf_counter()
    time.sleep(0.01 * len(selected_tests))
    duration = time.perf_counter() - start

    selected_names = {t["name"] for t in selected_tests}
    caught = [t for t in known_failing if t in selected_names]
    missed = [t for t in known_failing if t not in selected_names]

    return {
        "tests_run": len(selected_tests),
        "duration_sec": round(duration, 4),
        "caught": caught,
        "missed": missed,
        "detection_rate": len(caught) / len(known_failing) if known_failing else 1.0,
    }


def run_experiment():
    selector = RiskSelector()
    results = []

    print("\n" + "=" * 70)
    print("  CONTROLLED EXPERIMENT: Full vs Risk-based Selection")
    print("=" * 70)

    for scenario in HISTORICAL_SCENARIOS:
        print(f"\nScenario: {scenario['description']} ({scenario['commit']})")
        print(f"Changed files: {scenario['changed_files']}")

        full_result = simulate_execution(ALL_TESTS, scenario["known_failing_tests"])
        risk_selected = selector.select_tests(
            changed_files=scenario["changed_files"],
            all_tests=ALL_TESTS,
            historical_failures=HISTORICAL_FAILURES,
            min_score=0.15,
        )
        risk_result = simulate_execution(risk_selected, scenario["known_failing_tests"])

        print(f"  Full   → tests={full_result['tests_run']:2d}  duration={full_result['duration_sec']:.3f}s  detected={full_result['detection_rate']:.0%}")
        print(f"  Risk   → tests={risk_result['tests_run']:2d}  duration={risk_result['duration_sec']:.3f}s  detected={risk_result['detection_rate']:.0%}  missed={risk_result['missed']}")

        results.append({
            "scenario": scenario["description"],
            "commit": scenario["commit"],
            "full": full_result,
            "risk": risk_result,
            "runtime_ratio": round(risk_result["duration_sec"] / full_result["duration_sec"], 3) if full_result["duration_sec"] > 0 else 0,
            "test_reduction": round(1 - (risk_result["tests_run"] / full_result["tests_run"]), 3),
        })

    print("\n" + "-" * 70)
    print("SUMMARY")
    avg_reduction = sum(r["test_reduction"] for r in results) / len(results)
    avg_detection = sum(r["risk"]["detection_rate"] for r in results) / len(results)
    print(f"Average test reduction     : {avg_reduction:.1%}")
    print(f"Average failure detection  : {avg_detection:.1%}")
    print(f"Missed failures across all : {sum(len(r['risk']['missed']) for r in results)}")

    out_dir = Path("experiments/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"experiment_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nRaw results saved to: {out_file}")
    print("=" * 70 + "\n")
    return results


if __name__ == "__main__":
    run_experiment()