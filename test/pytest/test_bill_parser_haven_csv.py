import chellow.bill_parser_haven_csv
import pytest
from werkzeug.exceptions import BadRequest
from chellow.utils import to_utc, ct_datetime


def test_process_line_unknown_code(mocker):
    code = "BOB"
    row = {}
    headers = {}

    with pytest.raises(BadRequest, match=code):
        chellow.bill_parser_haven_csv._process_line(code, row, headers)


def test_process_line_SUMMARY():
    code = "SUMMARY"
    row = {}
    headers = {}

    chellow.bill_parser_haven_csv._process_line(code, row, headers)


def test_to_date():
    date_str = "20200430"
    dt = chellow.bill_parser_haven_csv._to_date(date_str)
    assert dt == to_utc(ct_datetime(2020, 4, 30))
