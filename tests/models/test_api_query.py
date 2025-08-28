"""Comprehensive unit tests for API query models.

This test suite covers:
- Success cases with various response formats
- Failure cases with malformed data
- Edge cases with empty/invalid parameters
- Exception scenarios that should raise errors
- All parsing utilities and model classes
"""

import pytest

from wyrestorm_networkhd.exceptions import DeviceNotFoundError
from wyrestorm_networkhd.models.api_query import (
    BaseMatrix,
    CustomMultiviewLayoutList,
    DeviceInfo,
    DeviceInfoAudioOutput,
    DeviceInfoSinkPower,
    DeviceInfoSinkPowerCecCommands,
    DeviceInfoSinkPowerRs232Commands,
    DeviceJsonString,
    DeviceJsonStringGroup,
    DeviceStatus,
    EndpointAliasHostname,
    IpSetting,
    MatrixAudio3,
    MatrixInfrared2,
    MatrixSerial2,
    MultiviewTile,
    PresetMultiviewLayoutList,
    Version,
    VideoWallLogicalScreenList,
    # Video wall models
    VideoWallSceneList,
    VideowallWithinWallSceneList,
    _parse_device_mode_assignment,
    # Core parsing utilities
    _parse_scene_items,
    _skip_to_header,
)

# =============================================================================
# Test Fixtures - API Response Examples
# =============================================================================


