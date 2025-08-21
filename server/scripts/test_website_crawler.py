#!/usr/bin/env python3
"""
Test script for the website crawler.

This script accepts a website URL as input, runs the crawler, validates that raw data is stored correctly,
triggers analysis, and verifies that observations are created.

Usage:
    python test_website_crawler.py <website_url>

Example:
    python test_website_crawler.py https://example.com
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import List, Optional, Dict

from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.website.cloner import normalize_domain, normalize_name

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dev_observer.analysis.stub import StubAnalysisProvider
from dev_observer.api.types.observations_pb2 import ObservationKey
from dev_observer.observations.memory import MemoryObservationsProvider
from dev_observer.processors.flattening import ObservationRequest
from dev_observer.processors.websites import WebsitesProcessor, ObservedWebsite
from dev_observer.prompts.provider import FormattedPrompt, PromptsProvider
from dev_observer.tokenizer.tiktoken import TiktokenTokenizerProvider
from dev_observer.website.crawler import ScrapyWebsiteCrawlerProvider

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_log = logging.getLogger(__name__)


class StubPromptsProvider(PromptsProvider):
    """Stub implementation of the PromptsProvider protocol for testing."""

    async def get_formatted(self, name: str, params=None) -> FormattedPrompt:
        """Get a formatted prompt."""
        from dev_observer.api.types.ai_pb2 import PromptConfig, ModelConfig, SystemMessage, UserMessage
        model_config = ModelConfig(
            provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )
        return FormattedPrompt(
            config=PromptConfig(model=model_config),
            system=SystemMessage(text="You are a helpful assistant."),
            user=UserMessage(text="Analyze this website."),
        )

    async def get_optional(self, name: str, params: Optional[Dict[str, str]] = None) -> Optional[FormattedPrompt]:
        return await self.get_formatted(name, params)


async def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description="Test the website crawler.")
    parser.add_argument("url", help="The URL of the website to crawl.")
    parser.add_argument("--output-dir",
                        help="The directory to store the crawled data. If not provided, a temporary directory will be used.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create providers
    website_crawler = ScrapyWebsiteCrawlerProvider()
    tokenizer = TiktokenTokenizerProvider(encoding="cl100k_base")  # Using the OpenAI encoding
    analysis = StubAnalysisProvider()
    prompts = StubPromptsProvider()
    observations = MemoryObservationsProvider()
    # observations = LocalObservationsProvider(root_dir="__obs")

    # Create processor
    processor = WebsitesProcessor(
        analysis=analysis,
        website_crawler=website_crawler,
        prompts=prompts,
        observations=observations,
        tokenizer=tokenizer,
    )

    # Create observation requests
    requests: List[ObservationRequest] = []

    # Create a test analyzer
    domain = normalize_domain(args.url)
    name = normalize_name(args.url)
    key = f"{domain}/{name}/test_analyzer"

    requests.append(ObservationRequest(
        prompt_prefix="Analyze this website:",
        key=ObservationKey(kind="websites", name="test_analyzer", key=key),
    ))

    # Process the website
    _log.info(f"Crawling website: {args.url}")
    await processor.process(ObservedWebsite(url=args.url), requests, GlobalConfig(), clean=False)

    # Verify that observations were created
    observation_keys = await observations.list(kind="websites")
    if not observation_keys:
        _log.error("No observations were created.")
        return 1

    _log.info(f"Created {len(observation_keys)} observations:")
    for key in observation_keys:
        observation = await observations.get(key)
        _log.info(f"  - {key.name} ({key.key}): {len(observation.content)} characters")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
