
import { useState, type FormEvent } from "react";
import "./Pacientes.css";
import FichaPaciente from "./FichaPaciente";
import type { Admision } from "./AdmisionPaciente";
import type { Escolaridad } from "./EscolaridadPaciente";
import type { ProfesionalTratante } from "./ProfesionalesIntervinientes";
import type { Objetivo } from "./ObjetivosPaciente";
export type Paciente = {
  id: number;
  nombre: string;
  apellido: string;
  fecha_nacimiento: string;
  fecha_inicio_seguimiento: string;
  activo: boolean;
};

// Datos ficticios para probar la pantalla.
const pacientesPrueba: Paciente[] = [
  {
    id: 1,
    nombre: "Juan",
    apellido: "Perez",
    fecha_nacimiento: "2015-05-10",
    fecha_inicio_seguimiento: "2026-10-14",
    activo: true,
  },
];

export default function Pacientes() {
  const [pacientes, setPacientes] = useState(pacientesPrueba);
  const [busqueda, setBusqueda] = useState("");
  const [creando, setCreando] = useState(false);
  const [seleccionado, setSeleccionado] = useState<Paciente | null>(null);
  const [admisiones, setAdmisiones] = useState<Record<number, Admision>>({});
  const pacientesFiltrados = pacientes.filter((paciente) =>
    `${paciente.nombre} ${paciente.apellido} ${paciente.apellido} ${paciente.nombre}`
      .toLowerCase()
      .includes(busqueda.toLowerCase().trim())
  );
  const [escolaridades, setEscolaridades] = useState<
  Record<number, Escolaridad[]>
>({});

const [profesionales, setProfesionales] = useState<
  Record<number, ProfesionalTratante[]>
>({});
const [objetivos, setObjetivos] = useState<Record<number, Objetivo[]>>({});
  function crearPaciente(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const datos = new FormData(evento.currentTarget);

    const nuevoPaciente: Paciente = {
      id: Date.now(),
      nombre: String(datos.get("nombre")).trim(),
      apellido: String(datos.get("apellido")).trim(),
      fecha_nacimiento: String(datos.get("fecha_nacimiento")),
      fecha_inicio_seguimiento: String(datos.get("fecha_inicio_seguimiento")),
      activo: true,
    };

    if (!nuevoPaciente.nombre || !nuevoPaciente.apellido) return;

    setPacientes((actuales) => [...actuales, nuevoPaciente]);
    setCreando(false);
  }


if (seleccionado) {
  return (
    <FichaPaciente
      paciente={seleccionado}
      admision={admisiones[seleccionado.id] ?? null}
      onGuardarAdmision={(datos) =>
        setAdmisiones((actuales) => ({
          ...actuales,
          [seleccionado.id]: datos,
        }))
      }
      escolaridades={escolaridades[seleccionado.id] ?? []}
      onGuardarEscolaridad={(registro) =>
        setEscolaridades((actuales) => {
          const registros = actuales[seleccionado.id] ?? [];
          const existe = registros.some((item) => item.id === registro.id);

          return {
            ...actuales,
            [seleccionado.id]: existe
              ? registros.map((item) =>
                  item.id === registro.id ? registro : item
                )
              : [...registros, registro],
          };
        })
      }
      profesionales={profesionales[seleccionado.id] ?? []}

onGuardarProfesional={(registro) =>
  setProfesionales((actuales) => {
    const registros = actuales[seleccionado.id] ?? [];
    const existe = registros.some((item) => item.id === registro.id);

    return {
      ...actuales,
      [seleccionado.id]: existe
        ? registros.map((item) =>
            item.id === registro.id ? registro : item
          )
        : [...registros, registro],
    };
  })
}
    objetivos={objetivos[seleccionado.id] ?? []}

onGuardarObjetivo={(registro) =>
  setObjetivos((actuales) => {
    const registros = actuales[seleccionado.id] ?? [];
    const existe = registros.some((item) => item.id === registro.id);

    return {
      ...actuales,
      [seleccionado.id]: existe
        ? registros.map((item) =>
            item.id === registro.id ? registro : item
          )
        : [...registros, registro],
    };
  })
}
      onVolver={() => setSeleccionado(null)}
    />
  );
}

  return (
    <div className="pagina-pacientes">
      <div className="pacientes-cabecera">
        <div>
          <p className="pacientes-subtitulo">PANEL DE SEGUIMIENTO</p>
          <h1>Pacientes</h1>
          <p className="pacientes-descripcion">
            Consultá los perfiles y continuá el seguimiento de cada paciente.
          </p>
        </div>

        <button
          className="pacientes-boton"
          onClick={() => setCreando(!creando)}
        >
          {creando ? "Cerrar formulario" : "+ Nuevo paciente"}
        </button>
      </div>

      {creando && (
        <section className="pacientes-panel">
          <h2>Nuevo paciente</h2>

          <form className="pacientes-formulario" onSubmit={crearPaciente}>
            <label>
              Nombre
              <input name="nombre" required />
            </label>

            <label>
              Apellido
              <input name="apellido" required />
            </label>

            <label>
              Fecha de nacimiento
              <input name="fecha_nacimiento" type="date" required />
            </label>

            <label>
              Inicio del seguimiento
              <input name="fecha_inicio_seguimiento" type="date" required />
            </label>

            <div className="pacientes-acciones">
              <button type="submit" className="pacientes-boton">
                Agregar paciente
              </button>
              <button type="button" onClick={() => setCreando(false)}>
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="pacientes-panel">
        <div className="pacientes-listado-cabecera">
          <h2>Listado</h2>
          <span>{pacientes.length} registrados</span>
        </div>

        <input
          className="pacientes-busqueda"
          type="search"
          placeholder="Buscar por nombre o apellido..."
          aria-label="Buscar pacientes"
          value={busqueda}
          onChange={(evento) => setBusqueda(evento.target.value)}
        />

        <div className="pacientes-lista">

{pacientesFiltrados.map((paciente) => (
  <button
    type="button"
    className="pacientes-fila"
    key={paciente.id}
    onClick={() => setSeleccionado(paciente)}
  >
    <span className="pacientes-avatar">
      {paciente.nombre[0]}{paciente.apellido[0]}
    </span>

    <div className="pacientes-datos">
      <strong>{paciente.apellido}, {paciente.nombre}</strong>
      <small>
        Seguimiento desde {paciente.fecha_inicio_seguimiento.split("-").reverse().join("/")}
      </small>
    </div>

    <span className="pacientes-estado">
      {paciente.activo ? "Activo" : "Inactivo"}
    </span>
  </button>
))}


          {pacientesFiltrados.length === 0 && (
            <p className="pacientes-vacio">
              {busqueda
                ? "No se encontraron pacientes."
                : "Todavía no hay pacientes registrados."}
            </p>
          )}
        </div>
      </section>

      <p className="pacientes-nota">
        Para este TFI se utilizará datos ficticios.
      </p>
    </div>
  );
}
