import unittest

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from dev_observer.analysis.util.models import chunk_messages, clean_tools, truncate_tool_msg
from dev_observer.tokenizer.tiktoken import TiktokenTokenizerProvider


class TestChunkMessages(unittest.TestCase):
    """Test cases for the _chunk_messages static method in CodeResearchNodes."""

    def setUp(self):
        """Set up test fixtures."""
        self.tokenizer = TiktokenTokenizerProvider(encoding="cl100k_base")

    def test_empty_messages_list(self):
        """Test that empty messages list returns empty chunks."""
        result = chunk_messages([], self.tokenizer)
        self.assertEqual(result, [])

    def test_single_message_under_limit(self):
        """Test chunking with a single message under token limit."""
        messages = [HumanMessage(content="Hello world!")]
        messages[0].response_metadata = {"iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 1)
        self.assertEqual(chunks[0][0].content, "Hello world!")

    def test_multiple_messages_same_iteration_under_limit(self):
        """Test multiple messages from same iteration that fit in one chunk."""
        messages = [
            HumanMessage(content="Message 1"),
            AIMessage(content="Response 1"),
            ToolMessage(content="Tool result 1", tool_call_id="test1")
        ]

        for msg in messages:
            msg.response_metadata = {"iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 3)

    def test_iteration_boundary_splitting_with_token_limit(self):
        """Test that messages are split at iteration boundaries when token limit is exceeded."""
        # Create messages with large content to exceed token limits
        large_content = "This is large content that will cause token limits to be exceeded. " * 200

        messages = [
            HumanMessage(content=large_content),
            AIMessage(content=large_content),
            HumanMessage(content=large_content),
            AIMessage(content=large_content),
        ]

        messages[0].response_metadata = {"iteration": 1}
        messages[1].response_metadata = {"iteration": 1}
        messages[2].response_metadata = {"iteration": 2}
        messages[3].response_metadata = {"iteration": 2}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=1000)

        # Should split when token limit is exceeded at iteration boundary
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0]), 2)  # First iteration
        self.assertEqual(len(chunks[1]), 2)  # Second iteration

        # Verify iteration integrity
        self.assertEqual(chunks[0][0].response_metadata["iteration"], 1)
        self.assertEqual(chunks[0][1].response_metadata["iteration"], 1)
        self.assertEqual(chunks[1][0].response_metadata["iteration"], 2)
        self.assertEqual(chunks[1][1].response_metadata["iteration"], 2)

    def test_token_limit_exceeded_within_iteration(self):
        """Test behavior when token limit is exceeded within an iteration."""
        # Create large content that will exceed token limits
        large_content = "This is a very large message content. " * 1000

        messages = [
            HumanMessage(content="Small message"),
            AIMessage(content=large_content),
            ToolMessage(content=large_content, tool_call_id="test1"),
            HumanMessage(content="Next iteration message")
        ]

        messages[0].response_metadata = {"iteration": 1}
        messages[1].response_metadata = {"iteration": 1}
        messages[2].response_metadata = {"iteration": 1}
        messages[3].response_metadata = {"iteration": 2}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=1000)

        # Should split at iteration boundary even if within iteration exceeds limit
        self.assertEqual(len(chunks), 2)

        # First chunk should have all iteration 1 messages despite exceeding token limit
        self.assertEqual(len(chunks[0]), 3)
        self.assertEqual(len(chunks[1]), 1)

        # Verify iteration integrity
        for msg in chunks[0]:
            self.assertEqual(msg.response_metadata["iteration"], 1)
        self.assertEqual(chunks[1][0].response_metadata["iteration"], 2)

    def test_messages_without_metadata(self):
        """Test handling of messages without response_metadata."""
        messages = [
            HumanMessage(content="Message without metadata"),
            AIMessage(content="Another message without metadata")
        ]

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 2)

    def test_mixed_metadata_presence(self):
        """Test handling of mixed messages with and without metadata."""
        messages = [
            HumanMessage(content="Message without metadata"),
            AIMessage(content="Message with iteration"),
            HumanMessage(content="Another message with iteration")
        ]

        messages[1].response_metadata = {"iteration": 1}
        messages[2].response_metadata = {"iteration": 2}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        # Should keep all messages together since token limit isn't exceeded
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 3)

    def test_multiple_iteration_changes_under_token_limit(self):
        """Test chunking with multiple iteration changes but under token limit."""
        messages = []
        for iteration in [1, 2, 3, 1, 2]:  # Include some iteration reuse
            msg = HumanMessage(content=f"Iteration {iteration} message")
            msg.response_metadata = {"iteration": iteration}
            messages.append(msg)

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        # Should keep all messages in one chunk since token limit isn't exceeded
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 5)

        # Verify all expected iterations are present
        iterations = [msg.response_metadata["iteration"] for msg in chunks[0]]
        self.assertEqual(iterations, [1, 2, 3, 1, 2])

    def test_large_single_iteration_exceeding_limit(self):
        """Test single iteration with multiple large messages exceeding token limit."""
        large_content = "Very large content that exceeds token limits. " * 2000

        messages = [
            HumanMessage(content=large_content),
            AIMessage(content=large_content),
            ToolMessage(content=large_content, tool_call_id="test1")
        ]

        for msg in messages:
            msg.response_metadata = {"iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=5000)

        # Should keep all messages in single chunk despite exceeding limit
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 3)

    def test_default_max_tokens_parameter(self):
        """Test that default max_tokens parameter is used correctly."""
        messages = [HumanMessage(content="Test message")]
        messages[0].response_metadata = {"iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer)  # No max_tokens specified

        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 1)

    def test_zero_max_tokens(self):
        """Test behavior with zero max_tokens (edge case)."""
        messages = [HumanMessage(content="Test")]
        messages[0].response_metadata = {"iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=0)

        # Should still create chunks - single message doesn't exceed limit since there's no "current" chunk
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 1)

    def test_messages_with_other_metadata_fields(self):
        """Test messages that have response_metadata but no iteration field."""
        messages = [
            HumanMessage(content="Message 1"),
            AIMessage(content="Message 2")
        ]

        messages[0].response_metadata = {"other_field": "value1"}
        messages[1].response_metadata = {"other_field": "value2", "iteration": 1}

        chunks = chunk_messages(messages, self.tokenizer, max_tokens=10000)

        # Should keep all messages together since token limit isn't exceeded
        self.assertEqual(len(chunks), 1)
        self.assertEqual(len(chunks[0]), 2)


