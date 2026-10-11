from discovery.locations import normalize_location


def test_city_aliases():
    assert normalize_location("Pune, Maharashtra, India") == "Pune"
    assert normalize_location("Secunderabad, Telangana") == "Hyderabad"
    assert normalize_location("Bangalore, India") == "Bengaluru"
    assert normalize_location("Gurugram, Haryana") == "Delhi NCR"
    assert normalize_location("Navi Mumbai") == "Mumbai"


def test_remote_and_unclassified():
    assert normalize_location("Remote - India") == "India - Remote/Other"
    assert normalize_location("India") == "India - Remote/Other"
    assert normalize_location("Mars") == "Unclassified"
    assert normalize_location(None) == "Unclassified"


def test_city_wins_over_remote():
    assert normalize_location("Remote, Mumbai, India") == "Mumbai"
