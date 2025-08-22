"""NetworkHD API query response data models."""

from dataclasses import dataclass
from typing import Literal

# =============================================================================
# Helper Functions for Common Parsing Patterns
# =============================================================================


def _skip_to_header(response: str, header: str) -> list[str]:
    """Skip everything before specified header and return data lines

    Args:
        response: The raw response string
        header: The header to look for (e.g., "information:", "list:", "scene list:", "mscene list:")

    Returns:
        list[str]: Lines of data after the header, with empty lines filtered out

    Notes:
        Used by parsers that have a header line before the actual data lines.
    """
    lines = response.strip().split("\n")
    data_lines = []
    data_started = False

    for line in lines:
        line = line.strip()

        # Skip everything until we find the specified header
        if line.endswith(header):
            data_started = True
            continue

        # Only collect non-empty lines after the header
        if data_started and line:
            data_lines.append(line)

    return data_lines


def _parse_device_mode_assignment(line: str) -> tuple[str, str, str | None]:
    """Parse device mode assignment lines

    Args:
        line: The line to parse (e.g., 'source1 single display1' or 'display1 api' or 'display2 null')

    Returns:
        tuple[str, str, str | None]: (device, mode, target_device)
            device: The device reference
            mode: The operational mode
            target_device: Target device (None unless mode is 'single')

    Notes:
        Used by MatrixInfrared2 and MatrixSerial2 parsers for lines like:
        'source1 single display1' or 'display1 api' or 'display2 null'
    """
    parts = line.split()
    if len(parts) < 2:
        raise ValueError(f"Invalid assignment line format: {line}")

    device = parts[0]
    mode = parts[1]
    target_device = parts[2] if len(parts) > 2 and mode == "single" else None

    return device, mode, target_device


def _parse_scene_items(response: str, list_header: str) -> list[tuple[str, str]]:
    """Parse videowall scene items from response

    Args:
        response: The raw response string
        list_header: The header to look for (e.g., "scene list:", "wscene2 list:")

    Returns:
        list[tuple[str, str]]: List of (videowall, scene) tuples

    Notes:
        Used by VideoWallSceneList and VideowallWithinWallSceneList parsers
        for parsing items like 'OfficeVW-Splitmode OfficeVW-Combined'
    """
    data_lines = _skip_to_header(response, list_header)
    scenes = []

    for line in data_lines:
        scene_items = line.split()
        for item in scene_items:
            if "-" in item:
                videowall, scene = item.split("-", 1)
                scenes.append((videowall, scene))

    return scenes


# =============================================================================
# 13.1 Query Commands – System Configuration
# =============================================================================


@dataclass
class Version:
    """Version information from 'config get version'"""

    api_version: str
    web_version: str
    core_version: str

    @classmethod
    def parse(cls, response: str) -> "Version":
        """Parse 'config get version' response

        Args:
            response: The raw response string from the device

        Returns:
            Version: Parsed version information object

        Raises:
            ValueError: If required version information cannot be found

        Notes:
            Searches through the response for version patterns, ignoring command echoes and other noise.
            Response format: API version: v<api><CR><LF>System version: v<web>(v<core>)
            Response example: API version: v1.21\nSystem version: v8.3.1(v8.3.8)
        """
        lines = response.strip().split("\n")

        api_version = cls._extract_api_version(lines)
        web_version, core_version = cls._extract_web_and_core_versions(lines)

        # Validate that we found all required information
        if api_version is None:
            raise ValueError(f"Could not find API version in response: {response}")
        if web_version is None:
            raise ValueError(f"Could not find System version in response: {response}")

        return cls(api_version=api_version, web_version=web_version, core_version=core_version)

    @classmethod
    def _extract_api_version(cls, lines: list[str]) -> str | None:
        """Extract API version from response lines

        Args:
            lines: List of response lines to search through

        Returns:
            str | None: API version string if found, None otherwise

        Notes:
            Looks for lines starting with "API version: v" and extracts the version number.
        """
        for line in lines:
            line = line.strip()
            if line.startswith("API version: v"):
                return line[14:]  # Remove "API version: v"
        return None

    @classmethod
    def _extract_web_and_core_versions(cls, lines: list[str]) -> tuple[str | None, str | None]:
        """Extract web and core version numbers from response lines

        Args:
            lines: List of response lines to search through

        Returns:
            tuple[str | None, str | None]: (web_version, core_version) - both None if not found

        Notes:
            Supports two formats:
            - If the line contains a core version in parentheses, e.g. "System version: v8.3.1(v8.3.8)",
              it returns a tuple of (web_version, core_version), e.g. ("8.3.1", "8.3.8").
            - If the line does not contain a core version in parentheses, e.g. "System version: v8.3.1",
              it returns a tuple with the same value for both web and core versions, e.g. ("8.3.1", "8.3.1").
        """
        for line in lines:
            line = line.strip()
            if line.startswith("System version: v"):
                version_part = line[17:]  # Remove "System version: v"
                # Parse system version format like '8.3.1(v8.3.8)' or '8.3.1'
                if "(" in version_part and ")" in version_part:
                    web_version = version_part.split("(")[0]
                    core_part = version_part.split("(v")[1].rstrip(")")
                    return web_version, core_part
                else:
                    # Fallback if no core version in parentheses
                    return version_part, version_part
        return None, None