@pytest.fixture(scope="session")
def api_v6_7_responses() -> dict[str, str]:
    """API v6.7 response examples from documentation."""
    return {
        # Version information
        "version": "API version: v1.21\nSystem version: v8.3.1(v8.3.8)",
        "version_no_core": "API version: v1.21\nSystem version: v8.3.1",
        "version_with_echo": "Welcome to NetworkHD\nconfig get version\nAPI version: v1.21\nSystem version: v8.3.1(v8.3.8)",
        # IP settings
        "ipsetting": "ipsetting is: ip4addr 169.254.1.1 netmask 255.255.0.0 gateway 169.254.1.254",
        "ipsetting2": "ipsetting2 is: ip4addr 192.168.11.243 netmask 255.255.255.0 gateway 192.168.11.1",
        # Device JSON responses
        "device_json": 'device json string: {"devices": [{"name": "source1", "type": "tx", "status": "online"}]}',
        "devices_json": 'devices json info: {"devices": [{"name": "source1", "type": "tx", "status": "online"}]}',
        # Device status responses with proper type examples
        "device_status_nhd_110_210": """devices status info:
{
    "devices status" : [
        {
            "aliasname" : "SOURCE1",
            "audio stream ip address" : "224.48.46.225",
            "encoding enable" : "true",
            "hdmi in active" : "true",
            "hdmi in frame rate" : "60",
            "line out audio enable" : "false",
            "name" : "NHD-140-TX-E4CE02102EE1",
            "resolution" : "1920x1080",
            "stream frame rate" : "60",
            "stream resolution" : "1920x1080",
            "video stream ip address" : "224.16.46.225"
        },
        {
            "aliasname" : "DISPLAY1",
            "audio bitrate" : "1536000",
            "audio input format" : "lpcm",
            "hdcp status" : "hdcp14",
            "hdmi out active" : "true",
            "hdmi out audio enable" : "true",
            "hdmi out frame rate" : "60",
            "hdmi out resolution" : "1920x1080",
            "line out audio enable" : "true",
            "name" : "NHD-210-RX-E4CE02107132",
            "stream error count" : "0",
            "stream frame rate" : "60",
            "stream resolution" : "1920x1080"
        }
    ]
}""",
        "device_status_nhd_400": """devices status info:
{
    "devices status" : [
        {
            "aliasname" : "DISPLAY1",
            "audio bitrate" : "3072000",
            "audio output format" : "lpcm",
            "hdcp" : "hdcp22",
            "hdmi out active" : "true",
            "hdmi out frame rate" : "60",
            "hdmi out resolution" : "1920x1080",
            "name" : "NHD-400-RX-E4CE02103CB3"
        },
        {
            "aliasname" : "SOURCE1",
            "audio bitrate" : "3072000",
            "audio input format" : "lpcm",
            "hdcp" : "hdcp22",
            "hdmi in active" : "true",
            "hdmi in frame rate" : "60",
            "name" : "NHD-400-TX-E4CE0210B6D4",
            "resolution" : "1920x1080"
        }
    ]
}""",
        "device_status_nhd_600": """devices status info:
{
    "devices status" : [
        {
            "aliasname" : "DISPLAY1",
            "hdcp" : "hdcp14",
            "hdmi out active" : "true",
            "hdmi out frame rate" : "60",
            "hdmi out resolution" : "1920x1080",
            "name" : "NHD-600-RX-D88039E5E525"
        },
        {
            "aliasname" : "SOURCE1",
            "hdcp" : "hdcp14",
            "hdmi in active" : "true",
            "hdmi in frame rate" : "60",
            "name" : "NHD-600-TX-D88039E5ED1E",
            "resolution" : "1920x1080"
        }
    ]
}""",
        # Device info responses with proper nested objects and type examples
        "device_info_nhd_110_210": """devices json info:
{
    "devices" : [
        {
            "aliasname" : "DISPLAY1",
            "audio" : [
                {
                    "mute" : false,
                    "name" : "lineout1"
                }
            ],
            "edid" : "null",
            "gateway" : "",
            "hdcp" : true,
            "ip4addr" : "169.254.7.192",
            "ip_mode" : "autoip",
            "mac" : "e4:ce:02:10:7d:f5",
            "name" : "NHD-220-RX-E4CE02107DF5",
            "netmask" : "255.255.0.0",
            "sourcein" : "NHD-140-TX-E4CE02102EE1;",
            "version" : "v2.12.2"
        },
        {
            "aliasname" : "SOURCE1",
            "cbr_avg_bitrate" : 10000,
            "edid" : "00FFFFFFFFFFFF001C4501000100000008120103807341780ACF74A3574CB023094",
            "enc_fps" : 60,
            "enc_gop" : 60,
            "enc_rc_mode" : "vbr",
            "fixqp_iqp" : 25,
            "fixqp_pqp" : 25,
            "gateway" : "169.254.0.254",
            "hdcp" : true,
            "ip4addr" : "169.254.85.242",
            "ip_mode" : "fixed",
            "mac" : "e4:ce:02:10:2e:e3",
            "name" : "NHD-140-TX-E4CE02102EE3",
            "netmask" : "255.255.0.0",
            "profile" : "hp",
            "sourcein" : "unknown",
            "transport_type" : "raw",
            "vbr_max_bitrate" : 20000,
            "vbr_max_qp" : 51,
            "vbr_min_qp" : 0,
            "version" : "v1.0.6"
        }
    ]
}""",
        "device_info_nhd_400": """devices json info:
{
    "devices" : [
        {
            "aliasname" : "DISPLAY1",
            "edid" : "null",
            "gateway" : "",
            "ip4addr" : "169.254.6.107",
            "ip_mode" : "dhcp",
            "km_over_ip_enable" : "true",
            "mac" : "e4:ce:02:10:2e:f0",
            "name" : "NHD-400-RX-E4CE02102EF0",
            "netmask" : "255.255.0.0",
            "version" : "v0.10.1",
            "videodetection" : "lost"
        },
        {
            "aliasname" : "SOURCE1",
            "audio_input_type" : "auto",
            "edid" : "null",
            "gateway" : "169.254.0.254",
            "ip4addr" : "169.254.5.209",
            "ip_mode" : "autoip",
            "km_over_ip_enable" : "true",
            "mac" : "e4:ce:02:10:6e:9e",
            "name" : "NHD-400-TX-E4CE02106E9E",
            "netmask" : "255.255.0.0",
            "version" : "v0.10.1",
            "videodetection" : "lost"
        }
    ]
}""",
        "device_info_nhd_600": """devices json info:
{
    "devices" : [
        {
            "aliasname" : "DISPLAY1",
            "analog_audio_source" : "analog",
            "edid" : "",
            "gateway" : "0.0.0.0",
            "hdmi_audio_source" : "hdmi",
            "ip4addr" : "169.254.38.229",
            "ip_mode" : "dhcp",
            "mac" : "d8:80:39:e5:e5:25",
            "name" : "NHD-600-RX-D88039E5E525",
            "netmask" : "255.255.0.0",
            "serial_param" : "57600-8n1",
            "sinkpower" : {
                "cec" : {
                    "onetouchplay" : "4004",
                    "standby" : "ff36"
                },
                "mode" : "CEC",
                "rs232" : {
                    "mode" : "ascii",
                    "onetouchplay" : "!POWERON~",
                    "param" : "115200-8n1",
                    "standby" : "!POWROFF~"
                }
            },
            "temperature" : 38,
            "version" : "3.6.0.0",
            "video_mode" : "fast_switch",
            "video_stretch_type" : "none",
            "video_timing" : "1080P@50"
        },
        {
            "aliasname" : "SOURCE1",
            "analog_audio_direction" : "INPUT",
            "bandwidth_adjust_mode" : 0,
            "bit_perpixel" : 8,
            "color_space" : "RGB",
            "edid" : "00ffffffffffff004dd903f901010101011b0103806c3d780a0dc9a05747982712484c",
            "gateway" : "0.0.0.0",
            "hdcp14_enable" : true,
            "hdcp22_enable" : true,
            "ip4addr" : "169.254.2.228",
            "ip_mode" : "dhcp",
            "mac" : "d8:80:39:e5:e4:01",
            "name" : "NHD-600-TX-D88039E5E401",
            "netmask" : "255.255.0.0",
            "serial_param" : "57600-8n1",
            "stream0_enable" : true,
            "stream0fps_by2_enable" : false,
            "stream1_enable" : true,
            "stream1_scale" : "960x544",
            "stream1fps_by2_enable" : false,
            "temperature" : 42,
            "version" : "3.6.0.0",
            "video_input" : true,
            "video_source" : "hdmi",
            "video_timing" : "1920x1080P@60"
        }
    ]
}""",
        # Device JSON string responses
        "device_json_string_mixed": """device json string:
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
    },
    {
        "aliasName" : "DISPLAY1",
        "deviceType" : "Receiver",
        "group" : [
            {
                "name" : "MainDisplays",
                "sequence" : 2
            }
        ],
        "ip" : "169.254.148.121",
        "online" : true,
        "sequence" : 2,
        "trueName" : "NHD-140-RX-E4CE02102EE2",
        "txName" : "SOURCE1"
    },
    {
        "aliasName" : "SOURCE7",
        "deviceType" : "Transmitter",
        "group" : [
            {
                "name" : "ungrouped",
                "sequence" : 1
            }
        ],
        "ip" : "169.254.1.1",
        "nameoverlay" : true,
        "online" : true,
        "sequence" : 7,
        "trueName" : "NHD-600-TX-D88039E5E401"
    }
]""",
        "device_json_string_single": """device json string:
[
    {
        "aliasName" : "TEST1",
        "deviceType" : "Transmitter",
        "group" : [
            {
                "name" : "testgroup",
                "sequence" : 1
            }
        ],
        "ip" : "192.168.1.100",
        "online" : false,
        "sequence" : 1,
        "trueName" : "TEST-DEVICE-001"
    }
]""",
        # Device aliases
        "device_name_single": "NHD-400-RX's alias is display1",
        "device_alias": "NHD-400-TX-E4CE02104E55's alias is source1",
        "device_aliases": "NHD-400-TX-E4CE02104E55's alias is source1\nNHD-400-TX-E4CE02104E56's alias is source2\nNHD-400-RX-E4CE02104A57's alias is display1\nNHD-400-RX-E4CE02104A58's alias is null",
        # Matrix information - All assignments
        "matrix": "matrix information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_with_echo": "matrix get\nmatrix information:\nSource1 Display1\nSource2 Display2",
        "single_matrix_assignment": "matrix information:\nSource1 Display1",
        "empty_matrix": "matrix information:",
        "matrix_video": "matrix video information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_audio": "matrix audio information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_audio2": "matrix audio2 information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_audio3": "matrix audio3 information:\nDisplay1\nSource1\nDisplay2\nSource3\nDisplay5\nSource2",
        "matrix_usb": "matrix usb information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_infrared": "matrix infrared information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nNULL Display4",
        "matrix_infrared2": "matrix infrared2 information:\nsource1 single display1\ndisplay1 api\nsource2 api\ndisplay2 null",
        "matrix_serial": "matrix serial information:\nSource1 Display1\nSource1 Display2\nSource2 Display3\nnull Display4",
        "matrix_serial2": "matrix serial2 information:\nsource1 single display1\ndisplay1 api\nsource2 api\ndisplay2 null",
        # Matrix information - Filtered responses (single items)
        "matrix_video_filtered": "matrix video information:\nSource1 Display1\nSource2 Display3",
        "matrix_audio_filtered": "matrix audio information:\nSource1 Display1\nSource2 Display3",
        "matrix_audio2_filtered": "matrix audio2 information:\nSource1 Display1\nSource2 Display3",
        "matrix_audio3_filtered": "matrix audio3 information:\nDisplay1\nSource3",
        "matrix_usb_filtered": "matrix usb information:\nSource1 Display1\nSource2 Display3",
        "matrix_infrared_filtered": "matrix infrared information:\nSource1 Display1\nSource2 Display3",
        "matrix_serial_filtered": "matrix serial information:\nSource1 Display1\nSource2 Display3",
        "matrix_infrared2_filtered": "matrix infrared2 information:\ndisplay1 api\nsource1 single display1",
        "matrix_serial2_filtered": "matrix serial2 information:\ndisplay1 api\nsource1 single display1",
        # Video wall scenes
        "video_wall_scenes": "scene list:\nOfficeVW-Splitmode OfficeVW-Combined",
        "video_wall_with_echo": "Welcome to NetworkHD\nvw get\nVideo wall information:\nOfficeVW-Combined_TopTwo source1\nRow 1: display1 display2",
        "single_scene": "scene list:\nOfficeVW-Single",
        "empty_scene_list": "scene list:",
        "video_wall_logical": "Video wall information:\nOfficeVW-Combined_TopTwo source1\nRow 1: display1 display2\nOfficeVW-AllCombined_AllDisplays source2\nRow 1: display1 display2 display3\nRow 2: display4 display5 display6",
        "wscene2_list": "wscene2 list:\nOfficeVW-windowscene1 OfficeVW-windowscene2",
        "mscene_list": "mscene list:\ndisplay5 gridlayout piplayout\ndisplay6 pip2layout\ndisplay7 grid5layout grid6layout",
        # Video wall scenes - Filtered responses
        "mscene_filtered": "mscene list:\ndisplay6 pip2layout",
        # Multiview
        "multiview_tile": "source1:0_0_960_540:fit",
        "custom_multiview": "mview information:\ndisplay10 tile source1:0_0_960_540:fit source2:960_0_960_540:fit source3:0_540_960_540:fit source4:960_540_960_540:fit\ndisplay11 overlay source1:100_50_256_144:fit source2:0_0_1920_1080:fit",
        "single_tile": "mview information:\ndisplay10 tile source1:0_0_960_540:fit",
        # Multiview - Filtered responses (simplified format for single item)
        "custom_multiview_filtered": "mview information:\ndisplay11 overlay source1:0_0_1920_1080:fit",
        # Common test patterns
        "multiview_tile_stretch": "source2:100_50_800_600:stretch",
        "command_echo_header": "Welcome\nCommand echo\nmatrix information:\nSource1 Display1\nSource2 Display2",
        "command_echo_no_header": "Welcome\nCommand echo\nNo header here",
    }


