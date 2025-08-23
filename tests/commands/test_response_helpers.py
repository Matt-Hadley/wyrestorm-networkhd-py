"""Unit tests for response helper functions."""

import pytest

from wyrestorm_networkhd.commands._response_helpers import (
    parse_json_response,
    require_command_mirror,
    require_contains,
    require_success_indicator,
)
from wyrestorm_networkhd.exceptions import CommandError, ResponseError

# =============================================================================
# require_command_mirror Tests
# =============================================================================


class TestRequireCommandMirror:
    """Test the require_command_mirror function."""

    def test_require_command_mirror_exact_match(self):
        """Test command mirror validation with exact match."""
        response = "config set session alias on"
        expected = "config set session alias on"

        result = require_command_mirror(response, expected)

        assert result is True

    def test_require_command_mirror_exact_match_with_whitespace(self):
        """Test command mirror validation with surrounding whitespace."""
        response = "  config set session alias off  "
        expected = "config set session alias off"

        result = require_command_mirror(response, expected)

        assert result is True

    def test_require_command_mirror_first_line_match(self):
        """Test command mirror validation with first line match."""
        response = "config set session alias on\nSome additional output"
        expected = "config set session alias on"

        result = require_command_mirror(response, expected)

        assert result is True

    def test_require_command_mirror_first_line_match_with_whitespace(self):
        """Test command mirror validation with first line match and whitespace."""
        response = "  config set session alias off  \nAdditional line"
        expected = "config set session alias off"

        result = require_command_mirror(response, expected)

        assert result is True

    def test_require_command_mirror_no_match(self):
        """Test command mirror validation failure."""
        response = "different command response"
        expected = "config set session alias on"

        with pytest.raises(ResponseError) as exc_info:
            require_command_mirror(response, expected)

        assert "Unexpected response" in str(exc_info.value)
        assert "config set session alias on" in str(exc_info.value)

    def test_require_command_mirror_empty_response(self):
        """Test command mirror validation with empty response."""
        response = ""
        expected = "config set session alias on"

        with pytest.raises(ResponseError) as exc_info:
            require_command_mirror(response, expected)

        assert "Unexpected response" in str(exc_info.value)

    def test_require_command_mirror_partial_match_fails(self):
        """Test command mirror validation fails with partial match."""
        response = "config set session"
        expected = "config set session alias on"

        with pytest.raises(ResponseError) as exc_info:
            require_command_mirror(response, expected)

        assert "Unexpected response" in str(exc_info.value)


# =============================================================================
# require_contains Tests
# =============================================================================


class TestRequireContains:
    """Test the require_contains function."""

    def test_require_contains_success(self):
        """Test substring validation success."""
        response = "The command was successful"
        substring = "successful"

        result = require_contains(response, substring)

        assert result is True

    def test_require_contains_case_insensitive(self):
        """Test substring validation is case insensitive."""
        response = "The COMMAND was SUCCESSFUL"
        substring = "successful"

        result = require_contains(response, substring)

        assert result is True

    def test_require_contains_with_whitespace(self):
        """Test substring validation with surrounding whitespace."""
        response = "  The command was successful  "
        substring = "successful"

        result = require_contains(response, substring)

        assert result is True

    def test_require_contains_failure(self):
        """Test substring validation failure."""
        response = "The command failed"
        substring = "successful"

        with pytest.raises(ResponseError) as exc_info:
            require_contains(response, substring)

        assert "Unexpected response" in str(exc_info.value)
        assert "successful" in str(exc_info.value)

    def test_require_contains_empty_response(self):
        """Test substring validation with empty response."""
        response = ""
        substring = "successful"

        with pytest.raises(ResponseError) as exc_info:
            require_contains(response, substring)

        assert "Unexpected response" in str(exc_info.value)


# =============================================================================
# require_success_indicator Tests
# =============================================================================


