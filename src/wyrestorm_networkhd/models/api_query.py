"""NetworkHD API query response data models."""

import json
import logging
import types
from collections.abc import Callable
from dataclasses import dataclass, fields
from typing import Any, Literal, TypeVar, cast, get_args, get_origin

from ..exceptions import DeviceNotFoundError, DeviceQueryError, ResponseError

_LOGGER = logging.getLogger(__name__)

# TypeVar for BaseMatrix generic return type
T = TypeVar("T", bound="BaseMatrix")
D = TypeVar("D")

# =============================================================================
# Helper Functions for Common Parsing Patterns
# =============================================================================


def _coerce_fields(cls: type, raw: dict[str, Any]) -> dict[str, Any]:
    """Convert one device's JSON object into keyword arguments for a dataclass

    Keys are converted from "space separated" to snake_case and keys the dataclass doesn't define are skipped. Values for
    int and bool fields are converted from the strings the API uses, with empty strings becoming None. Values for other
    fields (str, lists, nested objects) are passed through. None, and "null" for optional fields, become None.

    Args:
        cls: The dataclass to build arguments for
        raw: The device's JSON object

    Returns:
        dict[str, Any]: Keyword arguments for cls

    Raises:
        ResponseError: If an int or bool value can't be converted
    """
    field_types = {field.name: field.type for field in fields(cls)}
    converted: dict[str, Any] = {}
    for key, value in raw.items():
        name = key.replace(" ", "_")
        expected_type = field_types.get(name)
        if expected_type is None:
            _LOGGER.debug("Skipping unknown %s field %r", cls.__name__, key)
            continue

        # Unwrap Optional[T] (T | None) to T
        optional = False
        if get_origin(expected_type) is types.UnionType:
            args = get_args(expected_type)
            optional = type(None) in args
            expected_type = next(arg for arg in args if arg is not type(None))

        if value is None or (optional and value == "null") or (expected_type in (int, bool) and value == ""):
            converted[name] = None
        elif expected_type is int:
            try:
                converted[name] = int(value)
            except (TypeError, ValueError) as e:
                raise ResponseError(f"Invalid integer for {cls.__name__} field '{key}': {value!r}") from e
        elif expected_type is bool:
            if isinstance(value, bool):
                converted[name] = value
            elif isinstance(value, str) and value.lower() in ("true", "yes"):
                converted[name] = True
            elif isinstance(value, str) and value.lower() in ("false", "no"):
                converted[name] = False
            else:
                raise ResponseError(f"Invalid boolean for {cls.__name__} field '{key}': {value!r}")
        else:
            converted[name] = value
    return converted


def _build(cls: type[D], kwargs: dict[str, Any]) -> D:
    """Create a dataclass from parsed fields, raising ResponseError if required fields are missing

    Args:
        cls: The dataclass to create
        kwargs: Keyword arguments from _coerce_fields

    Returns:
        The dataclass instance

    Raises:
        ResponseError: If a required field is missing
    """
    try:
        return cls(**kwargs)
    except TypeError as e:
        raise ResponseError(f"Invalid {cls.__name__} data: {e}") from e


def _load_device_entries(response: str, key: str) -> list[dict[str, Any]]:
    """Load the device list from a 'config get device info/status' JSON response, dropping error entries

    The API reports devices it can't query as {"name": ..., "error": ...} entries. A query for one device raises for its
    error entry; in a list of several devices error entries are skipped so that one bad endpoint doesn't hide the rest.

    Args:
        response: The raw response string from the device
        key: The JSON key holding the device list ("devices" or "devices status")

    Returns:
        list[dict[str, Any]]: The device JSON objects without error entries

    Raises:
        ResponseError: If the response has no valid JSON or no device list
        DeviceQueryError: If the response's only entry is an error entry
    """
    json_start = response.find("{")
    if json_start == -1:
        raise ResponseError(f"No JSON content found in response: {response}")

    try:
        data = json.loads(response[json_start:])
    except json.JSONDecodeError as e:
        raise ResponseError(f"Invalid JSON in response: {e}") from e

    if not isinstance(data, dict) or not isinstance(data.get(key), list):
        raise ResponseError(f"No '{key}' key found in response: {response}")

    entries: list[dict[str, Any]] = data[key]
    errors = [entry for entry in entries if "error" in entry]
    if errors and len(entries) == 1:
        raise DeviceQueryError(errors[0].get("name", "unknown"), errors[0].get("error", "unknown error"))
    for entry in errors:
        _LOGGER.debug("Skipping device %s: %s", entry.get("name", "unknown"), entry.get("error"))
    return [entry for entry in entries if "error" not in entry]


