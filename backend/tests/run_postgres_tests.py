"""Ejecuta pytest en un cluster PostgreSQL temporal exclusivo, nunca en .env.

POSTGRES_BIN debe contener los binarios de PostgreSQL. Los argumentos se pasan
a pytest. Conserva los temporales para diagnóstico y detiene solo su cluster.
"""

import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile


def main():
    binaries = Path(os.environ["POSTGRES_BIN"]).resolve()
    suffix = ".exe" if sys.platform == "win32" else ""
    for name in ("initdb", "pg_ctl", "createdb"):
        if not (binaries / (name + suffix)).is_file():
            raise SystemExit(f"No existe {name} en POSTGRES_BIN")
    base = Path(tempfile.mkdtemp(prefix="auth-tests-"))
    data = base / "data"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    def run_pg(name, *args):
        log = base / (name + ".log")
        with log.open("w", encoding="utf-8") as output:
            result = subprocess.run(
                [str(binaries / (name + suffix)), *args],
                stdout=output, stderr=subprocess.STDOUT, timeout=60,
            )
        if result.returncode:
            raise RuntimeError(f"Falló {name}; revisar {log}")

    try:
        run_pg("initdb", "-D", str(data), "-U", "auth_test", "-A", "trust",
               "--encoding=UTF8", "--locale=C", "--no-sync")
        run_pg("pg_ctl", "-D", str(data), "-l", str(base / "postgres.log"),
               "-o", f"-h 127.0.0.1 -p {port} -c max_connections=30 -c shared_buffers=16MB",
               "-w", "-t", "15", "start")
        run_pg("createdb", "-h", "127.0.0.1", "-p", str(port), "-U", "auth_test", "seguimiento_auth_test")
        environment = os.environ.copy()
        environment["TEST_DATABASE_URL"] = f"postgresql+psycopg://auth_test@127.0.0.1:{port}/seguimiento_auth_test"
        environment["POSTGRES_BIN"] = str(binaries)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-c", "backend/pytest.ini", "-q",
             "-p", "no:cacheprovider", "--basetemp=" + str(base / "pytest"), *sys.argv[1:]],
            cwd=Path(__file__).resolve().parents[2], env=environment,
        )
        return result.returncode
    finally:
        if (data / "postmaster.pid").exists():
            run_pg("pg_ctl", "-D", str(data), "-m", "fast", "-w", "-t", "15", "stop")
        print(f"Temporales de pruebas: {base}")


if __name__ == "__main__":
    sys.exit(main())
