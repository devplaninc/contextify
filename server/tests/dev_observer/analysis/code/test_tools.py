import unittest

import pytest

from dev_observer.analysis.code.tools import _validate_bash_command, ALLOWED_BASH_COMMANDS


class TestValidateBashCommand(unittest.TestCase):
    """Test the _validate_bash_command function for various scenarios."""

    def test_valid_single_commands(self):
        """Test that valid single commands are accepted."""
        valid_commands = [
            "ls",
            "ls -la",
            "cat file.txt",
            "head -n 10 file.py",
            "tail -f log.txt",
            "grep pattern file.txt",
            "find . -name '*.py'",
            "tree -L 2",
            "wc -l file.txt",
            "sort file.txt",
            "uniq file.txt",
        ]
        
        for command in valid_commands:
            assert _validate_bash_command(command), f"Command should be valid: {command}"

    def test_valid_piped_commands(self):
        """Test that valid piped commands are accepted."""
        valid_piped_commands = [
            "ls | head -10",
            "cat file.txt | grep pattern",
            "find . -name '*.py' | head -5",
            "ls -la | grep test",
            "head file.py | grep import",
            "cat README.md | grep -i install",
            "find . -type f | wc -l",
            "ls | sort | uniq",
            "grep -r 'function' . | head -10",
            "tree | grep -v node_modules",
        ]
        
        for command in valid_piped_commands:
            assert _validate_bash_command(command), f"Piped command should be valid: {command}"

    def test_invalid_commands_not_in_whitelist(self):
        """Test that commands not in the whitelist are rejected."""
        invalid_commands = [
            "rm file.txt",
            "rm -rf directory",
            "mkdir newdir",
            "touch newfile",
            "chmod 755 file",
            "chown user file",
            "sudo ls",
            "su",
            "passwd",
            "ps aux",
            "kill -9 1234",
            "wget http://example.com",
            "curl http://example.com",
            "python script.py",
            "node app.js",
            "git clone repo",
            "mv file1 file2",
            "cp file1 file2",
            "dd if=/dev/zero of=file",
            "mount /dev/sda1",
            "umount /mnt",
        ]
        
        for command in invalid_commands:
            assert not _validate_bash_command(command), f"Command should be invalid: {command}"

    def test_headless_execution_patterns(self):
        """Test that headless execution patterns are rejected."""
        headless_commands = [
            "ls &",
            "ls -la &",
            "find . -name '*.py' &",
            "nohup ls",
            "nohup find . -name '*.py'",
            "ls > /dev/null &",
            "grep pattern file.txt > /dev/null &",
            "cat file.txt > /dev/null 2>&1 &",
            "   ls   &   ",  # with whitespace
            "nohup cat file.txt",
        ]
        
        for command in headless_commands:
            assert not _validate_bash_command(command), f"Headless command should be invalid: {command}"

    def test_mixed_valid_invalid_in_pipeline(self):
        """Test that pipelines with any invalid command are rejected."""
        mixed_commands = [
            "ls | rm file.txt",
            "cat file.txt | python process.py",
            "find . -name '*.py' | xargs rm",
            "ls | head -10 | rm",
            "grep pattern file.txt | sudo cat",
            "head file.py | mkdir newdir",
        ]
        
        for command in mixed_commands:
            assert not _validate_bash_command(command), f"Mixed pipeline should be invalid: {command}"

    def test_empty_and_whitespace_commands(self):
        """Test that empty and whitespace-only commands are rejected."""
        empty_commands = [
            "",
            " ",
            "   ",
            "\t",
            "\n",
            "  \t  \n  ",
        ]
        
        for command in empty_commands:
            assert not _validate_bash_command(command), f"Empty command should be invalid: '{command}'"

    def test_malformed_shell_syntax(self):
        """Test that commands with malformed shell syntax are rejected."""
        malformed_commands = [
            "ls 'unclosed quote",
            'grep "unclosed double quote',
            "find . -name '*.py",  # unclosed quote
            'head "file.txt',  # unclosed quote
            "ls | grep 'pattern",  # unclosed quote in pipeline
        ]
        
        for command in malformed_commands:
            assert not _validate_bash_command(command), f"Malformed command should be invalid: {command}"

    def test_pipeline_with_empty_parts(self):
        """Test pipelines with empty parts."""
        commands_with_empty_parts = [
            "ls | ",
            " | grep pattern",
            "ls |  | grep pattern",
            "cat file.txt | | head -10",
        ]
        
        # These should be handled gracefully - empty parts should be skipped
        # but the overall command should still be valid if remaining parts are valid
        for command in commands_with_empty_parts:
            # The function should handle empty pipeline parts gracefully
            # by continuing to check non-empty parts
            result = _validate_bash_command(command)
            # For "ls | " and " | grep pattern", should be valid as non-empty parts are valid
            # For commands with only empty parts between pipes, should be invalid
            if command.strip() in ["ls | ", " | grep pattern"]:
                assert result, f"Command with trailing/leading empty pipe should be valid: {command}"

    def test_complex_valid_pipelines(self):
        """Test complex but valid pipeline commands."""
        complex_commands = [
            "find . -name '*.py' | grep -v __pycache__ | head -20",
            "ls -la | grep -E '\\.(py|txt)$' | sort",
            "cat file1.txt file2.txt | grep pattern | uniq | sort",
            "find . -type f | head -100 | tail -50",
            "grep -r 'import' src/ | cut -d: -f1 | sort | uniq",
        ]
        
        for command in complex_commands:
            assert _validate_bash_command(command), f"Complex valid command should be accepted: {command}"

    def test_commands_with_various_arguments(self):
        """Test that commands with various argument patterns work correctly."""
        commands_with_args = [
            "ls -la /tmp",
            "grep -i -n -r 'pattern' .",
            "find /usr/local -name '*.so' -type f",
            "head -n 20 file.txt",
            "tail -f -n 100 log.txt",
            "wc -l -w -c file.txt",
            "sort -n -r file.txt",
            "uniq -c -d file.txt",
        ]
        
        for command in commands_with_args:
            assert _validate_bash_command(command), f"Command with arguments should be valid: {command}"

    def test_command_whitelist_completeness(self):
        """Test that the ALLOWED_BASH_COMMANDS set contains expected commands."""
        expected_commands = {
            'ls', 'cat', 'head', 'tail', 'grep', 'find', 'tree', 'wc', 'sort', 'uniq'
        }
        
        # Check that all expected commands are in the whitelist
        for cmd in expected_commands:
            assert cmd in ALLOWED_BASH_COMMANDS, f"Expected command '{cmd}' should be in ALLOWED_BASH_COMMANDS"
        
        # Verify that all whitelisted commands result in valid single commands
        for cmd in ALLOWED_BASH_COMMANDS:
            assert _validate_bash_command(cmd), f"Whitelisted command '{cmd}' should be valid"

    def test_case_sensitivity(self):
        """Test that command validation is case sensitive."""
        # Commands should be case sensitive - uppercase versions should be invalid
        case_sensitive_tests = [
            ("ls", True),
            ("LS", False),
            ("Cat", False),
            ("HEAD", False),
            ("Grep", False),
        ]
        
        for command, should_be_valid in case_sensitive_tests:
            result = _validate_bash_command(command)
            if should_be_valid:
                assert result, f"Command '{command}' should be valid"
            else:
                assert not result, f"Command '{command}' should be invalid (case sensitive)"

    def test_logical_or_valid_commands(self):
        """Test that valid logical OR commands are accepted."""
        valid_or_commands = [
            "ls || true",
            "grep pattern file.txt || true",
            "cat file.txt || ls",
            "head file.py || tail file.py",
            "find . -name '*.py' || grep -r 'pattern' .",
            "ls -la || tree",
            "cat nonexistent.txt || head default.txt",
        ]
        
        for command in valid_or_commands:
            assert _validate_bash_command(command), f"Valid OR command should be accepted: {command}"

    def test_logical_or_invalid_commands(self):
        """Test that logical OR commands with invalid parts are rejected."""
        invalid_or_commands = [
            "ls || echo 'not found'",  # echo not allowed
            "grep pattern file.txt || rm file.txt",  # rm not allowed
            "cat file.txt || python script.py",  # python not allowed
            "find . -name '*.py' || sudo ls",  # sudo not allowed
            "ls || mkdir newdir",  # mkdir not allowed
            "head file.txt || wget http://example.com",  # wget not allowed
        ]
        
        for command in invalid_or_commands:
            assert not _validate_bash_command(command), f"Invalid OR command should be rejected: {command}"

    def test_logical_or_edge_cases(self):
        """Test edge cases with logical OR operators."""
        edge_case_tests = [
            ("|| true", True),  # leading ||
            ("ls ||", True),    # trailing ||
            ("|| || ls", True), # multiple leading ||
            ("ls || || true", True), # multiple || in middle
            ("ls |||", True),  # triple ||| is treated as || + | (valid: empty parts are skipped)
            ("'ls || true'", False), # quoted command treated as literal (not in whitelist)
            ('"ls || echo test"', False), # quoted command treated as literal (not in whitelist)
        ]
        
        for command, should_be_valid in edge_case_tests:
            result = _validate_bash_command(command)
            if should_be_valid:
                assert result, f"Edge case command should be valid: {command}"
            else:
                assert not result, f"Edge case command should be invalid: {command}"

    def test_mixed_pipes_and_logical_or(self):
        """Test commands that mix pipes (|) and logical OR (||)."""
        mixed_commands = [
            "ls | head -10 || true",  # pipe then logical OR
            "cat file.txt || grep pattern | sort",  # logical OR then pipe
            "find . -name '*.py' | head -5 || tail -5",  # pipe, then logical OR
        ]
        
        for command in mixed_commands:
            assert _validate_bash_command(command), f"Mixed pipe/OR command should be valid: {command}"

    def test_true_command_in_whitelist(self):
        """Test that 'true' command is now in the whitelist."""
        assert "true" in ALLOWED_BASH_COMMANDS, "'true' should be in ALLOWED_BASH_COMMANDS"
        assert _validate_bash_command("true"), "'true' command should be valid"