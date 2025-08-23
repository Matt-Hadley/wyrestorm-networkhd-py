"""Protocol-specific integration tests - Testing protocol differences and edge cases."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH


@pytest.mark.integration
class TestProtocolSpecificBehavior:
    """Tests for protocol-specific differences and edge cases."""

    @pytest.mark.asyncio
    async def test_ssh_host_key_policy_handling(self):
        """Test SSH-specific host key policy behavior."""
        # Test different host key policies
        for policy in ["auto_add", "reject", "warn"]:
            client = NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy=policy
            )
            assert client.ssh_host_key_policy == policy

    @pytest.mark.asyncio
    async def test_rs232_baudrate_handling(self):
        """Test RS232-specific baudrate and serial parameter handling."""
        # Test different baudrates and serial parameters
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=115200, parity="even", stopbits=2)
        assert client.baudrate == 115200
        assert client.serial_kwargs == {"parity": "even", "stopbits": 2}

    @pytest.mark.asyncio
    async def test_ssh_connection_edge_cases(self):
        """Test SSH-specific connection edge cases."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Test transport becoming inactive after connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh, mock_shell, mock_transport = Mock(), Mock(), Mock()
            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()
                assert client.is_connected()

                # Transport becomes inactive
                mock_transport.is_active.return_value = False
                assert not client.is_connected()

    @pytest.mark.asyncio
    async def test_rs232_connection_edge_cases(self):
        """Test RS232-specific connection edge cases."""
        client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Test serial port becoming unavailable after connection
        with patch("async_pyserial.SerialPort") as mock_serial_class:
            mock_serial = Mock()
            mock_serial.is_open = True
            mock_serial.open = AsyncMock()
            mock_serial_class.return_value = mock_serial

            await client.connect()
            assert client.is_connected()

            # Port becomes unavailable
            mock_serial.is_open = False
            assert not client.is_connected()


@pytest.mark.integration
class TestProtocolMessageHandling:
    """Test protocol message handling for both client types."""

    @pytest.mark.parametrize("client_type", ["ssh", "rs232"])
    @pytest.mark.asyncio
    async def test_protocol_consistency(self, client_type):
        """Test that protocol works consistently across SSH and RS232."""
        if client_type == "ssh":
            client = NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
            )
        else:
            client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)

        # Mock connection based on client type
        if client_type == "ssh":
            with patch("paramiko.SSHClient") as mock_class:
                mock_conn, mock_shell, mock_transport = Mock(), Mock(), Mock()
                mock_shell.closed = False
                mock_transport.is_active.return_value = True
                mock_conn.get_transport.return_value = mock_transport
                mock_conn.invoke_shell.return_value = mock_shell
                mock_class.return_value = mock_conn

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()
        else:
            with patch("async_pyserial.SerialPort") as mock_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()
                mock_class.return_value = mock_serial

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()

        # Test standard commands work consistently
        test_commands = [
            ("get device info", "OK: device=WyreStorm NetworkHD"),
            ("set input 1", "OK: input set to 1"),
            ("get status", "OK: status=online"),
        ]

        for command, expected_response in test_commands:
            with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value=expected_response):
                response = await client.send_command(command)
                assert expected_response in response

    @pytest.mark.asyncio
    async def test_notification_handling_consistency(self):
        """Test notification handling works consistently across client types."""
        clients = [
            NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
            ),
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600),
        ]

        # Define callback factory outside loop
        def make_callback(notifications):
            def callback(notification):
                notifications.append(notification)

            return callback

        for client in clients:
            received_notifications = []
            callback = make_callback(received_notifications)
            client.register_notification_callback("test", callback)

            # Mock connection based on client type
            if isinstance(client, NetworkHDClientSSH):
                with patch("paramiko.SSHClient") as mock_ssh_class:
                    mock_ssh, mock_shell, mock_transport = Mock(), Mock(), Mock()
                    mock_shell.closed = False
                    mock_transport.is_active.return_value = True
                    mock_ssh.get_transport.return_value = mock_transport
                    mock_ssh.invoke_shell.return_value = mock_shell
                    mock_ssh_class.return_value = mock_ssh

                    with patch.object(client, "_start_message_dispatcher"):
                        await client.connect()
            else:
                with patch("async_pyserial.SerialPort") as mock_serial_class:
                    mock_serial = Mock()
                    mock_serial.is_open = True
                    mock_serial.open = AsyncMock()
                    mock_serial_class.return_value = mock_serial

                    with patch.object(client, "_start_message_dispatcher"):
                        await client.connect()

            # Test notification handling
            mock_notification = Mock()
            mock_notification.type = "test"

            with (
                patch.object(client.notification_handler._parser, "get_notification_type", return_value="test"),
                patch.object(client.notification_handler._parser, "parse_notification", return_value=mock_notification),
            ):
                await client.notification_handler.handle_notification("notify test data=value")

            assert len(received_notifications) == 1
            assert received_notifications[0].type == "test"
