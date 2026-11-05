import { useState } from "react";
import { PanelLeftClose, PanelLeftOpen, UsersRound } from "lucide-react";
import MarcaTrama from "../MarcaTrama";
import "./sideBar.css";

export default function SideBar() {
  const [contraida, setContraida] = useState(false);
  return (
    <aside className={`barra-lateral ${contraida ? "contraida" : ""}`} aria-label="Navegación principal">
      <div className="sidebar-top">
        <MarcaTrama compacta={contraida} lateral />
        <button type="button" className="boton-menu" onClick={() => setContraida(!contraida)}
          aria-label={contraida ? "Expandir menú" : "Contraer menú"} title={contraida ? "Expandir menú" : "Contraer menú"}>
          {contraida ? <PanelLeftOpen size={19} /> : <PanelLeftClose size={19} />}
        </button>
      </div>
      {!contraida && <p className="sidebar-etiqueta">ESPACIO DE TRABAJO</p>}
      <nav className="navegacion" aria-label="Secciones">
        <span className="opcion activa" aria-current="page" title="Pacientes">
          <UsersRound size={19} strokeWidth={1.9} aria-hidden="true" />
          {!contraida && <span>Pacientes</span>}
        </span>
      </nav>
      <div className="sidebar-pie">{!contraida && <><span className="sidebar-pie-linea" /><span>Seguimiento psicopedagógico</span><small>Registro y continuidad</small></>}</div>
    </aside>
  );
}
