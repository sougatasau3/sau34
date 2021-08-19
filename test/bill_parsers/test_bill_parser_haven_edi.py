from decimal import Decimal
from io import BytesIO

from werkzeug.exceptions import BadRequest

import chellow.bill_parser_haven_edi
from chellow.utils import utc_datetime


def test_process_BTL_zeroes(mocker):
    elements = {
        "UVLT": ["0"],
        "UTVA": ["0"],
        "TBTL": ["0"],
    }
    headers = {}
    chellow.bill_parser_haven_edi._process_BTL(elements, headers)
    expected_headers = {
        "net": Decimal("0.00"),
        "vat": Decimal("0.00"),
        "gross": Decimal("0.00"),
    }
    assert headers == expected_headers
    assert str(headers["net"]) == "0.00"


def test_process_BTL_non_zeroes(mocker):
    elements = {
        "UVLT": ["11"],
        "UTVA": ["12"],
        "TBTL": ["10"],
    }
    headers = {}
    chellow.bill_parser_haven_edi._process_BTL(elements, headers)
    expected_headers = {
        "net": Decimal("0.11"),
        "vat": Decimal("0.12"),
        "gross": Decimal("0.10"),
    }
    assert headers == expected_headers


def test_process_MTR_UTLHDR(mocker):
    elements = {}
    headers = {"message_type": "UTLHDR", "breakdown": {}}
    bill = chellow.bill_parser_haven_edi._process_MTR(elements, headers)
    assert bill is None


def test_process_MTR_UTLBIL(mocker):
    MockSupply = mocker.patch("chellow.bill_parser_haven_edi.Supply", autospec=True)
    mock_supply = mocker.Mock()
    MockSupply.get_by_mpan_core.return_value = mock_supply
    mock_era = mocker.Mock()
    mock_era.ssc.code = "0244"
    gbp = "10.31"
    cons = "113"
    mock_supply.find_era_at.return_value = mock_era
    elements = {}
    headers = {
        "sess": mocker.Mock(),
        "message_type": "UTLBIL",
        "breakdown": {},
        "bill_elements": [
            chellow.bill_parser_haven_edi.BillElement(
                gbp=Decimal(gbp),
                rate=Decimal("0.0001"),
                cons=Decimal(cons),
                titles=None,
                desc="Night",
            )
        ],
        "mpan_core": ["0850"],
        "kwh": 8,
        "reference": "a",
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "reads": [
            {
                "msn": "hgkh",
                "mpan": "      ",
                "coefficient": Decimal("0.00001"),
                "units": "kWh",
                "tpr_code": "Day",
                "prev_date": utc_datetime(2020, 3, 31, 22, 30),
                "prev_value": Decimal("1"),
                "prev_type_code": "N",
                "pres_date": utc_datetime(2020, 3, 1, 23, 30),
                "pres_value": Decimal("0"),
                "pres_type_code": "N",
            },
        ],
        "bill_type_code": "N",
    }
    expected_bill = {
        "kwh": 8,
        "reference": "a",
        "mpan_core": ["0850"],
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "breakdown": {
            "00206-gbp": Decimal(gbp),
            "00206-rate": {Decimal("0.0001")},
            "00206-kwh": Decimal(cons),
        },
        "reads": [
            {
                "msn": "hgkh",
                "mpan": "      ",
                "coefficient": Decimal("0.00001"),
                "units": "kWh",
                "tpr_code": "00040",
                "prev_date": utc_datetime(2020, 3, 31, 22, 30),
                "prev_value": Decimal("1"),
                "prev_type_code": "N",
                "pres_date": utc_datetime(2020, 3, 1, 23, 30),
                "pres_value": Decimal("0"),
                "pres_type_code": "N",
            }
        ],
        "bill_type_code": "N",
    }
    bill = chellow.bill_parser_haven_edi._process_MTR(elements, headers)
    assert bill == expected_bill