@dataclass
class IpSetting:
    """IP settings from 'config get ipsetting' or 'config get ipsetting2'"""

    ip4addr: str
    netmask: str
    gateway: str

    @classmethod
    def parse(cls, response: str) -> "IpSetting":
        """Parse 'config get ipsetting' or 'config get ipsetting2' response

        Args:
            response: The raw response string from the device

        Returns:
            IpSetting: Parsed IP setting information object

        Raises:
            ValueError: If response format is invalid or missing required settings

        Notes:
            Response format: ipsetting is: ip4addr <ipv4> netmask <nm> gateway <gw>
            Response example: ipsetting is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254
            Response example: ipsetting2 is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254
        """
        # Handle both ipsetting and ipsetting2 responses
        if "ipsetting is:" in response:
            settings_part = response.split("ipsetting is:")[1].strip()
        elif "ipsetting2 is:" in response:
            settings_part = response.split("ipsetting2 is:")[1].strip()
        else:
            raise ValueError(f"Invalid IP settings response ResponseFormat: {response}")

        parts = settings_part.split()
        settings = {}
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                key = parts[i]
                value = parts[i + 1]
                settings[key] = value

        if not all(key in settings for key in ["ip4addr", "netmask", "gateway"]):
            raise ValueError(f"Missing required IP settings in response: {response}")

        return cls(ip4addr=settings["ip4addr"], netmask=settings["netmask"], gateway=settings["gateway"])


# =============================================================================
# 13.2 Query Commands – Device Configuration
# =============================================================================


@dataclass
class EndpointAliasHostname:
    """Endpoint name from 'config get name'"""

    alias: str | None
    hostname: str

    @classmethod
    def parse_single(cls, response: str) -> "EndpointAliasHostname":
        """Parse 'config get name' (single entry) response

        Args:
            response: The raw response string from the device

        Returns:
            EndpointAliasHostname: Parsed alias/hostname information object

        Raises:
            DeviceNotFoundError: If the specified device does not exist
            ValueError: If response format is invalid

        Notes:
            Response format: <hostname>'s alias is <alias|null>
            Response example: NHD-400-TX-E4CE02104E55's alias is source1
            Error format: "<device_name> does not exist."
        """
        from ..exceptions import DeviceNotFoundError

        # Check for "does not exist" error
        if " does not exist." in response:
            # Extract device name from error message (preserve original device name including empty string)
            device_name = response.replace(" does not exist.", "").strip()
            # Remove surrounding quotes if present
            if device_name.startswith('"') and device_name.endswith('"'):
                device_name = device_name[1:-1]
            raise DeviceNotFoundError(device_name)

        parts = response.split("'s alias is ")
        if len(parts) != 2:
            raise ValueError(f"Invalid name response ResponseFormat: {response}")

        hostname = parts[0].strip()
        alias_part = parts[1].strip()
        alias = None if alias_part.lower() == "null" else alias_part

        return cls(alias=alias, hostname=hostname)

    @classmethod
    def parse_multiple(cls, response: str) -> list["EndpointAliasHostname"]:
        """Parse 'config get name' (multiple entries) response

        Args:
            response: The raw response string from the device

        Returns:
            list[EndpointAliasHostname]: List of parsed alias/hostname information objects

        Notes:
            Response format: <hostname1>'s alias is <alias1|null><CR><LF><hostname2>'s alias is <alias2|null><CR><LF>...
            Response example: NHD-400-TX-E4CE02104E55's alias is source1\nNHD-400-TX-E4CE02104E56's alias is source2\nNHD-400-RX-E4CE02104A57's alias is display1\nNHD-400-RX-E4CE02104A58's alias is null
        """
        names = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and "'s alias is " in line:
                names.append(cls.parse_single(line))
        return names


