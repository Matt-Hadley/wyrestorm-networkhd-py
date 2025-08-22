from typing import Literal

from ._response_helpers import require_command_mirror


class VideoStreamTextOverlayCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 15. Video Stream Text Overlay
    # =============================================================

    async def config_set_device_osd_param(
        self, text: str, position_x: int, position_y: int, text_color: str, text_size: int, tx: str
    ) -> bool:
        """Configure Text Overlay

        Args:
            text: The text to be displayed
            position_x: X coordinate of text; must be value between 0~1920
            position_y: Y coordinate of text; must be value between 0~1080
            text_color: Color of text in hex format
                Red: FFFF0000 (NHD-110/140-TX) or FC00 (NHD-200-TX)
                White: FFFFFFFF (NHD-110/140-TX) or FFFF (NHD-200-TX)
                Black: FF000000 (NHD-110/140-TX)
                Purple: FFFF00FF (NHD-110/140-TX)
                Blue: FF0000FF (NHD-110/140-TX)
                Green: FF00FFFF (NHD-110/140-TX) or BB00 (NHD-200-TX)
                Yellow: FF00 (NHD-200-TX)
                Gray: BDEF (NHD-200-TX)
            text_size: Value between 1-4
            tx: Hostname or alias of encoder

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-140-TX, NHD-200-TX

        Notes:
            NHD-200-TX hex format uses 4 characters vs 8 with NHD-110 & 140-TX. Use the format below if using an NHD-200-TX:
            Red: FC00
            White: FFFF
            Yellow: FF00
            Gray: BDEF
            Green: BB00
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            text: The text to be displayed
            position_x: X coordinate of text; must be value between 0~1920
            position_y: Y coordinate of text; must be value between 0~1080
            text_color: Color of text in hex format, examples below:
                Red: FFFF0000
                White: FFFFFFFF
                Black: FF000000
                Purple: FFFF00FF
                Blue: FF0000FF
                Green: FF00FFFF
                Note: NHD-200-TX hex format uses 4 characters vs 8 with NHD-110 & 140-TX. Use the format below if using an NHD-200-TX:
                Red: FC00
                White: FFFF
                Yellow: FF00
                Gray: BDEF
                Green: BB00
            text_size: Value between 1-4
            TX: Hostname or alias of encoder

        Command structure:
            config set device osd param <text> <position_x> <position_y> <text_color> <text_size> <TX>

        Response structure:
            config set device osd param <text> <position_x> <position_y> <text_color> <text_size> <TX>

        Command Example: Get list of all Scenes
            config set device osd param Hello 0 0 FFFFFFFF 1 Input1

        Response Example: Return data
            receive: config set device osd param Hello 0 0 FFFFFFFF 1 Input1
        """
        # Validate position parameters
        if not (0 <= position_x <= 1920):
            raise ValueError(f"position_x must be between 0 and 1920, got: {position_x}")
        if not (0 <= position_y <= 1080):
            raise ValueError(f"position_y must be between 0 and 1080, got: {position_y}")
        if not (1 <= text_size <= 4):
            raise ValueError(f"text_size must be between 1 and 4, got: {text_size}")

        command = f"config set device osd param {text} {position_x} {position_y} {text_color} {text_size} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_osd(self, state: Literal["on", "off"], tx: str) -> bool:
        """Enable/Disable Text Overlay

        Args:
            state: Overlay state
                on: Enable text overlay
                off: Disable text overlay
            tx: Hostname or alias of encoder

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-140-TX, NHD-200-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            on: Enable text overlay
            off: Disable text overlay
            TX: Hostname or alias of encoder

        Command structure:
            config set device osd <on|off> <TX>

        Response structure:
            config set device osd <on|off> <TX>

        Command Example: Get list of all Scenes
            config set device osd on Input1

        Response Example: Return data
            receive: config set device osd on Input1
        """
        command = f"config set device osd {state} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # Color Helper Methods
    # Get hex color code for common colors based on device type
    # =============================================================

    @staticmethod
    def get_color_hex(
        color: Literal["red", "white", "black", "purple", "blue", "green", "yellow", "gray"],
        device_type: Literal["nhd110_140", "nhd200"] = "nhd110_140",
    ) -> str:
        """Get hex color code for common colors based on device type

        Args:
            color: Color name
            device_type: Device type
                nhd110_140: For NHD-110/140-TX
                nhd200: For NHD-200-TX

        Returns:
            Hex color code string

        Raises:
            ValueError: If the specified color is not available for the device type
        """
        if device_type == "nhd110_140":
            colors = {
                "red": "FFFF0000",
                "white": "FFFFFFFF",
                "black": "FF000000",
                "purple": "FFFF00FF",
                "blue": "FF0000FF",
                "green": "FF00FFFF",
            }
        else:  # nhd200
            colors = {"red": "FC00", "white": "FFFF", "yellow": "FF00", "gray": "BDEF", "green": "BB00"}

        if color not in colors:
            available_colors = ", ".join(colors.keys())
            raise ValueError(f"Color '{color}' not available for {device_type}. Available colors: {available_colors}")

        return colors[color]
