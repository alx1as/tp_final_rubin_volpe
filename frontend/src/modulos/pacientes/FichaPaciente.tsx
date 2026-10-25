import { useEffect, useState, type KeyboardEvent } from "react";
import { ArrowLeft, ArrowRight, CalendarDays, ClipboardList, FileText, GraduationCap, Layers3, UserRound, UsersRound, Target, Activity } from "lucide-react";
import { listarSesiones, type Sesion } from "../../servicios/api-seguimiento";
import { obtenerAdmision, guardarAdmision, listarEscolaridades, guardarEscolaridad, listarProfesionalesTratantes, guardarProfesionalTratante, listarObjetivos, guardarObjetivo } from "../../servicios/api";

import type { Paciente } from "./Pacientes";
import AdmisionPaciente, { type Admision } from "./AdmisionPaciente";
import EscolaridadPaciente, { type Escolaridad, type EscolaridadGuardar } from "./EscolaridadPaciente";
import ProfesionalesIntervinientes, { type ProfesionalTratante, type ProfesionalTratanteGuardar } from "./ProfesionalesIntervinientes";
import ObjetivosPaciente, { type Objetivo, type ObjetivoGuardar } from "./ObjetivosPaciente";
import SesionesPaciente from "./SesionesPaciente";

type Pestana = "resumen" | "seguimiento" | "informacion";

type Props = {
  paciente: Paciente;
  onVolver: () => void;
};

