import asyncio
import logging
from typing import List
import shlex

from langchain_core.tools import tool, BaseTool

from dev_observer.log import s_

_log = logging.getLogger(__name__)


async def execute_repo_bash_tool(cmd: str, repo_path: str, args: str = "") -> str:
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
def tree(arg: str) -> str:
    """
    Display directory tree structure using the tree command.

    This tool is a direct equivalent to the bash `tree` command.
    It shows the hierarchical structure of directories and files in a tree format.
    It's useful for understanding the overall organization of a codebase.

    Args:
        arg: A single string argument for 'tree' bash command. Command line arguments for tree command (e.g., "-L 2 ." for max depth 2,
              "-I 'node_modules|.git'" to ignore certain directories)

    Returns:
        a string output of the command

    Examples:
        tree(".")  # Show tree of current directory
        tree("-L 2 src")  # Show tree of src directory with max depth 2
        tree("-I '.git|node_modules' .")  # Show tree ignoring .git and node_modules
    """
    pass


@tool(parse_docstring=True)
def ls(arg: str) -> str:
    """
    List directory contents using the ls command.

    This tool is a direct equivalent to the bash `ls` command.
    It displays files and directories in the specified location.
    It's useful for exploring directory contents and file permissions.

    Args:
        arg: A single string argument for 'ls' bash command. Command line arguments for ls command (e.g., "-la" for detailed listing,
              "-lh" for human-readable sizes, "src/" to list specific directory)

    Returns:
        a string output of the command

    Examples:
        ls(".")  # List current directory
        ls("-la")  # List all files with detailed info including hidden files
        ls("-lh src/")  # List src directory with human-readable file sizes
    """
    pass


@tool(parse_docstring=True)
def cat(arg: str) -> str:
    """
    Display file contents using the cat command.

    This tool is a direct equivalent to the bash `cat` command.
    It reads and displays the contents of one or more files.
    It's essential for examining source code, configuration files, and documentation.

    Args:
        arg: A single string argument for 'cat' bash command. (e.g., "README.md", "-n file.py" for numbered lines, "file1.txt file2.txt" for multiple files)

    Returns:
        a string output of the command

    Examples:
        cat("README.md")  # Display README file contents
        cat("-n src/main.py")  # Display main.py with line numbers
        cat("package.json Makefile")  # Display contents of multiple files
    """
    pass


@tool(parse_docstring=True)
def find(arg: str) -> str:
    """
    Search for files and directories using the find command.

    This tool is a direct equivalent to the bash `find` command.
    It locates files and directories based on various criteria like name, type, size, etc.
    It's powerful for discovering files matching specific patterns or properties in the codebase.

    Args:
        arg: A single string argument for 'find' bash command. Search criteria and options for find command (e.g., ". -name '*.py'",
              ". -type f -name 'test*'", "src -name '*.js' -not -path '*/node_modules/*'")

    Returns:
        a string output of the command

    Examples:
        find(". -name '*.py'")  # Find all Python files
        find(". -type f -name 'README*'")  # Find all README files
        find("src -name '*.js' -not -path '*/node_modules/*'")  # Find JS files excluding node_modules
    """
    pass


@tool(parse_docstring=True)
def grep(arg: str) -> str:
    """
    Search for text patterns in files using the grep command.

    This tool is a direct equivalent to the bash `grep` command.
    It searches through file contents for specific patterns, regular expressions, or text.
    It's invaluable for finding function definitions, imports, specific strings, or code patterns.

    Args:
        arg: A single string argument for 'grep' bash command. Pattern and options for grep command (e.g., "-r 'function' .", "-n 'import' src/", "'class.*:' --include='*.py' .")

    Returns:
        a string output of the command

    Examples:
        grep("-r 'function' .")  # Search for 'function' recursively in all files
        grep("-n 'import' src/")  # Search for 'import' in src/ with line numbers
        grep("'class.*:' --include='*.py' .")  # Find class definitions in Python files
    """
    pass


def bash_tools() -> List[BaseTool]:
    return [tree, ls, cat, find, grep]


def bash_tool_names() -> List[str]:
    return [t.name for t in bash_tools()]
