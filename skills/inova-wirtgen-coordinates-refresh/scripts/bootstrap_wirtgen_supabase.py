from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, Mapping
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit


PUBLISHER_BASE_ENV = "SUPABASE_WIRTGEN_TELEMETRY_PUBLISHER_DB_BASE_URL"
READER_BASE_ENV = "SUPABASE_WIRTGEN_TELEMETRY_READER_DB_BASE_URL"
PUBLISHER_ENV = "SUPABASE_WIRTGEN_TELEMETRY_PUBLISHER_DB_URL"
READER_ENV = "SUPABASE_WIRTGEN_TELEMETRY_READER_DB_URL"

PUBLISHER_TARGET = "Inova-Supabase-Wirtgen-Telemetry-Publisher"
READER_TARGET = "Inova-Supabase-Wirtgen-Telemetry-Reader"
MACHINE_ANALYZER_TARGET = "Inova-Wirtgen-Machine-Analyzer"
PUBLISHER_RECORD_USERNAME = "SUPABASE_WIRTGEN_TELEMETRY_PUBLISHER_DB_PASSWORD"
READER_RECORD_USERNAME = "SUPABASE_WIRTGEN_TELEMETRY_READER_DB_PASSWORD"
PUBLISHER_LOGIN = "inova_wirtgen_telemetry_publisher_login"
READER_LOGIN = "inova_wirtgen_telemetry_reader_login"
MACHINE_ANALYZER_USER_ENV = "WIRTGEN_DEERE_USER"
MACHINE_ANALYZER_PASSWORD_ENV = "WIRTGEN_DEERE_PASSWORD"

_ALLOWED_SCHEMES = frozenset({"postgres", "postgresql"})
_ALLOWED_PORTS = frozenset({5432, 6543})
_ALLOWED_SSLMODES = frozenset({"require", "verify-ca", "verify-full"})
_ALLOWED_QUERY_KEYS = frozenset(
    {
        "sslmode",
        "application_name",
        "connect_timeout",
        "target_session_attrs",
        "keepalives",
        "keepalives_idle",
        "keepalives_interval",
        "keepalives_count",
        "gssencmode",
        "channel_binding",
    }
)
_PROJECT_REF_RE = re.compile(r"^[a-z0-9]{20}$")
_POOLER_HOST_RE = re.compile(r"^[a-z0-9-]+\.pooler\.supabase\.com$")


class BootstrapError(RuntimeError):
    """Raised when Wirtgen Supabase credentials cannot be prepared safely."""


@dataclass(frozen=True, repr=False)
class CredentialRecord:
    user_name: str
    secret: str

    def __repr__(self) -> str:
        return f"CredentialRecord(user_name={self.user_name!r}, secret=<redacted>)"


@dataclass(frozen=True)
class _Endpoint:
    scheme: str
    hostname: str
    port: int
    project_ref: str
    query: tuple[tuple[str, str], ...]


