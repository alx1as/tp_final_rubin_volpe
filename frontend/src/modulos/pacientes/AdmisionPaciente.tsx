
import { useState, type FormEvent } from "react";

// Campos previstos en el modelo de admisión.
export type Admision = {
  fecha: string;
  motivo_consulta: string;
  antecedentes_personales: string;
  antecedentes_evolutivos: string;
  antecedentes_salud: string;
  grupo_familiar: string;
  tratamientos_actuales: string;
  observaciones: string;
};

const campos = [
  { clave: "motivo_consulta", etiqueta: "Motivo de consulta" },
  { clave: "antecedentes_personales", etiqueta: "Antecedentes personales" },
  { clave: "antecedentes_evolutivos", etiqueta: "Antecedentes evolutivos" },
  { clave: "antecedentes_salud", etiqueta: "Antecedentes de salud" },
  { clave: "grupo_familiar", etiqueta: "Grupo familiar" },
  { clave: "tratamientos_actuales", etiqueta: "Tratamientos actuales" },
  { clave: "observaciones", etiqueta: "Otras observaciones" },
] as const;

type Props = {
  admision: Admision | null;
  fechaInicial: string;
  onGuardar: (datos: Admision) => Promise<void>;
  cargando: boolean;
  error: string;
};

export default function AdmisionPaciente({
  admision,
  fechaInicial,
  onGuardar,
  cargando,
  error,
}: Props) {
  const [editando, setEditando] = useState(false);
  const [guardando, setGuardando] = useState(false);

  async function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const formulario = new FormData(evento.currentTarget);
    const leer = (nombre: string) =>
      String(formulario.get(nombre) ?? "").trim();

    const datos: Admision = {
      fecha: leer("fecha"),
      motivo_consulta: leer("motivo_consulta"),
      antecedentes_personales: leer("antecedentes_personales"),
      antecedentes_evolutivos: leer("antecedentes_evolutivos"),
      antecedentes_salud: leer("antecedentes_salud"),
      grupo_familiar: leer("grupo_familiar"),
      tratamientos_actuales: leer("tratamientos_actuales"),
      observaciones: leer("observaciones"),
    };

    setGuardando(true);
    try {
      await onGuardar(datos);
      setEditando(false);
    } catch {
      // El error se muestra desde la ficha; conservar el formulario abierto.
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Admisión</h2>

        {!cargando && !editando && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => setEditando(true)}
          >
            {admision ? "Editar" : "Registrar admisión"}
          </button>
        )}
      </div>

      {error && <p role="alert">{error}</p>}

      {cargando ? (
        <p className="pacientes-descripcion">Cargando admisión...</p>
      ) : editando ? (
        <form className="admision-formulario" onSubmit={guardar}>
          <label>
            Fecha
            <input
              type="date"
              name="fecha"
              defaultValue={admision?.fecha ?? fechaInicial}
              required
            />
          </label>

          {campos.map((campo) => (
            <label key={campo.clave}>
              {campo.etiqueta}
              {campo.clave === "motivo_consulta" && " *"}
              <textarea
                name={campo.clave}
                rows={3}
                defaultValue={admision?.[campo.clave] ?? ""}
                required={campo.clave === "motivo_consulta"}
              />
            </label>
          ))}

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar admisión"}
            </button>
            <button type="button" onClick={() => setEditando(false)} disabled={guardando}>
              Cancelar
            </button>
          </div>
        </form>
      ) : admision ? (
        <div className="admision-resumen">
          <div>
            <small>Fecha</small>
            <p>{admision.fecha.split("-").reverse().join("/")}</p>
          </div>

          {campos.filter((campo) => admision[campo.clave]).map((campo) => (
            <div key={campo.clave}>
              <small>{campo.etiqueta}</small>
              <p>{admision[campo.clave]}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="pacientes-descripcion">
          Todavía no se registró una admisión.
        </p>
      )}
    </section>
  );
}