@pytest.fixture(scope="session")
def malformed_responses() -> dict[str, str]:
    """Malformed API responses for testing error handling, organized by model section."""
    return {
        # Common/Global error patterns
        "empty": "",
        "whitespace": "   \n  \t  ",
        "missing_prefix": "No prefix here",
        "invalid_json": "device json string: {invalid json",
        # 13.1 System Configuration errors
        "version_missing_api": "System version: v8.3.1(v8.3.8)",
        "version_missing_system": "API version: v1.21",
        "ipsetting_invalid_format": "Invalid response format",
        "ipsetting_missing_fields": "ipsetting is: ip4addr 192.168.1.1",  # Missing netmask and gateway
        # 13.2 Device Configuration errors
        "endpoint_alias_hostname_invalid_format": "Invalid format",
        "endpoint_alias_hostname_quoted_device": '"DISPLAY1" does not exist.',
        "device_status_missing_header": "No devices status info header",
        "device_status_invalid_json": "devices status info:\n{invalid json}",
        "device_status_missing_devices_key": 'devices status info:\n{"other_key": []}',
        "device_status_no_json": "devices status info:\nno json content here",
        "device_info_missing_header": "No devices json info header",
        "device_info_invalid_json": "devices json info:\n{invalid json}",
        "device_info_missing_devices_key": 'devices json info:\n{"other_key": []}',
        "device_info_no_json": "devices json info:\nno json content here",
        "device_json_string_missing_header": "No device json string header",
        "device_json_string_invalid_json": "device json string:\n[invalid json}",
        "device_json_string_not_array": 'device json string:\n{"not": "array"}',
        "device_json_string_no_json": "device json string:\nno json content here",
        # 13.3 Stream Matrix Switching errors
        "matrix_malformed_assignment": "matrix information:\nSource1\nSource2 Display2",  # Missing RX for Source1
        "matrix_audio3_odd_lines": "matrix audio3 information:\nDisplay1\nSource1\nDisplay2",  # Missing TX
        # 13.4 Video Walls errors
        "video_wall_invalid_format": "Video wall information:\nInvalidFormat",
        "video_wall_missing_logical_screen_separator": "Video wall information:\nOfficeVW-CombinedTopTwo source1\nRow 1: display1 display2",
        "video_wall_missing_videowall_scene_separator": "Video wall information:\nOfficeVWCombined_TopTwo source1\nRow 1: display1 display2",
        # 13.5 Multiview errors
        "multiview_tile_config_missing_height": "source1:0_0_960:fit",  # Missing height
        "multiview_tile_config_missing_colon": "source1:0_0_960_540",  # Missing scaling
        "multiview_invalid_mode": "mview information:\ndisplay10 invalid_mode source1:0_0_960_540:fit",
        "multiview_missing_tiles": "mview information:\ndisplay10 tile",  # Missing tiles
        "multiview_malformed_tile_line": "mview information:\ndisplay10 tile source1:invalid_format",
        "multiview_no_valid_tiles": "mview information:\ndisplay10 tile invalid:tile:format another:bad:tile",  # Invalid tile formats
        "preset_multiview_malformed_line": "mscene list:\ndisplay5",  # Missing layout names
        "preset_multiview_no_layout_names": "mscene list:\ndisplay5 \t",  # RX with layout name as just whitespace
    }


# =============================================================================
# Test Core Parsing Utilities
# =============================================================================


class TestParsingUtilities:
    """Test the core parsing utility functions."""

    def test_skip_to_header_success(self, api_v6_7_responses):
        """Test successful header skipping."""
        response = api_v6_7_responses["command_echo_header"]
        result = _skip_to_header(response, "matrix information:")

        assert "Source1 Display1" in result
        assert "Source2 Display2" in result
        assert "Welcome" not in result
        assert "Command echo" not in result

    def test_skip_to_header_missing_header(self, api_v6_7_responses):
        """Test header skipping with missing header."""
        response = api_v6_7_responses["command_echo_no_header"]
        result = _skip_to_header(response, "matrix information:")

        # Should return empty list when header not found
        assert result == []

    def test_parse_device_mode_assignment_success(self):
        """Test successful device mode assignment parsing."""
        line = "source1 single display1"
        result = _parse_device_mode_assignment(line)

        assert result == ("source1", "single", "display1")

    def test_parse_device_mode_assignment_api_mode(self):
        """Test device mode assignment parsing with api mode."""
        line = "display1 api"
        result = _parse_device_mode_assignment(line)

        assert result == ("display1", "api", None)

    def test_parse_device_mode_assignment_null_mode(self):
        """Test device mode assignment parsing with null mode."""
        line = "display2 null"
        result = _parse_device_mode_assignment(line)

        assert result == ("display2", "null", None)

    def test_parse_device_mode_assignment_invalid_format(self):
        """Test device mode assignment parsing with invalid format."""
        line = "source1"  # Missing mode

        with pytest.raises(ValueError, match="Invalid assignment line format"):
            _parse_device_mode_assignment(line)

    def test_parse_scene_items_success(self, api_v6_7_responses):
        """Test successful scene items parsing."""
        response = api_v6_7_responses["video_wall_scenes"]
        result = _parse_scene_items(response, "scene list:")

        assert result == [("OfficeVW", "Splitmode"), ("OfficeVW", "Combined")]

    def test_parse_scene_items_empty_response(self, api_v6_7_responses):
        """Test scene items parsing with empty response."""
        response = api_v6_7_responses["empty_scene_list"]
        result = _parse_scene_items(response, "scene list:")

        assert result == []


# =============================================================================
# Test 13.1 Query Commands – System Configuration
# =============================================================================


class TestVersion:
    """Test the Version model parser."""

    def test_parse_success_with_core_version(self, api_v6_7_responses):
        """Test successful parsing with core version."""
        response = api_v6_7_responses["version"]
        version = Version.parse(response)

        assert version.api_version == "1.21"
        assert version.web_version == "8.3.1"
        assert version.core_version == "8.3.8"

    def test_parse_success_without_core_version(self, api_v6_7_responses):
        """Test successful parsing without core version."""
        response = api_v6_7_responses["version_no_core"]
        version = Version.parse(response)

        assert version.api_version == "1.21"
        assert version.web_version == "8.3.1"
        assert version.core_version == "8.3.1"  # Falls back to web version

    def test_parse_with_command_echo(self, api_v6_7_responses):
        """Test parsing with command echo and welcome message."""
        response = api_v6_7_responses["version_with_echo"]
        version = Version.parse(response)

        assert version.api_version == "1.21"
        assert version.web_version == "8.3.1"
        assert version.core_version == "8.3.8"

    def test_parse_missing_api_version(self, malformed_responses):
        """Test parsing with missing API version."""
        response = malformed_responses["version_missing_api"]

        with pytest.raises(ValueError, match="Could not find API version"):
            Version.parse(response)

    def test_parse_missing_system_version(self, malformed_responses):
        """Test parsing with missing system version."""
        response = malformed_responses["version_missing_system"]

        with pytest.raises(ValueError, match="Could not find System version"):
            Version.parse(response)

    def test_parse_empty_response(self, malformed_responses):
        """Test parsing with empty response."""
        response = malformed_responses["empty"]

        with pytest.raises(ValueError, match="Could not find API version"):
            Version.parse(response)


class TestIpSetting:
    """Test the IpSetting model parser."""

    def test_parse_ipsetting_success(self, api_v6_7_responses):
        """Test successful parsing of ipsetting response."""
        response = api_v6_7_responses["ipsetting"]
        ip_setting = IpSetting.parse(response)

        assert ip_setting.ip4addr == "169.254.1.1"
        assert ip_setting.netmask == "255.255.0.0"
        assert ip_setting.gateway == "169.254.1.254"

    def test_parse_ipsetting2_success(self, api_v6_7_responses):
        """Test successful parsing of ipsetting2 response."""
        response = api_v6_7_responses["ipsetting2"]
        ip_setting = IpSetting.parse(response)

        assert ip_setting.ip4addr == "192.168.11.243"
        assert ip_setting.netmask == "255.255.255.0"
        assert ip_setting.gateway == "192.168.11.1"

    def test_parse_invalid_format(self, malformed_responses):
        """Test parsing with invalid format."""
        response = malformed_responses["ipsetting_invalid_format"]

        with pytest.raises(ValueError, match="Invalid IP settings response"):
            IpSetting.parse(response)

    def test_parse_missing_required_fields(self, malformed_responses):
        """Test parsing with missing required fields."""
        response = malformed_responses["ipsetting_missing_fields"]

        with pytest.raises(ValueError, match="Missing required IP settings"):
            IpSetting.parse(response)


# =============================================================================
# Test 13.2 Query Commands – Device Configuration
# =============================================================================


