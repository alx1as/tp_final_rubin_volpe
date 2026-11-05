import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, CalendarDays, X } from "lucide-react";
import { listarCronologia, type EntradaCronologia } from "../../servicios/api-seguimiento";
import type { Objetivo } from "./ObjetivosPaciente";

type Props = {
  pacienteId: number;
  mes: string;
  objetivos: Objetivo[];
  revision: number;
  onVerSesion: (sesionId: number) => void;
  onCerrar: () => void;
};

const mostrarFecha = (valor: string) => valor.split("-").reverse().join("/");
function tituloMes(valor: string) {
  const [anio, mes] = valor.split("-").map(Number);
  return new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(anio, mes - 1, 1));
}

/** Consulta exclusivamente las sesiones del mes seleccionado mediante la API de cronología. */
export default function CronologiaPaciente({ pacienteId, mes, objetivos, revision, onVerSesion, onCerrar }: Props) {
  const [entradas, setEntradas] = useState<EntradaCronologia[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [abiertas, setAbiertas] = useState<number[]>([]);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError("");
    setEntradas([]);
    setAbiertas([]);
    listarCronologia(pacienteId, mes)
      .then((datos) => { if (vigente) setEntradas(datos); })
      .catch((fallo) => {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudo cargar la actividad del mes.");
      })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [pacienteId, mes, revision]);

  return (
    <section className="cronologia-detalle" aria-label={`Actividad de ${tituloMes(mes)}`}>
      <div className="cronologia-detalle-cabecera">
        <div><p className="vista-sobretitulo">ACTIVIDAD DEL PACIENTE</p><h3>{tituloMes(mes)}</h3></div>
        <button type="button" className="icono-boton" aria-label="Cerrar actividad del mes" onClick={onCerrar}><X size={19}/></button>
      </div>
      {cargando && <p role="status" className="texto-atenuado">Cargando actividad...</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && entradas.length === 0 && <p className="texto-atenuado">No se registraron sesiones en este mes.</p>}
      <div className="cronologia-entradas">
        {entradas.map((entrada) => {
          const abierto = abiertas.includes(entrada.id);
          return (
            <article className="cronologia-entrada" key={entrada.id}>
              <div className="cronologia-entrada-encabezado">
                <div><span className="cronologia-fecha"><CalendarDays size={15} aria-hidden="true"/>{mostrarFecha(entrada.fecha)}</span>
                  <span className={`estado-asistencia ${entrada.presente ? "" : "ausente"}`}>{entrada.presente ? "Asistió" : "Ausente"}</span>
                </div>
                <button type="button" className="texto-accion" onClick={() => onVerSesion(entrada.id)}>Abrir sesión <ArrowRight size={15}/></button>
              </div>
              {entrada.nota_general && <p className="cronologia-nota">{entrada.nota_general}</p>}
              {entrada.observaciones.length > 0 && (
                <>
                  <button type="button" className="texto-accion" aria-expanded={abierto}
                    onClick={() => setAbiertas((prev) => abierto ? prev.filter((id) => id !== entrada.id) : [...prev, entrada.id])}>
                    {abierto ? "Ocultar" : "Ver"} {entrada.observaciones.length} observación{entrada.observaciones.length !== 1 ? "es" : ""}
                  </button>
                  {abierto && <div className="cronologia-observaciones">{entrada.observaciones.map((obs) => {
                    const objetivo = objetivos.find((item) => item.id === obs.objetivo_id);
                    return <div className="seguimiento-registro" key={obs.id}>
                      {objetivo && <p><strong>Objetivo:</strong> {objetivo.descripcion}</p>}
                      {obs.contexto && <p><strong>Contexto:</strong> {obs.contexto}</p>}
                      {obs.conducta_observable && <p><strong>Conducta:</strong> {obs.conducta_observable}</p>}
                      {obs.intervencion && <p><strong>Intervención:</strong> {obs.intervencion}</p>}
                      {obs.resultado && <p><strong>Resultado:</strong> {obs.resultado}</p>}
                      {obs.nota_libre && <p><strong>Nota:</strong> {obs.nota_libre}</p>}
                    </div>;
                  })}</div>}
                </>
              )}
            </article>
          );
        })}
      </div>
      <button type="button" className="texto-accion cronologia-regresar" onClick={onCerrar}><ArrowLeft size={16}/> Volver a la ficha</button>
    </section>
  );
}
