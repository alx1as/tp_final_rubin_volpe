import { useCallback, useEffect, useState, type KeyboardEvent } from "react";
import { ArrowLeft, ArrowRight, CalendarDays, ClipboardList, FilePlus2, FileText, GraduationCap, Layers3, UserRound, UsersRound, Target, Activity, Clock3, Plus, ChevronRight, BookOpenText, MapPinned, ShieldCheck } from "lucide-react";
import { listarSesiones, type Sesion } from "../../servicios/api-seguimiento";
import { obtenerAdmision, guardarAdmision, listarEscolaridades, guardarEscolaridad, listarProfesionalesTratantes, guardarProfesionalTratante, listarObjetivos, guardarObjetivo } from "../../servicios/api";

import type { Paciente } from "./Pacientes";
import AdmisionPaciente, { type Admision } from "./AdmisionPaciente";
import EscolaridadPaciente, { type Escolaridad, type EscolaridadGuardar } from "./EscolaridadPaciente";
import ProfesionalesIntervinientes, { type ProfesionalTratante, type ProfesionalTratanteGuardar } from "./ProfesionalesIntervinientes";
import ObjetivosPaciente, { type Objetivo, type ObjetivoGuardar } from "./ObjetivosPaciente";
import SesionesPaciente from "./SesionesPaciente";
import InformesPaciente from "./InformesPaciente";
import DatosPersonalesPaciente from "./DatosPersonalesPaciente";
import CronologiaPaciente from "./CronologiaPaciente";
import "./Redisenio.css";

type Pestana = "resumen" | "seguimiento" | "informes" | "informacion";

type Props = {
  paciente: Paciente;
  onVolver: () => void;
  onPacienteActualizado: (actualizado: Paciente) => void;
};

