from qi.core.quality_gate import QualityGate


def test_quality_gate_allows_good_run():
    gate = QualityGate()

    results = [
        {"status": "passed", "criticality": "critical", "is_flaky": False},
        {"status": "passed", "criticality": "high", "is_flaky": False},
        {"status": "passed", "criticality": "medium", "is_flaky": False},
    ]

    decision = gate.evaluate(results)
    assert decision["can_release"] is True
    assert decision["decision"] == "ALLOWED"
    print("Quality Gate correctly ALLOWED a clean run!")


def test_quality_gate_blocks_critical_failure():
    gate = QualityGate()

    results = [
        {"status": "failed", "criticality": "critical", "is_flaky": False},
        {"status": "passed", "criticality": "high", "is_flaky": False},
    ]

    decision = gate.evaluate(results)
    assert decision["can_release"] is False
    assert decision["decision"] == "BLOCKED"
    assert "Critical failures" in decision["reasons"][0]
    print("Quality Gate correctly BLOCKED a critical failure!")