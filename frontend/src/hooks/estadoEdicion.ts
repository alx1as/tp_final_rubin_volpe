export type EstadoEdicion = { pendiente: boolean; ocupado: boolean };

// Un único registro para los editores montados en el espacio de trabajo.
export function crearRegistroEdicion() {
  const editores = new Map<symbol, EstadoEdicion>();
  return {
    registrar(id: symbol, estado: EstadoEdicion) { editores.set(id, estado); },
    retirar(id: symbol) { editores.delete(id); },
    estado(): EstadoEdicion {
      const valores = [...editores.values()];
      return { pendiente: valores.some((e) => e.pendiente), ocupado: valores.some((e) => e.ocupado) };
    },
    confirmar(confirmar: (mensaje: string) => boolean, avisar: (mensaje: string) => void) {
      const { pendiente, ocupado } = this.estado();
      if (ocupado) { avisar("Hay una operación en curso. Esperá a que termine."); return false; }
      return !pendiente || confirmar("Hay cambios o audio sin guardar. ¿Querés descartarlos?");
    },
  };
}
export const registroEdicion = crearRegistroEdicion();
export function confirmarSalidaEditor() {
  return registroEdicion.confirmar((mensaje) => window.confirm(mensaje), (mensaje) => window.alert(mensaje));
}
