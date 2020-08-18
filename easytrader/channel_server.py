import easytrader.channel_communication as channel
import logging
import time
logger = logging.getLogger(__name__)


client = None


def onOrderEvent(data):
    global client

    is_buy = data['is_buy']
    security = data['security']
    price = data['price']
    amount = data['amount']
    order_id = data['order_id']

    if is_buy:
        logger.info(f'Buying {security} at {price} with amount {amount} for order {order_id}')
        result = client.buy(security, price, amount)
    else:
        logger.info(f'Selling {security} at {price} with amount {amount}')
        result = client.sell(security, price, amount)
    logger.info(f'Order Result: {result}')
    entrust_no = result['entrust_no']

    timeout = 300
    interval = 5
    while True:
        time.sleep(interval)
        timeout -= interval
        today_entrusts = client.today_entrusts
        entrust = next((x for x in today_entrusts if x['合同编号'] == entrust_no), None)
        if entrust:
            if entrust['委托数量'] == entrust['成交数量']:
                logger.info(f'entrust {entrust_no} is done for order {order_id}')
                return {
                    'security': entrust['证券代码'],
                    'add_time': entrust['委托时间'],
                    'entrust_no': entrust['合同编号'],
                    'price': entrust['委托价格'],
                    'amount': entrust['委托数量'],
                    'success_amount': entrust['成交数量'],
                    'is_buy': is_buy
                }
        if timeout < 0:
            logger.info(f'entrust {entrust_no} is timeout for order {order_id}')
            if entrust:
                return {
                    'security': entrust['证券代码'],
                    'add_time': entrust['委托时间'],
                    'entrust_no': entrust['合同编号'],
                    'price': entrust['委托价格'],
                    'amount': entrust['委托数量'],
                    'success_amount': entrust['成交数量'],
                    'is_buy': is_buy
                }
            else:
                return {}


def onPortfolioEvent(data):
    global client

    balance = client.balance
    logger.info(f'Get balance {balance}')
    positions = client.position
    logger.info(f'Get positions {positions}')

    resp = {}
    resp['available_cash'] = balance['可用金额']
    resp['total_value'] = balance['总资产']
   # resp['account_id'] = balance['资金帐号']

    positions_dict = {}
    for position in positions:
        security = position['证券代码']
        positions_dict[security] = {
            'total_amount': position['股票余额'],
            'closeable_amount': position['可用余额'],
            'security': security,
            'price': position['市价']
        }
    resp['positions'] = positions_dict
    return resp


def run(cfg):
    channel.initRoot(cfg['event_storage'])
    channel.startHandlers({'orders': lambda x: onOrderEvent(x),
                           'portfolio': lambda x: onPortfolioEvent(x)})
    try:
        while True:
            time.sleep(300)
    except:
        channel.stop()

    channel.join()
