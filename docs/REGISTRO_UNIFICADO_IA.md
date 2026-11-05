# TRAMA · Registro unificado de sesiones

## Propósito

Registrar desde un único formulario una sesión y cero o varias observaciones, manteniendo el modelo relacional de la propuesta aprobada. La profesional puede dictar o escribir una nota, usar la transcripción como nota general o pedir sugerencias de organización con IA.

## Flujo de uso

1. Nueva sesión: seleccionar fecha, asistencia y completar la nota general si corresponde.
2. Grabar, transcribir y corregir la transcripción (o completar manualmente).
3. Elegir **Usar como nota general** o **Organizar con IA**.
4. Si se organiza, Groq puede proponer una nota general y hasta seis observaciones con objetivos sugeridos. Todas se pueden corregir antes de guardar.
5. Agregar, modificar o quitar bloques de observación manualmente. La asociación a objetivos es opcional.
6. **Guardar sesión** confirma una sola operación de base de datos: sesión y observaciones.
7. Para editar un registro existente, usar **Editar registro**: se cargan la sesión y sus observaciones en el mismo formulario. Quitar una observación persistida exige confirmación; la eliminación ocurre solo al guardar.

La IA solo organiza el texto y sugiere objetivos **existentes del paciente**; no crea objetivos, no cambia sus estados ni formula diagnósticos. La persona profesional revisa y confirma el resultado.

## Endpoints nuevos

- `POST /api/pacientes/{paciente_id}/sesiones/completa`: creación de sesión con observaciones en una transacción.
- `PATCH /api/pacientes/{paciente_id}/sesiones/{sesion_id}/completa`: edición, alta y eliminación confirmada de observaciones dentro de una transacción.
- `POST /api/pacientes/{paciente_id}/observaciones/organizar-registro`: genera sugerencias no persistidas; requiere autenticación y autorización para ese paciente.

Se conservaron los endpoints anteriores de sesiones, observaciones y transcripción. **No requiere migraciones ni librerías adicionales.**

## Privacidad

El organizador envía el texto de la transcripción y las descripciones de los objetivos al servicio Groq. No envía automáticamente el nombre ni otros datos personales estructurados de la ficha. **La nota libre sí podría incluir datos identificatorios**; para trabajar con casos reales deben evaluarse las autorizaciones y medidas de protección aplicables. Evitá datos identificatorios en la nota enviada al modelo. El archivo de audio no se conserva de manera permanente.

## Verificación

Desde la raíz del repositorio:

```bash
cd frontend
npm run build
npm run lint
cd ../backend
.venv/bin/python -m pytest tests/test_registro_completo_unit.py -v
```

La prueba de integración con PostgreSQL **solo** se ejecuta si existe una base exclusiva de pruebas, configurada mediante `TEST_DATABASE_URL` y terminada en `_test`:

```bash
.venv/bin/python -m pytest tests/test_registro_completo_integration.py -v
```

## Pruebas manuales antes de subir

1. Crear una sesión sin observaciones; guardar, salir y volver.
2. Crear una sesión con dos observaciones y objetivos diferentes; guardar y recargar.
3. Dictar una nota breve, transcribir y elegir **Usar como nota general**; verificar persistencia.
4. Dictar dos actividades, elegir **Organizar con IA**, corregir los campos y los objetivos sugeridos; guardar y recargar.
5. Editar una sesión existente, modificar una observación, eliminar otra y agregar una tercera; comprobar resultados.
6. Inducir un error antes del guardado: el formulario debe conservarse y PostgreSQL no debe almacenar un registro incompleto.
7. Si la conexión se corta **después** de que PostgreSQL confirma pero antes de recibir la respuesta, comprobar el listado antes de reintentar; la protección transaccional no garantiza idempotencia de una solicitud repetida por red.

No se hizo commit, push ni merge automáticamente.
