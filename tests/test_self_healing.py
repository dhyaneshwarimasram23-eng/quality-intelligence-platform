from qi.core.self_healing import SelfHealing


def test_self_healing_suggests_but_does_not_auto_apply():
    healer = SelfHealing()

    repair = healer.suggest_locator_fix(
        original_locator="css=.submit-btn",
        error_message="Locator not found",
    )

    assert repair["status"] == "SUGGESTED"
    assert repair["requires_verification"] is True
    assert len(repair["suggestions"]) > 0
    assert "Do NOT accept" in repair["warning"]
    print("Self-healing correctly suggested repair with guardrails!")


def test_self_healing_requires_verification():
    healer = SelfHealing()

    repair = healer.suggest_locator_fix(
        original_locator="data-testid=login-button",
        error_message="Element not found",
    )

    # Verification step
    result = healer.verify_repair(0, verified=True, notes="Confirmed UI changed intentionally")
    assert result["status"] == "VERIFIED_AND_ACCEPTED"
    print("Self-healing correctly required verification before accepting!")