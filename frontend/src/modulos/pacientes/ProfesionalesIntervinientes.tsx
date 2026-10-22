import { useState, type FormEvent } from "react";

export type ProfesionalTratante = {
  id: number;
  nombre: string;
  especialidad: string;
  contacto: string | null;
  fecha_inicio: string;
  fecha_fin: string | null;
  observaciones: string | null;
};

export type ProfesionalTratanteGuardar = Omit<ProfesionalTratante, "id">;

type Props = {
  registros: ProfesionalTratante[];
  onGuardar: (registro: ProfesionalTratanteGuardar, id?: number) => Promise<void>;
  cargando: boolean;
  error: string;
};

type Campo = {
  nombre: keyof ProfesionalTratanteGuardar;
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

export default function ProfesionalesIntervinientes({ registros, onGuardar, cargando, error }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState("");

  const actual = registros.find((registro) => registro.id === editando);

  function abrirFormulario(id: number | "nuevo") {
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
    ) as ProfesionalTratanteGuardar;

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
      // La ficha muestra el error; conservamos el formulario para reintentar.
    } finally {
      setGuardando(false);
    }
  }

  const fecha = (valor: string | null) =>
    valor ? valor.split("-").reverse().join("/") : "Actual";

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Profesionales intervinientes</h2>

        {!cargando && editando === null && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => abrirFormulario("nuevo")}
          >
            + Agregar profesional
          </button>
        )}
      </div>

      {cargando && <p className="pacientes-descripcion">Cargando profesionales...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && registros.length === 0 && editando === null && (
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
            {registro.contacto && <p>Contacto: {registro.contacto}</p>}
            {registro.observaciones && <p>Observaciones: {registro.observaciones}</p>}
          </div>
          <button
            type="button"
            onClick={() => abrirFormulario(registro.id)}
            disabled={guardando || cargando}
          >
            Editar
          </button>
        </div>
      ))}

      {!cargando && editando !== null && (
        <form key={editando} className="admision-formulario" onSubmit={guardar}>
          <h3>{editando === "nuevo" ? "Nuevo profesional" : "Editar profesional"}</h3>

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
              {guardando ? "Guardando..." : "Guardar profesional"}
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
