// Las fechas de dominio son días calendario ISO (AAAA-MM-DD), sin zona horaria.
export function escolaridadVigente<T extends { fecha_inicio: string; fecha_fin: string | null }>(registros: T[], hoy: string): T | undefined {
  return registros.filter((r) => r.fecha_inicio <= hoy && (!r.fecha_fin || r.fecha_fin >= hoy))
    .sort((a, b) => b.fecha_inicio.localeCompare(a.fecha_inicio))[0];
}

export function periodoSesiones(sesiones: { fecha: string }[], hoy: string) {
  const fechas = sesiones.map((s) => s.fecha).sort();
  return { periodo_desde: fechas[0] ?? hoy, periodo_hasta: fechas[fechas.length - 1] ?? hoy };
}
