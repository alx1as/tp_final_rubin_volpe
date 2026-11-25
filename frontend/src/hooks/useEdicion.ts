import { useCallback, useLayoutEffect, useRef, useState, type FormEvent } from "react";
import { registroEdicion } from "./estadoEdicion";

export function useEstadoEdicion(pendiente: boolean, ocupado: boolean) {
  const [id] = useState(() => Symbol("editor"));
  useLayoutEffect(() => {
    registroEdicion.registrar(id, { pendiente, ocupado });
    return () => registroEdicion.retirar(id);
  }, [id, pendiente, ocupado]);
}

// Los formularios HTML existentes conservan sus campos y contratos. La comparación
// se realiza contra los valores iniciales, no contra clases CSS ni su mera apertura.
function contenido(formulario: HTMLFormElement) {
  const campos: [string, FormDataEntryValue][] = [];
  new FormData(formulario).forEach((valor, nombre) => campos.push([nombre, valor]));
  return JSON.stringify(campos);
}
export function useFormularioEdicion(abierto: boolean, guardando: boolean) {
  const inicial = useRef("");
  const [modificado, setModificado] = useState(false);
  const registrarFormulario = useCallback((formulario: HTMLFormElement | null) => {
    if (formulario) inicial.current = contenido(formulario);
  }, []);
  const detectarCambios = useCallback((evento: FormEvent<HTMLFormElement>) => {
    const formulario = evento.currentTarget;
    // Esperar el render de los campos condicionales (por ejemplo, fecha de cierre).
    queueMicrotask(() => {
      if (formulario.isConnected) setModificado(contenido(formulario) !== inicial.current);
    });
  }, []);
  const reiniciar = useCallback(() => setModificado(false), []);
  useEstadoEdicion(abierto && modificado, guardando);
  return { registrarFormulario, detectarCambios, reiniciar };
}
