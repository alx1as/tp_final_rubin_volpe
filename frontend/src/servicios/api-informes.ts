import { solicitar, solicitarListaCompleta } from "./api";

export type EstadoInforme = "borrador" | "finalizado";

export type Informe = {
  id: number;
  paciente_id: number;
  titulo: string;
  fecha: string;
  periodo_desde: string;
  periodo_hasta: string;
  contenido: string;
  estado: EstadoInforme;
  asistido_ia: boolean;
};

export type InformeGuardar = Pick<
  Informe,
  "titulo" | "periodo_desde" | "periodo_hasta" | "contenido" | "asistido_ia"
>;

export function listarInformes(pacienteId: number): Promise<Informe[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/informes`);
}

export function crearInforme(pacienteId: number, datos: InformeGuardar): Promise<Informe> {
  return solicitar(`/api/pacientes/${pacienteId}/informes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

export function editarInforme(
  pacienteId: number,
  informeId: number,
  cambios: Partial<InformeGuardar> & { estado?: EstadoInforme }
): Promise<Informe> {
  return solicitar(`/api/pacientes/${pacienteId}/informes/${informeId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cambios),
  });
}

// Solo genera un borrador temporal: no se persiste hasta que el profesional lo revise.
export type SolicitudInformeIA = Pick<Informe, "titulo" | "periodo_desde" | "periodo_hasta">;

export function generarBorradorIA(
  pacienteId: number, datos: SolicitudInformeIA
): Promise<InformeGuardar> {
  return solicitar(`/api/pacientes/${pacienteId}/informes/generar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}
