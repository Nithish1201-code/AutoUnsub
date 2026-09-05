from sweeper import imap_scan


class FakeConnection:
    def select(self, mailbox, readonly=True):
        return "OK", [b""]

    def search(self, charset, query):
        return "OK", [b"1 2"]

    def fetch(self, message_id, query):
        messages = {
            b"1": b"From: Alice <alice@example.com>\r\n"
                  b"Date: Mon, 01 Sep 2026 10:00:00 +0000\r\n"
                  b"List-Unsubscribe: <https://example.com/unsub>\r\n\r\n",

            b"2": b"From: Bob <bob@example.com>\r\n"
                  b"Date: Tue, 02 Sep 2026 10:00:00 +0000\r\n"
                  b"List-Unsubscribe: <mailto:unsubscribe@example.com>\r\n\r\n"
        }

        return "OK", [(b"header", messages[message_id])]


def test_scan_inbox(monkeypatch):
    monkeypatch.setattr(
        imap_scan,
        "extract_sender",
        lambda from_hdr: (
            from_hdr.split(" <")[0],
            from_hdr.split("<")[1].rstrip(">")
        )
    )

    monkeypatch.setattr(
        imap_scan,
        "parse_list_unsubscribe",
        lambda header, post=None: type(
            "Unsub",
            (),
            {
                "method": "https_link" if header.startswith("<https") else "mailto",
                "https_url": (
                    header.strip("<>")
                    if header.startswith("<https")
                    else None
                ),
                "mailto_url": (
                    header.strip("<>")
                    if header.startswith("<mailto")
                    else None
                )
            }
        )()
    )

    results = imap_scan.scan_inbox(FakeConnection())

    assert len(results) == 2
    assert results[0]["email"] == "alice@example.com"
    assert results[0]["method"] == "https_link"
    assert results[1]["email"] == "bob@example.com"
    assert results[1]["method"] == "mailto"