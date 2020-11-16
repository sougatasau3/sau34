from chellow.models import (
    Contract, Cop, GspGroup, MarketRole, MeterPaymentType, MeterType, Mtc,
    Participant, Pc, Scenario, Site, Source, VoltageLevel, insert_cops,
    insert_sources, insert_voltage_levels
)
from chellow.reports.report_247 import _make_calcs, _make_site_deltas, content
from chellow.utils import utc_datetime

from utils import match

from zish import loads


def test_with_scenario(mocker, sess, client):
    mock_Thread = mocker.patch('chellow.reports.report_247.threading.Thread')

    properties = """{
      "scenario_start_year": 2009,
      "scenario_start_month": 8,
      "scenario_duration": 1,

      "era_maps": {
        2000-08-01T00:00:00Z: {
          "llfcs": {
            "22": {
              "new_export": "521"
            }
          },
          "supplier_contracts": {
            "new_export": 10
          }
        }
      },

      "hh_data": {
        "CI017": {
          "generated": "
                2009-08-01 00:00, 40
                2009-08-15 00:00, 40"
        }
      }
    }"""
    scenario_props = loads(properties)
    scenario = Scenario.insert(sess, "New Gen", scenario_props)
    sess.commit()

    now = utc_datetime(2020, 1, 1)
    mocker.patch(
        'chellow.reports.report_247.utc_datetime_now', return_value=now)

    site_code = 'CI017'
    site = Site.insert(sess, site_code, 'Water Works')

    data = {
        'site_id': site.id,
        'scenario_id': scenario.id,
        'compression': False,
    }

    response = client.get('/reports/247', data=data)

    match(response, 303)

    base_name = ['New Gen']
    args = scenario_props, base_name, site.id, None, None, False, [], now

    mock_Thread.assert_called_with(target=content, args=args)


def test_make_site_deltas(mocker):
    era_1 = mocker.Mock()
    era_1.start_date = utc_datetime(2018, 1, 1)
    era_1.finish_date = None
    filter_returns = iter([[era_1], []])

    class Sess():
        def query(self, *args):
            return self

        def join(self, *args):
            return self

        def filter(self, *args):
            return next(filter_returns)

    sess = Sess()
    report_context = {}
    site = mocker.Mock()
    site.code = '1'
    scenario_hh = {
        site.code: {
            'used': '2019-03-01 00:00, 0'
        }
    }
    forecast_from = utc_datetime(2019, 4, 1)
    supply_id = None

    ss = mocker.patch('chellow.computer.SiteSource', autospec=True)
    ss_instance = ss.return_value
    ss_instance.hh_data = [
        {
            'start-date': utc_datetime(2019, 3, 1),
            'used-kwh': 0,
            'export-net-kwh': 0,
            'import-net-kwh': 0,
            'msp-kwh': 0
        }
    ]

    se = mocker.patch('chellow.reports.report_247.SiteEra', autospec=True)
    se.site = mocker.Mock()

    sup_s = mocker.patch(
        'chellow.reports.report_247.SupplySource', autospec=True)
    sup_s_instance = sup_s.return_value
    sup_s_instance.hh_data = {}

    res = _make_site_deltas(
        sess, report_context, site, scenario_hh, forecast_from, supply_id)

    assert len(res['supply_deltas'][False]['net']['site']) == 0


def test_make_site_deltas_nhh(mocker):
    era_1 = mocker.Mock()
    era_1.start_date = utc_datetime(2018, 1, 1)
    era_1.finish_date = None
    '''
    filter_args = iter(
        [
            [
                'False',
                'era.finish_date IS NULL OR era.finish_date >= :finish_date_1',
                'era.imp_mpan_core IS NOT NULL',
                'era.start_date <= :start_date_1', 'pc.code != :code_1',
                'true = :param_1'
            ],
            [
                'False',
                'era.finish_date IS NULL OR era.finish_date >= :finish_date_1',
                'era.imp_mpan_core IS NOT NULL',
                'era.start_date <= :start_date_1', 'source.code = :code_1',
                'true = :param_1'
            ]
        ]
    )
    '''

    filter_returns = iter([[era_1], []])

    class Sess():
        def query(self, *args):
            return self

        def join(self, *args):
            return self

        def filter(self, *args):
            '''
            actual_args = sorted(map(str, args))
            expected_args = next(filter_args)
            assert actual_args == expected_args
            '''
            return next(filter_returns)

    sess = Sess()
    report_context = {}
    site = mocker.Mock()
    site.code = '1'
    scenario_hh = {
        site.code: {
            'used': '2019-03-01 00:00, 0'
        }
    }
    forecast_from = utc_datetime(2019, 4, 1)
    supply_id = None

    ss = mocker.patch('chellow.computer.SiteSource', autospec=True)
    ss_instance = ss.return_value
    ss_instance.hh_data = [
        {
            'start-date': utc_datetime(2019, 3, 1),
            'used-kwh': 0,
            'export-net-kwh': 0,
            'import-net-kwh': 0,
            'msp-kwh': 0
        }
    ]

    se = mocker.patch('chellow.reports.report_247.SiteEra', autospec=True)
    se.site = mocker.Mock()

    sup_s = mocker.patch(
        'chellow.reports.report_247.SupplySource', autospec=True)
    sup_s_instance = sup_s.return_value
    hh_start_date = utc_datetime(2019, 3, 1)
    sup_s_instance.hh_data = [
        {
            'start-date': hh_start_date,
            'msp-kwh': 10
        }
    ]

    res = _make_site_deltas(
        sess, report_context, site, scenario_hh, forecast_from, supply_id)

    assert res['supply_deltas'][True]['net']['site'] == {hh_start_date: -10.0}


