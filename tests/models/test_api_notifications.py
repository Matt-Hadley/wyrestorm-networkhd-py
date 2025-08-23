import pytest

from wyrestorm_networkhd.models.api_notifications import (
    NotificationCecinfo,
    NotificationEndpoint,
    NotificationIrinfo,
    NotificationParser,
    NotificationSerialinfo,
    NotificationSink,
    NotificationVideo,
)


class TestNotificationEndpoint:
    """Unit tests for NotificationEndpoint."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint online status notification
    # =============================================================================

    def test_parse_online_status_success(self):
        """Test parsing online status notification."""
        # Arrange
        notification = "notify endpoint + source1"

        # Act
        result = NotificationEndpoint.parse(notification)

        # Assert
        assert result.online is True
        assert result.device == "source1"

    def test_parse_offline_status_success(self):
        """Test parsing offline status notification."""
        # Arrange
        notification = "notify endpoint - display1"

        # Act
        result = NotificationEndpoint.parse(notification)

        # Assert
        assert result.online is False
        assert result.device == "display1"

    def test_parse_offline_status_success_em_dash(self):
        """Test parsing offline status notification with em dash."""
        notification = "notify endpoint – display1"
        result = NotificationEndpoint.parse(notification)

        assert result.online is False
        assert result.device == "display1"

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        notification = "  notify endpoint + source1  "
        result = NotificationEndpoint.parse(notification)

        assert result.online is True
        assert result.device == "source1"

    def test_parse_invalid_parts_count_too_few(self):
        """Test parsing with too few parts."""
        notification = "notify endpoint +"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            NotificationEndpoint.parse(notification)

    def test_parse_invalid_parts_count_too_many(self):
        """Test parsing with too many parts."""
        notification = "notify endpoint + display1 extra"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            NotificationEndpoint.parse(notification)

    def test_parse_invalid_first_part(self):
        """Test parsing with invalid first part."""
        notification = "invalid endpoint + display1"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            NotificationEndpoint.parse(notification)

    def test_parse_invalid_second_part(self):
        """Test parsing with invalid second part."""
        notification = "notify invalid + display1"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            NotificationEndpoint.parse(notification)

    def test_parse_invalid_status_indicator(self):
        """Test parsing with invalid status indicator."""
        notification = "notify endpoint = display1"
        with pytest.raises(ValueError, match="Invalid endpoint status indicator"):
            NotificationEndpoint.parse(notification)

    def test_parse_empty_device_name(self):
        """Test parsing with empty device name."""
        notification = "notify endpoint + "
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            NotificationEndpoint.parse(notification)


class TestNotificationCecinfo:
    """Unit tests for NotificationCecinfo."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint CEC data notification
    # =============================================================================

    def test_parse_cec_data_success(self):
        """Test parsing CEC data notification."""
        notification = 'notify cecinfo display1 "FF36"'
        result = NotificationCecinfo.parse(notification)

        assert result.device == "display1"
        assert result.cec_data == "FF36"

    def test_parse_cec_data_with_spaces_in_device(self):
        """Test parsing with spaces in device name."""
        notification = 'notify cecinfo display 1 "FF36"'
        result = NotificationCecinfo.parse(notification)

        assert result.device == "display 1"
        assert result.cec_data == "FF36"

    def test_parse_cec_data_empty_data(self):
        """Test parsing with empty CEC data."""
        notification = 'notify cecinfo display1 ""'
        result = NotificationCecinfo.parse(notification)

        assert result.device == "display1"
        assert result.cec_data == ""

    def test_parse_cec_data_complex_data(self):
        """Test parsing with complex CEC data."""
        notification = 'notify cecinfo source1 "FF36 1234 ABCD"'
        result = NotificationCecinfo.parse(notification)

        assert result.device == "source1"
        assert result.cec_data == "FF36 1234 ABCD"

    def test_parse_missing_prefix(self):
        """Test parsing with missing prefix."""
        notification = 'invalid cecinfo display1 "FF36"'
        with pytest.raises(ValueError, match="Invalid CEC data notification format"):
            NotificationCecinfo.parse(notification)

    def test_parse_no_quotes(self):
        """Test parsing without quotes."""
        notification = "notify cecinfo display1 FF36"
        with pytest.raises(ValueError, match="Invalid CEC data notification format"):
            NotificationCecinfo.parse(notification)

    def test_parse_no_opening_quote(self):
        """Test parsing without opening quote."""
        notification = 'notify cecinfo display1 FF36"'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            NotificationCecinfo.parse(notification)

    def test_parse_no_closing_quote(self):
        """Test parsing without closing quote."""
        notification = 'notify cecinfo display1 "FF36'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            NotificationCecinfo.parse(notification)

    def test_parse_only_one_quote(self):
        """Test parsing with only one quote."""
        notification = 'notify cecinfo display1 "FF36 incomplete'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            NotificationCecinfo.parse(notification)

    def test_parse_quotes_edge_case(self):
        """Test parsing with quotes edge case - this should parse successfully."""
        notification = 'notify cecinfo display1 FF36" "data'
        result = NotificationCecinfo.parse(notification)

        # This extracts content between first and last quote: FF36" "
        # Device is everything before first quote: display1 FF36
        # CEC data is between quotes: " " (the space and quote)
        assert result.device == "display1 FF36"
        assert result.cec_data == " "


