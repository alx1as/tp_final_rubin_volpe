import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  guardarRegistroSesion, listarObservaciones, listarSesiones, organizarRegistroConIA,
  type Observacion, type ObservacionGuardar, type RegistroSesionGuardar, type Sesion, type SesionGuardar,
} from "../../servicios/api-seguimiento";
import type { Objetivo } from "./ObjetivosPaciente";
import GrabadoraNota from "./GrabadoraNota";
import "./SesionRegistro.css";

type Props = {
  pacienteId: number;
  objetivos: Objetivo[];
  onCambiarObservaciones: () => void;
  onCambiarSesiones?: () => void;
  sesionDestino?: number | null;
  solicitudNueva?: number;
  onSolicitudNuevaProcesada?: () => void;
  objetivoOrigen?: number | null;
  onVolverObjetivo?: (objetivoId: number) => void;
};

type Bloque = { clave: number; id?: number; datos: ObservacionGuardar; sugeridoIA?: boolean };
const nombresCampos = ["contexto", "conducta_observable", "intervencion", "resultado", "nota_libre"] as const;
type CampoTexto = (typeof nombresCampos)[number];
const etiquetas: Record<CampoTexto, string> = {
  contexto: "Contexto", conducta_observable: "Conducta observable", intervencion: "Intervención",
  resultado: "Resultado", nota_libre: "Nota libre",
};
const campoVacio = (): ObservacionGuardar => ({
  objetivo_id: null, contexto: null, conducta_observable: null, intervencion: null,
  resultado: null, nota_libre: null,
});
const hoyLocal = () => {
  const fecha = new Date();
  const dos = (n: number) => String(n).padStart(2, "0");
  return `${fecha.getFullYear()}-${dos(fecha.getMonth() + 1)}-${dos(fecha.getDate())}`;
};
const formularioVacio = (): SesionGuardar => ({ fecha: hoyLocal(), presente: true, nota_general: null });
const mostrarFecha = (fecha: string) => fecha.split("-").reverse().join("/");
const ordenarSesiones = (sesiones: Sesion[]) => [...sesiones].sort((a, b) =>
  b.fecha.localeCompare(a.fecha) || b.id - a.id
);
const combinar = (anterior: string | null, nuevo: string) =>
  [anterior?.trim(), nuevo.trim()].filter(Boolean).join("\n\n") || null;
const algunaNota = (datos: ObservacionGuardar) => nombresCampos.some((nombre) => Boolean(datos[nombre]?.trim()));

