from discovery.roles import classify_role


def test_software_engineering_is_tech():
    assert classify_role("Senior Software Engineer") == ("Software Engineering", True)


def test_data_ml_ai_is_tech():
    assert classify_role("Machine Learning Engineer") == ("Data/ML/AI", True)


def test_non_tech_precedence():
    assert classify_role("Technical Account Manager", "Sales") == ("Non-Tech", False)


def test_product_design_is_tech_adjacent():
    assert classify_role("Product Designer") == ("Product/Design (tech-adjacent)", True)


def test_unknown_is_nullable():
    assert classify_role("Strategic Partnerships Specialist") == ("Unclassified", None)


def test_description_is_not_an_input():
    # The classifier has no description parameter; body text cannot affect labels.
    assert classify_role("Office Coordinator") == ("Unclassified", None)