export default function FichaPaciente({
  paciente,
  onVolver,
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

  useEffect(() => {
    let vigente = true;
    setCargandoSesionesResumen(true);
    listarSesiones(paciente.id)
      .then((datos) => { if (vigente) setSesionesResumen(datos); })
      .catch(() => { if (vigente) setSesionesResumen([]); })
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

  const fecha = (valor: string) => valor ? valor.split("-").reverse().join("/") : "Sin fecha";
  const activos = objetivos.filter((objetivo) => objetivo.estado === "activo");
  const ultimaSesion = [...sesionesResumen].sort((a, b) => b.fecha.localeCompare(a.fecha) || b.id - a.id)[0];
  const escolaridadActual = escolaridades.find((registro) => !registro.fecha_fin) ?? escolaridades[0];
  const tabs: { id: Pestana; texto: string; icono: typeof Layers3 }[] = [
    { id: "resumen", texto: "Resumen", icono: Layers3 },
    { id: "seguimiento", texto: "Seguimiento", icono: Activity },
    { id: "informacion", texto: "Información", icono: ClipboardList },
  ];
  function cambiarPestana(valor: Pestana) {
    setPestana(valor);
    window.scrollTo({ top: 0, behavior: "instant" });
  }
  function navegarPestanas(evento: KeyboardEvent<HTMLButtonElement>, indice: number) {
    const siguiente = evento.key === "ArrowRight" ? (indice + 1) % tabs.length
      : evento.key === "ArrowLeft" ? (indice - 1 + tabs.length) % tabs.length
      : evento.key === "Home" ? 0 : evento.key === "End" ? tabs.length - 1 : null;
    if (siguiente === null) return;
    evento.preventDefault();
    cambiarPestana(tabs[siguiente].id);
    document.getElementById(`pestana-${tabs[siguiente].id}`)?.focus();
  }

  return (
    <div className="pagina-pacientes pagina-ficha">
      <button type="button" className="ficha-volver" onClick={onVolver}>
        <ArrowLeft size={16} aria-hidden="true" /> Volver a pacientes
      </button>

      <header className="ficha-hero">
        <div className="ficha-hero-identidad">
          <div className="ficha-monograma" aria-hidden="true">{paciente.nombre[0]}{paciente.apellido[0]}</div>
          <div className="ficha-hero-textos">
            <p className="ficha-sobretitulo">FICHA DE SEGUIMIENTO</p>
            <h1>{paciente.apellido}, {paciente.nombre}</h1>
            <p>Registro y evolución psicopedagógica</p>
          </div>
        </div>
        <div className="ficha-hero-detalles">
          <span className={`ficha-estado ${paciente.activo ? "" : "inactivo"}`}>
            <span aria-hidden="true" className="punto-estado" /> {paciente.activo ? "Seguimiento activo" : "Inactivo"}
          </span>
          <span className="ficha-fecha-inicio"><CalendarDays size={15} aria-hidden="true" /> Desde {fecha(paciente.fecha_inicio_seguimiento)}</span>
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

      <div id="panel-resumen" role="tabpanel" aria-labelledby="pestana-resumen" hidden={pestana !== "resumen"} className="vista-pestana">
        <div className="vista-encabezado">
          <div><p className="vista-sobretitulo">EL CASO, EN PERSPECTIVA</p><h2>Vista general</h2>
            <p>Información esencial para retomar el seguimiento.</p></div>
          <button type="button" className="enlace-accion" onClick={() => cambiarPestana("seguimiento")}>
            Abrir seguimiento <ArrowRight size={16} aria-hidden="true" />
          </button>
        </div>
        <div className="resumen-indicadores">
          <div className="indicador"><span className="indicador-icono tono-violeta"><Target size={20} /></span>
            <div><strong>{cargandoObjetivos ? "—" : activos.length}</strong><span>Objetivos activos</span></div></div>
          <div className="indicador"><span className="indicador-icono tono-verde"><CalendarDays size={20} /></span>
            <div><strong>{cargandoSesionesResumen ? "—" : sesionesResumen.length}</strong><span>Sesiones registradas</span></div></div>
          <div className="indicador"><span className="indicador-icono tono-ambar"><UsersRound size={20} /></span>
            <div><strong>{cargandoProfesionales ? "—" : profesionales.length}</strong><span>Profesionales vinculados</span></div></div>
        </div>

        <div className="resumen-grilla">
          <section className="tarjeta-resumen tarjeta-objetivos">
            <div className="tarjeta-cabecera"><span className="tarjeta-icono"><Target size={19} /></span>
              <div><p className="tarjeta-etiqueta">PLAN DE TRABAJO</p><h3>Objetivos en curso</h3></div></div>
            {cargandoObjetivos ? <p className="texto-atenuado">Cargando objetivos...</p> : activos.length ? (
              <div className="lista-resumen-objetivos">{activos.slice(0, 3).map((objetivo) =>
                <div className="objetivo-preview" key={objetivo.id}><span className="punto-objetivo" aria-hidden="true" />
                  <span>{objetivo.descripcion}</span></div>)}
                {activos.length > 3 && <p className="texto-atenuado">Y {activos.length - 3} más</p>}</div>
            ) : <p className="texto-atenuado">Todavía no hay objetivos activos. Podés registrarlos desde Seguimiento.</p>}
            <button className="tarjeta-pie-accion" type="button" onClick={() => cambiarPestana("seguimiento")}>
              Ver objetivos y evidencias <ArrowRight size={16} aria-hidden="true" />
            </button>
          </section>
          <section className="tarjeta-resumen tarjeta-ultima-sesion">
            <div className="tarjeta-cabecera"><span className="tarjeta-icono"><CalendarDays size={19} /></span>
              <div><p className="tarjeta-etiqueta">ACTIVIDAD RECIENTE</p><h3>Última sesión</h3></div></div>
            {cargandoSesionesResumen ? <p className="texto-atenuado">Cargando sesiones...</p> : ultimaSesion ? (
              <div className="ultima-sesion-detalle"><strong className="ultima-sesion-fecha">{fecha(ultimaSesion.fecha)}</strong>
                <span className={`estado-asistencia ${ultimaSesion.presente ? "" : "ausente"}`}>{ultimaSesion.presente ? "Asistió" : "Ausente"}</span>
                <p>{ultimaSesion.nota_general || "Sin nota general registrada."}</p></div>
            ) : <p className="texto-atenuado">Todavía no hay sesiones registradas.</p>}
            <button className="tarjeta-pie-accion" type="button" onClick={() => cambiarPestana("seguimiento")}>
              Consultar sesiones <ArrowRight size={16} aria-hidden="true" />
            </button>
          </section>
        </div>
        <section className="tarjeta-resumen tarjeta-contexto">
          <div className="tarjeta-cabecera"><span className="tarjeta-icono"><UserRound size={19} /></span>
            <div><p className="tarjeta-etiqueta">REFERENCIAS DEL CASO</p><h3>Información de contexto</h3></div></div>
          <div className="contexto-columnas">
            <div><span className="contexto-icono"><FileText size={18} /></span><small>Motivo de consulta</small><p>{cargandoAdmision ? "Cargando..." : admision?.motivo_consulta || "Aún no registrado"}</p></div>
            <div><span className="contexto-icono"><GraduationCap size={18} /></span><small>Escolaridad</small><p>{cargandoEscolaridad ? "Cargando..." : escolaridadActual?.institucion || "Aún no registrada"}</p></div>
            <div><span className="contexto-icono"><CalendarDays size={18} /></span><small>Inicio del seguimiento</small><p>{fecha(paciente.fecha_inicio_seguimiento)}</p></div>
          </div>
          <button className="tarjeta-pie-accion" type="button" onClick={() => cambiarPestana("informacion")}>
            Consultar información completa <ArrowRight size={16} aria-hidden="true" />
          </button>
        </section>
      </div>

      <div id="panel-seguimiento" role="tabpanel" aria-labelledby="pestana-seguimiento" hidden={pestana !== "seguimiento"} className="vista-pestana">
        <div className="vista-encabezado"><div><p className="vista-sobretitulo">TRABAJO PROFESIONAL</p><h2>Seguimiento</h2>
          <p>Objetivos, sesiones y observaciones relacionadas.</p></div></div>
        <div className="seguimiento-columnas">
          <div className="columna-objetivos"><ObjetivosPaciente
            registros={objetivos} onGuardar={guardarObjetivoPaciente} cargando={cargandoObjetivos}
            error={errorObjetivos} pacienteId={paciente.id} revisionEvidencias={revisionEvidencias} /></div>
          <div className="columna-sesiones"><SesionesPaciente
            pacienteId={paciente.id} objetivos={objetivos}
            onCambiarObservaciones={() => setRevisionEvidencias((n) => n + 1)}
            onCambiarSesiones={() => setRevisionSesiones((n) => n + 1)} /></div>
        </div>
      </div>

      <div id="panel-informacion" role="tabpanel" aria-labelledby="pestana-informacion" hidden={pestana !== "informacion"} className="vista-pestana">
        <div className="vista-encabezado"><div><p className="vista-sobretitulo">ANTECEDENTES Y CONTEXTO</p><h2>Información del paciente</h2>
          <p>Datos personales y contexto del acompañamiento.</p></div></div>
        <section className="pacientes-panel ficha-datos-panel"><div className="titulo-icono"><UserRound size={19} /><h3>Datos personales</h3></div>
          <div className="ficha-datos"><div><small>Nombre completo</small><strong>{paciente.nombre} {paciente.apellido}</strong></div>
            <div><small>Fecha de nacimiento</small><strong>{fecha(paciente.fecha_nacimiento)}</strong></div>
            <div><small>Inicio del seguimiento</small><strong>{fecha(paciente.fecha_inicio_seguimiento)}</strong></div>
            <div><small>Estado</small><strong>{paciente.activo ? "Activo" : "Inactivo"}</strong></div></div></section>
        <div className="informacion-grid"><div className="informacion-principal"><AdmisionPaciente
          admision={admision} fechaInicial={paciente.fecha_inicio_seguimiento}
          onGuardar={guardarAdmisionPaciente} cargando={cargandoAdmision} error={errorAdmision} /></div>
        <div className="informacion-secundaria"><EscolaridadPaciente
          registros={escolaridades} onGuardar={guardarEscolaridadPaciente}
          cargando={cargandoEscolaridad} error={errorEscolaridad} />
          <ProfesionalesIntervinientes registros={profesionales}
          onGuardar={guardarProfesionalPaciente} cargando={cargandoProfesionales} error={errorProfesionales} />
        </div></div>
      </div>
    </div>
  );
}
