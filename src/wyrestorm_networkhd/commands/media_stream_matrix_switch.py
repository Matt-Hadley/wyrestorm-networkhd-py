from typing import Literal

from ._response_helpers import require_command_mirror


class MediaStreamMatrixSwitchCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 6.1 Stream Matrix Switching – All Media
    # Use this command to switch all primary media streams available to the NetworkHD endpoints simultaneously. Where available at
    # the NetworkHD endpoints, this will include the switching at the same time of primary video, primary audio, RS-232, Infrared and
    # USB between the TX and the RX.
    # =============================================================

    async def matrix_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign all primary TX media streams to RX(s)

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-TX/RX, NHD-120-IW-TX, NHD-124-TX, NHD-150-RX, NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX
            NHD-400-TX/RX, NHD-400-E-TX/RX, NHD-400-DNT-TX, NHD-400-IW-TX, NHD-500-TX/RX, NHD-500-E-TX/RX, NHD-500-DNT-TX, NHD-500-IW-TX, NHD-510-TX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            matrix set commands do not apply to Multiview, only decoders. See section 11- Multiview
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder to decoders
            matrix set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_set_null(self, rx: str | list[str]) -> bool:
        """Unassign all primary media streams from RX

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-RX, NHD-110-RX, NHD-100-RX, NHD-200-RX, NHD-210-RX
            NHD-500-RX, NHD-500-E-RX, NHD-400-RX, NHD-400-E-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            matrix set commands do not apply to Multiview, only decoders. See section 11- Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix set null <RX1> <RX2> … <RXn>

        Command Example: Unassign all media streams from RXs
            matrix set null display1 display2

        Response Example: Command acknowledgment
            matrix set null display1 display2
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 6.2 Stream Matrix Switching – Video Stream Breakaway
    # Use this command to switch video streams available to the NetworkHD endpoints independently. Commands will switch the video
    # streams only and leave the current assignment for all other media streams unaffected.
    # =============================================================

    async def matrix_video_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) video output to TX stream

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-TX, NHD-120-RX, NHD-110-TX, NHD-110-RX
            NHD-500-TX/RX, NHD-500-E-TX/RX, NHD-500-IW-TX, NHD-500-DNT-TX, NHD-510-TX, NHD-400-TX/RX, NHD-400-E-TX/RX, NHD-400-DNT-TX, NHD-400-TX-IW, NHD-0401-MV
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            matrix video set commands do not apply to Multiview, only decoders. See section 11- Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix video set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix video set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder video stream to decoders
            matrix video set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix video set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix video set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_video_set_null(self, rx: str | list[str]) -> bool:
        """Unassign video stream from RX

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-RX, NHD-110-RX
            NHD-500-RX, NHD-500-E-RX, NHD-400-RX, NHD-400-E-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            matrix video set commands do not apply to Multiview, only decoders. See section 11- Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix video set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix video set null <RX1> <RX2> … <RXn>

        Command Example: Unassign video stream from RXs
            matrix video set null display1 display2

        Response Example: Command acknowledgment
            matrix video set null display1 display2
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix video set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 6.3 Stream Matrix Switching – Audio Stream Breakaway
    # Use this command to switch audio streams available to the NetworkHD endpoints independently. Commands will switch the audio
    # streams only and leave the current assignment for all other media streams unaffected.
    # =============================================================

    async def matrix_audio_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) HDMI audio output to TX stream

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-TX, NHD-120-RX, NHD-110-TX, NHD-110-RX
            NHD-500-TX/RX, NHD-500-E-TX/RX, NHD-500-IW-TX, NHD-500-DNT-TX, NHD-510-TX, NHD-400-TX/RX, NHD-400-E-TX/RX, NHD-400-DNT-TX, NHD-400-TX-IW
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Analog audio output on a 100, 400 & 500 Series decoder will extract the HDMI audio at the decoder.
            HDMI audio on a 600 Series decoder will select the TX audio stream defined using the config set device audiosource
            command – see section 7.2 – Port Switching – Audio. The primary HDMI or DP audio stream is the factory default setting.
            Analog audio output on a 600 Series decoder will output the TX primary HDMI or DP audio stream if "dmix" is set using the
            config set audio2source command – see section 7.2 – Port Switching – Audio.
            Analog audio output on a 100, 200 and 400 Series decoder will convert 2 channel PCM audio only.
            Analog audio output on a 600 Series decoder can also downmix up to 8 channel PCM audio.
            matrix audio set commands do not apply to Multiview, only decoders. See section 11- Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix audio set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix audio set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder audio stream to decoders
            matrix audio set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix audio set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix audio set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_audio_set_null(self, rx: str | list[str]) -> bool:
        """Unassign RX(s) HDMI audio output to TX stream

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Analog audio output on a 100, 200 and 400 Series decoder will extract the HDMI audio at the decoder.
            HDMI audio on a 600 Series decoder will select the TX audio stream defined using the config set device audiosource
            command – see section 7.2 – Port Switching – Audio. The primary HDMI or DP audio stream is the factory default setting.
            Analog audio output on a 600 Series decoder will output the TX primary HDMI or DP audio stream if "dmix" is set using the
            config set audio2source command – see section 7.2 – Port Switching – Audio.
            matrix audio set commands do not apply to Multiview, only decoders. See section 11- Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix audio set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix audio set null <RX1> <RX2> … <RXn>

        Command Example: Unassign encoder audio stream to decoders
            matrix audio set null display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix audio set null display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix audio set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_audio2_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) analog audio output to TX analog audio stream

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Command will only be effective if "analog" is set using the config set audio2source command – see section 7.2 – Port
            Switching – Audio. This is the factory default setting.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix audio2 set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix audio2 set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder audio stream to decoders
            matrix audio2 set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix audio2 set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix audio2 set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_audio2_set_null(self, rx: str | list[str]) -> bool:
        """Unassign RX(s) analog audio output to TX analog audio stream

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Command will only be effective if "analog" is set using the config set audio2source command – see section 7.2 – Port
            Switching – Audio. This is the factory default setting.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix audio2 set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix audio2 set null <RX1> <RX2> … <RXn>

        Command Example: Unassign encoder audio stream to decoders
            matrix audio2 set null display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix audio2 set null display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix audio2 set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_audio3_set(self, rx: str, tx: str) -> bool:
        """Assign RX(s) ARC stream to TX

        Args:
            rx: Decoder reference (alias or hostname)
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-500-TX, NHD-500-RX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix audio3 set <RX1> <TX1>

        Response structure (command mirror):
            matrix audio3 set <RX1> <TX1>

        Command Example: Assign decoder ARC stream to encoder
            matrix audio3 set Display1 Source1

        Response Example: Return data
            matrix audio3 set Display1 Source1
        """
        command = f"matrix audio3 set {rx} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 6.4 Stream Matrix Switching – USB Stream Breakaway
    # Use this command to switch USB streams available to the NetworkHD endpoints independently. Commands will switch the USB
    # streams only and leave the current assignment for all other media streams unaffected.
    # =============================================================

    async def matrix_usb_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) USB ports to TX

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX, NHD-510-TX, NHD-500-IW-TX, NHD-500-DNT-TX
            NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            NHD-600 devices only support a 1:1 USB communication, meaning only one RX can be linked to a TX USB host
            port.
            Multiple NHD-500-RX "USB 2.0" ports can be linked to a single TX USB host port, up to 7 devices.
            Command will always be effective for RX USB ports in KMoIP mode.
            Command will only be effective for RX USB ports in USBoIP mode if the TX has 4 or less USBoIP mode RX ports
            already assigned.
            To assign an endpoint USB mode – see section 7.3 Port Switching – USB Mode
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix usb set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix usb set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder USB port to decoders
            matrix usb set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix usb set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix usb set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_usb_set_null(self, rx: str | list[str]) -> bool:
        """Unassign RX(s) USB ports

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX, NHD-510-TX, NHD-500-IW-TX, NHD-500-DNT-TX
            NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix usb set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix usb set null <RX1> <RX2> … <RXn>

        Command Example: Unassign decoder usb ports
            matrix usb set null display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix usb set null display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix usb set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 6.5 Stream Matrix Switching – Infrared Stream Breakaway
    # Use this command to switch infrared streams available to the NetworkHD endpoints independently. Commands will switch the
    # infrared streams only and leave the current assignment for all other media streams unaffected.
    # =============================================================

    async def matrix_infrared_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) infrared ports to TX

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            Encoder to decoder(s) assignments link the IR channels in both directions - the IR receiver port on the encoder to the IR emitter
            port on the decoder simultaneously with the IR receiver port on the decoder to the IR emitter port on the encoder.
            To generate IR codes directly from an encoder or decoder using IR code Hex notation, see section 8.2 - Device Control – Custom
            Command Generation.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix infrared set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix infrared set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder IR ports to decoder IR ports
            matrix infrared set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix infrared set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix infrared set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_infrared_set_null(self, rx: str | list[str]) -> bool:
        """Unassign RX(s) infrared ports

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix infrared set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix infrared set null <RX1> <RX2> … <RXn>

        Command Example: Unassign decoder IR ports
            matrix infrared set null display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix infrared set null display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix infrared set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_infrared2_set(
        self, device: str, mode: Literal["single", "api", "all"], target_device: str | None = None
    ) -> bool:
        """Assign RX or TX infrared receiver port to endpoint(s) or API notification

        Args:
            device: TX or RX device reference (alias or hostname)
            mode: Operational mode
                single: Assign to endpoint (requires target_device)
                api: Assign to API notification
                all: Assign to all other endpoints
            target_device: TX or RX device reference (required for 'single' mode)

        Returns:
            bool: True if command was successful

        Raises:
            ValueError: If target_device is required but not provided for 'single' mode

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Assignments are in one direction, from endpoint IR receiver port to endpoint IR emitter port or API notification.
            For details on infrared API notifications, see section 12.2 – Endpoint Notifications.
            To generate IR codes directly from an encoder or decoder using IR code Hex notation, see section 8.2 - Device Control – Custom
            Command Generation.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            mode: Operational mode
                single: Assigned to endpoint
                api: Assigned to API notification
                all: Assigned to all other endpoints
                null: Assigned to no endpoints

        Command structure:
            matrix infrared2 set <TX|RX> <mode> (<TX|RX>)

        Response structure (command mirror):
            matrix infrared2 set <TX|RX> <mode> (<TX|RX>)

        Command Example 1: Assign encoder IR receiver port to decoder IR emitter port
            matrix infrared2 set source1 single display1

        Response Example: Command acknowledgment
            matrix infrared2 set source1 single display1

        Command Example 2: Assign encoder IR receiver port to encoder IR emitter port
            matrix infrared2 set source1 single source2

        Response Example: Command acknowledgment
            matrix infrared2 set source1 single source2

        Command Example 3: Assign decoder IR receiver port to API notification
            matrix infrared2 set display1 api

        Response Example: Command acknowledgment
            matrix infrared2 set display1 api

        Command Example 4: Assign encoder IR receiver port to all endpoint IR emitter ports
            matrix infrared2 set source1 all

        Response Example: Command acknowledgment
            matrix infrared2 set source1 all
        """
        if mode == "single" and target_device is None:
            raise ValueError("target_device is required when mode is 'single'")

        if mode == "single":
            command = f"matrix infrared2 set {device} single {target_device}"
        else:
            command = f"matrix infrared2 set {device} {mode}"

        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_infrared2_set_null(self, device: str) -> bool:
        """Unassign TX or RX infrared receiver port

        Args:
            device: Device reference (TX or RX alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname

        Command structure:
            matrix infrared2 set <TX|RX> null

        Response structure (command mirror):
            matrix infrared2 set <TX|RX> null

        Command Example: Unassign decoder IR receiver port
            matrix infrared2 set display1 null

        Response Example: Command acknowledgment
            matrix infrared2 set display1 null
        """
        command = f"matrix infrared2 set {device} null"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 6.6 Stream Matrix Switching – RS-232 Stream Breakaway
    # Use this command to switch RS-232 streams available to the NetworkHD endpoints independently. Commands will switch the RS-
    # 232 streams only and leave the current assignment for all other media streams unaffected.
    # =============================================================

    async def matrix_serial_set(self, tx: str, rx: str | list[str]) -> bool:
        """Assign RX(s) RS-232 ports to TX

        Args:
            tx: Encoder reference (alias or hostname)
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-400-TX-IW, NHD-400-RX, NHD-500-TX, NHD-500-RX, NHD-510-TX

        Notes:
            The RS-232 stream is a bidirectional channel.
            To generate RS-232 codes directly from an encoder or decoder using ASCII or Hex notation, see section 8.2 - Device Control –
            Custom Command Generation.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix serial set <TX1> <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix serial set <TX1> <RX1> <RX2> … <RXn>

        Command Example: Assign encoder RS-232 port to decoders
            matrix serial set source1 display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix serial set source1 display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix serial set {tx} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_serial_set_null(self, rx: str | list[str]) -> bool:
        """Unassign RX(s) RS-232 ports

        Args:
            rx: Single decoder reference (alias or hostname) or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX, NHD-510-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname

        Command structure:
            matrix serial set null <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            matrix serial set null <RX1> <RX2> … <RXn>

        Command Example: Unassign decoder RS-232 ports
            matrix serial set null display1 display2 display3 display4

        Response Example: Command acknowledgment
            matrix serial set null display1 display2 display3 display4
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"matrix serial set null {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_serial2_set(
        self, device: str, mode: Literal["single", "api", "all"], target_device: str | None = None
    ) -> bool:
        """Assign RX or TX RS-232 port to endpoint(s) or API notification

        Args:
            device: TX or RX device reference (alias or hostname)
            mode: Operational mode
                single: Assign to endpoint (requires target_device)
                api: Assign to API notification
                all: Assign to all other endpoints
            target_device: TX or RX device reference (required for 'single' mode)

        Returns:
            bool: True if command was successful

        Raises:
            ValueError: If target_device is required but not provided for 'single' mode

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The RS-232 stream is a bidirectional channel.
            To generate RS-232 codes directly from an encoder or decoder using ASCII or Hex notation, see section 8.2 - Device Control –
            Custom Command Generation.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            mode: Operational mode
                single: Assigned to endpoint
                api: Assigned to API notification
                all: Assigned to all other endpoints
                null: Assigned to no endpoints

        Command structure:
            matrix serial2 set <TX|RX> <mode> (<TX|RX>)

        Response structure (command mirror):
            matrix serial2 set <TX|RX> <mode> (<TX|RX>)

        Command Example 1: Assign encoder RS-232 port to decoder RS-232 port
            matrix serial2 set source1 single display1

        Response Example: Command acknowledgment
            matrix serial2 set source1 single display1

        Command Example 2: Assign encoder RS-232 port to encoder RS-232 port
            matrix serial2 set source1 single source2

        Response Example: Command acknowledgment
            matrix serial2 set source1 single source2

        Command Example 3: Assign decoder RS-232 port to API notification
            matrix serial2 set display1 api

        Response Example: Command acknowledgment
            matrix serial2 set display1 api

        Command Example 4: Assign encoder RS-232 port to all endpoint RS-232 ports
            matrix serial2 set source1 all

        Response Example: Command acknowledgment
            matrix serial2 set source1 all
        """
        if mode == "single" and target_device is None:
            raise ValueError("target_device is required when mode is 'single'")

        if mode == "single":
            command = f"matrix serial2 set {device} single {target_device}"
        else:
            command = f"matrix serial2 set {device} {mode}"

        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def matrix_serial2_set_null(self, device: str) -> bool:
        """Unassign TX or RX RS-232 port

        Args:
            device: Device reference (TX or RX alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname

        Command structure:
            matrix serial2 set <TX|RX> null

        Response structure (command mirror):
            matrix serial2 set <TX|RX> null

        Command Example: Unassign decoder RS-232 port
            matrix serial2 set display1 null

        Response Example: Command acknowledgment
            matrix serial2 set display1 null
        """
        command = f"matrix serial2 set {device} null"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)
