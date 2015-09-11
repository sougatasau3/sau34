from net.sf.chellow.monad import Monad
import utils
import db
from collections import defaultdict
Monad.getUtils()['impt'](globals(), 'db', 'utils')
UserException = utils.UserException
Contract, RateScript = db.Contract, db.RateScript


def make_create_future_func_simple(contract_name, fnames):
    def create_future_func_simple(multiplier, constant):
        def future_func(ns):
            new_ns = {}
            for fname in fnames:
                try:
                    val = ns[fname]() * multiplier + constant
                except KeyError:
                    raise UserException(
                        "Can't find " + fname + " in rate script " + str(ns) +
                        " for contract name " + contract_name + " .")

                def rate_func():
                    return val

                new_ns[fname] = rate_func
            return new_ns
        return future_func
    return create_future_func_simple


def make_create_future_func_monthly(contract_name, fnames):
    def create_future_func_monthly(multiplier, constant):

        def future_func(ns):
            new_ns = {}
            for fname in fnames:
                old_result = ns[fname]()
                last_value = old_result[sorted(old_result.keys())[-1]]
                new_result = defaultdict(
                    lambda: last_value, [
                        (k, v * multiplier + constant)
                        for k, v in old_result.iteritems()])

                def rate_func():
                    return new_result

                new_ns[fname] = rate_func
            return new_ns
        return future_func
    return create_future_func_monthly