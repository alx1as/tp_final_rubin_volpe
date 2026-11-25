import { useEffect, useState } from "react";
import { listarSesiones, type Sesion } from "../../servicios/api-seguimiento";
import { obtenerAdmision, guardarAdmision, listarEscolaridades, guardarEscolaridad, listarProfesionalesTratantes, guardarProfesionalTratante, listarObjetivos, guardarObjetivo } from "../../servicios/api";

import type { Admision } from "./AdmisionPaciente";
import type { Escolaridad, EscolaridadGuardar } from "./EscolaridadPaciente";
import type { ProfesionalTratante, ProfesionalTratanteGuardar } from "./ProfesionalesIntervinientes";
import type { Objetivo, ObjetivoGuardar } from "./ObjetivosPaciente";

// Las consultas pertenecen a la ficha montada para un único paciente (key=paciente.id).
// Al actualizar una colección se mantiene el último resultado mientras llega la nueva lectura.
function useRecursoPaciente<T>(pacienteId: number, cargar: (id: number) => Promise<T>, inicial: T, mensaje: string, revision = 0) {
  const [datos, setDatos] = useState<T>(inicial);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    let vigente = true;
    queueMicrotask(() => {
      if (!vigente) return;
      setCargando(true);
      setError("");
      cargar(pacienteId)
        .then((resultado) => { if (vigente) setDatos(resultado); })
        .catch((fallo) => { if (vigente) setError(fallo instanceof Error ? fallo.message : mensaje); })
        .finally(() => { if (vigente) setCargando(false); });
    });
    return () => { vigente = false; };
  }, [pacienteId, cargar, mensaje, revision]);
  return [datos, setDatos, cargando, error, setError] as const;
}

// Datos y operaciones de la ficha; la navegación permanece en el componente.
export function useFichaPaciente(pacienteId: number) {
  const [revisionEvidencias, setRevisionEvidencias] = useState(0);
  const [revisionSesiones, setRevisionSesiones] = useState(0);
  const [admision, setAdmision, cargandoAdmision, errorAdmision, setErrorAdmision] =
    useRecursoPaciente<Admision | null>(pacienteId, obtenerAdmision, null, "No se pudo cargar la admisión.");
  const [escolaridades, setEscolaridades, cargandoEscolaridad, errorEscolaridad, setErrorEscolaridad] =
    useRecursoPaciente<Escolaridad[]>(pacienteId, listarEscolaridades, [], "No se pudo cargar la escolaridad.");
  const [profesionales, setProfesionales, cargandoProfesionales, errorProfesionales, setErrorProfesionales] =
    useRecursoPaciente<ProfesionalTratante[]>(pacienteId, listarProfesionalesTratantes, [], "No se pudieron cargar los profesionales.");
  const [objetivos, setObjetivos, cargandoObjetivos, errorObjetivos, setErrorObjetivos] =
    useRecursoPaciente<Objetivo[]>(pacienteId, listarObjetivos, [], "No se pudieron cargar los objetivos.");
  const [sesionesResumen, , cargandoSesionesResumen, errorSesionesResumen] =
    useRecursoPaciente<Sesion[]>(pacienteId, listarSesiones, [], "No se pudieron cargar las sesiones.", revisionSesiones);

  async function guardarObjetivoPaciente(datos: ObjetivoGuardar, id?: number): Promise<void> {
    setErrorObjetivos("");
    try {
      const guardado = await guardarObjetivo(pacienteId, datos, id);
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
      const guardado = await guardarProfesionalTratante(pacienteId, datos, id);
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
      const guardado = await guardarEscolaridad(pacienteId, datos, id);
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
      const guardada = await guardarAdmision(pacienteId, datos);
      setAdmision(guardada);
    } catch (fallo) {
      setErrorAdmision(
        fallo instanceof Error ? fallo.message : "No se pudo guardar la admisión."
      );
      throw fallo;
    }
  }

  return {
    admision,
    cargandoAdmision,
    errorAdmision,
    escolaridades,
    cargandoEscolaridad,
    errorEscolaridad,
    profesionales,
    cargandoProfesionales,
    errorProfesionales,
    objetivos,
    cargandoObjetivos,
    errorObjetivos,
    revisionEvidencias,
    setRevisionEvidencias,
    sesionesResumen,
    cargandoSesionesResumen,
    revisionSesiones,
    setRevisionSesiones,
    errorSesionesResumen,
    guardarObjetivoPaciente,
    guardarProfesionalPaciente,
    guardarEscolaridadPaciente,
    guardarAdmisionPaciente
  };
}