class TestNotificationIrinfo:
    """Unit tests for NotificationIrinfo."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint Infrared data notification
    # =============================================================================

    def test_parse_ir_data_success(self):
        """Test parsing infrared data notification."""
        notification = 'notify irinfo display1 "0000 0067 0000 0015"'
        result = NotificationIrinfo.parse(notification)

        assert result.device == "display1"
        assert result.ir_data == "0000 0067 0000 0015"

    def test_parse_ir_data_with_spaces_in_device(self):
        """Test parsing with spaces in device name."""
        notification = 'notify irinfo display 1 "0000 0067"'
        result = NotificationIrinfo.parse(notification)

        assert result.device == "display 1"
        assert result.ir_data == "0000 0067"

    def test_parse_ir_data_empty_data(self):
        """Test parsing with empty IR data."""
        notification = 'notify irinfo display1 ""'
        result = NotificationIrinfo.parse(notification)

        assert result.device == "display1"
        assert result.ir_data == ""

    def test_parse_ir_data_complex_data(self):
        """Test parsing with complex IR data."""
        notification = 'notify irinfo source1 "0000 0067 0000 0015 0060 0018 0018 0018"'
        result = NotificationIrinfo.parse(notification)

        assert result.device == "source1"
        assert result.ir_data == "0000 0067 0000 0015 0060 0018 0018 0018"

    def test_parse_missing_prefix(self):
        """Test parsing with missing prefix."""
        notification = 'invalid irinfo display1 "0000"'
        with pytest.raises(ValueError, match="Invalid infrared data notification format"):
            NotificationIrinfo.parse(notification)

    def test_parse_no_quotes(self):
        """Test parsing without quotes."""
        notification = "notify irinfo display1 0000"
        with pytest.raises(ValueError, match="Invalid infrared data notification format"):
            NotificationIrinfo.parse(notification)

    def test_parse_no_opening_quote(self):
        """Test parsing without opening quote."""
        notification = 'notify irinfo display1 0000"'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            NotificationIrinfo.parse(notification)

    def test_parse_no_closing_quote(self):
        """Test parsing without closing quote."""
        notification = 'notify irinfo display1 "0000'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            NotificationIrinfo.parse(notification)

    def test_parse_only_one_quote(self):
        """Test parsing with only one quote."""
        notification = 'notify irinfo display1 "0000 incomplete'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            NotificationIrinfo.parse(notification)


class TestNotificationSerialinfo:
    """Unit tests for NotificationSerialinfo."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint RS-232 data notification
    # =============================================================================

    def test_parse_rs232_hex_success(self):
        """Test parsing RS-232 hex data notification."""
        notification = "notify serialinfo display1 hex 371:\r\n48656c6c6f"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 371
        assert result.serial_data == "48656c6c6f"

    def test_parse_rs232_ascii_success(self):
        """Test parsing RS-232 ASCII data notification."""
        notification = "notify serialinfo source1 ascii 122:\r\nHello World"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "source1"
        assert result.data_format == "ascii"
        assert result.data_length == 122
        assert result.serial_data == "Hello World"

    def test_parse_rs232_no_crlf(self):
        """Test parsing without CR/LF before data."""
        notification = "notify serialinfo display1 hex 10:48656c6c6f"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 10
        assert result.serial_data == "48656c6c6f"

    def test_parse_rs232_only_cr(self):
        """Test parsing with only CR before data."""
        notification = "notify serialinfo display1 ascii 5:\rHello"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 5
        assert result.serial_data == "Hello"

    def test_parse_rs232_only_lf(self):
        """Test parsing with only LF before data."""
        notification = "notify serialinfo display1 ascii 5:\nHello"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 5
        assert result.serial_data == "Hello"

    def test_parse_rs232_empty_data(self):
        """Test parsing with empty data."""
        notification = "notify serialinfo display1 hex 0:"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 0
        assert result.serial_data == ""

    def test_parse_invalid_prefix(self):
        """Test parsing with invalid prefix."""
        notification = "invalid serialinfo display1 hex 10:data"
        with pytest.raises(ValueError, match="Invalid serial data notification format"):
            NotificationSerialinfo.parse(notification)

    def test_parse_no_colon(self):
        """Test parsing without colon separator."""
        notification = "notify serialinfo display1 hex 10 data"
        with pytest.raises(ValueError, match="Invalid serial data notification format \\(no colon\\)"):
            NotificationSerialinfo.parse(notification)

    def test_parse_invalid_header_too_few_parts(self):
        """Test parsing with too few header parts."""
        notification = "notify serialinfo display1 hex:data"
        with pytest.raises(ValueError, match="Invalid serial data notification header"):
            NotificationSerialinfo.parse(notification)

    def test_parse_invalid_header_too_many_parts(self):
        """Test parsing with too many header parts."""
        notification = "notify serialinfo display1 hex 10 extra:data"
        with pytest.raises(ValueError, match="Invalid serial data notification header"):
            NotificationSerialinfo.parse(notification)

    def test_parse_invalid_data_format(self):
        """Test parsing with invalid data format."""
        notification = "notify serialinfo display1 invalid 10:data"
        with pytest.raises(ValueError, match="Invalid serial data format: invalid"):
            NotificationSerialinfo.parse(notification)

    def test_parse_invalid_data_length_not_integer(self):
        """Test parsing with non-integer data length."""
        notification = "notify serialinfo display1 hex abc:data"
        with pytest.raises(ValueError):
            NotificationSerialinfo.parse(notification)

    def test_parse_data_with_colon(self):
        """Test parsing with colon in data part."""
        notification = "notify serialinfo display1 ascii 10:\r\nhello:world"
        result = NotificationSerialinfo.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 10
        assert result.serial_data == "hello:world"


