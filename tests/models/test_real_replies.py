"""Parsers against replies captured from a real controller (firmware v9.4.7, API v1.28, NHD-400 TX/RX).

The replies are verbatim apart from anonymisation: IP addresses are from 192.0.2.0/24, MAC-derived hostname suffixes
are made up, aliases and group names are generic, and EDIDs are shortened.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from wyrestorm_networkhd.commands.api_query import APIQueryCommands
from wyrestorm_networkhd.models.api_query import (
    DeviceInfo,
    DeviceJsonString,
    DeviceStatus,
    EndpointAliasHostname,
    IpSetting,
    Matrix,
    Version,
)

REAL_REPLIES = {
    "config get version": "config get version\nAPI version: v1.28\nSystem version: v9.4.7(v9.4.13)",
    "config get ipsetting": "config get ipsetting\nipsetting is:ip4addr 192.0.2.10 netmask 255.255.255.0 gateway 0.0.0.0",
    "config get ipsetting2": "config get ipsetting2\nipsetting2 is:ip4addr 192.0.2.11 netmask 255.255.255.0 gateway 192.0.2.12",
    "config get devicelist": "config get devicelist\ndevicelist is Display1 Display2 Source1 Source2",
    "config get devicejsonstring": 'config get devicejsonstring\ndevice json string:[\n{\n"aliasName" : "Display1",\n"deviceType" : "Receiver",\n"group" : [\n{\n"name" : "Group1",\n"sequence" : 2\n}\n],\n"ip" : "192.0.2.13",\n"online" : true,\n"sequence" : 2,\n"service" : [\n{\n"name" : "telnet",\n"status" : true\n},\n{\n"name" : "ssh",\n"status" : true\n},\n{\n"name" : "http",\n"status" : true\n},\n{\n"name" : "https",\n"status" : false\n}\n],\n"trueName" : "NHD-400-RX-000000000001",\n"txName" : "NHD-400-TX-000000000002"\n},\n{\n"aliasName" : "Display2",\n"deviceType" : "Receiver",\n"group" : [\n{\n"name" : "Group1",\n"sequence" : 2\n}\n],\n"ip" : "192.0.2.14",\n"online" : true,\n"sequence" : 1,\n"service" : [\n{\n"name" : "telnet",\n"status" : true\n},\n{\n"name" : "ssh",\n"status" : true\n},\n{\n"name" : "http",\n"status" : true\n},\n{\n"name" : "https",\n"status" : false\n}\n],\n"trueName" : "NHD-400-RX-000000000003",\n"txName" : "NHD-400-TX-000000000002"\n},\n{\n"aliasName" : "Source1",\n"deviceType" : "Transmitter",\n"group" : [\n{\n"name" : "ungrouped",\n"sequence" : 1\n}\n],\n"ip" : "192.0.2.15",\n"online" : true,\n"sequence" : 1,\n"service" : [\n{\n"name" : "telnet",\n"status" : true\n},\n{\n"name" : "ssh",\n"status" : true\n},\n{\n"name" : "http",\n"status" : true\n},\n{\n"name" : "https",\n"status" : false\n}\n],\n"trueName" : "NHD-400-TX-000000000004"\n},\n{\n"aliasName" : "Source2",\n"deviceType" : "Transmitter",\n"group" : [\n{\n"name" : "ungrouped",\n"sequence" : 1\n}\n],\n"ip" : "192.0.2.16",\n"online" : true,\n"sequence" : 2,\n"service" : [\n{\n"name" : "telnet",\n"status" : true\n},\n{\n"name" : "ssh",\n"status" : true\n},\n{\n"name" : "http",\n"status" : true\n},\n{\n"name" : "https",\n"status" : false\n}\n],\n"trueName" : "NHD-400-TX-000000000002"\n}\n]',
    "config get device status": 'config get device status\ndevices status info:\n{\n"devices status" : [\n{\n"aliasname" : "Source2",\n"audio bitrate" : "0",\n"audio input format" : "none",\n"hdcp" : "none",\n"hdmi in active" : "false",\n"hdmi in frame rate" : "0",\n"name" : "NHD-400-TX-000000000002",\n"resolution" : "0x0"\n},\n{\n"aliasname" : "Display1",\n"audio bitrate" : "0",\n"audio output format" : "lpcm",\n"hdcp" : "hdcp14",\n"hdmi out active" : "true",\n"hdmi out frame rate" : "0",\n"hdmi out resolution" : "0x0",\n"name" : "NHD-400-RX-000000000001"\n},\n{\n"aliasname" : "Display2",\n"audio bitrate" : "0",\n"audio output format" : "lpcm",\n"hdcp" : "hdcp14",\n"hdmi out active" : "true",\n"hdmi out frame rate" : "0",\n"hdmi out resolution" : "0x0",\n"name" : "NHD-400-RX-000000000003"\n},\n{\n"aliasname" : "Source1",\n"audio bitrate" : "3072000",\n"audio input format" : "lpcm",\n"hdcp" : "hdcp14",\n"hdmi in active" : "true",\n"hdmi in frame rate" : "60",\n"name" : "NHD-400-TX-000000000004",\n"resolution" : "1920x1080"\n}\n]\n}',
    "config get device info": 'config get device info\ndevices json info:\n{\n"devices" : [\n{\n"aliasname" : "Display1",\n"edid" : "00ffffffffffff00",\n"gateway" : "192.0.2.17",\n"ip4addr" : "192.0.2.13",\n"ip_mode" : "dhcp",\n"km_over_ip_enable" : "true",\n"mac" : "00:00:00:00:00:01",\n"name" : "NHD-400-RX-000000000001",\n"netmask" : "255.255.255.0",\n"version" : "v2.5.6",\n"videodetection" : "lost"\n},\n{\n"aliasname" : "Display2",\n"edid" : "00ffffffffffff00",\n"gateway" : "192.0.2.17",\n"ip4addr" : "192.0.2.14",\n"ip_mode" : "dhcp",\n"km_over_ip_enable" : "true",\n"mac" : "00:00:00:00:00:03",\n"name" : "NHD-400-RX-000000000003",\n"netmask" : "255.255.255.0",\n"version" : "v2.5.6",\n"videodetection" : "lost"\n},\n{\n"aliasname" : "Source2",\n"audio_input_type" : "auto",\n"edid" : "00ffffffffffff00",\n"gateway" : "192.0.2.17",\n"ip4addr" : "192.0.2.16",\n"ip_mode" : "dhcp",\n"km_over_ip_enable" : "true",\n"mac" : "00:00:00:00:00:02",\n"name" : "NHD-400-TX-000000000002",\n"netmask" : "255.255.255.0",\n"version" : "v2.5.6",\n"videodetection" : "lost"\n},\n{\n"aliasname" : "Source1",\n"audio_input_type" : "auto",\n"edid" : "00ffffffffffff00",\n"gateway" : "192.0.2.17",\n"ip4addr" : "192.0.2.15",\n"ip_mode" : "dhcp",\n"km_over_ip_enable" : "true",\n"mac" : "00:00:00:00:00:04",\n"name" : "NHD-400-TX-000000000004",\n"netmask" : "255.255.255.0",\n"version" : "v2.5.6",\n"videodetection" : "lost"\n}\n]\n}',
    "matrix get": "matrix get\nmatrix information:\nSource2 Display1\nSource2 Display2",
    "config get name": "config get name\nNHD-400-RX-000000000001's alias is Display1\nNHD-400-RX-000000000003's alias is Display2\nNHD-400-TX-000000000004's alias is Source1\nNHD-400-TX-000000000002's alias is Source2",
}


class TestRealControllerReplies:
    """Each query reply from the real controller parses into the expected values."""

    def test_version(self):
        # Act
        result = Version.parse(REAL_REPLIES["config get version"])

        # Assert
        assert (result.api_version, result.web_version, result.core_version) == ("1.28", "9.4.7", "9.4.13")

    @pytest.mark.parametrize(
        "command, expected",
        [
            ("config get ipsetting", ("192.0.2.10", "255.255.255.0", "0.0.0.0")),
            ("config get ipsetting2", ("192.0.2.11", "255.255.255.0", "192.0.2.12")),
        ],
    )
    def test_ipsetting(self, command, expected):
        # Act
        result = IpSetting.parse(REAL_REPLIES[command])

        # Assert
        assert (result.ip4addr, result.netmask, result.gateway) == expected

    @pytest.mark.asyncio
    async def test_devicelist(self):
        # Arrange
        client = Mock()
        client.send_command = AsyncMock(return_value=REAL_REPLIES["config get devicelist"])

        # Act
        result = await APIQueryCommands(client).config_get_devicelist()

        # Assert
        assert result == ["Display1", "Display2", "Source1", "Source2"]

    def test_devicejsonstring_ignores_service_list(self):
        # Act
        result = DeviceJsonString.parse(REAL_REPLIES["config get devicejsonstring"])

        # Assert
        assert [d.aliasName for d in result] == ["Display1", "Display2", "Source1", "Source2"]
        rx = result[0]
        assert rx.deviceType == "Receiver"
        assert rx.online is True
        assert rx.sequence == 2
        assert rx.group[0].name == "Group1"
        assert rx.txName == "NHD-400-TX-000000000002"
        assert result[2].txName is None

    def test_device_status_idle_and_active_values(self):
        # Act
        idle_tx, rx, _, active_tx = DeviceStatus.parse(REAL_REPLIES["config get device status"])

        # Assert
        assert idle_tx.hdmi_in_active is False
        assert idle_tx.hdmi_in_frame_rate == 0
        assert idle_tx.resolution == "0x0"
        assert idle_tx.hdcp == "none"
        assert idle_tx.audio_input_format == "none"
        assert idle_tx.audio_bitrate == 0
        assert rx.hdmi_out_active is True
        assert rx.hdmi_out_frame_rate == 0
        assert rx.hdmi_out_resolution == "0x0"
        assert rx.audio_output_format == "lpcm"
        assert rx.hdcp == "hdcp14"
        assert active_tx.hdmi_in_active is True
        assert active_tx.hdmi_in_frame_rate == 60
        assert active_tx.audio_bitrate == 3072000

    def test_device_info(self):
        # Act
        result = DeviceInfo.parse(REAL_REPLIES["config get device info"])

        # Assert
        assert len(result) == 4
        rx, tx = result[0], result[2]
        assert rx.km_over_ip_enable is True
        assert rx.videodetection == "lost"
        assert rx.ip_mode == "dhcp"
        assert rx.mac == "00:00:00:00:00:01"
        assert tx.audio_input_type == "auto"
        assert tx.version == "v2.5.6"

    def test_matrix(self):
        # Act
        result = Matrix.parse(REAL_REPLIES["matrix get"])

        # Assert
        assert [(a.tx, a.rx) for a in result.assignments] == [("Source2", "Display1"), ("Source2", "Display2")]

    def test_name(self):
        # Act
        result = EndpointAliasHostname.parse_multiple(REAL_REPLIES["config get name"])

        # Assert
        assert [(e.alias, e.hostname) for e in result][0] == ("Display1", "NHD-400-RX-000000000001")
        assert len(result) == 4
