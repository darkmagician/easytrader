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

rootDir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger(__name__)


def configLogging():
    logDir = os.path.join(rootDir, 'log')
    if not os.path.exists(logDir):
        os.makedirs(logDir)
    consoleHandler = logging.StreamHandler(sys.stdout)
    fileHandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logDir, 'runner.log'), when='MIDNIGHT', encoding='utf8')
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.INFO, handlers=[consoleHandler, fileHandler])


def getConfig(configName):
    configPath = os.path.join(rootDir, 'config', configName + '.json')
    if os.path.exists(configPath):
        logger.info('Loading config file from {0}'.format(configPath))
        return defaultdict(str, json.load(open(configPath, 'r', encoding="utf8")))
    else:
        logger.warn('config file {0} is not found'.format(configPath))
        return None


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

    target = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), datetime.time(9, 2))
    scheduler.enterabs(target.timestamp(), 1, restart_client, argument=(cfg, server))


def run_scheduler():
    try:
        scheduler.run()
    except:
        logger.exception('Scheduler Error: ')


def main():
    configLogging()
    cfg = getConfig('runner')
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
