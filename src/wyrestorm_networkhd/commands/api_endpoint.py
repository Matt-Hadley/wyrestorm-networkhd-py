from typing import Literal

from ._response_helpers import require_command_mirror


class APIEndpointCommands:
    def __init__(self, client):
        self.client = client

    # =============================================================
    # 4.1 Session Alias Mode
    # For the API session (Telnet or RS-232), the command responses or notifications from the NHD-CTL can reference either the
    # endpoint Hostname or Alias. For each new Telnet session, or after the NHD-CTL is rebooted, the default mode is applied.
    # =============================================================

    async def config_set_session_alias(self, mode: Literal["on", "off"]) -> bool:
        """Configure Alias mode for API responses or notifications from NHD-CTL

        Args:
            mode: Alias mode setting
                on: API responses and notifications will reference the endpoint by Alias
                off: API responses and notifications will reference the endpoint by hostname

        Returns:
            bool: True if command was successful

        Command applies to:
            NHD-000-CTL, NHD-CTL-PRO

        Notes:
            New session default: on
        """
        """NetworkHDReferenceAPI
        Command/response definitions:
            on: API responses and notifications will reference the endpoint by Alias
            off: API responses and notifications will reference the endpoint by hostname

        Command structure:
            config set session alias [on|off]

        Response structure (command mirror):
            config set session alias [on|off]

        Command Example: Session to use hostname referencing
            config set session alias off

        Response Example: Command acknowledgment
            config set session alias off
        """
        command = f"config set session alias {mode}"
        response = await self.client.send_command(command)
        return require_command_mirror(response, command)
