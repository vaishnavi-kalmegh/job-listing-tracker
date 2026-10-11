from collector.client import CollectorClient, normalize_job
from discovery.discover import ProbeError


def test_normalize_greenhouse_metadata_and_unclassified_location():
    item = normalize_job("greenhouse", {
        "id": 42, "title": "QA Engineer", "absolute_url": "https://example.invalid/1",
        "location": {"name": "Remote - India"}, "departments": [{"name": "Engineering"}],
        "content": "<p>not classifier input</p>",
    })
    assert item["job_id"] == "42"
    assert item["department"] == "Engineering"
    assert item["city_bucket"] == "India - Remote/Other"


def test_normalize_lever_department_and_team():
    item = normalize_job("lever", {
        "id": "abc", "text": "Data Analyst",
        "categories": {"location": "Pune, India", "department": "Data", "team": "Analytics"},
    })
    assert item["department"] == "Data"
    assert item["team"] == "Analytics"
    assert item["city_bucket"] == "Pune"


def test_robots_disallow_blocks_api_request(monkeypatch):
    client = CollectorClient()
    def fake_request(url):
        class Response:
            status_code = 200
            ok = True
            text = "User-agent: *\nDisallow: /v1/boards/"
        return Response()
    monkeypatch.setattr(client, "_request", fake_request)
    try:
        client.get_json("https://boards-api.greenhouse.io/v1/boards/example/jobs")
    except ProbeError as exc:
        assert "robots_disallow" in str(exc)
    else:
        raise AssertionError("robots disallow must block the API request")
