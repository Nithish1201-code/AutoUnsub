from sweeper import unsubscribe


def test_one_click_post(monkeypatch):
    called = {}

    class Response:
        status = 200

        def geturl(self):
            return "https://example.com/unsub"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(request, timeout):
        called["method"] = request.method
        called["url"] = request.full_url
        called["body"] = request.data

        return Response()

    monkeypatch.setattr(
        unsubscribe,
        "urlopen",
        fake_urlopen
    )

    status, url = unsubscribe.unsubscribe(
        "one_click_post",
        https_url="https://example.com/unsub"
    )

    assert status == 200
    assert url == "https://example.com/unsub"
    assert called["method"] == "POST"
    assert called["url"] == "https://example.com/unsub"
    assert b"List-Unsubscribe=One-Click" in called["body"]


def test_https_link(monkeypatch):
    called = {}

    class Response:
        status = 200

        def geturl(self):
            return "https://example.com/unsub"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(request, timeout):
        called["method"] = request.method
        called["url"] = request.full_url
        return Response()

    monkeypatch.setattr(
        unsubscribe,
        "urlopen",
        fake_urlopen
    )

    status, url = unsubscribe.unsubscribe(
        "https_link",
        https_url="https://example.com/unsub"
    )

    assert status == 200
    assert url == "https://example.com/unsub"
    assert called["method"] == "GET"


def test_mailto(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["host"] = host
            sent["port"] = port

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def login(self, address, password):
            sent["address"] = address
            sent["password"] = password

        def send_message(self, message):
            sent["message"] = message

    monkeypatch.setattr(
        unsubscribe.smtplib,
        "SMTP_SSL",
        FakeSMTP
    )

    status, url = unsubscribe.unsubscribe(
        "mailto",
        mailto_url="mailto:unsubscribe@example.com?subject=Unsubscribe",
        address="me@example.com",
        app_password="test-password"
    )

    assert status == 250
    assert url.startswith("mailto:")
    assert sent["host"] == "smtp.gmail.com"
    assert sent["port"] == 465
    assert sent["address"] == "me@example.com"
    assert sent["password"] == "test-password"
    assert sent["message"]["To"] == "unsubscribe@example.com"
    assert sent["message"]["Subject"] == "Unsubscribe"