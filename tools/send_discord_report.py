"""Build a pytest summary and send it to Discord from CI."""

from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
KST = timezone(timedelta(hours=9))
JUNIT_REPORT_PATH = Path(
    os.getenv(
        "JUNIT_REPORT_PATH",
        REPO_ROOT / "reports" / "junit.xml",
    )
)
ALLURE_RESULTS_PATH = Path(
    os.getenv(
        "ALLURE_RESULTS_DIR",
        REPO_ROOT / "reports" / "allure-results",
    )
)


def _first_env(*names: str, default: str = "-") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def parse_junit(path: Path) -> dict[str, object]:
    """Count pytest outcomes, keeping xfail separate from ordinary skips."""
    if not path.exists():
        return {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "skipped": 0,
            "xfailed": 0,
            "duration": 0.0,
            "failed_cases": [f"JUnit report not found: {path}"],
            "xfailed_cases": [],
        }

    root = ET.parse(path).getroot()
    test_cases = list(root.iter("testcase"))
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))

    result: dict[str, object] = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "duration": sum(float(suite.attrib.get("time", 0)) for suite in suites),
        "failed_cases": [],
        "xfailed_cases": [],
    }

    for case in test_cases:
        class_name = case.attrib.get("classname", "")
        test_name = case.attrib.get("name", "unknown")
        case_name = f"{class_name}.{test_name}" if class_name else test_name

        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")

        if failure is not None:
            result["failed"] += 1
            result["failed_cases"].append(case_name)
        elif error is not None:
            result["errors"] += 1
            result["failed_cases"].append(case_name)
        elif skipped is not None:
            skip_text = " ".join(
                [
                    skipped.attrib.get("type", ""),
                    skipped.attrib.get("message", ""),
                    skipped.text or "",
                ]
            ).lower()
            if "xfail" in skip_text:
                result["xfailed"] += 1
                result["xfailed_cases"].append(case_name)
            else:
                result["skipped"] += 1
        else:
            result["passed"] += 1

    return result


def _strip_parameters(case_name: str) -> str:
    return case_name.split("[", 1)[0]


def parse_allure_titles(path: Path) -> dict[str, str]:
    """Map JUnit case names to the human-readable Allure titles."""
    titles: dict[str, str] = {}
    if not path.is_dir():
        return titles

    for result_path in path.glob("*-result.json"):
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        full_name = str(result.get("fullName") or "")
        title = str(result.get("name") or "")
        if not full_name or not title:
            continue

        case_name = full_name.replace("#", ".")
        titles[case_name] = title
        titles[_strip_parameters(case_name)] = title

    return titles


def apply_allure_titles(result: dict[str, object], path: Path) -> None:
    """Replace technical pytest node names with Allure titles when available."""
    titles = parse_allure_titles(path)
    if not titles:
        return

    for key in ("failed_cases", "xfailed_cases"):
        cases = result[key]
        result[key] = [
            titles.get(case, titles.get(_strip_parameters(case), case))
            for case in cases
        ]


def _allure_report_url() -> str:
    explicit_url = os.getenv("ALLURE_REPORT_URL")
    if explicit_url:
        return explicit_url

    build_url = os.getenv("BUILD_URL")
    if build_url:
        return f"{build_url.rstrip('/')}/allure/"

    pages_url = os.getenv("CI_PAGES_URL")
    if pages_url:
        return f"{pages_url.rstrip('/')}/"

    project_url = _first_env("CI_PROJECT_URL")
    ref_name = _first_env("CI_COMMIT_REF_NAME")
    if project_url != "-" and ref_name != "-":
        return (
            f"{project_url}/-/jobs/artifacts/{ref_name}/browse/public"
            "?job=pages"
        )

    return _first_env("REPORT_PIPELINE_URL", "CI_PIPELINE_URL", "BUILD_URL")


def _append_cases(lines: list[str], title: str, cases: list[str]) -> None:
    if not cases:
        return
    lines.extend(["", f"### {title}"])
    lines.extend(f"- {case}" for case in cases[:5])
    if len(cases) > 5:
        lines.append(f"- 외 {len(cases) - 5}건")


def build_message(result: dict[str, object]) -> str:
    """Create a Discord message that stays below the 2,000 character limit."""
    failed_count = int(result["failed"]) + int(result["errors"])
    status = "성공" if failed_count == 0 else "실패"
    branch = _first_env(
        "REPORT_BRANCH",
        "CI_COMMIT_BRANCH",
        "gitlabSourceBranch",
        "BRANCH_NAME",
        "GIT_BRANCH",
        "CI_COMMIT_REF_NAME",
    )
    duration = float(result["duration"])
    tester = _first_env(
        "REPORT_TESTER",
        "GITLAB_USER_NAME",
        "gitlabUserName",
        "BUILD_USER",
        default="Jenkins",
    )
    trigger = _first_env(
        "REPORT_TRIGGER",
        "CI_PIPELINE_SOURCE",
        "gitlabActionType",
        default="Jenkins",
    )
    commit_sha = _first_env(
        "REPORT_COMMIT_SHA",
        "CI_COMMIT_SHORT_SHA",
        "GIT_COMMIT",
    )
    commit_title = _first_env("REPORT_COMMIT_TITLE", "CI_COMMIT_TITLE")
    commit_author = _first_env("REPORT_COMMIT_AUTHOR", "GIT_AUTHOR_NAME")
    project_name = _first_env("PROJECT_NAME", default="QA API Automation")
    pipeline_url = _first_env(
        "REPORT_PIPELINE_URL",
        "CI_PIPELINE_URL",
        "BUILD_URL",
    )

    lines = [
        f"## {project_name} - {branch} 테스트 {status}",
        "",
        f"- 실행 시각: {datetime.now(KST).strftime('%Y-%m-%d %H:%M')}",
        f"- 실행 사용자: {tester}",
        f"- 대상 브랜치: {branch}",
        f"- 실행 트리거: {trigger}",
        f"- 커밋 작성자: {commit_author}",
        f"- 커밋: {commit_sha} {commit_title}",
        "",
        "### 테스트 결과",
        f"- 성공: {result['passed']}",
        f"- 실패: {failed_count}",
        f"- 스킵: {result['skipped']}",
        f"- XFail: {result['xfailed']}",
        f"- 합계: {result['total']}",
        f"- 소요 시간: {duration:.2f}초",
        "",
        "### 리포트",
        f"- Allure Report: {_allure_report_url()}",
        f"- Build Details: {pipeline_url}",
    ]

    _append_cases(lines, "실패 테스트", result["failed_cases"])
    _append_cases(lines, "XFail 테스트", result["xfailed_cases"])

    message = "\n".join(lines)
    if len(message) > 2000:
        message = f"{message[:1900]}\n...\n{pipeline_url}"
    return message


def send_discord_message(
    message: str,
    webhook_url: str | None = None,
) -> bool:
    """Send a Jenkins report without depending on the shared local notifier."""
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        print("DISCORD_WEBHOOK_URL is not configured", file=sys.stderr)
        return False

    try:
        response = requests.post(
            url,
            json={"content": message},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Discord notification failed: {exc}", file=sys.stderr)
        return False

    return True


def main() -> int:
    result = parse_junit(JUNIT_REPORT_PATH)
    apply_allure_titles(result, ALLURE_RESULTS_PATH)
    message = build_message(result)
    print(message)
    return 0 if send_discord_message(message) else 1


if __name__ == "__main__":
    raise SystemExit(main())
