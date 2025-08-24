from typing import Literal

from ._response_helpers import require_command_mirror


class ConnectedDeviceControlCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 8.1 Device Control – Proxy Commands
    # Use this command to generate preset control commands for connected devices. Where available at the NetworkHD endpoints, this
    # will include sending CEC and/or RS-232 data to a connected device.
    #
    # Proxy commands are defined using NetworkHD Console, part of the WyreStorm Management Suite. Each decoder can have
    # different command data that is sent to a connected device when the proxy command is received.
    # =============================================================

    async def config_set_device_sinkpower(self, power: Literal["on", "off"], rx: str | list[str]) -> bool:
        """Send "power" proxy command for device attached to RX

        Args:
            power: Power state
                on: Power on proxy command
                off: Power off proxy command
            rx: Single decoder reference or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-100-RX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Power on and power off commands are defined as either CEC, RS-232 or both within NetworkHD Console. By default, power commands are disabled on each endpoint. Power commands can be specified uniquely for each endpoint.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname
            on: Power on proxy command
            off: Power off proxy command

        Command structure:
            config set device sinkpower [on|off] <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            config set device sinkpower [on|off] <RX1> <RX2> … <RXn>

        Command Example: Instruct decoder to send its unique power on command
            config set device sinkpower on display1

        Response Example: Command acknowledgment
            config set device sinkpower on display1
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"config set device sinkpower {power} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def config_set_device_cec(
        self, command_type: Literal["onetouchplay", "standby"], rx: str | list[str]
    ) -> bool:
        """Send CEC proxy command for device attached to RX

        Args:
            command_type: CEC command
                onetouchplay: CEC power on proxy command
                standby: CEC power off proxy command
            rx: Single decoder reference or list of decoder references (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-100-RX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            CEC power on and power off commands are defined within the NetworkHD Console. By default, CEC power commands will use the default CEC data commands. For details on the default CEC commands, see the NetworkHD Technical Reference Guide.
            Custom CEC power on and power off commands can be set within the NetworkHD Console to replace the default CEC commands.
            Unlike config set device sinkpower, the config set device cec command cannot be disabled in the NetworkHD Console and will always generate data from the decoder.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RXn: Decoder reference – Alias or hostname
            onetouchplay: CEC power on proxy command
            standby: CEC power off proxy command

        Command structure:
            config set device cec [onetouchplay|standby] <RX1> <RX2> … <RXn>

        Response structure (command mirror):
            config set device cec [onetouchplay|standby] <RX1> <RX2> … <RXn>

        Command Example: Instruct decoder to send its unique CEC standby command
            config set device cec standby display1

        Response Example: Command acknowledgment
            config set device cec standby display1
        """
        if isinstance(rx, str):
            rx = [rx]
        rx_list = " ".join(rx)
        command = f"config set device cec {command_type} {rx_list}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    # =============================================================
    # 8.2 Device Control – Custom Command Generation
    # Use this command to generate custom control commands for connected devices. Where available at the NetworkHD endpoints,
    # this will include sending custom command data to a connected device directly from the endpoint.
    # =============================================================

    async def cec(self, cecdata: str, rx: str) -> bool:
        """Send custom CEC command to device attached to RX

        Args:
            cecdata: CEC data bytes in hex format
            rx: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-100-RX, NHD-200-RX, NHD-210-RX, NHD-250-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            CEC data bytes are in hexadecimal notation with no space separation between bytes.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            RX: Decoder reference – Alias or hostname
            cecdata: CEC data bytes in hex format

        Command structure:
            cec "<cecdata>" <RX>

        Response structure (command mirror):
            cec "<cecdata>" <RX>

        Command Example: Instruct decoder to send custom CEC command
            cec "FF36" display1

        Response Example: Command acknowledgment
            cec "FF36" display1
        """
        command = f'cec "{cecdata}" {rx}'
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def infrared(self, irdata: str, device: str) -> bool:
        """Send custom infrared command to device attached to RX or TX

        Args:
            irdata: Infrared command data
            device: Device reference
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX, NHD-110-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            NHD-400 & 600 series require infrared data in Pronto CCF Hex format.
            NHD-110 series FW v6.0.xx requires infrared data in Global Cache format. FW v7.0.xx requires Pronto Hex format.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            irdata: Infrared command data

        Command structure:
            infrared "<irdata>" <TX|RX>

        Response structure (command mirror):
            infrared "<irdata>" <TX|RX>

        Command Example: Instruct encoder to send custom IR command
            ```
            infrared "0000 0067 0000 0015 0060 0018 0030 0018 0018 0018 0030 0018..." source1
            ```

        Response Example: Command acknowledgment
            ```
            infrared "0000 0067 0000 0015 0060 0018 0030 0018 0018 0018 0030 0018..." source1
            ```
        """
        command = f'infrared "{irdata}" {device}'
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)

    async def serial(
        self,
        baud: int,
        bits: Literal[6, 7, 8],
        parity: Literal["o", "e", "n"],
        stop: Literal[1, 2],
        cr: bool,
        lf: bool,
        hex_format: bool,
        data: str,
        device: str,
    ) -> bool:
        """Send custom RS-232 command to device attached to RX or TX

        Args:
            baud: Baud rate
                2400, 4800, 9600, 19200, 38400, 57600, 115200
            bits: Number of data bits
                6, 7, 8
            parity: Parity bit
                o: odd
                e: even
                n: none
            stop: Number of stop bits
                1, 2
            cr: Append carriage return delimiter (\r)(CR)
                True: on
                False: off
            lf: Append line feed delimiter (\n)(LF)
                True: on
                False: off
            hex_format: Data format
                True: Hexadecimal format
                False: ASCII format
            data: RS-232 command data
            device: Device reference
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Where specified, delimiters are appended to the end of the transmitted data.
            Delimiters cannot be included in command data (data) when using ASCII format e.g. \r or\n are not escaped and sent literally as ASCII.
            All hex data byte values are supported when using hexadecimal command data format (00 through FF) and are space-separated.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            baud: Baud rate: 2400, 4800, 9600, 19200, 38400, 57600, 115200
            bits: Number of data bits: 6, 7, 8
            parity: Parity bit odd / even / none: o, e, n
            stop: Number of stop bits: 1, 2
            CR: Append carriage return delimiter (\r)(CR): on, off
            LF: Append line feed delimiter (\n)(LF): on, off
            HEX: Data format: on = Hexadecimal format, off = ASCII format
            data: RS-232 command data

        Command structure:
            serial -b <baud>-<bits><parity><stop> -r <CR> -n <LF> -h <HEX> "<data>" <TX|RX>

        Response structure (command mirror):
            serial -b <baud>-<bits><parity><stop> -r <CR> -n <LF> -h <HEX> "<data>" <TX|RX>

        Command Example 1: Instruct encoder to send custom RS-232 ASCII command
            serial -b 115200-8n1 -r on -n on -h off "vol +80dB" source1

        Response Example: Command acknowledgment
            serial -b 115200-8n1 -r on -n on -h off "vol +80dB" source1

        Command Example 2: Instruct decoder to send custom RS-232 Hex command
            ```
            serial -b 19200-7e2 -r off -n off -h on "4c 6f 72 65 6d 20 69 70 73 75..." display1
            ```

        Response Example: Command acknowledgment
            ```
            serial -b 19200-7e2 -r off -n off -h on "4c 6f 72 65 6d 20 69 70 73 75..." display1
            ```
        """
        cr_flag = "on" if cr else "off"
        lf_flag = "on" if lf else "off"
        hex_flag = "on" if hex_format else "off"

        command = f'serial -b {baud}-{bits}{parity}{stop} -r {cr_flag} -n {lf_flag} -h {hex_flag} "{data}" {device}'
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)
