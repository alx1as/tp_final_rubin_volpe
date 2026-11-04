#!/usr/bin/env python3
"""Revisa sesiones de un paciente para un periodo. SOLO LECTURA: no agrega ni cambia datos.

Ejemplo desde la raiz del repositorio:
  backend/.venv/bin/python backend/scripts/diagnosticar_informes.py --paciente 6 --desde 2026-05-06 --hasta 2026-11-04
"""

import argparse
import sys
from datetime import date
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from sqlmodel import Session, select
from app.core.config import load_settings
from app.db.session import build_engine
from app.models import Paciente, Sesion
from app.schemas.integraciones import SolicitudBorrador
from app.services.generacion import recopilar_contexto


def main():
    parser = argparse.ArgumentParser(description="Diagnostico de fechas y sesiones para informes")
    parser.add_argument("--paciente", type=int, required=True)
    parser.add_argument("--desde", type=date.fromisoformat, required=True)
    parser.add_argument("--hasta", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    if args.hasta < args.desde:
        parser.error("El periodo hasta no puede ser anterior a desde")

    engine = build_engine(load_settings())
    try:
        with Session(engine) as session:
            paciente = session.get(Paciente, args.paciente)
            if paciente is None:
                print(f"Paciente {args.paciente}: no existe en esta base de datos")
                return

            fechas = session.exec(select(Sesion.fecha).where(
                Sesion.paciente_id == args.paciente
            ).order_by(Sesion.fecha)).all()
            coincidentes = [fecha for fecha in fechas if args.desde <= fecha <= args.hasta]
            solicitud = SolicitudBorrador(
                titulo="Diagnostico (sin generar ni guardar)",
                periodo_desde=args.desde,
                periodo_hasta=args.hasta,
            )
            contexto = recopilar_contexto(session, paciente, solicitud)
            print(f"Paciente ID: {args.paciente}")
            print(f"Sesiones totales en PostgreSQL: {len(fechas)}")
            print(f"Sesiones dentro del periodo: {len(coincidentes)}")
            print(f"Sesiones recibidas por el generador: {len(contexto.sesiones)}")
            if fechas:
                print(f"Primera / ultima: {fechas[0]} / {fechas[-1]}")
            print("Fechas en el periodo: " + (", ".join(map(str, coincidentes)) or "ninguna"))
            if len(coincidentes) != len(contexto.sesiones):
                print("ATENCION: la consulta del generador no coincide con las sesiones guardadas")
            elif not coincidentes:
                print("Las sesiones no estan cargadas en esta base para estas fechas o pertenecen a otro paciente")
            else:
                print("La consulta a PostgreSQL devuelve sesiones correctamente")
    finally:
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # No imprimir trazas que puedan incluir datos de conexion.
        print(f"Error en el diagnostico: {type(error).__name__}", file=sys.stderr)
        sys.exit(1)
