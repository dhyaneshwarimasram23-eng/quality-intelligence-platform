"""
Release Quality Gate
Decides whether a release should proceed based on test results and risk thresholds.
"""

from typing import List, Dict


class QualityGate:
    def __init__(
        self,
        max_critical_failures: int = 0,
        max_failure_rate: float = 0.05,
        max_flaky_rate: float = 0.15,
        min_pass_rate: float = 0.95,
    ):
        self.max_critical_failures = max_critical_failures
        self.max_failure_rate = max_failure_rate
        self.max_flaky_rate = max_flaky_rate
        self.min_pass_rate = min_pass_rate

    def evaluate(self, test_results: List[Dict]) -> Dict:
        """
        Evaluate test results and decide if the release can proceed.
        """
        total = len(test_results)
        if total == 0:
            return {
                "decision": "BLOCKED",
                "reason": "No tests were executed",
                "can_release": False,
            }

        passed = sum(1 for t in test_results if t.get("status") == "passed")
        failed = sum(1 for t in test_results if t.get("status") == "failed")
        flaky = sum(1 for t in test_results if t.get("is_flaky") is True)
        critical_failures = sum(
            1 for t in test_results
            if t.get("status") == "failed" and t.get("criticality") == "critical"
        )

        pass_rate = passed / total
        failure_rate = failed / total
        flaky_rate = flaky / total

        reasons = []
        can_release = True

        if critical_failures > self.max_critical_failures:
            can_release = False
            reasons.append(f"Critical failures: {critical_failures} (max allowed: {self.max_critical_failures})")

        if failure_rate > self.max_failure_rate:
            can_release = False
            reasons.append(f"Failure rate {failure_rate:.1%} exceeds limit {self.max_failure_rate:.1%}")

        if flaky_rate > self.max_flaky_rate:
            can_release = False
            reasons.append(f"Flaky rate {flaky_rate:.1%} exceeds limit {self.max_flaky_rate:.1%}")

        if pass_rate < self.min_pass_rate:
            can_release = False
            reasons.append(f"Pass rate {pass_rate:.1%} is below minimum {self.min_pass_rate:.1%}")

        decision = "ALLOWED" if can_release else "BLOCKED"

        return {
            "decision": decision,
            "can_release": can_release,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "flaky": flaky,
            "critical_failures": critical_failures,
            "pass_rate": round(pass_rate, 3),
            "failure_rate": round(failure_rate, 3),
            "flaky_rate": round(flaky_rate, 3),
            "reasons": reasons if reasons else ["All quality thresholds met"],
        }