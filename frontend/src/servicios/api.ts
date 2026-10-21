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