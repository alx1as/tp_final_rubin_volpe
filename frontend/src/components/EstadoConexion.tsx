import { useEffect, useState } from "react";
import { CircleAlert, CircleCheck } from "lucide-react";
import { consultarSalud } from "../servicios/api";

export default function EstadoConexion() {
  const [estado, setEstado] = useState<"cargando" | "ok" | "error">("cargando");
  const [detalle, setDetalle] = useState("Comprobando conexión con la API...");
  useEffect(() => {
    let vigente = true;
    consultarSalud().then(({ estado, postgresql }) => {
      if (!vigente) return;
      const disponible = estado === "ok" && postgresql === "conectado";
      setEstado(disponible ? "ok" : "error");
      setDetalle(disponible ? "API conectada · PostgreSQL conectado" : "API conectada · PostgreSQL no disponible");
    }).catch(() => {
      if (vigente) { setEstado("error"); setDetalle("No se pudo conectar con la API"); }
    });
    return () => { vigente = false; };
  }, []);
  return (
    <span className={`estado-conexion estado-${estado}`} role="status" title={detalle} aria-label={detalle}>
      {estado === "error" ? <CircleAlert size={15} aria-hidden="true" /> : <CircleCheck size={15} aria-hidden="true" />}
      <span>{estado === "ok" ? "Sistema disponible" : estado === "cargando" ? "Comprobando sistema" : "Revisar conexión"}</span>
    </span>
  );
}
