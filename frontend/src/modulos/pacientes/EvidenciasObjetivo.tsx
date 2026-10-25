import { useEffect, useState } from "react";
import { listarEvidenciasObjetivo, type EvidenciaObjetivo } from "../../servicios/api-seguimiento";

const mostrarFecha = (fecha: string) => fecha.split("-").reverse().join("/");

type Props = {
  pacienteId: number;
  objetivoId: number;
  revision: number;
};

export default function EvidenciasObjetivo({ pacienteId, objetivoId, revision }: Props) {
  const [abierto, setAbierto] = useState(false);
  const [evidencias, setEvidencias] = useState<EvidenciaObjetivo[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!abierto) return;
    let vigente = true;
    setCargando(true);
    setError("");
    listarEvidenciasObjetivo(pacienteId, objetivoId)
      .then((datos) => { if (vigente) setEvidencias(datos); })
      .catch((fallo) => {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las evidencias.");
      })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [pacienteId, objetivoId, abierto, revision]);

  return (
    <div className="seguimiento-evidencias">
      <button type="button" className="seguimiento-link" onClick={() => setAbierto(!abierto)}
        aria-expanded={abierto}>
        {abierto ? "Ocultar evidencias" : "Ver evidencias"}
      </button>
      {abierto && (
        <div className="seguimiento-subpanel">
          {cargando && <p className="pacientes-descripcion">Cargando evidencias...</p>}
          {error && <p role="alert">{error}</p>}
          {!cargando && !error && evidencias.length === 0 && (
            <p className="pacientes-descripcion">Todavía no hay observaciones vinculadas a este objetivo.</p>
          )}
          {!cargando && !error && evidencias.map((evidencia) => (
            <div key={evidencia.id} className="seguimiento-registro">
              <strong>Sesión del {mostrarFecha(evidencia.fecha_sesion)}</strong>
              {evidencia.contexto && <p><b>Contexto:</b> {evidencia.contexto}</p>}
              {evidencia.conducta_observable && <p><b>Conducta:</b> {evidencia.conducta_observable}</p>}
              {evidencia.intervencion && <p><b>Intervención:</b> {evidencia.intervencion}</p>}
              {evidencia.resultado && <p><b>Resultado:</b> {evidencia.resultado}</p>}
              {evidencia.nota_libre && <p><b>Nota:</b> {evidencia.nota_libre}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
