"""Sanitized API Object sample from the class-home test suite."""


class HomeAPI:
    """Keep HTTP details outside test cases so scenarios describe intent."""

    def __init__(self, classroom_client):
        self.classroom = classroom_client

    @staticmethod
    def _org_headers(org_name: str) -> dict[str, str]:
        return {"X-Organization": org_name}

    def get_classroom(self, classroom_id: str, org_name: str | None = None):
        headers = self._org_headers(org_name) if org_name else None
        return self.classroom.get(
            f"/classroom/{classroom_id}",
            headers=headers,
        )

    def get_classroom_without_org_header(self, classroom_id: str):
        return self.classroom.get(f"/classroom/{classroom_id}")

    def patch_classroom(
        self,
        classroom_id: str,
        payload: dict,
        org_name: str,
    ):
        return self.classroom.patch(
            f"/classroom/{classroom_id}",
            json=payload,
            headers=self._org_headers(org_name),
        )

    def get_schedule_list(
        self,
        classroom_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        count: int | str | None = None,
        org_name: str | None = None,
    ):
        params = {
            key: value
            for key, value in {
                "classroom_id": classroom_id,
                "start_date": start_date,
                "end_date": end_date,
                "count": count,
            }.items()
            if value is not None
        }
        headers = self._org_headers(org_name) if org_name else None
        return self.classroom.get("/schedule", params=params, headers=headers)
