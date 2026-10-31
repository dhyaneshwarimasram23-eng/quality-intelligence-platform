import pytest
from playwright.sync_api import sync_playwright
from qi.core.evidence_collector import EvidenceCollector

collector = EvidenceCollector()

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page", None)
        if page is not None:
            evidence = collector.capture_playwright_failure(
                page=page,
                test_name=item.nodeid,
                error_message=str(report.longrepr)[:500],
                stack_trace=str(report.longrepr),
            )
            collector.print_summary(evidence)
            report.sections.append(("Evidence Report", evidence.get("report_path", "")))
