
import { useEffect, useState, type FormEvent } from "react";
import { ArrowRight, Search, Plus, UsersRound, UserCheck, ShieldCheck } from "lucide-react";
import {
  listarPacientes,
  guardarPaciente,
  type PacienteCrear,
} from "../../servicios/api";

import "./Pacientes.css";
import FichaPaciente from "./FichaPaciente";

export type Paciente = {
  id: number;
  nombre: string;
  apellido: string;
  fecha_nacimiento: string;
  fecha_inicio_seguimiento: string;
  activo: boolean;
};

export default function Pacientes() {
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [busqueda, setBusqueda] = useState("");
  const [creando, setCreando] = useState(false);
  const [seleccionado, setSeleccionado] = useState<Paciente | null>(null);

  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");

  // Cargar pacientes desde PostgreSQL al abrir la pantalla.
  useEffect(() => {
    let vigente = true;

    listarPacientes()
      .then((datos) => {
        if (vigente) {
          setPacientes(datos);
        }
      })
      .catch((fallo) => {
        if (vigente) {
          setError(
            fallo instanceof Error
              ? fallo.message
              : "No se pudieron cargar los pacientes."
          );
        }
      })
      .finally(() => {
        if (vigente) {
          setCargando(false);
        }
      });

    return () => {
      vigente = false;
    };
  }, []);

  // Buscar pacientes por nombre o apellido.
  const pacientesFiltrados = pacientes.filter((paciente) =>
    `${paciente.nombre} ${paciente.apellido} ${paciente.apellido} ${paciente.nombre}`
      .toLowerCase()
      .includes(busqueda.toLowerCase().trim())
  );

  // Guardar un nuevo paciente mediante la API.
  async function crearPaciente(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const datos = new FormData(evento.currentTarget);

    const nuevoPaciente: PacienteCrear = {
      nombre: String(datos.get("nombre") ?? "").trim(),
      apellido: String(datos.get("apellido") ?? "").trim(),
      fecha_nacimiento: String(datos.get("fecha_nacimiento") ?? ""),
      fecha_inicio_seguimiento: String(
        datos.get("fecha_inicio_seguimiento") ?? ""
      ),
    };

    if (!nuevoPaciente.nombre || !nuevoPaciente.apellido) return;

    setGuardando(true);
    setError("");

    try {
      const guardado = await guardarPaciente(nuevoPaciente);

      setPacientes((actuales) => [...actuales, guardado]);
      setCreando(false);
    } catch (fallo) {
      setError(
        fallo instanceof Error
          ? fallo.message
          : "No se pudo guardar el paciente."
      );
    } finally {
      setGuardando(false);
    }
  }

  const pacientesActivos = pacientes.filter((paciente) => paciente.activo).length;

  // Mostrar la ficha del paciente seleccionado.
  if (seleccionado) {
    return (
      <FichaPaciente
        paciente={seleccionado}
        onVolver={() => setSeleccionado(null)}
      />
    );
  }

  return (
    <div className="pagina-pacientes">
      <header className="pacientes-presentacion">
        <div className="pacientes-presentacion-texto">
          <p className="pacientes-subtitulo">ESPACIO DE TRABAJO</p>
          <h1>Pacientes<span className="punto-titulo">.</span></h1>
          <p>Un espacio para organizar cada acompañamiento, registrar encuentros y consultar la evolución.</p>
          <button type="button" className="pacientes-boton pacientes-boton-grande" onClick={() => setCreando(!creando)}>
            {creando ? "Cerrar formulario" : <><Plus size={18} aria-hidden="true" /> Nuevo paciente</>}
          </button>
        </div>
        <div className="presentacion-indicadores" aria-label="Resumen de pacientes">
          <div className="presentacion-indicador"><span className="presentacion-indicador-icono"><UserCheck size={19} /></span>
            <strong>{cargando ? "—" : pacientesActivos}</strong><small>En seguimiento</small></div>
          <div className="presentacion-indicador"><span className="presentacion-indicador-icono"><UsersRound size={19} /></span>
            <strong>{cargando ? "—" : pacientes.length}</strong><small>Registrados</small></div>
        </div>
      </header>

      {error && <p role="alert">{error}</p>}

      {creando && (
        <section className="pacientes-panel">
          <h2>Nuevo paciente</h2>

          <form
            className="pacientes-formulario"
            onSubmit={crearPaciente}
          >
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
              <input
                name="fecha_nacimiento"
                type="date"
                required
              />
            </label>

            <label>
              Inicio del seguimiento
              <input
                name="fecha_inicio_seguimiento"
                type="date"
                required
              />
            </label>

            <div className="pacientes-acciones">
              <button
                type="submit"
                className="pacientes-boton"
                disabled={guardando}
              >
                {guardando ? "Guardando..." : "Agregar paciente"}
              </button>

              <button
                type="button"
                onClick={() => setCreando(false)}
                disabled={guardando}
              >
                Cancelar
              </button>
            </div>
          </form>
        </section>
      )}

      <section className="pacientes-panel pacientes-listado-panel">
        <div className="pacientes-listado-cabecera">
          <div><p className="seccion-eyebrow">PERFILES</p><h2>Listado de pacientes</h2></div>
          <span>{pacientesFiltrados.length} de {pacientes.length}</span>
        </div>
        <label className="busqueda-contenedor">
          <Search size={19} aria-hidden="true" />
          <input className="pacientes-busqueda" type="search"
            placeholder="Buscar por nombre o apellido" aria-label="Buscar pacientes"
            value={busqueda} onChange={(evento) => setBusqueda(evento.target.value)} />
        </label>

        <div className="pacientes-lista">
          {cargando && <p>Cargando pacientes...</p>}

          {pacientesFiltrados.map((paciente) => (
            <button
              type="button"
              className="pacientes-fila"
              key={paciente.id}
              onClick={() => setSeleccionado(paciente)}
            >
              <span className="pacientes-avatar">
                {paciente.nombre[0]}
                {paciente.apellido[0]}
              </span>

              <div className="pacientes-datos">
                <strong>
                  {paciente.apellido}, {paciente.nombre}
                </strong>
                <small>
                  Seguimiento desde{" "}
                  {paciente.fecha_inicio_seguimiento
                    .split("-")
                    .reverse()
                    .join("/")}
                </small>
              </div>

              <span className={`pacientes-estado ${paciente.activo ? "" : "inactivo"}`}>
                {paciente.activo ? "Activo" : "Inactivo"}
              </span>
              <ArrowRight className="fila-flecha" size={18} aria-hidden="true" />
            </button>
          ))}

          {!cargando && pacientesFiltrados.length === 0 && (
            <p className="pacientes-vacio">
              {busqueda
                ? "No se encontraron pacientes."
                : "Todavía no hay pacientes registrados."}
            </p>
          )}
        </div>
      </section>

      <p className="pacientes-nota"><ShieldCheck size={16} aria-hidden="true" /> Para las pruebas del TFI se utilizan datos ficticios.</p>
    </div>
  );
}
