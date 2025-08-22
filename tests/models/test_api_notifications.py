import pytest

from wyrestorm_networkhd.models.api_notifications import (
    EndpointCECDataNotification,
    EndpointInfraredDataNotification,
    EndpointOnlineStatusNotification,
    EndpointRS232DataNotification,
    EndpointVideoInputStatusNotification,
    NotificationParser,
)


class TestEndpointOnlineStatusNotification:
    """Unit tests for EndpointOnlineStatusNotification."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint online status notification
    # =============================================================================

    def test_parse_online_status_success(self):
        """Test parsing online status notification."""
        # Arrange
        notification = "notify endpoint + source1"

        # Act
        result = EndpointOnlineStatusNotification.parse(notification)

        # Assert
        assert result.online is True
        assert result.device == "source1"

    def test_parse_offline_status_success(self):
        """Test parsing offline status notification."""
        # Arrange
        notification = "notify endpoint - display1"

        # Act
        result = EndpointOnlineStatusNotification.parse(notification)

        # Assert
        assert result.online is False
        assert result.device == "display1"

    def test_parse_offline_status_success_em_dash(self):
        """Test parsing offline status notification with em dash."""
        notification = "notify endpoint – display1"
        result = EndpointOnlineStatusNotification.parse(notification)

        assert result.online is False
        assert result.device == "display1"

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        notification = "  notify endpoint + source1  "
        result = EndpointOnlineStatusNotification.parse(notification)

        assert result.online is True
        assert result.device == "source1"

    def test_parse_invalid_parts_count_too_few(self):
        """Test parsing with too few parts."""
        notification = "notify endpoint +"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            EndpointOnlineStatusNotification.parse(notification)

    def test_parse_invalid_parts_count_too_many(self):
        """Test parsing with too many parts."""
        notification = "notify endpoint + display1 extra"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            EndpointOnlineStatusNotification.parse(notification)

    def test_parse_invalid_first_part(self):
        """Test parsing with invalid first part."""
        notification = "invalid endpoint + display1"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            EndpointOnlineStatusNotification.parse(notification)

    def test_parse_invalid_second_part(self):
        """Test parsing with invalid second part."""
        notification = "notify invalid + display1"
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            EndpointOnlineStatusNotification.parse(notification)

    def test_parse_invalid_status_indicator(self):
        """Test parsing with invalid status indicator."""
        notification = "notify endpoint = display1"
        with pytest.raises(ValueError, match="Invalid endpoint status indicator"):
            EndpointOnlineStatusNotification.parse(notification)

    def test_parse_empty_device_name(self):
        """Test parsing with empty device name."""
        notification = "notify endpoint + "
        with pytest.raises(ValueError, match="Invalid endpoint status notification format"):
            EndpointOnlineStatusNotification.parse(notification)


class TestEndpointCECDataNotification:
    """Unit tests for EndpointCECDataNotification."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint CEC data notification
    # =============================================================================

    def test_parse_cec_data_success(self):
        """Test parsing CEC data notification."""
        notification = 'notify cecinfo display1 "FF36"'
        result = EndpointCECDataNotification.parse(notification)

        assert result.device == "display1"
        assert result.cec_data == "FF36"

    def test_parse_cec_data_with_spaces_in_device(self):
        """Test parsing with spaces in device name."""
        notification = 'notify cecinfo display 1 "FF36"'
        result = EndpointCECDataNotification.parse(notification)

        assert result.device == "display 1"
        assert result.cec_data == "FF36"

    def test_parse_cec_data_empty_data(self):
        """Test parsing with empty CEC data."""
        notification = 'notify cecinfo display1 ""'
        result = EndpointCECDataNotification.parse(notification)

        assert result.device == "display1"
        assert result.cec_data == ""

    def test_parse_cec_data_complex_data(self):
        """Test parsing with complex CEC data."""
        notification = 'notify cecinfo source1 "FF36 1234 ABCD"'
        result = EndpointCECDataNotification.parse(notification)

        assert result.device == "source1"
        assert result.cec_data == "FF36 1234 ABCD"

    def test_parse_missing_prefix(self):
        """Test parsing with missing prefix."""
        notification = 'invalid cecinfo display1 "FF36"'
        with pytest.raises(ValueError, match="Invalid CEC data notification format"):
            EndpointCECDataNotification.parse(notification)

    def test_parse_no_quotes(self):
        """Test parsing without quotes."""
        notification = "notify cecinfo display1 FF36"
        with pytest.raises(ValueError, match="Invalid CEC data notification format"):
            EndpointCECDataNotification.parse(notification)

    def test_parse_no_opening_quote(self):
        """Test parsing without opening quote."""
        notification = 'notify cecinfo display1 FF36"'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            EndpointCECDataNotification.parse(notification)

    def test_parse_no_closing_quote(self):
        """Test parsing without closing quote."""
        notification = 'notify cecinfo display1 "FF36'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            EndpointCECDataNotification.parse(notification)

    def test_parse_only_one_quote(self):
        """Test parsing with only one quote."""
        notification = 'notify cecinfo display1 "FF36 incomplete'
        with pytest.raises(ValueError, match="Invalid CEC data notification format \\(unclosed quotes\\)"):
            EndpointCECDataNotification.parse(notification)

    def test_parse_quotes_edge_case(self):
        """Test parsing with quotes edge case - this should parse successfully."""
        notification = 'notify cecinfo display1 FF36" "data'
        result = EndpointCECDataNotification.parse(notification)

        # This extracts content between first and last quote: FF36" "
        # Device is everything before first quote: display1 FF36
        # CEC data is between quotes: " " (the space and quote)
        assert result.device == "display1 FF36"
        assert result.cec_data == " "


