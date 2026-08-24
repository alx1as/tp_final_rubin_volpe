import { useState } from "react";
import {
  Home,
  Users,
  CalendarDays,
  Settings,
  Menu,
  Search,
} from "lucide-react";

import "./sideBar.css";

const opcionesMenu = [
  { nombre: "Inicio", icono: Home },
  { nombre: "Pacientes", icono: Users },
  { nombre: "Agenda", icono: CalendarDays },
];

function SideBar() {
  const [contraida, setContraida] = useState(false);
  const [activa, setActiva] = useState("Inicio");

  return (
    <aside className={`barra-lateral ${contraida ? "contraida" : ""}`}>
      <div className="cabecera">
        {!contraida && <span className="logo">Nombre App</span>}

        <button
          className="boton-menu"
          onClick={() => setContraida(!contraida)}
          aria-label="Abrir o cerrar menú"
        >
          <Menu size={21} />
        </button>
      </div>

      <div className="buscador">
        <Search size={18} />
        {!contraida && <input type="text" placeholder="Buscar paciente..." />}
      </div>

      <nav className="navegacion">
        {opcionesMenu.map((opcion) => {
          const Icono = opcion.icono;

          return (
            <button
              key={opcion.nombre}
              className={`opcion ${activa === opcion.nombre ? "activa" : ""}`}
              onClick={() => setActiva(opcion.nombre)}
              title={contraida ? opcion.nombre : undefined}
            >
              <Icono size={19} />
              {!contraida && <span>{opcion.nombre}</span>}
            </button>
          );
        })}
      </nav>

      <div className="pie">
        <button
          className="opcion"
          title={contraida ? "Configuración" : undefined}
        >
          <Settings size={19} />
          {!contraida && <span>Configuración</span>}
        </button>
      </div>
    </aside>
  );
}

export default SideBar;