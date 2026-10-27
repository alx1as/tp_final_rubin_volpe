import { solicitar } from "./api";

// Se envía el audio temporalmente; el backend devuelve texto para revisión.
export function transcribirAudio(audio: Blob, signal?: AbortSignal): Promise<string> {
  const formulario = new FormData();
  const formato = audio.type;
  const extension = formato.includes("mp4") ? "m4a" : formato.includes("ogg") ? "ogg" : "webm";
  formulario.append("audio", audio, `nota-voz.${extension}`);
  return solicitar<{ texto: string }>("/api/transcripciones", {
    method: "POST",
    body: formulario,
    signal,
  }).then((respuesta) => respuesta.texto);
}
