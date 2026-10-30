from unittest.mock import AsyncMock, Mock


def echoing_client() -> Mock:
    """Mock client whose send_command, like a real controller, starts every reply with the command echo.

    Tests script the device's reply with ``send_command.return_value``; the echo line is prepended to it.
    """
    client = Mock()
    send_command = AsyncMock()

    async def reply(command: str, *_args, **_kwargs) -> str:
        scripted = send_command.return_value
        return f"{command}\n{scripted}" if isinstance(scripted, str) and scripted else command

    send_command.side_effect = reply
    client.send_command = send_command
    return client
