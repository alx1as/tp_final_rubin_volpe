#!/usr/bin/env python3
"""Carga un caso ficticio integral para probar el TFI. Uso exclusivo en PostgreSQL local.

Ejecutar desde backend/:
    .venv/bin/python scripts/cargar_paciente_demo.py --validar
    .venv/bin/python scripts/cargar_paciente_demo.py

No cambia código, no altera registros existentes y hace COMMIT una sola vez.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Permite importar 'app' incluso si se ejecuta el script desde otro directorio.
BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from pydantic import BaseModel, ValidationError
from sqlalchemy.engine import make_url
from sqlmodel import Session, select

from app.core.config import load_settings
from app.db.session import build_engine
from app.models import (
    Admision, Escolaridad, Informe, Objetivo, Observacion, Paciente,
    Profesional, ProfesionalTratante, Sesion,
)
from app.schemas.admision import AdmisionGuardar
from app.schemas.escolaridad import EscolaridadGuardar
from app.schemas.informe import InformeDatos
from app.schemas.objetivo import ObjetivoGuardar
from app.schemas.observacion import ObservacionCrear
from app.schemas.paciente import PacienteCrear
from app.schemas.profesional_tratante import ProfesionalTratanteGuardar
from app.schemas.sesion import SesionCrear

ARCHIVO_JSON = Path(__file__).with_name("paciente_demo.json")


def revisar_datos() -> dict[str, Any]:
    """Valida el caso con los esquemas reales de la API antes de escribir nada."""
    datos = json.loads(ARCHIVO_JSON.read_text(encoding="utf-8"))
    campos = {
        "paciente", "admision", "escolaridades", "profesionales_tratantes",
        "objetivos", "sesiones", "informes",
    }
    if set(datos) != campos:
        raise ValueError(f"Las secciones del JSON deben ser exactamente: {', '.join(sorted(campos))}")

    verificados: dict[str, Any] = {
        "paciente": PacienteCrear.model_validate(datos["paciente"]),
        "admision": AdmisionGuardar.model_validate(datos["admision"]),
        "escolaridades": [EscolaridadGuardar.model_validate(x) for x in datos["escolaridades"]],
        "profesionales_tratantes": [
            ProfesionalTratanteGuardar.model_validate(x)
            for x in datos["profesionales_tratantes"]
        ],
        "objetivos": [],
        "sesiones": [],
        "informes": [InformeDatos.model_validate(x) for x in datos["informes"]],
    }

    claves_objetivos: set[str] = set()
    for entrada in datos["objetivos"]:
        clave = entrada.get("clave")
        if not isinstance(clave, str) or not clave or clave in claves_objetivos:
            raise ValueError(f"Clave de objetivo duplicada o inválida: {clave!r}")
        claves_objetivos.add(clave)
        objetivo = ObjetivoGuardar.model_validate({k: v for k, v in entrada.items() if k != "clave"})
        verificados["objetivos"].append((clave, objetivo))

    for entrada in datos["sesiones"]:
        sesion = SesionCrear.model_validate({k: v for k, v in entrada.items() if k != "observaciones"})
        observaciones: list[tuple[str | None, ObservacionCrear]] = []
        for obs in entrada.get("observaciones", []):
            clave = obs.get("objetivo_clave")
            if clave is not None and clave not in claves_objetivos:
                raise ValueError(f"Una observación hace referencia a un objetivo inexistente: {clave!r}")
            validada = ObservacionCrear.model_validate({k: v for k, v in obs.items() if k != "objetivo_clave"})
            observaciones.append((clave, validada))
        if not sesion.presente and observaciones:
            raise ValueError(f"La sesión ausente del {sesion.fecha} no debe tener observaciones")
        verificados["sesiones"].append((sesion, observaciones))
    return verificados


def elegir_profesional(session: Session, id_solicitado: int | None) -> Profesional:
    profesionales = session.exec(
        select(Profesional).where(Profesional.activo == True).order_by(Profesional.id)  # noqa: E712
    ).all()
    if not profesionales:
        raise ValueError("No hay profesionales activos. Primero registrate desde la aplicación.")

    print("\nCuentas profesionales activas:")
    for profesional in profesionales:
        print(f"  {profesional.id}: {profesional.nombre} {profesional.apellido} ({profesional.email})")
    if id_solicitado is None:
        if len(profesionales) == 1:
            elegido = profesionales[0]
        else:
            entrada = input("ID de tu cuenta profesional para cargar el caso: ").strip()
            if not entrada.isdecimal():
                raise ValueError("Tenés que indicar un ID numérico válido")
            id_solicitado = int(entrada)
            elegido = next((p for p in profesionales if p.id == id_solicitado), None)
    else:
        elegido = next((p for p in profesionales if p.id == id_solicitado), None)

    if elegido is None:
        raise ValueError("No se encontró una cuenta activa con ese ID")
    print(f"\nDestino: profesional {elegido.id} ({elegido.nombre} {elegido.apellido}).")
    return elegido


def cargar(session: Session, datos: dict[str, Any], profesional: Profesional) -> int:
    p: BaseModel = datos["paciente"]
    existente = session.exec(
        select(Paciente).where(
            Paciente.profesional_id == profesional.id,
            Paciente.nombre == p.nombre,
            Paciente.apellido == p.apellido,
            Paciente.fecha_nacimiento == p.fecha_nacimiento,
        )
    ).first()
    if existente:
        raise ValueError(
            f"Martina Demo ya existe para esta cuenta (paciente ID {existente.id}). "
            "No se duplicaron ni modificaron registros."
        )

    paciente = Paciente(profesional_id=profesional.id, **p.model_dump())
    session.add(paciente)
    session.flush()

    session.add(Admision(paciente_id=paciente.id, **datos["admision"].model_dump()))
    for escolaridad in datos["escolaridades"]:
        session.add(Escolaridad(paciente_id=paciente.id, **escolaridad.model_dump()))
    for tratante in datos["profesionales_tratantes"]:
        session.add(ProfesionalTratante(paciente_id=paciente.id, **tratante.model_dump()))

    ids_objetivos: dict[str, int] = {}
    for clave, info in datos["objetivos"]:
        objetivo = Objetivo(paciente_id=paciente.id, **info.model_dump())
        session.add(objetivo)
        session.flush()
        ids_objetivos[clave] = objetivo.id

    for info, observaciones in datos["sesiones"]:
        sesion = Sesion(paciente_id=paciente.id, **info.model_dump())
        session.add(sesion)
        session.flush()
        for clave, info_obs in observaciones:
            session.add(Observacion(
                sesion_id=sesion.id,
                objetivo_id=ids_objetivos[clave] if clave else None,
                **info_obs.model_dump(exclude={"objetivo_id"}),
            ))

    for informe in datos["informes"]:
        session.add(Informe(paciente_id=paciente.id, **informe.model_dump()))
    session.flush()  # Detecta errores antes de hacer el único COMMIT.
    return paciente.id


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga un paciente ficticio completo en PostgreSQL local")
    parser.add_argument("--validar", action="store_true", help="Solo valida el JSON, sin acceder a PostgreSQL")
    parser.add_argument("--profesional-id", type=int, help="Cuenta profesional propietaria del caso")
    args = parser.parse_args()

    datos = revisar_datos()
    cantidad_obs = sum(len(observaciones) for _, observaciones in datos["sesiones"])
    print(
        f"Caso válido: 1 paciente, 1 admisión, {len(datos['escolaridades'])} escolaridades, "
        f"{len(datos['profesionales_tratantes'])} profesionales intervinientes, "
        f"{len(datos['objetivos'])} objetivos, {len(datos['sesiones'])} sesiones, "
        f"{cantidad_obs} observaciones, {len(datos['informes'])} informes."
    )
    if args.validar:
        print("Solo validación: NO se escribió en la base de datos.")
        return

    settings = load_settings()
    host = make_url(settings.database_url.get_secret_value()).host
    if host not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Por seguridad, este cargador solamente funciona con PostgreSQL local")

    engine = build_engine(settings)
    try:
        with Session(engine) as session:
            profesional = elegir_profesional(session, args.profesional_id)
            confirmar = input("Para cargar el paciente ficticio escribí CARGAR: ").strip()
            if confirmar != "CARGAR":
                print("Cancelado. No se realizaron cambios.")
                return
            try:
                paciente_id = cargar(session, datos, profesional)
                session.commit()
            except Exception:
                session.rollback()
                raise
            print(f"\nCarga completa. Paciente: Martina Demo (ID {paciente_id}).")
            print("Abrí la aplicación y buscá 'Demo' entre tus pacientes.")
            print("Para probar Groq: informes → Nuevo → período 2026-04-09 a 2026-11-03 → Generar con IA.")
            print("Los audios y transcripciones NO se modificaron.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, ValidationError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        # Evitamos mostrar credenciales y datos de conexión en errores de SQLAlchemy.
        print(f"No se pudo completar la carga ({type(error).__name__}). No hubo una carga parcial.", file=sys.stderr)
        sys.exit(1)