export default function SesionesPaciente({
  pacienteId, objetivos, onCambiarObservaciones, onCambiarSesiones, sesionDestino,
  solicitudNueva, onSolicitudNuevaProcesada, objetivoOrigen, onVolverObjetivo,
}: Props) {
  const [sesiones, setSesiones] = useState<Sesion[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [sesionSeleccionada, setSesionSeleccionada] = useState<number | null>(null);
  const [observaciones, setObservaciones] = useState<Observacion[]>([]);
  const [cargandoObs, setCargandoObs] = useState(false);
  const [errorObs, setErrorObs] = useState("");
  const [mesFiltro, setMesFiltro] = useState("todos");

  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [cargandoEdicion, setCargandoEdicion] = useState(false);
  const [form, setForm] = useState<SesionGuardar>(formularioVacio);
  const [bloques, setBloques] = useState<Bloque[]>([]);
  const [bajas, setBajas] = useState<number[]>([]);
  const [original, setOriginal] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [organizando, setOrganizando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");
  const [avisoFormulario, setAvisoFormulario] = useState("");
  const secuencia = useRef(0);
  const solicitudEdicion = useRef(0);
  const solicitudOrganizador = useRef(0);
  const solicitudNuevaAtendida = useRef<number | undefined>(undefined);
  const [estadoInicial, setEstadoInicial] = useState("");

  // Se mantiene un registro de cambios reales para no descartar un borrador por accidente.
  const contenidoActual = JSON.stringify({ form, bloques: bloques.map(({ id, datos }) => ({ id, datos })), bajas });
  const hayCambios = editando !== null && estadoInicial !== contenidoActual && !cargandoEdicion;
  function confirmarAbandono() {
    return !hayCambios || window.confirm("Hay cambios sin guardar en la sesión. ¿Querés descartarlos?");
  }

  useEffect(() => {
    let vigente = true;
    queueMicrotask(() => {
      if (vigente) {
        setCargando(true); setError(""); setSesiones([]);
        setEditando(null); setObservaciones([]); setOriginal("");
        setSesionSeleccionada(sesionDestino ?? null);
      }
    });
    listarSesiones(pacienteId)
      .then((datos) => { if (vigente) setSesiones(ordenarSesiones(datos)); })
      .catch((fallo) => { if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las sesiones."); })
      .finally(() => { if (vigente) setCargando(false); });
    return () => {
      vigente = false;
      solicitudEdicion.current += 1;
      solicitudOrganizador.current += 1;
    };
    // El reinicio corresponde al cambio de paciente; sesionDestino se maneja aparte.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pacienteId]);

  useEffect(() => {
    if (sesionSeleccionada === null) return;
    let vigente = true;
    queueMicrotask(() => {
      if (vigente) { setCargandoObs(true); setObservaciones([]); setErrorObs(""); }
    });
    listarObservaciones(pacienteId, sesionSeleccionada)
      .then((datos) => { if (vigente) setObservaciones(datos); })
      .catch((fallo) => { if (vigente) setErrorObs(fallo instanceof Error ? fallo.message : "No se pudieron cargar las observaciones."); })
      .finally(() => { if (vigente) setCargandoObs(false); });
    return () => { vigente = false; };
  }, [pacienteId, sesionSeleccionada]);

  useEffect(() => {
    if (sesionDestino == null) return;
    const animacion = window.requestAnimationFrame(() => {
      setSesionSeleccionada(sesionDestino);
      document.getElementById(`sesion-${sesionDestino}`)?.scrollIntoView({ behavior: "smooth", block: "center" });
    });
    return () => window.cancelAnimationFrame(animacion);
  }, [sesionDestino, cargando]);


  useEffect(() => {
    if (!hayCambios) return;
    function evitarCierre(evento: BeforeUnloadEvent) { evento.preventDefault(); }
    window.addEventListener("beforeunload", evitarCierre);
    return () => window.removeEventListener("beforeunload", evitarCierre);
  }, [hayCambios]);

  const meses = [...new Set(sesiones.map((sesion) => sesion.fecha.slice(0, 7)))];
  const sesionesVisibles = mesFiltro === "todos" ? sesiones : sesiones.filter((sesion) => sesion.fecha.startsWith(mesFiltro));
  function nuevoBloque(datos: ObservacionGuardar = campoVacio(), id?: number, sugeridoIA = false): Bloque {
    secuencia.current += 1;
    return { clave: secuencia.current, id, datos, sugeridoIA };
  }
  function iniciarFormulario(tipo: number | "nuevo", datos: SesionGuardar, observacionesExistentes: Observacion[] = []) {
    const iniciales = observacionesExistentes.map((obs) => nuevoBloque({
      objetivo_id: obs.objetivo_id, contexto: obs.contexto, conducta_observable: obs.conducta_observable,
      intervencion: obs.intervencion, resultado: obs.resultado, nota_libre: obs.nota_libre,
    }, obs.id));
    setEstadoInicial(JSON.stringify({ form: datos, bloques: iniciales.map(({ id, datos }) => ({ id, datos })), bajas: [] }));
    setForm(datos);
    setBloques(iniciales);
    setBajas([]);
    setOriginal("");
    setErrorFormulario("");
    setAvisoFormulario("");
    setEditando(tipo);
  }
  function prepararNueva() {
    solicitudEdicion.current += 1;
    setCargandoEdicion(false);
    iniciarFormulario("nuevo", formularioVacio());
  }
  useEffect(() => {
    if (!solicitudNueva || solicitudNuevaAtendida.current === solicitudNueva) return;
    solicitudNuevaAtendida.current = solicitudNueva;
    const id = window.requestAnimationFrame(() => {
      if (confirmarAbandono()) prepararNueva();
      onSolicitudNuevaProcesada?.();
    });
    return () => window.cancelAnimationFrame(id);
    // La solicitud se procesa una sola vez por su número.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [solicitudNueva]);

  function abrirNueva() { if (confirmarAbandono()) prepararNueva(); }

  async function abrirEdicion(sesion: Sesion) {
    if (!confirmarAbandono()) return;
    const pedido = ++solicitudEdicion.current;
    setCargandoEdicion(true);
    setEditando(sesion.id);
    setErrorFormulario("");
    try {
      const registros = await listarObservaciones(pacienteId, sesion.id);
      if (pedido !== solicitudEdicion.current) return;
      iniciarFormulario(sesion.id, { fecha: sesion.fecha, presente: sesion.presente, nota_general: sesion.nota_general }, registros);
    } catch (fallo) {
      if (pedido !== solicitudEdicion.current) return;
      setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar las observaciones de la sesión.");
      setEditando(null); // Nunca mostrar el formulario con datos de otra sesión.
    } finally {
      if (pedido === solicitudEdicion.current) setCargandoEdicion(false);
    }
  }

  function cerrarFormulario() {
    if (guardando || organizando || !confirmarAbandono()) return;
    solicitudEdicion.current += 1;
    setEditando(null);
    setCargandoEdicion(false);
  }
  function cambiarBloque(clave: number, cambios: Partial<ObservacionGuardar>) {
    setBloques((actuales) => actuales.map((bloque) => bloque.clave === clave
      ? { ...bloque, datos: { ...bloque.datos, ...cambios } } : bloque));
  }
  function quitarBloque(bloque: Bloque) {
    if (bloque.id && !window.confirm("¿Quitar esta observación? Se eliminará definitivamente al guardar la sesión.")) return;
    if (bloque.id) setBajas((actuales) => [...actuales, bloque.id!]);
    setBloques((actuales) => actuales.filter((actual) => actual.clave !== bloque.clave));
  }
  function usarComoNotaGeneral(texto: string) {
    setForm((actual) => ({ ...actual, nota_general: combinar(actual.nota_general, texto) }));
    setAvisoFormulario("Transcripción incorporada a la nota general. Guardá la sesión para conservarla.");
  }

  async function organizarTexto(texto: string): Promise<boolean> {
    if (editando === null || organizando) return false;
    const solicitud = ++solicitudOrganizador.current;
    setOrganizando(true);
    setErrorFormulario("");
    setAvisoFormulario("");
    try {
      const propuesta = await organizarRegistroConIA(pacienteId, texto);
      if (solicitud !== solicitudOrganizador.current) return false;
      const permitidos = new Set(objetivos.map((obj) => obj.id));
      const nuevos = propuesta.observaciones.map((obs) => nuevoBloque({
        ...obs, objetivo_id: obs.objetivo_id !== null && permitidos.has(obs.objetivo_id)
          ? obs.objetivo_id : null,
      }, undefined, true));
      // La IA suma sugerencias al borrador, nunca sobrescribe textos existentes.
      setBloques((actuales) => [...actuales, ...nuevos]);
      if (propuesta.nota_general) setForm((actual) => ({
        ...actual, nota_general: combinar(actual.nota_general, propuesta.nota_general!),
      }));
      setOriginal(texto);
      setAvisoFormulario(`IA propuso ${nuevos.length} observación${nuevos.length === 1 ? "" : "es"}. Revisá los campos y objetivos antes de guardar.`);
      return true;
    } catch (fallo) {
      if (solicitud === solicitudOrganizador.current) {
        setErrorFormulario(fallo instanceof Error ? fallo.message : "No se pudo organizar el audio.");
      }
      return false; // La grabadora conserva la transcripción para reintentar.
    } finally {
      if (solicitud === solicitudOrganizador.current) setOrganizando(false);
    }
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (editando === null || guardando || organizando || cargandoEdicion) return;
    setErrorFormulario("");
    if (!form.fecha) { setErrorFormulario("Completá la fecha de la sesión."); return; }
    const invalidas = bloques.some((bloque) => !algunaNota(bloque.datos));
    if (invalidas) { setErrorFormulario("Hay observaciones vacías. Completá al menos un campo o quitá el bloque."); return; }
    if (bloques.length > 30) { setErrorFormulario("El máximo es de 30 observaciones por sesión."); return; }
    const datos: RegistroSesionGuardar = {
      ...form,
      nota_general: form.nota_general?.trim() || null,
      observaciones: bloques.map(({ id, datos: obs }) => ({
        ...obs, ...(id ? { id } : {}),
        ...Object.fromEntries(nombresCampos.map((campo) => [campo, obs[campo]?.trim() || null])),
      })),
      observaciones_eliminar: bajas,
    };
    setGuardando(true);
    try {
      const resultado = await guardarRegistroSesion(pacienteId, datos,
        typeof editando === "number" ? editando : undefined);
      setSesiones((actuales) => ordenarSesiones([
        ...actuales.filter((sesion) => sesion.id !== resultado.sesion.id), resultado.sesion,
      ]));
      setMesFiltro("todos");
      setSesionSeleccionada(resultado.sesion.id);
      setObservaciones(resultado.observaciones);
      setEditando(null);
      setOriginal("");
      onCambiarSesiones?.();
      onCambiarObservaciones();
    } catch (fallo) {
      setErrorFormulario((fallo instanceof Error ? fallo.message : "No se pudo guardar el registro.") +
        " No se descartó el formulario. Si se interrumpió la conexión, verificá el listado antes de reintentar.");
    } finally { setGuardando(false); }
  }

  return (
    <section className="pacientes-panel sesiones-unificadas" aria-label="Sesiones de seguimiento">
      <div className="admision-cabecera">
        <div>
          <h2>Sesiones de seguimiento</h2>
          <p className="pacientes-descripcion">Una sesión puede incluir una nota breve o varias observaciones vinculadas a objetivos.</p>
        </div>
        {editando === null && (
          <button className="pacientes-boton" type="button" disabled={cargando} onClick={abrirNueva}>+ Nueva sesión</button>
        )}
      </div>
      {error && <p role="alert">{error}</p>}
      {cargando && <p className="pacientes-descripcion">Cargando sesiones...</p>}
      {!cargando && !error && sesiones.length === 0 && editando === null && (
        <p className="pacientes-descripcion">Todavía no se registraron sesiones.</p>
      )}

      {editando !== null && (
        <form className="admision-formulario registro-unico" onSubmit={(evento) => void guardar(evento)}>
          <div className="registro-unico-encabezado">
            <div>
              <p className="vista-sobretitulo">REGISTRO DE SEGUIMIENTO</p>
              <h3>{editando === "nuevo" ? "Nueva sesión" : "Editar sesión y observaciones"}</h3>
            </div>
            <button type="button" className="registro-unico-cerrar" disabled={guardando || organizando} onClick={cerrarFormulario}>Cerrar</button>
          </div>
          {cargandoEdicion ? <p role="status">Cargando el registro completo...</p> : (
            <fieldset disabled={guardando || organizando} className="registro-unico-campos">
              <div className="registro-unico-fila">
                <label>Fecha
                  <input type="date" required value={form.fecha} onChange={(e) => setForm((v) => ({ ...v, fecha: e.target.value }))} />
                </label>
                <label>Asistencia
                  <select value={String(form.presente)} onChange={(e) => setForm((v) => ({ ...v, presente: e.target.value === "true" }))}>
                    <option value="true">Presente</option><option value="false">Ausente</option>
                  </select>
                </label>
              </div>
              <label>Nota general <span className="registro-unico-opcional">· opcional</span>
                <textarea rows={3} value={form.nota_general ?? ""} placeholder="Información general de la sesión, si corresponde..."
                  onChange={(e) => setForm((v) => ({ ...v, nota_general: e.target.value }))} />
              </label>
              <div className="registro-unico-audio">
                <GrabadoraNota onConfirmarTexto={usarComoNotaGeneral} onOrganizarTexto={organizarTexto}
                  etiquetaConfirmar="Usar como nota general" />
                <p>Podés dictar libremente. Si elegís organizar con IA, revisá las observaciones y los objetivos sugeridos. Evitá incluir nombres u otros datos identificatorios en el audio enviado al servicio externo.</p>
              </div>
              {original && (
                <details className="registro-unico-transcripcion">
                  <summary>Consultar transcripción original</summary>
                  <p>{original}</p>
                  <button type="button" onClick={() => setForm((v) => ({ ...v, nota_general: combinar(v.nota_general, original) }))}>
                    Añadir texto original a nota general
                  </button>
                </details>
              )}
              <div className="registro-unico-seccion-cabecera">
                <div>
                  <h4>Observaciones <span className="registro-unico-contador">{bloques.length}</span></h4>
                  <p>Registrá solo lo observado. Cada bloque puede vincularse con un objetivo existente.</p>
                </div>
                <button type="button" className="registro-unico-agregar" onClick={() => setBloques((v) => [...v, nuevoBloque()])}
                  disabled={bloques.length >= 30}>+ Agregar observación</button>
              </div>
              {bloques.length === 0 && <p className="registro-unico-vacio">No hay observaciones cargadas. Podés guardar solo la nota general o agregar una observación.</p>}
              {bloques.map((bloque, indice) => (
                <section key={bloque.clave} className="registro-unico-observacion" aria-label={`Observación ${indice + 1}`}>
                  <div className="registro-unico-observacion-titulo">
                    <div><strong>Observación {indice + 1}</strong>{bloque.sugeridoIA && <span className="registro-unico-ia">Sugerida por IA · revisar</span>}</div>
                    <button type="button" onClick={() => quitarBloque(bloque)}>Quitar</button>
                  </div>
                  <label>Objetivo relacionado <span className="registro-unico-opcional">· opcional</span>
                    <select value={bloque.datos.objetivo_id ?? ""}
                      onChange={(e) => cambiarBloque(bloque.clave, { objetivo_id: e.target.value ? Number(e.target.value) : null })}>
                      <option value="">Sin objetivo vinculado</option>
                      {objetivos.map((objetivo) => <option key={objetivo.id} value={objetivo.id}>
                        {objetivo.descripcion} ({objetivo.estado})
                      </option>)}
                    </select>
                  </label>
                  <div className="registro-unico-observacion-campos">
                    {nombresCampos.map((campo) => (
                      <label key={campo}>{etiquetas[campo]}
                        <textarea rows={campo === "nota_libre" ? 3 : 2} value={bloque.datos[campo] ?? ""}
                          onChange={(e) => cambiarBloque(bloque.clave, { [campo]: e.target.value })} />
                      </label>
                    ))}
                  </div>
                </section>
              ))}
            </fieldset>
          )}
          {avisoFormulario && <p role="status" className="registro-unico-aviso">{avisoFormulario}</p>}
          {errorFormulario && <p role="alert" className="registro-unico-error">{errorFormulario}</p>}
          <div className="pacientes-acciones registro-unico-acciones">
            <button className="pacientes-boton" type="submit" disabled={guardando || organizando || cargandoEdicion}>
              {guardando ? "Guardando registro..." : "Guardar sesión"}
            </button>
            <button type="button" onClick={cerrarFormulario} disabled={guardando || organizando}>Cancelar</button>
          </div>
          <p className="registro-unico-ayuda">La sesión y sus observaciones se guardan juntas. Ninguna sugerencia de IA se guarda sin tu confirmación.</p>
        </form>
      )}

      {meses.length > 1 && <label className="filtro-mes-sesiones">Filtrar por mes
        <select value={mesFiltro} onChange={(e) => setMesFiltro(e.target.value)}>
          <option value="todos">Todas las sesiones</option>
          {meses.map((mes) => <option value={mes} key={mes}>{new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(`${mes}-01T12:00:00`))}</option>)}
        </select>
      </label>}
      <div className="seguimiento-lista">
        {sesionesVisibles.map((sesion) => (
          <div key={sesion.id} className="sesion-contenedor">
            <div className={`seguimiento-fila ${sesionSeleccionada === sesion.id ? "resaltada" : ""}`} id={`sesion-${sesion.id}`}>
              <div>
                <strong>{mostrarFecha(sesion.fecha)} · {sesion.presente ? "Presente" : "Ausente"}</strong>
                {sesion.nota_general && <p>{sesion.nota_general}</p>}
              </div>
              <div className="seguimiento-acciones">
                <button type="button" onClick={() => setSesionSeleccionada((id) => id === sesion.id ? null : sesion.id)}>
                  {sesionSeleccionada === sesion.id ? "Ocultar detalle" : "Ver detalle"}
                </button>
                <button type="button" onClick={() => void abrirEdicion(sesion)} disabled={guardando || organizando}>
                  Editar registro
                </button>
              </div>
            </div>
            {sesionSeleccionada === sesion.id && (
              <div className="seguimiento-subpanel" id="sesion-detalle">
                {objetivoOrigen != null && onVolverObjetivo && (
                  <button type="button" className="texto-accion" onClick={() => onVolverObjetivo(objetivoOrigen)}>← Volver al objetivo</button>
                )}
                <div className="admision-cabecera">
                  <h3>Observaciones · {mostrarFecha(sesion.fecha)}</h3>
                  <button type="button" className="registro-unico-agregar" onClick={() => void abrirEdicion(sesion)}>Editar sesión y observaciones</button>
                </div>
                {cargandoObs && <p className="pacientes-descripcion">Cargando observaciones...</p>}
                {errorObs && <p role="alert">{errorObs}</p>}
                {!cargandoObs && !errorObs && observaciones.length === 0 && <p className="pacientes-descripcion">Esta sesión no tiene observaciones.</p>}
                {!cargandoObs && observaciones.map((obs, indice) => (
                  <div className="seguimiento-registro" key={obs.id}>
                    <strong>Observación {indice + 1}</strong>
                    {obs.objetivo_id !== null && <p><b>Objetivo:</b> {objetivos.find((o) => o.id === obs.objetivo_id)?.descripcion ?? "Objetivo no disponible"}</p>}
                    {nombresCampos.map((campo) => obs[campo] && <p key={campo}><b>{etiquetas[campo]}:</b> {obs[campo]}</p>)}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
