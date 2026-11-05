import { useState, type RefObject } from "react";
import { organizarNotaConIA, type SugerenciaObservacion } from "../../servicios/api-seguimiento";
import "./OrganizadorObservacion.css";

type Campo = keyof SugerenciaObservacion;
const CAMPOS: { clave: Campo; etiqueta: string }[] = [
  { clave: "contexto", etiqueta: "Contexto" },
  { clave: "conducta_observable", etiqueta: "Conducta observable" },
  { clave: "intervencion", etiqueta: "Intervención" },
  { clave: "resultado", etiqueta: "Resultado" },
  { clave: "nota_libre", etiqueta: "Nota libre (sin clasificar)" },
];

type Props = { pacienteId: number; formularioRef: RefObject<HTMLFormElement | null> };

function campoFormulario(formulario: HTMLFormElement | null, nombre: Campo): HTMLTextAreaElement | null {
  const control = formulario?.elements.namedItem(nombre);
  return control instanceof HTMLTextAreaElement ? control : null;
}

export default function OrganizadorObservacion({ pacienteId, formularioRef }: Props) {
  const [generando, setGenerando] = useState(false);
  const [sugerencia, setSugerencia] = useState<SugerenciaObservacion | null>(null);
  const [textoOriginal, setTextoOriginal] = useState("");
  const [conservarOriginal, setConservarOriginal] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");

  async function organizar() {
    const texto = campoFormulario(formularioRef.current, "nota_libre")?.value.trim() || "";
    if (texto.length < 5) {
      setError("Escribí o incorporá una transcripción en Nota libre antes de organizarla.");
      return;
    }
    setGenerando(true);
    setError("");
    setMensaje("");
    setSugerencia(null);
    try {
      const datos = await organizarNotaConIA(pacienteId, texto);
      setTextoOriginal(texto);
      setSugerencia(datos);
      setConservarOriginal(true);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo organizar la nota.");
    } finally {
      setGenerando(false);
    }
  }

  function aplicar() {
    if (!sugerencia) return;
    const formulario = formularioRef.current;
    if (!formulario) return;
    const nota = campoFormulario(formulario, "nota_libre");
    if (!nota) return;
    const textoEditado = nota.value.trim();
    // Nunca borrar texto editado después de solicitar las sugerencias.
    if (!conservarOriginal && textoEditado !== textoOriginal) {
      setError("La nota libre cambió mientras revisabas la propuesta. Volvé a organizarla para no perder cambios.");
      return;
    }
    if (!["contexto", "conducta_observable", "intervencion", "resultado", "nota_libre"]
        .some((clave) => Boolean(sugerencia[clave as Campo]?.trim()))) {
      setError("La propuesta está vacía. Revisá el texto antes de continuar.");
      return;
    }

    for (const campo of CAMPOS) {
      const control = campoFormulario(formulario, campo.clave);
      const propuesto = sugerencia[campo.clave]?.trim();
      if (!control || !propuesto || campo.clave === "nota_libre") continue;
      // No sobrescribir lo que el profesional ya completó.
      control.value = [control.value.trim(), propuesto].filter(Boolean).join("\n\n");
      control.dispatchEvent(new Event("input", { bubbles: true }));
    }
    if (!conservarOriginal) {
      nota.value = sugerencia.nota_libre?.trim() || "";
      nota.dispatchEvent(new Event("input", { bubbles: true }));
    }
    setSugerencia(null);
    setMensaje("Propuesta incorporada al formulario. Revisá los campos y presioná Guardar observación.");
    setError("");
  }

  return (
    <div className="organizador-observacion">
      <div className="organizador-observacion-titulo">
        <strong>Organizar nota con IA</strong>
        <p>Después de transcribir, incorporá el texto en Nota libre. La IA puede sugerir qué corresponde a contexto, conducta, intervención o resultado. También podés escribir normalmente.</p>
      </div>
      <button type="button" className="organizador-observacion-boton"
        onClick={() => void organizar()} disabled={generando}>
        {generando ? "Organizando..." : "Organizar nota libre con IA"}
      </button>
      <p className="organizador-observacion-aviso">Se envía el texto de la nota a Groq para obtener sugerencias. Evitá incluir nombres y otros datos identificatorios. No se guarda automáticamente.</p>
      {sugerencia && (
        <div className="organizador-observacion-propuesta">
          <h4>Revisá la propuesta antes de aplicarla</h4>
          <p>Los campos sin información suficiente quedan vacíos. Podés corregir cualquier texto.</p>
          {CAMPOS.map(({ clave, etiqueta }) => (
            <label key={clave}>{etiqueta}
              <textarea rows={2} value={sugerencia[clave] || ""}
                onChange={(evento) => setSugerencia((anterior) => anterior ? {
                  ...anterior, [clave]: evento.target.value || null,
                } : null)} />
            </label>
          ))}
          <label className="organizador-observacion-check">
            <input type="checkbox" checked={conservarOriginal}
              onChange={(evento) => setConservarOriginal(evento.target.checked)} />
            Conservar la transcripción original en Nota libre
          </label>
          <div className="organizador-observacion-acciones">
            <button type="button" className="pacientes-boton" onClick={aplicar}>Aplicar al formulario</button>
            <button type="button" onClick={() => setSugerencia(null)}>Descartar propuesta</button>
          </div>
        </div>
      )}
      {mensaje && <p className="organizador-observacion-exito" role="status">{mensaje}</p>}
      {error && <p className="organizador-observacion-error" role="alert">{error}</p>}
    </div>
  );
}
