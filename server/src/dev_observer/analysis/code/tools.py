import asyncio
import dataclasses
import logging
from typing import List
import shlex
import re

from langchain_core.tools import tool, BaseTool

from dev_observer.log import s_

_log = logging.getLogger(__name__)

# Allowed readonly commands for bash tool security
ALLOWED_BASH_COMMANDS = {
    'ls', 'cat', 'head', 'tail', 'grep', 'find', 'tree', 'wc', 'sort', 'uniq', 'cut'
}

@dataclasses.dataclass
class BashResult:
    result: str
    success: bool = True


def _validate_bash_command(command_string: str) -> bool:
    """Validate that a command string only contains allowed commands and is not headless."""
    if not command_string.strip():
        return False
    
    # Check for headless execution patterns (commands ending with &, nohup, etc.)
    headless_patterns = [
        r'&\s*$',  # ending with &
        r'^\s*nohup\s+',  # starting with nohup
        r'>\s*/dev/null.*&',  # redirecting to /dev/null and backgrounding
    ]
    for pattern in headless_patterns:
        if re.search(pattern, command_string):
            return False
    
    # Split by pipes while respecting quotes
    # First, try to parse the entire command to check for syntax errors
    try:
        # This will raise ValueError if there are unclosed quotes
        shlex.split(command_string)
    except ValueError:
        # Invalid shell syntax (unclosed quotes, etc.)
        return False
    
    # Split by pipes using a more sophisticated approach that respects quotes
    pipe_parts = []
    current_part = ""
    in_quote = False
    quote_char = None
    
    i = 0
    while i < len(command_string):
        char = command_string[i]
        
        if not in_quote and char in ('"', "'"):
            in_quote = True
            quote_char = char
            current_part += char
        elif in_quote and char == quote_char:
            # Check if it's escaped
            if i > 0 and command_string[i-1] == '\\':
                current_part += char
            else:
                in_quote = False
                quote_char = None
                current_part += char
        elif not in_quote and char == '|':
            pipe_parts.append(current_part.strip())
            current_part = ""
        else:
            current_part += char
        
        i += 1
    
    # Add the last part
    if current_part.strip():
        pipe_parts.append(current_part.strip())
    
    # Validate each pipeline part
    for part in pipe_parts:
        if not part:
            continue
            
        # Parse the first word (command name) from each pipe part
        try:
            tokens = shlex.split(part)
            if not tokens:
                continue
            command_name = tokens[0]
        except ValueError:
            # Invalid shell syntax
            return False
        
        # Check if command is in allowed list
        if command_name not in ALLOWED_BASH_COMMANDS:
            return False
    
    return True


async def _execute_bash_pipeline(command_string: str, repo_path: str) -> BashResult:
    """Execute a bash command pipeline safely."""
    _log.debug(s_("Executing bash pipeline", command=command_string, repo_path=repo_path))
    
    try:
        # Execute the full pipeline using shell
        process = await asyncio.create_subprocess_shell(
            command_string,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_path,
            shell=True
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            err = stderr.decode('utf-8').strip()
            out = stdout.decode('utf-8').strip()
            _log.warning(s_("Bash pipeline failed", command=command_string, err=err, out=out, returncode=process.returncode))
            return BashResult(
                result=f"Non 0 return code: \ncode: {process.returncode}\nstdout: {out}\nstderr: {err}",
                success=False
            )

        return BashResult(result=stdout.decode('utf-8'))
    except Exception as e:
        _log.warning(s_("Bash pipeline crashed", command=command_string, exc=e))
        return BashResult(result=f"Error: {str(e)}", success=False)


async def execute_repo_bash_tool(cmd: str, repo_path: str, args: str = "") -> str:
    """Legacy function for backward compatibility with individual commands."""
    _log.debug(s_("Executing bash tool", tool=cmd, args=args))
    try:
        parsed_args = shlex.split(args) if args.strip() else []

        # Build full command
        full_cmd = [cmd] + parsed_args

        # Execute command asynchronously
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_path
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            err = stderr.decode('utf-8').strip()
            out = stdout.decode('utf-8').strip()
            _log.warning(s_("Bash tool failed", tool=cmd, args=args, err=err, out=out, returncode=process.returncode))
            return f"Non 0 return code: \ncode: {process.returncode}\nstdout: {out}\nstderr: {err}"

        return stdout.decode('utf-8')
    except Exception as e:
        _log.warning(s_("Bash tool crashed", tool=cmd, args=args, exc=e))
        return f"Error: {str(e)}"


@tool(parse_docstring=True)
def bash(command: str) -> str:
    """
    Execute bash commands safely with support for pipes and readonly operations.

    This tool allows executing bash command pipelines for code exploration and analysis.
    It supports piped commands like 'head test.tsx | grep java' and only allows
    readonly commands from a predefined whitelist for security.

    Args:
        command (str): A bash command string that can include pipes. Only readonly commands from the following whitelist: ls, cat, head, tail, grep, find, tree, wc, sort, uniq, cut. Commands cannot be run headless (no & or nohup).


    Returns:
        a string output of the command

    Examples:
        bash("ls -la")  # List directory contents
        bash("find . -name '*.py' | head -10")  # Find Python files, show first 10
        bash("cat README.md | grep -i install")  # Search for install in README
        bash("head -20 src/main.py | grep import")  # Show imports from main.py
    """
    # This will be implemented via dynamic binding in bash_tools()
    return "Tool not implemented - use via dynamic binding"


def bash_tools() -> List[BaseTool]:
    """Return list of bash tools."""
    return [bash]


def bash_tool_names() -> List[str]:
    return [t.name for t in bash_tools()]
