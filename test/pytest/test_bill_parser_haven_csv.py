import chellow.bill_parser_haven_csv
import pytest
from werkzeug.exceptions import BadRequest


def test_process_line_unknown_code(mocker):
    code = "BOB"
    row = {}
    headers = {}

    with pytest.raises(BadRequest, match=code):
        chellow.bill_parser_haven_csv._process_line(code, row, headers)


def test_process_line_SUMMARY(mocker):
    code = "SUMMARY"
    row = {}
    headers = {}

    chellow.bill_parser_haven_csv._process_line(code, row, headers)