# =============================================================================
# 13.3 Query Commands – Stream Matrix Switching
# =============================================================================


@dataclass
class MatrixAssignment:
    """Matrix assignment entry"""

    tx: str | None  # None for NULL assignments
    rx: str


@dataclass
class BaseMatrix:
    """Base class for matrix assignments with common parsing logic"""

    assignments: list[MatrixAssignment]

    @classmethod
    def parse(cls, response: str) -> "BaseMatrix":
        """Parse 'matrix get' response (and similar variants) with standard format

        Args:
            response: The raw response string from the device

        Returns:
            BaseMatrix: Parsed matrix assignment information object

        Raises:
            ValueError: If matrix assignment line format is invalid

        Notes:
            Ignores everything before the matrix information header and parses only the actual matrix data.
            Response format: matrix [type] information:<CR><LF><TXn|NULL> <RX1><CR><LF><TXn|NULL> <RX2> … <CR><LF><TXn|NULL> <RXn>
            Response example: matrix information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4
            Response example: matrix video information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 2:
                raise ValueError(f"Invalid matrix assignment line format, expected 'TX RX': {line}")

            tx = None if parts[0].upper() == "NULL" else parts[0]
            rx = parts[1]
            assignments.append(MatrixAssignment(tx=tx, rx=rx))

        return cls(assignments=assignments)


@dataclass
class Matrix(BaseMatrix):
    """Matrix assignments from 'matrix get'"""

    pass


@dataclass
class MatrixVideo(BaseMatrix):
    """Matrix video assignments from 'matrix video get'"""

    pass


@dataclass
class MatrixAudio(BaseMatrix):
    """Matrix audio assignments from 'matrix audio get'"""

    pass


@dataclass
class MatrixAudio2(BaseMatrix):
    """Matrix audio2 assignments from 'matrix audio2 get'"""

    pass


@dataclass
class ARCAssignment:
    """ARC assignment entry"""

    rx: str
    tx: str


@dataclass
class MatrixAudio3:
    """Matrix audio3 assignments from 'matrix audio3 get'"""

    assignments: list[ARCAssignment]

    @classmethod
    def parse(cls, response: str) -> "MatrixAudio3":
        """Parse 'matrix audio3 get' response

        Args:
            response: The raw response string from the device

        Returns:
            MatrixAudio3: Parsed ARC assignment information object

        Raises:
            ValueError: If response format is invalid or missing TX for RX

        Notes:
            Ignores everything before the 'matrix audio3 information:' line and parses only the actual assignment data.
            Response format: matrix audio3 information:<CR><LF><RX1><CR><LF><TX1>
            Response example: matrix audio3 information:\nDisplay1 Source1\nDisplay2 Source3\nDisplay5 Source2
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        # Process pairs (RX followed by TX)
        for i in range(0, len(data_lines), 2):
            if i + 1 < len(data_lines):
                rx = data_lines[i].strip()
                tx = data_lines[i + 1].strip()

                assignments.append(ARCAssignment(rx=rx, tx=tx))
            else:
                # Odd number of lines - missing TX for last RX
                rx = data_lines[i].strip()
                raise ValueError(f"Invalid matrix audio3 response format, missing TX for RX: {rx}")

        return cls(assignments=assignments)


