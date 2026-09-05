import email
import imaplib
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

from .unsub_parse import extract_sender, parse_list_unsubscribe


IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
HEADERS_WE_WANT = "FROM SUBJECT DATE LIST-UNSUBSCRIBE LIST-UNSUBSCRIBE-POST"


def connect(address, app_password):
    conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)

    try:
        conn.login(address, app_password)
    except imaplib.IMAP4.error:
        print("login failed")
        conn.logout()
        return None

    return conn


def _get_header_data(data):
    if not data:
        return None

    for item in data:
        if isinstance(item, tuple) and len(item) > 1:
            if isinstance(item[1], bytes):
                return item[1]

    return None


def _get_seen_at(message):
    date = message.get("Date")

    if not date:
        return datetime.now(timezone.utc).isoformat()

    try:
        value = parsedate_to_datetime(date)

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        return datetime.now(timezone.utc).isoformat()


def scan_inbox(conn, days=30, mailbox="INBOX", limit=None):
    status, _ = conn.select(mailbox, readonly=True)

    if status != "OK":
        return []

    since = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).strftime("%d-%b-%Y")

    status, data = conn.search(None, f"SINCE {since}")

    if status != "OK" or not data or not data[0]:
        return []

    ids = data[0].split()

    if limit:
        ids = ids[-limit:]

    results = []

    for message_id in ids:
        status, data = conn.fetch(
            message_id,
            f"(BODY.PEEK[HEADER.FIELDS ({HEADERS_WE_WANT})])"
        )

        if status != "OK":
            continue

        raw = _get_header_data(data)

        if not raw:
            continue

        message = email.message_from_bytes(raw)

        sender_name, sender_email = extract_sender(
            message.get("From")
        )

        unsub = parse_list_unsubscribe(
            message.get("List-Unsubscribe"),
            message.get("List-Unsubscribe-Post")
        )

        results.append({
            "email": sender_email,
            "name": sender_name,
            "method": unsub.method,
            "https_url": unsub.https_url,
            "mailto_url": unsub.mailto_url,
            "seen_at": _get_seen_at(message)
        })

    return results