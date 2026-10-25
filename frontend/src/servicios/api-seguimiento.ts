import { solicitar, solicitarListaCompleta } from "./api";

// Las sesiones son encuentros clínicos, no sesiones de autenticación.
export type Sesion = {
  id: number;
  paciente_id: number;
  fecha: string;
  presente: boolean;
  nota_general: string | null;
};
export type SesionGuardar = Pick<Sesion, "fecha" | "presente" | "nota_general">;

export type Observacion = {
  id: number;
  sesion_id: number;
  objetivo_id: number | null;
  contexto: string | null;
  conducta_observable: string | null;
  intervencion: string | null;
  resultado: string | null;
  nota_libre: string | null;
};
export type ObservacionGuardar = Omit<Observacion, "id" | "sesion_id">;
export type EvidenciaObjetivo = Observacion & { fecha_sesion: string };

function cuerpoJson(datos: unknown): RequestInit {
  return {
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  };
}

export function listarSesiones(pacienteId: number): Promise<Sesion[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/sesiones`);
}

export function guardarSesion(
  pacienteId: number, datos: SesionGuardar, sesionId?: number
): Promise<Sesion> {
  const ruta = `/api/pacientes/${pacienteId}/sesiones` +
    (sesionId === undefined ? "" : `/${sesionId}`);
  return solicitar(ruta, {
    method: sesionId === undefined ? "POST" : "PATCH",
    ...cuerpoJson(datos),
  });
}

export function listarObservaciones(pacienteId: number, sesionId: number): Promise<Observacion[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/sesiones/${sesionId}/observaciones`);
}

export function guardarObservacion(
  pacienteId: number, sesionId: number, datos: ObservacionGuardar, observacionId?: number
): Promise<Observacion> {
  const ruta = `/api/pacientes/${pacienteId}/sesiones/${sesionId}/observaciones` +
    (observacionId === undefined ? "" : `/${observacionId}`);
  return solicitar(ruta, {
    method: observacionId === undefined ? "POST" : "PATCH",
    ...cuerpoJson(datos),
  });
}

export function listarEvidenciasObjetivo(pacienteId: number, objetivoId: number): Promise<EvidenciaObjetivo[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/objetivos/${objetivoId}/observaciones`);
}
