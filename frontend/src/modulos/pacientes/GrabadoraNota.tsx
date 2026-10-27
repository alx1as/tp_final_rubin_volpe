import { useEffect, useRef, useState } from "react";
import { ErrorAPI } from "../../servicios/api";
import { transcribirAudio } from "../../servicios/api-transcripciones";
import "./GrabadoraNota.css";

type Props = { onConfirmarTexto: (texto: string) => void };
type Estado = "sin-audio" | "grabando" | "procesando" | "lista";

export default function GrabadoraNota({ onConfirmarTexto }: Props) {
  const [estado, setEstado] = useState<Estado>("sin-audio");
  const [urlAudio, setUrlAudio] = useState<string | null>(null);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [texto, setTexto] = useState<string | null>(null);
  const [transcribiendo, setTranscribiendo] = useState(false);
  const [error, setError] = useState("");

  const grabadoraRef = useRef<MediaRecorder | null>(null);
  const microfonoRef = useRef<MediaStream | null>(null);
  const urlRef = useRef<string | null>(null);
  const solicitudRef = useRef<AbortController | null>(null);
  const vigenteRef = useRef(true);
  const descartarRef = useRef(false);

  function soltarMicrofono() {
    microfonoRef.current?.getTracks().forEach((pista) => pista.stop());
    microfonoRef.current = null;
  }

  function limpiarAudio() {
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = null;
    setUrlAudio(null);
    setAudio(null);
    setTexto(null);
  }

  useEffect(() => {
    vigenteRef.current = true;
    return () => {
      vigenteRef.current = false;
      solicitudRef.current?.abort();
      if (grabadoraRef.current?.state === "recording") {
        descartarRef.current = true;
        grabadoraRef.current.stop();
      }
      microfonoRef.current?.getTracks().forEach((pista) => pista.stop());
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    };
  }, []);

  async function iniciar() {
    setError("");
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Este navegador no permite grabar audio. Probá con una versión actualizada.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!vigenteRef.current) {
        stream.getTracks().forEach((pista) => pista.stop());
        return;
      }
      microfonoRef.current = stream;
      const formatos = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
      const tipo = formatos.find((formato) => MediaRecorder.isTypeSupported(formato));
      const grabadora = new MediaRecorder(stream, tipo ? { mimeType: tipo } : undefined);
      const fragmentos: BlobPart[] = [];
      descartarRef.current = false;
      grabadoraRef.current = grabadora;
      grabadora.ondataavailable = (evento) => {
        if (evento.data.size > 0) fragmentos.push(evento.data);
      };
      grabadora.onerror = () => {
        soltarMicrofono();
        if (vigenteRef.current) {
          setEstado("sin-audio");
          setError("Se interrumpió la grabación. Volvé a intentarlo.");
        }
      };
      grabadora.onstop = () => {
        soltarMicrofono();
        if (!vigenteRef.current || descartarRef.current) return;
        const archivo = new Blob(fragmentos, { type: grabadora.mimeType || "audio/webm" });
        if (!archivo.size) {
          setEstado("sin-audio");
          setError("La grabación quedó vacía. Intentá nuevamente.");
          return;
        }
        const direccion = URL.createObjectURL(archivo);
        urlRef.current = direccion;
        setAudio(archivo);
        setUrlAudio(direccion);
        setEstado("lista");
      };
      grabadora.start();
      setEstado("grabando");
    } catch (fallo) {
      soltarMicrofono();
      setError(fallo instanceof DOMException && fallo.name === "NotAllowedError"
        ? "No se concedió permiso para usar el micrófono."
        : "No se pudo iniciar la grabación. Revisá el micrófono y sus permisos.");
    }
  }

  function detener() {
    if (grabadoraRef.current?.state !== "recording") return;
    setEstado("procesando");
    grabadoraRef.current.stop();
  }

  function descartar() {
    solicitudRef.current?.abort();
    descartarRef.current = true;
    if (grabadoraRef.current?.state === "recording") grabadoraRef.current.stop();
    soltarMicrofono();
    limpiarAudio();
    setEstado("sin-audio");
    setTranscribiendo(false);
    setError("");
  }

  async function solicitarTranscripcion() {
    if (!audio || transcribiendo) return;
    setError("");
    const controlador = new AbortController();
    solicitudRef.current = controlador;
    setTranscribiendo(true);
    try {
      const resultado = await transcribirAudio(audio, controlador.signal);
      if (!controlador.signal.aborted) {
        setTexto(resultado);
      }
    } catch (fallo) {
      if (controlador.signal.aborted) return;
      if (fallo instanceof ErrorAPI && fallo.status === 503) {
        setError("La transcripción todavía no está disponible en el servidor. La grabación se puede escuchar o descartar.");
      } else {
        setError(fallo instanceof Error ? fallo.message : "No se pudo transcribir el audio.");
      }
    } finally {
      if (solicitudRef.current === controlador) {
        solicitudRef.current = null;
        setTranscribiendo(false);
      }
    }
  }

  function confirmar() {
    if (!texto?.trim()) return;
    onConfirmarTexto(texto.trim());
    descartar();
  }

  return (
    <div className="grabadora-nota">
      <p className="grabadora-nota-titulo">Nota de voz</p>
      <p className="grabadora-nota-ayuda">El audio no se guarda en la ficha. Podés transcribirlo y revisar el texto antes de guardarlo.</p>
      <div className="grabadora-nota-acciones">
        {estado === "sin-audio" && (
          <button type="button" onClick={iniciar}>Grabar audio</button>
        )}
        {estado === "grabando" && (
          <button type="button" className="grabadora-nota-detenida" onClick={detener}>Detener grabación</button>
        )}
        {estado === "procesando" && <span>Preparando audio...</span>}
        {estado === "lista" && (
          <>
            <button type="button" onClick={solicitarTranscripcion} disabled={transcribiendo}>
              {transcribiendo ? "Transcribiendo..." : "Transcribir"}
            </button>
            <button type="button" onClick={descartar}>Descartar audio</button>
          </>
        )}
      </div>
      {estado === "grabando" && <p className="grabadora-nota-indicador" role="status">Grabando · micrófono activo</p>}
      {urlAudio && (
        <audio controls src={urlAudio} aria-label="Escuchar nota de voz grabada">
          El navegador no permite reproducir este formato de audio.
        </audio>
      )}
      {texto !== null && (
        <div className="grabadora-nota-revision">
          <label>Revisar y corregir transcripción
            <textarea rows={4} value={texto} onChange={(evento) => setTexto(evento.target.value)} />
          </label>
          <button type="button" onClick={confirmar} disabled={!texto.trim()}>Incorporar texto a la nota</button>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
    </div>
  );
}