class TestCleanTools(unittest.TestCase):
    """Test cases for the clean_tools and clean_tool_msg functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.tokenizer = TiktokenTokenizerProvider(encoding="cl100k_base")

    def test_clean_tool_msg_under_token_limit(self):
        """Test that tool messages under token limit are not modified."""
        tool_msg = ToolMessage(content="Short content", tool_call_id="test1", status="success")
        
        result = truncate_tool_msg(tool_msg, self.tokenizer, max_tool_tokens=1000)
        
        self.assertEqual(result.content, "Short content")
        self.assertEqual(result.tool_call_id, "test1")
        self.assertEqual(result.status, "success")

    def test_clean_tool_msg_over_token_limit(self):
        """Test that tool messages over token limit are truncated with redaction message."""
        # Create content that will exceed a small token limit
        large_content = "This is a very long message that will exceed the token limit. " * 100
        tool_msg = ToolMessage(content=large_content, tool_call_id="test2", status="success")
        
        result = truncate_tool_msg(tool_msg, self.tokenizer, max_tool_tokens=10)
        
        self.assertTrue(result.content.endswith(" [REDACTED: CONTENT TOO LONG]"))
        self.assertNotEqual(result.content, large_content)
        self.assertEqual(result.tool_call_id, "test2")
        self.assertEqual(result.status, "success")

    def test_clean_tool_msg_exact_token_limit(self):
        """Test behavior when content is exactly at token limit."""
        # Create content that's exactly at the limit
        content = "Short"  # This should be under any reasonable limit
        tool_msg = ToolMessage(content=content, tool_call_id="test3", status="success")
        
        # Set limit to exact token count
        token_count = len(self.tokenizer.encode(content))
        result = truncate_tool_msg(tool_msg, self.tokenizer, max_tool_tokens=token_count)
        
        # Should not be truncated when exactly at limit
        self.assertEqual(result.content, content)

    def test_clean_tools_depth_zero_all_messages(self):
        """Test clean_tools with depth=0 cleans all tool messages."""
        messages = [
            HumanMessage(content="User message"),
            ToolMessage(content="Tool result 1", tool_call_id="tool1", status="success"),
            AIMessage(content="AI response"),
            ToolMessage(content="Tool result 2", tool_call_id="tool2", status="success")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=0, max_tool_tokens=1000)
        
        self.assertEqual(len(result), 4)
        self.assertIsInstance(result[0], HumanMessage)
        self.assertIsInstance(result[1], ToolMessage)
        self.assertIsInstance(result[2], AIMessage)
        self.assertIsInstance(result[3], ToolMessage)
        
        # Tool messages should be unchanged if under limit
        self.assertEqual(result[1].content, "[REDACTED]")
        self.assertEqual(result[3].content, "[REDACTED]")

    def test_clean_tools_depth_zero_with_truncation(self):
        """Test clean_tools with depth=0 truncates large tool messages."""
        large_content = "Very large tool result content. " * 200
        messages = [
            HumanMessage(content="User message"),
            ToolMessage(content=large_content, tool_call_id="tool1", status="success"),
            AIMessage(content="AI response")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=0, max_tool_tokens=10)
        
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].content, "[REDACTED]")

    def test_clean_tools_with_depth(self):
        """Test clean_tools with depth parameter only cleans messages before specified AI message."""
        messages = [
            ToolMessage(content="Tool result 1", tool_call_id="tool1", status="success"),
            AIMessage(content="AI response 1"),
            ToolMessage(content="Tool result 2", tool_call_id="tool2", status="success"),
            AIMessage(content="AI response 2"),
            ToolMessage(content="Tool result 3", tool_call_id="tool3", status="success")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=1, max_tool_tokens=1000)
        
        # depth=1 means latest AI message is at index 3, so clean messages before index 3
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].content, "[REDACTED]")
        self.assertEqual(result[2].content, "[REDACTED]")  # Should be cleaned (redacted before AI index)
        self.assertEqual(result[4].content, "Tool result 3")  # Should not be cleaned

    def test_clean_tools_insufficient_ai_messages_for_depth(self):
        """Test clean_tools when there aren't enough AI messages for specified depth."""
        messages = [
            ToolMessage(content="Tool result 1", tool_call_id="tool1", status="success"),
            AIMessage(content="AI response 1"),
            ToolMessage(content="Tool result 2", tool_call_id="tool2", status="success")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=3, max_tool_tokens=1000)
        
        # Should return unchanged messages since depth=3 but only 1 AI message
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].content, "Tool result 1")
        self.assertEqual(result[2].content, "Tool result 2")

    def test_clean_tools_empty_messages_list(self):
        """Test clean_tools with empty messages list."""
        result = clean_tools([], self.tokenizer, depth=0, max_tool_tokens=1000)
        self.assertEqual(result, [])

    def test_clean_tools_no_tool_messages(self):
        """Test clean_tools with no tool messages in the list."""
        messages = [
            HumanMessage(content="User message"),
            AIMessage(content="AI response")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=0, max_tool_tokens=1000)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].content, "User message")
        self.assertEqual(result[1].content, "AI response")

    def test_clean_tool_msg_with_list_content(self):
        """Test clean_tool_msg with list content (should be handled by to_str_content)."""
        list_content = ["Part 1 of content", "Part 2 of content"]
        tool_msg = ToolMessage(content=list_content, tool_call_id="test4", status="success")
        
        result = truncate_tool_msg(tool_msg, self.tokenizer, max_tool_tokens=1000)
        
        # Should handle list content correctly
        self.assertIsInstance(result.content, str)
        self.assertEqual(result.tool_call_id, "test4")

    def test_clean_tool_msg_preserves_status(self):
        """Test that clean_tool_msg preserves the original status."""
        tool_msg_error = ToolMessage(content="Error content", tool_call_id="test5", status="error")
        
        result = truncate_tool_msg(tool_msg_error, self.tokenizer, max_tool_tokens=1000)
        
        self.assertEqual(result.status, "error")
        self.assertEqual(result.content, "Error content")

    def test_clean_tools_depth_negative_one(self):
        """Test clean_tools with depth=-1 does not clean but still truncates messages."""
        # Test with both small and large content
        large_content = "This is a very long message that will exceed the token limit. " * 100
        messages = [
            HumanMessage(content="User message"),
            ToolMessage(content="Short tool result", tool_call_id="tool1", status="success"),
            AIMessage(content="AI response 1"),
            ToolMessage(content=large_content, tool_call_id="tool2", status="success"),
            AIMessage(content="AI response 2"),
            ToolMessage(content="Another short result", tool_call_id="tool3", status="error")
        ]
        
        result = clean_tools(messages, self.tokenizer, depth=-1, max_tool_tokens=10)
        
        # Should have same number of messages
        self.assertEqual(len(result), 6)
        
        # Non-tool messages should be unchanged
        self.assertIsInstance(result[0], HumanMessage)
        self.assertEqual(result[0].content, "User message")
        self.assertIsInstance(result[2], AIMessage)
        self.assertEqual(result[2].content, "AI response 1")
        self.assertIsInstance(result[4], AIMessage)
        self.assertEqual(result[4].content, "AI response 2")
        
        # Short tool messages should remain unchanged (not cleaned/redacted)
        self.assertIsInstance(result[1], ToolMessage)
        self.assertEqual(result[1].content, "Short tool result")
        self.assertEqual(result[1].tool_call_id, "tool1")
        self.assertEqual(result[1].status, "success")
        
        self.assertIsInstance(result[5], ToolMessage)
        self.assertEqual(result[5].content, "Another short result")
        self.assertEqual(result[5].tool_call_id, "tool3")
        self.assertEqual(result[5].status, "error")
        
        # Large tool message should be truncated (not cleaned/redacted)
        self.assertIsInstance(result[3], ToolMessage)
        self.assertTrue(result[3].content.endswith(" [REDACTED: CONTENT TOO LONG]"))
        self.assertNotEqual(result[3].content, large_content)
        self.assertNotEqual(result[3].content, "[REDACTED]")  # Should not be fully redacted
        self.assertEqual(result[3].tool_call_id, "tool2")
        self.assertEqual(result[3].status, "success")

