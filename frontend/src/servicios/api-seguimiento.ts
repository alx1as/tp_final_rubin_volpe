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

// Solo propone una distribución; la observación se guarda con guardarObservacion.
export type SugerenciaObservacion = Pick<ObservacionGuardar,
  "contexto" | "conducta_observable" | "intervencion" | "resultado" | "nota_libre">;

export function organizarNotaConIA(
  pacienteId: number, texto: string
): Promise<SugerenciaObservacion> {
  return solicitar(`/api/pacientes/${pacienteId}/observaciones/organizar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
}

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

/** La API pagina por sesión y devuelve cada sesión con sus observaciones. */
export type EntradaCronologia = Sesion & { observaciones: Observacion[] };

export function listarCronologia(pacienteId: number, mes: string): Promise<EntradaCronologia[]> {
  if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(mes)) {
    return Promise.reject(new Error("El mes seleccionado no es válido."));
  }
  const [anio, numeroMes] = mes.split("-").map(Number);
  const ultimoDia = new Date(anio, numeroMes, 0).getDate();
  const desde = `${mes}-01`;
  const hasta = `${mes}-${String(ultimoDia).padStart(2, "0")}`;
  return solicitarListaCompleta<EntradaCronologia>(
    `/api/pacientes/${pacienteId}/cronologia?desde=${desde}&hasta=${hasta}`
  );
}

/** Registro compuesto: una sola transacción en el backend. */
export type ObservacionEnRegistro = ObservacionGuardar & { id?: number };
export type RegistroSesionGuardar = SesionGuardar & {
  observaciones: ObservacionEnRegistro[];
  observaciones_eliminar: number[];
};
export type RegistroSesionRespuesta = {
  sesion: Sesion;
  observaciones: Observacion[];
};

export function guardarRegistroSesion(
  pacienteId: number, datos: RegistroSesionGuardar, sesionId?: number
): Promise<RegistroSesionRespuesta> {
  const ruta = `/api/pacientes/${pacienteId}/sesiones` +
    (sesionId === undefined ? "/completa" : `/${sesionId}/completa`);
  return solicitar(ruta, {
    method: sesionId === undefined ? "POST" : "PATCH",
    ...cuerpoJson(datos),
  });
}

export type RegistroAsistido = {
  nota_general: string | null;
  observaciones: ObservacionGuardar[];
};

export function organizarRegistroConIA(pacienteId: number, texto: string): Promise<RegistroAsistido> {
  return solicitar(`/api/pacientes/${pacienteId}/observaciones/organizar-registro`, {
    method: "POST",
    ...cuerpoJson({ texto }),
  });
}
