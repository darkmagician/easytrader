import json
import logging
import datetime
import time
import os

logger = logging.getLogger(__name__)
rootDir = os.path.abspath('./queues')

event_dir = 'events'


def initRoot(root):
    global rootDir
    rootDir = os.path.abspath(root)


def call(channel, event_id, data):
    event = {
        'timestamp': str(datetime.datetime.now()),
        'channel': channel,
        'data': data
    }
    logger.info(f'Sending event to {channel}/{event_id}: {event}')
    saveFile(event_dir, event_id, event)
    resp_file = os.path.join(rootDir, channel, event_id + '.json')
    logger.info(f'waiting for response event at  {resp_file}')
    for i in range(100):
        time.sleep(1)
        logger.info(f'checking {resp_file}')
        if os.path.exists(resp_file):
            time.sleep(1)
            resp = json.load(open(resp_file, 'r'))
            logger.info(f'Receiving reponse event from {resp_file}, {resp}')
            return resp
    logger.warn(f'No response is received at {resp_file}')
    return None


def saveFile(dir, name, content):
    parentDir = os.path.join(rootDir, dir)
    if not os.path.exists(parentDir):
        os.makedirs(parentDir)
    filepath = os.path.join(parentDir, name + '.json')
    logger.debug('writing json file to {}'.format(filepath))
    with open(filepath, "w") as write_file:
        json.dump(content, write_file)


observer = None


def startHandlers(handlers):
    from watchdog.observers import Observer
    from watchdog.events import PatternMatchingEventHandler

    class QueueHandler(PatternMatchingEventHandler):
        def __init__(self):
            super().__init__(patterns=["*.json"], ignore_directories=True)

        def on_created(self, event):
            fname = event.src_path
            time.sleep(1)
            event = json.load(open(fname, 'r'))
            channel = event['channel']
            logger.info(f'Receiving {channel} event from {fname}: {event} ')

            if channel in handlers:
                resp_data = handlers[channel](event['data'])
                resp = {
                    'timestamp': str(datetime.datetime.now()),
                    'response_to': event,
                    'data': resp_data
                }
                name = os.path.splitext(os.path.basename(fname))[0]
                saveFile(channel, name, resp)
                logger.info(f'Sending {channel} response for {name}: {resp} ')
                os.remove(fname)
            else:
                logger.error(f'No handler support {channel} event')
            # print(f'event type: {event.event_type}  path : {event.src_path}')

    stop()

    event_handler = QueueHandler()
    observer = Observer()
    eventPath = os.path.join(rootDir, event_dir)
    if not os.path.exists(eventPath):
        os.makedirs(eventPath)
    observer.schedule(event_handler, path=eventPath, recursive=False)
    observer.start()
    # observer.join()


def stop():
    if observer:
        observer.stop()


def join():
    if observer:
        observer.join()


def main():
    startHandlers({'orders': lambda x: {'resp': 12}})
    join()


def main2():
    call('orders', datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), {'haha': 121})


if __name__ == '__main__':
    main2()
