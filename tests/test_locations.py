from discovery.locations import normalize_location


def test_city_aliases():
    assert normalize_location("Pune, Maharashtra, India") == "Pune"
    assert normalize_location("Secunderabad, Telangana") == "Hyderabad"
    assert normalize_location("Bangalore, India") == "Bengaluru"
    assert normalize_location("Bangalore Urban") == "Bengaluru"
    assert normalize_location("Whitefield, Bangalore") == "Bengaluru"
    assert normalize_location("Hinjewadi Phase 2") == "Pune"
    assert normalize_location("Hinjawadi, Pune") == "Pune"
    assert normalize_location("Kharadi, Pune") == "Pune"
    assert normalize_location("Gachibowli, Hyderabad") == "Hyderabad"
    assert normalize_location("Hitec City") == "Hyderabad"
    assert normalize_location("Hitech City, Hyderabad") == "Hyderabad"
    assert normalize_location("Gurugram, Haryana") == "Delhi NCR"
    assert normalize_location("Gurgaon") == "Delhi NCR"
    assert normalize_location("Noida") == "Delhi NCR"
    assert normalize_location("Navi Mumbai") == "Mumbai"
    assert normalize_location("Andheri East") == "Mumbai"
    assert normalize_location("Powai, Mumbai") == "Mumbai"
    assert normalize_location("BKC, Mumbai") == "Mumbai"


def test_remote_and_unparsed():
    assert normalize_location("Remote - India") == "India - Remote/Other"
    assert normalize_location("India") == "India - Remote/Other"
    assert normalize_location("Remote") == "Unparsed"
    assert normalize_location("Mars") == "Unparsed"
    assert normalize_location("Somewhere") == "Unparsed"
    assert normalize_location(None) == "Unparsed"
    assert normalize_location("") == "Unparsed"


def test_outside_india_is_separated_from_unparsed():
    assert normalize_location("London, United Kingdom") == "Outside India"
    assert normalize_location("New York, USA") == "Outside India"
    assert normalize_location("Toronto, Canada") == "Outside India"
    assert normalize_location("Remote - Singapore") == "Outside India"
    assert normalize_location("Remote, London") == "Outside India"


def test_indian_city_wins_over_remote_or_country_metadata():
    assert normalize_location("Remote, Mumbai, India") == "Mumbai"
    assert normalize_location("Remote - Hinjawadi, Pune") == "Pune"
