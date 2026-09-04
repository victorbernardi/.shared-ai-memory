from __future__ import annotations

from urllib.parse import unquote, urlsplit

import pytest

import bootstrap_jd_supabase as bootstrap


PROJECT_REF = "abcdefghijklmnopqrst"
BASE_URL = (
    "postgresql://postgres."
    + PROJECT_REF
    + "@db-example.pooler.supabase.com:6543/postgres?sslmode=verify-full"
)


def _environment() -> dict[str, str]:
    return {
        "SUPABASE_PUBLISHER_DB_BASE_URL": BASE_URL,
        "SUPABASE_READER_DB_BASE_URL": BASE_URL,
    }


def _records() -> dict[str, bootstrap.CredentialRecord]:
    return {
        bootstrap.PUBLISHER_TARGET: bootstrap.CredentialRecord(
            "SUPABASE_PUBLISHER_DB_PASSWORD", "pub/secret?1"
        ),
        bootstrap.READER_TARGET: bootstrap.CredentialRecord(
            "SUPABASE_READER_DB_PASSWORD", "reader secret#2"
        ),
    }


def test_builds_jd_dsns_from_dedicated_targets_without_mutating_input():
    records = _records()
    environment = _environment()

    configured = bootstrap.build_jd_environment(
        environment,
        credential_reader=records.__getitem__,
    )

    assert "SUPABASE_PUBLISHER_DB_URL" not in environment
    assert "SUPABASE_READER_DB_URL" not in environment
    publisher = urlsplit(configured["SUPABASE_PUBLISHER_DB_URL"])
    reader = urlsplit(configured["SUPABASE_READER_DB_URL"])
    assert publisher.username == f"inova_telemetry_publisher_login.{PROJECT_REF}"
    assert unquote(publisher.password or "") == "pub/secret?1"
    assert reader.username == f"inova_telemetry_reader_login.{PROJECT_REF}"
    assert unquote(reader.password or "") == "reader secret#2"
    assert publisher.geturl() != reader.geturl()


def test_rejects_a_credential_manager_record_with_wrong_username():
    records = _records()
    records[bootstrap.PUBLISHER_TARGET] = bootstrap.CredentialRecord("wrong", "secret")

    with pytest.raises(bootstrap.BootstrapError, match="publisher target"):
        bootstrap.build_jd_environment(
            _environment(),
            credential_reader=records.__getitem__,
        )


def test_rejects_base_url_with_embedded_password():
    environment = _environment()
    environment["SUPABASE_PUBLISHER_DB_BASE_URL"] = (
        BASE_URL.replace("postgres.", "postgres:password@postgres.")
    )

    with pytest.raises(bootstrap.BootstrapError, match="publisher base URL"):
        bootstrap.build_jd_environment(environment, credential_reader=lambda _: None)