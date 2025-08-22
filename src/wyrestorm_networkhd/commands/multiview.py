from typing import Literal

from ._response_helpers import require_command_mirror, require_success_indicator


class MultiviewCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 11.1 Multiview Decoders – Single Encoder
    # Use this command to apply a single source to a display. Where available at the NetworkHD endpoints, equivalent commands to
    # stream matrix switching can be achieved on Multiview decoders.
    # =============================================================

    async def mview_set_single(self, rx: str, tx: str, mode: Literal["tile", "overlay"] | None = None) -> bool:
        """Assign a single TX audio and video stream to a Multiview RX

        Args:
            rx: Decoder reference (alias or hostname)
            tx: Encoder reference (alias or hostname)
            mode: Optional tile mode
                tile: Use for non-overlapping tile layouts
                overlay: Use for overlapping tile layouts

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-220-RX, NHD-250-RX

        Notes:
            Multiview only decoders do not respond to matrix set commands found in section 6 – Media Stream Matrix Switch Commands, equivalent functions can be applied using this command.
            The use of tile or overlay in the command is optional and can be used where switching to/from Preset or Custom Tile layouts where a small switching delay advantage can be obtained when staying in the same mode.
            For NetworkHD 600, use matrix set commands found in section 6 – Media Stream Matrix Switch Commands.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            tile: Use for non-overlapping tile layouts
            overlay: Use for overlapping tile layouts

        Command structure:
            mview set <RX> ([tile|overlay]) <TX>

        Response structure:
            mview set <RX> ([tile|overlay]) <TX> [success|failure]

        Command Example: Assign a TX to an RX
            mview set display1 source1

        Response Example: Command acknowledgment
            mview set display1 source1 success
        """
        command = f"mview set {rx} {mode} {tx}" if mode else f"mview set {rx} {tx}"
        response = await self.client.send_command(command)
        return require_success_indicator(response)

    # =============================================================
    # 11.2 Multiview Decoders – Preset Tile Layouts
    # Use this command to apply preset Multiview layouts to a decoder. Where available at the NetworkHD endpoints, Multiview layouts
    # configured in the NetworkHD Console software utility can be recalled and applied to NetworkHD decoders.
    # =============================================================

    async def mscene_active(self, rx: str, lname: str) -> bool:
        """Apply a preset Multiview layout to an RX

        Args:
            rx: Decoder reference (alias or hostname)
            lname: Preconfigured layout name

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-220-RX, NHD-250-RX
            NHD-0401-MV
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Multiview layout names are given to preset layouts when they are created. These are listed and selected in NetworkHD Console.
            When Multiview layouts are configured, the layout tiles will have default encoders assigned to them.
            Layout naming for NHD-0401-MV can't be customized.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            lname: Preconfigured layout name

        Command structure:
            mscene active <RX> <lname>

        Response structure:
            mscene active <RX> <lname> [success|failure]

        Command Example: Apply a layout to a decoder
            mscene active display1 gridlayout

        Response Example: Command acknowledgment
            mscene active display1 gridlayout success
        """
        command = f"mscene active {rx} {lname}"
        response = await self.client.send_command(command)
        return require_success_indicator(response, expected_start=f"mscene active {rx} {lname}")

    async def mscene_change(self, rx: str, lname: str, tile: int, tx: str) -> bool:
        """Change the TX for a tile within a preset Multiview layout

        Args:
            rx: Decoder reference (alias or hostname)
            lname: Preconfigured layout name
            tile: Tile reference
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-220-RX, NHD-250-RX
            NHD-0401-MV
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command is effective immediately and does not save to the default Scene.
            Tile reference is the integer reference inferred to the target tile when the layout is created. This value can be referenced when configuring the layout in NetworkHD Console.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            lname: Preconfigured layout name
            tile: Tile reference

        Command structure:
            mscene change <RX> <lname> <tile> <TX>

        Response structure:
            mscene change <RX> <lname> <tile> <TX> [success|failure]

        Command Example: Reposition and resize a window within a scene
            mscene change display1 gridlayout 1 source1

        Response Example: Command acknowledgment
            mscene change display1 gridlayout 1 source1 success
        """
        command = f"mscene change {rx} {lname} {tile} {tx}"
        response = await self.client.send_command(command)
        return require_success_indicator(response, expected_start=f"mscene change {rx} {lname} {tile} {tx}")

    async def mscene_set_audio(
        self, rx: str, lname: str, audio_mode: Literal["window", "separate"], target: str | int
    ) -> bool:
        """Change the audio mode within a preset Multiview layout

        Args:
            rx: Decoder reference (alias or hostname)
            lname: Preconfigured layout name
            audio_mode: Audio mode
                window: RX audio follows video for Tile
                separate: RX audio is assigned to TX directly
            target: Target reference
                tile: Tile reference (integer) when audio_mode is "window"
                tx: Encoder reference (alias or hostname) when audio_mode is "separate"

        Returns:
            bool: True if command was successful

        Raises:
            ValueError: If target type doesn't match audio_mode (int for window, str for separate)

        Command applies to:
            NHD-220-RX, NHD-250-RX

        Notes:
            Command saves audio mode to RX and is not effective immediately. Use the mscene active command to apply the audio mode.
            Tile reference is the integer reference inferred to the target tile when the layout is created. This value can be referenced when configuring the layout in NetworkHD Console.
            For NetworkHD 600 Series, use the relevant audio commands found in section 6.3 – Stream Matrix Switching – Audio Stream Breakaway.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            lname: Preconfigured layout name
            tile: Tile reference
            window: RX audio follows video for Tile
            separate: RX audio is assigned to TX directly

        Command structure:
            mscene set audio <RX> <lname> [window|separate] <tile|TX>

        Response structure:
            mscene set audio <RX> <lname> [window|separate] <tile|TX> [success|failure]

        Command Example: Apply RX audio to a specific TX
            mscene set audio display1 gridlayout separate source1

        Response Example: Command acknowledgment
            mscene set audio display1 gridlayout separate source1 success

        Command Example: Apply RX audio to a specific tile
            mscene set audio display1 gridlayout window 1

        Response Example: Command acknowledgment
            mscene set audio display1 gridlayout window 1 success
        """
        if audio_mode == "window" and not isinstance(target, int):
            raise ValueError("target must be an integer (tile reference) when audio_mode is 'window'")
        elif audio_mode == "separate" and not isinstance(target, str):
            raise ValueError("target must be a string (encoder reference) when audio_mode is 'separate'")

        command = f"mscene set audio {rx} {lname} {audio_mode} {target}"
        response = await self.client.send_command(command)
        return require_success_indicator(
            response, expected_start=f"mscene set audio {rx} {lname} {audio_mode} {target}"
        )

    async def config_set_device_info_audio_src(
        self, input_source: Literal["hdmiin1", "hdmiin2", "hdmiin3", "hdmiin4"], rx: str
    ) -> bool:
        """Change the audio source

        Args:
            input_source:
                hdmiin1
                hdmiin2
                hdmiin3
                hdmiin4
            rx: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-0401-MV
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            input: hdmiin1, hdmiin2, hdmiin3 or hdmiin4

        Command structure:
            config set device info audio_src=<input> <RX>

        Response structure:
            config set device info audio_src=<input> <RX>

        Command Example: Set the HDMI input 1 as audio source
            config set device info audio_src=hdmiin1 0401-MV

        Response Example: Command acknowledgment
            config set device info audio_src=hdmiin1 0401-MV
        """
        command = f"config set device info audio_src={input_source} {rx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_info_audio_mute(
        self, audio_type: Literal["audio_mute_hdmi", "audio_mute_av"], mute_state: Literal["mute", "unmute"], rx: str
    ) -> bool:
        """Mute the audio signal

        Args:
            audio_type: Audio type to control
                audio_mute_hdmi: use for control HDMI audio signal
                audio_mute_av: use for control analog audio output
            mute_state: Mute state
                mute: Mute the audio output
                unmute: Unmute the audio output
            rx: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-0401-MV

        Notes:
            Using this command you can mute the HDMI audio signal or audio signal on the Analog Audio Output.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            audio_mute_hdmi: use for control HDMI audio signal
            audio_mute_av: use for control analog audio output

        Command structure:
            config set device info [audio_mute_hdmi|audio_mute_av]=[mute|unmute] <RX>

        Response structure:
            config set device info [audio_mute_hdmi|audio_mute_av]=[mute|unmute] <RX>

        Command Example: mute the HDMI audio output
            config set device info audio_mute_hdmi=mute 0401-MV

        Response Example: Command acknowledgment
            config set device info audio_mute_hdmi=mute 0401-MV
        """
        command = f"config set device info {audio_type}={mute_state} {rx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 11.3 Multiview Decoders – Custom Tile Layouts
    # Use this command to apply a custom Multiview layout to a decoder. Where available at the NetworkHD endpoints, custom
    # Multiview layouts can be created and applied to NetworkHD decoders.
    # =============================================================

    class TileConfig:
        """Configuration for a single tile in a custom multiview layout"""

        def __init__(
            self, tx: str, x: int, y: int, width: int, height: int, scaling: Literal["fit", "stretch"] = "fit"
        ):
            self.tx = tx
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.scaling = scaling

        def to_string(self) -> str:
            return f"{self.tx}:{self.x}_{self.y}_{self.width}_{self.height}:{self.scaling}"

    async def mview_set_custom(self, rx: str, mode: Literal["tile", "overlay"], tiles: list[TileConfig]) -> bool:
        """Apply a custom Multiview layout to an RX

        Args:
            rx: Decoder reference (alias or hostname)
            mode: Layout mode
                tile: Use for non-overlapping tile layouts
                overlay: Use for overlapping tile layouts
            tiles: List of tile configurations

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-220-RX, NHD-250-RX

        Notes:
            Command is effective immediately but does not save to NHD-CTL.
            Tile horizontal and vertical start pixels are relative to the top left canvas pixel but can be no greater that the bottom right canvas pixel.
            Tile size must ensure that the tile will not exceed the available pixels in the canvas.
            overlay mode is only supported on NetworkHD decoders that support this feature.
            fit scaling will fill the tile with the source video and not distort the source video, but it may result in some missing video if the aspect ratio is not matched to the tile.
            stretch scaling will fill the tile with the source video, but it may introduce distortion if the aspect ratio is not matched to the tile.
            The tile layer order follows the order in which tiles are defined. The topmost tile is the first to be defined.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            Xn: Tile's top left pixel – horizontal reference
            Yn: Tile's top left pixel – vertical reference
            Wn: Tile horizontal size in pixels
            Hn: Tile vertical size in pixels
            tile: Use for non-overlapping tile layouts
            overlay: Use for overlapping tile layouts
            fit: Scales source to fit window without distortion
            stretch: Scales source to fit window completely

        Command structure:
            mview set <RX> [tile|overlay] <TX1>:<X1>_<Y1>_<W1>_<H1>:[fit|stretch] <TX2>:<X2>_<Y2>_<W2>_<H2>:[fit|stretch] … <TXn>:<Xn>_<Yn>_<Wn>_<Hn>:[fit|stretch]>

        Response structure:
            mview set <RX> [tile|overlay] <TX1>:<X1>_<Y1>_<W1>_<H1>:[fit|stretch] <TX2>:<X2>_<Y2>_<W2>_<H2>:[fit|stretch] … <TXn>:<Xn>_<Yn>_<Wn>_<Hn>:[fit|stretch]> [success|failure]

        Command Example: Apply a 2x2 tile-mode layout to an RX
            mview set display1 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit

        Response Example: Command acknowledgment
            mview set display1 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit success

        Command Example: Apply a PiP overlay-mode layout to an RX
            mview set display1 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit

        Response Example: Command acknowledgment
            mview set display1 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit success
        """
        tile_strings = [tile.to_string() for tile in tiles]
        tile_config = " ".join(tile_strings)
        command = f"mview set {rx} {mode} {tile_config}"
        response = await self.client.send_command(command)
        return require_success_indicator(response)

    async def mview_set_audio_custom(self, rx: str, tx: str) -> bool:
        """Change the audio source within a custom Multiview layout

        Args:
            rx: Decoder reference (alias or hostname)
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-220-RX, NHD-250-RX

        Notes:
            Command is effective immediately but does not save to NHD-CTL.
            Default behavior for an RX using a custom Multiview layout is to have no audio.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname

        Command structure:
            mview set audio <RX> separate <TX>

        Response structure:
            mview set audio <RX> separate <TX> [success|failure]

        Command Example: Apply RX audio to a specific TX
            mview set audio display1 separate source1

        Response Example: Command acknowledgment
            mview set audio display1 separate source1 success
        """
        command = f"mview set audio {rx} separate {tx}"
        response = await self.client.send_command(command)
        expected_start = f"mview set audio {rx} separate {tx}"
        return require_success_indicator(response, expected_start)

    # =============================================================
    # 11.4 Multiview Decoders – PiP position
    # =============================================================

    async def mscene_set_pipposition(self, rx: str, position: Literal[0, 1, 2, 3]) -> bool:
        """Set the position of PiP tile

        Args:
            rx: Decoder reference (alias or hostname)
            position: PiP position
                0: top left
                1: bottom left
                2: top right
                3: bottom right

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-0401-MV
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            Position: 0: top left, 1: bottom left, 2: top right, 3: bottom right

        Command structure:
            mscene set pipposition <RX> 2-2 <position>

        Response structure:
            mscene set pipposition <RX> 2-2 <position> [success|failure]

        Command Example: Set pip position to top left corner
            mscene set pipposition 0401-MV 2-2 0

        Response Example: Command acknowledgment
            mscene set pipposition 0401-MV 2-2 0 success
        """
        command = f"mscene set pipposition {rx} 2-2 {position}"
        response = await self.client.send_command(command)
        expected_start = f"mscene set pipposition {rx} 2-2 {position}"
        return require_success_indicator(response, expected_start)
