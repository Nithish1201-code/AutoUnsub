from sweeper.db import (
    get_connection,
    get_sender,
    list_actionable,
    list_senders,
    upsert_message
)


def make_db():
    return get_connection(":memory:")


def test_list_senders():
    db = make_db()

    upsert_message(
        db,
        "alice@example.com",
        "Alice",
        "https_link",
        "https://example.com/unsub",
        None,
        "2026-09-01T00:00:00+00:00"
    )

    upsert_message(
        db,
        "bob@example.com",
        "Bob",
        "none",
        None,
        None,
        "2026-09-01T00:00:00+00:00"
    )

    rows = list_senders(db)

    assert len(rows) == 2
    assert rows[0]["email"] == "alice@example.com"


def test_get_sender():
    db = make_db()

    upsert_message(
        db,
        "alice@example.com",
        "Alice",
        "mailto",
        None,
        "mailto:unsubscribe@example.com",
        "2026-09-01T00:00:00+00:00"
    )

    row = get_sender(
        db,
        "alice@example.com"
    )

    assert row["email"] == "alice@example.com"
    assert row["display_name"] == "Alice"
    assert row["unsub_method"] == "mailto"


def test_list_actionable():
    db = make_db()

    upsert_message(
        db,
        "alice@example.com",
        "Alice",
        "https_link",
        "https://example.com/unsub",
        None,
        "2026-09-01T00:00:00+00:00"
    )

    upsert_message(
        db,
        "bob@example.com",
        "Bob",
        "none",
        None,
        None,
        "2026-09-01T00:00:00+00:00"
    )

    rows = list_actionable(db)

    assert len(rows) == 1
    assert rows[0]["email"] == "alice@example.com"