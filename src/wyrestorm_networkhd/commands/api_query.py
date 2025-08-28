from ..models.api_query import (
    CustomMultiviewLayoutList,
    DeviceInfo,
    DeviceJsonString,
    DeviceStatus,
    EndpointAliasHostname,
    IpSetting,
    Matrix,
    MatrixAudio,
    MatrixAudio2,
    MatrixAudio3,
    MatrixInfrared,
    MatrixInfrared2,
    MatrixSerial,
    MatrixSerial2,
    MatrixUsb,
    MatrixVideo,
    PresetMultiviewLayoutList,
    Version,
    VideoWallLogicalScreenList,
    VideoWallSceneList,
    VideowallWithinWallSceneList,
)


class APIQueryCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 13.1 Query Commands – System Configuration
    # Use this command to query NetworkHD system configuration parameters.
    # =============================================================

    async def config_get_version(self) -> Version:
        """Query NHD-CTL version

        Returns:
            Version: Parsed version information

        Command applies to:
            NHD-000-CTL, NHD-CTL-PRO
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            api: API version number
            web: Webserver version number
            core: System core version number
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            config get version

        Response structure:
            API version: v<api><CR><LF>System version: v<web>(v<core>)

        Command Example: Get NHD-CTL version
            config get version

        Response Example: Return data
            API version: v1.21
            System version: v8.3.1(v8.3.8)
        """
        command = "config get version"
        response = await self.client.send_command(command)
        return Version.parse(response)

    async def config_get_ipsetting(self) -> IpSetting:
        """Query NHD-CTL "AV" port network interface details

        Returns:
            IpSetting: Parsed IP setting information

        Command applies to:
            NHD-000-CTL, NHD-CTL-PRO

        Notes:
            Values can be assigned using the NetworkHD Console application.
            Default gateway values will be listed but might not be active for the interface. The NHD-CTL can only have one active gateway IP. The interface with the disabled gateway will list gw as 0.0.0.0
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            ipv4: IPv4 address value
            nm: Netmask value
            gw: IPv4 default gateway address value

        Command structure:
            config get ipsetting

        Response structure:
            ipsetting is: ip4addr <ipv4> netmask <nm> gateway <gw>

        Command Example: Get NHD-CTL "AV" port network interface details
            config get ipsetting

        Response Example: Return data
            ipsetting is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254
        """
        command = "config get ipsetting"
        response = await self.client.send_command(command)
        return IpSetting.parse(response)

    async def config_get_ipsetting2(self) -> IpSetting:
        """Query NHD-CTL "CONTROL" port network interface details

        Returns:
            IpSetting: Parsed IP setting information

        Command applies to:
            NHD-000-CTL, NHD-CTL-PRO

        Notes:
            Values can be assigned using the NetworkHD Console application.
            Default gateway values will be listed but might not be active for the interface. The NHD-CTL can only have one active gateway IP. The interface with the disabled gateway will list gw as 0.0.0.0
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            ipv4: IPv4 address value
            nm: Netmask value
            gw: IPv4 default gateway address value

        Command structure:
            config get ipsetting2

        Response structure:
            ipsetting2 is: ip4addr <ipv4> netmask <nm> gateway <gw>

        Command Example: Get NHD-CTL "CONTROL" port network interface details
            config get ipsetting2

        Response Example: Return data
            ipsetting2 is: ip4addr 192.168.11.243 netmask 255.255.255.0 gateway 192.168.11.1
        """
        command = "config get ipsetting2"
        response = await self.client.send_command(command)
        return IpSetting.parse(response)

    async def config_get_devicelist(self) -> list[str]:
        """Query online endpoint names

        Returns:
            list[str]: List of device names (aliases or hostnames)

        Raises:
            ValueError: If devicelist response format is invalid

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            This will not return offline device names.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname

        Command structure:
            config get devicelist

        Response structure:
            devicelist is <TX1|RX1> <TX2|RX2> … <TXn|RXn>

        Command Example: Get online endpoints
            config get devicelist

        Response Example: Return data
            devicelist is source1 source2 display1 display2 display3
        """
        command = "config get devicelist"
        response = await self.client.send_command(command)

        # Parse the response directly
        if "devicelist is" not in response:
            raise ValueError(f"Invalid devicelist response format: {response}")

        # Extract devices after "devicelist is"
        devices_part = response.split("devicelist is")[1].strip()
        devices = [device.strip() for device in devices_part.split() if device.strip()]

        return devices

    async def config_get_devicejsonstring(self) -> list[DeviceJsonString]:
        """Query general information for all TX or RX saved in the NHD-CTL

        Returns:
            list[DeviceJsonString]: Parsed device JSON string information objects

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Refer to Appendix A for further JSON format response data information.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            JSONdata: data in JSON format

        Command structure:
            config get devicejsonstring

        Response structure:
            device json string: <JSONdata>

        Command Example: Get online endpoints
            config get devicejsonstring

        Response Example: See Appendix A
        """
        command = "config get devicejsonstring"
        response = await self.client.send_command(command)
        return DeviceJsonString.parse(response)

    # =============================================================
    # 13.2 Query Commands – Device Configuration
    # Use this command to query NetworkHD endpoint configurations. Where available at the NetworkHD endpoints, endpoints can be
    # queried to return current status information.
    # =============================================================

    async def config_get_name(self, device: str | None = None) -> EndpointAliasHostname | list[EndpointAliasHostname]:
        """Query endpoint Alias and Hostname

        Args:
            device: Optional device reference (alias or hostname)

        Returns:
            EndpointAliasHostname | list[EndpointAliasHostname]: Parsed alias/hostname information

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Alias may be null if the endpoint has not had the default Alias changed using the NetworkHD Console utility.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            alias: endpoint Alias
            hostname: endpoint Hostname

        Command structure:
            config get name (<alias|hostname>)

        Response structure:
            <hostname>'s alias is <alias|null>

        Command Example 1: Get all endpoint Alias and Hostname
            config get name

        Response Example:
            NHD-400-TX-E4CE02104E55's alias is source1
            NHD-400-TX-E4CE02104E56's alias is source2
            NHD-400-RX-E4CE02104A57's alias is display1
            NHD-400-RX-E4CE02104A58's alias is null

        Command Example 2: Get endpoint Alias and Hostname
            config get name NHD-400-RX-E4CE02104A57

        Response Example:
            NHD-400-RX's alias is display1
        """
        command = f"config get name {device}" if device else "config get name"
        response = await self.client.send_command(command)

        if device:
            # Single device query
            return EndpointAliasHostname.parse_single(response)
        else:
            # Multiple devices query
            return EndpointAliasHostname.parse_multiple(response)

    async def config_get_device_info(self, device: str | None = None) -> list[DeviceInfo]:
        """Query TX or RX device working parameters

        Args:
            device: Optional device reference (TX or RX alias/hostname)

        Returns:
            list[DeviceInfo]: Parsed device information objects

        Raises:
            DeviceQueryError: If device is not found or returns an error

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Refer to Appendix A for further JSON format response data information.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            JSONdata: data in JSON format

        Command structure:
            config get device info (<TX|RX>)

        Response structure:
            devices json info: <JSONdata>

        Command Example 1: Get all TX and RX device working parameters
            config get device info

        Response Example: See Appendix A

        Command Example 2: Get TX device working parameters
            config get device info source1

        Response Example: See Appendix A
        """
        command = f"config get device info {device}" if device else "config get device info"
        response = await self.client.send_command(command, response_timeout=5)
        return DeviceInfo.parse(response)

    async def config_get_device_status(self, device: str | None = None) -> list[DeviceStatus]:
        """Query TX or RX device real-time status

        Args:
            device: Optional device reference (TX or RX alias/hostname)

        Returns:
            list[DeviceStatus]: Parsed device status information objects

        Raises:
            DeviceQueryError: If device is not found or returns an error

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Refer to Appendix A for further JSON format response data information.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            JSONdata: data in JSON format

        Command structure:
            config get device status (<TX|RX>)

        Response structure:
            devices status info: <JSONdata>

        Command Example 1: Get all TX and RX device real-time status
            config get device status

        Response Example: See Appendix A

        Command Example 2: Get TX device real-time status
            config get device status source1

        Response Example: See Appendix A
        """
        command = f"config get device status {device}" if device else "config get device status"
        response = await self.client.send_command(command)
        return DeviceStatus.parse(response)

    # =============================================================
    # 13.3 Query Commands – Stream Matrix Switching
    # Use this command to query stream matrix assignments. Where available at the NetworkHD endpoints, endpoints can be queried to
    # return the current stream matrix assignments between endpoints.
    # =============================================================

    async def matrix_get(self, rx_devices: list[str] | None = None) -> Matrix:
        """Query RX assignments where using all primary media streams

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            Matrix: Parsed matrix information

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set command found in section 6.1 – Stream Matrix Switching – All Media
            3) The RX has been assigned discrete media streams. E.g. using the matrix video set, matrix audio set commands found in section 6 – Media Stream Matrix Switch Commands
            The response does not return assignments for RXs using Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get RX assignments where using all primary media streams
            matrix get

        Response Example: Return data
            matrix information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix get {device_list}"
        else:
            command = "matrix get"
        response = await self.client.send_command(command)
        return Matrix.parse(response)

    async def matrix_video_get(self, rx_devices: list[str] | None = None) -> MatrixVideo:
        """Query RX stream assignments for video output

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixVideo: Parsed matrix video information

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix video set command found in section 6 – Media Stream Matrix Switch Commands
            The response does not return assignments for RXs using Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix video get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix video information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for primary video streams
            matrix video get

        Response Example: Return data
            matrix video information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4

        Command Example: Get RX assignments for primary video streams
            matrix video get display1 display3

        Response Example: Return data
            matrix video information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix video get {device_list}"
        else:
            command = "matrix video get"
        response = await self.client.send_command(command)
        return MatrixVideo.parse(response)

    async def matrix_audio_get(self, rx_devices: list[str] | None = None) -> MatrixAudio:
        """Query RX stream assignments for HDMI audio output

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixAudio: Parsed matrix audio information

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix audio set command found in section 6 – Media Stream Matrix Switch Commands
            The response does not return assignments for RXs using Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix audio get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix audio information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for HDMI audio streams
            matrix audio get

        Response Example: Return data
            matrix audio information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4

        Command Example: Get RX assignments for HDMI audio streams
            matrix audio get display1 display3

        Response Example: Return data
            matrix audio information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix audio get {device_list}"
        else:
            command = "matrix audio get"
        response = await self.client.send_command(command)
        return MatrixAudio.parse(response)

    async def matrix_audio2_get(self, rx_devices: list[str] | None = None) -> MatrixAudio2:
        """Query RX stream assignments for analog audio output

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixAudio2: Parsed matrix audio2 information

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix audio2 set command found in section 6 – Media Stream Matrix Switch Commands
            Note that while an assignment may be made to a TX, the audio path may not be set in the RX. See the config set device audio2source command found in section 7.2 – Port Switching - Audio
            The response does not return assignments for RXs using Multiview.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix audio2 get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix audio2 information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for analog audio streams
            matrix audio2 get

        Response Example: Return data
            matrix audio2 information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4

        Command Example: Get RX assignments for analog audio streams
            matrix audio2 get display1 display3

        Response Example: Return data
            matrix audio2 information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix audio2 get {device_list}"
        else:
            command = "matrix audio2 get"
        response = await self.client.send_command(command)
        return MatrixAudio2.parse(response)

    async def matrix_audio3_get(self, rx_device: str | None = None, tx_device: str | None = None) -> MatrixAudio3:
        """Query RX stream assignments for ARC

        Args:
            rx_device: Optional RX device reference (alias or hostname)
            tx_device: Optional TX device reference (alias or hostname)

        Returns:
            MatrixAudio3: Parsed matrix audio3 information

        Command applies to:
            NHD-500-TX, NHD-500-RX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix audio3 get (<RX1>) (<TX1>)

        Response structure:
            matrix audio3 information:<CR><LF><RX1><CR><LF><TX1>

        Command Example: Get all RX assignments for ARC streams
            matrix audio3 get

        Response Example: Return data
            matrix audio3 information:
            Display1 Source1
            Display2 Source3
            Display5 Source2

        Command Example: Get specific RX assignment for ARC streams
            matrix audio3 Display1

        Response Example: Return data
            matrix audio3 information:
            Display1 Source3
        """
        if rx_device and tx_device:
            command = f"matrix audio3 get {rx_device} {tx_device}"
        elif rx_device:
            command = f"matrix audio3 get {rx_device}"
        else:
            command = "matrix audio3 get"
        response = await self.client.send_command(command)
        return MatrixAudio3.parse(response)

    async def matrix_usb_get(self, rx_devices: list[str] | None = None) -> MatrixUsb:
        """Query RX stream assignments for USB

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixUsb: Parsed matrix USB information

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix usb set command found in section 6 – Media Stream Matrix Switch Commands
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix usb get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix usb information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for USB
            matrix usb get

        Response Example: Return data
            matrix usb information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4

        Command Example: Get RX assignments for USB
            matrix usb get display1 display3

        Response Example: Return data
            matrix usb information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix usb get {device_list}"
        else:
            command = "matrix usb get"
        response = await self.client.send_command(command)
        return MatrixUsb.parse(response)

    async def matrix_infrared_get(self, rx_devices: list[str] | None = None) -> MatrixInfrared:
        """Query RX stream assignments for infrared

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixInfrared: Parsed matrix infrared information

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix infrared set command found in section 6 – Media Stream Matrix Switch Commands
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix infrared get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix infrared information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for infrared
            matrix infrared get

        Response Example: Return data
            matrix infrared information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            NULL Display4

        Command Example: Get RX assignments for infrared
            matrix infrared get display1 display3

        Response Example: Return data
            matrix infrared information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix infrared get {device_list}"
        else:
            command = "matrix infrared get"
        response = await self.client.send_command(command)
        return MatrixInfrared.parse(response)

    async def matrix_infrared2_get(self, devices: list[str] | None = None) -> MatrixInfrared2:
        """Query TX or RX stream assignments for infrared receiver port

        Args:
            devices: Optional list of device references (TX or RX alias or hostname)

        Returns:
            MatrixInfrared2: Parsed matrix infrared2 information

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The endpoint IR receiver assignment will show NULL if:
            1) The endpoint is in a default state and has not yet been assigned a TX
            2) The endpoint IR receiver has been assigned NULL using the matrix set, matrix infrared2 set command found in section 6 – Media Stream Matrix Switch Commands
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)
            mode: Operational mode
                single: Assigned to endpoint
                api: Assigned to API notification
                all: Assigned to all other endpoints
                null: Assigned to no endpoints

        Command structure:
            matrix infrared2 get (<TX1|RX1>) (<TX2|RX2>) … (<TXn|RXn>)

        Response structure:
            matrix infrared2 information:<CR><LF><TX1|RX1> <mode> (<TXn|RXn>)<CR><LF><TX2|RX2> <mode> (<TXn|RXn>) … <CR><LF><TXn|RXn> <mode> (<TXn|RXn>)>

        Command Example: Get all endpoint IR receiver assignments
            matrix infrared2 get

        Response Example: Return data
            matrix infrared2 information:
            source1 single display1
            display1 api
            source2 api
            display2 null

        Command Example: Get endpoint IR assignments
            matrix infrared2 get display1 source1

        Response Example: Return data
            matrix infrared2 information:
            display1 api
            source1 single display1
        """
        if devices:
            device_list = " ".join(devices)
            command = f"matrix infrared2 get {device_list}"
        else:
            command = "matrix infrared2 get"
        response = await self.client.send_command(command)
        return MatrixInfrared2.parse(response)

    async def matrix_serial_get(self, rx_devices: list[str] | None = None) -> MatrixSerial:
        """Query RX stream assignments for RS-232

        Args:
            rx_devices: Optional list of RX device references (alias or hostname)

        Returns:
            MatrixSerial: Parsed matrix serial information

        Command applies to:
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            The RX assignment will show NULL if:
            1) The RX is in a default state and has not yet been assigned a TX
            2) The RX has been assigned NULL using the matrix set, matrix serial set command found in section 6 – Media Stream Matrix Switch Commands
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            matrix serial get (<RX1>) (<RX2>) … (<RXn>)

        Response structure:
            matrix serial information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>

        Command Example: Get all RX assignments for RS-232
            matrix serial get

        Response Example: Return data
            matrix serial information:
            Source1 Display1
            Source1 Display2
            Source2 Display3
            null Display4

        Command Example: Get RX assignments for RS-232
            matrix serial get display1 display3

        Response Example: Return data
            matrix serial information:
            Source1 Display1
            Source2 Display3
        """
        if rx_devices:
            device_list = " ".join(rx_devices)
            command = f"matrix serial get {device_list}"
        else:
            command = "matrix serial get"
        response = await self.client.send_command(command)
        return MatrixSerial.parse(response)

    async def matrix_serial2_get(self, devices: list[str] | None = None) -> MatrixSerial2:
        """Query TX or RX stream assignments for RS-232 port

        Args:
            devices: Optional list of device references (TX or RX alias or hostname)

        Returns:
            MatrixSerial2: Parsed matrix serial2 information

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            The endpoint RS-232 port assignment will show NULL if:
            1) The endpoint is in a default state and has not yet been assigned a TX
            2) The endpoint IR receiver has been assigned NULL using the matrix set, matrix serial2 set command found in section 6 – Media Stream Matrix Switch Commands
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)
            mode: Operational mode
                single: Assigned to endpoint
                api: Assigned to API notification
                all: Assigned to all other endpoints
                null: Assigned to no endpoints

        Command structure:
            matrix serial2 get (<TX1|RX1>) (<TX2|RX2>) … (<TXn|RXn>)

        Response structure:
            matrix serial2 information:<CR><LF><TX1|RX1> <mode> (<TXn|RXn>)<CR><LF><TX2|RX2> <mode> (<TXn|RXn>) … <CR><LF><TXn|RXn> <mode> (<TXn|RXn>)>

        Command Example: Get all endpoint RS-232 receiver assignments
            matrix serial2 get

        Response Example: Return data
            matrix serial2 information:
            source1 single display1
            display1 api
            source2 api
            display2 null

        Command Example: Get endpoint RS-232assignments
            matrix serial2 get display1 source1

        Response Example: Return data
            matrix serial2 information:
            display1 api
            source1 single display1
        """
        if devices:
            device_list = " ".join(devices)
            command = f"matrix serial2 get {device_list}"
        else:
            command = "matrix serial2 get"
        response = await self.client.send_command(command)
        return MatrixSerial2.parse(response)

    # =============================================================
    # 13.4 Query Commands – Video Walls
    # Use this command to query elements of Video wall configurations. Where available at the NetworkHD endpoints, endpoints can be
    # queried to return the current configurations related to video walls.
    # =============================================================

    async def scene_get(self) -> VideoWallSceneList:
        """Query 'standard video wall' Scene list

        Returns:
            VideoWallSceneList: Parsed video wall scene list

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Video wall names are given to physical video wall arrays when created in the NetworkHD Console software utility.
            Scene names are given to Scenes when created in the NetworkHD Console software utility.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            scene get

        Response structure:
            scene list:<CR><LF><videowall1>-<scene1> <videowall1>-<scene2> … <videowalln>-<scenen>

        Command Example: Get list of all Scenes
            scene get

        Response Example: Return data
            scene list:
            OfficeVW-Splitmode OfficeVW-Combined
        """
        command = "scene get"
        response = await self.client.send_command(command)
        return VideoWallSceneList.parse(response)

    async def vw_get(self) -> VideoWallLogicalScreenList:
        """Query 'standard video wall' logical screen list

        Returns:
            VideoWallLogicalScreenList: Parsed video wall logical screen list

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Video wall names are given to physical video wall arrays when created in the NetworkHD Console software utility.
            Scene names are given to Scenes when created in the NetworkHD Console software utility.
            Logical screen names are given to logical screens when created in the NetworkHD Console software utility.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            Lscreen: Preconfigured logical screen name
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            vw get

        Response structure:
            Video wall information:<CR><LF><videowall1>-<scene1>_<Lscreen1> <TX><CR><LF>Row 1: <RX1> <RX2>… <CR><LF><videowalln>-<scenen>_<Lscreenn> <TX><CR><LF>Row 1: <RXn> <RXn>Row 2: <RXn> <RXn> …>

        Command Example: Get list of all logical screens
            vw get

        Response Example: Return data
            Video wall information:
            OfficeVW-Combined_TopTwo source1
            Row 1: display1 display2
            OfficeVW-AllCombined_AllDisplays source2
            Row 1: display1 display2 display3
            Row 2: display4 display5 display6
            Row 3: display7 display8 display9
        """
        command = "vw get"
        response = await self.client.send_command(command)
        return VideoWallLogicalScreenList.parse(response)

    async def wscene2_get(self) -> VideowallWithinWallSceneList:
        """Query 'videowall within a wall' Scene list

        Returns:
            VideowallWithinWallSceneList: Parsed videowall within wall scene list

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Video wall names are given to physical video wall arrays when created in the NetworkHD Console software utility.
            Scene names are given to Scenes when created in the NetworkHD Console software utility.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            wscene2 get

        Response structure:
            wscene2 list:<CR><LF><videowall1>-<wscene1> <videowall1>-<wscene2> … <videowalln>-<wscenen>

        Command Example: Get list of all Scenes
            wscene2 get

        Response Example: Return data
            wscene2 list:
            OfficeVW-windowscene1 OfficeVW-windowscene2
        """
        command = "wscene2 get"
        response = await self.client.send_command(command)
        return VideowallWithinWallSceneList.parse(response)

    # =============================================================
    # 13.5 Query Commands – Multiview
    # Use this command to query elements of Multiview configurations. Where available at the NetworkHD endpoints, endpoints can be
    # queried to return the current configurations related to Multiview.
    # =============================================================

    async def mscene_get(self, rx: str | None = None) -> PresetMultiviewLayoutList:
        """Query preset Multiview layout list

        Args:
            rx: Optional decoder reference (alias or hostname)

        Returns:
            PresetMultiviewLayoutList: Parsed preset multiview layout list

        Command applies to:
            NHD-220-RX, NHD-250-RX
            NHD-0401-MV
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Multiview layout names are given to preset layouts when they are created. These are listed and selected in NetworkHD Console.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            lname: Preconfigured layout name
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            mscene get (<RX>)

        Response structure:
            mscene list:<CR><LF><RX> <lname1> <lname2> … <lnamen><CR>LF>… <CR><LF><RXn> <lname3> <lname4> …>

        Command Example: Get list of all layouts
            mscene get

        Response Example: Return data
            mscene list:
            display5 gridlayout piplayout
            display6 pip2layout
            display7 grid5layout grid6layout

        Command Example: Get list of layouts for RX
            mscene get display6

        Response Example: Return data
            mscene list:
            display6 pip2layout
        """
        command = f"mscene get {rx}" if rx else "mscene get"
        response = await self.client.send_command(command)
        return PresetMultiviewLayoutList.parse(response)

    async def mview_get(self, rx: str | None = None) -> CustomMultiviewLayoutList:
        """Query custom Multiview layout list

        Args:
            rx: Optional decoder reference (alias or hostname)

        Returns:
            CustomMultiviewLayoutList: Parsed custom multiview layout list

        Command applies to:
            NHD-220-RX, NHD-250-RX

        Notes:
            tile: Use for non-overlapping tile layouts
            overlay: Use for overlapping tile layouts
            fit: Scales source to fit window without distortion
            stretch: Scales source to fit window completely
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            Xn: Tile's top left pixel – horizontal reference
            Yn: Tile's top left pixel – vertical reference
            Wn: Tile horizontal size in pixels
            Hn: Tile vertical size in pixels
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            mview get (<RX>)

        Response structure:
            mview information:<CR><LF><RX1> [tile|overlay] <TX1>:<X1>_Y1>_<W1>_<H1>:[fit|stretch] <TX2>:<X2>_Y2>_<W2>_<H2>:[fit|stretch] … <TXn>:<Xn>_Yn>_<Wn>_<Hn>:[fit|stretch]>

        Command Example: Get list of all layouts
            mview get

        Response Example: Return data
            mview information:
            display10 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit
            display11 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit

        Command Example: Get list of layouts for RX
            mview get display11

        Response Example: Return data
            mview information:
            display11 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit
        """
        command = f"mview get {rx}" if rx else "mview get"
        response = await self.client.send_command(command)
        return CustomMultiviewLayoutList.parse(response)
