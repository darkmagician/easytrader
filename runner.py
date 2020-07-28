import easytrader
import time
import json
import logging
import logging.handlers
import os
import sys
from collections import defaultdict


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


def main():
    configLogging()
    cfg = getConfig('runner')
    client = easytrader.use(cfg['client'])
    client.prepare(user=cfg['user'], password=cfg['pass'], exe_path=cfg['exe_path'])
    # print('balance: ' + str(client.balance))
    # time.sleep(10)
    # print('position: ' + str(client.position))
    impl = cfg['impl']
    if impl == 'channel':
        import easytrader.channel_server as server
        server.run(client, cfg['channel'])
    elif impl == 'http':
        import easytrader.http_server as server
        server.run(client, cfg['http'])
    else:
        logger.error(f'Unknown Impl {impl}')


if __name__ == '__main__':
    main()
