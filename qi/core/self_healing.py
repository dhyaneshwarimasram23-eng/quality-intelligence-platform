"""
Self-Healing with Guardrails
Suggests locator repairs when UI changes, but requires verification.
Never silently converts a real product defect into a passing test.
"""

from typing import List, Dict, Optional


class SelfHealing:
    def __init__(self):
        self.suggested_repairs = []

    def suggest_locator_fix(
        self,
        original_locator: str,
        error_message: str,
        page_content: Optional[str] = None,
    ) -> Dict:
        """
        Suggest alternative locators when a locator fails.
        This is only a suggestion – never auto-applied.
        """
        suggestions = []

        # Simple rule-based suggestions
        if "data-testid" in original_locator:
            suggestions.append({
                "type": "role",
                "value": "button",
                "reason": "Try role-based locator as fallback"
            })
            suggestions.append({
                "type": "text",
                "value": "Submit",
                "reason": "Try text content locator"
            })
        elif "css=" in original_locator or original_locator.startswith("."):
            suggestions.append({
                "type": "data-testid",
                "value": "suggested-testid",
                "reason": "Prefer data-testid over CSS selectors"
            })

        # Always add a generic suggestion
        suggestions.append({
            "type": "xpath",
            "value": "//*[contains(text(),'...')]",
            "reason": "XPath as last resort – review carefully"
        })

        repair = {
            "original_locator": original_locator,
            "error": error_message,
            "suggestions": suggestions,
            "status": "SUGGESTED",  # never "APPLIED" automatically
            "requires_verification": True,
            "warning": "Do NOT accept this repair without verifying the test still catches real defects."
        }

        self.suggested_repairs.append(repair)
        return repair

    def verify_repair(self, repair_id: int, verified: bool, notes: str = "") -> Dict:
        """
        Human (or verification suite) must explicitly accept or reject a suggestion.
        """
        if repair_id >= len(self.suggested_repairs):
            return {"error": "Invalid repair ID"}

        repair = self.suggested_repairs[repair_id]
        if verified:
            repair["status"] = "VERIFIED_AND_ACCEPTED"
            repair["verification_notes"] = notes
        else:
            repair["status"] = "REJECTED"
            repair["verification_notes"] = notes or "Rejected – possible real product defect"

        return repair