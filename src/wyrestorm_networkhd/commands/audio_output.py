from typing import Literal

from ._response_helpers import require_command_mirror


class AudioOutputCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 9.1 Volume Control – Analog Audio
    # Use this command to alter the audio volume level of an endpoint analog audio output. Where available at the NetworkHD
    # endpoints, this will alter the audio volume exiting an analog audio port.
    # =============================================================

    async def config_set_device_audio_volume_analog(
        self, level: Literal["up", "down", "mute", "unmute"], device: str
    ) -> bool:
        """Alter the analog audio volume from a TX or RX

        Args:
            level: Volume command
                up: Increase the audio volume level
                down: Decrease the audio volume level
                mute: Mute the audio output
                unmute: Unmute the audio output
            device: Device reference
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX

        Notes:
            NetworkHD 400 Series endpoints only support volume up and volume down commands and not the mute and unmute commands.
            NetworkHD 100/200 Series endpoints only support mute and unmute and not the volume up and down commands.
            The factory default volume level for a NetworkHD endpoint is maximum volume level (unmuted).
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            level: volume command
                up: up
                down: down
                mute: mute
                unmute: unmute

        Command structure:
            config set device audio volume <level> analog <TX|RX>

        Response structure (command mirror):
            config set device audio volume <level> analog <TX|RX>

        Command Example: Decrease the audio volume level from decoder
            config set device audio volume down analog display1

        Response Example: Command acknowledgment
            config set device audio volume down analog display1
        """
        command = f"config set device audio volume {level} analog {device}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)
