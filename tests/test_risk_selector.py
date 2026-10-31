from qi.core.risk_selector import RiskSelector


def test_risk_selector_basic():
    selector = RiskSelector()

    changed_files = ["src/payment/transfer.py", "src/auth/login.py"]
    all_tests = [
        {"name": "test_transfer_success", "file": "tests/api/test_transfer.py", "criticality": "critical"},
        {"name": "test_transfer_limit",   "file": "tests/api/test_transfer.py", "criticality": "critical"},
        {"name": "test_login",            "file": "tests/ui/test_login.py",     "criticality": "high"},
        {"name": "test_profile",          "file": "tests/ui/test_profile.py",   "criticality": "low"},
        {"name": "test_dashboard",        "file": "tests/ui/test_dashboard.py", "criticality": "medium"},
    ]

    selected = selector.select_tests(changed_files, all_tests)

    # Should return at least the high-impact tests
    assert len(selected) >= 2

    # Highest risk test should be related to payment/transfer
    assert "transfer" in selected[0]["name"] or "transfer" in selected[0]["file"]

    # Every returned test must have a risk_score
    for test in selected:
        assert "risk_score" in test
        assert test["risk_score"] >= 0.15