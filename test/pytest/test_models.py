from chellow.models import Contract, Era, Mtc, Scenario, Supply
from chellow.utils import utc_datetime

import pytest

import sqlalchemy.exc

from werkzeug.exceptions import BadRequest


def test_Era_update(mocker):
    sess = mocker.Mock()
    start_date = utc_datetime(2019, 1, 1)
    finish_date = utc_datetime(2019, 1, 10)
    mop_contract = mocker.Mock()
    mop_contract.start_date.return_value = start_date
    mop_contract.finish_date.return_value = finish_date
    mop_account = "mop account"
    dc_contract = mocker.Mock()
    dc_contract.start_date.return_value = start_date
    dc_contract.finish_date.return_value = finish_date
    dc_account = "dc account"
    msn = " yhlk "
    pc = mocker.Mock()
    mtc = mocker.Mock()
    cop = mocker.Mock()
    ssc = mocker.Mock()
    properties = {}
    imp_mpan_core = '22 3423 2442 127'
    imp_llfc_code = '110'
    imp_supplier_contract = mocker.Mock()
    imp_supplier_contract.start_date.return_value = start_date
    imp_supplier_contract.finish_date.return_value = None
    imp_supplier_account = 'supplier account'
    imp_sc = 400
    exp_mpan_core = exp_llfc_code = exp_supplier_contract = None
    exp_supplier_account = exp_sc = None

    era = mocker.Mock()
    era.start_date = start_date
    era.finish_date = finish_date
    era.supply.dno.dno_code = '22'
    era.supply.dno.get_llfc_by_code().valid_to = finish_date
    era.supply.dno.get_llfc_by_code().is_import = True
    era.supply.find_era_at.return_value = None
    Era.update(
        era, sess, start_date, finish_date, mop_contract, mop_account,
        dc_contract, dc_account, msn, pc, mtc, cop, ssc, properties,
        imp_mpan_core, imp_llfc_code, imp_supplier_contract,
        imp_supplier_account, imp_sc, exp_mpan_core, exp_llfc_code,
        exp_supplier_contract, exp_supplier_account, exp_sc)
    assert era.msn == 'yhlk'


def test_MTC_find_by_code(mocker):
    q_mock = mocker.Mock()
    q_mock.filter_by = mocker.Mock(return_value=mocker.Mock())
    sess = mocker.Mock()
    sess.query.return_value = q_mock
    dno = mocker.Mock()
    code = '34'

    Mtc.find_by_code(sess, dno, code)
    q_mock.filter_by.assert_called_with(dno=dno, code='034')


def test_update_Era_llfc_valid_to(mocker):
    """
    Error raised if LLFC finishes before the era
    """
    llfc = mocker.Mock()
    llfc.valid_from = utc_datetime(2000, 1, 1)
    llfc.valid_to = utc_datetime(2010, 5, 1)

    start_date = utc_datetime(2010, 1, 1)
    finish_date = utc_datetime(2011, 1, 1)
    mop_account = "A mop account"
    dc_account = "A dc account"
    msn = "mtr001"
    mtc_code = "845"
    properties = {}
    imp_mpan_core = "22 9877 3472 588"
    imp_llfc_code = "510"
    imp_supplier_contract = mocker.Mock()
    imp_supplier_contract.start_date.return_value = utc_datetime(2000, 1, 1)
    imp_supplier_contract.finish_date.return_value = None
    instance = mocker.Mock()
    instance.supply.dno.dno_code = '22'
    instance.supply.dno.get_llfc_by_code.return_value = llfc

    with pytest.raises(
            BadRequest,
            match="The imp line loss factor 510 is only valid until "
            "2010-05-01 01:00 but the era ends at 2011-01-01 00:00."):
        Era.update(
            instance, mocker.Mock(), start_date, finish_date, mocker.Mock(),
            mop_account, mocker.Mock(), dc_account, msn, mocker.Mock(),
            mtc_code, mocker.Mock(), mocker.Mock(), properties, imp_mpan_core,
            imp_llfc_code, imp_supplier_contract, mocker.Mock(), mocker.Mock(),
            mocker.Mock(), mocker.Mock(), mocker.Mock(), mocker.Mock(),
            mocker.Mock(), mocker.Mock())


def test_Contract_get_next_batch_details(mocker):
    MockBatch = mocker.patch('chellow.models.Batch', autospec=True)
    MockBatch.contract = mocker.Mock()
    instance = mocker.Mock()

    batch_description = "A King"
    batch = mocker.Mock()
    batch.reference = "king-098"
    batch.description = batch_description

    returns = iter([batch])

    class Sess():
        def query(self, *args):
            return self

        def join(self, *args):
            return self

        def order_by(self, *args):
            return self

        def filter(self, *args):
            return self

        def first(self, *args):
            return next(returns)

    sess = Sess()
    ref, desc = Contract.get_next_batch_details(instance, sess)
    assert ref == "king-099"
    assert desc == batch_description


def test_Contract_get_next_batch_details__no_suffix(mocker):
    MockBatch = mocker.patch('chellow.models.Batch', autospec=True)
    MockBatch.contract = mocker.Mock()
    instance = mocker.Mock()

    batch_reference = "king"
    batch_description = "A King"
    batch = mocker.Mock()
    batch.reference = batch_reference
    batch.description = batch_description

    returns = iter([batch])

    class Sess():
        def query(self, *args):
            return self

        def join(self, *args):
            return self

        def order_by(self, *args):
            return self

        def filter(self, *args):
            return self

        def first(self, *args):
            return next(returns)

    sess = Sess()
    ref, desc = Contract.get_next_batch_details(instance, sess)
    assert ref == batch_reference
    assert desc == batch_description


def test_sql_insert_GExitZone(mocker, sess):
    with pytest.raises(
            sqlalchemy.exc.ProgrammingError,
            match='null value in column "g_ldz_id" violates not-null '
            'constraint'):
        sess.execute(
            "INSERT INTO g_exit_zone (id, code, g_ldz_id) VALUES "
            "(DEFAULT, 'E1', null)")


def test_Supply_get_by_MPAN_core(sess):
    mpan_core = '22 1737 1873 221'

    with pytest.raises(
            BadRequest,
            match=f"The MPAN core {mpan_core} is not set up in Chellow."):

        Supply.get_by_mpan_core(sess, mpan_core)


def test_Scenario_init(sess):
    name = "scenario_bau"
    properties = {
      "local_rates": {},
      "scenario_start_year": 2015,
      "scenario_start_month": 6,
      "scenario_duration": 1
    }

    with pytest.raises(BadRequest, match="The 'local_rates' must be a list."):
        Scenario(name, properties)
