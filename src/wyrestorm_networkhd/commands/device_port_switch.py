from typing import Literal

from ._response_helpers import require_command_mirror


class DevicePortSwitchCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 7.1 Port Switching – Video
    # Use this command to define which video source input port an encoder will use. Where available at the NetworkHD endpoints, this
    # will include the switching between discrete video source input ports to select which connected video source will be used with
    # encoder AV over IP processing.
    # =============================================================

    async def config_set_device_videosource(self, tx: str, source: Literal["auto", "hdmi", "dp"]) -> bool:
        """Switch TX video input port

        Args:
            tx: Encoder reference (alias or hostname)
            source: Video input port
                auto: Automatic selection (default)
                hdmi: HDMI port
                dp: DisplayPort port

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            source: Video input port:
                auto: Automatic selection (default)
                hdmi: HDMI port
                dp: DisplayPort port

        Command structure:
            config set device videosource <TX> <source>

        Response structure (command mirror):
            config set device videosource <TX> <source>

        Command Example: Select the HDMI port at the encoder
            config set device videosource source1 hdmi

        Response Example: Command acknowledgment
            config set device videosource source1 hdmi
        """
        command = f"config set device videosource {tx} {source}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_info_video_source_switch(
        self, source: Literal["hdmi", "usb-c", "none"], tx: str
    ) -> bool:
        """Switch TX video input port

        Args:
            source: Video input port
                hdmi: HDMI port
                usb-c: USB-C port
                none: Audio only(NHD-500-IW-TX)
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-510-TX, NHD-500-IW-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            source: Video input port:
                hdmi: HDMI port
                usb-c: USB-C port
                none: Audio only(NHD-500-IW-TX)

        Command structure:
            config set device info video_source_switch=<source> <TX>

        Response structure (command mirror):
            config set device info video_source_switch=<source> <TX>

        Command Example: Select the HDMI port at the encoder
            config set device info video_source_switch=HDMI Source1

        Response Example: Command acknowledgment
            config set device info video_source_switch=HDMI Source1
        """
        command = f"config set device info video_source_switch={source} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 7.2 Port Switching – Audio
    # Use this command to define which audio source a decoder port will use when assigned to a specific encoder. Where multiple audio
    # sources are available to a NetworkHD decoder, this will include the switching between discrete audio sources to select which audio
    # source will be used with a decoder port.
    # =============================================================

    async def config_set_device_audiosource(self, rx: str, source: Literal["hdmi", "dmix", "analog"]) -> bool:
        """Switch RX HDMI audio output port to a discrete audio stream from an assigned TX

        Args:
            rx: Decoder reference (alias or hostname)
            source: Assigned encoder's audio stream
                hdmi: HDMI audio stream (default)
                dmix: 2ch downmix HDMI audio stream
                analog: Analog port stream

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Where an encoder offers multiple audio streams, a decoder will switch to the audio stream on that encoder defined by this command. This remains the stream selection when assigning a different encoder using the Media Stream Matrix Switch commands found in section 6 – Media Stream Matrix Switch Commands.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            source: Assigned encoder's audio stream:
                hdmi: HDMI audio stream (default)
                dmix: 2ch downmix HDMI audio stream
                analog: Analog port stream

        Command structure:
            config set device audiosource <RX> <source>

        Response structure (command mirror):
            config set device audiosource <RX> <source>

        Command Example: Select the assigned encoder's HDMI audio stream
            config set device audiosource display1 hdmi

        Response Example: Command acknowledgment
            config set device audiosource display1 hdmi
        """
        command = f"config set device audiosource {rx} {source}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_audio2source(self, rx: str, stream: Literal["analog", "dmix"]) -> bool:
        """Switch RX analog audio output port to a discrete audio source

        Args:
            rx: Decoder reference (alias or hostname)
            stream: Audio source
                analog: Assigned encoder's analog audio stream (default)
                dmix: 2ch downmix of the RX HDMI audio output

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Where analog is selected, the decoder analog audio output port joins with the assigned encoder analog audio input port. This remains the stream selection and will assign to a different encoder when using the matrix set commands found in section 6.1 – Stream Matrix Switching – All Media or the matrix audio2 set commands found in section 6.2 – Stream Matrix Switching – Audio Stream Breakaway. The decoder analog output port will NOT assign to a different encoder when using the discrete HDMI audio matrix audio set command, found in section 6.2 – Stream Matrix Switching – Audio Stream Breakaway.
            Where dmix is selected, the decoder analog audio output port always follows the decoder HDMI audio output.
            The decoder analog audio output port offers 2 channel downmixing of up to 8 channel PCM audio.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            source: Audio source:
                analog: Assigned encoder's analog audio stream (default)
                dmix: 2ch downmix of the RX HDMI audio output

        Command structure:
            config set device audio2source <RX> <stream>

        Response structure (command mirror):
            config set device audio2source <RX> <stream>

        Command Example: Select a downmix of the decoder's HDMI audio output
            config set device audio2source display1 dmix

        Response Example: Command acknowledgment
            config set device audio2source display1 dmix
        """
        command = f"config set device audio2source {rx} {stream}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_audio_input_type(self, source: Literal["auto", "hdmi", "analog"], tx: str) -> bool:
        """Switch audio input port on NHD-500-DNT-TX for main audio stream

        Args:
            source: Video input port
                auto: Automatic selection (default)
                hdmi: HDMI port
                analog: 3.5mm port
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-500-DNT-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            source: Video input port:
                auto: Automatic selection (default)
                hdmi: HDMI port
                analog: 3.5mm port

        Command structure:
            config set device audio input type <source> <TX>

        Response structure (command mirror):
            config set device audio input type <source> <TX>

        Command Example: Select the HDMI port at the encoder
            config set device audio input type hdmi source1

        Response Example: Command acknowledgment
            config set device audio input type hdmi source1
        """
        command = f"config set device audio input type {source} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_info_dante_audio_input(self, source: Literal["hdmi", "analog"], tx: str) -> bool:
        """Switch audio input port on NHD-500-DNT-TX for Dante stream

        Args:
            source: Video input port
                hdmi: HDMI port (default)
                analog: 3.5mm port
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-500-DNT-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            source: Video input port:
                hdmi: HDMI port (default)
                analog: 3.5mm port

        Command structure:
            config set device info dante.audio_input=<source> <TX>

        Response structure (command mirror):
            config set device info dante.audio_input=<source> <TX>

        Command Example: Select the HDMI port at the encoder
            config set device info dante.audio_input=hdmi source1

        Response Example: Command acknowledgment
            config set device info dante.audio_input=hdmi source1
        """
        command = f"config set device info dante.audio_input={source} {tx}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 7.3 Port Switching – USB Mode
    # Use this command to define the working mode for a USB port. Where available to a NetworkHD endpoint, this will configure the
    # working mode of the USB ports on an endpoint.
    # =============================================================

    async def config_set_device_info_km_over_ip_enable(self, enable: Literal["on", "off"], device: str) -> bool:
        """Configure USB working mode for endpoint

        Args:
            enable: USB mode
                on: Automatic KMoIP mode enabled (default)
                off: KMoIP mode disabled – Use USBoIP mode
            device: Device reference
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-400-TX, NHD-400-RX

        Notes:
            When automatic KMoIP mode is enabled on an RX, this mode will be used when the RX detects a connected device that uses a USB HID Class (Base Class 03).
            When automatic KMoIP mode is enabled on a TX, this will prompt a connected device to enumerate a composite HID device.
            For more detail on the USB operating modes, please refer to the NetworkHD Technical Reference Guide.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            on: Automatic KMoIP mode enabled (default)
            off: KMoIP mode disabled – Use USBoIP mode

        Command structure:
            config set device info km_over_ip_enable=<on|off> <TX|RX>

        Response structure (command mirror):
            config set device info km_over_ip_enable=<on|off> <TX|RX>

        Command Example: Disable automatic KMoIP mode on endpoint
            config set device info km_over_ip_enable=off display1

        Response Example: Command acknowledgment
            config set device info km_over_ip_enable=off display1
        """
        command = f"config set device info km_over_ip_enable={enable} {device}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)
