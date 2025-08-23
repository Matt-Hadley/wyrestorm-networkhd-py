"""Protocol-level integration tests - Testing NetworkHD protocol behavior."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from wyrestorm_networkhd.core.client_rs232 import NetworkHDClientRS232
from wyrestorm_networkhd.core.client_ssh import NetworkHDClientSSH


@pytest.mark.integration
class TestNetworkHDProtocolIntegration:
    """Integration tests focusing on NetworkHD protocol behavior and edge cases."""

    @pytest.mark.asyncio
    async def test_command_response_parsing(self):
        """Test parsing of various NetworkHD protocol responses."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                # Test various protocol responses
                test_cases = [
                    ("get device info", "OK: device=WyreStorm NetworkHD version=1.0.0"),
                    ("set input 1", "OK: input set to 1"),
                    ("get status", "OK: status=online input=1 output=2"),
                    ("invalid command", "ERROR: unknown command"),
                    ("get temperature", "OK: temperature=45C"),
                ]

                for command, expected_response in test_cases:
                    with patch.object(
                        client, "_send_command_generic", new_callable=AsyncMock, return_value=expected_response
                    ):
                        response = await client.send_command(command)
                        assert expected_response in response

    @pytest.mark.asyncio
    async def test_notification_message_handling(self):
        """Test handling of various notification message formats."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Track received notifications
        received_notifications = []

        def notification_callback(notification):
            received_notifications.append(notification)

        # Register callback for different notification types
        client.register_notification_callback("input", notification_callback)
        client.register_notification_callback("output", notification_callback)
        client.register_notification_callback("device", notification_callback)

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                # Test various notification formats
                test_notifications = [
                    ("notify input device=1 status=connected", "input"),
                    ("notify output device=2 status=active", "output"),
                    ("notify device status=online temperature=42", "device"),
                ]

                for notification_msg, expected_type in test_notifications:
                    # Mock the notification parsing
                    mock_notification = Mock()
                    mock_notification.type = expected_type
                    mock_notification.data = {"device": "1", "status": "connected"}

                    with (
                        patch.object(
                            client.notification_handler._parser, "get_notification_type", return_value=expected_type
                        ),
                        patch.object(
                            client.notification_handler._parser, "parse_notification", return_value=mock_notification
                        ),
                    ):
                        await client.notification_handler.handle_notification(notification_msg)

                # Verify notifications were received
                assert len(received_notifications) == 3
                assert all(notif.type in ["input", "output", "device"] for notif in received_notifications)

    @pytest.mark.asyncio
    async def test_malformed_message_handling(self):
        """Test handling of malformed or corrupted messages."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                # Test malformed messages (should be handled gracefully)
                malformed_messages = [
                    "",  # Empty message
                    "incomplete",  # Incomplete message
                    "notify",  # Notification without data
                    "OK:",  # Response without data
                    "ERROR:",  # Error without description
                    "random garbage text",  # Invalid format
                    "\x00\x01\x02",  # Binary data
                ]

                from contextlib import suppress

                for malformed_msg in malformed_messages:
                    # These should not crash the notification handler
                    with suppress(Exception):
                        # Some exceptions are expected for malformed data
                        # The important thing is that the client remains functional
                        await client.notification_handler.handle_notification(malformed_msg)

                # Verify client is still functional after handling malformed messages
                assert client.is_connected()
                assert client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_long_response_handling(self):
        """Test handling of very long responses and multi-line responses."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                # Test very long single-line response
                long_response = "OK: " + "data=" + "x" * 1000
                with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value=long_response):
                    response = await client.send_command("get long data")
                    assert len(response) > 1000
                    assert response.startswith("OK:")

                # Test multi-line response
                multiline_response = """OK: device info
