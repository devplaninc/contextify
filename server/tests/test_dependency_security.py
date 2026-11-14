"""Exercise upstream dependency security fixes with real parsers."""

import dns.exception
import dns.rdata
import pytest
from twisted.mail.imap4 import wildcardToRegexp


@pytest.mark.parametrize("service", [-1, 65536])
def test_wks_rejects_out_of_range_service_numbers(service):
    # Use bounded inputs: a vulnerable parser accepts 65536 without a huge allocation.
    with pytest.raises(dns.exception.SyntaxError):
        dns.rdata.from_text("IN", "WKS", f"10.0.0.1 udp {service}")


@pytest.mark.parametrize("service", [0, 53, 65535])
def test_wks_preserves_valid_service_numbers(service):
    record = dns.rdata.from_text("IN", "WKS", f"10.0.0.1 udp {service}")
    assert record.bitmap[service // 8] & (0x80 >> (service % 8))
    assert dns.rdata.from_wire("IN", "WKS", record.to_wire(), 0, len(record.to_wire())) == record


@pytest.mark.parametrize("delimiter", [None, "/"])
def test_imap_patterns_treat_regex_syntax_literally(delimiter):
    pattern = "(a+)+z"
    expression = wildcardToRegexp(pattern, delimiter)
    # Check literal handling before attempting the advisory's backtracking input.
    assert expression.fullmatch(pattern)
    assert expression.fullmatch("a" * 28) is None


@pytest.mark.parametrize(
    ("pattern", "mailbox", "matches"),
    [
        ("INBOX/*", "inbox/folder/child", True),
        ("INBOX/%", "inbox/folder", True),
        ("INBOX/%", "inbox/folder/child", False),
        ("INBOX/a.b", "inbox/a.b", True),
        ("INBOX/a.b", "inbox/axb", False),
    ],
)
def test_imap_wildcards_preserve_mailbox_matching(pattern, mailbox, matches):
    assert (wildcardToRegexp(pattern, "/").fullmatch(mailbox) is not None) == matches
