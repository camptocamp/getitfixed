# -*- coding: utf-8 -*-

import logging
import smtplib

from email.mime.text import MIMEText
from email.header import Header


LOG = logging.getLogger(__name__)


def send_email(request, to, template_name, template_args=[], template_kwargs={}):
    """Send acknowledgment email to rpfe and requerant"""
    settings = request.registry.settings
    smtp = settings["smtp"]
    if not smtp:
        LOG.warning("Email cannot be sent as smtp service is not configured.")
        return False

    template = settings["emails"][request.localizer.locale_name][template_name]
    sender = template["email_from"]

    body = template["email_body"].format(template, *template_args, **template_kwargs)

    msg = MIMEText(body, _charset="UTF-8")
    msg["From"] = Header(sender)
    msg["To"] = Header(to)
    # msg['Bcc'] = Header(sender)
    msg["Subject"] = Header(template["email_subject"], "utf-8")

    # Connect to server
    smtp_host = smtp["host"]
    if "ssl" in smtp_host and smtp["ssl"]:
        server = smtplib.SMTP_SSL(smtp_host)
    else:
        server = smtplib.SMTP(smtp_host)
    if "user" in smtp and smtp["user"]:
        server.login(smtp["user"], smtp["password"])
    if "starttls" in smtp and smtp["starttls"]:
        server.starttls()

    # Send message
    server.sendmail(sender, [to, sender], msg.as_string())

    # Diconnect from server
    server.quit()

    return True
