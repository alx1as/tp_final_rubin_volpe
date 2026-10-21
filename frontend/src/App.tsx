import "./App.css";
import SideBar from "./components/sidebar/SideBar";
import Pacientes from "./modulos/pacientes/Pacientes";
import EstadoConexion from "./components/EstadoConexion";

export default function App() {
  return (
    <div className="estructura-app">
      <SideBar />

      <main className="contenido-principal">
        <EstadoConexion />
        <Pacientes />
      </main>
    </div>
  );
}