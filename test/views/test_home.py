from decimal import Decimal
from io import BytesIO

from flask import g

from utils import match


from chellow.models import (
    BillType,
    Comm,
    Contract,
    Cop,
    EnergisationStatus,
    GContract,
    GDn,
    GReadType,
    GReadingFrequency,
    GUnit,
    GspGroup,
    MarketRole,
    MeterPaymentType,
    MeterType,
    Mtc,
    MtcLlfc,
    MtcLlfcSsc,
    MtcLlfcSscPc,
    MtcParticipant,
    MtcSsc,
    Participant,
    Pc,
    ReportRun,
    Site,
    Snag,
    Source,
    Ssc,
    VoltageLevel,
    insert_bill_types,
    insert_comms,
    insert_cops,
    insert_energisation_statuses,
    insert_g_read_types,
    insert_g_reading_frequencies,
    insert_g_units,
    insert_sources,
    insert_voltage_levels,
)
from chellow.utils import ct_datetime, to_utc, utc_datetime


def test_site_edit_post_fail(client, sess):
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    bank_holiday_rate_script = {"bank_holidays": []}
    Contract.insert_non_core(
        sess,
        "bank_holidays",
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        bank_holiday_rate_script,
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "00", "hh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    insert_comms(sess)
    cop = Cop.get_by_code(sess, "5")
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(
        sess,
        "845",
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    dno.insert_llfc(
        sess,
        "521",
        "Export (HV)",
        voltage_level,
        False,
        False,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    sess.commit()

    data = {
        "source_id": str(source.id),
        "name": "Bob",
        "start_date_year": "2000",
        "start_date_month": "01",
        "start_date_day": "01",
        "start_date_hour": "00",
        "start_date_minute": "00",
        "insert_electricity": "Insert Electricity",
        "mop_contract_id": str(mop_contract.id),
        "dc_contract_id": str(dc_contract.id),
        "pc_id": str(pc.id),
        "cop_id": str(cop.id),
        "imp_supplier_contract_id": str(imp_supplier_contract.id),
        "energisation_status_id": str(energisation_status.id),
        "gsp_group_id": str(gsp_group.id),
    }
    response = client.post(f"/sites/{site.id}/edit", data=data)

    patterns = [
        r'<select name="energisation_status_id">\s*'
        r'<option value="2">D - De-Energised</option>\s*'
        r'<option value="1" selected>E - Energised</option>\s*'
        r"</select>",
        r'<select name="comm_id">\s*'
        r'<option value="3">GPRS General Packet Radio Service</option>\s*'
        r'<option value="2">GSM Global System for Mobile Communications</option>\s*'
        r'<option value="6">HP Handheld Perm</option>\s*'
        r'<option value="1">IP Internet Protocol</option>\s*'
        r'<option value="5">PK Paknet</option>\s*'
        r'<option value="4">PS Public Switch \(BT Line\)</option>\s*'
        r'<option value="7">SUB Sub Meter</option>\s*'
        r"</select>",
    ]
    match(response, 400, *patterns)


def test_site_get(client, sess):
    valid_from = to_utc(ct_datetime(2000, 1, 1))
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    bank_holiday_rate_script = {"bank_holidays": []}
    Contract.insert_non_core(
        sess,
        "bank_holidays",
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        bank_holiday_rate_script,
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "00", "hh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, "5")
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(
        sess,
        "845",
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    mtc_participant = MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    llfc = dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    MtcLlfc.insert(sess, mtc_participant, llfc, valid_from, None)
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    insert_comms(sess)
    comm = Comm.get_by_code(sess, "GSM")
    site.insert_e_supply(
        sess,
        source,
        None,
        "Bob",
        utc_datetime(2000, 1, 1),
        utc_datetime(2020, 1, 1),
        gsp_group,
        mop_contract,
        "773",
        dc_contract,
        "ghyy3",
        "hgjeyhuw",
        pc,
        "845",
        cop,
        comm,
        None,
        energisation_status,
        {},
        "22 0470 7514 535",
        "510",
        imp_supplier_contract,
        "7748",
        361,
        None,
        None,
        None,
        None,
        None,
    )
    sess.commit()

    response = client.get(f"/sites/{site.id}")

    patterns = []
    match(response, 200, *patterns)


def test_site_get_dumb(client, sess):
    valid_from = to_utc(ct_datetime(1996, 1, 1))
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    bank_holiday_rate_script = {"bank_holidays": []}
    Contract.insert_non_core(
        sess,
        "bank_holidays",
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        bank_holiday_rate_script,
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "02", "nhh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, "5")
    ssc = Ssc.insert(sess, "0001", "All", True, utc_datetime(1996, 1), None)
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(
        sess,
        "845",
        False,
        True,
        valid_from,
        None,
    )
    mtc_participant = MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    llfc = dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    insert_comms(sess)
    comm = Comm.get_by_code(sess, "GSM")
    MtcLlfc.insert(sess, mtc_participant, llfc, valid_from, None)
    mtc_ssc = MtcSsc.insert(sess, mtc_participant, ssc, valid_from, None)
    mtc_llfc_ssc = MtcLlfcSsc.insert(sess, mtc_ssc, llfc, valid_from, None)
    MtcLlfcSscPc.insert(sess, mtc_llfc_ssc, pc, valid_from, None)
    site.insert_e_supply(
        sess,
        source,
        None,
        "Bob",
        utc_datetime(2000, 1, 1),
        utc_datetime(2020, 1, 1),
        gsp_group,
        mop_contract,
        "773",
        dc_contract,
        "ghyy3",
        "hgjeyhuw",
        pc,
        "845",
        cop,
        comm,
        ssc,
        energisation_status,
        {},
        "22 0470 7514 535",
        "510",
        imp_supplier_contract,
        "7748",
        361,
        None,
        None,
        None,
        None,
        None,
    )
    sess.commit()

    response = client.get(f"/sites/{site.id}")

    patterns = []
    match(response, 200, *patterns)


def test_site_hh_data(sess, client):
    site = Site.insert(sess, "CI017", "Water Works")
    sess.commit()

    query_string = {
        "year": "2022",
        "month": "3",
    }
    response = client.get(f"/sites/{site.id}/hh_data", query_string=query_string)

    match(response, 200)


def test_g_bill_get(client, sess):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_supply = site.insert_g_supply(
        sess,
        "87614362",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")

    breakdown = {"units_consumed": 771}
    insert_bill_types(sess)
    bill_type_n = BillType.get_by_code(sess, "N")
    g_bill = g_batch.insert_g_bill(
        sess,
        g_supply,
        bill_type_n,
        "55h883",
        "dhgh883",
        utc_datetime(2019, 4, 3),
        utc_datetime(2020, 1, 1),
        utc_datetime(2020, 1, 31, 23, 30),
        Decimal("45"),
        Decimal("12.40"),
        Decimal("1.20"),
        Decimal("14.52"),
        "",
        breakdown,
    )

    sess.commit()

    response = client.get(f"/g_bills/{g_bill.id}")

    regexes = [r"<tr>\s*" r"<td>units</td>\s*" r"<td>771</td>"]

    match(response, 200, *regexes)


def test_g_bill_imports_post_full(mocker, app, client, sess):
    file_lines = (
        "STX=ANA:1+Marsh Gas:MARSH Gas Limited+BPAJA:Bill Paja 771+"
        "171023:867369+856123++UTLHDR'",
        "MHD=1+UTLHDR:3'",
        "TYP=0715'",
        "SDT=Marsh Gas+Marsh Gas Limited++818671845'",
        "CDT=BPAJA:BPAJA+Bill Paja Limited - BPAJA++1'",
        "FIL=1+1+171023'",
        "MTR=6'",
        "MHD=2+UTLBIL:3'",
        "CLO=::10205041+Bill Paja Limited+Mole Hall, BATH::BA1 9MH'",
        "BCD=171022+171022+7868273476++M+N++170601:170630'",
        "CCD=1+1::GAS+MARSH6:Meter Reading++hyygk4882+87614362+170701+170601++"
        "83551:01:81773:01+8746000+771000:M3+CF:102264+841349:M3++831200:KWH+"
        "170601+170701'",
        "ADJ=1+1+CV:3930000'",
        "CCD=2+3::PPK+MARSH6:Unidentified Gas++++++++8746000++CF:100000++"
        "008521+8746000+170601+170631+008727+091'",
        "CCD=3+3::PPK+MARSH6:Commodity++++++++8746000++CF:100000++9873510+"
        "8746000+170601+170630+815510+9931'",
        "CCD=4+3::PPD+MARSH6:Transportation++++++++30000++CF:100000++86221004+"
        "30000+170601+170630+86221004+9224'",
        "CCD=5+3::PPD+MARSH6:Meter Reading++++++++30000++CF:100000++82113473+"
        "30000+170601+170630+8582284+941'",
        "CCD=6+3::PPD+MARSH6:Meter Rental++++++++30000++CF:100000++3228000+"
        "30000+170601+170630+8993000+841'",
        "CCD=7+3::PPK+MARSH6:Transportation++++++++8116500++CF:100000++"
        "005337+4617800+170601+170630+006120+882'",
        "VAT=1+++L+7986+23885+331+86334'",
        "BTL=000+88772+332++77345'",
        "MTR=14'",
        "MHD=2+UTLBIL:3'",
        "CLO=::10205041+Bill Paja Limited+Mole Hall, BATH::BA1 9MH'",
        "BCD=171022+171022+7868273476++M+N++170601:170630'",
        "CCD=1+1::GAS+MARSH6:Meter Reading++hyygk4882+87614362+170701+170601++"
        "83551:01:81773:01+8746000+771000:M3+CF:102264+841349:M3++831200:KWH+"
        "170601+170701'",
        "ADJ=1+1+CV:3930000'",
        "CCD=2+3::PPK+MARSH6:Unidentified Gas++++++++8746000++CF:100000++"
        "008521+8746000+170601+170631+008727+091'",
        "CCD=3+3::PPK+MARSH6:Commodity++++++++8746000++CF:100000++9873510+"
        "8746000+170601+170630+815510'",
        "CCD=4+3::PPD+MARSH6:Transportation++++++++30000++CF:100000++86221004+"
        "30000+170601+170630+86221004+9224'",
        "CCD=5+3::PPD+MARSH6:Meter Reading++++++++30000++CF:100000++82113473+"
        "30000+170601+170630+8582284+941'",
        "CCD=6+3::PPD+MARSH6:Meter Rental++++++++30000++CF:100000++3228000+"
        "30000+170601+170630+8993000+841'",
        "CCD=7+3::PPK+MARSH6:Transportation++++++++8116500++CF:100000++005337+"
        "4617800+170601+170630+006120+882'",
        "VAT=1+++L+7986+23885+331+86334'",
        "BTL=000+88772+332++77345'",
        "MTR=14'",
        "END=288'",
    )

    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")
    insert_bill_types(sess)
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    site.insert_g_supply(
        sess,
        "87614362",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    insert_g_read_types(sess)
    sess.commit()

    file_name = "gas.engie.edi"
    file_bytes = "\n".join(file_lines).encode("utf8")
    f = BytesIO(file_bytes)

    data = {"g_batch_id": str(g_batch.id), "import_file": (f, file_name)}

    response = client.post("/g_bill_imports", data=data)

    match(response, 303, "/g_bill_imports/0")

    response = client.get("/g_bill_imports/0")

    match(
        response,
        200,
        r"All the bills have been successfully loaded and attached to the " r"batch.",
    )
    sess.rollback()
    res = sess.execute("select breakdown from g_bill where id = 2")
    assert '"units_consumed": 771,' in next(res)[0]


def test_g_bill_imports_post(mocker, app, client, sess):
    g_contract = GContract.insert(
        sess,
        "Fusion 2020",
        "",
        {},
        utc_datetime(2019, 1, 1),
        utc_datetime(2019, 2, 28, 23, 30),
        {},
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")
    sess.commit()

    file_name = "gas.engie.edi"
    file_bytes = b"edifile'"
    f = BytesIO(file_bytes)

    data = {"g_batch_id": str(g_batch.id), "import_file": (f, file_name)}

    import_id = 3

    mock_start_importer = mocker.patch(
        "chellow.views.home.chellow.g_bill_import.start_bill_importer",
        return_value=import_id,
    )

    response = client.post("/g_bill_imports", data=data)
    mock_start_importer.assert_called_with(g.sess, g_batch.id, file_name, file_bytes)

    match(response, 303, "/g_bill_imports/3")


def test_g_batch_add_post(client, sess):
    g_contract = GContract.insert(
        sess,
        "Fusion 2020",
        "",
        {},
        utc_datetime(2019, 1, 1),
        utc_datetime(2019, 2, 28, 23, 30),
        {},
    )
    sess.commit()

    data = {"reference": "engie_edi", "description": "Engie EDI"}

    response = client.post(f"/g_contracts/{g_contract.id}/add_batch", data=data)

    match(response, 303, "/g_batches/1")


def g_supply_note_add_get(client, sess):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_supply = site.insert_g_supply(
        sess,
        "7y94u5",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    sess.commit()

    response = client.get(f"/g_supplies/{g_supply.id}/notes/add")

    match(response, 200)


def g_supply_notes_get(client, sess):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_supply = site.insert_g_supply(
        sess,
        "7y94u5",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )

    response = client.get(f"/g_supplies/{g_supply.id}/notes")

    match(response, 200)


def test_g_read_edit_post_delete(sess, client):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_supply = site.insert_g_supply(
        sess,
        "7y94u5",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")
    insert_bill_types(sess)
    bill_type_n = BillType.get_by_code(sess, "N")
    g_bill = g_batch.insert_g_bill(
        sess,
        g_supply,
        bill_type_n,
        "55h883",
        "dhgh883",
        utc_datetime(2019, 4, 3),
        utc_datetime(2020, 1, 1),
        utc_datetime(2020, 1, 31, 23, 30),
        Decimal("45"),
        Decimal("12.40"),
        Decimal("1.20"),
        Decimal("14.52"),
        "",
        {},
    )
    insert_g_read_types(sess)
    g_read_type_A = GReadType.get_by_code(sess, "A")
    g_read = g_bill.insert_g_read(
        sess,
        "ghu5438gt",
        g_unit_M3,
        1,
        37,
        Decimal(800),
        utc_datetime(2020, 1, 1),
        g_read_type_A,
        Decimal(900),
        utc_datetime(2020, 1, 31),
        g_read_type_A,
    )
    sess.commit()

    data = {
        "delete": "Delete",
    }

    response = client.post(f"/g_reads/{g_read.id}/edit", data=data)

    match(response, 303, f"/g_bills/{g_bill.id}")


def test_g_rate_script_edit_post_delete(sess, client):
    g_contract = GContract.insert(
        sess,
        "Fusion 2020",
        "",
        {},
        utc_datetime(2019, 1, 1),
        utc_datetime(2019, 2, 28, 23, 30),
        {},
    )
    g_rate_script = g_contract.insert_g_rate_script(sess, utc_datetime(2019, 2, 1), {})
    sess.commit()

    data = {
        "delete": "Delete",
    }

    response = client.post(f"/g_rate_scripts/{g_rate_script.id}/edit", data=data)

    match(response, 303, f"/g_contracts/{g_contract.id}")


def test_g_read_add_get(sess, client):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    g_supply = site.insert_g_supply(
        sess,
        "7y94u5",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")
    insert_bill_types(sess)
    bill_type_n = BillType.get_by_code(sess, "N")
    g_bill = g_batch.insert_g_bill(
        sess,
        g_supply,
        bill_type_n,
        "55h883",
        "dhgh883",
        utc_datetime(2019, 4, 3),
        utc_datetime(2020, 1, 1),
        utc_datetime(2020, 1, 31, 23, 30),
        Decimal("45"),
        Decimal("12.40"),
        Decimal("1.20"),
        Decimal("14.52"),
        "",
        {},
    )
    sess.commit()

    response = client.get(f"/g_bills/{g_bill.id}/edit")

    match(response, 200)


def test_g_era_post_delete(sess, client):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    g_supply = site.insert_g_supply(
        sess,
        "7y94u5",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_era = g_supply.insert_g_era_at(sess, utc_datetime(2018, 3, 1))
    sess.commit()

    data = {
        "delete": "Delete",
    }

    response = client.post(f"/g_eras/{g_era.id}/edit", data=data)

    match(response, 303, r"/g_supplies/1")


def test_general_import_post_full(sess, client):
    """General import of channel snag unignore and check the import that's
    been created.
    """
    valid_from = to_utc(ct_datetime(1996, 1, 1))
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    bank_holiday_rate_script = {"bank_holidays": []}
    Contract.insert_non_core(
        sess,
        "bank_holidays",
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        bank_holiday_rate_script,
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "00", "hh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, "5")
    insert_comms(sess)
    comm = Comm.get_by_code(sess, "GSM")
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(
        sess,
        "845",
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    mtc_participant = MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    llfc = dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    MtcLlfc.insert(sess, mtc_participant, llfc, valid_from, None)
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    supply = site.insert_e_supply(
        sess,
        source,
        None,
        "Bob",
        utc_datetime(2000, 1, 1),
        utc_datetime(2020, 1, 1),
        gsp_group,
        mop_contract,
        "773",
        dc_contract,
        "ghyy3",
        "hgjeyhuw",
        pc,
        "845",
        cop,
        comm,
        None,
        energisation_status,
        {},
        "22 0470 7514 535",
        "510",
        imp_supplier_contract,
        "7748",
        361,
        None,
        None,
        None,
        None,
        None,
    )
    era = supply.eras[0]
    channel = era.insert_channel(sess, False, "ACTIVE")
    channel.add_snag(
        sess,
        "Missing",
        utc_datetime(2003, 8, 2, 23, 30),
        utc_datetime(2004, 7, 6, 22, 30),
    )
    snag = sess.query(Snag).order_by(Snag.start_date).first()
    snag.set_is_ignored(True)
    sess.commit()

    file_items = [
        "insert",
        "channel_snag_unignore",
        "22 0470 7514 535",
        "FALSE",
        "Active",
        "Missing",
        "2003-08-03 00:00",
        "2004-07-06 23:30",
    ]
    file_name = "gi_channel_snag_ignore.csv"
    file_bytes = ",".join(file_items).encode("utf8")
    f = BytesIO(file_bytes)

    data = {"import_file": (f, file_name)}

    response = client.post("/general_imports", data=data)

    match(response, 303, "/general_imports/0")

    response = client.get("/general_imports/0")

    match(response, 200, r"The file has been imported successfully\.")
    sess.rollback()

    assert not snag.is_ignored


def test_g_bill_add_post(sess, client):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    mprn = "750278673"
    site.insert_g_supply(
        sess,
        mprn,
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")
    insert_bill_types(sess)
    sess.commit()

    data = {
        "bill_type_id": "2",
        "mprn": mprn,
        "reference": "765988",
        "account": "1",
        "issue_year": "2017",
        "issue_month": "02",
        "issue_day": "03",
        "issue_hour": "00",
        "issue_minute": "00",
        "start_year": "2017",
        "start_month": "03",
        "start_day": "01",
        "start_hour": "00",
        "start_minute": "00",
        "finish_year": "2017",
        "finish_month": "04",
        "finish_day": "01",
        "finish_hour": "00",
        "finish_minute": "30",
        "kwh": "0.00",
        "net": "0.00",
        "vat": "0.00",
        "gross": "0.00",
        "breakdown": "{}",
    }

    response = client.post(f"/g_batches/{g_batch.id}/add_bill", data=data)

    match(response, 303, r"/g_bills/1")


def test_g_bill_edit_post(sess, client):
    site = Site.insert(sess, "22488", "Water Works")
    g_dn = GDn.insert(sess, "EE", "East of England")
    g_ldz = g_dn.insert_g_ldz(sess, "EA")
    g_exit_zone = g_ldz.insert_g_exit_zone(sess, "EA1")
    insert_g_units(sess)
    g_unit_M3 = GUnit.get_by_code(sess, "M3")
    g_contract = GContract.insert(
        sess, "Fusion 2020", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    insert_g_reading_frequencies(sess)
    g_reading_frequency_M = GReadingFrequency.get_by_code(sess, "M")
    g_supply = site.insert_g_supply(
        sess,
        "87614362",
        "main",
        g_exit_zone,
        utc_datetime(2018, 1, 1),
        None,
        "hgeu8rhg",
        1,
        g_unit_M3,
        g_contract,
        "d7gthekrg",
        g_reading_frequency_M,
    )
    g_batch = g_contract.insert_g_batch(sess, "b1", "Jan batch")

    breakdown = {"units_consumed": 771}
    insert_bill_types(sess)
    bill_type_n = BillType.get_by_code(sess, "N")
    g_bill = g_batch.insert_g_bill(
        sess,
        g_supply,
        bill_type_n,
        "55h883",
        "dhgh883",
        utc_datetime(2019, 4, 3),
        utc_datetime(2020, 1, 1),
        utc_datetime(2020, 1, 31, 23, 30),
        Decimal("45"),
        Decimal("12.40"),
        Decimal("1.20"),
        Decimal("14.52"),
        "",
        breakdown,
    )

    sess.commit()

    data = {
        "bill_type_id": "3",
        "reference": "8899900012",
        "account": "college_rooms",
        "issue_year": "2015",
        "issue_month": "11",
        "issue_day": "01",
        "issue_hour": "00",
        "issue_minute": "00",
        "start_year": "2015",
        "start_month": "09",
        "start_day": "01",
        "start_hour": "01",
        "start_minute": "00",
        "finish_year": "2015",
        "finish_month": "09",
        "finish_day": "30",
        "finish_hour": "01",
        "finish_minute": "00",
        "kwh": "4500901",
        "net_gbp": "6972.33",
        "vat_gbp": "1003.89",
        "gross_gbp": "7976.22",
        "raw_lines": "reference,mprn,bill_type,account,issue_date,"
        "start_date,finish_date,kwh,net_gbp,vat_gbp,gross_gbp,"
        "breakdown,msn,unit,correction_factor,"
        "calorific_value,prev_date,prev_value,prev_type,pres_date,"
        "prev_value,pres_type\n"
        "8899900012,750278673,N,college_rooms,2015-11-01 00:00,"
        "2015-09-01 00:00,2015-09-30 00:00,4500901,6972.33,1003.89,"
        '7976.22,{"gas_rate": 0.019448, "gas_gbp": 8936.13,'
        '"ccl_gbp": 275.32, "vat_0500pc": 0.3, "vat_1500pc": 49.12, '
        '"vat_1750pc": 55.7, "vat_2000pc": 801},hwo8tt,HCUF,FALSE,,'
        "39.300811,2015-09-01 00:00,567822,A,2015-10-01 00:00,"
        "575652,A",
        "breakdown": '{"ccl_gbp": 275.32, "gas_gbp": 8936.13, '
        '"gas_rate": 0.019448, "vat_0500pc": 0.3, "vat_1500pc": 49.12,'
        '"vat_1750pc": 55.7, "vat_2000pc": 801}',
    }

    response = client.post(f"/g_bills/{g_bill.id}/edit", data=data)

    match(response, 303)


def test_non_core_auto_importer_get(sess, client):
    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    contract = Contract.insert_non_core(
        sess, "bank_holidays", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    sess.commit()

    response = client.get(f"/non_core_contracts/{contract.id}/auto_importer")

    match(response, 200)


def test_non_core_auto_importer_post(mocker, sess, client):
    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    contract = Contract.insert_non_core(
        sess, "bank_holidays", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    sess.commit()

    mocker.patch("chellow.views.home.import_module")

    response = client.post(f"/non_core_contracts/{contract.id}/auto_importer")

    match(response, 303)


def test_non_core_contract_edit_post(sess, client):
    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    contract = Contract.insert_non_core(
        sess, "g_cv", "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    sess.commit()

    data = {
        "name": "g_cv",
        "properties": """{
"enabled": true,
"url": "http://localhost:8080/nationalgrid/cv.csv"}
""",
    }

    response = client.post(f"/non_core_contracts/{contract.id}/edit", data=data)

    match(response, 303)


def test_non_core_rate_script_edit_get(sess, client):
    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    contract = Contract.insert_non_core(
        sess, "rcrc", "import nonexistent", {}, utc_datetime(2000, 1, 1), None, {}
    )
    rs = contract.start_rate_script
    sess.commit()

    response = client.get(f"/non_core_rate_scripts/{rs.id}/edit")

    match(response, 200)


def test_site_edit_get(sess, client, app):
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    insert_cops(sess)
    insert_comms(sess)
    Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(
        sess,
        "845",
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_sources(sess)
    insert_energisation_statuses(sess)
    sess.commit()

    response = client.get(f"/sites/{site.id}/edit")
    patterns = [
        r'<select name="comm_id">\s*'
        r'<option value="3">GPRS General Packet Radio Service</option>\s*'
    ]
    match(response, 200, *patterns)


def test_site_edit_post_hh(sess, client):
    valid_from = to_utc(ct_datetime(1996, 1, 1))
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "00", "hh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, "5")
    insert_comms(sess)
    comm = Comm.get_by_code(sess, "GSM")
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(sess, "845", False, True, valid_from, None)
    mtc_participant = MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    llfc = dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    MtcLlfc.insert(sess, mtc_participant, llfc, valid_from, None)
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    sess.commit()

    data = {
        "source_id": source.id,
        "gsp_group_id": gsp_group.id,
        "mop_contract_id": mop_contract.id,
        "dc_contract_id": dc_contract.id,
        "dc_account": "dc1",
        "msn": "jjl4",
        "pc_id": pc.id,
        "mtc_code": "845",
        "cop_id": cop.id,
        "comm_id": comm.id,
        "ssc_code": "",
        "properties": "{}",
        "start_year": "2021",
        "start_month": "01",
        "start_day": "01",
        "start_hour": "00",
        "start_minute": "00",
        "mop_account": "ma1",
        "imp_mpan_core": "22 6644 1123 880",
        "imp_supplier_contract_id": imp_supplier_contract.id,
        "imp_supplier_account": "sup1",
        "imp_sc": "200",
        "imp_llfc_code": "510",
        "energisation_status_id": energisation_status.id,
        "insert_electricity": "insert_electricity",
        "name": "main",
    }
    response = client.post(f"/sites/{site.id}/edit", data=data)
    match(response, 303)


def test_site_edit_post_nhh(sess, client):
    valid_from = to_utc(ct_datetime(1996, 1, 1))
    site = Site.insert(sess, "CI017", "Water Works")

    market_role_Z = MarketRole.get_by_code(sess, "Z")
    participant = Participant.insert(sess, "CALB", "AK Industries")
    participant.insert_party(
        sess, market_role_Z, "None core", utc_datetime(2000, 1, 1), None, None
    )
    market_role_X = MarketRole.insert(sess, "X", "Supplier")
    market_role_M = MarketRole.insert(sess, "M", "Mop")
    market_role_C = MarketRole.insert(sess, "C", "HH Dc")
    market_role_R = MarketRole.insert(sess, "R", "Distributor")
    participant.insert_party(
        sess, market_role_M, "Fusion Mop Ltd", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_X, "Fusion Ltc", utc_datetime(2000, 1, 1), None, None
    )
    participant.insert_party(
        sess, market_role_C, "Fusion DC", utc_datetime(2000, 1, 1), None, None
    )
    mop_contract = Contract.insert_mop(
        sess, "Fusion", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    dc_contract = Contract.insert_dc(
        sess, "Fusion DC 2000", participant, "", {}, utc_datetime(2000, 1, 1), None, {}
    )
    pc = Pc.insert(sess, "03", "hh", utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, "5")
    insert_comms(sess)
    comm = Comm.get_by_code(sess, "GSM")
    imp_supplier_contract = Contract.insert_supplier(
        sess,
        "Fusion Supplier 2000",
        participant,
        "",
        {},
        utc_datetime(2000, 1, 1),
        None,
        {},
    )
    dno = participant.insert_party(
        sess, market_role_R, "WPD", utc_datetime(2000, 1, 1), None, "22"
    )
    meter_type = MeterType.insert(sess, "C5", "COP 1-5", utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, "CR", "Credit", utc_datetime(1996, 1, 1), None
    )
    mtc = Mtc.insert(sess, "845", False, True, valid_from, None)
    mtc_participant = MtcParticipant.insert(
        sess,
        mtc,
        participant,
        "HH COP5 And Above With Comms",
        False,
        True,
        meter_type,
        meter_payment_type,
        0,
        valid_from,
        None,
    )
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, "HV")
    llfc = dno.insert_llfc(
        sess,
        "510",
        "PC 5-8 & HH HV",
        voltage_level,
        False,
        True,
        utc_datetime(1996, 1, 1),
        None,
    )
    insert_sources(sess)
    source = Source.get_by_code(sess, "net")
    gsp_group = GspGroup.insert(sess, "_L", "South Western")
    insert_energisation_statuses(sess)
    energisation_status = EnergisationStatus.get_by_code(sess, "E")
    ssc = Ssc.insert(sess, "0001", "All", True, utc_datetime(1996, 1, 1), None)
    MtcLlfc.insert(sess, mtc_participant, llfc, valid_from, None)
    mtc_ssc = MtcSsc.insert(sess, mtc_participant, ssc, valid_from, None)
    mtc_llfc_ssc = MtcLlfcSsc.insert(sess, mtc_ssc, llfc, valid_from, None)
    MtcLlfcSscPc.insert(sess, mtc_llfc_ssc, pc, valid_from, None)
    sess.commit()

    data = {
        "source_id": source.id,
        "gsp_group_id": gsp_group.id,
        "mop_contract_id": mop_contract.id,
        "dc_contract_id": dc_contract.id,
        "dc_account": "dc1",
        "msn": "jjl4",
        "pc_id": pc.id,
        "mtc_code": "845",
        "cop_id": cop.id,
        "comm_id": comm.id,
        "ssc_code": ssc.code,
        "properties": "{}",
        "start_year": "2021",
        "start_month": "01",
        "start_day": "01",
        "start_hour": "00",
        "start_minute": "00",
        "mop_account": "ma1",
        "imp_mpan_core": "22 6644 1123 880",
        "imp_supplier_contract_id": imp_supplier_contract.id,
        "imp_supplier_account": "sup1",
        "imp_sc": "200",
        "imp_llfc_code": "510",
        "energisation_status_id": energisation_status.id,
        "insert_electricity": "insert_electricity",
        "name": "main",
    }
    response = client.post(f"/sites/{site.id}/edit", data=data)
    match(response, 303)


def test_report_run_spreadsheet_get(sess, client):
    report_run = ReportRun.insert(sess, "bill_check", None, "_b_88", {})
    report_run.insert_row(sess, "", ["clump"], {}, {})
    sess.commit()

    response = client.get(f"/report_runs/{report_run.id}/spreadsheet")
    match(response, 200)