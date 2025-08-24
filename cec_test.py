#!/usr/bin/env python3
"""
Simple CEC Test Script - Power cycle the Dining TV
This script sends CEC power off, waits 5 seconds, then power on to the Dining TV.
"""

import asyncio

from wyrestorm_networkhd import NHDAPI, NetworkHDClientSSH


async def main():
    """Simple CEC power cycle test for Dining TV."""
    # Create client with SSH connection
    client = NetworkHDClientSSH(
        host="192.168.0.234",
        port=10022,
        username="wyrestorm",
        password="networkhd",
        ssh_host_key_policy="auto_add",
        timeout=10.0,
    )

    try:
        print("🔌 Connecting to NetworkHD device...")
        await client.connect()
        print("✅ Connected!")

        # Create API wrapper
        api = NHDAPI(client)

        # Enable CEC notifications for Dining
        print("🔔 Enabling CEC notifications for Dining...")
        try:
            await api.api_notifications.config_set_device_cec_notify("on", "Dining")
            print("✅ CEC notifications enabled")
        except Exception as e:
            print(f"⚠️ Warning: Could not enable CEC notifications: {e}")

        print("\n🎮 Power cycling Dining TV...")

        # Send CEC standby (power off)
        print("📴 Sending CEC Standby (Power Off)...")
        await api.connected_device_control.config_set_device_cec("standby", "Dining")
        print("✅ Power off sent")

        # Wait 5 seconds
        print("⏳ Waiting 5 seconds...")
        await asyncio.sleep(5)

        # Send CEC one touch play (power on)
        print("📺 Sending CEC One Touch Play (Power On)...")
        await api.connected_device_control.config_set_device_cec("onetouchplay", "Dining")
        print("✅ Power on sent")

        print("\n✅ Power cycle complete! Check your notification listener for CEC notifications.")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if client.is_connected():
            await client.disconnect()
            print("🔌 Disconnected from device")


if __name__ == "__main__":
    asyncio.run(main())