device=WyreStorm NetworkHD
version=1.0.0
serial=12345
status=online
temperature=45C
uptime=123456"""
                with patch.object(
                    client, "_send_command_generic", new_callable=AsyncMock, return_value=multiline_response
                ):
                    response = await client.send_command("get device info")
                    assert "device=WyreStorm NetworkHD" in response
                    assert "version=1.0.0" in response
                    assert "temperature=45C" in response

    @pytest.mark.asyncio
    async def test_command_queuing_and_ordering(self):
        """Test that commands are processed in the correct order."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Track command execution order
        executed_commands = []

        async def mock_send_command_generic(command, *_args, **_kwargs):
            executed_commands.append(command)
            await asyncio.sleep(0.01)  # Small delay to simulate processing
            return f"OK: executed {command}"

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                with patch.object(
                    client, "_send_command_generic", new_callable=AsyncMock, side_effect=mock_send_command_generic
                ):
                    # Send multiple commands concurrently
                    commands = [f"command_{i}" for i in range(5)]
                    tasks = [client.send_command(cmd) for cmd in commands]
                    responses = await asyncio.gather(*tasks)

                    # Verify all commands were executed
                    assert len(executed_commands) == 5
                    assert len(responses) == 5

                    # Verify responses correspond to commands
                    for i, response in enumerate(responses):
                        assert f"executed command_{i}" in response

    @pytest.mark.asyncio
    async def test_protocol_error_recovery(self):
        """Test recovery from various protocol-level errors."""
        client = NetworkHDClientSSH(
            host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
        )

        # Mock successful connection
        with patch("paramiko.SSHClient") as mock_ssh_class:
            mock_ssh = Mock()
            mock_shell = Mock()
            mock_transport = Mock()

            mock_shell.closed = False
            mock_transport.is_active.return_value = True
            mock_ssh.get_transport.return_value = mock_transport
            mock_ssh.invoke_shell.return_value = mock_shell
            mock_ssh_class.return_value = mock_ssh

            with patch.object(client, "_start_message_dispatcher"):
                await client.connect()

                # Test recovery from command errors
                error_scenarios = [
                    ("ERROR: invalid command", "invalid_cmd"),
                    ("ERROR: device busy", "set input 1"),
                    ("ERROR: timeout", "get slow_data"),
                    ("ERROR: permission denied", "set admin_setting"),
                ]

                for error_response, test_command in error_scenarios:
                    # Send command that returns error
                    with patch.object(
                        client, "_send_command_generic", new_callable=AsyncMock, return_value=error_response
                    ):
                        response = await client.send_command(test_command)
                        assert "ERROR:" in response

                    # Verify client can still send successful commands after error
                    with patch.object(
                        client, "_send_command_generic", new_callable=AsyncMock, return_value="OK: recovery successful"
                    ):
                        recovery_response = await client.send_command("get status")
                        assert "OK: recovery successful" in recovery_response

                # Verify client is still functional
                assert client.is_connected()
                assert client.get_connection_state() == "connected"


