import type { Paciente } from "../modulos/pacientes/Pacientes";
import type { Admision } from "../modulos/pacientes/AdmisionPaciente";
import type { Escolaridad, EscolaridadGuardar } from "../modulos/pacientes/EscolaridadPaciente";

/* Centraliza la URL y la comunicación con el backend.
Cuando desarrollemos los endpoints de pacientes, vamos a utilizar esta misma carpeta.*/
export type SaludAPI = {
  estado: "ok" | "error";
  postgresql: "conectado" | "no_disponible";
};

const API_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

export async function consultarSalud(): Promise<SaludAPI> {
  const respuesta = await fetch(`${API_URL}/api/salud`);

  if (respuesta.status !== 200 && respuesta.status !== 503) {
    throw new Error(`Error HTTP ${respuesta.status}`);
  }

  return (await respuesta.json()) as SaludAPI;
}


export type PacienteCrear = Omit<Paciente, "id" | "activo">;

export async function listarPacientes(): Promise<Paciente[]> {
  const respuesta = await fetch(`${API_URL}/api/pacientes`);

  if (!respuesta.ok) {
    throw new Error("No se pudieron cargar los pacientes");
  }

  return respuesta.json();
}

export async function guardarPaciente(
  datos: PacienteCrear
): Promise<Paciente> {
  const respuesta = await fetch(`${API_URL}/api/pacientes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(datos),
  });

  if (!respuesta.ok) {
    throw new Error(`No se pudo guardar el paciente (HTTP ${respuesta.status})`);
  }

  return respuesta.json();
}

// Cada paciente tiene una única admisión: se consulta y se crea/actualiza con PUT.

export async function obtenerAdmision(pacienteId: number): Promise<Admision | null> {
  const respuesta = await fetch(`${API_URL}/api/pacientes/${pacienteId}/admision`);
  if (!respuesta.ok) {
    throw new Error(`No se pudo cargar la admisión (HTTP ${respuesta.status})`);
  }
  return respuesta.json();
}

export async function guardarAdmision(
  pacienteId: number,
  datos: Admision
): Promise<Admision> {
  const respuesta = await fetch(`${API_URL}/api/pacientes/${pacienteId}/admision`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    throw new Error(`No se pudo guardar la admisión (HTTP ${respuesta.status})`);
  }
  return respuesta.json();
}


// Escolaridad: un paciente puede tener varios períodos escolares.
export async function listarEscolaridades(pacienteId: number): Promise<Escolaridad[]> {
  const respuesta = await fetch(`${API_URL}/api/pacientes/${pacienteId}/escolaridades`);
  if (!respuesta.ok) {
    throw new Error(`No se pudo cargar la escolaridad (HTTP ${respuesta.status})`);
  }
  return respuesta.json();
}

export async function guardarEscolaridad(
  pacienteId: number,
  datos: EscolaridadGuardar,
  escolaridadId?: number
): Promise<Escolaridad> {
  const url = `${API_URL}/api/pacientes/${pacienteId}/escolaridades` +
    (escolaridadId === undefined ? "" : `/${escolaridadId}`);
  const respuesta = await fetch(url, {
    method: escolaridadId === undefined ? "POST" : "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  if (!respuesta.ok) {
    throw new Error(`No se pudo guardar la escolaridad (HTTP ${respuesta.status})`);
  }
  return respuesta.json();
}
