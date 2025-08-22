"""Comprehensive unit tests for API query models.

This test suite covers:
- Success cases with various response formats
- Failure cases with malformed data
- Edge cases with empty/invalid parameters
- Exception scenarios that should raise errors
- All parsing utilities and model classes
"""

import pytest

from wyrestorm_networkhd.models.api_query import (
    BaseMatrix,
    CustomMultiviewLayoutList,
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
        "devices_status": 'devices status info: {"devices": [{"name": "source1", "type": "tx", "status": "online"}]}',
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