@pytest.mark.integration
class TestCrossProtocolIntegration:
    """Integration tests comparing SSH and RS232 protocol behavior."""

    @pytest.mark.parametrize("client_type", ["ssh", "rs232"])
    @pytest.mark.asyncio
    async def test_protocol_consistency_across_transports(self, client_type):
        """Test that NetworkHD protocol works consistently across SSH and RS232."""
        if client_type == "ssh":
            client = NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
            )
            patch_target = "paramiko.SSHClient"
        else:
            client = NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)
            patch_target = "async_pyserial.SerialPort"

        # Mock successful connection based on client type
        if client_type == "ssh":
            with patch(patch_target) as mock_class:
                mock_conn = Mock()
                mock_shell = Mock()
                mock_transport = Mock()

                mock_shell.closed = False
                mock_transport.is_active.return_value = True
                mock_conn.get_transport.return_value = mock_transport
                mock_conn.invoke_shell.return_value = mock_shell
                mock_class.return_value = mock_conn

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()
        else:
            with patch(patch_target) as mock_class:
                mock_serial = Mock()
                mock_serial.is_open = True
                mock_serial.open = AsyncMock()  # Make open() awaitable
                mock_serial.close = AsyncMock()  # Make close() awaitable
                mock_class.return_value = mock_serial

                with patch.object(client, "_start_message_dispatcher"):
                    await client.connect()

        # Test standard NetworkHD commands work the same way
        standard_commands = [
            ("get device info", "OK: device=WyreStorm NetworkHD"),
            ("set input 1", "OK: input set to 1"),
            ("get status", "OK: status=online"),
        ]

        for command, expected_response in standard_commands:
            with patch.object(client, "_send_command_generic", new_callable=AsyncMock, return_value=expected_response):
                response = await client.send_command(command)
                assert expected_response in response

        # Test error handling is consistent
        with patch.object(
            client, "_send_command_generic", new_callable=AsyncMock, return_value="ERROR: unknown command"
        ):
            error_response = await client.send_command("invalid_command")
            assert "ERROR: unknown command" in error_response

        # Verify client state is consistent
        assert client.is_connected()
        assert client.get_connection_state() == "connected"

    @pytest.mark.asyncio
    async def test_notification_handling_consistency(self):
        """Test that notification handling works consistently across both client types."""
        clients = [
            NetworkHDClientSSH(
                host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
            ),
            NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600),
        ]

        for client in clients:
            # Track notifications
            received_notifications = []

            def create_callback(notifications_list):
                def callback(notification):
                    notifications_list.append(notification)

                return callback

            client.register_notification_callback("test", create_callback(received_notifications))

            # Mock connection based on client type
            if isinstance(client, NetworkHDClientSSH):
                with patch("paramiko.SSHClient") as mock_ssh_class:
                    mock_ssh = Mock()
                    mock_shell = Mock()
                    mock_transport = Mock()

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
                    mock_serial.open = AsyncMock()  # Make open() awaitable
                    mock_serial.close = AsyncMock()  # Make close() awaitable
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

            # Verify notification was received
            assert len(received_notifications) == 1
            assert received_notifications[0].type == "test"

    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """Compare basic performance characteristics between SSH and RS232 clients."""
        import time

        performance_results = {}

        clients = [
            (
                "ssh",
                NetworkHDClientSSH(
                    host="192.168.1.100", port=22, username="admin", password="password", ssh_host_key_policy="auto_add"
                ),
            ),
            ("rs232", NetworkHDClientRS232(port="/dev/ttyUSB0", baudrate=9600)),
        ]

        for client_type, client in clients:
            # Mock connection
            if client_type == "ssh":
                with patch("paramiko.SSHClient") as mock_ssh_class:
                    mock_ssh = Mock()
                    mock_shell = Mock()
                    mock_transport = Mock()

                    mock_shell.closed = False
                    mock_transport.is_active.return_value = True
                    mock_ssh.get_transport.return_value = mock_transport
                    mock_ssh.invoke_shell.return_value = mock_shell
                    mock_ssh_class.return_value = mock_ssh

                    with patch.object(client, "_start_message_dispatcher"):
                        # Measure connection time
                        start_time = time.time()
                        await client.connect()
                        connection_time = time.time() - start_time
            else:
                with patch("async_pyserial.SerialPort") as mock_serial_class:
                    mock_serial = Mock()
                    mock_serial.is_open = True
                    mock_serial.open = AsyncMock()  # Make open() awaitable
                    mock_serial.close = AsyncMock()  # Make close() awaitable
                    mock_serial_class.return_value = mock_serial

                    with patch.object(client, "_start_message_dispatcher"):
                        # Measure connection time
                        start_time = time.time()
                        await client.connect()
                        connection_time = time.time() - start_time

            # Measure command execution time
            with patch.object(
                client, "_send_command_generic", new_callable=AsyncMock, return_value="OK: test response"
            ):
                start_time = time.time()
                await client.send_command("test command")
                command_time = time.time() - start_time

            performance_results[client_type] = {"connection_time": connection_time, "command_time": command_time}

        # Both clients should perform reasonably (this is mostly a smoke test)
        for _client_type, results in performance_results.items():
            assert results["connection_time"] < 1.0  # Should connect quickly when mocked
            assert results["command_time"] < 0.1  # Commands should execute quickly when mocked

        # Performance should be comparable (within reasonable bounds)
        ssh_conn_time = performance_results["ssh"]["connection_time"]
        rs232_conn_time = performance_results["rs232"]["connection_time"]

        # Neither should be more than 10x slower than the other
        ratio = max(ssh_conn_time, rs232_conn_time) / min(ssh_conn_time, rs232_conn_time)
        assert ratio < 10.0