class TestEndpointInfraredDataNotification:
    """Unit tests for EndpointInfraredDataNotification."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint Infrared data notification
    # =============================================================================

    def test_parse_ir_data_success(self):
        """Test parsing infrared data notification."""
        notification = 'notify irinfo display1 "0000 0067 0000 0015"'
        result = EndpointInfraredDataNotification.parse(notification)

        assert result.device == "display1"
        assert result.ir_data == "0000 0067 0000 0015"

    def test_parse_ir_data_with_spaces_in_device(self):
        """Test parsing with spaces in device name."""
        notification = 'notify irinfo display 1 "0000 0067"'
        result = EndpointInfraredDataNotification.parse(notification)

        assert result.device == "display 1"
        assert result.ir_data == "0000 0067"

    def test_parse_ir_data_empty_data(self):
        """Test parsing with empty IR data."""
        notification = 'notify irinfo display1 ""'
        result = EndpointInfraredDataNotification.parse(notification)

        assert result.device == "display1"
        assert result.ir_data == ""

    def test_parse_ir_data_complex_data(self):
        """Test parsing with complex IR data."""
        notification = 'notify irinfo source1 "0000 0067 0000 0015 0060 0018 0018 0018"'
        result = EndpointInfraredDataNotification.parse(notification)

        assert result.device == "source1"
        assert result.ir_data == "0000 0067 0000 0015 0060 0018 0018 0018"

    def test_parse_missing_prefix(self):
        """Test parsing with missing prefix."""
        notification = 'invalid irinfo display1 "0000"'
        with pytest.raises(ValueError, match="Invalid infrared data notification format"):
            EndpointInfraredDataNotification.parse(notification)

    def test_parse_no_quotes(self):
        """Test parsing without quotes."""
        notification = "notify irinfo display1 0000"
        with pytest.raises(ValueError, match="Invalid infrared data notification format"):
            EndpointInfraredDataNotification.parse(notification)

    def test_parse_no_opening_quote(self):
        """Test parsing without opening quote."""
        notification = 'notify irinfo display1 0000"'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            EndpointInfraredDataNotification.parse(notification)

    def test_parse_no_closing_quote(self):
        """Test parsing without closing quote."""
        notification = 'notify irinfo display1 "0000'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            EndpointInfraredDataNotification.parse(notification)

    def test_parse_only_one_quote(self):
        """Test parsing with only one quote."""
        notification = 'notify irinfo display1 "0000 incomplete'
        with pytest.raises(ValueError, match="Invalid infrared data notification format \\(unclosed quotes\\)"):
            EndpointInfraredDataNotification.parse(notification)


class TestEndpointRS232DataNotification:
    """Unit tests for EndpointRS232DataNotification."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint RS-232 data notification
    # =============================================================================

    def test_parse_rs232_hex_success(self):
        """Test parsing RS-232 hex data notification."""
        notification = "notify serialinfo display1 hex 371:\r\n48656c6c6f"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 371
        assert result.serial_data == "48656c6c6f"

    def test_parse_rs232_ascii_success(self):
        """Test parsing RS-232 ASCII data notification."""
        notification = "notify serialinfo source1 ascii 122:\r\nHello World"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "source1"
        assert result.data_format == "ascii"
        assert result.data_length == 122
        assert result.serial_data == "Hello World"

    def test_parse_rs232_no_crlf(self):
        """Test parsing without CR/LF before data."""
        notification = "notify serialinfo display1 hex 10:48656c6c6f"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 10
        assert result.serial_data == "48656c6c6f"

    def test_parse_rs232_only_cr(self):
        """Test parsing with only CR before data."""
        notification = "notify serialinfo display1 ascii 5:\rHello"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 5
        assert result.serial_data == "Hello"

    def test_parse_rs232_only_lf(self):
        """Test parsing with only LF before data."""
        notification = "notify serialinfo display1 ascii 5:\nHello"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 5
        assert result.serial_data == "Hello"

    def test_parse_rs232_empty_data(self):
        """Test parsing with empty data."""
        notification = "notify serialinfo display1 hex 0:"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 0
        assert result.serial_data == ""

    def test_parse_invalid_prefix(self):
        """Test parsing with invalid prefix."""
        notification = "invalid serialinfo display1 hex 10:data"
        with pytest.raises(ValueError, match="Invalid serial data notification format"):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_no_colon(self):
        """Test parsing without colon separator."""
        notification = "notify serialinfo display1 hex 10 data"
        with pytest.raises(ValueError, match="Invalid serial data notification format \\(no colon\\)"):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_invalid_header_too_few_parts(self):
        """Test parsing with too few header parts."""
        notification = "notify serialinfo display1 hex:data"
        with pytest.raises(ValueError, match="Invalid serial data notification header"):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_invalid_header_too_many_parts(self):
        """Test parsing with too many header parts."""
        notification = "notify serialinfo display1 hex 10 extra:data"
        with pytest.raises(ValueError, match="Invalid serial data notification header"):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_invalid_data_format(self):
        """Test parsing with invalid data format."""
        notification = "notify serialinfo display1 invalid 10:data"
        with pytest.raises(ValueError, match="Invalid serial data format: invalid"):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_invalid_data_length_not_integer(self):
        """Test parsing with non-integer data length."""
        notification = "notify serialinfo display1 hex abc:data"
        with pytest.raises(ValueError):
            EndpointRS232DataNotification.parse(notification)

    def test_parse_data_with_colon(self):
        """Test parsing with colon in data part."""
        notification = "notify serialinfo display1 ascii 10:\r\nhello:world"
        result = EndpointRS232DataNotification.parse(notification)

        assert result.device == "display1"
        assert result.data_format == "ascii"
        assert result.data_length == 10
        assert result.serial_data == "hello:world"


