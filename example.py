#!/usr/bin/env python3
"""
Example usage of the WyreStorm NetworkHD API Client

This example demonstrates how to use the library to connect to a NetworkHD controller
and execute various commands across different categories.

To run this example:
1. Install the development environment: make install
2. Activate the virtual environment: source .venv/bin/activate
3. Update the connection details below for your device
4. Run: python example.py

For development workflow: make dev-workflow
"""

import asyncio

from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH


async def main():
    """Example usage of the NetworkHD API client"""

    # Create client with SSH connection
    client = NetworkHDClientSSH(
        host="192.168.1.100",  # Replace with your NHD-CTL IP address
        port=22,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="warn",  # Change to "auto_add" to auto-accept unknown keys
        timeout=10.0,
    )

    try:
        # Use async context manager for automatic connection handling
        async with client:
            print("Connected to NetworkHD controller!")

            # Create API wrapper for organized command access
            api = NHDAPI(client)

            # Example 1: System Configuration Commands
            print("\n=== System Configuration ===")

            # Reboot the controller
            print("Rebooting controller...")
            response = await api.reboot_reset.set_reboot()
            print(f"Response: {response}")

            # Example 2: Matrix Switching Commands
            print("\n=== Matrix Switching ===")

            # Assign source1 to display1 and display2
            print("Setting up matrix routing...")
            response = await api.media_stream_matrix_switch.matrix_set("source1", ["display1", "display2"])
            print(f"Response: {response}")

            # Set video-only routing
            response = await api.media_stream_matrix_switch.matrix_video_set("source2", "display3")
            print(f"Video routing response: {response}")

            # Example 3: Connected Device Control Commands
            print("\n=== Connected Device Control ===")

            # Send power on command to displays
            print("Powering on displays...")
            response = await api.connected_device_control.config_set_device_sinkpower("on", ["display1", "display2"])
            print(f"Power response: {response}")

            # Send custom infrared command
            ir_data = "0000 0067 0000 0015 0060 0018 0030 0018"  # Example IR data
            response = await api.connected_device_control.infrared(ir_data, "source1")
            print(f"IR response: {response}")

            # Example 4: Video Wall Commands
            print("\n=== Video Wall ===")

            # Apply a video wall scene
            print("Activating video wall scene...")
            response = await api.video_wall.scene_active("OfficeVW", "Splitmode")
            print(f"Scene response: {response}")

            # Example 5: Multiview Commands
            print("\n=== Multiview ===")

            # Apply multiview layout
            print("Setting multiview layout...")
            response = await api.multiview.mscene_active("display5", "gridlayout")
            print(f"Multiview response: {response}")

            # Example 6: Device Port Switching
            print("\n=== Device Port Switching ===")

            # Switch video source on encoder
            response = await api.device_port_switch.config_set_device_videosource("source1", "hdmi")
            print(f"Video source switch: {response}")

            # Example 7: Query Commands
            print("\n=== System Queries ===")

            # Get device list
            response = await api.api_query.get_devicelist()
            print(f"Device list: {response}")

            # Get matrix status
            response = await api.api_query.matrix_get()
            print(f"Matrix status: {response}")

            # Example 8: Audio Output Control
            print("\n=== Audio Control ===")

            # Control analog audio volume
            response = await api.audio_output.config_set_device_audio_volume_analog("up", "display1")
            print(f"Volume response: {response}")

            # Example 9: Text Overlay
            print("\n=== Text Overlay ===")

            # Configure text overlay
            color = api.video_stream_text_overlay.get_color_hex("white", "nhd110_140")
            response = await api.video_stream_text_overlay.config_set_device_osd_param(
                text="Hello World", position_x=100, position_y=100, text_color=color, text_size=2, tx="source1"
            )
            print(f"Text overlay config: {response}")

            # Enable text overlay
            response = await api.video_stream_text_overlay.config_set_device_osd("on", "source1")
            print(f"Text overlay enable: {response}")

            # Example 10: Real-time Notifications
            print("\n=== Real-time Notifications ===")

            # Register notification callbacks
            def on_device_status(notification):
                print(f"Device {notification.device} is {'online' if notification.online else 'offline'}")

            def on_cec_data(notification):
                print(f"CEC data from {notification.device}: {notification.data}")

            # Register callbacks for different notification types
            client.register_notification_callback("endpoint", on_device_status)
            client.register_notification_callback("cec", on_cec_data)

            print("Notification callbacks registered - you'll see real-time updates while connected")

            print("\n=== All commands completed successfully! ===")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
