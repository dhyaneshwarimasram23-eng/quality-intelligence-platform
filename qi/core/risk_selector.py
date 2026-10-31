"""
Risk-based Test Selection Engine
Selects the most relevant tests based on code changes, history, and dependencies.
"""

from typing import List, Dict, Optional, Set
from pathlib import Path
import re


class RiskSelector:
    def __init__(self):
        self.criticality_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
        }

        self.module_keywords = {
            "payments": ["payment", "transfer", "transaction", "wallet", "balance"],
            "auth": ["auth", "login", "logout", "session", "token", "password"],
            "user": ["user", "profile", "account", "settings"],
            "ui": ["ui", "page", "component", "frontend"],
            "api": ["api", "endpoint", "service", "controller"],
        }

        self.weights = {
            "change_impact": 0.45,
            "historical_failure": 0.30,
            "criticality": 0.20,
            "dependency_boost": 0.05,
        }

    def select_tests(
        self,
        changed_files: List[str],
        all_tests: List[Dict],
        historical_failures: Optional[Dict[str, float]] = None,
        top_n: Optional[int] = None,
        min_score: float = 0.15,
    ) -> List[Dict]:
        historical_failures = historical_failures or {}
        scored = []

        for test in all_tests:
            score, breakdown = self._calculate_risk_score(
                test, changed_files, historical_failures
            )
            if score >= min_score:
                scored.append({
                    **test,
                    "risk_score": round(score, 3),
                    "score_breakdown": breakdown,
                })

        scored.sort(key=lambda x: x["risk_score"], reverse=True)

        if top_n is not None:
            scored = scored[:top_n]

        return scored

    def _calculate_risk_score(
        self,
        test: Dict,
        changed_files: List[str],
        historical_failures: Dict[str, float],
    ):
        change_impact = self._change_impact(test, changed_files)
        hist = historical_failures.get(test.get("name", ""), 0.0)
        crit = self.criticality_weights.get(
            test.get("criticality", "medium").lower(), 0.5
        )
        dep_boost = 0.1 if change_impact > 0.7 else 0.0

        score = (
            self.weights["change_impact"] * change_impact
            + self.weights["historical_failure"] * hist
            + self.weights["criticality"] * crit
            + self.weights["dependency_boost"] * dep_boost
        )

        breakdown = {
            "change_impact": round(change_impact, 3),
            "historical_failure": round(hist, 3),
            "criticality": round(crit, 3),
            "dependency_boost": round(dep_boost, 3),
        }
        return score, breakdown

    def _change_impact(self, test: Dict, changed_files: List[str]) -> float:
        if not changed_files:
            return 0.0

        test_file = (test.get("file") or "").lower()
        test_name = (test.get("name") or "").lower()
        test_modules = self._extract_modules(test_file + " " + test_name)

        impact = 0.0
        for changed in changed_files:
            changed_l = changed.lower()
            changed_modules = self._extract_modules(changed_l)

            if test_file and (test_file in changed_l or changed_l in test_file):
                impact = max(impact, 1.0)
                continue

            common = test_modules & changed_modules
            if common:
                impact = max(impact, 0.7 + 0.1 * len(common))

            for mod, keywords in self.module_keywords.items():
                if any(k in changed_l for k in keywords) and mod in test_modules:
                    impact = max(impact, 0.6)

        return min(impact, 1.0)

    def _extract_modules(self, text: str) -> Set[str]:
        found = set()
        for mod, keywords in self.module_keywords.items():
            if any(k in text for k in keywords):
                found.add(mod)
        return found