class _Credential(ctypes.Structure):
    _fields_ = [
        ("Flags", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
        ("TargetName", ctypes.wintypes.LPWSTR),
        ("Comment", ctypes.wintypes.LPWSTR),
        ("LastWritten", ctypes.wintypes.FILETIME),
        ("CredentialBlobSize", ctypes.wintypes.DWORD),
        ("CredentialBlob", ctypes.c_void_p),
        ("Persist", ctypes.wintypes.DWORD),
        ("AttributeCount", ctypes.wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", ctypes.wintypes.LPWSTR),
        ("UserName", ctypes.wintypes.LPWSTR),
    ]


def _decode_secret(blob: bytes) -> str:
    if not blob:
        return ""
    try:
        if len(blob) % 2 == 0 and b"\x00" in blob[1::2]:
            return blob.decode("utf-16-le").rstrip("\x00")
        return blob.decode("utf-8").rstrip("\x00")
    except UnicodeDecodeError as error:
        raise BootstrapError("Credential Manager secret encoding is invalid") from error


def read_windows_credential(target: str) -> CredentialRecord:
    """Read one generic Windows credential without exposing its secret."""
    if os.name != "nt":
        raise BootstrapError("Credential Manager bootstrap is available only on Windows")

    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    cred_read = advapi32.CredReadW
    cred_read.argtypes = [
        ctypes.wintypes.LPWSTR,
        ctypes.wintypes.DWORD,
        ctypes.wintypes.DWORD,
        ctypes.POINTER(ctypes.POINTER(_Credential)),
    ]
    cred_read.restype = ctypes.wintypes.BOOL
    cred_free = advapi32.CredFree
    cred_free.argtypes = [ctypes.c_void_p]
    cred_free.restype = ctypes.wintypes.DWORD

    pointer = ctypes.POINTER(_Credential)()
    if not cred_read(target, 1, 0, ctypes.byref(pointer)):
        raise BootstrapError(f"Could not read Credential Manager target: {target}")
    try:
        record = pointer.contents
        blob = ctypes.string_at(record.CredentialBlob, record.CredentialBlobSize)
        secret = _decode_secret(blob)
        if not secret:
            raise BootstrapError(f"Credential Manager target has no secret: {target}")
        return CredentialRecord(record.UserName or "", secret)
    finally:
        cred_free(pointer)


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise BootstrapError(f"Missing required environment variable: {name}")
    return value


def _parse_query(name: str, query: str) -> tuple[tuple[str, str], ...]:
    pairs = tuple(parse_qsl(query, keep_blank_values=True))
    if not pairs or any(key not in _ALLOWED_QUERY_KEYS for key, _ in pairs):
        raise BootstrapError(f"Invalid query in {name}")
    sslmodes = [value.lower() for key, value in pairs if key == "sslmode"]
    if len(sslmodes) != 1 or sslmodes[0] not in _ALLOWED_SSLMODES:
        raise BootstrapError(f"TLS sslmode is required in {name}")
    return pairs


def _parse_base_url(name: str, value: str) -> _Endpoint:
    role = "publisher" if name == PUBLISHER_BASE_ENV else "reader"
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise BootstrapError(f"Invalid {role} base URL: {name}") from error

    username = parsed.username or ""
    project_ref = username.removeprefix("postgres.")
    if (
        parsed.scheme.lower() not in _ALLOWED_SCHEMES
        or not hostname
        or not _POOLER_HOST_RE.fullmatch(hostname.lower())
        or port not in _ALLOWED_PORTS
        or parsed.password is not None
        or parsed.path != "/postgres"
        or parsed.fragment
        or username != f"postgres.{project_ref}"
        or not _PROJECT_REF_RE.fullmatch(project_ref)
    ):
        raise BootstrapError(f"Invalid {role} base URL: {name}")
    return _Endpoint(
        scheme=parsed.scheme.lower(),
        hostname=hostname.lower(),
        port=port,
        project_ref=project_ref,
        query=_parse_query(name, parsed.query),
    )


def _parse_runtime_dsn(name: str, value: str, expected_login: str) -> None:
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as error:
        raise BootstrapError(f"Invalid runtime DSN: {name}") from error
    username = parsed.username or ""
    prefix = f"{expected_login}."
    project_ref = username.removeprefix(prefix)
    if (
        parsed.scheme.lower() not in _ALLOWED_SCHEMES
        or not hostname
        or not _POOLER_HOST_RE.fullmatch(hostname.lower())
        or port not in _ALLOWED_PORTS
        or not parsed.password
        or parsed.path != "/postgres"
        or parsed.fragment
        or not username.startswith(prefix)
        or not _PROJECT_REF_RE.fullmatch(project_ref)
    ):
        raise BootstrapError(f"Invalid runtime DSN: {name}")
    _parse_query(name, parsed.query)


def _expected_record(
    target: str,
    expected_username: str,
    reader: Callable[[str], CredentialRecord],
    label: str,
) -> CredentialRecord:
    try:
        record = reader(target)
    except BootstrapError:
        raise
    except Exception as error:
        raise BootstrapError(f"Could not read {label} target") from error
    if not isinstance(record, CredentialRecord) or record.user_name != expected_username:
        raise BootstrapError(f"Unexpected username in {label} target")
    if not record.secret:
        raise BootstrapError(f"Empty secret in {label} target")
    return record


def _ensure_machine_analyzer_environment(
    environment: dict[str, str],
    reader: Callable[[str], CredentialRecord],
) -> None:
    current_user = environment.get(MACHINE_ANALYZER_USER_ENV, "").strip()
    current_password = environment.get(MACHINE_ANALYZER_PASSWORD_ENV, "")
    if current_user or current_password:
        if not current_user or not current_password:
            raise BootstrapError(
                "Both Machine Analyzer credentials are required together"
            )
        return

    try:
        record = reader(MACHINE_ANALYZER_TARGET)
    except BootstrapError:
        raise
    except Exception as error:
        raise BootstrapError("Could not read Machine Analyzer credential target") from error
    if not isinstance(record, CredentialRecord) or not record.user_name:
        raise BootstrapError("Machine Analyzer credential target has no username")
    if not record.secret:
        raise BootstrapError("Machine Analyzer credential target has no password")
    environment[MACHINE_ANALYZER_USER_ENV] = record.user_name
    environment[MACHINE_ANALYZER_PASSWORD_ENV] = record.secret


def _compose_dsn(endpoint: _Endpoint, login: str, secret: str) -> str:
    user = quote(f"{login}.{endpoint.project_ref}", safe="")
    password = quote(secret, safe="")
    query = urlencode(endpoint.query)
    return urlunsplit(
        (
            endpoint.scheme,
            f"{user}:{password}@{endpoint.hostname}:{endpoint.port}",
            "/postgres",
            query,
            "",
        )
    )


def build_wirtgen_environment(
    environ: Mapping[str, str],
    *,
    credential_reader: Callable[[str], CredentialRecord] | None = None,
) -> dict[str, str]:
    """Return a child environment with Wirtgen DSNs and no parent mutation."""
    result = dict(environ)
    reader = credential_reader or read_windows_credential
    full_values = (result.get(PUBLISHER_ENV, "").strip(), result.get(READER_ENV, "").strip())
    if any(full_values):
        if not all(full_values):
            raise BootstrapError("Both Wirtgen runtime DSNs are required together")
        _parse_runtime_dsn(PUBLISHER_ENV, full_values[0], PUBLISHER_LOGIN)
        _parse_runtime_dsn(READER_ENV, full_values[1], READER_LOGIN)
        if full_values[0] == full_values[1]:
            raise BootstrapError("Wirtgen publisher and reader DSNs must differ")
        _ensure_machine_analyzer_environment(result, reader)
        return result

    publisher_endpoint = _parse_base_url(
        PUBLISHER_BASE_ENV,
        _required(result, PUBLISHER_BASE_ENV),
    )
    reader_endpoint = _parse_base_url(READER_BASE_ENV, _required(result, READER_BASE_ENV))
    if publisher_endpoint != reader_endpoint:
        raise BootstrapError("Wirtgen publisher and reader base URLs must match")

    publisher_record = _expected_record(
        PUBLISHER_TARGET,
        PUBLISHER_RECORD_USERNAME,
        reader,
        "publisher",
    )
    reader_record = _expected_record(
        READER_TARGET,
        READER_RECORD_USERNAME,
        reader,
        "reader",
    )
    result[PUBLISHER_ENV] = _compose_dsn(
        publisher_endpoint,
        PUBLISHER_LOGIN,
        publisher_record.secret,
    )
    result[READER_ENV] = _compose_dsn(
        reader_endpoint,
        READER_LOGIN,
        reader_record.secret,
    )
    if result[PUBLISHER_ENV] == result[READER_ENV]:
        raise BootstrapError("Wirtgen publisher and reader DSNs must differ")
    _ensure_machine_analyzer_environment(result, reader)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a child command with Wirtgen Supabase DSNs bootstrapped in memory."
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = list(args.command)
    if command[:1] == ["--"]:
        command.pop(0)
    if not command:
        parser.error("a child command is required after --")

    try:
        child_environment = build_wirtgen_environment(os.environ)
    except BootstrapError as error:
        print(f"status=blocked error={error}", file=sys.stderr)
        return 2

    print("status=credentials_configured")
    try:
        return subprocess.run(command, env=child_environment, check=False).returncode
    except OSError as error:
        print(f"status=blocked error=child command could not start: {error.__class__.__name__}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
