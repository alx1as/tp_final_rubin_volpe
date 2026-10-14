
import { useState } from "react";
import { Home, Menu } from "lucide-react";
import "./sideBar.css";

export default function SideBar() {
  const [contraida, setContraida] = useState(false);

  return (
    <aside className={`barra-lateral ${contraida ? "contraida" : ""}`}>
      <div className="cabecera">
        {!contraida && <span className="logo">Seguimiento</span>}

        <button
          type="button"
          className="boton-menu"
          onClick={() => setContraida(!contraida)}
          aria-label="Abrir o cerrar menú"
        >
          <Menu size={21} />
        </button>
      </div>

      <nav className="navegacion">
        <button type="button" className="opcion activa" aria-current="page">
          <Home size={19} />
          {!contraida && <span>Inicio - Pacientes</span>}
        </button>
      </nav>
    </aside>
  );
}
