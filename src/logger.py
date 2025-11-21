"""
Logging utilities for trade signals and email notifications.
"""
import os
import smtplib
from email.message import EmailMessage
import pandas as pd

from . import config


def append_signal_log(row: dict):
    """
    Append a signal/trade to the CSV log file.

    Args:
        row: dictionary containing trade signal data
    """
    df = pd.DataFrame([row])
    header = not os.path.exists(config.SIGNAL_LOG_CSV)
    df.to_csv(config.SIGNAL_LOG_CSV, mode='a', header=header, index=False)


def send_email(subject, body):
    """
    Send email notification if email alerts are enabled.

    Args:
        subject: email subject line
        body: email body content
    """
    if not config.EMAIL_ALERT.get("enabled", False):
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_ALERT["from_addr"]
    msg["To"] = ", ".join(config.EMAIL_ALERT["to_addrs"])
    msg.set_content(body)

    try:
        with smtplib.SMTP(config.EMAIL_ALERT["smtp_server"], config.EMAIL_ALERT["smtp_port"]) as s:
            s.starttls()
            s.login(config.EMAIL_ALERT["username"], config.EMAIL_ALERT["password"])
            s.send_message(msg)
    except Exception as e:
        print("Failed to send email:", e)

