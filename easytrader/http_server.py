import functools

from flask import Flask, jsonify, request

from . import api
from .log import logger

app = Flask(__name__)

user = None


def error_handle(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # pylint: disable=broad-except
        except Exception as e:
            logger.exception("server error")
            message = "{}: {}".format(e.__class__, e)
            return jsonify({"error": message}), 400

    return wrapper


def get_balance(req_data):
    result = user.balance
    return {
        'available_cash': result['可用金额'],
        'total_value': result['总资产']
    }


def get_position(req_data):
    result = user.position
    return {position['证券代码']: {
        'total_amount': position['股票余额'],
        'closeable_amount': position['可用余额'],
        'security': position['证券代码'],
        'price': position['市价']
    } for position in result
    }


def get_today_entrusts(req_data):
    result = user.today_entrusts
    return {
        'security': result['证券代码'],
        'add_time': result['委托时间'],
        'entrust_no': result['合同编号'],
        'price': result['委托价格'],
        'amount': result['委托数量'],
        'success_amount': result['成交数量'],
        'is_buy': result['操作'] == '买入'
    }


def get_today_trades(req_data):
    return user.today_trades


def get_cancel_entrusts(req_data):
    return user.cancel_entrusts


def do_buy(req_data):
    req_dict = {
        'security': data['security'],
        'price': data['price'],
        'amount': data['amount']
    }

    return user.buy(**req_dict)


def do_sell(req_data):
    req_dict = {
        'security': data['security'],
        'price': data['price'],
        'amount': data['amount']
    }

    return user.sell(**req_dict)


def do_cancel_entrust(req_data):
    return user.cancel_entrust(**req_data)


operation_handlers = {
    'balance': get_balance,
    'position': get_position,
    'today_entrusts': get_today_entrusts,
    'today_trades': get_today_trades,
    'cancel_entrusts': get_cancel_entrusts,
    'buy': do_buy,
    'sell': do_sell,
    'cancel_entrust': do_cancel_entrust
}


@app.route("/ops", methods=["POST"])
@error_handle
def handle_request():
    json_data = request.get_json(force=True)

    ops = json_data['operation']
    request_data = json_data.get('data', None)
    logger.info(f'{ops} <- {request_data}')
    if ops in operation_handlers:
        resp_data = operation_handlers[ops](request_data)
        logger.info(f'{ops} -> {resp_data}')
        return jsonify({'result': 'success', 'data': resp_data}), 200

    return jsonify({"error": 'Unknown Operation'}), 404


def run(client, cfg):
    global user
    user = client
    port = cfg['port']
    logger.info(f'starting http server at {port}')
    app.run(host="0.0.0.0", port=port)