class TestNotificationVideo:
    """Unit tests for NotificationVideo."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint video input status notification
    # =============================================================================

    def test_parse_video_found_with_source(self):
        """Test parsing video found notification with source device."""
        notification = "notify video found display1 source1"
        result = NotificationVideo.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device == "source1"

    def test_parse_video_lost_without_source(self):
        """Test parsing video lost notification without source device."""
        notification = "notify video lost source1"
        result = NotificationVideo.parse(notification)

        assert result.status == "lost"
        assert result.device == "source1"
        assert result.source_device is None

    def test_parse_video_found_without_source(self):
        """Test parsing video found notification without source device."""
        notification = "notify video found display1"
        result = NotificationVideo.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device is None

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        notification = "  notify video lost source1  "
        result = NotificationVideo.parse(notification)

        assert result.status == "lost"
        assert result.device == "source1"
        assert result.source_device is None

    def test_parse_invalid_too_few_parts(self):
        """Test parsing with too few parts."""
        notification = "notify video"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            NotificationVideo.parse(notification)

    def test_parse_invalid_first_part(self):
        """Test parsing with invalid first part."""
        notification = "invalid video found display1"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            NotificationVideo.parse(notification)

    def test_parse_invalid_second_part(self):
        """Test parsing with invalid second part."""
        notification = "notify invalid found display1"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            NotificationVideo.parse(notification)

    def test_parse_invalid_status(self):
        """Test parsing with invalid video status."""
        notification = "notify video invalid display1"
        with pytest.raises(ValueError, match="Invalid video status: invalid"):
            NotificationVideo.parse(notification)

    def test_parse_exact_minimum_parts(self):
        """Test parsing with exactly minimum required parts."""
        notification = "notify video found display1"
        result = NotificationVideo.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device is None


class TestNotificationSink:
    """Unit tests for NotificationSink."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint sink power status notification
    # =============================================================================

    def test_parse_sink_power_lost_success(self):
        """Test parsing sink power lost notification."""
        notification = "notify sink lost display1"
        result = NotificationSink.parse(notification)

        assert result.status == "lost"
        assert result.device == "display1"

    def test_parse_sink_power_found_success(self):
        """Test parsing sink power found notification."""
        notification = "notify sink found display1"
        result = NotificationSink.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        notification = "  notify sink lost display1  "
        result = NotificationSink.parse(notification)

        assert result.status == "lost"
        assert result.device == "display1"

    def test_parse_invalid_parts_count_too_few(self):
        """Test parsing with too few parts."""
        notification = "notify sink lost"
        with pytest.raises(ValueError, match="Invalid sink power status notification format"):
            NotificationSink.parse(notification)

    def test_parse_invalid_parts_count_too_many(self):
        """Test parsing with too many parts."""
        notification = "notify sink lost display1 extra"
        with pytest.raises(ValueError, match="Invalid sink power status notification format"):
            NotificationSink.parse(notification)

    def test_parse_invalid_first_part(self):
        """Test parsing with invalid first part."""
        notification = "invalid sink lost display1"
        with pytest.raises(ValueError, match="Invalid sink power status notification format"):
            NotificationSink.parse(notification)

    def test_parse_invalid_second_part(self):
        """Test parsing with invalid second part."""
        notification = "notify invalid lost display1"
        with pytest.raises(ValueError, match="Invalid sink power status notification format"):
            NotificationSink.parse(notification)

    def test_parse_invalid_status(self):
        """Test parsing with invalid sink power status."""
        notification = "notify sink invalid display1"
        with pytest.raises(ValueError, match="Invalid sink power status: invalid"):
            NotificationSink.parse(notification)

    def test_parse_empty_device_name(self):
        """Test parsing with empty device name."""
        notification = "notify sink lost "
        with pytest.raises(ValueError, match="Invalid sink power status notification format"):
            NotificationSink.parse(notification)


