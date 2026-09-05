import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .unsub_parse import parse_mailto


USER_AGENT = "AutoUnsub/0.1"
TIMEOUT = 15


def _request(url, method="GET", data=None):
    if not url:
        raise ValueError("missing unsubscribe url")

    if not url.lower().startswith(("http://", "https://")):
        raise ValueError("unsupported unsubscribe url")

    body = None
    headers = {
        "User-Agent": USER_AGENT
    }

    if data is not None:
        body = urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    request = Request(
        url,
        data=body,
        headers=headers,
        method=method
    )

    with urlopen(request, timeout=TIMEOUT) as response:
        return response.status, response.geturl()


def unsubscribe_http(method, url):
    if method == "one_click_post":
        return _request(
            url,
            method="POST",
            data={
                "List-Unsubscribe": "One-Click"
            }
        )

    if method == "https_link":
        return _request(url)

    raise ValueError("unsupported http unsubscribe method")


def unsubscribe_mailto(url, address, app_password):
    target = parse_mailto(url)

    if not target["to"]:
        raise ValueError("missing mailto recipient")

    message = EmailMessage()
    message["From"] = address
    message["To"] = target["to"]
    message["Subject"] = target["subject"]
    message.set_content(target["body"])

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        timeout=TIMEOUT
    ) as smtp:
        smtp.login(address, app_password)
        smtp.send_message(message)


def unsubscribe(
    method,
    https_url=None,
    mailto_url=None,
    address=None,
    app_password=None
):
    if method in ("one_click_post", "https_link"):
        return unsubscribe_http(
            method,
            https_url
        )

    if method == "mailto":
        if not address or not app_password:
            raise ValueError("gmail credentials required for mailto")

        unsubscribe_mailto(
            mailto_url,
            address,
            app_password
        )

        return 250, mailto_url

    raise ValueError("no supported unsubscribe method")