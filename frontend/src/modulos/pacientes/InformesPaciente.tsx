import { periodoSesiones } from "./seguimientoFechas";
import { useEstadoEdicion } from "../../hooks/useEdicion";
import { confirmarSalidaEditor } from "../../hooks/estadoEdicion";
import { useEffect, useState, type FormEvent } from "react";
import { Check, Eye, FilePlus2, FileText, Pencil, RotateCcw, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  crearInforme,
  editarInforme,
  generarBorradorIA,
  listarInformes,
  type EstadoInforme,
  type Informe,
  type InformeGuardar,
} from "../../servicios/api-informes";
import { type Sesion } from "../../servicios/api-seguimiento";
import "./InformesPaciente.css";

type Props = { pacienteId: number; sesiones: Sesion[] | null };

const hoyLocal = () => {
  const ahora = new Date();
  return new Date(ahora.getTime() - ahora.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 10);
};

const formularioVacio = (): InformeGuardar => ({
  titulo: "",
  periodo_desde: hoyLocal(),
  periodo_hasta: hoyLocal(),
  contenido: "",
  asistido_ia: false,
});

const fechaLegible = (valor: string) => valor.split("-").reverse().join("/");
const camposInforme = (informe: Informe): InformeGuardar => ({
  titulo: informe.titulo,
  periodo_desde: informe.periodo_desde,
  periodo_hasta: informe.periodo_hasta,
  contenido: informe.contenido,
  asistido_ia: informe.asistido_ia,
});

