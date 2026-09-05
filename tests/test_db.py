import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sweeper.db import (
    get_connection,
    upsert_message,
    list_senders,
    set_status
)


def fresh_conn():
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return get_connection(Path(f.name))


def test_insert_new_sender():
    conn = fresh_conn()

    upsert_message(
        conn,
        "a@x.com",
        "A",
        "one_click_post",
        "https://x.com/u",
        None,
        "d1"
    )

    assert list_senders(conn)[0]["message_count"] == 1


def test_count_goes_up():
    conn = fresh_conn()

    for _ in range(4):
        upsert_message(
            conn,
            "a@x.com",
            "A",
            "mailto",
            None,
            "mailto:b@x.com",
            "d"
        )

    assert list_senders(conn)[0]["message_count"] == 4


def test_method_upgrades_not_downgrades():
    conn = fresh_conn()

    upsert_message(
        conn,
        "a@x.com",
        "A",
        "mailto",
        None,
        "mailto:b@x.com",
        "d1"
    )

    upsert_message(
        conn,
        "a@x.com",
        "A",
        "one_click_post",
        "https://x.com/u",
        None,
        "d2"
    )

    assert list_senders(conn)[0]["unsub_method"] == "one_click_post"

    upsert_message(
        conn,
        "a@x.com",
        "A",
        "none",
        None,
        None,
        "d3"
    )

    assert list_senders(conn)[0]["unsub_method"] == "one_click_post"


def test_sorted_by_volume():
    conn = fresh_conn()

    upsert_message(
        conn,
        "quiet@x.com",
        "Q",
        "mailto",
        None,
        "mailto:b@x.com",
        "d"
    )

    for _ in range(5):
        upsert_message(
            conn,
            "loud@x.com",
            "L",
            "mailto",
            None,
            "mailto:b@x.com",
            "d"
        )

    assert list_senders(conn)[0]["email"] == "loud@x.com"


def test_status_change():
    conn = fresh_conn()

    upsert_message(
        conn,
        "a@x.com",
        "A",
        "mailto",
        None,
        "mailto:b@x.com",
        "d"
    )

    set_status(conn, "a@x.com", "ignored")

    assert list_senders(conn, status="ignored")[0]["email"] == "a@x.com"