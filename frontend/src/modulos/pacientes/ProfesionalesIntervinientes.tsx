import { useState, type FormEvent } from "react";

export type ProfesionalTratante = {
  id: number;
  nombre: string;
  especialidad: string;
  contacto: string;
  fecha_inicio: string;
  fecha_fin: string;
  observaciones: string;
};

type Props = {
  registros: ProfesionalTratante[];
  onGuardar: (registro: ProfesionalTratante) => void;
};

type Campo = {
  nombre: keyof Omit<ProfesionalTratante, "id">;
  etiqueta: string;
  tipo?: "date" | "textarea";
  requerido?: boolean;
};

const campos: Campo[] = [
  { nombre: "nombre", etiqueta: "Nombre y apellido", requerido: true },
  { nombre: "especialidad", etiqueta: "Especialidad", requerido: true },
  { nombre: "contacto", etiqueta: "Contacto" },
  { nombre: "fecha_inicio", etiqueta: "Fecha de inicio", tipo: "date", requerido: true },
  { nombre: "fecha_fin", etiqueta: "Fecha de finalización", tipo: "date" },
  { nombre: "observaciones", etiqueta: "Observaciones", tipo: "textarea" },
];

export default function ProfesionalesIntervinientes({ registros, onGuardar }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [error, setError] = useState("");

  const actual = registros.find((registro) => registro.id === editando);

  function abrirFormulario(id: number | "nuevo") {
    setError("");
    setEditando(id);
  }

  function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const formulario = new FormData(evento.currentTarget);

    const valores = Object.fromEntries(
      campos.map((campo) => [
        campo.nombre,
        String(formulario.get(campo.nombre) ?? "").trim(),
      ])
    ) as Omit<ProfesionalTratante, "id">;

    if (valores.fecha_fin && valores.fecha_fin < valores.fecha_inicio) {
      setError("La fecha de finalización no puede ser anterior al inicio.");
      return;
    }

    onGuardar({
      id: typeof editando === "number" ? editando : Date.now(),
      ...valores,
    });

    setError("");
    setEditando(null);
  }

  const fecha = (valor: string) =>
    valor ? valor.split("-").reverse().join("/") : "Actual";

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Profesionales intervinientes</h2>

        {editando === null && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => abrirFormulario("nuevo")}
          >
            + Agregar profesional
          </button>
        )}
      </div>

      {registros.length === 0 && editando === null && (
        <p className="pacientes-descripcion">
          Todavía no se registraron profesionales externos.
        </p>
      )}

      {registros.map((registro) => (
        <div className="interviniente-registro" key={registro.id}>
          <div>
            <strong>{registro.nombre}</strong>

            <p>
              {registro.especialidad} · {fecha(registro.fecha_inicio)} — {fecha(registro.fecha_fin)}
            </p>

            {registro.contacto && (
              <p>Contacto: {registro.contacto}</p>
            )}

            {registro.observaciones && (
              <p>Observaciones: {registro.observaciones}</p>
            )}
          </div>

          <button
            type="button"
            onClick={() => abrirFormulario(registro.id)}
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
          <h3>
            {editando === "nuevo" ? "Nuevo profesional" : "Editar profesional"}
          </h3>

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

          {error && <p role="alert">{error}</p>}

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton">
              Guardar profesional
            </button>

            <button
              type="button"
              onClick={() => setEditando(null)}
            >
              Cancelar
            </button>
          </div>
        </form>
      )}
    </section>
  );
}