@dataclass
class MatrixUsb(BaseMatrix):
    """Matrix USB assignments from 'matrix usb get'"""

    pass


@dataclass
class MatrixInfrared(BaseMatrix):
    """Matrix infrared assignments from 'matrix infrared get'"""

    pass


@dataclass
class InfraredReceiverAssignment:
    """Infrared receiver assignment entry"""

    device: str  # TX or RX device
    mode: Literal["single", "api", "all", "null"]
    target_device: str | None  # Only present for "single" mode


@dataclass
class MatrixInfrared2:
    """Matrix infrared2 assignments from 'matrix infrared2 get'"""

    assignments: list[InfraredReceiverAssignment]

    @classmethod
    def parse(cls, response: str) -> "MatrixInfrared2":
        """Parse 'matrix infrared2 get' response

        Args:
            response: The raw response string from the device

        Returns:
            MatrixInfrared2: Parsed infrared receiver assignment information object

        Notes:
            Ignores everything before the 'matrix infrared2 information:' line and parses only the actual assignment data.
            Response format: matrix infrared2 information:<CR><LF><TX1|RX1> <mode> (<TXn|RXn>)<CR><LF><TX2|RX2> <mode> (<TXn|RXn>) …
            Response example: matrix infrared2 information:\nsource1 single display1\ndisplay1 api\nsource2 api\ndisplay2 null
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            device, mode, target_device = _parse_device_mode_assignment(line)
            assignments.append(InfraredReceiverAssignment(device=device, mode=mode, target_device=target_device))

        return cls(assignments=assignments)


@dataclass
class MatrixSerial(BaseMatrix):
    """Matrix serial assignments from 'matrix serial get'"""

    pass


@dataclass
class SerialPortAssignment:
    """Serial port assignment entry"""

    device: str  # TX or RX device
    mode: Literal["single", "api", "all", "null"]
    target_device: str | None  # Only present for "single" mode


@dataclass
class MatrixSerial2:
    """Matrix serial2 assignments from 'matrix serial2 get'"""

    assignments: list[SerialPortAssignment]

    @classmethod
    def parse(cls, response: str) -> "MatrixSerial2":
        """Parse 'matrix serial2 get' response

        Args:
            response: The raw response string from the device

        Returns:
            MatrixSerial2: Parsed serial port assignment information object

        Notes:
            Ignores everything before the 'matrix serial2 information:' line and parses only the actual assignment data.
            Response format: matrix serial2 information:<CR><LF><TX1|RX1> <mode> (<TXn|RXn>)<CR><LF><TX2|RX2> <mode> (<TXn|RXn>) …
            Response example: matrix serial2 information:\nsource1 single display1\ndisplay1 api\nsource2 api\ndisplay2 null
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            device, mode, target_device = _parse_device_mode_assignment(line)
            assignments.append(SerialPortAssignment(device=device, mode=mode, target_device=target_device))

        return cls(assignments=assignments)


# =============================================================================
# 13.4 Query Commands – Video Walls
# =============================================================================


@dataclass
class VideoWallScene:
    """Video wall scene entry"""

    videowall: str
    scene: str


@dataclass
class VideoWallSceneList:
    """Scene list from 'scene get'"""

    scenes: list[VideoWallScene]

    @classmethod
    def parse(cls, response: str) -> "VideoWallSceneList":
        """Parse 'scene get' response

        Args:
            response: The raw response string from the device

        Returns:
            VideoWallSceneList: Parsed video wall scene list information object

        Raises:
            ValueError: If no valid scenes are found in response

        Notes:
            Response format: scene list:<CR><LF><videowall1>-<scene1> <videowall1>-<scene2> … <videowalln>-<scenen>
            Response example: scene list:\nOfficeVW-Splitmode OfficeVW-Combined
        """
        scene_tuples = _parse_scene_items(response, "scene list:")

        if not scene_tuples:
            raise ValueError(f"No valid scenes found in response: {response}")

        scenes = [VideoWallScene(videowall=vw, scene=sc) for vw, sc in scene_tuples]
        return cls(scenes=scenes)