def test_scenario_new_generation(mocker, sess):
    site = Site.insert(sess, 'CI017', 'Water Works')
    start_date = utc_datetime(2009, 7, 31, 23, 00)
    finish_date = utc_datetime(2009, 8, 31, 22, 30)
    supply_id = None
    report_context = {}
    forecast_from = utc_datetime(2020, 1, 1)

    market_role_Z = MarketRole.insert(sess, 'Z', 'Non-core')
    participant = Participant.insert(sess, 'CALB', 'AK Industries')
    participant.insert_party(
        sess, market_role_Z, 'None core', utc_datetime(2000, 1, 1), None,
        None)
    bank_holiday_rate_script = {
        'bank_holidays': []
    }
    Contract.insert_non_core(
        sess, 'bank_holidays', '', {}, utc_datetime(2000, 1, 1), None,
        bank_holiday_rate_script)
    market_role_X = MarketRole.insert(sess, 'X', 'Supplier')
    market_role_M = MarketRole.insert(sess, 'M', 'Mop')
    market_role_C = MarketRole.insert(sess, 'C', 'HH Dc')
    market_role_R = MarketRole.insert(sess, 'R', 'Distributor')
    participant.insert_party(
        sess, market_role_M, 'Fusion Mop Ltd', utc_datetime(2000, 1, 1), None,
        None)
    participant.insert_party(
        sess, market_role_X, 'Fusion Ltc', utc_datetime(2000, 1, 1), None,
        None)
    participant.insert_party(
        sess, market_role_C, 'Fusion DC', utc_datetime(2000, 1, 1), None,
        None)
    mop_contract = Contract.insert_mop(
        sess, 'Fusion', participant, '', {}, utc_datetime(2000, 1, 1), None,
        {})
    dc_contract = Contract.insert_hhdc(
        sess, 'Fusion DC 2000', participant, '', {}, utc_datetime(2000, 1, 1),
        None, {})
    pc = Pc.insert(sess, '00', 'hh', utc_datetime(2000, 1, 1), None)
    insert_cops(sess)
    cop = Cop.get_by_code(sess, '5')
    imp_supplier_contract = Contract.insert_supplier(
        sess, 'Fusion Supplier 2000', participant, '', {},
        utc_datetime(2000, 1, 1), None, {})
    dno = participant.insert_party(
        sess, market_role_R, 'WPD', utc_datetime(2000, 1, 1), None, '22')
    meter_type = MeterType.insert(
        sess, 'C5', 'COP 1-5', utc_datetime(2000, 1, 1), None)
    meter_payment_type = MeterPaymentType.insert(
        sess, 'CR', 'Credit', utc_datetime(1996, 1, 1), None)
    Mtc.insert(
        sess, None, '845', 'HH COP5 And Above With Comms', False, False, True,
        meter_type, meter_payment_type, 0, utc_datetime(1996, 1, 1), None)
    insert_voltage_levels(sess)
    voltage_level = VoltageLevel.get_by_code(sess, 'HV')
    dno.insert_llfc(
        sess, '510', 'PC 5-8 & HH HV', voltage_level, False, True,
        utc_datetime(1996, 1, 1), None)
    dno.insert_llfc(
        sess, '521', 'Export (HV)', voltage_level, False, False,
        utc_datetime(1996, 1, 1), None)
    insert_sources(sess)
    source = Source.get_by_code(sess, 'net')
    gsp_group = GspGroup.insert(sess, '_L', 'South Western')
    site.insert_e_supply(
        sess, source, None, "Bob", utc_datetime(2000, 1, 1),
        None, gsp_group, mop_contract, '773', dc_contract, 'ghyy3', 'hgjeyhuw',
        pc, '845', cop, None, {}, '22 7867 6232 781', '510',
        imp_supplier_contract, '7748', 361, None, None, None, None, None)

    sess.commit()

    scenario_hh = {
        "CI017": {
          "generated": """
                2009-08-01 00:00, 40
                2009-08-15 00:00, 40"""
        }
    }

    era_maps = {
        utc_datetime(2000, 8, 1): {
            "llfcs": {
                "22": {
                    "new_export": "521"
                }
            },
            "supplier_contracts": {
                "new_export": 4
            }
        }
    }

    site_deltas = _make_site_deltas(
        sess, report_context, site, scenario_hh, forecast_from, supply_id)
    calcs, _, _ = _make_calcs(
        sess, site, start_date, finish_date, supply_id, site_deltas,
        forecast_from, report_context, era_maps)

    assert calcs[1][1] == 'CI017_extra_gen_TRUE'
    assert calcs[2][2] == 'CI017_extra_net_export'