class TestRequireSuccessIndicator:
    """Test the require_success_indicator function."""

    def test_require_success_indicator_success(self):
        """Test success indicator validation with success."""
        response = "Operation completed successfully"

        result = require_success_indicator(response)

        assert result is True

    def test_require_success_indicator_success_case_insensitive(self):
        """Test success indicator validation is case insensitive."""
        response = "Operation completed SUCCESS"

        result = require_success_indicator(response)

        assert result is True

    def test_require_success_indicator_with_expected_start(self):
        """Test success indicator validation with expected start."""
        response = "Status: Operation completed successfully"
        expected_start = "Status:"

        result = require_success_indicator(response, expected_start)

        assert result is True

    def test_require_success_indicator_failure_raises_command_error(self):
        """Test success indicator validation with failure raises CommandError."""
        response = "Operation completed with failure"

        with pytest.raises(CommandError) as exc_info:
            require_success_indicator(response)

        assert "Device reported failure" in str(exc_info.value)

    def test_require_success_indicator_failure_case_insensitive(self):
        """Test failure detection is case insensitive."""
        response = "Operation completed with FAILURE"

        with pytest.raises(CommandError) as exc_info:
            require_success_indicator(response)

        assert "Device reported failure" in str(exc_info.value)

    def test_require_success_indicator_wrong_start(self):
        """Test success indicator validation with wrong start."""
        response = "Different: Operation completed successfully"
        expected_start = "Status:"

        with pytest.raises(ResponseError) as exc_info:
            require_success_indicator(response, expected_start)

        assert "Unexpected response start" in str(exc_info.value)
        assert "Status:" in str(exc_info.value)

    def test_require_success_indicator_no_indicator(self):
        """Test success indicator validation with no success/failure indicator."""
        response = "Operation completed"

        with pytest.raises(ResponseError) as exc_info:
            require_success_indicator(response)

        assert "Response missing success/failure indicator" in str(exc_info.value)

    def test_require_success_indicator_with_whitespace(self):
        """Test success indicator validation with whitespace."""
        response = "  Operation completed successfully  "

        result = require_success_indicator(response)

        assert result is True

    def test_require_success_indicator_expected_start_with_whitespace(self):
        """Test success indicator validation with expected start and whitespace."""
        response = "  Status: Operation completed successfully  "
        expected_start = "Status:"

        result = require_success_indicator(response, expected_start)

        assert result is True


# =============================================================================
# parse_json_response Tests
# =============================================================================


class TestParseJsonResponse:
    """Test the parse_json_response function."""

    def test_parse_json_response_success(self):
        """Test successful JSON parsing."""
        response = 'device json string: {"devices": [{"name": "source1", "type": "tx", "status": "online"}]}'
        result = parse_json_response(response, "device json string:")

        assert result == {"devices": [{"name": "source1", "type": "tx", "status": "online"}]}

    def test_parse_json_response_missing_prefix(self):
        """Test JSON parsing with missing prefix."""
        response = "No prefix here"

        with pytest.raises(ValueError, match="Invalid response format"):
            parse_json_response(response, "device json string:")

    def test_parse_json_response_invalid_json(self):
        """Test JSON parsing with invalid JSON."""
        response = "device json string: {invalid json"

        with pytest.raises(ValueError, match="Invalid JSON in response"):
            parse_json_response(response, "device json string:")

    def test_parse_json_response_with_whitespace(self):
        """Test JSON parsing with extra whitespace."""
        response = '  device json string:  {"devices": [{"name": "source1"}]}  '
        result = parse_json_response(response, "device json string:")

        assert result == {"devices": [{"name": "source1"}]}

    def test_parse_json_response_complex_json(self):
        """Test JSON parsing with complex nested JSON."""
        response = """device json string: {
            "devices": [
                {
                    "name": "TX1",
                    "type": "transmitter",
                    "status": "online",
                    "settings": {
                        "resolution": "1920x1080",
                        "fps": 60
                    }
                }
            ]
        }"""
        result = parse_json_response(response, "device json string:")

        assert result["devices"][0]["name"] == "TX1"
        assert result["devices"][0]["type"] == "transmitter"
        assert result["devices"][0]["settings"]["resolution"] == "1920x1080"
        assert result["devices"][0]["settings"]["fps"] == 60
