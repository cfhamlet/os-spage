
from os_spage.validator import check_error_reason, simple_check_url


def test_check_error_reason():
    valid_data = ['HTTP 404', 'RULE 16', 'DNS -2', 'SERVER 110', 'SSL -2']
    for data in valid_data:
        assert check_error_reason(data) == True

    invalid_data = ['HTTP404', 'RULE  16', 'RULE TEST']
    for data in invalid_data:
        assert check_error_reason(data) == False


def test_simple_check_url():
    valid_data = [
        "http://www.google.com/",
        "https://www.google.com/",
    ]
    for data in valid_data:
        assert simple_check_url(data) == True

    invalid_data = [
        "htp://www.google.com/",
        "https/www.google.com/",
    ]
    for data in invalid_data:
        assert simple_check_url(data) == False