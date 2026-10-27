import { useEffect, useState, type FormEvent } from "react";
import { Check, FilePlus2, FileText, Pencil, RotateCcw } from "lucide-react";
import {
  crearInforme,
  editarInforme,
  listarInformes,
  type EstadoInforme,
  type Informe,
  type InformeGuardar,
} from "../../servicios/api-informes";
import "./InformesPaciente.css";

type Props = { pacienteId: number };

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
});

const fechaLegible = (valor: string) => valor.split("-").reverse().join("/");
const camposInforme = (informe: Informe): InformeGuardar => ({
  titulo: informe.titulo,
  periodo_desde: informe.periodo_desde,
  periodo_hasta: informe.periodo_hasta,
  contenido: informe.contenido,
});

export default function InformesPaciente({ pacienteId }: Props) {
  const [informes, setInformes] = useState<Informe[]>([]);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [actual, setActual] = useState<Informe | null>(null);
  const [creando, setCreando] = useState(false);
  const [formulario, setFormulario] = useState<InformeGuardar>(formularioVacio);

  useEffect(() => {
    let vigente = true;
    setCargando(true);
    setError("");
    listarInformes(pacienteId)
      .then((datos) => { if (vigente) setInformes(datos); })
      .catch((fallo) => {
        if (vigente) setError(fallo instanceof Error ? fallo.message : "No se pudieron cargar los informes.");
      })
      .finally(() => { if (vigente) setCargando(false); });
    return () => { vigente = false; };
  }, [pacienteId]);

  const editando = creando || actual !== null;
  const cambioPendiente = creando
    ? formulario.titulo.trim() !== "" || formulario.contenido.trim() !== "" ||
      formulario.periodo_desde !== formulario.periodo_hasta
    : actual !== null && JSON.stringify(formulario) !== JSON.stringify(camposInforme(actual));

  function confirmarSalida(): boolean {
    return !cambioPendiente || window.confirm("Hay cambios sin guardar. ¿Querés descartarlos?");
  }

  function nuevoInforme() {
    if (!confirmarSalida()) return;
    setActual(null);
    setCreando(true);
    setFormulario(formularioVacio());
    setError("");
    setMensaje("");
  }

  function seleccionarInforme(informe: Informe) {
    if (actual?.id === informe.id && !creando) return;
    if (!confirmarSalida()) return;
    setActual(informe);
    setCreando(false);
    setFormulario(camposInforme(informe));
    setError("");
    setMensaje("");
  }

  function actualizar(campo: keyof InformeGuardar, valor: string) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }));
    setMensaje("");
  }

  async function guardar(estado?: EstadoInforme) {
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
          <button type="button" className="pacientes-boton" onClick={nuevoInforme}>
            <FilePlus2 size={16} aria-hidden="true" /> Nuevo
          </button>
        </div>
        {cargando ? <p className="informes-aviso">Cargando informes...</p> :
          informes.length === 0 ? <p className="informes-aviso">Todavía no hay informes guardados.</p> :
          <div className="informes-items">
            {informes.map((informe) => (
              <button key={informe.id} type="button"
                className={`informes-item ${actual?.id === informe.id && !creando ? "activo" : ""}`}
                onClick={() => seleccionarInforme(informe)}>
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
            <button type="button" className="pacientes-boton" onClick={nuevoInforme}>Crear informe</button>
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
            <fieldset disabled={guardando}>
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
              <label>Contenido del informe
                <textarea value={formulario.contenido} onChange={(e) => actualizar("contenido", e.target.value)}
                  rows={15} required placeholder="Redactá el informe a partir de los registros del paciente..." />
              </label>
            </fieldset>
            {actual?.asistido_ia && <p className="informes-ayuda">Este informe contiene texto asistido por IA. Revisá su contenido antes de finalizarlo.</p>}
            {error && <p className="informes-error" role="alert">{error}</p>}
            {mensaje && <p className="informes-exito" role="status">{mensaje}</p>}
            <div className="informes-acciones">
              <button type="submit" className="pacientes-boton" disabled={guardando}>
                <Check size={16} aria-hidden="true" /> {guardando ? "Guardando..." : creando ? "Guardar borrador" : "Guardar cambios"}
              </button>
              {!creando && actual?.estado === "borrador" &&
                <button type="button" className="informes-boton-secundario" disabled={guardando}
                  onClick={() => void guardar("finalizado")}>
                  <Pencil size={15} aria-hidden="true" /> Finalizar informe
                </button>}
              {!creando && actual?.estado === "finalizado" &&
                <button type="button" className="informes-boton-secundario" disabled={guardando}
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
