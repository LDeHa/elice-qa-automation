"""Jenkins 결과 요약과 웹훅 알림의 단위 테스트."""

from __future__ import annotations

import requests

from tools import send_discord_report


def test_parse_junit_separates_xfail_from_skip(tmp_path):
    report_path = tmp_path / "junit.xml"
    report_path.write_text(
        """<?xml version="1.0" encoding="utf-8"?>
<testsuite tests="4" time="1.25">
  <testcase classname="tests.test_sample" name="test_pass" />
  <testcase classname="tests.test_sample" name="test_fail"><failure /></testcase>
  <testcase classname="tests.test_sample" name="test_skip"><skipped message="skip" /></testcase>
  <testcase classname="tests.test_sample" name="test_xfail"><skipped type="pytest.xfail" /></testcase>
</testsuite>
""",
        encoding="utf-8",
    )

    result = send_discord_report.parse_junit(report_path)

    assert result["total"] == 4
    assert result["passed"] == 1
    assert result["failed"] == 1
    assert result["skipped"] == 1
    assert result["xfailed"] == 1
    assert result["duration"] == 1.25


def test_build_message_uses_jenkins_metadata(monkeypatch):
    monkeypatch.setenv("REPORT_BRANCH", "develop")
    monkeypatch.setenv("REPORT_TRIGGER", "PUSH")
    monkeypatch.setenv("REPORT_COMMIT_SHA", "abc1234")
    monkeypatch.setenv("REPORT_PIPELINE_URL", "https://jenkins.example.invalid/job/1/")
    monkeypatch.setenv("PROJECT_NAME", "Portfolio QA")
    result = {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "duration": 0.5,
        "failed_cases": [],
        "xfailed_cases": [],
    }

    message = send_discord_report.build_message(result)

    assert "develop 테스트 성공" in message
    assert "실행 트리거: PUSH" in message
    assert "abc1234" in message
    assert len(message) <= 2000


def test_send_discord_message_posts_content_payload(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr(requests, "post", fake_post)

    assert send_discord_report.send_discord_message(
        "테스트",
        webhook_url="https://example.invalid/hook",
    ) is True
    assert captured["url"] == "https://example.invalid/hook"
    assert captured["json"] == {"content": "테스트"}
    assert captured["timeout"] == 10


def test_send_discord_message_handles_request_failure(monkeypatch):
    def fake_post(url, json, timeout):
        raise requests.HTTPError("403 Client Error")

    monkeypatch.setattr(requests, "post", fake_post)

    assert send_discord_report.send_discord_message(
        "테스트",
        webhook_url="https://example.invalid/hook",
    ) is False