export default function InformesPaciente({ pacienteId, sesiones }: Props) {
  const [informes, setInformes] = useState<Informe[]>([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [actual, setActual] = useState<Informe | null>(null);
  const [creando, setCreando] = useState(false);
  const [formulario, setFormulario] = useState<InformeGuardar>(formularioVacio);
  const [baseNueva, setBaseNueva] = useState<InformeGuardar>(formularioVacio);
  const [modoContenido, setModoContenido] = useState<"edicion" | "vista_previa">("edicion");
  const [filtro, setFiltro] = useState<"todos" | EstadoInforme>("todos");

  useEffect(() => {
    let vigente = true;
    listarInformes(pacienteId)
      .then((datos) => { if (vigente) setInformes(datos); })
      .catch((fallo) => {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar los informes.");
      })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [pacienteId]);

  const sesionesEnPeriodo = sesiones?.filter((sesion) =>
    sesion.fecha >= formulario.periodo_desde && sesion.fecha <= formulario.periodo_hasta
  );
  const editando = creando || actual !== null;
  const cambioPendiente = editando && JSON.stringify(formulario) !== JSON.stringify(actual ? camposInforme(actual) : baseNueva);
  useEstadoEdicion(cambioPendiente, guardando || generando);

  const informesFiltrados = filtro === "todos" ? informes : informes.filter((informe) => informe.estado === filtro);

  function nuevoInforme() {
    if (cargando || guardando || generando) return;
    if (!confirmarSalidaEditor()) return;
    setActual(null);
    setCreando(true);
    const nuevo = { ...formularioVacio(), ...periodoSesiones(sesiones ?? [], hoyLocal()) };
    setBaseNueva(nuevo);
    setFormulario(nuevo);
    setModoContenido("edicion");
    setError("");
    setMensaje("");
  }

  function seleccionarInforme(informe: Informe) {
    if (guardando || generando) return;
    if (actual?.id === informe.id && !creando) return;
    if (!confirmarSalidaEditor()) return;
    setActual(informe);
    setCreando(false);
    setFormulario(camposInforme(informe));
    setModoContenido(informe.contenido.trim() ? "vista_previa" : "edicion");
    setError("");
    setMensaje("");
  }

  function actualizar(campo: keyof InformeGuardar, valor: string) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }));
    setMensaje("");
  }

  async function generar() {
    if (guardando || generando) return;
    setError("");
    setMensaje("");
    if (!formulario.titulo.trim() || !formulario.periodo_desde || !formulario.periodo_hasta ||
        formulario.periodo_hasta < formulario.periodo_desde) {
      setError("Completá el título y revisá las fechas antes de generar el borrador.");
      return;
    }
    if (sesionesEnPeriodo && sesionesEnPeriodo.length === 0) {
      setError("No hay sesiones registradas en el período seleccionado. Revisá las fechas antes de generar.");
      return;
    }
    if (formulario.contenido.trim() &&
      !window.confirm("Se reemplazará el texto del editor por el borrador de IA. ¿Continuar?")) return;

    setGenerando(true);
    try {
      const borrador = await generarBorradorIA(pacienteId, {
        titulo: formulario.titulo.trim(),
        periodo_desde: formulario.periodo_desde,
        periodo_hasta: formulario.periodo_hasta,
      });
      setFormulario((anterior) => ({
        ...anterior, contenido: borrador.contenido, asistido_ia: true,
      }));
      setModoContenido("vista_previa");
      setMensaje("Borrador generado. Revisá y corregí el texto antes de guardarlo.");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo generar el borrador.");
    } finally {
      setGenerando(false);
    }
  }

  async function guardar(estado?: EstadoInforme) {
    if (guardando || generando || !editando) return;
    setError("");
    setMensaje("");
    if (!formulario.titulo.trim() || !formulario.contenido.trim()) {
      setError("Completá el título y el contenido del informe.");
      return;
    }
    if (!formulario.periodo_desde || !formulario.periodo_hasta ||
      formulario.periodo_hasta < formulario.periodo_desde) {
      setError("Revisá las fechas del período del informe.");
      return;
    }
    setGuardando(true);
    try {
      const datos = {
        ...formulario,
        titulo: formulario.titulo.trim(),
        contenido: formulario.contenido.trim(),
      };
      const guardado = actual
        ? await editarInforme(pacienteId, actual.id, { ...datos, ...(estado ? { estado } : {}) })
        : await crearInforme(pacienteId, datos);
      setInformes((anteriores) => [guardado, ...anteriores.filter((informe) => informe.id !== guardado.id)]
        .sort((a, b) => b.fecha.localeCompare(a.fecha) || b.id - a.id));
      setActual(guardado);
      setCreando(false);
      setFormulario(camposInforme(guardado));
      setMensaje(estado === "finalizado" ? "Informe finalizado y guardado." :
        estado === "borrador" ? "El informe volvió a borrador." : "Informe guardado correctamente.");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo guardar el informe.");
    } finally {
      setGuardando(false);
    }
  }

  function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    void guardar();
  }

  return (
    <section className="informes-layout" aria-label="Gestión de informes">
      <div className="pacientes-panel informes-listado">
        <div className="informes-listado-cabecera">
          <div>
            <h3>Informes guardados</h3>
            <p>Registros del seguimiento</p>
          </div>
          <button type="button" className="pacientes-boton" onClick={nuevoInforme} disabled={cargando || guardando || generando}>
            <FilePlus2 size={16} aria-hidden="true" /> Nuevo
          </button>
        </div>
        <div className="filtros-informes" role="group" aria-label="Filtrar informes">
          {(["todos", "borrador", "finalizado"] as const).map((estado) => (
            <button type="button" key={estado} className={`filtro-pildora ${filtro === estado ? "seleccionado" : ""}`}
              aria-pressed={filtro === estado} onClick={() => setFiltro(estado)}>
              {estado === "todos" ? "Todos" : estado === "borrador" ? "Borradores" : "Finalizados"}
            </button>
          ))}
        </div>
        {cargando ? <p className="informes-aviso">Cargando informes...</p> :
          informes.length === 0 ? <p className="informes-aviso">Todavía no hay informes guardados.</p> :
          informesFiltrados.length === 0 ? <p className="informes-aviso">No hay informes con este estado.</p> :
          <div className="informes-items">
            {informesFiltrados.map((informe) => (
              <button key={informe.id} type="button"
                className={`informes-item ${actual?.id === informe.id && !creando ? "activo" : ""}`}
                onClick={() => seleccionarInforme(informe)} disabled={guardando || generando}>
                <span className="informes-item-titulo"><FileText size={16} aria-hidden="true" /> {informe.titulo}</span>
                <span className="informes-item-periodo">{fechaLegible(informe.periodo_desde)} – {fechaLegible(informe.periodo_hasta)}</span>
                <span className="informes-item-pie">
                  <span className={`informes-estado ${informe.estado}`}>{informe.estado === "borrador" ? "Borrador" : "Finalizado"}</span>
                  {informe.asistido_ia && <span className="informes-marca-ia">Asistido por IA</span>}
                </span>
              </button>
            ))}
          </div>}
      </div>

      <div className="pacientes-panel informes-editor">
        {!editando ? (
          <div className="informes-sin-seleccion">
            <FileText size={29} strokeWidth={1.6} aria-hidden="true" />
            <h3>Redactar o revisar un informe</h3>
            <p>Seleccioná un informe guardado o creá uno nuevo. Los borradores se pueden continuar más adelante.</p>
            <button type="button" className="pacientes-boton" onClick={nuevoInforme} disabled={cargando || guardando || generando}>Crear informe</button>
          </div>
        ) : (
          <form onSubmit={enviar} className="informes-formulario">
            <div className="informes-editor-cabecera">
              <div>
                <p className="vista-sobretitulo">DOCUMENTACIÓN DEL SEGUIMIENTO</p>
                <h3>{creando ? "Nuevo informe" : "Editar informe"}</h3>
              </div>
              {!creando && actual && <span className={`informes-estado ${actual.estado}`}>
                {actual.estado === "borrador" ? "Borrador" : "Finalizado"}
              </span>}
            </div>
            <fieldset disabled={guardando || generando}>
              <label>Título
                <input value={formulario.titulo} onChange={(e) => actualizar("titulo", e.target.value)}
                  maxLength={200} required placeholder="Ej.: Informe de seguimiento trimestral" />
              </label>
              <div className="informes-periodo">
                <label>Período desde
                  <input type="date" value={formulario.periodo_desde}
                    onChange={(e) => actualizar("periodo_desde", e.target.value)} required />
                </label>
                <label>Período hasta
                  <input type="date" value={formulario.periodo_hasta}
                    onChange={(e) => actualizar("periodo_hasta", e.target.value)} required />
                </label>
              </div>
              {sesionesEnPeriodo && <p className="informes-ayuda">
                {sesionesEnPeriodo.length === 0
                  ? "No hay sesiones registradas entre esas fechas."
                  : `${sesionesEnPeriodo.length} sesión(es) registradas en el período seleccionado.`}
              </p>}
              <div className="informes-contenido">
                <div className="informes-contenido-cabecera">
                  <span>Contenido del informe</span>
                  <div className="informes-contenido-modos" role="group" aria-label="Modo de visualización">
                    <button type="button"
                      className={modoContenido === "edicion" ? "activo" : ""}
                      onClick={() => setModoContenido("edicion")}
                      aria-pressed={modoContenido === "edicion"}>
                      <Pencil size={15} aria-hidden="true" /> Editar
                    </button>
                    <button type="button"
                      className={modoContenido === "vista_previa" ? "activo" : ""}
                      onClick={() => setModoContenido("vista_previa")}
                      aria-pressed={modoContenido === "vista_previa"}>
                      <Eye size={15} aria-hidden="true" /> Vista previa
                    </button>
                  </div>
                </div>
                {modoContenido === "edicion" ? (
                  <textarea value={formulario.contenido} onChange={(e) => actualizar("contenido", e.target.value)}
                    rows={15} placeholder="Redactá el informe a partir de los registros del paciente..." />
                ) : (
                  <div className="informes-preview">
                    {formulario.contenido.trim() ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{formulario.contenido}</ReactMarkdown>
                    ) : (
                      <p className="informes-preview-vacio">Todavía no hay contenido para mostrar.</p>
                    )}
                  </div>
                )}
              </div>
            </fieldset>
            {formulario.asistido_ia && <p className="informes-ayuda informes-revision">Este borrador fue asistido por IA. Revisá su contenido antes de finalizarlo.</p>}
            {error && <p className="informes-error" role="alert">{error}</p>}
            {mensaje && <p className="informes-exito" role="status">{mensaje}</p>}
            <div className="informes-acciones">
              {(creando || actual?.estado === "borrador") &&
                <button type="button" className="informes-boton-secundario"
                  disabled={guardando || generando} onClick={() => void generar()}>
                  <Sparkles size={16} aria-hidden="true" /> {generando ? "Generando..." : "Generar con IA"}
                </button>}
              <button type="submit" className="pacientes-boton" disabled={guardando || generando}>
                <Check size={16} aria-hidden="true" /> {guardando ? "Guardando..." : creando ? "Guardar borrador" : "Guardar cambios"}
              </button>
              {!creando && actual?.estado === "borrador" &&
                <button type="button" className="informes-boton-secundario" disabled={guardando || generando}
                  onClick={() => void guardar("finalizado")}>
                  <Pencil size={15} aria-hidden="true" /> Finalizar informe
                </button>}
              {!creando && actual?.estado === "finalizado" &&
                <button type="button" className="informes-boton-secundario" disabled={guardando || generando}
                  onClick={() => void guardar("borrador")}>
                  <RotateCcw size={15} aria-hidden="true" /> Volver a borrador
                </button>}
            </div>
            <p className="informes-ayuda">El informe se guarda únicamente cuando seleccionás una acción. Finalizar no impide editarlo después.</p>
          </form>
        )}
      </div>
    </section>
  );
}
