from typing import Literal

from ._response_helpers import require_command_mirror


class APINotificationsCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 12.1 Enable / Disable Notifications
    # Use this command to enable or disable API notifications. Where available, some API notifications can be suppressed to remove
    # large amounts of data being sent to the 3rd-party control system.
    # =============================================================

    async def config_set_device_cec_notify(
        self, state: Literal["on", "off"], devices: str | list[str] | Literal["ALL_DEV", "ALL_TX", "ALL_RX"]
    ) -> bool:
        """Enable or disable the CEC API notifications

        Args:
            state: Notification state
                on: Enable CEC API notifications
                off: Disable CEC API notifications
            devices: Device reference or bulk selector
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)
                bulk: Multiple devices
                    ALL_DEV: All endpoints
                    ALL_TX: All encoders
                    ALL_RX: All decoders

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            Some API notifications can be suppressed to remove large amounts of data being sent to the 3rd-party control system.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            bulk: multiple devices
            ALL_DEV: all endpoints
            ALL_TX: all encoders
            ALL_RX: all decoders

        Command structure:
            config set device cec notify [on|off] <TX|RX|bulk>

        Response structure (command mirror):
            config set device cec notify [on|off] <TX|RX|bulk>

        Command Example: Turn on CEC notifications for all RX
            config set device cec notify on ALL_RX

        Response Example: Command acknowledgment
            config set device cec notify on ALL_RX
        """
        device_list = " ".join(devices) if isinstance(devices, list) else devices

        command = f"config set device cec notify {state} {device_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)


# =============================================================
# 12.2 Endpoint Notifications
# See models.notifications for notification data classes and parsers
# =============================================================
