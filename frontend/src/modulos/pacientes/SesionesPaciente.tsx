import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  guardarObservacion, guardarSesion, listarObservaciones, listarSesiones,
  type Observacion, type ObservacionGuardar, type Sesion,
} from "../../servicios/api-seguimiento";
import type { Objetivo } from "./ObjetivosPaciente";
import CronologiaPaciente from "./CronologiaPaciente";
import GrabadoraNota from "./GrabadoraNota";

type Props = {
  pacienteId: number;
  objetivos: Objetivo[];
  onCambiarObservaciones: () => void;
  onCambiarSesiones?: () => void;
};

const mostrarFecha = (fecha: string) => fecha.split("-").reverse().join("/");
const ordenadas = (sesiones: Sesion[]) => [...sesiones].sort((a, b) =>
  b.fecha.localeCompare(a.fecha) || b.id - a.id
);
function hoyLocal() {
  const fecha = new Date();
  const numero = (valor: number) => String(valor).padStart(2, "0");
  return `${fecha.getFullYear()}-${numero(fecha.getMonth() + 1)}-${numero(fecha.getDate())}`;
}

const camposTexto = ["contexto", "conducta_observable", "intervencion", "resultado", "nota_libre"] as const;
const etiquetas: Record<(typeof camposTexto)[number], string> = {
  contexto: "Contexto", conducta_observable: "Conducta observable", intervencion: "Intervención",
  resultado: "Resultado", nota_libre: "Nota libre",
};

