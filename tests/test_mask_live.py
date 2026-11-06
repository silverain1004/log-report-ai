import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))

import mask_live as ml  # noqa: E402


def _mask(text, deny=()):
    return ml.Masker(list(deny)).mask(text)


def test_ip_mapping_is_consistent_and_safe():
    m = ml.Masker([])
    out = m.mask("172.19.34.115 then 220.230.47.9 then 172.19.34.115")
    a, _, b, _, c = out.split(" ")
    assert a == c and a.startswith("10.20.")
    assert b.startswith("198.18.")
    assert ml.leaks(out, []) == []


def test_customer_domain_and_words():
    out = _mask('host: "vpn.seahbesteel.co.kr" referer https://inout.seahbesteel.co.kr/main seah')
    assert "seah" not in out.lower()
    assert "vpn.customer-1.example" in out and "inout.customer-1.example" in out
    assert ml.leaks(out, []) == []


def test_email_query_jwt_ids_paths():
    out = _mask(
        "me@vntgcorp.com GET /api/x?token=abcdef&amp;page=2 "
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.sig_part "
        "/users/1234567/info C:\\Users\\e_out\\Desktop /home/e_biz/key.pem"
    )
    assert "user1@example.com" in out
    assert "token=***" in out and "page=2" in out
    assert "eyJ" not in out
    assert "/users/{id}/info" in out
    assert "e_out" not in out and "e_biz" not in out
    assert ml.leaks(out, []) == []


def test_paths_are_not_mistaken_for_tokens():
    line = 'open() "/usr/share/nginx/html/api/v2/static/not.found" failed'
    assert _mask(line) == line


def test_extra_deny_words_and_leak_detection():
    out = _mask("operator kimchulsoo restarted WIN-PRODAPP01", deny=["kimchulsoo", "WIN-PRODAPP01"])
    assert "kimchulsoo" not in out and "PRODAPP01" not in out
    assert ml.leaks("10.1.2.3 a@b.com x.seahbesteel.co.kr", []) != []