class TestEndpointAliasHostname:
    """Test the EndpointAliasHostname model parser."""

    def test_parse_single_device(self, api_v6_7_responses):
        """Test parsing single device name."""
        response = api_v6_7_responses["device_name_single"]
        device_name = EndpointAliasHostname.parse_single(response)

        assert device_name.hostname == "NHD-400-RX"
        assert device_name.alias == "display1"

    def test_parse_multiple_devices(self, api_v6_7_responses):
        """Test parsing multiple device names."""
        response = api_v6_7_responses["device_aliases"]
        device_names = EndpointAliasHostname.parse_multiple(response)

        assert len(device_names) == 4

        # Check first device
        assert device_names[0].hostname == "NHD-400-TX-E4CE02104E55"
        assert device_names[0].alias == "source1"

        # Check second device
        assert device_names[1].hostname == "NHD-400-TX-E4CE02104E56"
        assert device_names[1].alias == "source2"

        # Check third device
        assert device_names[2].hostname == "NHD-400-RX-E4CE02104A57"
        assert device_names[2].alias == "display1"

        # Check fourth device
        assert device_names[3].hostname == "NHD-400-RX-E4CE02104A58"
        assert device_names[3].alias is None

    def test_parse_invalid_format(self, malformed_responses):
        """Test parsing with invalid format."""
        response = malformed_responses["endpoint_alias_hostname_invalid_format"]

        with pytest.raises(ValueError, match="Invalid name response"):
            EndpointAliasHostname.parse_single(response)

    def test_parse_device_with_quotes_error(self, malformed_responses):
        """Test parsing device name with quotes in error message."""
        response = malformed_responses["endpoint_alias_hostname_quoted_device"]

        with pytest.raises(DeviceNotFoundError) as exc_info:
            EndpointAliasHostname.parse_single(response)

        # Verify the quotes are stripped from the device name
        assert exc_info.value.device_name == "DISPLAY1"


class TestDeviceStatus:
    """Test the DeviceStatus model parser."""

    def test_parse_nhd_110_210_devices(self, api_v6_7_responses):
        """Test parsing NHD-110/210 series device status with mixed TX/RX types."""
        response = api_v6_7_responses["device_status_nhd_110_210"]
        devices = DeviceStatus.parse(response)

        assert len(devices) == 2

        # Check TX device (SOURCE1)
        tx_device = devices[0]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-140-TX-E4CE02102EE1"
        assert tx_device.audio_stream_ip_address == "224.48.46.225"
        assert tx_device.encoding_enable is True  # "true" -> bool
        assert tx_device.hdmi_in_active is True  # "true" -> bool
        assert tx_device.hdmi_in_frame_rate == 60  # "60" -> int
        assert tx_device.line_out_audio_enable is False  # "false" -> bool
        assert tx_device.resolution == "1920x1080"
        assert tx_device.stream_frame_rate == 60  # "60" -> int
        assert tx_device.stream_resolution == "1920x1080"
        assert tx_device.video_stream_ip_address == "224.16.46.225"
        # Check that RX-only fields are None for TX device
        assert tx_device.audio_bitrate is None
        assert tx_device.hdmi_out_active is None

        # Check RX device (DISPLAY1)
        rx_device = devices[1]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-210-RX-E4CE02107132"
        assert rx_device.audio_bitrate == 1536000  # "1536000" -> int
        assert rx_device.audio_input_format == "lpcm"
        assert rx_device.hdcp_status == "hdcp14"
        assert rx_device.hdmi_out_active is True  # "true" -> bool
        assert rx_device.hdmi_out_audio_enable is True  # "true" -> bool
        assert rx_device.hdmi_out_frame_rate == 60  # "60" -> int
        assert rx_device.hdmi_out_resolution == "1920x1080"
        assert rx_device.line_out_audio_enable is True  # "true" -> bool
        assert rx_device.stream_error_count == 0  # "0" -> int
        assert rx_device.stream_frame_rate == 60  # "60" -> int
        assert rx_device.stream_resolution == "1920x1080"
        # Check that TX-only fields are None for RX device
        assert rx_device.encoding_enable is None
        assert rx_device.hdmi_in_active is None

    def test_parse_nhd_400_devices(self, api_v6_7_responses):
        """Test parsing NHD-400 series device status with different field set."""
        response = api_v6_7_responses["device_status_nhd_400"]
        devices = DeviceStatus.parse(response)

        assert len(devices) == 2

        # Check RX device
        rx_device = devices[0]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-400-RX-E4CE02103CB3"
        assert rx_device.audio_bitrate == 3072000  # "3072000" -> int
        assert rx_device.audio_output_format == "lpcm"
        assert rx_device.hdcp == "hdcp22"
        assert rx_device.hdmi_out_active is True  # "true" -> bool
        assert rx_device.hdmi_out_frame_rate == 60  # "60" -> int
        assert rx_device.hdmi_out_resolution == "1920x1080"

        # Check TX device
        tx_device = devices[1]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-400-TX-E4CE0210B6D4"
        assert tx_device.audio_bitrate == 3072000  # "3072000" -> int
        assert tx_device.audio_input_format == "lpcm"
        assert tx_device.hdcp == "hdcp22"
        assert tx_device.hdmi_in_active is True  # "true" -> bool
        assert tx_device.hdmi_in_frame_rate == 60  # "60" -> int
        assert tx_device.resolution == "1920x1080"

    def test_parse_nhd_600_devices(self, api_v6_7_responses):
        """Test parsing NHD-600 series device status with minimal field set."""
        response = api_v6_7_responses["device_status_nhd_600"]
        devices = DeviceStatus.parse(response)

        assert len(devices) == 2

        # Check RX device
        rx_device = devices[0]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-600-RX-D88039E5E525"
        assert rx_device.hdcp == "hdcp14"
        assert rx_device.hdmi_out_active is True  # "true" -> bool
        assert rx_device.hdmi_out_frame_rate == 60  # "60" -> int
        assert rx_device.hdmi_out_resolution == "1920x1080"

        # Check TX device
        tx_device = devices[1]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-600-TX-D88039E5ED1E"
        assert tx_device.hdcp == "hdcp14"
        assert tx_device.hdmi_in_active is True  # "true" -> bool
        assert tx_device.hdmi_in_frame_rate == 60  # "60" -> int
        assert tx_device.resolution == "1920x1080"

    def test_parse_missing_header(self, malformed_responses):
        """Test parsing with missing 'devices status info:' header."""
        response = malformed_responses["device_status_missing_header"]

        with pytest.raises(ValueError, match="No JSON content found"):
            DeviceStatus.parse(response)

    def test_parse_no_json_content(self, malformed_responses):
        """Test parsing with no JSON content."""
        response = malformed_responses["device_status_no_json"]

        with pytest.raises(ValueError, match="No JSON content found"):
            DeviceStatus.parse(response)

    def test_parse_invalid_json(self, malformed_responses):
        """Test parsing with invalid JSON."""
        response = malformed_responses["device_status_invalid_json"]

        with pytest.raises(ValueError, match="Invalid JSON in response"):
            DeviceStatus.parse(response)

    def test_parse_missing_devices_key(self, malformed_responses):
        """Test parsing with missing 'devices status' key in JSON."""
        response = malformed_responses["device_status_missing_devices_key"]

        with pytest.raises(ValueError, match="No 'devices status' key found"):
            DeviceStatus.parse(response)

    def test_type_conversion_edge_cases(self):
        """Test type conversion with edge case boolean values."""
        response = """devices status info:
            {
                "devices status" : [
                    {
                        "aliasname" : "TEST1",
                        "name" : "TEST-DEVICE",
                        "hdmi in active" : "FALSE",
                        "encoding enable" : "TRUE",
                        "audio bitrate" : "0"
                    }
                ]
            }"""
        devices = DeviceStatus.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.hdmi_in_active is False  # "FALSE" -> False
        assert device.encoding_enable is True  # "TRUE" -> True
        assert device.audio_bitrate == 0  # "0" -> 0


