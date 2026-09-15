#!/usr/bin/env python
"""Container bootstrap: wait for Postgres, migrate, collectstatic, optional seed."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from urllib.parse import urlparse


def wait_for_postgres(database_url: str, timeout: int = 60) -> None:
    if not database_url.startswith("postgres"):
        print("DATABASE_URL is not postgres; skipping wait.")
        return

    import psycopg2

    parsed = urlparse(database_url)
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            conn = psycopg2.connect(
                dbname=(parsed.path or "/postgres").lstrip("/") or "postgres",
                user=parsed.username,
                password=parsed.password,
                host=parsed.hostname,
                port=parsed.port or 5432,
            )
            conn.close()
            print("PostgreSQL is ready.")
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            print(f"Postgres not ready yet: {exc}")
            time.sleep(2)

    raise SystemExit(f"Timed out waiting for PostgreSQL: {last_error}")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    wait_for_postgres(os.environ.get("DATABASE_URL", ""))
    run([sys.executable, "manage.py", "migrate", "--noinput"])
    run([sys.executable, "manage.py", "collectstatic", "--noinput"])

    if os.environ.get("RUN_SEED", "True").lower() in {"1", "true", "yes"}:
        try:
            run([sys.executable, "manage.py", "seed_demo"])
        except subprocess.CalledProcessError as exc:
            print(f"seed_demo failed (continuing): {exc}")

    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
    raise SystemExit("No command provided to entrypoint.")


if __name__ == "__main__":
    main()
