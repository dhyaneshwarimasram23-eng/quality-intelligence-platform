from qi.core.risk_selector import RiskSelector


def test_risk_selector_basic():
    selector = RiskSelector()

    changed_files = ["src/payment/transfer.py"]
    all_tests = [
        {"name": "test_transfer_success", "file": "tests/api/test_transfer.py", "criticality": "critical"},
        {"name": "test_login", "file": "tests/ui/test_login.py", "criticality": "high"},
        {"name": "test_profile_update", "file": "tests/ui/test_profile.py", "criticality": "low"},
    ]

    selected = selector.select_tests(changed_files, all_tests)

    assert len(selected) == 3
    assert selected[0]["name"] == "test_transfer_success"  # should have highest score
    assert selected[0]["risk_score"] > selected[2]["risk_score"]
    print("Risk selector is working correctly!")