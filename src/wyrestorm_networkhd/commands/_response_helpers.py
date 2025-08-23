"""Utilities for command response validation and parsing.

This module provides helper functions for validating and parsing responses
from NetworkHD API commands. These utilities ensure consistent error handling
and response validation across all command implementations.
"""

import json
from typing import Any

from ..exceptions import CommandError, ResponseError


def require_command_mirror(response: str, expected: str) -> bool:
    """Validate that the response echoed the command

    Args:
        response: The raw response string from the device
        expected: The expected command echo string

    Returns:
        bool: True if response matches expected echo

    Raises:
        ResponseError: If response does not match expected echo

    Notes:
        Succeeds if the entire response equals the expected echo OR the first
        non-empty line equals the expected echo.
    """
    stripped = response.strip()
    expected_stripped = expected.strip()
    if stripped == expected_stripped:
        return True
    first_line = stripped.splitlines()[0] if stripped else ""
    if first_line.strip() == expected_stripped:
        return True
    raise ResponseError(f"Unexpected response. Expected echo of: '{expected}', got: '{response}'")


def require_contains(response: str, substring: str) -> bool:
    """Validate that the response contains the given substring (case-insensitive)

    Args:
        response: The raw response string from the device
        substring: The substring that must be present in the response

    Returns:
        bool: True if substring is found in response

    Raises:
        ResponseError: If substring is not found in response

    Notes:
        Case-insensitive comparison is performed.
    """
    if substring.lower() in response.strip().lower():
        return True
    raise ResponseError(f"Unexpected response. Expected to contain: '{substring}', got: '{response}'")


def require_success_indicator(response: str, expected_start: str | None = None) -> bool:
    """Validate that response contains a success/failure indicator and return True on success

    Args:
        response: The raw response string from the device
        expected_start: Optional expected start of the response string

    Returns:
        bool: True if response contains success indicator

    Raises:
        ResponseError: If response format is invalid or missing success/failure indicator
        CommandError: If device reported failure

    Notes:
        If expected_start is provided, the response must start with it; otherwise ResponseError is raised.
        If the response contains 'failure', CommandError is raised.
        If it contains 'success', True is returned.
        Otherwise, ResponseError is raised.
    """
    lower = response.strip().lower()
    if expected_start and not response.strip().startswith(expected_start):
        raise ResponseError(f"Unexpected response start. Expected to start with: '{expected_start}', got: '{response}'")
    if "failure" in lower:
        raise CommandError(f"Device reported failure: '{response}'")
    if "success" in lower:
        return True
    raise ResponseError(f"Response missing success/failure indicator: '{response}'")


def parse_json_response(response: str, prefix: str) -> dict[str, Any]:
    """Helper function for parsing JSON responses from API commands

    Args:
        response: The raw response string from the device
        prefix: The expected prefix before the JSON data (e.g., "device json string:")

    Returns:
        dict[str, Any]: The parsed JSON data as a dictionary

    Raises:
        ValueError: If the response format is invalid or contains invalid JSON

    Notes:
        Extracts JSON data that appears after the specified prefix in the response.
        Handles both valid JSON parsing and format validation.
    """
    if prefix not in response:
        raise ValueError(f"Invalid response format, expected '{prefix}': {response}")

    json_part = response.split(prefix)[1].strip()
    try:
        parsed_data: dict[str, Any] = json.loads(json_part)
        return parsed_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {e}") from e
