from collector.db import connect, save_complete_snapshot


def job(job_id: str, title: str = "QA Engineer"):
    return {"job_id": job_id, "title": title, "location_raw": "Pune, India",
            "city_bucket": "Pune", "url": "https://example.invalid/job", "description_text": "Short description"}


def test_idempotent_same_timestamp(tmp_path):
    db = connect(tmp_path / "jobs.db")
    first = save_complete_snapshot(db, "lever", "acme", "Acme", [job("1")], "2026-10-12T00:00:00+00:00")
    second = save_complete_snapshot(db, "lever", "acme", "Acme", [job("1")], "2026-10-12T00:00:00+00:00")
    assert first["new"] == 1
    assert second["new"] == 0
    assert db.execute("select count(*) from observations").fetchone()[0] == 1


def test_vanish_only_on_complete_snapshot_call(tmp_path):
    db = connect(tmp_path / "jobs.db")
    save_complete_snapshot(db, "lever", "acme", "Acme", [job("1"), job("2")], "2026-10-12T00:00:00+00:00")
    summary = save_complete_snapshot(db, "lever", "acme", "Acme", [job("1")], "2026-10-13T00:00:00+00:00")
    assert summary["vanished"] == 1
    assert db.execute("select is_active from jobs where job_id='2'").fetchone()[0] == 0


def test_zero_job_complete_snapshot_marks_absent(tmp_path):
    db = connect(tmp_path / "jobs.db")
    save_complete_snapshot(db, "lever", "acme", "Acme", [job("1")], "2026-10-12T00:00:00+00:00")
    summary = save_complete_snapshot(db, "lever", "acme", "Acme", [], "2026-10-13T00:00:00+00:00")
    assert summary["vanished"] == 1


def test_non_tech_and_unclassified_are_retained_and_descriptions_do_not_label(tmp_path):
    db = connect(tmp_path / "jobs.db")
    rows = [
        {"job_id": "sales", "title": "Sales Executive", "location_raw": "Pune, India",
         "city_bucket": "Pune", "url": "", "description_text": "software engineer"},
        {"job_id": "unknown", "title": "Office Coordinator", "location_raw": "Pune, India",
         "city_bucket": "Pune", "url": "", "description_text": "QA Engineer"},
    ]
    save_complete_snapshot(db, "lever", "acme", "Acme", rows, "2026-10-12T00:00:00+00:00")
    stored = {r["job_id"]: r for r in db.execute("SELECT job_id,role_category,is_tech FROM jobs")}
    assert stored["sales"]["role_category"] == "Non-Tech"
    assert stored["sales"]["is_tech"] == 0
    assert stored["unknown"]["role_category"] == "Unclassified"
    assert stored["unknown"]["is_tech"] is None
    assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2