export default function FichaPaciente({
  paciente,
  onVolver,
  onPacienteActualizado,
}: Props) {
  const [admision, setAdmision] = useState<Admision | null>(null);
  const [cargandoAdmision, setCargandoAdmision] = useState(true);
  const [errorAdmision, setErrorAdmision] = useState("");
  const [escolaridades, setEscolaridades] = useState<Escolaridad[]>([]);
  const [cargandoEscolaridad, setCargandoEscolaridad] = useState(true);
  const [errorEscolaridad, setErrorEscolaridad] = useState("");
  const [profesionales, setProfesionales] = useState<ProfesionalTratante[]>([]);
  const [cargandoProfesionales, setCargandoProfesionales] = useState(true);
  const [errorProfesionales, setErrorProfesionales] = useState("");
  const [objetivos, setObjetivos] = useState<Objetivo[]>([]);
  const [cargandoObjetivos, setCargandoObjetivos] = useState(true);
  const [errorObjetivos, setErrorObjetivos] = useState("");
  const [revisionEvidencias, setRevisionEvidencias] = useState(0);
  const [pestana, setPestana] = useState<Pestana>("resumen");
  const [sesionesResumen, setSesionesResumen] = useState<Sesion[]>([]);
  const [cargandoSesionesResumen, setCargandoSesionesResumen] = useState(true);
  const [revisionSesiones, setRevisionSesiones] = useState(0);
  const [errorSesionesResumen, setErrorSesionesResumen] = useState("");
  const [vistaSeguimiento, setVistaSeguimiento] = useState<"sesiones" | "objetivos">("sesiones");
  const [detalleInformacion, setDetalleInformacion] = useState<"datos" | "admision" | "escolaridad" | "profesionales" | null>(null);
  const [mesCronologia, setMesCronologia] = useState<string | null>(null);
  const [sesionDestino, setSesionDestino] = useState<number | null>(null);
  const [objetivoOrigen, setObjetivoOrigen] = useState<number | null>(null);
  const [objetivoDestino, setObjetivoDestino] = useState<number | null>(null);
  const [solicitudNueva, setSolicitudNueva] = useState(0);
  const confirmarSolicitudNueva = useCallback(() => setSolicitudNueva(0), []);

  useEffect(() => {
    if (!mesCronologia) return;
    const cerrar = (evento: globalThis.KeyboardEvent) => {
      if (evento.key === "Escape") setMesCronologia(null);
    };
    window.addEventListener("keydown", cerrar);
    return () => window.removeEventListener("keydown", cerrar);
  }, [mesCronologia]);

  useEffect(() => {
    let vigente = true;
    setCargandoSesionesResumen(true);
    setErrorSesionesResumen("");
    listarSesiones(paciente.id)
      .then((datos) => { if (vigente) setSesionesResumen(datos); })
      .catch((fallo) => {
        if (vigente) {
          setSesionesResumen([]);
          setErrorSesionesResumen(fallo instanceof Error ? fallo.message : "No se pudieron cargar las sesiones.");
        }
      })
      .finally(() => { if (vigente) setCargandoSesionesResumen(false); });
    return () => { vigente = false; };
  }, [paciente.id, revisionSesiones]);

  useEffect(() => {
    let vigente = true;
    setCargandoAdmision(true);
    setErrorAdmision("");

    obtenerAdmision(paciente.id)
      .then((datos) => {
        if (vigente) setAdmision(datos);
      })
      .catch((fallo) => {
        if (vigente) {
          setErrorAdmision(
            fallo instanceof Error ? fallo.message : "No se pudo cargar la admisión."
          );
        }
      })
      .finally(() => {
        if (vigente) setCargandoAdmision(false);
      });

    return () => {
      vigente = false;
    };
  }, [paciente.id]);

  useEffect(() => {
    let vigente = true;
    setCargandoEscolaridad(true);
    setErrorEscolaridad("");
    setEscolaridades([]);

    listarEscolaridades(paciente.id)
      .then((datos) => {
        if (vigente) setEscolaridades(datos);
      })
      .catch((fallo) => {
        if (vigente) {
          setErrorEscolaridad(
            fallo instanceof Error ? fallo.message : "No se pudo cargar la escolaridad."
          );
        }
      })
      .finally(() => {
        if (vigente) setCargandoEscolaridad(false);
      });

    return () => {
      vigente = false;
    };
  }, [paciente.id]);

  useEffect(() => {
    let vigente = true;
    setCargandoProfesionales(true);
    setErrorProfesionales("");
    setProfesionales([]);

    listarProfesionalesTratantes(paciente.id)
      .then((datos) => {
        if (vigente) setProfesionales(datos);
      })
      .catch((fallo) => {
        if (vigente) {
          setErrorProfesionales(
            fallo instanceof Error ? fallo.message : "No se pudieron cargar los profesionales."
          );
        }
      })
      .finally(() => {
        if (vigente) setCargandoProfesionales(false);
      });

    return () => { vigente = false; };
  }, [paciente.id]);

  useEffect(() => {
    let vigente = true;
    setCargandoObjetivos(true);
    setErrorObjetivos("");
    setObjetivos([]);

    listarObjetivos(paciente.id)
      .then((datos) => {
        if (vigente) setObjetivos(datos);
      })
      .catch((fallo) => {
        if (vigente) setErrorObjetivos(
          fallo instanceof Error ? fallo.message : "No se pudieron cargar los objetivos."
        );
      })
      .finally(() => { if (vigente) setCargandoObjetivos(false); });

    return () => { vigente = false; };
  }, [paciente.id]);

  async function guardarObjetivoPaciente(datos: ObjetivoGuardar, id?: number): Promise<void> {
    setErrorObjetivos("");
    try {
      const guardado = await guardarObjetivo(paciente.id, datos, id);
      setObjetivos((actuales) =>
        id === undefined
          ? [guardado, ...actuales]
          : actuales.map((registro) => registro.id === guardado.id ? guardado : registro)
      );
    } catch (fallo) {
      setErrorObjetivos(
        fallo instanceof Error ? fallo.message : "No se pudo guardar el objetivo."
      );
      throw fallo;
    }
  }

  async function guardarProfesionalPaciente(
    datos: ProfesionalTratanteGuardar, id?: number
  ): Promise<void> {
    setErrorProfesionales("");
    try {
      const guardado = await guardarProfesionalTratante(paciente.id, datos, id);
      setProfesionales((actuales) =>
        id === undefined
          ? [guardado, ...actuales]
          : actuales.map((registro) => registro.id === guardado.id ? guardado : registro)
      );
    } catch (fallo) {
      setErrorProfesionales(
        fallo instanceof Error ? fallo.message : "No se pudo guardar el profesional."
      );
      throw fallo;
    }
  }

  async function guardarEscolaridadPaciente(
    datos: EscolaridadGuardar, id?: number
  ): Promise<void> {
    setErrorEscolaridad("");
    try {
      const guardado = await guardarEscolaridad(paciente.id, datos, id);
      setEscolaridades((actuales) =>
        id === undefined
          ? [guardado, ...actuales]
          : actuales.map((registro) => registro.id === guardado.id ? guardado : registro)
      );
    } catch (fallo) {
      setErrorEscolaridad(
        fallo instanceof Error ? fallo.message : "No se pudo guardar la escolaridad."
      );
      throw fallo;
    }
  }

  async function guardarAdmisionPaciente(datos: Admision): Promise<void> {
    setErrorAdmision("");
    try {
      const guardada = await guardarAdmision(paciente.id, datos);
      setAdmision(guardada);
    } catch (fallo) {
      setErrorAdmision(
        fallo instanceof Error ? fallo.message : "No se pudo guardar la admisión."
      );
      throw fallo;
    }
  }

  const fecha = (valor: string | null | undefined) => valor ? valor.split("-").reverse().join("/") : "Sin fecha";
  const hoy = new Date();
  const fechaActual = [hoy.getFullYear(), String(hoy.getMonth() + 1).padStart(2, "0"), String(hoy.getDate()).padStart(2, "0")].join("-");
  const nacimiento = paciente.fecha_nacimiento?.split("-").map(Number);
  const edad = nacimiento?.length === 3 && nacimiento.every(Number.isFinite)
    ? hoy.getFullYear() - nacimiento[0] - (fechaActual.slice(5) < paciente.fecha_nacimiento.slice(5) ? 1 : 0)
    : null;
  const edadLegible = edad !== null && edad >= 0 && edad <= 120 ? `${edad} años` : "Edad no disponible";
  const activos = objetivos.filter((objetivo) => objetivo.estado === "activo");
  const ultimaSesion = [...sesionesResumen].sort((a, b) => b.fecha.localeCompare(a.fecha) || b.id - a.id)[0];
  const escolaridadActual = [...escolaridades]
    .filter((registro) => !registro.fecha_fin && registro.fecha_inicio <= fechaActual)
    .sort((a, b) => b.fecha_inicio.localeCompare(a.fecha_inicio))[0];
  const meses = Object.entries(sesionesResumen.reduce<Record<string, number>>((acum, sesion) => {
    const mes = sesion.fecha.slice(0, 7);
    acum[mes] = (acum[mes] ?? 0) + 1;
    return acum;
  }, {})).sort(([a], [b]) => b.localeCompare(a));
  const nombreMes = (mes: string) => new Intl.DateTimeFormat("es-AR", { month: "short", year: "numeric" })
    .format(new Date(`${mes}-01T12:00:00`));
  const tabs: { id: Pestana; texto: string; icono: typeof Layers3 }[] = [
    { id: "resumen", texto: "Inicio", icono: Layers3 },
    { id: "informacion", texto: "Historia y contexto", icono: BookOpenText },
    { id: "seguimiento", texto: "Seguimiento", icono: Activity },
    { id: "informes", texto: "Informes", icono: FileText },
  ];

  function hayFormularioSinGuardar() {
    const panel = document.querySelector(`#panel-${pestana}`);
    // Los editores de registros se desmontan al navegar, por eso se solicita confirmación.
    const formularioAbierto = panel?.querySelector("form.admision-formulario, form.ficha-datos-formulario");
    const informePendiente = panel?.querySelector('[data-pendiente="true"]');
    return Boolean(formularioAbierto || informePendiente);
  }
  function confirmarNavegacion() {
    return !hayFormularioSinGuardar() || window.confirm("Hay un formulario abierto con posibles cambios sin guardar. ¿Querés salir de esta vista?");
  }
  function cambiarPestana(valor: Pestana) {
    if (valor === pestana || !confirmarNavegacion()) return false;
    setPestana(valor);
    window.scrollTo({ top: 0, behavior: "instant" });
    return true;
  }
  function cambiarDetalle(valor: typeof detalleInformacion) {
    if (detalleInformacion === valor || !confirmarNavegacion()) return;
    setDetalleInformacion(valor);
  }
  function abrirNuevaSesion() {
    if (pestana !== "seguimiento" && !cambiarPestana("seguimiento")) return;
    if (pestana === "seguimiento" && !confirmarNavegacion()) return;
    setVistaSeguimiento("sesiones");
    setSesionDestino(null);
    setObjetivoOrigen(null);
    setSolicitudNueva((n) => n + 1);
  }
  function abrirSeguimiento(seccion: "sesiones" | "objetivos") {
    if (pestana !== "seguimiento" && !cambiarPestana("seguimiento")) return;
    if (pestana === "seguimiento" && seccion !== vistaSeguimiento && !confirmarNavegacion()) return;
    setVistaSeguimiento(seccion);
    setObjetivoOrigen(null);
    if (seccion === "sesiones") setSesionDestino(null);
  }
  function abrirSesion(id: number, objetivoId?: number) {
    if (pestana !== "seguimiento" && !cambiarPestana("seguimiento")) return;
    if (pestana === "seguimiento" && !confirmarNavegacion()) return;
    setVistaSeguimiento("sesiones");
    setObjetivoOrigen(objetivoId ?? null);
    setSesionDestino(id);
    setMesCronologia(null);
    window.setTimeout(() => document.getElementById(`sesion-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 100);
  }
  function volverObjetivo(id: number) {
    if (!confirmarNavegacion()) return;
    setObjetivoDestino(id);
    setVistaSeguimiento("objetivos");
    window.setTimeout(() => document.getElementById(`objetivo-${id}`)?.scrollIntoView({ behavior: "smooth", block: "center" }), 100);
  }
  function navegarPestanas(evento: KeyboardEvent<HTMLButtonElement>, indice: number) {
    const siguiente = evento.key === "ArrowRight" ? (indice + 1) % tabs.length
      : evento.key === "ArrowLeft" ? (indice - 1 + tabs.length) % tabs.length
      : evento.key === "Home" ? 0 : evento.key === "End" ? tabs.length - 1 : null;
    if (siguiente === null) return;
    evento.preventDefault();
    if (cambiarPestana(tabs[siguiente].id)) document.getElementById(`pestana-${tabs[siguiente].id}`)?.focus();
  }
  const categorias = [
    { id: "datos", titulo: "Datos personales", descripcion: "Identificación y fechas del seguimiento", contenido: `${edadLegible} · ${paciente.activo ? "Seguimiento activo" : "Inactivo"}`, icono: UserRound },
    { id: "admision", titulo: "Admisión y antecedentes", descripcion: "Motivo de consulta, historia evolutiva y familiar", contenido: cargandoAdmision ? "Cargando..." : admision?.motivo_consulta || "Motivo de consulta pendiente", icono: ClipboardList },
    { id: "escolaridad", titulo: "Trayectoria escolar", descripcion: "Instituciones, períodos y apoyos registrados", contenido: cargandoEscolaridad ? "Cargando..." : escolaridadActual?.institucion || `${escolaridades.length} período(s) registrados`, icono: GraduationCap },
    { id: "profesionales", titulo: "Profesionales intervinientes", descripcion: "Equipo que participa del acompañamiento", contenido: cargandoProfesionales ? "Cargando..." : `${profesionales.length} profesional(es) vinculados`, icono: UsersRound },
  ] as const;

  return (
    <div className="pagina-pacientes pagina-ficha ficha-redisenio">
      <button type="button" className="ficha-volver" onClick={() => { if (confirmarNavegacion()) onVolver(); }}>
        <ArrowLeft size={16} aria-hidden="true" /> Pacientes
      </button>

      <header className="ficha-hero">
        <div className="ficha-hero-identidad">
          <div className="ficha-monograma" aria-hidden="true">{paciente.nombre[0]}{paciente.apellido[0]}</div>
          <div className="ficha-hero-textos">
            <p className="ficha-sobretitulo">ESPACIO DE SEGUIMIENTO</p>
            <h1>{paciente.nombre} {paciente.apellido}</h1>
            <div className="ficha-meta">
              <span>{edadLegible}</span><span aria-hidden="true">·</span>
              <span>{escolaridadActual ? `${escolaridadActual.nivel} · ${escolaridadActual.grado_anio_sala}` : "Escolaridad sin actualizar"}</span>
            </div>
            {!cargandoAdmision && admision?.motivo_consulta && <p className="ficha-motivo"><strong>Motivo:</strong> {admision.motivo_consulta}</p>}
            <div className="ficha-meta estado-paciente">
              <span className={`ficha-estado ${paciente.activo ? "" : "inactivo"}`}><span aria-hidden="true" className="punto-estado" />{paciente.activo ? "Activo" : "Inactivo"}</span>
              <span><CalendarDays size={14} aria-hidden="true"/> Desde {fecha(paciente.fecha_inicio_seguimiento)}</span>
            </div>
          </div>
        </div>
        <div className="ficha-acciones-principales">
          <button type="button" className="pacientes-boton" onClick={abrirNuevaSesion}><Plus size={17}/> Nueva sesión</button>
          <button type="button" className="boton-secundario" onClick={() => abrirSeguimiento("objetivos")}><Target size={17}/> Objetivos</button>
          <button type="button" className="boton-secundario" onClick={() => cambiarPestana("informes")}><FilePlus2 size={17}/> Informes</button>
        </div>
      </header>

      <div className="navegador-ficha" role="tablist" aria-label="Secciones del paciente">
        {tabs.map(({id, texto, icono: Icono}, indice) => (
          <button key={id} type="button" role="tab" id={`pestana-${id}`}
            aria-selected={pestana === id} aria-controls={`panel-${id}`}
            tabIndex={pestana === id ? 0 : -1} onClick={() => cambiarPestana(id)}
            onKeyDown={(e) => navegarPestanas(e, indice)}
            className={`ficha-tab ${pestana === id ? "seleccionada" : ""}`}>
            <Icono size={18} strokeWidth={1.85} aria-hidden="true" /> <span>{texto}</span>
          </button>
        ))}
      </div>

      <div className="ficha-espacio">
        <div className="ficha-contenido" aria-label="Contenido de la ficha">
          <div id="panel-resumen" role="tabpanel" aria-labelledby="pestana-resumen" hidden={pestana !== "resumen"} className="vista-pestana">
          {pestana === "resumen" && <>
            <div className="vista-encabezado"><div><p className="vista-sobretitulo">CONTINUIDAD DEL ACOMPAÑAMIENTO</p><h2>Para retomar el trabajo</h2>
              <p>Lo más importante del paciente, sin recorrer toda su ficha.</p></div></div>
            <section className="resumen-destacado" aria-label="Última sesión">
              <div className="resumen-destacado-cabecera"><span className="etiqueta-suave"><Clock3 size={16}/> ACTIVIDAD RECIENTE</span>
                <button className="texto-accion" type="button" onClick={() => abrirSeguimiento("sesiones")}>Todas las sesiones <ArrowRight size={16}/></button>
              </div>
              <h3>Última sesión</h3>
              {cargandoSesionesResumen ? <p className="texto-atenuado">Cargando actividad...</p> : errorSesionesResumen ? <p role="alert">{errorSesionesResumen}</p> : ultimaSesion ? <>
                <div className="ultima-sesion-resumen"><span className="fecha-grande">{fecha(ultimaSesion.fecha)}</span>
                  <span className={`estado-asistencia ${ultimaSesion.presente ? "" : "ausente"}`}>{ultimaSesion.presente ? "Asistió" : "Ausente"}</span></div>
                <p className="nota-resumen">{ultimaSesion.nota_general || "Sin nota general registrada."}</p>
                <button className="texto-accion" type="button" onClick={() => abrirSesion(ultimaSesion.id)}>Abrir esta sesión <ArrowRight size={16}/></button>
              </> : <><p className="texto-atenuado">Todavía no hay sesiones registradas.</p>
                <button className="texto-accion" type="button" onClick={abrirNuevaSesion}>Registrar primera sesión <ArrowRight size={16}/></button></>}
            </section>
            <div className="resumen-grilla-redisenio">
              <section className="pacientes-panel resumen-panel">
                <div className="resumen-panel-cabecera"><div className="titulo-icono"><Target size={18}/><h3>Objetivos activos</h3></div><span className="contador-suave">{cargandoObjetivos ? "…" : activos.length}</span></div>
                {cargandoObjetivos ? <p className="texto-atenuado">Cargando objetivos...</p> : errorObjetivos ? <p role="alert">{errorObjetivos}</p> : activos.length ? <div className="lista-resumen-objetivos">{activos.slice(0, 4).map((objetivo) =>
                  <div className="objetivo-preview" key={objetivo.id}><span className="punto-objetivo" aria-hidden="true"/><span>{objetivo.descripcion}</span></div>
                )}</div> : <p className="texto-atenuado">No hay objetivos activos registrados.</p>}
                <button className="texto-accion" type="button" onClick={() => abrirSeguimiento("objetivos")}>Consultar objetivos y evidencias <ArrowRight size={16}/></button>
              </section>
              <section className="pacientes-panel resumen-panel">
                <div className="resumen-panel-cabecera"><div className="titulo-icono"><ClipboardList size={18}/><h3>Contexto del caso</h3></div></div>
                <span className="resumen-label">Motivo de consulta</span>
                <p className="nota-resumen">{cargandoAdmision ? "Cargando..." : errorAdmision || admision?.motivo_consulta || "Aún no registrado."}</p>
                <span className="resumen-label">Escolaridad actual</span>
                <p>{cargandoEscolaridad ? "Cargando..." : errorEscolaridad || escolaridadActual?.institucion || "No consta escolaridad vigente."}</p>
                <button className="texto-accion" type="button" onClick={() => cambiarPestana("informacion")}>Historia y contexto <ArrowRight size={16}/></button>
              </section>
            </div>
            <div className="resumen-indicadores resumen-indicadores-pequenos">
              <div className="indicador"><span className="indicador-icono tono-verde"><CalendarDays size={19}/></span><div><strong>{cargandoSesionesResumen || errorSesionesResumen ? "—" : sesionesResumen.length}</strong><span>Sesiones</span></div></div>
              <div className="indicador"><span className="indicador-icono tono-violeta"><Target size={19}/></span><div><strong>{cargandoObjetivos || errorObjetivos ? "—" : activos.length}</strong><span>Objetivos activos</span></div></div>
              <div className="indicador"><span className="indicador-icono tono-ambar"><UsersRound size={19}/></span><div><strong>{cargandoProfesionales || errorProfesionales ? "—" : profesionales.length}</strong><span>Profesionales</span></div></div>
            </div>
          </>}
          </div>

          <div id="panel-informacion" role="tabpanel" aria-labelledby="pestana-informacion" hidden={pestana !== "informacion"} className="vista-pestana">
          {pestana === "informacion" && <>
            <div className="vista-encabezado"><div><p className="vista-sobretitulo">EL PACIENTE Y SU CONTEXTO</p><h2>Historia y contexto</h2>
              <p>Consultá la información por temas y editá solamente cuando lo necesites.</p></div></div>
            {detalleInformacion === null ? (
              <div className="historia-categorias">
                {categorias.map(({ id, titulo, descripcion, contenido, icono: Icono }) => <button type="button" className="historia-categoria" key={id} onClick={() => cambiarDetalle(id)}>
                  <span className="historia-icono"><Icono size={22}/></span><span className="historia-categoria-textos"><strong>{titulo}</strong><small>{descripcion}</small><span className="historia-resumen">{contenido}</span></span><ChevronRight size={20} className="historia-flecha"/>
                </button>)}
              </div>
            ) : (
              <div className="historia-detalle">
                <button type="button" className="texto-accion historia-volver" onClick={() => cambiarDetalle(null)}><ArrowLeft size={17}/> Todas las categorías</button>
                <div className="historia-detalle-encabezado"><span className="historia-icono"><MapPinned size={20}/></span>
                  <div><p className="vista-sobretitulo">HISTORIA Y CONTEXTO</p><h3>{categorias.find((categoria) => categoria.id === detalleInformacion)?.titulo}</h3></div>
                </div>
                {detalleInformacion === "datos" && <DatosPersonalesPaciente paciente={paciente} onActualizar={onPacienteActualizado}/>}
                {detalleInformacion === "admision" && <AdmisionPaciente admision={admision} fechaInicial={paciente.fecha_inicio_seguimiento} onGuardar={guardarAdmisionPaciente} cargando={cargandoAdmision} error={errorAdmision}/>}
                {detalleInformacion === "escolaridad" && <EscolaridadPaciente registros={escolaridades} onGuardar={guardarEscolaridadPaciente} cargando={cargandoEscolaridad} error={errorEscolaridad}/>}
                {detalleInformacion === "profesionales" && <ProfesionalesIntervinientes registros={profesionales} onGuardar={guardarProfesionalPaciente} cargando={cargandoProfesionales} error={errorProfesionales}/>}
              </div>
            )}
          </>}
          </div>

          <div id="panel-seguimiento" role="tabpanel" aria-labelledby="pestana-seguimiento" hidden={pestana !== "seguimiento"} className="vista-pestana">
          {pestana === "seguimiento" && <>
            <div className="vista-encabezado"><div><p className="vista-sobretitulo">TRABAJO PROFESIONAL</p><h2>Seguimiento</h2>
              <p>Registrá intervenciones y consultá las evidencias de cada objetivo.</p></div></div>
            <div className="subnavegacion-seguimiento" role="group" aria-label="Tipo de registros de seguimiento">
              <button type="button" className={vistaSeguimiento === "sesiones" ? "activo" : ""} aria-pressed={vistaSeguimiento === "sesiones"} onClick={() => abrirSeguimiento("sesiones")}><CalendarDays size={17}/> Sesiones</button>
              <button type="button" className={vistaSeguimiento === "objetivos" ? "activo" : ""} aria-pressed={vistaSeguimiento === "objetivos"} onClick={() => abrirSeguimiento("objetivos")}><Target size={17}/> Objetivos</button>
            </div>
            {vistaSeguimiento === "sesiones" ? <SesionesPaciente pacienteId={paciente.id} objetivos={objetivos} sesionDestino={sesionDestino} solicitudNueva={solicitudNueva} onSolicitudNuevaProcesada={confirmarSolicitudNueva}
              objetivoOrigen={objetivoOrigen} onVolverObjetivo={volverObjetivo}
              onCambiarObservaciones={() => setRevisionEvidencias((n) => n + 1)} onCambiarSesiones={() => setRevisionSesiones((n) => n + 1)}/> :
              <ObjetivosPaciente registros={objetivos} onGuardar={guardarObjetivoPaciente} cargando={cargandoObjetivos} error={errorObjetivos} pacienteId={paciente.id}
                revisionEvidencias={revisionEvidencias} onVerSesion={abrirSesion} objetivoDestino={objetivoDestino}/>}
          </>}
          </div>

          <div id="panel-informes" role="tabpanel" aria-labelledby="pestana-informes" hidden={pestana !== "informes"} className="vista-pestana">
          {pestana === "informes" && <>
            <div className="vista-encabezado"><div><p className="vista-sobretitulo">DOCUMENTACIÓN DEL ACOMPAÑAMIENTO</p><h2>Informes</h2>
              <p>Consultá borradores, redactá y revisá informes del paciente.</p></div></div>
            <InformesPaciente pacienteId={paciente.id}/>
          </>}
          </div>
        </div>

        <aside className="ficha-cronologia-lateral" aria-label="Navegación por meses">
          <div className="cronologia-lateral-cabecera"><span className="cronologia-lateral-icono"><Clock3 size={18}/></span>
            <div><h3>Actividad</h3><p>Por mes</p></div></div>
          <div className="cronologia-meses">
            {cargandoSesionesResumen && <p className="texto-atenuado">Cargando...</p>}
            {errorSesionesResumen && <p role="alert">{errorSesionesResumen}</p>}
            {!cargandoSesionesResumen && !errorSesionesResumen && meses.length === 0 && <p className="texto-atenuado">Sin sesiones registradas.</p>}
            {meses.map(([mes, cantidad]) => <button key={mes} type="button" className={`cronologia-mes ${mesCronologia === mes ? "activo" : ""}`}
              aria-expanded={mesCronologia === mes} onClick={() => setMesCronologia((anterior) => anterior === mes ? null : mes)}>
              <span>{nombreMes(mes)}</span><small>{cantidad} sesión{cantidad === 1 ? "" : "es"}</small>
            </button>)}
          </div>
          <p className="cronologia-ayuda"><ShieldCheck size={15}/> Registros del paciente seleccionado.</p>
        </aside>
      </div>

      {mesCronologia && <div className="cronologia-panel-flotante" role="region" aria-label="Exploración de la cronología mensual">
        <label className="selector-mes-panel">Mes
          <select value={mesCronologia} onChange={(evento) => setMesCronologia(evento.target.value)}>
            {meses.map(([mes]) => <option value={mes} key={mes}>{nombreMes(mes)}</option>)}
          </select>
        </label>
        <CronologiaPaciente pacienteId={paciente.id} mes={mesCronologia} objetivos={objetivos}
          revision={revisionSesiones + revisionEvidencias} onVerSesion={(id) => abrirSesion(id)} onCerrar={() => setMesCronologia(null)}/>
      </div>}
      <button type="button" className="boton-cronologia-movil" aria-expanded={mesCronologia !== null}
        onClick={() => setMesCronologia((actual) => actual ? null : (meses[0]?.[0] ?? null))}>
        <Clock3 size={17}/> {mesCronologia ? "Cerrar actividad" : "Explorar actividad mensual"}
      </button>
    </div>
  );
}
