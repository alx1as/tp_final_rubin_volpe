from sqlmodel import Session, select


def check_database(session: Session) -> bool:
    """Consulta PostgreSQL en cada llamada, sin escribir ni comprobar tablas."""
    return session.exec(select(1)).one() == 1
