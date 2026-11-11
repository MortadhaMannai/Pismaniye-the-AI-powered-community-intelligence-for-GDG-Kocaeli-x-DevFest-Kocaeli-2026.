"""OpenTelemetry observability and trace span collection for PISMANIYE."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator
import uuid

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult


class InMemoryOtelExporter(SpanExporter):
    """Lightweight in-memory OpenTelemetry span collector for CLI & Web trace inspection."""

    def __init__(self) -> None:
        self.spans: list[dict[str, Any]] = []

    def export(self, spans: Any) -> SpanExportResult:
        for span in spans:
            self.spans.append(
                {
                    "name": span.name,
                    "trace_id": format(span.context.trace_id, "032x"),
                    "span_id": format(span.context.span_id, "016x"),
                    "attributes": dict(span.attributes or {}),
                    "start_time": span.start_time,
                    "end_time": span.end_time,
                }
            )
        if len(self.spans) > 500:
            self.spans = self.spans[-500:]
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        return None


class PismaniyeTelemetry:
    """OpenTelemetry tracer wrapper recording agent executions, tool calls, and RAG queries."""

    def __init__(self) -> None:
        self.exporter = InMemoryOtelExporter()
        resource = Resource.create(
            {
                "service.name": "pismaniye-multi-agent-platform",
                "service.version": "1.0.0",
                "community.owner": "gdg-kocaeli",
            }
        )
        self.provider = TracerProvider(resource=resource)
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer("pismaniye.orchestrator")

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[Any]:
        with self.tracer.start_as_current_span(name) as active_span:
            for k, v in attributes.items():
                if v is not None:
                    active_span.set_attribute(k, str(v))
            yield active_span

    def latest_otel_trace_id(self) -> str:
        if self.exporter.spans:
            return str(self.exporter.spans[-1]["trace_id"])
        return uuid.uuid4().hex


_telemetry: PismaniyeTelemetry | None = None


def get_telemetry() -> PismaniyeTelemetry:
    global _telemetry
    if _telemetry is None:
        _telemetry = PismaniyeTelemetry()
    return _telemetry
