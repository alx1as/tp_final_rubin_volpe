import { useState, type FormEvent } from "react";

export type EstadoObjetivo = "activo" | "cumplido" | "cerrado";

export type Objetivo = {
  id: number;
  descripcion: string;
  fecha_inicio: string;
  estado: EstadoObjetivo;
  fecha_cierre: string | null;
  observaciones_generales: string | null;
};

export type ObjetivoGuardar = Omit<Objetivo, "id">;

type Props = {
  registros: Objetivo[];
  onGuardar: (registro: ObjetivoGuardar, id?: number) => Promise<void>;
  cargando: boolean;
  error: string;
};

const mostrarFecha = (fecha: string) =>
  fecha ? fecha.split("-").reverse().join("/") : "Sin fecha";

const etiquetasEstado: Record<EstadoObjetivo, string> = {
  activo: "Activo",
  cumplido: "Cumplido",
  cerrado: "Cerrado sin cumplimiento",
};

export default function ObjetivosPaciente({ registros, onGuardar, cargando, error }: Props) {
  const [editando, setEditando] = useState<number | "nuevo" | null>(null);
  const [estadoFormulario, setEstadoFormulario] = useState<EstadoObjetivo>("activo");
  const [errorFormulario, setErrorFormulario] = useState("");
  const [guardando, setGuardando] = useState(false);

  const objetivoActual = registros.find((objetivo) => objetivo.id === editando);

  function abrirFormulario(id: number | "nuevo") {
    const registro = registros.find((objetivo) => objetivo.id === id);
    setEstadoFormulario(registro?.estado ?? "activo");
    setErrorFormulario("");
    setEditando(id);
  }

  async function guardar(evento: FormEvent<HTMLFormElement>) {
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
      setErrorFormulario("Completá la descripción y la fecha de inicio.");
      return;
    }

    if (estadoFormulario !== "activo" && !fecha_cierre) {
      setErrorFormulario("Indicá la fecha de cierre del objetivo.");
      return;
    }

    if (fecha_cierre && fecha_cierre < fecha_inicio) {
      setErrorFormulario("La fecha de cierre no puede ser anterior a la de inicio.");
      return;
    }

    setGuardando(true);
    setErrorFormulario("");
    try {
      await onGuardar({
        descripcion,
        fecha_inicio,
        estado: estadoFormulario,
        fecha_cierre: fecha_cierre || null,
        observaciones_generales: observaciones_generales || null,
      }, typeof editando === "number" ? editando : undefined);
      setEditando(null);
    } catch {
      // La ficha muestra el error y conservamos el formulario para reintentar.
    } finally {
      setGuardando(false);
    }
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
          disabled={cargando || guardando}
          >
            + Agregar objetivo
          </button>
        )}
      </div>

      {cargando && <p className="pacientes-descripcion">Cargando objetivos...</p>}
      {error && <p role="alert">{error}</p>}

      {!cargando && registros.length === 0 && editando === null && (
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

          <button type="button" onClick={() => abrirFormulario(objetivo.id)} disabled={cargando || guardando}>
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
                setErrorFormulario("");
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

          {errorFormulario && <p role="alert">{errorFormulario}</p>}

          <div className="pacientes-acciones">
            <button type="submit" className="pacientes-boton" disabled={guardando}>
              {guardando ? "Guardando..." : "Guardar objetivo"}
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