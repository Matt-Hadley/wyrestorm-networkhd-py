from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.api_endpoint import APIEndpointCommands


class TestAPIEndpointCommands:
    """Unit tests for APIEndpointCommands using mocked client."""

    def setup_method(self):
        """Set up mock client for each test."""
        self.mock_client = Mock()
        self.mock_client.send_command = AsyncMock()
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
        """Test setting session alias mode with multiline response."""
        # Arrange
        mode = "on"
        expected_command = "config set session alias on"
        expected_response = "config set session alias on\nAdditional output line"
        self.mock_client.send_command.return_value = expected_response

        # Act
        result = await self.commands.config_set_session_alias(mode)

        # Assert
        self.mock_client.send_command.assert_called_once_with(expected_command)
        assert result is True

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
