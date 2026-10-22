
import { useState, type FormEvent } from "react";

export type Escolaridad = {
  id: number;
  institucion: string;
  nivel: string;
  grado_anio_sala: string;
  modalidad: string;
  jornada: string | null;
  fecha_inicio: string;
  fecha_fin: string | null;
  apoyos: string | null;
  observaciones: string | null;
  referente_nombre: string | null;
  referente_rol: string | null;
  referente_contacto: string | null;
};

export type EscolaridadGuardar = Omit<Escolaridad, "id">;

type Props = {
  registros: Escolaridad[];
  onGuardar: (registro: EscolaridadGuardar, id?: number) => Promise<void>;
  cargando: boolean;
  error: string;
};

type Campo = {
  nombre: keyof Omit<Escolaridad, "id">;
  etiqueta: string;
  tipo?: "date" | "textarea";
  requerido?: boolean;
};

const campos: Campo[] = [
  { nombre: "institucion", etiqueta: "Institución", requerido: true },
  { nombre: "nivel", etiqueta: "Nivel", requerido: true },
  { nombre: "grado_anio_sala", etiqueta: "Grado, año o sala", requerido: true },
  { nombre: "modalidad", etiqueta: "Modalidad", requerido: true },
  { nombre: "jornada", etiqueta: "Jornada" },
  { nombre: "fecha_inicio", etiqueta: "Fecha de inicio", tipo: "date", requerido: true },
  { nombre: "fecha_fin", etiqueta: "Fecha de finalización", tipo: "date" },
  { nombre: "apoyos", etiqueta: "Apoyos escolares", tipo: "textarea" },
  { nombre: "observaciones", etiqueta: "Observaciones", tipo: "textarea" },
  { nombre: "referente_nombre", etiqueta: "Nombre del referente" },
  { nombre: "referente_rol", etiqueta: "Rol del referente" },
  { nombre: "referente_contacto", etiqueta: "Contacto del referente" },
];

export default function EscolaridadPaciente({ registros, onGuardar, cargando, error }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const actual = registros.find((registro) => registro.id === editando);

  function iniciarEdicion(id: number | "nuevo") {
    setErrorFormulario("");
    setEditando(id);
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const formulario = new FormData(evento.currentTarget);
    const valores = Object.fromEntries(
      campos.map((campo) => [
        campo.nombre,
        String(formulario.get(campo.nombre) ?? "").trim(),
      ])
    ) as EscolaridadGuardar;

    if (valores.fecha_fin && valores.fecha_fin < valores.fecha_inicio) {
      setErrorFormulario("La fecha de finalización no puede ser anterior al inicio.");
      return;
    }

    setGuardando(true);
    setErrorFormulario("");
    try {
      await onGuardar(valores, typeof editando === "number" ? editando : undefined);
      setEditando(null);
    } catch {
      // La ficha muestra el error y conservamos los datos del formulario.
    } finally {
      setGuardando(false);
    }
  }

  const fecha = (valor: string | null) =>
    valor ? valor.split("-").reverse().join("/") : "Actual";

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Escolaridad</h2>

        {!cargando && editando === null && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => iniciarEdicion("nuevo")}
          >
            + Agregar período
          </button>
        )}
      </div>

      {cargando && <p className="pacientes-descripcion">Cargando escolaridad...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && registros.length === 0 && editando === null && (
        <p className="pacientes-descripcion">
          Todavía no se registraron períodos escolares.
        </p>
      )}

      {registros.map((registro) => (
        <div className="escolaridad-registro" key={registro.id}>
          <div>
            <strong>{registro.institucion}</strong>
            <p>
              {registro.nivel} · {registro.grado_anio_sala} · {registro.modalidad}
            </p>
            <small>
              {fecha(registro.fecha_inicio)} — {fecha(registro.fecha_fin)}
            </small>
          </div>

          <button
            type="button"
            onClick={() => iniciarEdicion(registro.id)}
          >
            Editar
          </button>
        </div>
      ))}

      {!cargando && editando !== null && (
        <form
          key={editando}
          className="admision-formulario"
          onSubmit={guardar}
        >
          <h3>{editando === "nuevo" ? "Nueva escolaridad" : "Editar escolaridad"}</h3>

          {campos.map((campo) => (
            <label key={campo.nombre}>
              {campo.etiqueta}

              {campo.tipo === "textarea" ? (
                <textarea
                  name={campo.nombre}
                  rows={3}
                  defaultValue={actual?.[campo.nombre] ?? ""}
                />
              ) : (
                <input
                  name={campo.nombre}
                  type={campo.tipo ?? "text"}
                  required={campo.requerido}
                  defaultValue={actual?.[campo.nombre] ?? ""}
                />
              )}
            </label>
          ))}

          {errorFormulario && <p role="alert">{errorFormulario}</p>}

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar escolaridad"}
            </button>

            <button type="button" onClick={() => setEditando(null)} disabled={guardando}>
              Cancelar
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
