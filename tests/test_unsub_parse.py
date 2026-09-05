import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sweeper.unsub_parse import ONE_CLICK_POST, HTTPS_LINK, MAILTO, extract_sender, parse_list_unsubscribe, parse_mailto

def test_one_click():
    t = parse_list_unsubscribe("<https://x.com/u?id=1>", True)
    assert t.method == ONE_CLICK_POST

def test_prefers_one_click_when_both_present():
    t = parse_list_unsubscribe("<https://x.com/u>, <mailto:bye@x.com>", True)
    assert t.method == ONE_CLICK_POST
    assert t.mailto_url == "mailto:bye@x.com"

def test_https_no_post_header_is_link_only():
    t = parse_list_unsubscribe("<https://x.com/u>", False)
    assert t.method == HTTPS_LINK

def test_mailto_only():
    t = parse_list_unsubscribe("<mailto:bye@x.com>", False)
    assert t.method == MAILTO

def test_nothing():
    t = parse_list_unsubscribe(None, False)
    assert not t.is_actionable

def test_no_angle_brackets():
    t = parse_list_unsubscribe("https://x.com/u", False)
    assert t.https_url == "https://x.com/u"

def test_mailto_fields():
    f = parse_mailto("mailto:bye@x.com?subject=Unsub%20me&body=please")
    assert f["to"] == "bye@x.com"
    assert f["subject"] == "Unsub me"

def test_extract_sender():
    name, addr = extract_sender('"Some Newsletter" <news@x.com>')
    assert name == "Some Newsletter"
    assert addr == "news@x.com"