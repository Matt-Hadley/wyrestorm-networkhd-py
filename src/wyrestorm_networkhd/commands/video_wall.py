from typing import Literal

from ._response_helpers import require_success_indicator


class VideoWallCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 10.1 Video Wall – 'Standard Video Wall' Scenes
    # Use this command to apply preset 'standard video wall' Scenes to a video wall. Where available at the NetworkHD endpoints,
    # 'standard video wall' scenes configured in the NetworkHD Console software utility can be recalled and applied to physical video
    # wall arrays.
    # =============================================================

    async def scene_active(self, videowall: str, scene: str) -> bool:
        """Apply a 'standard video wall' Scene to a physical video wall array

        Args:
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Video wall names are given to physical video wall arrays when created in the NetworkHD Console software utility.
            When video wall arrays are created in Console, the physical displays will have decoders assigned to them.
            Scene names are given to Scenes when created in the NetworkHD Console software utility.
            When scenes are created in Console, the decoders will have default encoders or no encoder (NULL) assigned to them.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name

        Command structure:
            scene active <videowall>-<scene>

        Response structure:
            scene <videowall>-<scene> active [success|failure]

        Command Example: Apply a videowall scene
            scene active OfficeVW-Splitmode

        Response Example: Command acknowledgment
            scene OfficeVW-Splitmode active success
        """
        command = f"scene active {videowall}-{scene}"
        response = await self.client.send_command(command)
        return require_success_indicator(response, expected_start=f"scene {videowall}-{scene} active")

    async def scene_set(self, videowall: str, scene: str, x: int, y: int, tx: str) -> bool:
        """Change the encoder assigned to a single decoder in a 'standard video wall' Scene

        Args:
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            x: Decoder's horizontal position in display array
            y: Decoder's vertical position in display array
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command commits and saves change to Scene but does not apply live until using the scene active command.
            Command will only be effective for decoders that are not part of a Logical Screen element in a Scene.
            Horizontal and vertical positions are relative to the top left display.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            X: Decoder's horizontal position in display array
            Y: Decoder's vertical position in display array

        Command structure:
            scene set <videowall>-<scene> <X> <Y> <TX>

        Response structure:
            scene <videowall>-<scene>'s source in [<X>,<Y>] change to <TX>

        Command Example: Change the encoder assigned to decoder in a scene
            scene set OfficeVW-Splitmode 1 2 source1

        Response Example: Command acknowledgment
            scene OfficeVW-Splitmode's source in [1,2] change to source1
        """
        command = f"scene set {videowall}-{scene} {x} {y} {tx}"
        response = await self.client.send_command(command)
        # Consider success if the response matches the expected statement exactly
        success: bool = response.strip() == f"scene {videowall}-{scene}'s source in [{x},{y}] change to {tx}"
        return success

    async def vw_change(self, videowall: str, scene: str, lscreen: str, tx: str) -> bool:
        """Change the encoder assigned to a Logical Screen in a 'standard video wall' Scene

        Args:
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            lscreen: Preconfigured Logical Screen name
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command will be effective immediately for the Logical Screen and will not save to Scene.
            Following with a scene active command will reset the Logical Screen to the default encoder for the Scene.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            videowall: Preconfigured video wall name
            scene: Preconfigured Scene name
            Lscreen: Preconfigured Logical Screen name

        Command structure:
            vw change <videowall>-<scene>_<Lscreen> <TX>

        Response structure:
            videowall <videowall>-<scene>_<Lscreen> tx connect to <TX>

        Command Example: Change the encoder assigned to a Logical Screen in a scene
            vw change OfficeVW-Combined_TopTwo source1

        Response Example: Command acknowledgment
            videowall change OfficeVW-Combined_TopTwo tx connect to source1
        """
        command = f"vw change {videowall}-{scene}_{lscreen} {tx}"
        response = await self.client.send_command(command)
        success: bool = response.strip() == f"videowall change {videowall}-{scene}_{lscreen} tx connect to {tx}"
        return success

    # =============================================================
    # 10.2 Video Wall – 'Video Wall within a Wall' Scenes
    # Use this command to apply window functions to 'video wall within a wall' Scenes to a video wall. Where available at the NetworkHD
    # endpoints, 'videowall within a wall' scenes configured in the NetworkHD Console software utility can be recalled and manipulation
    # of windows applied to physical video wall arrays.
    # =============================================================

    async def wscene2_active(self, videowall: str, wscene: str) -> bool:
        """Apply a 'video wall within a wall' Scene to a physical video wall array

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Video wall names are given to physical video wall arrays when created in the NetworkHD Console software utility.
            When video wall arrays are created in the NetworkHD Console, the physical displays will have decoders assigned to them.
            Scene names are given to Scenes when created in the NetworkHD Console software utility.
            When scenes are created in the NetworkHD Console, the decoders will have no encoder (NULL) assigned to them.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name

        Command structure:
            wscene2 active <videowall>-<wscene>

        Response structure:
            wscene2 active <videowall>-<wscene> [success|failure]

        Command Example: Apply a video wall scene
            wscene2 active OfficeVW-windowscene

        Response Example: Command acknowledgment
            wscene2 active OfficeVW-windowscene success
        """
        command = f"wscene2 active {videowall}-{wscene}"
        response = await self.client.send_command(command)
        return require_success_indicator(response, expected_start=f"wscene2 active {videowall}-{wscene}")

    async def wscene2_window_open(
        self, videowall: str, wscene: str, wname: str, x: int, y: int, h: int, v: int, tx: str
    ) -> bool:
        """Open a window within a 'video wall within a wall' Scene

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            x: Window's top left decoder horizontal position in display array
            y: Window's top left decoder vertical position in display array
            h: Window's horizontal size in number of displays
            v: Window's vertical size in number of displays
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Positions are ZERO INDEXED in this command, e.g. top-left display is X = 0, Y = 0
            Command is effective immediately and does not save to the default Scene.
            Horizontal and vertical positions are relative to the top left display.
            Window names must be unique to the command and are not defined using the NetworkHD Console software utility.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            X: Window's top left decoder horizontal position in display array
            Y: Window's top left decoder vertical position in display array
            H: Window's horizontal size in number of displays
            V: Window's vertical size in number of displays

        Command structure:
            wscene2 window open <videowall>-<wscene> <wname> <X> <Y> <H> <V> <TX>

        Response structure:
            wscene2 window open <videowall>-<wscene> <wname> <X> <Y> <H> <V> <TX> [success|failure]

        Command Example: Open a window within a scene
            wscene2 window open OfficeVW-windowscene window1 0 0 2 2 source1

        Response Example: Command acknowledgment
            wscene2 window open OfficeVW-windowscene window1 0 0 2 2 source1 success
        """
        command = f"wscene2 window open {videowall}-{wscene} {wname} {x} {y} {h} {v} {tx}"
        response = await self.client.send_command(command)
        return require_success_indicator(
            response, expected_start=f"wscene2 window open {videowall}-{wscene} {wname} {x} {y} {h} {v} {tx}"
        )

    async def wscene2_window_close(self, videowall: str, wscene: str, wname: str) -> bool:
        """Close a window within a 'video wall within a wall' Scene

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command is effective immediately and does not save to the default Scene.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name

        Command structure:
            wscene2 window close <videowall>-<wscene> <wname>

        Response structure:
            wscene2 window close <videowall>-<wscene> <wname> [success|failure]

        Command Example: Close a window within a scene
            wscene2 window close OfficeVW-windowscene window1

        Response Example: Command acknowledgment
            wscene2 window close OfficeVW-windowscene window1 success
        """
        command = f"wscene2 window close {videowall}-{wscene} {wname}"
        response = await self.client.send_command(command)
        return require_success_indicator(response, expected_start=f"wscene2 window close {videowall}-{wscene} {wname}")

    async def wscene2_window_change(self, videowall: str, wscene: str, wname: str, tx: str) -> bool:
        """Change the TX for an open window within a 'video wall within a wall' Scene

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            tx: Encoder reference (alias or hostname)

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command is effective immediately and does not save to the default Scene.
            Window names must use names of windows currently open in the Scene.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            TX: Encoder reference – Alias or hostname
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name

        Command structure:
            wscene2 window change <videowall>-<wscene> <wname> <TX>

        Response structure:
            wscene2 window change <videowall>-<wscene> <wname> <TX> [success|failure]

        Command Example: Reposition and resize a window within a scene
            wscene2 window change OfficeVW-windowscene window1 source1

        Response Example: Command acknowledgment
            wscene2 window change OfficeVW-windowscene window1 source1 success
        """
        command = f"wscene2 window change {videowall}-{wscene} {wname} {tx}"
        response = await self.client.send_command(command)
        return require_success_indicator(
            response, expected_start=f"wscene2 window change {videowall}-{wscene} {wname} {tx}"
        )

    async def wscene2_window_adjust(
        self, videowall: str, wscene: str, wname: str, x: int, y: int, h: int, v: int
    ) -> bool:
        """Reposition and resize an open window within a 'video wall within a wall' Scene

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            x: Window's top left decoder horizontal position in display array
            y: Window's top left decoder vertical position in display array
            h: Window's horizontal size in number of displays
            v: Window's vertical size in number of displays

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command is effective immediately and does not save to the default Scene.
            Horizontal and vertical positions are relative to the top left display.
            Window names must use names of windows currently open in the Scene.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            X: Window's top left decoder horizontal position in display array
            Y: Window's top left decoder vertical position in display array
            H: Window's horizontal size in number of displays
            W: Window's vertical size in number of displays

        Command structure:
            wscene2 window adjust <videowall>-<wscene> <wname> <X> <Y> <H> <W>

        Response structure:
            wscene2 window adjust <videowall>-<wscene> <wname> <X> <Y> <H> <W> [success|failure]

        Command Example: Reposition and resize a window within a scene
            wscene2 window adjust OfficeVW-windowscene window1 1 1 2 2

        Response Example: Command acknowledgment
            wscene2 window adjust OfficeVW-windowscene window1 1 1 2 2 success
        """
        command = f"wscene2 window adjust {videowall}-{wscene} {wname} {x} {y} {h} {v}"
        response = await self.client.send_command(command)
        return require_success_indicator(
            response, expected_start=f"wscene2 window adjust {videowall}-{wscene} {wname} {x} {y} {h} {v}"
        )

    async def wscene2_window_move(
        self, videowall: str, wscene: str, wname: str, layer: Literal["up", "down", "top", "bottom"]
    ) -> bool:
        """Change the layer for an open window within a 'video wall within a wall' Scene

        Args:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            layer: Window's layer reference
                up: Move window up one layer
                down: Move window down one layer
                top: Move window to top layer
                bottom: Move window to bottom layer

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-110-RX, NHD-210-RX
            NHD-400-RX, NHD-500-RX
            NHD-600-RX, NHD-600-TRX, NHD-600-TRXF, NHD-610-RX

        Notes:
            Command is effective immediately and does not save to the default Scene.
            Window names must use names of windows currently open in the Scene.
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            videowall: Preconfigured video wall name
            wscene: Preconfigured Scene name
            wname: Unique window name
            layer: Window's layer reference
                up: up
                down: down
                top: top
                bottom: bottom

        Command structure:
            wscene2 window move <videowall>-<wscene> <wname> <layer>

        Response structure:
            wscene2 window move <videowall>-<wscene> <wname> <layer> [success|failure]

        Command Example: Move window to top layer
            wscene2 window move OfficeVW-windowscene window1 top

        Response Example: Command acknowledgment
            wscene2 window move OfficeVW-windowscene window1 top success
        """
        command = f"wscene2 window move {videowall}-{wscene} {wname} {layer}"
        response = await self.client.send_command(command)
        return require_success_indicator(
            response, expected_start=f"wscene2 window move {videowall}-{wscene} {wname} {layer}"
        )
