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
  "titulo" | "periodo_desde" | "periodo_hasta" | "contenido"
>;

export function listarInformes(pacienteId: number): Promise<Informe[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/informes`);
}

export function crearInforme(pacienteId: number, datos: InformeGuardar): Promise<Informe> {
  return solicitar(`/api/pacientes/${pacienteId}/informes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...datos, asistido_ia: false }),
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
