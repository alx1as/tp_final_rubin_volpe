import type { Paciente } from "../modulos/pacientes/Pacientes";
import type { Admision } from "../modulos/pacientes/AdmisionPaciente";
import type { Escolaridad, EscolaridadGuardar } from "../modulos/pacientes/EscolaridadPaciente";
import type { ProfesionalTratante, ProfesionalTratanteGuardar } from "../modulos/pacientes/ProfesionalesIntervinientes";
import type { Objetivo, ObjetivoGuardar } from "../modulos/pacientes/ObjetivosPaciente";

/* Cliente HTTP compartido: las solicitudes viajan con la cookie de sesión.
En desarrollo, Vite redirige /api al backend para evitar mezclar hosts. */
export type SaludAPI = {
  estado: "ok" | "error";
  postgresql: "conectado" | "no_disponible";
};

export type ProfesionalAutenticado = {
  id: number;
  nombre: string;
  apellido: string;
  email: string;
  activo: boolean;
};

export type RegistroProfesional = {
  nombre: string;
  apellido: string;
  email: string;
  password: string;
};

type Pagina<T> = {
  items: T[];
  total: number;
  offset: number;
  limit: number;
};

// Para producción se puede definir VITE_API_URL; localmente usamos el proxy de Vite.
const API_URL = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

export class ErrorAPI extends Error {
  status: number;

  constructor(status: number, mensaje: string) {
    super(mensaje);
    this.name = "ErrorAPI";
    this.status = status;
  }
}

export async function solicitar<T>(
  ruta: string,
  opciones: RequestInit = {},
  avisarSesionVencida = true
): Promise<T> {
  const respuesta = await fetch(`${API_URL}${ruta}`, {
    ...opciones,
    credentials: "include",
  });

  if (!respuesta.ok) {
    if (respuesta.status === 401 && avisarSesionVencida) {
      window.dispatchEvent(new Event("sesion-vencida"));
    }
    const datos = await respuesta.json().catch(() => null);
    const detalle = datos?.detail;
    const mensaje = typeof detalle === "string"
      ? detalle
      : respuesta.status === 422
        ? "Revisá los datos ingresados."
        : `Error HTTP ${respuesta.status}`;
    throw new ErrorAPI(respuesta.status, mensaje);
  }

  if (respuesta.status === 204) return undefined as T;
  return (await respuesta.json()) as T;
}

export async function solicitarListaCompleta<T>(ruta: string): Promise<T[]> {
  const todos: T[] = [];
  const limite = 100; // Máximo que admite el backend por página.
  let offset = 0;

  while (true) {
    const separador = ruta.includes("?") ? "&" : "?";
    const pagina = await solicitar<Pagina<T>>(
      `${ruta}${separador}offset=${offset}&limit=${limite}`
    );
    todos.push(...pagina.items);
    offset += pagina.items.length;
    if (offset >= pagina.total || pagina.items.length === 0) break;
  }
  return todos;
}

export async function consultarSalud(): Promise<SaludAPI> {
  const respuesta = await fetch(`${API_URL}/api/salud`);
  if (respuesta.status !== 200 && respuesta.status !== 503) {
    throw new Error(`Error HTTP ${respuesta.status}`);
  }
  return (await respuesta.json()) as SaludAPI;
}

export async function obtenerSesionActual(): Promise<ProfesionalAutenticado | null> {
  try {
    return await solicitar<ProfesionalAutenticado>("/api/auth/me", {}, false);
  } catch (error) {
    if (error instanceof ErrorAPI && error.status === 401) return null;
    throw error;
  }
}

export function iniciarSesion(email: string, password: string): Promise<ProfesionalAutenticado> {
  return solicitar("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }, false);
}

export function registrarProfesional(datos: RegistroProfesional): Promise<ProfesionalAutenticado> {
  return solicitar("/api/auth/registro", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  }, false);
}

export function cerrarSesion(): Promise<void> {
  return solicitar("/api/auth/logout", { method: "POST" }, false);
}

export type PacienteCrear = Omit<Paciente, "id" | "activo">;

export function listarPacientes(): Promise<Paciente[]> {
  return solicitarListaCompleta("/api/pacientes");
}

export function guardarPaciente(datos: PacienteCrear): Promise<Paciente> {
  return solicitar("/api/pacientes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

// Editar los datos básicos de un paciente ya registrado.
export type PacienteActualizar = Pick<
  Paciente,
  "nombre" | "apellido" | "fecha_nacimiento" | "fecha_inicio_seguimiento"
>;

export function editarPaciente(pacienteId: number, datos: PacienteActualizar): Promise<Paciente> {
  return solicitar(`/api/pacientes/${pacienteId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

// Cada paciente tiene una sola admisión; un 404 significa que aún no fue creada.
export async function obtenerAdmision(pacienteId: number): Promise<Admision | null> {
  try {
    return await solicitar(`/api/pacientes/${pacienteId}/admision`);
  } catch (error) {
    if (error instanceof ErrorAPI && error.status === 404) return null;
    throw error;
  }
}

export function guardarAdmision(pacienteId: number, datos: Admision): Promise<Admision> {
  return solicitar(`/api/pacientes/${pacienteId}/admision`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

// Escolaridad: un paciente puede tener varios períodos escolares.
export function listarEscolaridades(pacienteId: number): Promise<Escolaridad[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/escolaridades`);
}

export function guardarEscolaridad(
  pacienteId: number, datos: EscolaridadGuardar, escolaridadId?: number
): Promise<Escolaridad> {
  const ruta = `/api/pacientes/${pacienteId}/escolaridades` +
    (escolaridadId === undefined ? "" : `/${escolaridadId}`);
  return solicitar(ruta, {
    method: escolaridadId === undefined ? "POST" : "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

// Profesionales externos vinculados a un paciente (no son usuarios de acceso).
export function listarProfesionalesTratantes(pacienteId: number): Promise<ProfesionalTratante[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/profesionales-tratantes`);
}

export function guardarProfesionalTratante(
  pacienteId: number, datos: ProfesionalTratanteGuardar, profesionalId?: number
): Promise<ProfesionalTratante> {
  const ruta = `/api/pacientes/${pacienteId}/profesionales-tratantes` +
    (profesionalId === undefined ? "" : `/${profesionalId}`);
  return solicitar(ruta, {
    method: profesionalId === undefined ? "POST" : "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}

// Objetivos: múltiples registros de seguimiento por paciente.
export function listarObjetivos(pacienteId: number): Promise<Objetivo[]> {
  return solicitarListaCompleta(`/api/pacientes/${pacienteId}/objetivos`);
}

export function guardarObjetivo(
  pacienteId: number, datos: ObjetivoGuardar, objetivoId?: number
): Promise<Objetivo> {
  const ruta = `/api/pacientes/${pacienteId}/objetivos` +
    (objetivoId === undefined ? "" : `/${objetivoId}`);
  return solicitar(ruta, {
    method: objetivoId === undefined ? "POST" : "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
}