class TestDeviceInfo:
    """Test the DeviceInfo model parser."""

    def test_parse_nhd_110_210_devices(self, api_v6_7_responses):
        """Test parsing NHD-110/210 series device info with audio array and TX/RX types."""
        response = api_v6_7_responses["device_info_nhd_110_210"]
        devices = DeviceInfo.parse(response)

        assert len(devices) == 2

        # Check RX device (DISPLAY1) with audio array
        rx_device = devices[0]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-220-RX-E4CE02107DF5"
        assert rx_device.edid is None  # "null" -> None
        assert rx_device.gateway == ""
        assert rx_device.hdcp is True  # JSON boolean -> bool
        assert rx_device.ip4addr == "169.254.7.192"
        assert rx_device.ip_mode == "autoip"
        assert rx_device.mac == "e4:ce:02:10:7d:f5"
        assert rx_device.netmask == "255.255.0.0"
        assert rx_device.sourcein == "NHD-140-TX-E4CE02102EE1;"
        assert rx_device.version == "v2.12.2"

        # Check audio array parsing
        assert rx_device.audio is not None
        assert len(rx_device.audio) == 1
        assert isinstance(rx_device.audio[0], DeviceInfoAudioOutput)
        assert rx_device.audio[0].mute is False  # JSON boolean -> bool
        assert rx_device.audio[0].name == "lineout1"

        # Check that TX-only fields are None for RX device
        assert rx_device.cbr_avg_bitrate is None
        assert rx_device.enc_fps is None

        # Check TX device (SOURCE1)
        tx_device = devices[1]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-140-TX-E4CE02102EE3"
        assert tx_device.cbr_avg_bitrate == 10000  # JSON number -> int
        assert tx_device.edid == "00FFFFFFFFFFFF001C4501000100000008120103807341780ACF74A3574CB023094"
        assert tx_device.enc_fps == 60  # JSON number -> int
        assert tx_device.enc_gop == 60  # JSON number -> int
        assert tx_device.enc_rc_mode == "vbr"
        assert tx_device.fixqp_iqp == 25  # JSON number -> int
        assert tx_device.fixqp_pqp == 25  # JSON number -> int
        assert tx_device.gateway == "169.254.0.254"
        assert tx_device.hdcp is True  # JSON boolean -> bool
        assert tx_device.ip4addr == "169.254.85.242"
        assert tx_device.ip_mode == "fixed"
        assert tx_device.profile == "hp"
        assert tx_device.sourcein == "unknown"
        assert tx_device.transport_type == "raw"
        assert tx_device.vbr_max_bitrate == 20000  # JSON number -> int
        assert tx_device.vbr_max_qp == 51  # JSON number -> int
        assert tx_device.vbr_min_qp == 0  # JSON number -> int
        assert tx_device.version == "v1.0.6"

        # Check that RX-only fields are None for TX device
        assert tx_device.audio is None
        assert tx_device.sinkpower is None

    def test_parse_nhd_400_devices(self, api_v6_7_responses):
        """Test parsing NHD-400 series device info with km_over_ip_enable."""
        response = api_v6_7_responses["device_info_nhd_400"]
        devices = DeviceInfo.parse(response)

        assert len(devices) == 2

        # Check RX device
        rx_device = devices[0]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-400-RX-E4CE02102EF0"
        assert rx_device.edid is None  # "null" -> None
        assert rx_device.gateway == ""
        assert rx_device.ip4addr == "169.254.6.107"
        assert rx_device.ip_mode == "dhcp"
        assert rx_device.km_over_ip_enable is True  # "true" -> bool
        assert rx_device.mac == "e4:ce:02:10:2e:f0"
        assert rx_device.netmask == "255.255.0.0"
        assert rx_device.version == "v0.10.1"
        assert rx_device.videodetection == "lost"

        # Check TX device
        tx_device = devices[1]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-400-TX-E4CE02106E9E"
        assert tx_device.audio_input_type == "auto"
        assert tx_device.edid is None  # "null" -> None
        assert tx_device.gateway == "169.254.0.254"
        assert tx_device.ip4addr == "169.254.5.209"
        assert tx_device.ip_mode == "autoip"
        assert tx_device.km_over_ip_enable is True  # "true" -> bool
        assert tx_device.mac == "e4:ce:02:10:6e:9e"
        assert tx_device.netmask == "255.255.0.0"
        assert tx_device.version == "v0.10.1"
        assert tx_device.videodetection == "lost"

    def test_parse_nhd_600_devices_with_sinkpower(self, api_v6_7_responses):
        """Test parsing NHD-600 series device info with complex nested sinkpower object."""
        response = api_v6_7_responses["device_info_nhd_600"]
        devices = DeviceInfo.parse(response)

        assert len(devices) == 2

        # Check RX device with sinkpower object
        rx_device = devices[0]
        assert rx_device.aliasname == "DISPLAY1"
        assert rx_device.name == "NHD-600-RX-D88039E5E525"
        assert rx_device.analog_audio_source == "analog"
        assert rx_device.edid == ""
        assert rx_device.gateway == "0.0.0.0"
        assert rx_device.hdmi_audio_source == "hdmi"
        assert rx_device.ip4addr == "169.254.38.229"
        assert rx_device.ip_mode == "dhcp"
        assert rx_device.serial_param == "57600-8n1"
        assert rx_device.temperature == 38  # JSON number -> int
        assert rx_device.version == "3.6.0.0"
        assert rx_device.video_mode == "fast_switch"
        assert rx_device.video_stretch_type == "none"
        assert rx_device.video_timing == "1080P@50"

        # Check sinkpower nested object parsing
        assert rx_device.sinkpower is not None
        assert isinstance(rx_device.sinkpower, DeviceInfoSinkPower)
        assert rx_device.sinkpower.mode == "CEC"

        # Check CEC commands
        assert rx_device.sinkpower.cec is not None
        assert isinstance(rx_device.sinkpower.cec, DeviceInfoSinkPowerCecCommands)
        assert rx_device.sinkpower.cec.onetouchplay == "4004"
        assert rx_device.sinkpower.cec.standby == "ff36"

        # Check RS232 commands
        assert rx_device.sinkpower.rs232 is not None
        assert isinstance(rx_device.sinkpower.rs232, DeviceInfoSinkPowerRs232Commands)
        assert rx_device.sinkpower.rs232.mode == "ascii"
        assert rx_device.sinkpower.rs232.onetouchplay == "!POWERON~"
        assert rx_device.sinkpower.rs232.param == "115200-8n1"
        assert rx_device.sinkpower.rs232.standby == "!POWROFF~"

        # Check TX device with many technical fields
        tx_device = devices[1]
        assert tx_device.aliasname == "SOURCE1"
        assert tx_device.name == "NHD-600-TX-D88039E5E401"
        assert tx_device.analog_audio_direction == "INPUT"
        assert tx_device.bandwidth_adjust_mode == 0  # JSON number -> int
        assert tx_device.bit_perpixel == 8  # JSON number -> int
        assert tx_device.color_space == "RGB"
        assert tx_device.edid == "00ffffffffffff004dd903f901010101011b0103806c3d780a0dc9a05747982712484c"
        assert tx_device.gateway == "0.0.0.0"
        assert tx_device.hdcp14_enable is True  # JSON boolean -> bool
        assert tx_device.hdcp22_enable is True  # JSON boolean -> bool
        assert tx_device.ip4addr == "169.254.2.228"
        assert tx_device.ip_mode == "dhcp"
        assert tx_device.serial_param == "57600-8n1"
        assert tx_device.stream0_enable is True  # JSON boolean -> bool
        assert tx_device.stream0fps_by2_enable is False  # JSON boolean -> bool
        assert tx_device.stream1_enable is True  # JSON boolean -> bool
        assert tx_device.stream1_scale == "960x544"
        assert tx_device.stream1fps_by2_enable is False  # JSON boolean -> bool
        assert tx_device.temperature == 42  # JSON number -> int
        assert tx_device.version == "3.6.0.0"
        assert tx_device.video_input is True  # JSON boolean -> bool
        assert tx_device.video_source == "hdmi"
        assert tx_device.video_timing == "1920x1080P@60"

    def test_parse_missing_header(self, malformed_responses):
        """Test parsing with missing 'devices json info:' header."""
        response = malformed_responses["device_info_missing_header"]

        with pytest.raises(ValueError, match="No JSON content found"):
            DeviceInfo.parse(response)

    def test_parse_no_json_content(self, malformed_responses):
        """Test parsing with no JSON content."""
        response = malformed_responses["device_info_no_json"]

        with pytest.raises(ValueError, match="No JSON content found"):
            DeviceInfo.parse(response)

    def test_parse_invalid_json(self, malformed_responses):
        """Test parsing with invalid JSON."""
        response = malformed_responses["device_info_invalid_json"]

        with pytest.raises(ValueError, match="Invalid JSON in response"):
            DeviceInfo.parse(response)

    def test_parse_missing_devices_key(self, malformed_responses):
        """Test parsing with missing 'devices' key in JSON."""
        response = malformed_responses["device_info_missing_devices_key"]

        with pytest.raises(ValueError, match="No 'devices' key found"):
            DeviceInfo.parse(response)

    def test_nested_object_edge_cases(self):
        """Test parsing with edge cases for nested objects."""
        response = """devices json info:
{
    "devices" : [
        {
            "aliasname" : "TEST1",
            "name" : "TEST-DEVICE",
            "audio" : [],
            "sinkpower" : {
                "mode" : "NONE"
            }
        }
    ]
}"""
        devices = DeviceInfo.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.audio == []  # Empty audio array
        assert device.sinkpower is not None
        assert device.sinkpower.mode == "NONE"
        assert device.sinkpower.cec is None
        assert device.sinkpower.rs232 is None

    def test_type_conversion_edge_cases(self):
        """Test type conversion with edge cases for boolean and int fields."""
        response = """devices json info:
{
    "devices" : [
        {
            "aliasname" : "TEST1",
            "name" : "TEST-DEVICE",
            "hdcp14_enable" : false,
            "stream0_enable" : true,
            "temperature" : 0,
            "gateway" : ""
        }
    ]
}"""
        devices = DeviceInfo.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.hdcp14_enable is False  # JSON false -> False
        assert device.stream0_enable is True  # JSON true -> True
        assert device.temperature == 0  # JSON 0 -> 0
        assert device.gateway == ""  # Empty string stays empty


