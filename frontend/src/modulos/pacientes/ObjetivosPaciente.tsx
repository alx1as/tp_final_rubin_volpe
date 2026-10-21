import { useState, type FormEvent } from "react";

export type EstadoObjetivo = "activo" | "cumplido" | "cerrado";

export type Objetivo = {
  id: number;
  descripcion: string;
  fecha_inicio: string;
  estado: EstadoObjetivo;
  fecha_cierre: string;
  observaciones_generales: string;
};

type Props = {
  registros: Objetivo[];
  onGuardar: (registro: Objetivo) => void;
};

const mostrarFecha = (fecha: string) =>
  fecha ? fecha.split("-").reverse().join("/") : "Sin fecha";

const etiquetasEstado: Record<EstadoObjetivo, string> = {
  activo: "Activo",
  cumplido: "Cumplido",
  cerrado: "Cerrado sin cumplimiento",
};

export default function ObjetivosPaciente({ registros, onGuardar }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [estadoFormulario, setEstadoFormulario] = useState<EstadoObjetivo>("activo");
  const [error, setError] = useState("");

  const objetivoActual = registros.find((objetivo) => objetivo.id === editando);

  function abrirFormulario(id: number | "nuevo") {
    const registro = registros.find((objetivo) => objetivo.id === id);
    setEstadoFormulario(registro?.estado ?? "activo");
    setError("");
    setEditando(id);
  }

  function guardar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();

    const datos = new FormData(evento.currentTarget);
    const descripcion = String(datos.get("descripcion") ?? "").trim();
    const fecha_inicio = String(datos.get("fecha_inicio") ?? "");
    const fecha_cierre =
      estadoFormulario === "activo" ? "" : String(datos.get("fecha_cierre") ?? "");
    const observaciones_generales = String(
      datos.get("observaciones_generales") ?? ""
    ).trim();

    if (!descripcion || !fecha_inicio) {
      setError("Completá la descripción y la fecha de inicio.");
      return;
    }

    if (estadoFormulario !== "activo" && !fecha_cierre) {
      setError("Indicá la fecha de cierre del objetivo.");
      return;
    }

    if (fecha_cierre && fecha_cierre < fecha_inicio) {
      setError("La fecha de cierre no puede ser anterior a la de inicio.");
      return;
    }

    onGuardar({
      id: typeof editando === "number" ? editando : Date.now(),
      descripcion,
      fecha_inicio,
      estado: estadoFormulario,
      fecha_cierre,
      observaciones_generales,
    });

    setEditando(null);
    setError("");
  }

  return (
    <section className="pacientes-panel">
      <div className="admision-cabecera">
        <h2>Objetivos de seguimiento</h2>

        {editando === null && (
          <button
            type="button"
            className="pacientes-boton"
            onClick={() => abrirFormulario("nuevo")}
          >
            + Agregar objetivo
          </button>
        )}
      </div>

      {registros.length === 0 && editando === null && (
        <p className="pacientes-descripcion">
          Todavía no se registraron objetivos.
        </p>
      )}

      {registros.map((objetivo) => (
        <div className="objetivo-registro" key={objetivo.id}>
          <div>
            <strong>{objetivo.descripcion}</strong>
            <p>
              {etiquetasEstado[objetivo.estado]} · Inicio: {mostrarFecha(objetivo.fecha_inicio)}
              {objetivo.fecha_cierre && ` · Cierre: ${mostrarFecha(objetivo.fecha_cierre)}`}
            </p>
            {objetivo.observaciones_generales && (
              <p>Observaciones: {objetivo.observaciones_generales}</p>
            )}
          </div>

          <button type="button" onClick={() => abrirFormulario(objetivo.id)}>
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
            {editando === "nuevo" ? "Nuevo objetivo" : "Editar objetivo"}
          </h3>

          <label>
            Descripción del objetivo
            <textarea
              name="descripcion"
              rows={3}
              required
              defaultValue={objetivoActual?.descripcion ?? ""}
            />
          </label>

          <label>
            Fecha de inicio
            <input
              type="date"
              name="fecha_inicio"
              required
              defaultValue={objetivoActual?.fecha_inicio ?? ""}
            />
          </label>

          <label>
            Estado
            <select
              name="estado"
              value={estadoFormulario}
              onChange={(evento) => {
                setEstadoFormulario(evento.target.value as EstadoObjetivo);
                setError("");
              }}
            >
              <option value="activo">Activo</option>
              <option value="cumplido">Cumplido</option>
              <option value="cerrado">Cerrado sin cumplimiento</option>
            </select>
          </label>

          {estadoFormulario !== "activo" && (
            <label>
              Fecha de cierre
              <input
                type="date"
                name="fecha_cierre"
                required
                defaultValue={objetivoActual?.fecha_cierre ?? ""}
              />
            </label>
          )}

          <label>
            Observaciones generales
            <textarea
              name="observaciones_generales"
              rows={3}
              defaultValue={objetivoActual?.observaciones_generales ?? ""}
            />
          </label>

          {error && <p role="alert">{error}</p>}

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton">
              Guardar objetivo
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