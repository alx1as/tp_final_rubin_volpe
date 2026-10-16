"""Recorrido HTTP real con Uvicorn y un cluster PostgreSQL temporal exclusivo."""

import os
from pathlib import Path
import socket
import subprocess
import sys
from time import monotonic, sleep

import httpx
import psycopg
import pytest

OK = {"estado": "ok", "postgresql": "conectado"}
UNAVAILABLE = {"estado": "error", "postgresql": "no_disponible"}


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def managed_postgres(tmp_path):
    configured_bin = os.environ.get("POSTGRES_BIN")
    if not configured_bin:
        pytest.skip("Configurar POSTGRES_BIN para probar parada y recuperación real")
    binary_dir = Path(configured_bin).resolve()
    suffix = ".exe" if sys.platform == "win32" else ""

    def binary(name):
        path = binary_dir / (name + suffix)
        if not path.is_file():
            pytest.fail(f"No existe {name} en POSTGRES_BIN")
        return str(path)

    # El directorio lo crea pytest; nunca recibe un PGDATA externo.
    data = tmp_path / "data"
    port = free_port()

    def run(command):
        # En Windows postgres puede heredar una tubería de pg_ctl y mantenerla
        # abierta después de que pg_ctl termine. Un archivo evita ese bloqueo.
        with (tmp_path / "commands.log").open("w+", encoding="utf-8") as output:
            result = subprocess.run(
                command, stdout=output, stderr=subprocess.STDOUT, timeout=45,
            )
            if result.returncode:
                output.seek(0)
                pytest.fail(f"Falló {Path(command[0]).name}: {output.read()}")

    run([binary("initdb"), "-D", str(data), "-U", "e1_test", "-A", "trust",
         "--encoding=UTF8", "--locale=C", "--no-sync"])

    class Cluster:
        running = False
        url = f"postgresql+psycopg://e1_test@127.0.0.1:{port}/seguimiento_e1_test"
        conninfo = f"host=127.0.0.1 port={port} user=e1_test dbname=seguimiento_e1_test connect_timeout=3"

        def start(self):
            run([binary("pg_ctl"), "-D", str(data), "-l", str(tmp_path / "postgres.log"),
                 "-o", f"-h 127.0.0.1 -p {port} -c max_connections=20 -c shared_buffers=16MB",
                 "-w", "-t", "15", "start"])
            self.running = True

        def stop(self):
            run([binary("pg_ctl"), "-D", str(data), "-m", "fast", "-w", "-t", "15", "stop"])
            self.running = False

    cluster = Cluster()
    try:
        cluster.start()
        run([binary("createdb"), "-h", "127.0.0.1", "-p", str(port), "-U", "e1_test",
             "seguimiento_e1_test"])
        cluster.stop()
        yield cluster
    finally:
        if cluster.running:
            cluster.stop()


@pytest.mark.integration
def test_uvicorn_starts_with_database_down_and_recovers_without_restart(managed_postgres, tmp_path):
    cluster = managed_postgres
    port = free_port()
    backend = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["DATABASE_URL"] = cluster.url
    with (tmp_path / "uvicorn.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:create_app", "--factory",
             "--app-dir", str(backend), "--host", "127.0.0.1", "--port", str(port)],
            env=environment, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=15, trust_env=False) as client:
                deadline = monotonic() + 15
                while True:
                    assert process.poll() is None, "Uvicorn no pudo iniciar"
                    try:
                        assert client.get("/docs").status_code == 200
                        break
                    except httpx.ConnectError:
                        if monotonic() >= deadline:
                            pytest.fail("Uvicorn no respondió dentro del plazo")
                        sleep(0.1)
                original_pid = process.pid
                assert client.get("/openapi.json").status_code == 200

                def check_health(code, body):
                    response = client.get("/api/salud")
                    assert response.status_code == code
                    assert response.json() == body
                    assert process.pid == original_pid and process.poll() is None

                check_health(503, UNAVAILABLE)
                cluster.start()
                check_health(200, OK)
                cluster.stop()
                check_health(503, UNAVAILABLE)
                cluster.start()
                check_health(200, OK)
                with psycopg.connect(cluster.conninfo) as connection:
                    assert connection.execute(
                        "SELECT count(*) FROM pg_tables WHERE schemaname='public'"
                    ).fetchone() == (0,)
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
