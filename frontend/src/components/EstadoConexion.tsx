/* Este componente utiliza useEffect para consultar el backend cuando se carga la aplicación.*/
import { useEffect, useState } from "react";
import { consultarSalud } from "../servicios/api";

export default function EstadoConexion() {
  const [mensaje, setMensaje] = useState(
    "Comprobando conexión con la API..."
  );

  useEffect(() => {
    let vigente = true;

    consultarSalud()
      .then(({ estado, postgresql }) => {
        if (!vigente) return;

        setMensaje(
          estado === "ok" && postgresql === "conectado"
            ? "API conectada · PostgreSQL conectado"
            : "API conectada · PostgreSQL no disponible"
        );
      })
      .catch(() => {
        if (vigente) {
          setMensaje("No se pudo conectar con la API");
        }
      });

    return () => {
      vigente = false;
    };
  }, []);

  return (
    <p
      role="status"
      style={{
        marginBottom: 16,
        fontSize: 13,
        color: "var(--color-texto-secundario)",
      }}
    >
      {mensaje}
    </p>
  );
}