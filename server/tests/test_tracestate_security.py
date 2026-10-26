"""Regression coverage for untrusted OpenTelemetry propagation headers."""

import subprocess
import sys


def test_tracestate_rejects_oversized_headers_without_quadratic_parsing():
    # Isolate the parser so a vulnerable version cannot hang the test worker.
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            """
from opentelemetry.trace import TraceState
for whitespace in (" ", "\\t"):
    assert len(TraceState.from_header(["a=b" + whitespace * 200_000 + "x"])) == 0
assert dict(TraceState.from_header(["vendor=value,other=second"]).items()) == {
    "vendor": "value", "other": "second"
}
""",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode == 0, result.stderr
