import easytrader
import time
import json
import logging
import logging.handlers
import os
import sys
import datetime
from collections import defaultdict
import sched
import threading
import notification
import config


logger = logging.getLogger(__name__)


scheduler = sched.scheduler(time.time, time.sleep)


def restart_client(cfg, server):

    if server.client:
        logger.info('Restarting client ...')
        server.client.exit()
        time.sleep(60)
    logger.info('Starting client ...')
    client = easytrader.use(cfg['client'])
    client.prepare(user=cfg['user'], password=cfg['pass'], exe_path=cfg['exe_path'])
    server.client = client

    logger.info('Started client ...')
    time.sleep(15)
    # test the client
    client.position

    target = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(9, 2))
    scheduler.enterabs(target.timestamp(), 1, restart_client, argument=(cfg, server))


def run_scheduler():
    try:
        scheduler.run()
    except:
        logger.exception('Runner Error: ')
        message = traceback.format_exc()
        # notify('Quant Error', message)
        notification.sendMessage('Runner Error', 'error', {'err_message': message})


def main():
    config.configLogging()
    cfg = config.getConfig('runner')
    impl = cfg['impl']
    if impl == 'channel':
        import easytrader.channel_server as server
    elif impl == 'http':
        import easytrader.http_server as server
    else:
        logger.error(f'Unknown Impl {impl}')

    restart_client(cfg, server)

    threading.Thread(target=run_scheduler, daemon=True).start()
    server.run(cfg[impl])


if __name__ == '__main__':
    main()