export default function SesionesPaciente({ pacienteId, objetivos, onCambiarObservaciones, onCambiarSesiones }: Props) {
  const notaSesionRef = useRef<HTMLTextAreaElement>(null);
  const notaObservacionRef = useRef<HTMLTextAreaElement>(null);

  // Las transcripciones se incorporan al formulario para revisión, no se guardan automáticamente.
  function insertarTexto(referencia: { current: HTMLTextAreaElement | null }, texto: string) {
    const campo = referencia.current;
    if (!campo) return;
    campo.value = [campo.value.trim(), texto.trim()].filter(Boolean).join("\n\n");
    campo.focus();
  }

  const [sesiones, setSesiones] = useState<Sesion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [formSesion, setFormSesion] = useState<number | "nuevo" | null>(null);
  const [guardandoSesion, setGuardandoSesion] = useState(false);
  const [errorSesion, setErrorSesion] = useState("");
  const [sesionSeleccionada, setSesionSeleccionada] = useState<number | null>(null);
  const [observaciones, setObservaciones] = useState<Observacion[]>([]);
  const [cargandoObs, setCargandoObs] = useState(false);
  const [errorObs, setErrorObs] = useState("");
  const [formObs, setFormObs] = useState<number | "nuevo" | null>(null);
  const [guardandoObs, setGuardandoObs] = useState(false);
  const [errorFormObs, setErrorFormObs] = useState("");
  const [cronologiaVisible, setCronologiaVisible] = useState(false);
  const [revisionCronologia, setRevisionCronologia] = useState(0);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError("");
    setSesiones([]);
    setSesionSeleccionada(null);
    listarSesiones(pacienteId)
      .then((datos) => { if (vigente) setSesiones(ordenadas(datos)); })
      .catch((fallo) => {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las sesiones.");
      })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [pacienteId]);

  useEffect(() => {
    if (sesionSeleccionada === null) return;
    let vigente = true;
    setObservaciones([]);
    setCargandoObs(true);
    setErrorObs("");
    listarObservaciones(pacienteId, sesionSeleccionada)
      .then((datos) => { if (vigente) setObservaciones(datos); })
      .catch((fallo) => {
        if (vigente) setErrorObs(fallo instanceof Error ? fallo.message : "No se pudieron cargar las observaciones.");
      })
      .finally(() => { if (vigente) setCargandoObs(false); });
    return () => { vigente = false; };
  }, [pacienteId, sesionSeleccionada]);

  async function guardarFormularioSesion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const datos = new FormData(evento.currentTarget);
    const fecha = String(datos.get("fecha") ?? "");
    const presente = datos.get("presente") === "true";
    const nota_general = String(datos.get("nota_general") ?? "").trim() || null;
    if (!fecha) { setErrorSesion("Completá la fecha."); return; }
    setGuardandoSesion(true);
    setErrorSesion("");
    try {
      const guardada = await guardarSesion(pacienteId, { fecha, presente, nota_general },
        typeof formSesion === "number" ? formSesion : undefined);
      setSesiones((actuales) => ordenadas([
        ...actuales.filter((actual) => actual.id !== guardada.id), guardada,
      ]));
      setFormSesion(null);
      setSesionSeleccionada(guardada.id);
      setRevisionCronologia((n) => n + 1);
      onCambiarSesiones?.();
    } catch (fallo) {
      setErrorSesion(fallo instanceof Error ? fallo.message : "No se pudo guardar la sesión.");
    } finally {
      setGuardandoSesion(false);
    }
  }

  async function guardarFormularioObservacion(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (sesionSeleccionada === null) return;
    const formulario = new FormData(evento.currentTarget);
    const objetivo = String(formulario.get("objetivo_id") ?? "");
    const datos: ObservacionGuardar = {
      objetivo_id: objetivo ? Number(objetivo) : null,
      contexto: String(formulario.get("contexto") ?? "").trim() || null,
      conducta_observable: String(formulario.get("conducta_observable") ?? "").trim() || null,
      intervencion: String(formulario.get("intervencion") ?? "").trim() || null,
      resultado: String(formulario.get("resultado") ?? "").trim() || null,
      nota_libre: String(formulario.get("nota_libre") ?? "").trim() || null,
    };
    if (camposTexto.every((campo) => !datos[campo])) {
      setErrorFormObs("Completá al menos uno de los campos de texto.");
      return;
    }
    setGuardandoObs(true);
    setErrorFormObs("");
    try {
      const guardada = await guardarObservacion(pacienteId, sesionSeleccionada, datos,
        typeof formObs === "number" ? formObs : undefined);
      setObservaciones((actuales) => [
        ...actuales.filter((actual) => actual.id !== guardada.id), guardada,
      ].sort((a, b) => a.id - b.id));
      setFormObs(null);
      setRevisionCronologia((n) => n + 1);
      onCambiarObservaciones();
    } catch (fallo) {
      setErrorFormObs(fallo instanceof Error ? fallo.message : "No se pudo guardar la observación.");
    } finally {
      setGuardandoObs(false);
    }
  }

  const sesionParaEditar = sesiones.find((sesion) => sesion.id === formSesion);
  const observacionParaEditar = observaciones.find((obs) => obs.id === formObs);

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Sesiones de seguimiento</h2>
        {formSesion === null && (
          <button className="pacientes-boton" type="button" disabled={cargando}
            onClick={() => { setFormSesion("nuevo"); setErrorSesion(""); }}>
            + Nueva sesión
          </button>
        )}
      </div>
      {cargando && <p className="pacientes-descripcion">Cargando sesiones...</p>}
      {error && <p role="alert">{error}</p>}
      {!cargando && !error && sesiones.length === 0 && formSesion === null && (
        <p className="pacientes-descripcion">Todavía no se registraron sesiones.</p>
      )}

      {formSesion !== null && (
        <form key={formSesion} className="admision-formulario" onSubmit={guardarFormularioSesion}>
          <h3>{formSesion === "nuevo" ? "Nueva sesión" : "Editar sesión"}</h3>
          <label>Fecha
            <input type="date" name="fecha" required defaultValue={sesionParaEditar?.fecha ?? hoyLocal()} />
          </label>
          <label>Asistencia
            <select name="presente" defaultValue={String(sesionParaEditar?.presente ?? true)}>
              <option value="true">Presente</option>
              <option value="false">Ausente</option>
            </select>
          </label>
          <label>Nota general (opcional)
            <textarea ref={notaSesionRef} name="nota_general" rows={3}
              defaultValue={sesionParaEditar?.nota_general ?? ""} />
          </label>
          <GrabadoraNota onConfirmarTexto={(texto) => insertarTexto(notaSesionRef, texto)} />
          {errorSesion && <p role="alert">{errorSesion}</p>}
          <div className="pacientes-acciones">
            <button className="pacientes-boton" type="submit" disabled={guardandoSesion}>
              {guardandoSesion ? "Guardando..." : "Guardar sesión"}
            </button>
            <button type="button" disabled={guardandoSesion} onClick={() => setFormSesion(null)}>Cancelar</button>
          </div>
        </form>
      )}

      <div className="seguimiento-lista">
        {sesiones.map((sesion) => (
          <div className="seguimiento-fila" key={sesion.id}>
            <div>
              <strong>{mostrarFecha(sesion.fecha)} · {sesion.presente ? "Presente" : "Ausente"}</strong>
              {sesion.nota_general && <p>{sesion.nota_general}</p>}
            </div>
            <div className="seguimiento-acciones">
              <button type="button" onClick={() => {
                setSesionSeleccionada((id) => id === sesion.id ? null : sesion.id);
                setFormObs(null);
              }}>
                {sesionSeleccionada === sesion.id ? "Cerrar" : "Observaciones"}
              </button>
              <button type="button" onClick={() => {
                setFormSesion(sesion.id); setErrorSesion("");
              }}>Editar</button>
            </div>
          </div>
        ))}
      </div>

      {sesionSeleccionada !== null && (
        <div className="seguimiento-subpanel">
          <div className="admision-cabecera">
            <h3>Observaciones · {mostrarFecha(sesiones.find((sesion) => sesion.id === sesionSeleccionada)?.fecha ?? "")}</h3>
            {formObs === null && (
              <button type="button" className="pacientes-boton" disabled={cargandoObs}
                onClick={() => { setFormObs("nuevo"); setErrorFormObs(""); }}>
                + Agregar observación
              </button>
            )}
          </div>
          {cargandoObs && <p className="pacientes-descripcion">Cargando observaciones...</p>}
          {errorObs && <p role="alert">{errorObs}</p>}
          {!cargandoObs && !errorObs && observaciones.length === 0 && formObs === null && (
            <p className="pacientes-descripcion">Esta sesión todavía no tiene observaciones.</p>
          )}
          {observaciones.map((obs) => (
            <div className="seguimiento-registro" key={obs.id}>
              {obs.objetivo_id !== null && (
                <p><b>Objetivo:</b> {objetivos.find((obj) => obj.id === obs.objetivo_id)?.descripcion ?? "Objetivo no disponible"}</p>
              )}
              {camposTexto.map((campo) => obs[campo] && (
                <p key={campo}><b>{etiquetas[campo]}:</b> {obs[campo]}</p>
              ))}
              <button type="button" className="seguimiento-link" onClick={() => {
                setFormObs(obs.id); setErrorFormObs("");
              }}>Editar observación</button>
            </div>
          ))}
          {formObs !== null && (
            <form key={formObs} className="admision-formulario" onSubmit={guardarFormularioObservacion}>
              <h3>{formObs === "nuevo" ? "Nueva observación" : "Editar observación"}</h3>
              <label>Objetivo relacionado (opcional)
                <select name="objetivo_id" defaultValue={observacionParaEditar?.objetivo_id ?? ""}>
                  <option value="">Sin objetivo vinculado</option>
                  {objetivos.map((obj) => <option value={obj.id} key={obj.id}>{obj.descripcion}</option>)}
                </select>
              </label>
              {camposTexto.map((campo) => (
                <label key={campo}>{etiquetas[campo]}
                  <textarea ref={campo === "nota_libre" ? notaObservacionRef : undefined}
                    name={campo} rows={campo === "nota_libre" ? 4 : 2}
                    defaultValue={observacionParaEditar?.[campo] ?? ""} />
                </label>
              ))}
              <GrabadoraNota onConfirmarTexto={(texto) => insertarTexto(notaObservacionRef, texto)} />
              <p className="pacientes-descripcion">Completá los campos que correspondan. Al menos uno debe tener texto.</p>
              {errorFormObs && <p role="alert">{errorFormObs}</p>}
              <div className="pacientes-acciones">
                <button className="pacientes-boton" type="submit" disabled={guardandoObs}>
                  {guardandoObs ? "Guardando..." : "Guardar observación"}
                </button>
                <button type="button" disabled={guardandoObs} onClick={() => setFormObs(null)}>Cancelar</button>
              </div>
            </form>
          )}
        </div>
      )}
      <div className="seguimiento-cronologia-control">
        <button type="button" className="seguimiento-link" onClick={() => setCronologiaVisible(!cronologiaVisible)}
          disabled={cargando || !!error} aria-expanded={cronologiaVisible}>
          {cronologiaVisible ? "Ocultar cronología" : "Ver cronología completa"}
        </button>
      </div>
      {cronologiaVisible && !cargando && !error && (
        <CronologiaPaciente key={revisionCronologia} pacienteId={pacienteId} sesiones={sesiones} objetivos={objetivos} />
      )}
    </section>
  );
}
