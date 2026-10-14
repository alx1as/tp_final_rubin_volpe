
import "./App.css";
import SideBar from "./components/sidebar/SideBar";
import Pacientes from "./modulos/pacientes/Pacientes";

export default function App() {
  return (
    <div className="estructura-app">
      <SideBar />

      <main className="contenido-principal">
        <Pacientes />
      </main>
    </div>
  );
}
