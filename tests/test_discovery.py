from discovery.discover import entry_level, extract_jobs, token_evidence_ok


def test_entry_level_heuristic_excludes_senior_title():
    assert entry_level("Graduate Software Engineer", "Build software")
    assert not entry_level("Senior Graduate Program Manager", "Graduate program")


def test_greenhouse_schema_and_zero_jobs():
    jobs, complete, status = extract_jobs("greenhouse", {"jobs": []})
    assert jobs == []
    assert complete
    assert status == "ok"


def test_invalid_schema_not_empty_success():
    jobs, complete, status = extract_jobs("greenhouse", {"data": []})
    assert jobs == []
    assert not complete
    assert status.startswith("schema_error")


def test_lever_schema():
    jobs, complete, status = extract_jobs("lever", [])
    assert jobs == [] and complete and status == "ok"
    jobs, complete, status = extract_jobs("lever", {"postings": []})
    assert not complete and status.startswith("schema_error")


def test_token_must_be_evidenced_by_matching_public_board_url():
    assert token_evidence_ok("greenhouse", "acme", "https://boards.greenhouse.io/acme")
    assert token_evidence_ok("lever", "acme", "https://jobs.lever.co/acme")
    assert not token_evidence_ok("greenhouse", "acme", "https://example.com/acme")
    assert not token_evidence_ok("lever", "guessed", "https://jobs.lever.co/acme")
