import functools

from flask import Flask, jsonify, request

from .utils import encrypt
from . import api
from .log import logger
import json

app = Flask(__name__)

user = None
txIdSeq = -1


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
    return [{
        'security': result['证券代码'],
        'add_time': result['委托时间'],
        'entrust_no': result['合同编号'],
        'price': result['委托价格'],
        'amount': result['委托数量'],
        'success_amount': result['成交数量'],
        'is_buy': result['操作'] == '买入'
    } for result in user.today_entrusts]


def get_today_trades(req_data):
    return user.today_trades


def get_cancel_entrusts(req_data):
    return user.cancel_entrusts


def do_buy(req_data):
    req_dict = {
        'security': req_data['security'],
        'price': req_data['price'],
        'amount': req_data['amount']
    }

    return user.buy(**req_dict)


def do_sell(req_data):
    req_dict = {
        'security': req_data['security'],
        'price': req_data['price'],
        'amount': req_data['amount']
    }

    return user.sell(**req_dict)


def do_cancel_entrust(req_data):
    return user.cancel_entrust(**req_data)


def get_txId(req_data):
    global txIdSeq
    return txIdSeq


operation_handlers = {
    'balance': get_balance,
    'position': get_position,
    'today_entrusts': get_today_entrusts,
    'today_trades': get_today_trades,
    'cancel_entrusts': get_cancel_entrusts,
    'buy': do_buy,
    'sell': do_sell,
    'cancel_entrust': do_cancel_entrust,
    'txId': get_txId
}


def onRequest(req_body):
    global txIdSeq
    if txIdSeq >= 0:
        val = encrypt.decrypt(req_body['payload'])
       # print(val)
        val = json.loads(val)
        ops = val['operation']
        if ops == 'txId':
            return val
        txId = val['txId']
        if txId > txIdSeq and txId < txIdSeq + 16:
            txIdSeq = txId
        else:
            raise Exception("Out of TxId")
        return val
    return req_body


def onResponse(resp_body):
    global txIdSeq
    if txIdSeq >= 0:
        val = encrypt.encrypt(json.dumps(resp_body))
        return {'payload': val}
    return resp_body


@app.route("/ops", methods=["POST"])
@error_handle
def handle_request():
    json_data = onRequest(request.get_json(force=True))

    ops = json_data['operation']
    request_data = json_data.get('data', None)
    if ops in operation_handlers:
        logger.info(f'{ops} <- {request_data}')
        resp_data = operation_handlers[ops](request_data)
        logger.info(f'{ops} -> {resp_data}')
        return jsonify(onResponse({'result': 'success', 'data': resp_data})), 200
    logger.info(f'Unknown Operation {ops}')
    return jsonify({"error": 'Unknown Operation'}), 404


def run(client, cfg):
    global user
    global txIdSeq

    user = client
    port = cfg['port']
    key = cfg.get('enc_key', None)
    if key:
        logger.info('encryption is enabled.')

        encrypt.init_cipher(key)
        import random
        txIdSeq = random.randint(0, 1000000)

    logger.info(f'starting http server at {port}')
    app.run(host="0.0.0.0", port=port)