class TestEndpointVideoInputStatusNotification:
    """Unit tests for EndpointVideoInputStatusNotification."""

    # =============================================================================
    # 12.2 Endpoint Notifications - Endpoint video input status notification
    # =============================================================================

    def test_parse_video_found_with_source(self):
        """Test parsing video found notification with source device."""
        notification = "notify video found display1 source1"
        result = EndpointVideoInputStatusNotification.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device == "source1"

    def test_parse_video_lost_without_source(self):
        """Test parsing video lost notification without source device."""
        notification = "notify video lost source1"
        result = EndpointVideoInputStatusNotification.parse(notification)

        assert result.status == "lost"
        assert result.device == "source1"
        assert result.source_device is None

    def test_parse_video_found_without_source(self):
        """Test parsing video found notification without source device."""
        notification = "notify video found display1"
        result = EndpointVideoInputStatusNotification.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device is None

    def test_parse_with_whitespace(self):
        """Test parsing with extra whitespace."""
        notification = "  notify video lost source1  "
        result = EndpointVideoInputStatusNotification.parse(notification)

        assert result.status == "lost"
        assert result.device == "source1"
        assert result.source_device is None

    def test_parse_invalid_too_few_parts(self):
        """Test parsing with too few parts."""
        notification = "notify video"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            EndpointVideoInputStatusNotification.parse(notification)

    def test_parse_invalid_first_part(self):
        """Test parsing with invalid first part."""
        notification = "invalid video found display1"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            EndpointVideoInputStatusNotification.parse(notification)

    def test_parse_invalid_second_part(self):
        """Test parsing with invalid second part."""
        notification = "notify invalid found display1"
        with pytest.raises(ValueError, match="Invalid video status notification format"):
            EndpointVideoInputStatusNotification.parse(notification)

    def test_parse_invalid_status(self):
        """Test parsing with invalid video status."""
        notification = "notify video invalid display1"
        with pytest.raises(ValueError, match="Invalid video status: invalid"):
            EndpointVideoInputStatusNotification.parse(notification)

    def test_parse_exact_minimum_parts(self):
        """Test parsing with exactly minimum required parts."""
        notification = "notify video found display1"
        result = EndpointVideoInputStatusNotification.parse(notification)

        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device is None


class TestNotificationParser:
    """Unit tests for NotificationParser."""

    # =============================================================================
    # Notification Parser Utility
    # =============================================================================

    def test_parse_endpoint_notification(self):
        """Test parsing endpoint notification."""
        notification = "notify endpoint + display1"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointOnlineStatusNotification)
        assert result.online is True
        assert result.device == "display1"

    def test_parse_cec_notification(self):
        """Test parsing CEC notification."""
        notification = 'notify cecinfo display1 "FF36"'
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointCECDataNotification)
        assert result.device == "display1"
        assert result.cec_data == "FF36"

    def test_parse_infrared_notification(self):
        """Test parsing infrared notification."""
        notification = 'notify irinfo display1 "0000 0067"'
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointInfraredDataNotification)
        assert result.device == "display1"
        assert result.ir_data == "0000 0067"

    def test_parse_serial_notification(self):
        """Test parsing serial notification."""
        notification = "notify serialinfo display1 hex 10:\r\n48656c6c6f"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointRS232DataNotification)
        assert result.device == "display1"
        assert result.data_format == "hex"
        assert result.data_length == 10
        assert result.serial_data == "48656c6c6f"

    def test_parse_video_notification(self):
        """Test parsing video notification."""
        notification = "notify video found display1 source1"
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointVideoInputStatusNotification)
        assert result.status == "found"
        assert result.device == "display1"
        assert result.source_device == "source1"

    def test_parse_with_whitespace(self):
        """Test parsing with whitespace around notification."""
        notification = "  notify endpoint + display1  "
        result = NotificationParser.parse_notification(notification)

        assert isinstance(result, EndpointOnlineStatusNotification)
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
