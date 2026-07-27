"""Representative, sanitized pytest patterns from the class-home scope.

This file is a review sample. The original fixtures and private API environment
are intentionally not included in the portfolio repository.
"""

import allure
import pytest


INVALID_CLASSROOM_CASES = [
    pytest.param("00000000-0000-0000-0000-000000000000", id="not-found"),
    pytest.param("invalid-format", id="invalid-format"),
]

SCHEDULE_PARAMETER_CASES = [
    pytest.param({"start_date": None, "end_date": None}, id="missing-dates"),
    pytest.param({"classroom_id": None}, id="missing-classroom-id"),
    pytest.param({"start_date": "abc", "end_date": "xyz"}, id="invalid-dates"),
    pytest.param({"count": "abc"}, id="invalid-count"),
]


def assert_client_error(response):
    """Accept either an HTTP 4xx or the service's documented failure envelope."""
    if response.status_code in {400, 401, 403, 404, 409, 422}:
        return
    body = response.json()
    if response.status_code == 200 and body.get("result", {}).get("status") == "fail":
        return
    pytest.fail(f"Expected client error, got HTTP {response.status_code}")


@allure.feature("class home")
class TestClassHome:
    @pytest.mark.smoke
    @pytest.mark.positive
    @allure.title("TC-HOME-001 student can read class-home information")
    def test_student_can_read_home(self, home_api, classroom_id, org_name):
        response = home_api.get_classroom(classroom_id, org_name)
        assert response.status_code == 200

    @pytest.mark.negative
    @pytest.mark.parametrize("bad_id", INVALID_CLASSROOM_CASES)
    @allure.title("TC-HOME-005/006 invalid classroom id is rejected")
    def test_invalid_classroom_id(self, home_api, org_name, bad_id):
        assert_client_error(home_api.get_classroom(bad_id, org_name))

    @pytest.mark.negative
    @allure.title("TC-HOME-007 missing organization header is rejected")
    def test_missing_organization_header(self, home_api, classroom_id):
        response = home_api.get_classroom_without_org_header(classroom_id)
        if response.status_code == 200:
            pytest.xfail("Known contract mismatch: required header was not enforced")
        assert_client_error(response)

    @pytest.mark.boundary
    @allure.title("TC-HOME-024 student cannot update classroom settings")
    def test_student_cannot_update_settings(
        self,
        home_api,
        classroom_id,
        org_name,
    ):
        response = home_api.patch_classroom(
            classroom_id,
            payload={"opened": False},
            org_name=org_name,
        )
        assert_client_error(response)

    @pytest.mark.negative
    @pytest.mark.parametrize("overrides", SCHEDULE_PARAMETER_CASES)
    @allure.title("TC-HOME-013/014/015/018 invalid schedule parameters")
    def test_invalid_schedule_parameters(
        self,
        home_api,
        valid_schedule_query,
        overrides,
    ):
        query = {**valid_schedule_query, **overrides}
        query = {key: value for key, value in query.items() if value is not None}
        assert_client_error(home_api.get_schedule_list(**query))