def _build_devices(entries: list[dict[str, Any]], build: Callable[[dict[str, Any]], D]) -> list[D]:
    """Build one object per device entry; in a list of several devices, skip (and log) entries that don't parse

    Args:
        entries: The device JSON objects from _load_device_entries
        build: Builds one object from one device's JSON object

    Returns:
        list[D]: The objects built

    Raises:
        ResponseError: If the only entry doesn't parse
    """
    devices = []
    for entry in entries:
        try:
            devices.append(build(entry))
        except ResponseError as e:
            if len(entries) == 1:
                raise
            _LOGGER.warning("Skipping device %s: %s", entry.get("name", "unknown"), e)
    return devices


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
        raise ResponseError(f"Invalid assignment line format: {line}")

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
            ResponseError: If required version information cannot be found

        Notes:
            Searches through the response for version patterns, ignoring command echoes and other noise.

            Underlying NetworkHD API raw response format:
                ```
                API version: v<api>
                System version: v<web>(v<core>)
                ```

            Underlying NetworkHD API raw response example:
                ```
                API version: v1.21
                System version: v8.3.1(v8.3.8)
                ```
        """
        lines = response.strip().split("\n")

        api_version = cls._extract_api_version(lines)
        web_version, core_version = cls._extract_web_and_core_versions(lines)

        # Validate that we found all required information
        if api_version is None:
            raise ResponseError(f"Could not find API version in response: {response}")
        if web_version is None or core_version is None:
            raise ResponseError(f"Could not find System version in response: {response}")

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
            ResponseError: If response format is invalid or missing required settings

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                ipsetting is: ip4addr <ipv4> netmask <nm> gateway <gw>
                ```

            Underlying NetworkHD API raw response examples:
                ```
                ipsetting is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254
                ipsetting2 is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254
                ```
        """
        # Handle both ipsetting and ipsetting2 responses
        if "ipsetting is:" in response:
            settings_part = response.split("ipsetting is:")[1].strip()
        elif "ipsetting2 is:" in response:
            settings_part = response.split("ipsetting2 is:")[1].strip()
        else:
            raise ResponseError(f"Invalid IP settings response ResponseFormat: {response}")

        parts = settings_part.split()
        settings = {}
        for i in range(0, len(parts), 2):
            if i + 1 < len(parts):
                key = parts[i]
                value = parts[i + 1]
                settings[key] = value

        if not all(key in settings for key in ["ip4addr", "netmask", "gateway"]):
            raise ResponseError(f"Missing required IP settings in response: {response}")

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
            ResponseError: If response format is invalid

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                <hostname>'s alias is <alias|null>
                ```

            Underlying NetworkHD API raw response example:
                ```
                NHD-400-TX-E4CE02104E55's alias is source1
                ```

            Underlying NetworkHD API raw response erorr:
                ```
                "<device_name> does not exist."
                ```
        """

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
            raise ResponseError(f"Invalid name response ResponseFormat: {response}")

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
            Underlying NetworkHD API raw response format:
                ```
                Multiple lines, each with format <hostname>'s alias is <alias|null>
                ```

            Underlying NetworkHD API raw response example:
                ```
                NHD-400-TX-E4CE02104E55's alias is source1
                NHD-400-TX-E4CE02104E56's alias is source2
                NHD-400-RX-E4CE02104A57's alias is display1
                NHD-400-RX-E4CE02104A58's alias is null
                ```
        """
        names = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and "'s alias is " in line:
                names.append(cls.parse_single(line))
        return names


@dataclass
class DeviceJsonStringGroup:
    """Group configuration for device json string"""

    name: str
    sequence: int


@dataclass
class DeviceJsonString:
    """Device information from 'config get devicejsonstring'"""

    # Required fields
    aliasName: str  # Note: API uses camelCase, keeping original field name
    deviceType: str
    group: list[DeviceJsonStringGroup]
    ip: str
    online: bool
    sequence: int
    trueName: str

    # Optional fields
    nameoverlay: bool | None = None  # TX only (600 series)
    txName: str | None = None  # RX only

    @classmethod
    def parse(cls, response: str) -> list["DeviceJsonString"]:
        """Parse 'config get devicejsonstring' response

        Args:
            response: The raw response string from the device

        Returns:
            list[DeviceJsonString]: List of parsed device json string objects

        Raises:
            ResponseError: If the response isn't valid device JSON

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                device json string:
                [
                    {
                        "aliasName" : "<alias>",
                        "deviceType" : "Transmitter",
                        "group" : [
                            {
                                "name" : "ungrouped",
                                "sequence" : 1
                            }
                        ],
                        "ip" : "<ip>",
                        "online" : true,
                        "sequence" : 1,
                        "trueName" : "<hostname>"
                    },
                    ... more devices ...
                ]
                ```

            Underlying NetworkHD API raw response example:
                ```
                device json string:
                [
                    {
                        "aliasName" : "SOURCE1",
                        "deviceType" : "Transmitter",
                        "group" : [
                            {
                                "name" : "ungrouped",
                                "sequence" : 1
                            }
                        ],
                        "ip" : "169.254.232.229",
                        "online" : true,
                        "sequence" : 1,
                        "trueName" : "NHD-140-TX-E4CE02102EE1"
                    }
                ]
                ```
        """
        json_start = response.find("[")
        if json_start == -1:
            raise ResponseError(f"No JSON array content found in response: {response}")

        try:
            data = json.loads(response[json_start:])
        except json.JSONDecodeError as e:
            raise ResponseError(f"Invalid JSON in response: {e}") from e
        if not isinstance(data, list) or not all(isinstance(device_data, dict) for device_data in data):
            raise ResponseError(f"Expected a JSON list of device objects in response: {response}")

        devices = []
        for device_data in data:
            converted_data = _coerce_fields(cls, device_data)
            if isinstance(device_data.get("group"), list):
                converted_data["group"] = [
                    DeviceJsonStringGroup(name=group_item.get("name", ""), sequence=group_item.get("sequence", 0))
                    for group_item in device_data["group"]
                ]
            devices.append(_build(cls, converted_data))

        return devices


@dataclass
class DeviceInfoAudioOutput:
    """Audio output configuration from device info"""

    mute: bool
    name: str


@dataclass
class DeviceInfoSinkPowerCecCommands:
    """CEC command configuration for device info sinkpower"""

    onetouchplay: str
    standby: str


@dataclass
class DeviceInfoSinkPowerRs232Commands:
    """RS232 command configuration for device info sinkpower"""

    mode: str
    onetouchplay: str
    param: str
    standby: str


@dataclass
class DeviceInfoSinkPower:
    """Sink power configuration for RX devices"""

    mode: str
    cec: DeviceInfoSinkPowerCecCommands | None = None
    rs232: DeviceInfoSinkPowerRs232Commands | None = None


@dataclass
class DeviceInfo:
    """Device information from 'config get device info'"""

    # Required fields
    aliasname: str
    name: str

    # Common fields (all device types)
    edid: str | None = None
    gateway: str | None = None
    ip4addr: str | None = None
    ip_mode: str | None = None
    mac: str | None = None
    netmask: str | None = None
    version: str | None = None

    # RX-only fields
    audio: list[DeviceInfoAudioOutput] | None = None
    sourcein: str | None = None
    analog_audio_source: str | None = None
    hdmi_audio_source: str | None = None
    sinkpower: DeviceInfoSinkPower | None = None
    video_mode: str | None = None
    video_stretch_type: str | None = None
    video_timing: str | None = None

    # TX-only fields
    cbr_avg_bitrate: int | None = None
    enc_fps: int | None = None
    enc_gop: int | None = None
    enc_rc_mode: str | None = None
    fixqp_iqp: int | None = None
    fixqp_pqp: int | None = None
    profile: str | None = None
    transport_type: str | None = None
    vbr_max_bitrate: int | None = None
    vbr_max_qp: int | None = None
    vbr_min_qp: int | None = None
    audio_input_type: str | None = None
    analog_audio_direction: str | None = None
    bandwidth_adjust_mode: int | None = None
    bit_perpixel: int | None = None
    color_space: str | None = None
    stream0_enable: bool | None = None
    stream0fps_by2_enable: bool | None = None
    stream1_enable: bool | None = None
    stream1_scale: str | None = None
    stream1fps_by2_enable: bool | None = None
    video_input: bool | None = None
    video_source: str | None = None

    # NHD-400 specific
    km_over_ip_enable: bool | None = None
    videodetection: str | None = None

    # NHD-600 specific
    serial_param: str | None = None
    temperature: int | None = None
    genlock_scaling_resolution: str | None = None
    hdcp14_enable: bool | None = None
    hdcp22_enable: bool | None = None

    # Legacy/deprecated fields
    hdcp: bool | None = None

    @classmethod
    def parse(cls, response: str) -> list["DeviceInfo"]:
        """Parse 'config get device info' response

        Args:
            response: The raw response string from the device

        Returns:
            list[DeviceInfo]: List of parsed device information objects. In a response for several devices, entries the
                controller reports as errors (for example a device that can't be queried), and entries with values that
                can't be converted (logged), are skipped.

        Raises:
            ResponseError: If the response isn't valid device JSON
            DeviceQueryError: If the response's only device entry is an error

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                devices json info:
                {
                "devices" : [
                    {
                        "aliasname" : "<alias>",
                        "name" : "<hostname>",
                        ... other fields ...
                    },
                    ... more devices ...
                ]
                }
                ```

            Underlying NetworkHD API raw response example:
                ```
                devices json info:
                {
                "devices" : [
                    {
                        "aliasname" : "DISPLAY1",
                        "edid" : "null",
                        "gateway" : "",
                        "ip4addr" : "169.254.7.192",
                        "name" : "NHD-220-RX-E4CE02107DF5"
                    }
                ]
                }
                ```
        """
        return _build_devices(_load_device_entries(response, "devices"), cls._parse_device)

    @classmethod
    def _parse_device(cls, device_data: dict[str, Any]) -> "DeviceInfo":
        """Build one DeviceInfo from one device's JSON object"""
        converted_data = _coerce_fields(cls, device_data)

        audio = device_data.get("audio")
        if isinstance(audio, list):
            converted_data["audio"] = [
                DeviceInfoAudioOutput(mute=audio_item.get("mute", False), name=audio_item.get("name", ""))
                for audio_item in audio
            ]

        sinkpower = device_data.get("sinkpower")
        if isinstance(sinkpower, dict):
            cec_data = sinkpower.get("cec")
            rs232_data = sinkpower.get("rs232")

            cec_commands = None
            if cec_data:
                cec_commands = DeviceInfoSinkPowerCecCommands(
                    onetouchplay=cec_data.get("onetouchplay", ""), standby=cec_data.get("standby", "")
                )

            rs232_commands = None
            if rs232_data:
                rs232_commands = DeviceInfoSinkPowerRs232Commands(
                    mode=rs232_data.get("mode", ""),
                    onetouchplay=rs232_data.get("onetouchplay", ""),
                    param=rs232_data.get("param", ""),
                    standby=rs232_data.get("standby", ""),
                )

            converted_data["sinkpower"] = DeviceInfoSinkPower(
                mode=sinkpower.get("mode", ""), cec=cec_commands, rs232=rs232_commands
            )

        return _build(cls, converted_data)


@dataclass
class DeviceStatus:
    """Device status information from 'config get device status'"""

    # Common fields (all device types)
    aliasname: str
    name: str

    # Common fields (NHD-110/200/210 series)
    line_out_audio_enable: bool | None = None
    stream_frame_rate: int | None = None
    stream_resolution: str | None = None

    # RX only fields (NHD-110/200/210 series)
    audio_bitrate: int | None = None
    audio_input_format: str | None = None
    hdcp_status: str | None = None  # NHD-110/200/210 series uses "hdcp status"
    hdmi_out_active: bool | None = None
    hdmi_out_audio_enable: bool | None = None
    hdmi_out_frame_rate: int | None = None
    hdmi_out_resolution: str | None = None
    stream_error_count: int | None = None

    # TX only fields (NHD-110/200/210 series)
    audio_stream_ip_address: str | None = None
    encoding_enable: bool | None = None
    hdmi_in_active: bool | None = None
    hdmi_in_frame_rate: int | None = None
    resolution: str | None = None
    video_stream_ip_address: str | None = None

    # NHD-400 series fields
    hdcp: str | None = None  # NHD-400/600 series uses "hdcp"
    audio_output_format: str | None = None  # NHD-400 RX only

    @classmethod
    def parse(cls, response: str) -> list["DeviceStatus"]:
        """Parse 'config get device status' response

        Args:
            response: The raw response string from the device

        Returns:
            list[DeviceStatus]: List of parsed device status information objects. In a response for several devices, entries the
                controller reports as errors (for example a device that can't be queried), and entries with values that
                can't be converted (logged), are skipped.

        Raises:
            ResponseError: If the response isn't valid device JSON
            DeviceQueryError: If the response's only device entry is an error

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                devices status info:
                {
                "devices status" : [
                    {
                        "aliasname" : "<alias>",
                        "name" : "<hostname>",
                        ... other fields ...
                    },
                    ... more devices ...
                ]
                }
                ```

            Underlying NetworkHD API raw response example:
                ```
                devices status info:
                {
                "devices status" : [
                    {
                        "aliasname" : "DISPLAY1",
                        "hdcp" : "hdcp14",
                        "hdmi out active" : "true",
                        "hdmi out frame rate" : "60",
                        "hdmi out resolution" : "1920x1080",
                        "name" : "NHD-600-RX-D88039E5E525"
                    }
                ]
                }
                ```
        """
        return _build_devices(
            _load_device_entries(response, "devices status"),
            lambda device_data: _build(cls, _coerce_fields(cls, device_data)),
        )


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
    def parse(cls: type[T], response: str) -> T:
        """Parse 'matrix get' response (and similar variants) with standard format

        Args:
            response: The raw response string from the device

        Returns:
            BaseMatrix: Parsed matrix assignment information object

        Raises:
            ResponseError: If matrix assignment line format is invalid

        Notes:
            Ignores everything before the matrix information header and parses only the actual matrix data.

            Underlying NetworkHD API raw response format:
                ```
                matrix [type] information:
                <TXn|NULL> <RX1>
                <TXn|NULL> <RX2>
                ...
                <TXn|NULL> <RXn>
                ```

            Underlying NetworkHD API raw response examples:
                ```
                matrix information:
                Source1 Display1
                Source1 Display2
                Source2 Display3
                NULL Display4
                ```

                ```
                matrix video information:
                Source1 Display1
                Source1 Display2
                Source2 Display3
                NULL Display4
                ```
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 2:
                raise ResponseError(f"Invalid matrix assignment line format, expected 'TX RX': {line}")

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
            ResponseError: If response format is invalid or missing TX for RX

        Notes:
            Ignores everything before the 'matrix audio3 information:' line and parses only the actual assignment data.

            Underlying NetworkHD API raw response format:
                ```
                matrix audio3 information:
                <RX1>
                <TX1>
                ```

            Underlying NetworkHD API raw response example:
                ```
                matrix audio3 information:
                Display1 Source1
                Display2 Source3
                Display5 Source2
                ```
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
                raise ResponseError(f"Invalid matrix audio3 response format, missing TX for RX: {rx}")

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

            Underlying NetworkHD API raw response format:
                ```
                matrix infrared2 information:
                <TX1|RX1> <mode> (<TXn|RXn>)
                <TX2|RX2> <mode> (<TXn|RXn>)
                ...
                ```

            Underlying NetworkHD API raw response example:
                ```
                matrix infrared2 information:
                source1 single display1
                display1 api
                source2 api
                display2 null
                ```
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            device, mode, target_device = _parse_device_mode_assignment(line)
            validated_mode = cast(Literal["single", "api", "all", "null"], mode)
            assignments.append(
                InfraredReceiverAssignment(device=device, mode=validated_mode, target_device=target_device)
            )

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

            Underlying NetworkHD API raw response format:
                ```
                matrix serial2 information:
                <TX1|RX1> <mode> (<TXn|RXn>)
                <TX2|RX2> <mode> (<TXn|RXn>)
                ...
                ```

            Underlying NetworkHD API raw response example:
                ```
                matrix serial2 information:
                source1 single display1
                display1 api
                source2 api
                display2 null
                ```
        """
        data_lines = _skip_to_header(response, "information:")
        assignments = []

        for line in data_lines:
            device, mode, target_device = _parse_device_mode_assignment(line)
            validated_mode = cast(Literal["single", "api", "all", "null"], mode)
            assignments.append(SerialPortAssignment(device=device, mode=validated_mode, target_device=target_device))

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
            ResponseError: If no valid scenes are found in response

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                scene list:
                <videowall1>-<scene1> <videowall1>-<scene2> ... <videowalln>-<scenen>
                ```

            Underlying NetworkHD API raw response example:
                ```
                scene list:
                OfficeVW-Splitmode OfficeVW-Combined
                ```
        """
        scene_tuples = _parse_scene_items(response, "scene list:")

        if not scene_tuples:
            raise ResponseError(f"No valid scenes found in response: {response}")

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
            Underlying NetworkHD API raw response format:
                ```
                Video wall information:
                <videowall1>-<scene1>_<Lscreen1> <TX>
                Row 1: <RX1> <RX2>
                Row 2: <RX3> <RX4>
                ...
                ```

            Underlying NetworkHD API raw response example:
                ```
                Video wall information:
                OfficeVW-Combined_TopTwo source1
                Row 1: display1 display2
                OfficeVW-AllCombined_AllDisplays source2
                Row 1: display1 display2 display3
                Row 2: display4 display5 display6
                ```
        """
        data_lines = _skip_to_header(response, "Video wall information:")
        screens: list[VideoWallLogicalScreen] = []
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
            raise ResponseError(f"Invalid screen header format, expected 'videowall-scene_logicalscreen TX': {line}")

        if "_" not in parts[0]:
            raise ResponseError(f"Invalid screen header format, missing logical screen separator '_': {line}")

        if "-" not in parts[0]:
            raise ResponseError(f"Invalid screen header format, missing videowall-scene separator '-': {line}")

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
            Underlying NetworkHD API raw response format:
                ```
                wscene2 list:
                <videowall1>-<wscene1> <videowall1>-<wscene2> ... <videowalln>-<wscenen>
                ```

            Underlying NetworkHD API raw response example:
                ```
                wscene2 list:
                OfficeVW-windowscene1 OfficeVW-windowscene2
                ```
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
            ResponseError: If preset multiview layout line format is invalid

        Notes:
            Ignores everything before the 'mscene list:' line and parses only the actual layout data.

            Underlying NetworkHD API raw response format:
                ```
                mscene list:
                <RX> <lname1> <lname2> ... <lnamen>
                <RXn> <lname3> <lname4> ...
                ```

            Underlying NetworkHD API raw response example:
                ```
                mscene list:
                display5 gridlayout piplayout
                display6 pip2layout
                display7 grid5layout grid6layout
                ```
        """
        data_lines = _skip_to_header(response, "mscene list:")
        layouts = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 2:
                raise ResponseError(
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
            ResponseError: If tile configuration format is invalid

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                <tx>:<x>_<y>_<width>_<height>:<scaling>
                ```

            Underlying NetworkHD API raw response example:
                ```
                source1:0_0_960_540:fit
                ```
        """
        parts = tile_config.split(":")
        if len(parts) != 3:
            raise ResponseError(f"Invalid tile configuration: {tile_config}")

        tx = parts[0]
        coords = parts[1].split("_")
        scaling = parts[2]

        if len(coords) != 4:
            raise ResponseError(f"Invalid tile coordinates: {parts[1]}")

        validated_scaling = cast(Literal["fit", "stretch"], scaling)
        return cls(
            tx=tx,
            x=int(coords[0]),
            y=int(coords[1]),
            width=int(coords[2]),
            height=int(coords[3]),
            scaling=validated_scaling,
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
            ResponseError: If multiview layout line format is invalid or tile configuration is invalid

        Notes:
            Underlying NetworkHD API raw response format:
                ```
                mview information:
                <RX1> [tile|overlay] <TX1>:<X1>_Y1>_<W1>_<H1>:[fit|stretch] <TX2>:<X2>_Y2>_<W2>_<H2>:[fit|stretch] ...
                ```

            Underlying NetworkHD API raw response example:
                ```
                mview information:
                display10 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit
                display11 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit
                ```
        """
        data_lines = _skip_to_header(response, "information:")
        configurations = []

        for line in data_lines:
            line = line.strip()

            parts = line.split()
            if len(parts) < 3:
                raise ResponseError(f"Invalid multiview layout line format, expected 'RX mode tile1 tile2...': {line}")

            rx = parts[0]
            mode = parts[1]

            if mode not in ["tile", "overlay"]:
                raise ResponseError(f"Invalid multiview mode '{mode}', expected 'tile' or 'overlay': {line}")

            tile_configs = parts[2:]

            tiles = []
            for tile_config in tile_configs:
                try:
                    tiles.append(MultiviewTile.parse_tile_config(tile_config))
                except ValueError as e:
                    raise ResponseError(f"Invalid tile configuration in line '{line}': {e}") from e

            validated_mode = cast(Literal["tile", "overlay"], mode)
            configurations.append(CustomMultiviewLayout(rx=rx, mode=validated_mode, tiles=tiles))

        return cls(configurations=configurations)
