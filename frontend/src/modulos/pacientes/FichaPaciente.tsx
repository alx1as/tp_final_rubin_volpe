
import type { Paciente } from "./Pacientes";
import AdmisionPaciente, { type Admision } from "./AdmisionPaciente";
import EscolaridadPaciente, { type Escolaridad } from "./EscolaridadPaciente";
import ProfesionalesIntervinientes, { type ProfesionalTratante } from "./ProfesionalesIntervinientes";
import ObjetivosPaciente, { type Objetivo } from "./ObjetivosPaciente";

type Props = {
  paciente: Paciente;
  onVolver: () => void;
  admision: Admision | null;
  onGuardarAdmision: (datos: Admision) => void;
  escolaridades: Escolaridad[];
onGuardarEscolaridad: (registro: Escolaridad) => void;
profesionales: ProfesionalTratante[];
onGuardarProfesional: (registro: ProfesionalTratante) => void;
objetivos: Objetivo[];
onGuardarObjetivo: (registro: Objetivo) => void;
};

export default function FichaPaciente({
  paciente,
  onVolver,
  admision,
  onGuardarAdmision,
  escolaridades,
  onGuardarEscolaridad,
  profesionales,
onGuardarProfesional,
objetivos,
onGuardarObjetivo,
}: Props) {
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
        onGuardar={onGuardarAdmision}
      />

      <EscolaridadPaciente
  registros={escolaridades}
  onGuardar={onGuardarEscolaridad}
/>

      <section className="pacientes-panel">
        <h2>Profesionales intervinientes</h2>
        <p className="pacientes-descripcion">
        <ProfesionalesIntervinientes
  registros={profesionales}
  onGuardar={onGuardarProfesional}
/>
      <ObjetivosPaciente
  registros={objetivos}
  onGuardar={onGuardarObjetivo}
/>
        </p>
      </section>
    </div>
  );
}
