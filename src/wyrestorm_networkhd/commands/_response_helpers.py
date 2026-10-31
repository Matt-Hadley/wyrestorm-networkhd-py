"""Utilities for command response validation and parsing.

This module provides helper functions for validating and parsing responses
from NetworkHD API commands. These utilities ensure consistent error handling
and response validation across all command implementations.
"""

from ..exceptions import CommandError, ResponseError


def join_devices(devices: str | list[str]) -> str:
    """Join device references into the space-separated list a command takes

    Args:
        devices: A device reference, or a list of them

    Returns:
        str: The references separated by spaces

    Raises:
        ValueError: If there are no references, or one is empty

    Notes:
        A command sent with no device names is not defined by the API, so it is never sent.
    """
    names = [devices] if isinstance(devices, str) else list(devices)
    if not names or not all(isinstance(name, str) and name.strip() for name in names):
        raise ValueError(f"Device references must be non-empty strings, got: {devices!r}")
    return " ".join(names)


def require_no_quote(data: str) -> None:
    """Reject data that would end the quoted data argument of a command early

    Raises:
        ValueError: If data contains a double quote
    """
    if '"' in data:
        raise ValueError(f"Data must not contain a double quote: {data!r}")


def strip_echo(response: str, command: str) -> str:
    """Drop the line echoing the command from the start of a response

    Args:
        response: The raw response string from the device
        command: The command that was sent

    Returns:
        str: The response after the echo line, or the response unchanged if it does not start with the echo

    Notes:
        Real controllers echo every command as the first line of their reply; parsers expect the reply without it.
    """
    first_line, _, rest = response.strip().partition("\n")
    return rest if first_line.strip() == command.strip() else response


def require_command_mirror(response: str, expected: str) -> bool:
    """Validate that the response mirrored the command

    Args:
        response: The raw response string from the device
        expected: The expected command echo string

    Returns:
        bool: True if response matches expected echo

    Raises:
        ResponseError: If response does not match expected echo

    Notes:
        Succeeds if the response is exactly the expected echo, optionally followed by one identical mirror line, which
        may carry the "receive: " prefix the PDF shows for some commands. Anything else (such as an error message
        after the echo) fails.
    """
    expected_stripped = expected.strip()
    lines = [line.strip().removeprefix("receive: ") for line in response.strip().splitlines()]
    if lines in ([expected_stripped], [expected_stripped, expected_stripped]):
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
        If the last word of the response is 'failure', CommandError is raised.
        If it is 'success', True is returned.
        Otherwise, ResponseError is raised.
    """
    words = response.lower().split()
    if expected_start and not response.strip().startswith(expected_start):
        raise ResponseError(f"Unexpected response start. Expected to start with: '{expected_start}', got: '{response}'")
    # Only the last word counts, so a name containing "success" or "failure" is not mistaken for the result
    if words and words[-1] == "failure":
        raise CommandError(f"Device reported failure: '{response}'")
    if words and words[-1] == "success":
        return True
    raise ResponseError(f"Response missing success/failure indicator: '{response}'")