class TestNotificationParser:
    """Unit tests for NotificationParser."""

    # =============================================================================
    # Notification Parser Utility
    # =============================================================================

    def test_parse_endpoint_notification(self):
        """Test parsing endpoint notification."""
        notification = "notify endpoint + display1"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationEndpoint)
        assert result.online is True
        assert result.device == "display1"

    def test_parse_cec_notification(self):
        """Test parsing CEC notification."""
        notification = 'notify cecinfo display1 "FF36"'
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationCecinfo)
        assert result.device == "display1"
        assert result.cec_data == "FF36"

    def test_parse_infrared_notification(self):
        """Test parsing infrared notification."""
        notification = 'notify irinfo display1 "0000 0067"'
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationIrinfo)
        assert result.device == "display1"
        assert result.ir_data == "0000 0067"

    def test_parse_serial_notification(self):
        """Test parsing serial notification."""
        notification = "notify serialinfo display1 hex 10:\r\n48656c6c6f"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationSerialinfo)
        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 10
        assert result.serial_data == "48656c6c6f"

    def test_parse_video_notification(self):
        """Test parsing video notification."""
        notification = "notify video found display1 source1"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationVideo)
        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device == "source1"

    def test_parse_sink_power_notification(self):
        """Test parsing sink power notification."""
        notification = "notify sink lost display1"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationSink)
        assert result.status == "lost"
        assert result.device == "display1"

    def test_parse_with_whitespace(self):
        """Test parsing with whitespace around notification."""
        notification = "  notify endpoint + display1  "
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, NotificationEndpoint)
        assert result.online is True
        assert result.device == "display1"

    def test_parse_unknown_notification_type(self):
        """Test parsing unknown notification type."""
        notification = "notify unknown data"
        with pytest.raises(ValueError, match="Unknown notification type"):
            NotificationParser.parse_notification(notification)

    def test_parse_invalid_notification_format(self):
        """Test parsing completely invalid notification format."""
        notification = "invalid notification format"
        with pytest.raises(ValueError, match="Unknown notification type"):
            NotificationParser.parse_notification(notification)

    def test_parse_empty_notification(self):
        """Test parsing empty notification."""
        notification = ""
        with pytest.raises(ValueError, match="Unknown notification type"):
            NotificationParser.parse_notification(notification)

    def test_parse_whitespace_only_notification(self):
        """Test parsing whitespace-only notification."""
        notification = "   "
        with pytest.raises(ValueError, match="Unknown notification type"):
            NotificationParser.parse_notification(notification)

    def test_get_notification_type_endpoint(self):
        """Test getting notification type for endpoint notifications."""
        assert NotificationParser.get_notification_type("notify endpoint + display1") == "endpoint"
        assert NotificationParser.get_notification_type("notify endpoint - display1") == "endpoint"

    def test_get_notification_type_cecinfo(self):
        """Test getting notification type for CEC notifications."""
        assert NotificationParser.get_notification_type('notify cecinfo display1 "data"') == "cecinfo"

    def test_get_notification_type_irinfo(self):
        """Test getting notification type for infrared notifications."""
        assert NotificationParser.get_notification_type('notify irinfo display1 "data"') == "irinfo"

    def test_get_notification_type_serialinfo(self):
        """Test getting notification type for serial notifications."""
        assert NotificationParser.get_notification_type("notify serialinfo display1 hex 10:data") == "serialinfo"

    def test_get_notification_type_video(self):
        """Test getting notification type for video notifications."""
        assert NotificationParser.get_notification_type("notify video found display1") == "video"

    def test_get_notification_type_sink(self):
        """Test getting notification type for sink notifications."""
        assert NotificationParser.get_notification_type("notify sink lost display1") == "sink"

    def test_get_notification_type_with_whitespace(self):
        """Test getting notification type with whitespace."""
        assert NotificationParser.get_notification_type("  notify endpoint + display1  ") == "endpoint"

    def test_get_notification_type_unknown(self):
        """Test getting notification type for unknown notifications."""
        with pytest.raises(ValueError, match="Unknown notification type: notify unknown data"):
            NotificationParser.get_notification_type("notify unknown data")

    def test_get_notification_type_invalid_format(self):
        """Test getting notification type for invalid format."""
        with pytest.raises(ValueError, match="Unknown notification type: invalid format"):
            NotificationParser.get_notification_type("invalid format")

    def test_get_notification_type_empty_string(self):
        """Test getting notification type for empty string."""
        with pytest.raises(ValueError, match="Unknown notification type: "):
            NotificationParser.get_notification_type("")

    def test_get_notification_type_whitespace_only(self):
        """Test getting notification type for whitespace-only string."""
        with pytest.raises(ValueError, match="Unknown notification type: "):
            NotificationParser.get_notification_type("   ")
