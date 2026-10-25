import { useEffect, useState } from "react";
import { obtenerAdmision, guardarAdmision, listarEscolaridades, guardarEscolaridad, listarProfesionalesTratantes, guardarProfesionalTratante, listarObjetivos, guardarObjetivo } from "../../servicios/api";

import type { Paciente } from "./Pacientes";
import AdmisionPaciente, { type Admision } from "./AdmisionPaciente";
import EscolaridadPaciente, { type Escolaridad, type EscolaridadGuardar } from "./EscolaridadPaciente";
import ProfesionalesIntervinientes, { type ProfesionalTratante, type ProfesionalTratanteGuardar } from "./ProfesionalesIntervinientes";
import ObjetivosPaciente, { type Objetivo, type ObjetivoGuardar } from "./ObjetivosPaciente";
import SesionesPaciente from "./SesionesPaciente";

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

  const fecha = (valor: string) =>
    valor.split("-").reverse().join("/");

  return (
    <div className="pagina-pacientes">
      <button
        type="button"
        className="ficha-volver"
        onClick={onVolver}
      >
        ← Volver a pacientes
      </button>

      <div className="pacientes-cabecera">
        <div>
          <p className="pacientes-subtitulo">FICHA DE SEGUIMIENTO</p>
          <h1>{paciente.apellido}, {paciente.nombre}</h1>
          <p className="pacientes-descripcion">
            Registro y evolución psicopedagógica
          </p>
        </div>

        <span className="pacientes-estado">
          {paciente.activo ? "Seguimiento activo" : "Inactivo"}
        </span>
      </div>

      <section className="pacientes-panel">
        <h2>Datos del paciente</h2>

        <div className="ficha-datos">
          <div>
            <small>Nombre completo</small>
            <strong>{paciente.nombre} {paciente.apellido}</strong>
          </div>

          <div>
            <small>Fecha de nacimiento</small>
            <strong>{fecha(paciente.fecha_nacimiento)}</strong>
          </div>

          <div>
            <small>Inicio del seguimiento</small>
            <strong>{fecha(paciente.fecha_inicio_seguimiento)}</strong>
          </div>

          <div>
            <small>Estado</small>
            <strong>{paciente.activo ? "Activo" : "Inactivo"}</strong>
          </div>
        </div>
      </section>

      <AdmisionPaciente
        admision={admision}
        fechaInicial={paciente.fecha_inicio_seguimiento}
        onGuardar={guardarAdmisionPaciente}
        cargando={cargandoAdmision}
        error={errorAdmision}
      />

      <EscolaridadPaciente
        registros={escolaridades}
        onGuardar={guardarEscolaridadPaciente}
        cargando={cargandoEscolaridad}
        error={errorEscolaridad}
      />

      <ProfesionalesIntervinientes
        registros={profesionales}
        onGuardar={guardarProfesionalPaciente}
        cargando={cargandoProfesionales}
        error={errorProfesionales}
      />

      <ObjetivosPaciente
        registros={objetivos}
        onGuardar={guardarObjetivoPaciente}
        cargando={cargandoObjetivos}
        error={errorObjetivos}
        pacienteId={paciente.id}
        revisionEvidencias={revisionEvidencias}
      />

      <SesionesPaciente
        pacienteId={paciente.id}
        objetivos={objetivos}
        onCambiarObservaciones={() => setRevisionEvidencias((n) => n + 1)}
      />
    </div>
  );
}