@dataclass
class VideoWallLogicalScreen:
    """Logical screen entry"""

    videowall: str
    scene: str
    logical_screen: str
    tx: str
    rows: list[list[str]]  # List of rows, each containing RX devices


@dataclass
class VideoWallLogicalScreenList:
    """Video wall logical screens from 'vw get'"""

    logical_screens: list[VideoWallLogicalScreen]

    @classmethod
    def parse(cls, response: str) -> "VideoWallLogicalScreenList":
        """Parse 'vw get' response

        Args:
            response: The raw response string from the device

        Returns:
            VideoWallLogicalScreenList: Parsed video wall logical screen information object

        Notes:
            Response format: Video wall information:<CR><LF><videowall1>-<scene1>_<Lscreen1> <TX><CR><LF>Row 1: <RX1> <RX2><Row 2: <RX3> <RX4> …
            Response example: Video wall information:\nOfficeVW-Combined_TopTwo source1\nRow 1: display1 display2\nOfficeVW-AllCombined_AllDisplays source2\nRow 1: display1 display2 display3\nRow 2: display4 display5 display6
        """
        data_lines = _skip_to_header(response, "Video wall information:")
        screens = []
        current_screen = None
        current_rows = []

        for line in data_lines:
            line = line.strip()
            if line.startswith("Row "):
                # Parse row data: "Row 1: display1 display2"
                row_devices = line.split(": ")[1].split() if ": " in line else []
                current_rows.append(row_devices)
            else:
                # Save previous screen if exists
                cls._finalize_screen(current_screen, current_rows, screens)

                # Parse new screen header
                current_screen = cls._parse_screen_header(line)
                current_rows = []

        # Finalize the last screen
        cls._finalize_screen(current_screen, current_rows, screens)
        return cls(logical_screens=screens)

    @classmethod
    def _finalize_screen(cls, screen: VideoWallLogicalScreen | None, rows: list[list[str]], screens: list) -> None:
        """Add completed screen to screens list"""
        if screen:
            screen.rows = rows
            screens.append(screen)

    @classmethod
    def _parse_screen_header(cls, line: str) -> VideoWallLogicalScreen | None:
        """Parse screen header line like 'OfficeVW-Combined_TopTwo source1'"""
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(f"Invalid screen header format, expected 'videowall-scene_logicalscreen TX': {line}")

        if "_" not in parts[0]:
            raise ValueError(f"Invalid screen header format, missing logical screen separator '_': {line}")

        if "-" not in parts[0]:
            raise ValueError(f"Invalid screen header format, missing videowall-scene separator '-': {line}")

        videowall_scene, logical_screen = parts[0].split("_", 1)
        videowall, scene = videowall_scene.split("-", 1)
        tx = parts[1]

        return VideoWallLogicalScreen(videowall=videowall, scene=scene, logical_screen=logical_screen, tx=tx, rows=[])


@dataclass
class VideowallWithinWallSceneList:
    """Videowall within wall scene list from 'wscene2 get'"""

    scenes: list[VideoWallScene]

    @classmethod
    def parse(cls, response: str) -> "VideowallWithinWallSceneList":
        """Parse 'wscene2 get' response

        Args:
            response: The raw response string from the device

        Returns:
            VideowallWithinWallSceneList: Parsed videowall within wall scene list information object

        Notes:
            Response format: wscene2 list:<CR><LF><videowall1>-<wscene1> <videowall1>-<wscene2> … <videowalln>-<wscenen>
            Response example: wscene2 list:\nOfficeVW-windowscene1 OfficeVW-windowscene2
        """
        scene_tuples = _parse_scene_items(response, "wscene2 list:")
        scenes = [VideoWallScene(videowall=vw, scene=sc) for vw, sc in scene_tuples]
        return cls(scenes=scenes)


# =============================================================================
# 13.5 Query Commands – Multiview
# =============================================================================


@dataclass
class MultiviewLayout:
    """Multiview layout entry"""

    rx: str
    layouts: list[str]


