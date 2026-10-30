"""SSH host key pinning: fingerprint parsing, and the check against a real paramiko server on loopback."""

import base64
import hashlib
import shutil
import socket
import subprocess  # nosec B404 - runs ssh-keygen on a key file the test wrote
import threading

import paramiko
import pytest

import wyrestorm_networkhd
from wyrestorm_networkhd import HostKeyMismatchError, NetworkHDClientSSH, normalize_fingerprints
from wyrestorm_networkhd.core.client_ssh import _fingerprint
from wyrestorm_networkhd.exceptions import ConnectionError

pytestmark = pytest.mark.unit

ECDSA_KEY = paramiko.ECDSAKey.generate()
RSA_KEY = paramiko.RSAKey.generate(2048)


def openssh_fingerprint(key: paramiko.PKey) -> str:
    return "SHA256:" + base64.b64encode(hashlib.sha256(key.asbytes()).digest()).decode().rstrip("=")


ECDSA_FP = openssh_fingerprint(ECDSA_KEY)
RSA_FP = openssh_fingerprint(RSA_KEY)
OTHER_FP = openssh_fingerprint(paramiko.ECDSAKey.generate())


# ============================================================================
# Fingerprints and parsing
# ============================================================================


def test_fingerprint_matches_ssh_keygen(tmp_path):
    ssh_keygen = shutil.which("ssh-keygen")
    if ssh_keygen is None:
        pytest.skip("ssh-keygen is not installed")
    for key in (ECDSA_KEY, RSA_KEY):
        path = tmp_path / "key.pub"
        path.write_text(f"{key.get_name()} {key.get_base64()} test\n")
        output = subprocess.run([ssh_keygen, "-lf", str(path)], capture_output=True, text=True, check=True).stdout  # nosec B603
        assert output.split()[1] == _fingerprint(key)
        assert normalize_fingerprints(output) == (_fingerprint(key),)


def test_fingerprint_format():
    assert _fingerprint(ECDSA_KEY) == ECDSA_FP
    assert len(ECDSA_FP) == len("SHA256:") + 43 and not ECDSA_FP.endswith("=")


@pytest.mark.parametrize(
    "value",
    [
        ECDSA_FP,
        ECDSA_FP[7:],  # bare base64
        ECDSA_FP + "=",  # padded
        ECDSA_FP[7:] + "=",
        "sha256:" + ECDSA_FP[7:],
        f"  {ECDSA_FP}\n",
        [ECDSA_FP],
        (ECDSA_FP[7:],),
    ],
)
def test_normalize_single(value):
    assert normalize_fingerprints(value) == (ECDSA_FP,)


@pytest.mark.parametrize(
    "value",
    [
        f"{ECDSA_FP},{RSA_FP}",
        f"{ECDSA_FP}, {RSA_FP[7:]}=",
        f"{ECDSA_FP}\n{RSA_FP}\n",
        f"{ECDSA_FP} {RSA_FP} {ECDSA_FP}",  # duplicates removed
        [ECDSA_FP, f"{RSA_FP}\n"],
        f"256 {ECDSA_FP} [device.test]:10022 (ECDSA)\n3072 {RSA_FP} [device.test]:10022 (RSA)\n",
    ],
)
def test_normalize_several(value):
    assert normalize_fingerprints(value) == (ECDSA_FP, RSA_FP)


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   \n",
        [],
        "not a fingerprint",
        "MD5:16:27:ac:a5:76:28:2d:36:63:1b:56:4d:eb:df:a6:48",
        "SHA256:tooshort",
        f"{ECDSA_FP} SHA256:tooshort",  # an explicit SHA256 token must be valid
        ECDSA_FP[7:-1] + "!",  # not base64
        [ECDSA_FP, 42],
    ],
)
def test_normalize_invalid(value):
    with pytest.raises(ValueError):
        normalize_fingerprints(value)


def test_exports():
    assert wyrestorm_networkhd.normalize_fingerprints is normalize_fingerprints
    assert issubclass(HostKeyMismatchError, ConnectionError)


def test_constructor_normalizes_and_validates():
    def make(fingerprints):
        return NetworkHDClientSSH("device.test", 10022, "user", "secret", "reject", host_key_fingerprints=fingerprints)

    assert make(None).host_key_fingerprints is None
    assert make(ECDSA_FP[7:] + "=").host_key_fingerprints == (ECDSA_FP,)
    assert make(None).host_key_fingerprint is None
    with pytest.raises(ValueError):
        make("garbage")


def test_mismatch_message_has_presented_fingerprint_only():
    error = HostKeyMismatchError("[device.test]:10022", OTHER_FP)
    assert error.presented_fingerprint == OTHER_FP
    assert OTHER_FP in str(error) and "does not match" in str(error)


# ============================================================================
# Against a real SSH server
# ============================================================================


