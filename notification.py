import logging
import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import config


logger = logging.getLogger(__name__)

notify_cfg = config.getConfig('notification')


if notify_cfg:
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(autoescape=select_autoescape(['html', 'htm', 'xml']),
                      loader=PackageLoader('notification', 'templates'))
    notify_type = notify_cfg['type']
    logger.info(f'Notification is enabled with {notify_type}')


def sendMessage(subject, templateName, message_ctx):
    try:
        if notify_cfg:
            body, bodyType = createBody(templateName, message_ctx)
            if body is None:
                logger.info(f'{templateName} is not found for notification')
                return

            if notify_type == 'smtp':
                useSMTP(subject, body, bodyType)
            elif notify_type == 'http':
                useHttpHook(subject, body, bodyType)
            else:
                logger.error(f'unknown notification type {notify_type}')

        else:
            logger.info('No notification config is avaiable')
    except:
        logger.exception('Notification Error: ')
        return


def createBody(templateName, message_ctx):
    availables = env.list_templates()
    for file in availables:
        name, ext = file.split('.')
        if name == templateName:
            template = env.get_template(file)
            return template.render(**message_ctx), ext
    return None, None


def useHttpHook(subject, body, bodyType):
    cfg = notify_cfg['http']
    r = requests.post(cfg['hook'], data={'text': subject, 'desp': body})
    logger.info('HTTP Hook Resp ' + r.text)


def useSMTP(subject, body, bodyType):
    cfg = notify_cfg['smtp']

    mailTo = cfg['to']
    logger.info(f'Sending Notification using smtp for {subject}')

    mailFrom = cfg['from']
    smtpServer = cfg['server']

    user = cfg['user']
    password = cfg['pass']

    mineType = 'html' if bodyType == 'html' else 'plain'

    message = MIMEText(body, mineType, 'utf-8')
    message['From'] = config.getQuantName('quant') + '<' + mailFrom + '>'
    message['To'] = mailTo + '<' + mailTo + '>'
    message['Subject'] = Header(subject, 'utf-8').encode()
    if cfg['ssl']:
        smtp = smtplib.SMTP_SSL(smtpServer)
    else:
        smtp = smtplib.SMTP(smtpServer)
    smtp.login(user, password)
    smtp.sendmail(mailFrom, mailTo, message.as_string())
    smtp.close()


if __name__ == '__main__':
    print(f'==== {env.list_templates()}')
    body, btype = createBody('hello', {'aaa': 1})
    print(f'==== {btype}  {body}')

    sendMessage('test', 'hello', {'aaa': 1})