class TestDeviceJsonString:
    """Test the DeviceJsonString model parser."""

    def test_parse_mixed_device_types(self, api_v6_7_responses):
        """Test parsing mixed TX/RX devices with different optional fields."""
        response = api_v6_7_responses["device_json_string_mixed"]
        devices = DeviceJsonString.parse(response)

        assert len(devices) == 3

        # Check first TX device (SOURCE1)
        tx_device1 = devices[0]
        assert tx_device1.aliasName == "SOURCE1"
        assert tx_device1.deviceType == "Transmitter"
        assert tx_device1.ip == "169.254.232.229"
        assert tx_device1.online is True  # JSON boolean -> bool
        assert tx_device1.sequence == 1  # JSON number -> int
        assert tx_device1.trueName == "NHD-140-TX-E4CE02102EE1"
        assert tx_device1.nameoverlay is None  # Not present for this device
        assert tx_device1.txName is None  # TX devices don't have txName

        # Check group array parsing
        assert len(tx_device1.group) == 1
        assert isinstance(tx_device1.group[0], DeviceJsonStringGroup)
        assert tx_device1.group[0].name == "ungrouped"
        assert tx_device1.group[0].sequence == 1  # JSON number -> int

        # Check RX device (DISPLAY1) with txName
        rx_device = devices[1]
        assert rx_device.aliasName == "DISPLAY1"
        assert rx_device.deviceType == "Receiver"
        assert rx_device.ip == "169.254.148.121"
        assert rx_device.online is True  # JSON boolean -> bool
        assert rx_device.sequence == 2  # JSON number -> int
        assert rx_device.trueName == "NHD-140-RX-E4CE02102EE2"
        assert rx_device.txName == "SOURCE1"  # RX-specific field
        assert rx_device.nameoverlay is None  # RX devices don't have nameoverlay

        # Check group with different name
        assert len(rx_device.group) == 1
        assert rx_device.group[0].name == "MainDisplays"
        assert rx_device.group[0].sequence == 2  # JSON number -> int

        # Check second TX device (SOURCE7) with nameoverlay
        tx_device2 = devices[2]
        assert tx_device2.aliasName == "SOURCE7"
        assert tx_device2.deviceType == "Transmitter"
        assert tx_device2.ip == "169.254.1.1"
        assert tx_device2.nameoverlay is True  # JSON boolean -> bool, 600 series specific
        assert tx_device2.online is True  # JSON boolean -> bool
        assert tx_device2.sequence == 7  # JSON number -> int
        assert tx_device2.trueName == "NHD-600-TX-D88039E5E401"
        assert tx_device2.txName is None  # TX devices don't have txName

    def test_parse_single_device(self, api_v6_7_responses):
        """Test parsing single device with offline status."""
        response = api_v6_7_responses["device_json_string_single"]
        devices = DeviceJsonString.parse(response)

        assert len(devices) == 1
        device = devices[0]

        assert device.aliasName == "TEST1"
        assert device.deviceType == "Transmitter"
        assert device.ip == "192.168.1.100"
        assert device.online is False  # JSON boolean -> bool
        assert device.sequence == 1  # JSON number -> int
        assert device.trueName == "TEST-DEVICE-001"
        assert device.nameoverlay is None
        assert device.txName is None

        # Check group parsing
        assert len(device.group) == 1
        assert device.group[0].name == "testgroup"
        assert device.group[0].sequence == 1  # JSON number -> int

    def test_parse_missing_header(self, malformed_responses):
        """Test parsing with missing 'device json string:' header."""
        response = malformed_responses["device_json_string_missing_header"]

        with pytest.raises(ValueError, match="No JSON array content found"):
            DeviceJsonString.parse(response)

    def test_parse_no_json_content(self, malformed_responses):
        """Test parsing with no JSON content."""
        response = malformed_responses["device_json_string_no_json"]

        with pytest.raises(ValueError, match="No JSON array content found"):
            DeviceJsonString.parse(response)

    def test_parse_invalid_json(self, malformed_responses):
        """Test parsing with invalid JSON."""
        response = malformed_responses["device_json_string_invalid_json"]

        with pytest.raises(ValueError, match="Invalid JSON in response"):
            DeviceJsonString.parse(response)

    def test_parse_not_json_array(self, malformed_responses):
        """Test parsing when JSON is not an array."""
        response = malformed_responses["device_json_string_not_array"]

        with pytest.raises(ValueError, match="No JSON array content found"):
            DeviceJsonString.parse(response)

    def test_empty_group_array_edge_case(self):
        """Test parsing with empty group array."""
        response = """device json string:
[
    {
        "aliasName" : "TEST1",
        "deviceType" : "Transmitter",
        "group" : [],
        "ip" : "192.168.1.100",
        "online" : true,
        "sequence" : 1,
        "trueName" : "TEST-DEVICE"
    }
]"""
        devices = DeviceJsonString.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.group == []  # Empty group array

    def test_type_conversion_edge_cases(self):
        """Test type conversion edge cases for boolean and int fields."""
        response = """device json string:
[
    {
        "aliasName" : "TEST1",
        "deviceType" : "Transmitter",
        "group" : [
            {
                "name" : "testgroup",
                "sequence" : 0
            }
        ],
        "ip" : "192.168.1.100",
        "online" : false,
        "sequence" : 0,
        "trueName" : "TEST-DEVICE",
        "nameoverlay" : true
    }
]"""
        devices = DeviceJsonString.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.online is False  # JSON false -> False
        assert device.sequence == 0  # JSON 0 -> 0
        assert device.nameoverlay is True  # JSON true -> True
        assert device.group[0].sequence == 0  # Group sequence 0 -> 0

    def test_parse_with_unknown_fields(self):
        """Test parsing with unknown fields not in the dataclass."""
        response = """device json string:
[
    {
        "aliasName" : "TEST1",
        "deviceType" : "Transmitter",
        "group" : [
            {
                "name" : "testgroup",
                "sequence" : 1
            }
        ],
        "ip" : "192.168.1.100",
        "online" : true,
        "sequence" : 1,
        "trueName" : "TEST-DEVICE",
        "unknownField" : "someValue"
    }
]"""
        # Unknown fields should be silently filtered out during parsing
        devices = DeviceJsonString.parse(response)

        assert len(devices) == 1
        device = devices[0]
        assert device.aliasName == "TEST1"
        assert device.deviceType == "Transmitter"
        assert device.ip == "192.168.1.100"
        assert device.online is True
        assert device.sequence == 1
        assert device.trueName == "TEST-DEVICE"
        # Unknown fields are silently ignored


# =============================================================================
# Test 13.3 Query Commands – Stream Matrix Switching
# =============================================================================


