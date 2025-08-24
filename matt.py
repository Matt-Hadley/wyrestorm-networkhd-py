#!/usr/bin/env python3
"""Example NetworkHD client script for Matt.

Connects to NetworkHD device and runs various get commands.
"""

import asyncio

from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH


async def main():
    """Main function to connect and run commands."""

    # Create client with SSH connection
    client = NetworkHDClientSSH(
        host="192.168.0.234",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",
        timeout=10.0,
    )

    try:
        # Connect to the device
        print("Connecting to NetworkHD device...")
        await client.connect()
        print("Connected successfully!")

        # Test basic command first
        print("\n--- Testing Basic Command ---")
        try:
            response = await client.send_command("config get version")
            print(f"Raw response: {repr(response)}")
        except Exception as e:
            print(f"Error with basic command: {e}")
            return

        # Create API wrapper
        api = NHDAPI(client)

        # Get device status
        print("\n--- Device Status ---")
        try:
            device_status = await api.api_query.config_get_device_status()
            print(f"Device Status: {device_status}")
        except Exception as e:
            print(f"Error getting device status: {e}")

        # Get device list
        print("\n--- Device List ---")
        try:
            device_list = await api.api_query.config_get_devicelist()
            print(f"Device List: {device_list}")
        except Exception as e:
            print(f"Error getting device list: {e}")

        # Get matrix info
        print("\n--- Matrix Info ---")
        try:
            matrix_info = await api.api_query.matrix_get()
            print(f"Matrix Info: {matrix_info}")
        except Exception as e:
            print(f"Error getting matrix info: {e}")

        # Get system version
        print("\n--- System Version ---")
        try:
            version = await api.api_query.config_get_version()
            print(f"System Version: {version}")
        except Exception as e:
            print(f"Error getting version: {e}")

        # Get IP settings
        print("\n--- IP Settings ---")
        try:
            ip_settings = await api.api_query.config_get_ipsetting()
            print(f"IP Settings: {ip_settings}")
        except Exception as e:
            print(f"Error getting IP settings: {e}")

        # Text overlay example
        print("\n--- Text Overlay Example ---")
        try:
            # Configure text overlay with white text
            color = api.video_stream_text_overlay.get_color_hex("white", "nhd110_140")
            overlay_response = await api.video_stream_text_overlay.config_set_device_osd_param(
                text="Hello from Python!",
                position_x=100,
                position_y=100,
                text_color=color,
                text_size=2,
                tx="ServerCupboardAppleTV",
            )
            print(f"Text overlay configured: {overlay_response}")

            # Enable text overlay
            enable_response = await api.video_stream_text_overlay.config_set_device_osd("on", "ServerCupboardAppleTV")
            print(f"Text overlay enabled: {enable_response}")

            print("Text overlay 'Hello from Python!' should now be visible on Dining display")

            # Wait 10 seconds then disable
            print("Waiting 10 seconds before disabling...")
            await asyncio.sleep(10)

            # Disable text overlay
            disable_response = await api.video_stream_text_overlay.config_set_device_osd("off", "ServerCupboardAppleTV")
            print(f"Text overlay disabled: {disable_response}")

        except Exception as e:
            print(f"Error with text overlay: {e}")

        print("\nAll commands completed!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect
        if client.is_connected():
            await client.disconnect()
            print("Disconnected from device")


# Comment out the main function to test notifications instead
if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())


# ============================================================================
# NOTIFICATION STREAMING CODE (ACTIVE)
# ============================================================================


async def stream_notifications():
    """Stream notifications for 30 seconds to test notification handling."""
    # Create client with SSH connection
    client = NetworkHDClientSSH(
        host="192.168.0.234",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="auto_add",  # Changed from "warn" to "auto_add" to avoid host key issues
        timeout=10.0,
    )

    # Register notification callbacks
    def on_device_status(notification):
        print(f"🔔 Device Status: {notification.device} is {'🟢 online' if notification.online else '🔴 offline'}")

    def on_cec_data(notification):
        print(f"📺 CEC Data: {notification.device} - {notification.cec_data}")

    def on_infrared_data(notification):
        print(f"📡 Infrared Data: {notification}")

    def on_rs232_data(notification):
        print(f"🔌 RS232 Data: {notification}")

    def on_video_input_change(notification):
        if notification.source_device:
            print(
                f"📺 Video Input: {notification.device} {'🟢 found' if notification.status == 'found' else '🔴 lost'} connection to {notification.source_device}"
            )
        else:
            print(
                f"📹 Video Input: {notification.device} {'🟢 found' if notification.status == 'found' else '🔴 lost'} video signal"
            )

    def on_sink_power_change(notification):
        print(
            f"🔌 Sink Power: {notification.device} is {'🟢 powered on' if notification.status == 'found' else '🔴 powered off'}"
        )

    # Register callbacks for all notification types
    client.register_notification_callback("endpoint", on_device_status)
    client.register_notification_callback("cecinfo", on_cec_data)
    client.register_notification_callback("irinfo", on_infrared_data)
    client.register_notification_callback("serialinfo", on_rs232_data)
    client.register_notification_callback("video", on_video_input_change)
    client.register_notification_callback("sink", on_sink_power_change)

    # Add a raw notification handler to see what's actually coming through
    def on_raw_notification(notification):
        # print(f"🔍 RAW: {repr(notification)}")
        pass

    # Register for all notification types to catch everything
    for notification_type in ["endpoint", "cecinfo", "irinfo", "serialinfo", "video", "sink"]:
        client.register_notification_callback(notification_type, on_raw_notification)

    try:
        # Connect and start receiving notifications
        print("🔌 Connecting to NetworkHD device for notifications...")
        await client.connect()
        print("✅ Connected! Listening for notifications for 30 seconds...")
        print("🎯 To test notifications, try:")
        print("   • Disconnect/reconnect HDMI sources (video)")
        print("   • Send CEC commands from devices (cecinfo)")
        print("   • Send IR commands to endpoints (irinfo)")
        print("   • Send RS232 commands (serialinfo)")
        print("   • Power cycle endpoints (endpoint)")
        print("   • Send power commands via CEC/RS232 (sink)")
        print("⏰ Will automatically stop after 300 seconds...")

        # Listen for notifications for 300 seconds
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 300.0:
            await asyncio.sleep(0.1)

        print("⏰ 300 seconds elapsed, stopping...")

    except KeyboardInterrupt:
        print("\n🛑 Stopping notification stream...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if client.is_connected():
            await client.disconnect()
            print("🔌 Disconnected from device")


# Run notification streaming for testing
# if __name__ == "__main__":
#     asyncio.run(stream_notifications())