class _Server(paramiko.ServerInterface):
    def __init__(self, attempts: list[str]) -> None:
        self.attempts = attempts

    def get_allowed_auths(self, _username):
        return "password"

    def check_auth_password(self, _username, password):
        self.attempts.append(password)
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, _kind, _chanid):
        return paramiko.OPEN_SUCCEEDED

    def check_channel_pty_request(self, *_args):
        return True

    def check_channel_shell_request(self, _channel):
        return True


class SSHServer:
    """A loopback SSH server presenting ``host_keys``; records every password it is sent."""

    def __init__(self, host_keys: list[paramiko.PKey]) -> None:
        self.host_keys = host_keys
        self.passwords: list[str] = []
        self.transports: list[paramiko.Transport] = []
        self.channels: list[paramiko.Channel | None] = []  # kept so they aren't closed by garbage collection
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen()
        self.port = self.sock.getsockname()[1]
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self) -> None:
        while True:
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            transport = paramiko.Transport(conn)
            self.transports.append(transport)
            for key in self.host_keys:
                transport.add_server_key(key)
            try:
                transport.start_server(server=_Server(self.passwords))
            except Exception:  # noqa: BLE001 - the client hung up during the handshake
                continue
            self.channels.append(transport.accept(5))

    def close(self) -> None:
        self.sock.close()
        for transport in self.transports:
            transport.close()

    def client(self, **kwargs) -> NetworkHDClientSSH:
        return NetworkHDClientSSH("127.0.0.1", self.port, "user", "secret", "auto_add", timeout=5.0, **kwargs)


@pytest.fixture
def server():
    servers: list[SSHServer] = []

    def start(*keys: paramiko.PKey) -> SSHServer:
        servers.append(SSHServer(list(keys) or [ECDSA_KEY]))
        return servers[-1]

    yield start
    for s in servers:
        s.close()


@pytest.mark.asyncio
async def test_unpinned_connect_records_fingerprint(server):
    ssh = server()
    client = ssh.client()
    await client.connect()
    try:
        assert client.host_key_fingerprint == ECDSA_FP
        assert ssh.passwords == ["secret"]
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_matching_pin_connects(server):
    ssh = server()
    client = ssh.client(host_key_fingerprints=[OTHER_FP, ECDSA_FP])
    await client.connect()
    try:
        assert client.is_connected()
        assert client.host_key_fingerprint == ECDSA_FP
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_rsa_pin_for_rsa_only_server(server):
    ssh = server(RSA_KEY)
    client = ssh.client(host_key_fingerprints=f"256 {ECDSA_FP} x (ECDSA)\n3072 {RSA_FP} x (RSA)")
    await client.connect()
    try:
        assert client.host_key_fingerprint == RSA_FP
    finally:
        await client.disconnect()


@pytest.mark.asyncio
async def test_mismatch_raises_before_password_is_sent(server):
    ssh = server()
    client = ssh.client(host_key_fingerprints=OTHER_FP)

    with pytest.raises(HostKeyMismatchError) as excinfo:
        await client.connect()

    assert excinfo.value.presented_fingerprint == ECDSA_FP
    assert ECDSA_FP in str(excinfo.value) and "secret" not in str(excinfo.value)
    assert ssh.passwords == []
    assert not client.is_connected()
    assert client.get_connection_state() == "error"
    assert client.host_key_fingerprint is None


@pytest.mark.asyncio
async def test_pin_overrides_reject_policy(server):
    ssh = server()
    client = NetworkHDClientSSH(
        "127.0.0.1", ssh.port, "user", "secret", "reject", timeout=5.0, host_key_fingerprints=ECDSA_FP
    )
    await client.connect()
    await client.disconnect()
    assert ssh.passwords == ["secret"]


@pytest.mark.asyncio
async def test_unpinned_reject_policy_unchanged(server):
    ssh = server()
    client = NetworkHDClientSSH("127.0.0.1", ssh.port, "user", "secret", "reject", timeout=5.0)
    with pytest.raises(ConnectionError, match="not found in known_hosts"):
        await client.connect()
    assert ssh.passwords == []


@pytest.mark.asyncio
async def test_reconnect_does_not_retry_mismatch(server):
    ssh = server()
    client = ssh.client(host_key_fingerprints=OTHER_FP)

    with pytest.raises(HostKeyMismatchError):
        await client.reconnect(max_attempts=3, delay=0.001)

    assert len(ssh.transports) == 1
    assert ssh.passwords == []


@pytest.mark.asyncio
async def test_pinning_existing_client_applies_on_next_connect(server):
    ssh = server()
    client = ssh.client()
    await client.connect()
    await client.disconnect()
    assert client.host_key_fingerprint == ECDSA_FP

    client.host_key_fingerprints = normalize_fingerprints(OTHER_FP)
    with pytest.raises(HostKeyMismatchError):
        await client.connect()

    assert ssh.passwords == ["secret"]  # only the first, unpinned connect sent it
    assert client.host_key_fingerprint == ECDSA_FP