class TestBaseMatrix:
    """Test the BaseMatrix model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of matrix assignments."""
        response = api_v6_7_responses["matrix"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 4
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source1"
        assert matrix.assignments[1].rx == "Display2"
        assert matrix.assignments[2].tx == "Source2"
        assert matrix.assignments[2].rx == "Display3"
        assert matrix.assignments[3].tx is None
        assert matrix.assignments[3].rx == "Display4"

    def test_parse_invalid_assignment_line(self, malformed_responses):
        """Test parsing with invalid assignment line."""
        response = malformed_responses["matrix_malformed_assignment"]

        with pytest.raises(ValueError, match="Invalid matrix assignment line format"):
            BaseMatrix.parse(response)

    def test_parse_empty_response(self, api_v6_7_responses):
        """Test parsing with empty response."""
        response = api_v6_7_responses["empty_matrix"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 0

    def test_parse_single_matrix_assignment(self, api_v6_7_responses):
        """Test parsing with single matrix assignment."""
        response = api_v6_7_responses["single_matrix_assignment"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 1
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"


class TestMatrixAudio3:
    """Test the MatrixAudio3 model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of audio3 matrix."""
        response = api_v6_7_responses["matrix_audio3"]
        matrix = MatrixAudio3.parse(response)

        assert len(matrix.assignments) == 3
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[1].rx == "Display2"
        assert matrix.assignments[1].tx == "Source3"
        assert matrix.assignments[2].rx == "Display5"
        assert matrix.assignments[2].tx == "Source2"

    def test_parse_filtered_response(self, api_v6_7_responses):
        """Test parsing filtered audio3 matrix response."""
        response = api_v6_7_responses["matrix_audio3_filtered"]
        matrix = MatrixAudio3.parse(response)

        assert len(matrix.assignments) == 1
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[0].tx == "Source3"

    def test_parse_missing_tx(self):
        """Test parsing with missing TX (odd number of lines)."""
        response = "matrix audio3 information:\nDisplay1\nSource1\nDisplay2"  # Missing TX for Display2

        with pytest.raises(ValueError, match="missing TX for RX"):
            MatrixAudio3.parse(response)

    def test_parse_odd_matrix_audio3_response(self, malformed_responses):
        """Test parsing with odd number of lines in matrix audio3."""
        response = malformed_responses["matrix_audio3_odd_lines"]

        with pytest.raises(ValueError, match="Invalid matrix audio3 response format"):
            MatrixAudio3.parse(response)


class TestFilteredMatrixResponses:
    """Test matrix parsers with filtered responses (single items)."""

    def test_matrix_video_filtered(self, api_v6_7_responses):
        """Test parsing filtered video matrix response."""
        response = api_v6_7_responses["matrix_video_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_audio_filtered(self, api_v6_7_responses):
        """Test parsing filtered audio matrix response."""
        response = api_v6_7_responses["matrix_audio_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_audio2_filtered(self, api_v6_7_responses):
        """Test parsing filtered audio2 matrix response."""
        response = api_v6_7_responses["matrix_audio2_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_usb_filtered(self, api_v6_7_responses):
        """Test parsing filtered USB matrix response."""
        response = api_v6_7_responses["matrix_usb_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_infrared_filtered(self, api_v6_7_responses):
        """Test parsing filtered infrared matrix response."""
        response = api_v6_7_responses["matrix_infrared_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_serial_filtered(self, api_v6_7_responses):
        """Test parsing filtered serial matrix response."""
        response = api_v6_7_responses["matrix_serial_filtered"]
        matrix = BaseMatrix.parse(response)

        assert len(matrix.assignments) == 2
        assert matrix.assignments[0].tx == "Source1"
        assert matrix.assignments[0].rx == "Display1"
        assert matrix.assignments[1].tx == "Source2"
        assert matrix.assignments[1].rx == "Display3"

    def test_matrix_infrared2_filtered(self, api_v6_7_responses):
        """Test parsing filtered infrared2 matrix response."""
        response = api_v6_7_responses["matrix_infrared2_filtered"]
        matrix = MatrixInfrared2.parse(response)

        assert len(matrix.assignments) == 2
        # First assignment: display1 api
        assert matrix.assignments[0].device == "display1"
        assert matrix.assignments[0].mode == "api"
        assert matrix.assignments[0].target_device is None
        # Second assignment: source1 single display1
        assert matrix.assignments[1].device == "source1"
        assert matrix.assignments[1].mode == "single"
        assert matrix.assignments[1].target_device == "display1"

    def test_matrix_serial2_filtered(self, api_v6_7_responses):
        """Test parsing filtered serial2 matrix response."""
        response = api_v6_7_responses["matrix_serial2_filtered"]
        matrix = MatrixSerial2.parse(response)

        assert len(matrix.assignments) == 2
        # First assignment: display1 api
        assert matrix.assignments[0].device == "display1"
        assert matrix.assignments[0].mode == "api"
        assert matrix.assignments[0].target_device is None
        # Second assignment: source1 single display1
        assert matrix.assignments[1].device == "source1"
        assert matrix.assignments[1].mode == "single"
        assert matrix.assignments[1].target_device == "display1"


# =============================================================================
# Test 13.4 Query Commands – Video Walls
# =============================================================================


class TestVideoWallSceneList:
    """Test the VideoWallSceneList model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of video wall scene list."""
        response = api_v6_7_responses["video_wall_scenes"]
        scene_list = VideoWallSceneList.parse(response)

        assert len(scene_list.scenes) == 2
        assert scene_list.scenes[0].videowall == "OfficeVW"
        assert scene_list.scenes[0].scene == "Splitmode"
        assert scene_list.scenes[1].videowall == "OfficeVW"
        assert scene_list.scenes[1].scene == "Combined"

    def test_parse_single_scene(self, api_v6_7_responses):
        """Test parsing with single scene."""
        response = api_v6_7_responses["single_scene"]
        scene_list = VideoWallSceneList.parse(response)

        assert len(scene_list.scenes) == 1
        assert scene_list.scenes[0].videowall == "OfficeVW"
        assert scene_list.scenes[0].scene == "Single"

    def test_parse_empty_scene_list(self, api_v6_7_responses):
        """Test parsing with empty scene list."""
        response = api_v6_7_responses["empty_scene_list"]

        with pytest.raises(ValueError, match="No valid scenes found in response"):
            VideoWallSceneList.parse(response)

    def test_parse_with_command_echo(self):
        """Test parsing with command echo."""
        # Extract just the scene list part
        scene_response = "scene list:\nOfficeVW-Combined_TopTwo"
        scene_list = VideoWallSceneList.parse(scene_response)

        assert len(scene_list.scenes) == 1
        assert scene_list.scenes[0].videowall == "OfficeVW"
        assert scene_list.scenes[0].scene == "Combined_TopTwo"


# =============================================================================
# Test 13.5 Query Commands – Multiview
# =============================================================================


class TestPresetMultiviewLayoutList:
    """Test the PresetMultiviewLayoutList model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of preset multiview layout list."""
        response = api_v6_7_responses["mscene_list"]
        layout_list = PresetMultiviewLayoutList.parse(response)

        assert len(layout_list.multiview_layouts) == 3

        # Check first layout
        layout1 = layout_list.multiview_layouts[0]
        assert layout1.rx == "display5"
        assert layout1.layouts == ["gridlayout", "piplayout"]

        # Check second layout
        layout2 = layout_list.multiview_layouts[1]
        assert layout2.rx == "display6"
        assert layout2.layouts == ["pip2layout"]

        # Check third layout
        layout3 = layout_list.multiview_layouts[2]
        assert layout3.rx == "display7"
        assert layout3.layouts == ["grid5layout", "grid6layout"]

    def test_parse_malformed_line(self, malformed_responses):
        """Test parsing with malformed line."""
        response = malformed_responses["preset_multiview_malformed_line"]

        with pytest.raises(ValueError, match="Invalid preset multiview layout line format"):
            PresetMultiviewLayoutList.parse(response)

    def test_parse_empty_response(self, api_v6_7_responses):
        """Test parsing with empty response."""
        response = api_v6_7_responses["empty_scene_list"]
        layout_list = PresetMultiviewLayoutList.parse(response)

        assert len(layout_list.multiview_layouts) == 0

    def test_parse_malformed_layout_line_error(self, malformed_responses):
        """Test parsing with malformed layout line."""
        response = malformed_responses["preset_multiview_malformed_line"]

        with pytest.raises(ValueError, match="Invalid preset multiview layout line format"):
            PresetMultiviewLayoutList.parse(response)


class TestVideoWallLogicalScreenList:
    """Test the VideoWallLogicalScreenList model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of video wall logical screen list."""
        response = api_v6_7_responses["video_wall_logical"]
        screen_list = VideoWallLogicalScreenList.parse(response)

        assert len(screen_list.logical_screens) == 2

        # Check first screen
        screen1 = screen_list.logical_screens[0]
        assert screen1.videowall == "OfficeVW"
        assert screen1.scene == "Combined"
        assert screen1.logical_screen == "TopTwo"
        assert screen1.tx == "source1"
        assert len(screen1.rows) == 1
        assert screen1.rows[0] == ["display1", "display2"]

        # Check second screen
        screen2 = screen_list.logical_screens[1]
        assert screen2.videowall == "OfficeVW"
        assert screen2.scene == "AllCombined"
        assert screen2.logical_screen == "AllDisplays"
        assert screen2.tx == "source2"
        assert len(screen2.rows) == 2
        assert screen2.rows[0] == ["display1", "display2", "display3"]
        assert screen2.rows[1] == ["display4", "display5", "display6"]

    def test_parse_invalid_screen_header_format(self, malformed_responses):
        """Test parsing with invalid screen header format."""
        response = malformed_responses["video_wall_invalid_format"]

        with pytest.raises(ValueError, match="Invalid screen header format"):
            VideoWallLogicalScreenList.parse(response)

    def test_parse_missing_logical_screen_separator(self, malformed_responses):
        """Test parsing with missing logical screen separator."""
        response = malformed_responses["video_wall_missing_logical_screen_separator"]

        with pytest.raises(ValueError, match="missing logical screen separator"):
            VideoWallLogicalScreenList.parse(response)

    def test_parse_missing_videowall_separator(self, malformed_responses):
        """Test parsing with missing videowall separator."""
        response = malformed_responses["video_wall_missing_videowall_scene_separator"]

        with pytest.raises(ValueError, match="videowall-scene separator"):
            VideoWallLogicalScreenList.parse(response)

    def test_parse_with_command_echo(self, api_v6_7_responses):
        """Test parsing with command echo."""
        response = api_v6_7_responses["video_wall_with_echo"]
        screen_list = VideoWallLogicalScreenList.parse(response)

        assert len(screen_list.logical_screens) == 1
        assert screen_list.logical_screens[0].videowall == "OfficeVW"
        assert screen_list.logical_screens[0].scene == "Combined"
        assert screen_list.logical_screens[0].logical_screen == "TopTwo"


class TestVideowallWithinWallSceneList:
    """Test the VideowallWithinWallSceneList model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of wscene2 list."""
        response = api_v6_7_responses["wscene2_list"]
        scene_list = VideowallWithinWallSceneList.parse(response)

        assert len(scene_list.scenes) == 2
        assert scene_list.scenes[0].videowall == "OfficeVW"
        assert scene_list.scenes[0].scene == "windowscene1"
        assert scene_list.scenes[1].videowall == "OfficeVW"
        assert scene_list.scenes[1].scene == "windowscene2"


class TestFilteredSceneResponses:
    """Test scene parsers with filtered responses (single items)."""

    def test_mscene_filtered(self, api_v6_7_responses):
        """Test parsing filtered mscene response."""
        response = api_v6_7_responses["mscene_filtered"]
        scene_list = PresetMultiviewLayoutList.parse(response)

        assert len(scene_list.multiview_layouts) == 1
        assert scene_list.multiview_layouts[0].rx == "display6"
        assert scene_list.multiview_layouts[0].layouts == ["pip2layout"]

    def test_custom_multiview_filtered(self, api_v6_7_responses):
        """Test parsing filtered custom multiview response."""
        response = api_v6_7_responses["custom_multiview_filtered"]
        layout_list = CustomMultiviewLayoutList.parse(response)

        assert len(layout_list.configurations) == 1
        config = layout_list.configurations[0]
        assert config.rx == "display11"
        assert config.mode == "overlay"
        assert len(config.tiles) == 1
        assert config.tiles[0].tx == "source1"
        assert config.tiles[0].x == 0
        assert config.tiles[0].y == 0
        assert config.tiles[0].width == 1920
        assert config.tiles[0].height == 1080


class TestMultiviewTile:
    """Test the MultiviewTile model parser."""

    def test_parse_tile_config_success(self, api_v6_7_responses):
        """Test successful parsing of tile configuration."""
        tile_config = api_v6_7_responses["multiview_tile"]
        tile = MultiviewTile.parse_tile_config(tile_config)

        assert tile.tx == "source1"
        assert tile.x == 0
        assert tile.y == 0
        assert tile.width == 960
        assert tile.height == 540
        assert tile.scaling == "fit"

    def test_parse_tile_config_stretch(self, api_v6_7_responses):
        """Test parsing with stretch scaling."""
        tile_config = api_v6_7_responses["multiview_tile_stretch"]
        tile = MultiviewTile.parse_tile_config(tile_config)

        assert tile.scaling == "stretch"
        assert tile.x == 100
        assert tile.y == 50
        assert tile.width == 800
        assert tile.height == 600

    def test_parse_tile_config_missing_colon(self, malformed_responses):
        """Test parsing with missing colon."""
        invalid_config = malformed_responses["multiview_tile_config_missing_colon"]

        with pytest.raises(ValueError, match="Invalid tile configuration"):
            MultiviewTile.parse_tile_config(invalid_config)

    def test_parse_tile_config_invalid_coordinates(self, malformed_responses):
        """Test parsing with invalid coordinates."""
        tile_config = malformed_responses["multiview_tile_config_missing_height"]

        with pytest.raises(ValueError, match="Invalid tile coordinates"):
            MultiviewTile.parse_tile_config(tile_config)


class TestCustomMultiviewLayoutList:
    """Test the CustomMultiviewLayoutList model parser."""

    def test_parse_success(self, api_v6_7_responses):
        """Test successful parsing of custom multiview layout."""
        response = api_v6_7_responses["custom_multiview"]

        layout_list = CustomMultiviewLayoutList.parse(response)

        assert len(layout_list.configurations) == 2

        # Check first configuration
        config1 = layout_list.configurations[0]
        assert config1.rx == "display10"
        assert config1.mode == "tile"
        assert len(config1.tiles) == 4

        # Check second configuration
        config2 = layout_list.configurations[1]
        assert config2.rx == "display11"
        assert config2.mode == "overlay"
        assert len(config2.tiles) == 2

    def test_parse_invalid_mode(self, malformed_responses):
        """Test parsing with invalid mode."""
        response = malformed_responses["multiview_invalid_mode"]

        with pytest.raises(ValueError, match="Invalid multiview mode"):
            CustomMultiviewLayoutList.parse(response)

    def test_parse_malformed_line(self, malformed_responses):
        """Test parsing with malformed line."""
        response = malformed_responses["multiview_missing_tiles"]

        with pytest.raises(ValueError, match="Invalid multiview layout line format"):
            CustomMultiviewLayoutList.parse(response)

    def test_parse_invalid_tile_config(self, malformed_responses):
        """Test parsing with invalid tile configuration."""
        response = malformed_responses["multiview_no_valid_tiles"]

        with pytest.raises(ValueError, match="Invalid tile configuration"):
            CustomMultiviewLayoutList.parse(response)

    def test_parse_no_valid_tiles(self, malformed_responses):
        """Test parsing with no valid tiles."""
        response = malformed_responses["multiview_missing_tiles"]

        with pytest.raises(ValueError, match="Invalid multiview layout line format"):
            CustomMultiviewLayoutList.parse(response)

    def test_parse_single_tile(self, api_v6_7_responses):
        """Test parsing with single tile."""
        response = api_v6_7_responses["single_tile"]
        layout_list = CustomMultiviewLayoutList.parse(response)

        assert len(layout_list.configurations) == 1
        config = layout_list.configurations[0]
        assert config.rx == "display10"
        assert config.mode == "tile"
        assert len(config.tiles) == 1

    def test_parse_invalid_tile_configuration_error(self, malformed_responses):
        """Test parsing with invalid tile configuration."""
        response = malformed_responses["multiview_malformed_tile_line"]

        with pytest.raises(ValueError, match="Invalid tile configuration"):
            CustomMultiviewLayoutList.parse(response)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
