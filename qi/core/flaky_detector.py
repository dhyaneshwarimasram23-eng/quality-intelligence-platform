"""
Flaky Test Intelligence
Detects intermittent failures and tracks failure rates.
"""

from typing import List, Dict
from datetime import datetime, timezone


class FlakyDetector:
    def __init__(self, threshold: float = 0.2):
        """
        Args:
            threshold: Failure rate above which a test is considered flaky (default 20%)
        """
        self.threshold = threshold

    def analyze_runs(self, test_name: str, results: List[str]) -> Dict:
        """
        Analyze a sequence of test results.

        Args:
            test_name: Name of the test
            results: List of "passed" / "failed" strings

        Returns:
            Analysis dictionary
        """
        total = len(results)
        if total == 0:
            return {"test_name": test_name, "is_flaky": False, "failure_rate": 0.0}

        fail_count = results.count("failed")
        failure_rate = fail_count / total

        is_flaky = failure_rate >= self.threshold and fail_count > 0 and fail_count < total

        return {
            "test_name": test_name,
            "total_runs": total,
            "fail_count": fail_count,
            "failure_rate": round(failure_rate, 3),
            "is_flaky": is_flaky,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }