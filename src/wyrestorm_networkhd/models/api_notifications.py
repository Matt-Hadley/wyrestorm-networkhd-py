"""NetworkHD API notification data models."""

from dataclasses import dataclass
from typing import Any, Literal, cast

# =============================================================
# 12.2 Endpoint Notifications
# Use this command for notifications that originate from an endpoint. Where available, endpoints will use API notifications to signal
# a change in status or availability of data.
# =============================================================


@dataclass
class NotificationEndpoint:
    """Endpoint online status notification"""

    online: bool
    device: str

    @classmethod
    def parse(cls, notification: str) -> "NotificationEndpoint":
        """Parse endpoint online status notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationEndpoint: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-140-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX
        """
        """NetworkHDReferenceAPI
        Notification definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname

        Notification structure:
            notify endpoint [+|-] <TX|RX>

        Notification example: RX has gone offline
            notify endpoint – display1

        Notification example 2: TX has come online
            notify endpoint + source1
        """
        parts = notification.strip().split()
        if len(parts) != 4 or parts[0] != "notify" or parts[1] != "endpoint":
            raise ValueError(f"Invalid endpoint status notification format: {notification}")

        status_indicator = parts[2]
        device = parts[3]

        if status_indicator == "+":
            return cls(online=True, device=device)
        elif status_indicator == "-" or status_indicator == "–":  # Handle both minus and em dash
            return cls(online=False, device=device)
        else:
            raise ValueError(f"Invalid endpoint status indicator in notification: {notification}")


@dataclass
class NotificationCecinfo:
    """Endpoint CEC data notification"""

    device: str
    cec_data: str

    @classmethod
    def parse(cls, notification: str) -> "NotificationCecinfo":
        """Parse endpoint CEC data notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationCecinfo: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX
        """
        """NetworkHDReferenceAPI
        Notification definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            cecdata: CEC data string

        Notification structure:
            notify cecinfo <TX|RX> "<cecdata>"

        Notification example: RX has received CEC data
            notify cecinfo display1 "FF36"
        """
        # Handle quoted CEC data
        if "notify cecinfo " not in notification or '"' not in notification:
            raise ValueError(f"Invalid CEC data notification format: {notification}")

        prefix = "notify cecinfo "
        remaining = notification[len(prefix) :]

        # Find the device name (everything before the first quote)
        quote_pos = remaining.find('"')
        device = remaining[:quote_pos].strip()

        # Extract CEC data from quotes
        end_quote_pos = remaining.rfind('"')
        if end_quote_pos <= quote_pos:
            raise ValueError(f"Invalid CEC data notification format (unclosed quotes): {notification}")

        cec_data = remaining[quote_pos + 1 : end_quote_pos]

        return cls(device=device, cec_data=cec_data)


@dataclass
class NotificationIrinfo:
    """Endpoint Infrared data notification"""

    device: str
    ir_data: str

    @classmethod
    def parse(cls, notification: str) -> "NotificationIrinfo":
        """Parse endpoint infrared data notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationIrinfo: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            Infrared data will be received if the correct setting is applied to endpoints using the matrix infrared2 set command found in
            section 6.5 - Stream Matrix Switching – Infrared Stream Breakaway.
        """
        """NetworkHDReferenceAPI
        Notification definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            irdata: Infrared data string

        Notification structure:
            notify irinfo <TX|RX> "<irdata>"

        Notification example: RX has received infrared data
            notify irinfo display1 "0000 0067 0000 0015 0060 0018 0030 0018
            0018 0018 0030 0018 0018 0018 0030 0018 0018 0018 0018 0018 0018
            0018 0030 0018 0018 0018 0030 0018 0030 0018 0018 0018 0030 0018
            0018 0018 0018 0018 0018 0018 0030 0018 0030 0018 0030 01FE"
        """
        # Handle quoted IR data
        if "notify irinfo " not in notification or '"' not in notification:
            raise ValueError(f"Invalid infrared data notification format: {notification}")

        prefix = "notify irinfo "
        remaining = notification[len(prefix) :]

        # Find the device name (everything before the first quote)
        quote_pos = remaining.find('"')
        device = remaining[:quote_pos].strip()

        # Extract IR data from quotes
        end_quote_pos = remaining.rfind('"')
        if end_quote_pos <= quote_pos:
            raise ValueError(f"Invalid infrared data notification format (unclosed quotes): {notification}")

        ir_data = remaining[quote_pos + 1 : end_quote_pos]

        return cls(device=device, ir_data=ir_data)


