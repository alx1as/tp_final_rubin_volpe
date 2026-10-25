import { useEffect, useState } from "react";
import { listarObservaciones, type Observacion, type Sesion } from "../../servicios/api-seguimiento";
import type { Objetivo } from "./ObjetivosPaciente";

type Entrada = { sesion: Sesion; observaciones: Observacion[] };
type Props = { pacienteId: number; sesiones: Sesion[]; objetivos: Objetivo[] };

const mostrarFecha = (fecha: string) => fecha.split("-").reverse().join("/");

export default function CronologiaPaciente({ pacienteId, sesiones, objetivos }: Props) {
  const [entradas, setEntradas] = useState<Entrada[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let vigente = true;
    async function cargar() {
      setCargando(true);
      setError("");
      setEntradas([]);
      try {
        const registros: Entrada[] = [];
        // Carga por grupos: evita disparar demasiadas peticiones simultáneas.
        for (let i = 0; i < sesiones.length; i += 5) {
          const grupo = sesiones.slice(i, i + 5);
          const resultados = await Promise.all(grupo.map(async (sesion) => ({
            sesion,
            observaciones: await listarObservaciones(pacienteId, sesion.id),
          })));
          if (!vigente) return;
          registros.push(...resultados);
        }
        if (vigente) setEntradas(registros);
      } catch (fallo) {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la cronología.");
      } finally {
        if (vigente) setCargando(false);
      }
    }
    void cargar();
    return () => { vigente = false; };
  }, [pacienteId, sesiones]);

  return (
    <div className="seguimiento-subpanel seguimiento-cronologia">
      {cargando && <p className="pacientes-descripcion">Cargando cronología...</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && entradas.length === 0 && (
        <p className="pacientes-descripcion">Todavía no se registraron sesiones.</p>
      )}
      {!cargando && !error && entradas.map(({ sesion, observaciones }) => (
        <article className="seguimiento-cronologia-item" key={sesion.id}>
          <h3>{mostrarFecha(sesion.fecha)} · {sesion.presente ? "Asistió" : "Ausente"}</h3>
          {sesion.nota_general && <p>{sesion.nota_general}</p>}
          {observaciones.length === 0 && <p className="pacientes-descripcion">Sin observaciones.</p>}
          {observaciones.map((obs) => {
            const objetivo = objetivos.find((actual) => actual.id === obs.objetivo_id);
            return (
              <div className="seguimiento-registro" key={obs.id}>
                {objetivo && <p><b>Objetivo:</b> {objetivo.descripcion}</p>}
                {obs.contexto && <p><b>Contexto:</b> {obs.contexto}</p>}
                {obs.conducta_observable && <p><b>Conducta:</b> {obs.conducta_observable}</p>}
                {obs.intervencion && <p><b>Intervención:</b> {obs.intervencion}</p>}
                {obs.resultado && <p><b>Resultado:</b> {obs.resultado}</p>}
                {obs.nota_libre && <p><b>Nota:</b> {obs.nota_libre}</p>}
              </div>
            );
          })}
        </article>
      ))}
    </div>
  );
}