def test_process_MTR_UTLBIL_multiple_charges_one_tpr(mocker):
    MockSupply = mocker.patch("chellow.bill_parser_haven_edi.Supply", autospec=True)
    mock_supply = mocker.Mock()
    MockSupply.get_by_mpan_core.return_value = mock_supply
    mock_era = mocker.Mock()
    mock_era.ssc.code = "0244"
    gbp = "10.31"
    cons = "113"
    mock_supply.find_era_at.return_value = mock_era
    elements = {}
    headers = {
        "sess": mocker.Mock(),
        "message_type": "UTLBIL",
        "breakdown": {},
        "bill_elements": [
            chellow.bill_parser_haven_edi.BillElement(
                gbp=Decimal(gbp),
                rate=Decimal("0.0001"),
                cons=Decimal(cons),
                titles=None,
                desc="Night",
            ),
            chellow.bill_parser_haven_edi.BillElement(
                gbp=Decimal(gbp),
                rate=Decimal("0.0001"),
                cons=Decimal(cons),
                titles=None,
                desc="Night",
            ),
        ],
        "mpan_core": ["0850"],
        "kwh": 8,
        "reference": "a",
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "reads": [
            {
                "msn": "hgkh",
                "mpan": "      ",
                "coefficient": Decimal("0.00001"),
                "units": "kWh",
                "tpr_code": "Day",
                "prev_date": utc_datetime(2020, 3, 31, 22, 30),
                "prev_value": Decimal("1"),
                "prev_type_code": "N",
                "pres_date": utc_datetime(2020, 3, 1, 23, 30),
                "pres_value": Decimal("0"),
                "pres_type_code": "N",
            },
        ],
        "bill_type_code": "N",
    }
    expected_bill = {
        "kwh": 8,
        "reference": "a",
        "mpan_core": ["0850"],
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "breakdown": {
            "00206-gbp": Decimal(gbp) * 2,
            "00206-rate": {Decimal("0.0001")},
            "00206-kwh": Decimal(cons) * 2,
        },
        "reads": [
            {
                "msn": "hgkh",
                "mpan": "      ",
                "coefficient": Decimal("0.00001"),
                "units": "kWh",
                "tpr_code": "00040",
                "prev_date": utc_datetime(2020, 3, 31, 22, 30),
                "prev_value": Decimal("1"),
                "prev_type_code": "N",
                "pres_date": utc_datetime(2020, 3, 1, 23, 30),
                "pres_value": Decimal("0"),
                "pres_type_code": "N",
            }
        ],
        "bill_type_code": "N",
    }
    bill = chellow.bill_parser_haven_edi._process_MTR(elements, headers)
    assert bill == expected_bill


def test_process_MTR_UTLBIL_unmetered(mocker):
    MockSupply = mocker.patch("chellow.bill_parser_haven_edi.Supply", autospec=True)
    mock_supply = mocker.Mock()
    MockSupply.get_by_mpan_core.return_value = mock_supply
    mock_era = mocker.Mock()
    mock_era.ssc.code = "0428"
    mock_mr_00258 = mocker.Mock()
    mock_mr_00258.tpr.code = "00258"
    mock_mr_00259 = mocker.Mock()
    mock_mr_00259.tpr.code = "00259"
    mock_era.ssc.measurement_requirements = [mock_mr_00258, mock_mr_00259]
    gbp = "10.31"
    cons = "113"
    mock_supply.find_era_at.return_value = mock_era
    elements = {}
    headers = {
        "sess": mocker.Mock(),
        "message_type": "UTLBIL",
        "breakdown": {},
        "bill_elements": [
            chellow.bill_parser_haven_edi.BillElement(
                gbp=Decimal(gbp),
                rate=Decimal("0.0001"),
                cons=Decimal(cons),
                titles=None,
                desc="Energy Charges",
            )
        ],
        "mpan_core": ["0850"],
        "kwh": 8,
        "reference": "a",
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "reads": [],
        "bill_type_code": "N",
    }
    expected_bill = {
        "kwh": 8,
        "reference": "a",
        "mpan_core": ["0850"],
        "issue_date": "d",
        "account": "acc",
        "start_date": "d",
        "finish_date": "d",
        "net": 0,
        "vat": 0,
        "gross": 0,
        "breakdown": {
            "00258-gbp": Decimal(gbp) / 2,
            "00258-rate": {Decimal("0.0001")},
            "00258-kwh": Decimal(cons) / 2,
            "00259-gbp": Decimal(gbp) / 2,
            "00259-rate": {Decimal("0.0001")},
            "00259-kwh": Decimal(cons) / 2,
        },
        "reads": [],
        "bill_type_code": "N",
    }
    bill = chellow.bill_parser_haven_edi._process_MTR(elements, headers)
    assert bill == expected_bill


