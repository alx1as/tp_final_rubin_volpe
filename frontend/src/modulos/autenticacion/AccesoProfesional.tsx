import { useState, type FormEvent } from "react";
import {
  iniciarSesion,
  registrarProfesional,
  type ProfesionalAutenticado,
} from "../../servicios/api";
import "./AccesoProfesional.css";

type Props = {
  onIngresar: (profesional: ProfesionalAutenticado) => void;
};

export default function AccesoProfesional({ onIngresar }: Props) {
  const [modo, setModo] = useState<"login" | "registro">("login");
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setEnviando(true);
    setError("");
    try {
      if (modo === "registro") {
        // El endpoint de registro crea la cuenta, pero no abre sesión.
        await registrarProfesional({ nombre, apellido, email, password });
      }
      const usuario = await iniciarSesion(email, password);
      onIngresar(usuario);
    } catch (fallo) {
      setError(fallo instanceof Error ? fallo.message : "No se pudo completar la operación.");
    } finally {
      setEnviando(false);
    }
  }

  function cambiarModo() {
    setModo((actual) => actual === "login" ? "registro" : "login");
    setError("");
    setPassword("");
  }

  return (
    <main className="pantalla-acceso">
      <section className="tarjeta-acceso">
        <p className="acceso-subtitulo">SEGUIMIENTO PSICOPEDAGÓGICO</p>
        <h1>{modo === "login" ? "Iniciar sesión" : "Crear cuenta profesional"}</h1>
        <p className="acceso-descripcion">Acceso exclusivo para profesionales.</p>
        <form onSubmit={enviar} className="formulario-acceso">
          {modo === "registro" && (
            <>
              <label>Nombre
                <input value={nombre} onChange={(evento) => setNombre(evento.target.value)} required autoComplete="given-name" />
              </label>
              <label>Apellido
                <input value={apellido} onChange={(evento) => setApellido(evento.target.value)} required autoComplete="family-name" />
              </label>
            </>
          )}
          <label>Correo electrónico
            <input type="email" value={email} onChange={(evento) => setEmail(evento.target.value)} required autoComplete="email" />
          </label>
          <label>Contraseña
            <input type="password" value={password} onChange={(evento) => setPassword(evento.target.value)} minLength={modo === "registro" ? 8 : 1} required autoComplete={modo === "login" ? "current-password" : "new-password"} />
          </label>
          {modo === "registro" && <p className="acceso-ayuda">Mínimo 8 caracteres.</p>}
          {error && <p className="acceso-error" role="alert">{error}</p>}
          <button className="acceso-boton" type="submit" disabled={enviando}>
            {enviando ? "Procesando..." : modo === "login" ? "Ingresar" : "Registrarme"}
          </button>
        </form>
        <button className="acceso-cambiar" type="button" onClick={cambiarModo} disabled={enviando}>
          {modo === "login" ? "¿No tenés cuenta? Registrate" : "¿Ya tenés cuenta? Iniciá sesión"}
        </button>
      </section>
    </main>
  );
}
