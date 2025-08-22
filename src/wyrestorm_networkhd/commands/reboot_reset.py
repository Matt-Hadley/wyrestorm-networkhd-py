from ._response_helpers import require_contains


class RebootResetCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 5.1 Device Reboot
    # To reboot a single or multiple NetworkHD devices (retains current settings):
    # =============================================================
    async def set_reboot(self) -> bool:
        """Reboot the NHD-CTL

        Returns:
            bool: True if command was successful

        Command structure:
            config set reboot

        Response structure:
            system will reboot now

        Command Example: Reboot the NHD-CTL
            config set reboot

        Response Example: Command acknowledgment
            system will reboot now

        Command applies to:
            NHD-000-CTL, NHD-CTL-PRO
        """
        response = await self.client.send_command("config set reboot")
        return require_contains(response, "system will reboot now")

    async def set_device_reboot(self, devices: str | list[str]) -> bool:
        """Reboot TX or RX devices

        Args:
            devices: Single device reference or list of device references
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-TX/RX, NHD-120-IW-TX, NHD-124-TX, NHD-150-RX, NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-500-TX/RX, NHD-500-E-TX/RX, NHD-500-IW-TX, NHD-510-TX, NHD-500-DNT-TX, NHD-400-TX/RX, NHD-400-E-TX/RX, NHD-400-DNT-TX, NHD-400-TX-IW, NHD-0401-MV
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            config set device reboot <TX1|RX1> <TX2|RX2>

        Response structure:
            the following device will reboot now:<CR><LF>
            <TX1|RX1><CR><LF><TX2|RX2>

        Command Example: Reboot encoders
            config set device reboot source1 source2

        Response Example: Command acknowledgment
            the following device will reboot now:
            source1
            source2
        """
        if isinstance(devices, str):
            devices = [devices]
        device_list = " ".join(devices)
        response = await self.client.send_command(f"config set device reboot {device_list}", response_timeout=10.0)
        return require_contains(response, "the following device will reboot now:")

    # =============================================================
    # 5.2 Device Reset
    # To reset a single or multiple NetworkHD devices (defaults all settings):
    # =============================================================

    async def config_set_device_restorefactory(self, devices: str | list[str]) -> bool:
        """Reset TX or RX devices

        Args:
            devices: Single device reference or list of device references
                TX: Encoder reference (alias or hostname)
                RX: Decoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-120-TX/RX, NHD-120-IW-TX, NHD-124-TX, NHD-150-RX, NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-500-TX/RX, NHD-500-E-TX/RX, NHD-500-IW-TX, NHD-510-TX, NHD-500-DNT-TX, NHD-400-TX/RX, NHD-400-E-TX/RX, NHD-400-DNT-TX, NHD-400-TX-IW, NHD-0401-MV
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TXn: Encoder reference – Alias or hostname
            RXn: Decoder reference – Alias or hostname
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)

        Command structure:
            config set device restorefactory <TX1|RX1> <TX2|RX2>

        Response structure:
            the following device will restore now:<CR><LF>
            <TX1|RX1><CR><LF><TX2|RX2> … <CR><LF><TXn|RXn>

        Command Example: Reboot encoders
            config set device restorefactory source1 source2

        Response Example: Command acknowledgment
            the following device will restore now:
            source1
            source2
        """
        if isinstance(devices, str):
            devices = [devices]
        device_list = " ".join(devices)
        response = await self.client.send_command(
            f"config set device restorefactory {device_list}", response_timeout=10.0
        )
        return require_contains(response, "the following device will restore now:")
