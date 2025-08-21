import os
import re
import tomllib
from typing import Optional, Dict, Protocol

from google.protobuf import json_format

from dev_observer.api.types.ai_pb2 import PromptTemplate
from dev_observer.prompts.provider import PromptsProvider, FormattedPrompt


class PromptTemplateParser(Protocol):
    def parse(self, template_body: bytes) -> PromptTemplate:
        ...


class JSONPromptTemplateParser(PromptTemplateParser):
    def parse(self, template_body: bytes) -> PromptTemplate:
        return PromptTemplate.FromString(template_body)


class TomlPromptTemplateParser(PromptTemplateParser):
    def parse(self, template_body: bytes) -> PromptTemplate:
        toml_dict = tomllib.loads(template_body.decode('utf-8'))
        return json_format.ParseDict(toml_dict, PromptTemplate())


def replace_template_parameters(text: str, params: Dict[str, str]) -> str:
    """
    Replace template parameters in the format {{<parameter>}} with their values.

    Args:
        text: The text containing template parameters
        params: Dictionary of parameter names to their values

    Returns:
        Text with parameters replaced
    """
    if not text or not params:
        return text

    def replace_param(match):
        param_name = match.group(1).strip()
        return params.get(param_name, match.group(0))  # Return original if param not found

    # Pattern to match {{parameter_name}}
    pattern = r'\{\{([^}]+)\}\}'
    return re.sub(pattern, replace_param, text)


class LocalPromptsProvider(PromptsProvider):
    prompts_path: str
    extension: str
    parser: PromptTemplateParser

    def __init__(self, prompts_path: str, extension: str, parser: PromptTemplateParser):
        self.prompts_path = prompts_path
        self.extension = extension
        self.parser = parser

    async def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        res = await self.get_optional(name, params)
        if res is None:
            raise ValueError(f"Prompt template '{name}' not found")
        return res

    async def get_optional(self, name: str, params: Optional[Dict[str, str]] = None) -> Optional[FormattedPrompt]:
        file_path = self._get_file_path(name)
        if not file_path:
            return None
        with open(file_path, 'rb') as f:
            content = f.read()

        template = self.parser.parse(content)

        if params:
            if template.system:
                template.system.text = replace_template_parameters(template.system.text, params)

            if template.user and template.user.text:
                template.user.text = replace_template_parameters(template.user.text, params)

        return FormattedPrompt(
            system=template.system,
            user=template.user,
            config=template.config,
            prompt_name=name,
        )

    def _get_file_path(self, name: str) -> Optional[str]:
        file_path = os.path.join(self.prompts_path, f"{name}{self.extension}")
        if os.path.exists(file_path):
            return file_path
        return None
