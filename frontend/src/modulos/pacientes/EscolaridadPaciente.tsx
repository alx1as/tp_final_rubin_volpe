
import { useState, type FormEvent } from "react";

export type Escolaridad = {
  id: number;
  institucion: string;
  nivel: string;
  grado_anio_sala: string;
  modalidad: string;
  jornada: string;
  fecha_inicio: string;
  fecha_fin: string;
  apoyos: string;
  observaciones: string;
  referente_nombre: string;
  referente_rol: string;
  referente_contacto: string;
};

type Props = {
  registros: Escolaridad[];
  onGuardar: (registro: Escolaridad) => void;
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

export default function EscolaridadPaciente({ registros, onGuardar }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);

  const actual = registros.find((registro) => registro.id === editando);

  function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const formulario = new FormData(evento.currentTarget);

    const valores = Object.fromEntries(
      campos.map((campo) => [
        campo.nombre,
        String(formulario.get(campo.nombre) ?? "").trim(),
      ])
    ) as Omit<Escolaridad, "id">;

    onGuardar({
      id: typeof editando === "number" ? editando : Date.now(),
      ...valores,
    });

    setEditando(null);
  }

  const fecha = (valor: string) =>
    valor ? valor.split("-").reverse().join("/") : "Actual";

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Escolaridad</h2>

        {editando === null && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => setEditando("nuevo")}
          >
            + Agregar período
          </button>
        )}
      </div>

      {registros.length === 0 && editando === null && (
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
            onClick={() => setEditando(registro.id)}
          >
            Editar
          </button>
        </div>
      ))}

      {editando !== null && (
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

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton">
              Guardar escolaridad
            </button>

            <button type="button" onClick={() => setEditando(null)}>
              Cancelar
            </button>
          </div>
        </form>
      )}
    </section>
  );
}