@dataclass
class NotificationSerialinfo:
    """Endpoint RS-232 data notification"""

    device: str
    data_format: Literal["hex", "ascii"]
    data_length: int
    serial_data: str

    @classmethod
    def parse(cls, notification: str) -> "NotificationSerialinfo":
        """Parse endpoint RS-232 data notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationSerialinfo: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-110-TX/RX, NHD-100-TX, NHD-100-RX, NHD-200-TX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-TX (IW only), NHD-400-RX, NHD-500-TX, NHD-500-RX
            NHD-600-TX, NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX, NHD-610-TX

        Notes:
            RS-232 data will generate a notification automatically on NetworkHD 100, 200 and 400 Series endpoints.
            On NetworkHD 600 Series endpoints, data will be received if the correct setting is applied to endpoints using the matrix
            serial2 set command found in section 6.6 - Stream Matrix Switching – RS-232 Stream Breakaway.
        """
        """NetworkHDReferenceAPI
        Notification definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            infolen: length of formatted data string (sdata) in characters
                for ASCII: infolen = number of received bytes
                for Hex: (infolen + 1)/3 = number of received bytes
            CR: Carriage Return byte (0x0D) (CR) (\r)
            LF: Line Feed byte (0x0A) (LF) (\n)
            sdata: RS-232 formatted data string

        Notification structure:
            notify serialinfo <TX|RX> [hex|ascii] <infolen>:<CR><LF><sdata>

        Notification example 1: RX has received RS-232 data in Hex format
            notify serialinfo display1 hex 371:
            4c 6f 72 65 6d 20 69 70 73 75 6d 20 64 6f 6c 6f 72 20 73 69 74
            20 61 6d 65 74 2c 20 63 6f 6e 73 65 63 74 65 74 75 72 20 61 64
            69 70 69 73 63 69 6e 67 20 65 6c 69 74 2c 20 73 65 64 20 64 6f
            20 65 69 75 73 6d 6f 64 20 74 65 6d 70 6f 72 20 69 6e 63 69 64
            69 64 75 6e 74 20 75 74 20 6c 61 62 6f 72 65 20 65 74 20 64 6f
            6c 6f 72 65 20 6d 61 67 6e 61 20 61 6c 69 71 75 61 0D 0A

        Notification example 2: RX has received RS-232 data in ASCII format
            notify serialinfo display1 ascii 122:
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua
        """
        if not notification.startswith("notify serialinfo "):
            raise ValueError(f"Invalid serial data notification format: {notification}")

        # Remove prefix
        remaining = notification[len("notify serialinfo ") :]

        # Split on colon to separate header from data
        if ":" not in remaining:
            raise ValueError(f"Invalid serial data notification format (no colon): {notification}")

        header, data_part = remaining.split(":", 1)
        header_parts = header.strip().split()

        if len(header_parts) != 3:
            raise ValueError(f"Invalid serial data notification header: {header}")

        device = header_parts[0]
        data_format = header_parts[1]
        data_length = int(header_parts[2])

        if data_format not in ["hex", "ascii"]:
            raise ValueError(f"Invalid serial data format: {data_format}")

        # Remove leading CR/LF from data
        serial_data = data_part.lstrip("\r\n")

        # Cast data_format to the correct Literal type after validation
        validated_format = cast(Literal["hex", "ascii"], data_format)
        return cls(device=device, data_format=validated_format, data_length=data_length, serial_data=serial_data)


@dataclass
class NotificationVideo:
    """Video input status notification"""

    status: Literal["lost", "found"]
    device: str
    source_device: str | None = None  # Only present for RX found notifications

    @classmethod
    def parse(cls, notification: str) -> "NotificationVideo":
        """Parse endpoint video status notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationVideo: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-400-TX, NHD-400-RX, NHD-500-TX, NHD-500-RX

        Notes:
            Video input at a TX means the video signal entering the video input port. This is not the same thing as hotplug detection, e.g. the
            source has entered a standby mode and is not outputting video but is still physically connected.
            Video input at an RX means the AV over IP video stream from an encoder. It is not concerned with video output connections.
            The field in parenthesis is only used when an RX reports a (re)established connection to a TX and informs of the connected TX as
            the last variable.
        """
        """NetworkHDReferenceAPI
        Notification definitions:
            TX: Encoder reference – Alias or hostname
            RX: Decoder reference – Alias or hostname
            lost: video input has been lost from endpoint
            found: video input has been (re)established with endpoint

        Notification structure:
            notify video [lost|found] <TX|RX> (<TX>)

        Notification example: RX has (re)established connection with TX
            notify video found display1 source1

        Notification example: TX has lost source input video
            notify video lost source1
        """
        parts = notification.strip().split()
        if len(parts) < 3 or parts[0] != "notify" or parts[1] != "video":
            raise ValueError(f"Invalid video status notification format: {notification}")

        status = parts[2]
        device = parts[3]

        if status not in ["lost", "found"]:
            raise ValueError(f"Invalid video status: {status}")

        # Check for source device (RX found notifications)
        source_device = None
        if len(parts) > 4:
            source_device = parts[4]

        # Cast status to the correct Literal type after validation
        validated_status = cast(Literal["lost", "found"], status)
        return cls(status=validated_status, device=device, source_device=source_device)


