import "./MarcaTrama.css";

type Props = { compacta?: boolean; lateral?: boolean };

export default function MarcaTrama({ compacta = false, lateral = false }: Props) {
  return (
    <div className={`marca-trama${compacta ? " marca-trama-compacta" : ""}${lateral ? " marca-trama-lateral" : ""}`}
      role="img" aria-label="TRAMA · Sistema de seguimiento psicopedagógico">
      <img className="marca-trama-simbolo" src="/trama-simbolo.svg" alt="" width="720" height="430" />
      {!compacta && <div className="marca-trama-identidad">
        <span className="marca-trama-nombre">TRAMA</span>
        <span className="marca-trama-descripcion">Sistema de seguimiento<br />psicopedagógico</span>
      </div>}
    </div>
  );
}