def test_process_MAN(mocker):
    elements = {
        "MADN": ["20", "0000000000", "6", "00", "001", "002"],
    }

    headers = {}
    chellow.bill_parser_haven_edi._process_MAN(elements, headers)
    expected_headers = {"mpan_core": "20 0000 0000 006"}
    assert headers == expected_headers


def test_process_MHD(mocker):
    message_type = "UTLBIL"
    elements = {"TYPE": [message_type]}

    sess = mocker.Mock()
    headers = {"sess": sess}
    chellow.bill_parser_haven_edi._process_MHD(elements, headers)
    expected_headers = {
        "message_type": message_type,
        "reads": [],
        "bill_elements": [],
        "breakdown": {"raw-lines": []},
        "sess": sess,
        "kwh": Decimal("0"),
    }
    assert headers == expected_headers
    assert type(headers["breakdown"]) == type(expected_headers)


def test_process_CCD_3(mocker):
    elements = {
        "CCDE": ["3", "", "NRG"],
        "TCOD": ["NIGHT", "Night"],
        "TMOD": ["453043"],
        "CONS": [[]],
        "BPRI": ["10"],
    }

    headers = {
        "bill_elements": [],
        "kwh": Decimal("0"),
    }

    chellow.bill_parser_haven_edi._process_CCD_3(elements, headers)

    expected_headers = {
        "kwh": Decimal("0"),
        "bill_elements": [
            chellow.bill_parser_haven_edi.BillElement(
                gbp=Decimal("0.00"),
                rate=Decimal("0.0001"),
                cons=Decimal("0"),
                titles=None,
                desc="Night",
            )
        ],
    }
    assert headers == expected_headers


def test_process_CCD_1(mocker):
    msn = "hgkh"

    elements = {
        "CCDE": ["1", "", "NRG"],
        "TCOD": ["NIGHT", "Night"],
        "TMOD": ["453043"],
        "MTNR": [msn],
        "CONS": [[]],
        "BPRI": ["10"],
        "PRDT": ["200301"],
        "PVDT": ["200331"],
        "MLOC": [""],
        "PRRD": ["0", "00", "1", "00"],
        "ADJF": ["", "1"],
    }

    headers = {
        "reads": [],
    }

    chellow.bill_parser_haven_edi._process_CCD_1(elements, headers)

    expected_headers = {
        "reads": [
            {
                "msn": msn,
                "mpan": "      ",
                "coefficient": Decimal("0.00001"),
                "units": "kWh",
                "tpr_code": "453043",
                "prev_date": utc_datetime(2020, 3, 31, 22, 30),
                "prev_value": Decimal("1"),
                "prev_type_code": "N",
                "pres_date": utc_datetime(2020, 3, 1, 23, 30),
                "pres_value": Decimal("0"),
                "pres_type_code": "N",
            }
        ]
    }
    assert headers == expected_headers


def test_process_CLO(mocker):
    account = "accnt"

    elements = {"CLOC": [account, ""]}

    headers = {}

    chellow.bill_parser_haven_edi._process_CLO(elements, headers)

    expected_headers = {
        "account": "",
    }
    assert headers == expected_headers


def test_process_segment_error(mocker):
    mocker.patch("chellow.bill_parser_haven_edi._process_BTL", side_effect=BadRequest())

    code = "BTL"
    elements = []
    line = ""
    headers = {}
    line_number = 13

    bill = chellow.bill_parser_haven_edi._process_segment(
        code, elements, line, headers, line_number
    )

    assert bill == {
        "error": "Can't parse the line number 13  : The browser (or proxy) "
        "sent a request that this server could not understand."
    }


def test_Parser(mocker, sess):
    file_lines = [
        "MHD=2+UTLBIL:3'",
        "MTR=6'",
    ]
    f = BytesIO(b"\n".join(n.encode("utf8") for n in file_lines))
    parser = chellow.bill_parser_haven_edi.Parser(f)
    parser.make_raw_bills()