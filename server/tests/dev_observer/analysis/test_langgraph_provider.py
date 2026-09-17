from langfuse import Langfuse
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from dev_observer.analysis.langgraph_provider import _use_langfuse_session


def test_langfuse_session_is_propagated_to_spans() -> None:
    exporter = InMemorySpanExporter()
    client = Langfuse(
        public_key="pk-lf-contextify-test",
        secret_key="sk-lf-contextify-test",
        base_url="http://127.0.0.1:1",
        span_exporter=exporter,
    )

    with _use_langfuse_session("contextify-test-session"):
        with client.start_as_current_observation(name="analysis"):
            pass
    client.flush()

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["session.id"] == "contextify-test-session"
