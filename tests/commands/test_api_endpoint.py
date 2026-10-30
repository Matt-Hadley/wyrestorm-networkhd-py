import pytest

from tests.commands import echoing_client
from wyrestorm_networkhd.commands.api_endpoint import APIEndpointCommands
from wyrestorm_networkhd.exceptions import ResponseError


class TestAPIEndpointCommands:
    """Unit tests for APIEndpointCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = echoing_client()
        self.commands = APIEndpointCommands(self.mock_client)

    # =============================================================================
    # 4.1 Session Alias Mode
    # =============================================================================

    @pytest.mark.asyncio
    async def test_set_session_alias_on(self):
        """Test setting session alias mode to on."""
        # Arrange
        mode = "on"
        expected_command = "config set session alias on"
        expected_response = "config set session alias on"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_session_alias(mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_session_alias_off(self):
        """Test setting session alias mode to off."""
        # Arrange
        mode = "off"
        expected_command = "config set session alias off"
        expected_response = "config set session alias off"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_session_alias(mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_session_alias_with_multiline_response(self):
        """Test setting session alias mode with multiline response is rejected."""
        # Arrange
        mode = "on"
        expected_command = "config set session alias on"
        expected_response = "config set session alias on\nAdditional output line"
        self.mock_client.send_command.return_value = expected_response

        # Act / Assert: anything after the mirror means the device did not just accept the command
        with pytest.raises(ResponseError):
            await self.commands.config_set_session_alias(mode)

        self.mock_client.send_command.assert_called_once_with(expected_command)

    @pytest.mark.asyncio
    async def test_set_session_alias_with_whitespace_response(self):
        """Test setting session alias mode with whitespace in response."""
        # Arrange
        mode = "off"
        expected_command = "config set session alias off"
        expected_response = "  config set session alias off  "
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_session_alias(mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True