@dataclass
class NotificationSink:
    """Sink power status notification"""

    status: Literal["lost", "found"]
    device: str

    @classmethod
    def parse(cls, notification: str) -> "NotificationSink":
        """Parse sink power status notification

        Args:
            notification: The notification string to parse

        Returns:
            NotificationSink: Parsed notification object

        Raises:
            ValueError: If notification format is invalid

        Command applies to:
            NHD-110-RX, NHD-100-RX, NHD-200-RX, NHD-210-RX, NHD-220-RX, NHD-250-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Sink power status notifications indicate when a device's power state changes
            due to CEC, RS-232, or other power control commands.
        """
        """NetworkHDReferenceAPI
        Notification structure:
            notify sink [lost|found] <RX>

        Notification example: RX has lost power
            notify sink lost display1

        Notification example 2: RX has regained power
            notify sink found display1
        """
        parts = notification.strip().split()
        if len(parts) != 4 or parts[0] != "notify" or parts[1] != "sink":
            raise ValueError(f"Invalid sink power status notification format: {notification}")

        status = parts[2]
        device = parts[3]

        if status not in ["lost", "found"]:
            raise ValueError(f"Invalid sink power status: {status}")

        # Cast status to the correct Literal type after validation
        validated_status = cast(Literal["lost", "found"], status)
        return cls(status=validated_status, device=device)


class NotificationParser:
    """Utility class to parse any NetworkHD API notification"""

    # Static mapping of notification prefixes to type info
    _NOTIFICATION_MAPPINGS: dict[str, dict[str, Any]] = {
        "notify endpoint": {
            "type": "endpoint",
            "class": NotificationEndpoint,
        },
        "notify cecinfo": {
            "type": "cecinfo",
            "class": NotificationCecinfo,
        },
        "notify irinfo": {
            "type": "irinfo",
            "class": NotificationIrinfo,
        },
        "notify serialinfo": {
            "type": "serialinfo",
            "class": NotificationSerialinfo,
        },
        "notify video": {
            "type": "video",
            "class": NotificationVideo,
        },
        "notify sink": {
            "type": "sink",
            "class": NotificationSink,
        },
    }

    @staticmethod
    def get_notification_type(notification: str) -> str:
        """Extract the notification type from a notification string.

        Args:
            notification: The notification string to analyze

        Returns:
            The notification type string used for callback registration

        Raises:
            ValueError: If notification type is unknown
        """
        notification = notification.strip()

        for prefix, info in NotificationParser._NOTIFICATION_MAPPINGS.items():
            if notification.startswith(prefix):
                return str(info["type"])

        raise ValueError(f"Unknown notification type: {notification}")

    @staticmethod
    def parse_notification(
        notification: str,
    ) -> (
        NotificationEndpoint
        | NotificationCecinfo
        | NotificationIrinfo
        | NotificationSerialinfo
        | NotificationVideo
        | NotificationSink
    ):
        """Parse any NetworkHD API notification and return the appropriate notification object

        Args:
            notification: The notification string to parse

        Returns:
            Union of notification objects: Parsed notification object

        Raises:
            ValueError: If notification type is unknown or format is invalid
        """
        notification = notification.strip()

        for prefix, info in NotificationParser._NOTIFICATION_MAPPINGS.items():
            if notification.startswith(prefix):
                notification_class = info["class"]
                # Type checker can't know the specific class type from the dict
                return notification_class.parse(notification)  # type: ignore[no-any-return]

        raise ValueError(f"Unknown notification type: {notification}")


# Type alias for all notification objects (defined after all classes)
# Extract classes dynamically from the NotificationParser mappings
def _get_notification_types():
    """Get all notification types dynamically from the parser mappings."""
    return tuple(info["class"] for info in NotificationParser._NOTIFICATION_MAPPINGS.values())


NotificationObject = _get_notification_types()
