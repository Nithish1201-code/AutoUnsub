
import re
from types import SimpleNamespace
from email.utils import parseaddr

ANGLE_BRACKETS = re.compile(r"<([^>]+)>")

ONE_CLICK_POST = "one_click_post"
HTTPS_LINK = "https_link"
MAILTO = "mailto"
NONE = "none"


def make_target(method, https_url=None, mailto_url=None):
    return SimpleNamespace(
        method=method,
        https_url=https_url,
        mailto_url=mailto_url,
        is_actionable=method != NONE
    )


def parse_list_unsubscribe(hdr, one_click):
    if not hdr:
        return make_target(NONE)

    urls = ANGLE_BRACKETS.findall(hdr)

    if not urls:
        urls = hdr.split(",")

    https_url = None
    http_url = None
    mailto_url = None

    for url in urls:
        url = url.strip()

        if url.lower().startswith("https://") and not https_url:
            https_url = url
        elif url.lower().startswith("http://") and not http_url:
            http_url = url
        elif url.lower().startswith("mailto:") and not mailto_url:
            mailto_url = url

    if https_url and one_click:
        return make_target(ONE_CLICK_POST, https_url, mailto_url)

    if https_url or http_url:
        return make_target(HTTPS_LINK, https_url or http_url, mailto_url)

    if mailto_url:
        return make_target(MAILTO, mailto_url=mailto_url)

    return make_target(NONE)


def parse_mailto(url):
    from urllib.parse import unquote_plus

    value = url[len("mailto:"):]
    addr, _, query = value.partition("?")

    result = {
        "to": addr.strip(),
        "subject": "unsubscribe",
        "body": ""
    }

    if query:
        for item in query.split("&"):
            if "=" not in item:
                continue

            key, value = item.split("=", 1)

            if key.lower() == "subject":
                result["subject"] = unquote_plus(value)
            elif key.lower() == "body":
                result["body"] = unquote_plus(value)

    return result


def extract_sender(from_hdr):
    name, address = parseaddr(from_hdr or "")
    return name.strip(), address.strip().lower()