# -*- coding: utf-8 -*-

import logging
import smtplib

from email.mime.text import MIMEText
from email.header import Header


LOG = logging.getLogger(__name__)


def send_email(request, to, template_name, template_args=[], template_kwargs={}):
    '''Send acknowledgment email to rpfe and requerant'''
    settings = request.registry.settings
    import pprint
    LOG.error(pprint.pformat(settings, indent=4))
    smtp = settings['smtp']['host']
    if not smtp:
        return False

    template = settings[template_name]
    sender = template['email_from']
    logging.getLogger(__name__).error(pprint.pformat(template))

    body = template['email_body'].format(template, *template_args, **template_kwargs)

    msg = MIMEText(body, _charset="UTF-8")
    msg['From'] = Header(sender)
    msg['To'] = Header(to)
    #msg['Bcc'] = Header(sender)
    msg['Subject'] = Header(template['email_subject'], "utf-8")

    # Connect to server
    if 'ssl' in smtp and smtp['mail.ssl']:
        server = smtplib.SMTP_SSL(smtp)
    else:
        server = smtplib.SMTP(smtp)
    if 'user' in smtp and smtp['mail.user']:
        server.login(smtp['mail.user'], smtp['mail.password'])
    if 'starttls' in smtp and smtp['starttls']:
        server.starttls()

    # Send message
    server.sendmail(sender, [to, sender], msg.as_string())

    # Diconnect from server
    server.quit()

    return True