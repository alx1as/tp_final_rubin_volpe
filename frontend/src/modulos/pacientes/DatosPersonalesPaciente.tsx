import { useState, type FormEvent } from "react";
import { Pencil, UserRound } from "lucide-react";
import { editarPaciente, type PacienteActualizar } from "../../servicios/api";
import type { Paciente } from "./Pacientes";

type Props = {
  paciente: Paciente;
  onActualizar: (actualizado: Paciente) => void;
};

function mostrarFecha(valor: string): string {
  return valor ? valor.split("-").reverse().join("/") : "Sin fecha";
}

export default function DatosPersonalesPaciente({ paciente, onActualizar }: Props) {
  const [editando, setEditando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  function comenzarEdicion() {
    setError("");
    setMensaje("");
    setEditando(true);
  }

  async function guardarCambios(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    const formulario = new FormData(evento.currentTarget);
    const datos: PacienteActualizar = {
      nombre: String(formulario.get("nombre") ?? "").trim(),
      apellido: String(formulario.get("apellido") ?? "").trim(),
      fecha_nacimiento: String(formulario.get("fecha_nacimiento") ?? ""),
      fecha_inicio_seguimiento: String(formulario.get("fecha_inicio_seguimiento") ?? ""),
    };

    if (!datos.nombre || !datos.apellido) {
      setError("El nombre y el apellido son obligatorios.");
      return;
    }
    if (datos.fecha_inicio_seguimiento < datos.fecha_nacimiento) {
      setError("El seguimiento no puede comenzar antes del nacimiento.");
      return;
    }

    setError("");
    setMensaje("");
    setGuardando(true);
    try {
      const actualizado = await editarPaciente(paciente.id, datos);
      onActualizar(actualizado);
      setEditando(false);
      setMensaje("Datos personales actualizados.");
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudieron actualizar los datos.");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section className="pacientes-panel ficha-datos-panel">
      <div className="ficha-datos-cabecera">
        <div className="titulo-icono">
          <UserRound size={19} aria-hidden="true" />
          <h3>Datos personales</h3>
        </div>
        {!editando && (
          <button type="button" className="enlace-accion" onClick={comenzarEdicion}>
            <Pencil size={15} aria-hidden="true" /> Editar datos
          </button>
        )}
      </div>

      {error && <p role="alert" className="ficha-datos-mensaje error">{error}</p>}
      {mensaje && <p role="status" className="ficha-datos-mensaje exito">{mensaje}</p>}

      {editando ? (
        <form className="pacientes-formulario ficha-datos-formulario" onSubmit={guardarCambios}>
          <label>Nombre
            <input name="nombre" defaultValue={paciente.nombre} required disabled={guardando} />
          </label>
          <label>Apellido
            <input name="apellido" defaultValue={paciente.apellido} required disabled={guardando} />
          </label>
          <label>Fecha de nacimiento
            <input name="fecha_nacimiento" type="date" defaultValue={paciente.fecha_nacimiento} required disabled={guardando} />
          </label>
          <label>Inicio del seguimiento
            <input name="fecha_inicio_seguimiento" type="date" defaultValue={paciente.fecha_inicio_seguimiento} required disabled={guardando} />
          </label>
          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar cambios"}
            </button>
            <button type="button" disabled={guardando} onClick={() => { setEditando(false); setError(""); }}>
              Cancelar
            </button>
          </div>
        </form>
      ) : (
        <div className="ficha-datos">
          <div><small>Nombre completo</small><strong>{paciente.nombre} {paciente.apellido}</strong></div>
          <div><small>Fecha de nacimiento</small><strong>{mostrarFecha(paciente.fecha_nacimiento)}</strong></div>
          <div><small>Inicio del seguimiento</small><strong>{mostrarFecha(paciente.fecha_inicio_seguimiento)}</strong></div>
          <div><small>Estado</small><strong>{paciente.activo ? "Activo" : "Inactivo"}</strong></div>
        </div>
      )}
    </section>
  );
}
