"""Exercise the upstream Twisted IMAP fix while it is pinned to a release candidate."""

import pytest
from twisted.mail.imap4 import wildcardToRegexp


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
