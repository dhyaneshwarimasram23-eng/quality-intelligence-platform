from qi.core.flaky_detector import FlakyDetector


def test_flaky_detection():
    detector = FlakyDetector(threshold=0.2)

    # Simulate a flaky test (fails sometimes)
    results = ["passed", "failed", "passed", "failed", "passed"]
    analysis = detector.analyze_runs("test_payment_flow", results)

    assert analysis["is_flaky"] is True
    assert analysis["failure_rate"] == 0.4
    assert analysis["fail_count"] == 2
    print("Flaky detector correctly identified flaky test!")


def test_stable_test():
    detector = FlakyDetector(threshold=0.2)

    # Stable test – always passes
    results = ["passed", "passed", "passed", "passed", "passed"]
    analysis = detector.analyze_runs("test_login", results)

    assert analysis["is_flaky"] is False
    assert analysis["failure_rate"] == 0.0
    print("Flaky detector correctly identified stable test!")