@dataclass
class PresetMultiviewLayoutList:
    """Preset multiview layout list from 'mscene get'"""

    multiview_layouts: list[MultiviewLayout]

    @classmethod
    def parse(cls, response: str) -> "PresetMultiviewLayoutList":
        """Parse 'mscene get' response

        Args:
            response: The raw response string from the device

        Returns:
            PresetMultiviewLayoutList: Parsed preset multiview layout list information object

        Raises:
            ValueError: If preset multiview layout line format is invalid

        Notes:
            Ignores everything before the 'mscene list:' line and parses only the actual layout data.
            Response format: mscene list:<CR><LF><RX> <lname1> <lname2> … <lnamen><CR>LF><RXn> <lname3> <lname4> …
            Response example: mscene list:\ndisplay5 gridlayout piplayout\ndisplay6 pip2layout\ndisplay7 grid5layout grid6layout
        """
        data_lines = _skip_to_header(response, "mscene list:")
        layouts = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 2:
                raise ValueError(
                    f"Invalid preset multiview layout line format, expected 'RX layout1 layout2...': {line}"
                )

            rx = parts[0]
            layout_names = parts[1:]

            layouts.append(MultiviewLayout(rx=rx, layouts=layout_names))

        return cls(multiview_layouts=layouts)


@dataclass
class MultiviewTile:
    """Multiview tile configuration"""

    tx: str
    x: int
    y: int
    width: int
    height: int
    scaling: Literal["fit", "stretch"]

    @classmethod
    def parse_tile_config(cls, tile_config: str) -> "MultiviewTile":
        """Parse tile configuration string

        Args:
            tile_config: The tile configuration string to parse

        Returns:
            MultiviewTile: Parsed tile configuration object

        Raises:
            ValueError: If tile configuration format is invalid

        Notes:
            Response format: <tx>:<x>_<y>_<width>_<height>:<scaling>
            Response example: source1:0_0_960_540:fit
        """
        parts = tile_config.split(":")
        if len(parts) != 3:
            raise ValueError(f"Invalid tile configuration: {tile_config}")

        tx = parts[0]
        coords = parts[1].split("_")
        scaling = parts[2]

        if len(coords) != 4:
            raise ValueError(f"Invalid tile coordinates: {parts[1]}")

        return cls(
            tx=tx, x=int(coords[0]), y=int(coords[1]), width=int(coords[2]), height=int(coords[3]), scaling=scaling
        )


@dataclass
class CustomMultiviewLayout:
    """Custom multiview configuration entry"""

    rx: str
    mode: Literal["tile", "overlay"]
    tiles: list[MultiviewTile]


@dataclass
class CustomMultiviewLayoutList:
    """Custom multiview layout list from 'mview get'"""

    configurations: list[CustomMultiviewLayout]

    @classmethod
    def parse(cls, response: str) -> "CustomMultiviewLayoutList":
        """Parse 'mview get' response

        Args:
            response: The raw response string from the device

        Returns:
            CustomMultiviewLayoutList: Parsed custom multiview layout list information object

        Raises:
            ValueError: If multiview layout line format is invalid or tile configuration is invalid

        Notes:
            Response format: mview information:<CR><LF><RX1> [tile|overlay] <TX1>:<X1>_Y1>_<W1>_<H1>:[fit|stretch] <TX2>:<X2>_Y2>_<W2>_<H2>:[fit|stretch] …
            Response example: mview information:\ndisplay10 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit\ndisplay11 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit
        """
        data_lines = _skip_to_header(response, "information:")
        configurations = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 3:
                raise ValueError(f"Invalid multiview layout line format, expected 'RX mode tile1 tile2...': {line}")

            rx = parts[0]
            mode = parts[1]

            if mode not in ["tile", "overlay"]:
                raise ValueError(f"Invalid multiview mode '{mode}', expected 'tile' or 'overlay': {line}")

            tile_configs = parts[2:]

            tiles = []
            for tile_config in tile_configs:
                try:
                    tiles.append(MultiviewTile.parse_tile_config(tile_config))
                except ValueError as e:
                    raise ValueError(f"Invalid tile configuration in line '{line}': {e}") from e

            configurations.append(CustomMultiviewLayout(rx=rx, mode=mode, tiles=tiles))

        return cls(configurations=configurations)
