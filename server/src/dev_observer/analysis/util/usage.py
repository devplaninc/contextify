from typing import Optional, List

from langchain_core.messages import BaseMessage, AIMessage

from dev_observer.api.types.ai_pb2 import UsageMetadata


def extract_usage(msg: BaseMessage) -> UsageMetadata:
    if not isinstance(msg, AIMessage):
        return UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)
    md = msg.usage_metadata
    if not md:
        return UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)
    return UsageMetadata(
        input_tokens=md.get("input_tokens", 0),
        output_tokens=md.get("output_tokens", 0),
        total_tokens=md.get("total_tokens", 0)
    )


def sum_all(usages: List[Optional[UsageMetadata]]) -> UsageMetadata:
    result = UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)
    for usage in usages:
        result = sum_usage(result, usage)
    return result

def sum_usage(left: Optional[UsageMetadata], right: Optional[UsageMetadata]) -> UsageMetadata:
    if left is None and right is None:
        return UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)
    if left is None:
        return UsageMetadata(
            input_tokens=right.input_tokens,
            output_tokens=right.output_tokens,
            total_tokens=right.total_tokens
        )
    if right is None:
        return UsageMetadata(
            input_tokens=left.input_tokens,
            output_tokens=left.output_tokens,
            total_tokens=left.total_tokens
        )
    return UsageMetadata(
        input_tokens=left.input_tokens + right.input_tokens,
        output_tokens=left.output_tokens + right.output_tokens,
        total_tokens=left.total_tokens + right.total_tokens
    )
