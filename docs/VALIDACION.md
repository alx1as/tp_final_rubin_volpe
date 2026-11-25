# Validación de TRAMA

## Verificaciones automatizadas

Desde la raíz, con dependencias instaladas:

```bash
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
```

Backend (activar primero `backend/.venv`, instalar `requirements-dev.txt`):

```bash
python -m pytest -c backend/pytest.ini -m "not integration" -q
export POSTGRES_BIN="$(pg_config --bindir)"
python backend/tests/run_postgres_tests.py
```

El último comando crea un PostgreSQL temporal de pruebas y no utiliza la base de trabajo. GitHub Actions ejecuta las verificaciones del frontend y la suite de backend en cada push y pull request.

## Validación de recorridos

Usar exclusivamente cuentas y pacientes ficticios. Registrar el resultado real de cada recorrido antes de entregar; las pruebas unitarias no sustituyen la prueba en navegador.

| Recorrido | Resultado esperado |
|---|---|
| Registro profesional, acceso y cierre | La sesión se mantiene al recargar; el cierre vuelve al acceso. |
| Dos profesionales | Los registros de un profesional no son accesibles por otro. |
| Alta y edición de paciente | El listado y la ficha muestran los datos persistidos. |
| Admisión, escolaridad y profesionales | Crear y editar, comprobar persistencia al reabrir. |
| Escolaridad con fecha de fin futura | Figura como vigente hasta la fecha de finalización. |
| Formulario intacto / modificado | El primero permite salir; el segundo pide confirmar. Cancelar mantiene el contenido. |
| Guardado en curso | No se puede cambiar de editor ni cerrar sesión hasta que termine. |
| Sesión y observaciones | Guardar en conjunto; revisar detalle, objetivo vinculado y cronología. |
| Audio | Probar permiso, grabación, escucha, transcripción y descarte. No se guarda una sesión con audio aún pendiente. |
| IA de organización | Revisar las propuestas antes de guardar; si falla, el texto sigue disponible. |
| Evidencias y cronología | Abrir sesión de origen, incluso de otro mes, y regresar al objetivo. |
| Informe nuevo | Abrir y salir sin editar no muestra advertencia; modificar fechas o contenido sí. |
| Informe con IA | Generar, revisar, editar, guardar, finalizar y reabrir. |
| Informe histórico | No presentar el cierre de un objetivo posterior al período como logro del período. |
| Falla de red o de IA | Mostrar el error y conservar el formulario para reintentar. |
| Escritorio y móvil | Verificar navegación, foco, formularios y lectura. |
| Despliegue HTTPS | Verificar login, cookie, salud, audio e informes desde la URL publicada. |

## Alcance

Las pruebas de frontend cubren reglas unitarias de edición, fechas y contratos HTTP con respuestas simuladas. Los recorridos anteriores requieren ejecución con navegador y backend. No se necesita un proveedor real para las pruebas automatizadas de integración simuladas; la demostración completa de IA sí requiere una clave configurada.
