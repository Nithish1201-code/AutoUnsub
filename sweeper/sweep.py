from .config import load_credentials
from .db import add_message, get_connection, get_stats, upsert_message
from .imap_scan import connect, scan_inbox


def run(days=30, limit=None, credentials=None):
    if credentials is None:
        credentials = load_credentials()

    conn = connect(
        credentials["address"],
        credentials["app_password"]
    )

    if not conn:
        return False

    db = get_connection()

    try:
        results = scan_inbox(
            conn,
            days=days,
            limit=limit
        )

        new_messages = 0

        for result in results:
            is_new = add_message(
                db,
                result["message_id"],
                result["email"],
                result["seen_at"]
            )

            if not is_new:
                continue

            upsert_message(
                db,
                result["email"],
                result["name"],
                result["method"],
                result["https_url"],
                result["mailto_url"],
                result["seen_at"]
            )

            new_messages += 1

        stats = get_stats(db)

        print()
        print(f"scanned {len(results)} messages")
        print(f"new messages {new_messages}")
        print()

        for status, values in stats.items():
            print(
                f"{status}: "
                f"{values['senders']} senders, "
                f"{values['messages']} messages"
            )

        return True

    finally:
        db.close()
        conn.logout()