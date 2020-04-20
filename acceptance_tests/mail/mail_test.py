import email
import pytest
from unittest.mock import MagicMock, patch

from getitfixed.emails.email_service import send_email


TEST_EMAIL_CONFIG = {
        "email_from": "sender@example.com",
        "email_subject": "This is a test email",
        "email_body": """
Hello {username},

This is a test email.

Best

Get It Fixed Team"""
}


@pytest.fixture(scope="function")
def smtp_mock():
    with patch("getitfixed.emails.email_service.smtplib.SMTP") as SMTP:
        yield SMTP


@pytest.mark.usefixtures("app_env")
@pytest.mark.usefixtures("smtp_mock")
def test_send_email(app_env, smtp_mock):
    app_env.get("registry").settings["getitfixed"]["test_email"] = TEST_EMAIL_CONFIG
    request = app_env["request"]

    send_email(request,
               "user@example.com",
               "test_email",
               template_args=[],
               template_kwargs={"username": "Username"}
    )

    smtp = smtp_mock.return_value
    smtp.sendmail.assert_called_once()
    kall = smtp.sendmail.call_args[0]
    assert kall[0] == 'sender@example.com'
    assert kall[1] == ['user@example.com', 'sender@example.com']
    assert (
        email.message_from_string(kall[2]).get_payload(decode=True).decode("utf8")
        == TEST_EMAIL_CONFIG["email_body"].format(username="Username")
    )
