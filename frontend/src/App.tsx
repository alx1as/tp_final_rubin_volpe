import { useEffect, useState } from "react";
import "./App.css";
import SideBar from "./components/sidebar/SideBar";
import Pacientes from "./modulos/pacientes/Pacientes";
import EstadoConexion from "./components/EstadoConexion";
import AccesoProfesional from "./modulos/autenticacion/AccesoProfesional";
import {
  cerrarSesion,
  ErrorAPI,
  obtenerSesionActual,
  type ProfesionalAutenticado,
} from "./servicios/api";

export default function App() {
  const [profesional, setProfesional] = useState<ProfesionalAutenticado | null>(null);
  const [comprobando, setComprobando] = useState(true);
  const [errorInicio, setErrorInicio] = useState("");
  const [errorSalida, setErrorSalida] = useState("");
  const [cerrando, setCerrando] = useState(false);

  useEffect(() => {
    let vigente = true;
    obtenerSesionActual()
      .then((usuario) => { if (vigente) setProfesional(usuario); })
      .catch(() => { if (vigente) setErrorInicio("No se pudo verificar la sesión. Revisá la conexión con el backend."); })
      .finally(() => { if (vigente) setComprobando(false); });

    return () => { vigente = false; };
  }, []);

  useEffect(() => {
    const sesionVencida = () => setProfesional(null);
    window.addEventListener("sesion-vencida", sesionVencida);
    return () => window.removeEventListener("sesion-vencida", sesionVencida);
  }, []);

  async function salir() {
    setCerrando(true);
    setErrorSalida("");
    try {
      await cerrarSesion();
      setProfesional(null);
    } catch (error) {
      if (error instanceof ErrorAPI && error.status === 401) {
        setProfesional(null);
      } else {
        setErrorSalida("No se pudo cerrar la sesión. Intentá nuevamente.");
      }
    } finally {
      setCerrando(false);
    }
  }

  if (comprobando) {
    return <div className="pantalla-cargando">Comprobando sesión...</div>;
  }
  if (errorInicio) {
    return (
      <div className="pantalla-cargando" role="alert">
        {errorInicio} <button type="button" onClick={() => window.location.reload()}>Reintentar</button>
      </div>
    );
  }
  if (!profesional) {
    return <AccesoProfesional onIngresar={setProfesional} />;
  }

  return (
    <div className="estructura-app">
      <SideBar />
      <main className="contenido-principal">
        <header className="cabecera-sesion">
          <span>{profesional.nombre} {profesional.apellido}</span>
          <button type="button" onClick={salir} disabled={cerrando}>
            {cerrando ? "Cerrando..." : "Cerrar sesión"}
          </button>
        </header>
        {errorSalida && <p role="alert">{errorSalida}</p>}
        <EstadoConexion />
        <Pacientes />
      </main>
    </div>
  );
}
