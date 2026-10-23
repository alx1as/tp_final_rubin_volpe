# Contratos del backend: perfil y seguimiento

Este documento describe los contratos implementados y verificados de E3 y E4. La comprobación es
por HTTP y PostgreSQL exclusivo de pruebas. Adaptar o conectar el frontend es
responsabilidad externa y no condiciona el cierre de las tareas del backend.

## Contratos actuales y objetivo

La tabla siguiente conserva la transición del perfil en E3; las secciones de
E4 describen el estado actual de objetivos, sesiones, observaciones y evidencias.

`P` representa `/api/pacientes/{paciente_id}`. Todas las operaciones de dominio
requieren la cookie `sesion` creada por `/api/auth/login`. Sesión ausente,
vencida, revocada o profesional inactivo: `401`. Recursos de otro profesional,
de otro paciente de la ruta o inexistentes: `404`.

| Recurso | Antes de E3 | Contrato de E3 |
| --- | --- | --- |
| Lista de pacientes | Array completo, orden por apellido y nombre. | Objeto paginado; apellido, nombre e ID ascendentes. |
| Paciente individual | Sin consulta ni edición. | GET y PATCH en P, incluida desactivación con `activo=false`. |
| Admisión | GET devuelve null/200 si falta; PUT siempre 200. | GET ausente 404; PUT crea con 201 o reemplaza con 200, conservando un único registro. |
| Escolaridades | Array completo; POST y PUT de reemplazo. | Lista paginada; POST; GET/PATCH individual; PUT completo de compatibilidad. |
| Profesionales tratantes | Array completo; POST y PUT de reemplazo. | Lista paginada; POST; GET/PATCH individual; PUT completo de compatibilidad. |
| Objetivos | Array completo; POST y PUT de reemplazo. | Sin cambios en E3; consulta individual, PATCH y paginación quedan en E4-T01. |

E3 adopta las respuestas paginadas de forma explícita en las rutas del perfil;
no infiere el formato por la presencia de parámetros ni agrega un modo legacy.
El consumidor externo debe leer `items` y los metadatos. Los PUT existentes de
escolaridad y contactos se conservan como reemplazo completo y se marcan como
deprecados en OpenAPI; los nuevos PATCH permiten ediciones parciales. No se
retira ninguna ruta existente en E3 ni se agrega DELETE.

## Listas

Parámetros: `offset=0`, `limit=20`; `offset >= 0` y `1 <= limit <= 100`.
Valores inválidos responden `422`. La respuesta es siempre:

```json
{"items": [], "total": 0, "offset": 0, "limit": 20}
```

`total` cuenta los resultados del contexto autorizado antes de paginar. Un
offset posterior al último resultado devuelve items vacío y conserva total.
Escolaridades y contactos se ordenan por fecha de inicio e ID descendentes.
El listado de pacientes incluye activos e inactivos: desactivar conserva el
registro, sus datos hijos y la posibilidad de consultarlos.

## Cuerpos y transacciones

- JSON snake_case y fechas de dominio `YYYY-MM-DD`.
- La base genera los IDs. El profesional procede de la sesión y el paciente de
  la ruta. Los cuerpos no aceptan `id`, `profesional_id` ni `paciente_id`.
- PATCH: campo omitido conserva su valor; null solo es válido en opcionales.
  Se valida el registro completo resultante antes de modificar o guardar.
  Un PATCH vacío es una operación válida sin cambios.
- Texto obligatorio recortado y no vacío. Texto opcional vacío o compuesto de
  espacios pasa a NULL. Fecha opcional vacía pasa a NULL.
- Se respetan las restricciones de SQL: seguimiento no anterior al nacimiento
  y final de período no anterior a inicio. Varias escolaridades vigentes son
  válidas. Los contactos tratantes no crean cuentas ni permisos.
- PUT de admisión y PUT de compatibilidad reemplazan los campos completos;
  los opcionales omitidos vuelven a NULL. IDs y propietarios no se reasignan.
- Las escrituras se confirman en transacción. Un error revierte la operación;
  conflicto de integridad: 409, PostgreSQL no disponible: 503, sin SQL ni
  valores sensibles en las respuestas. Errores de validación: 422 con detail.

## Verificación HTTP prevista

1. Listas vacías, límites, offsets, total autorizado y desempate por ID.
2. Crear, consultar y editar pacientes propios; null obligatorio rechazado;
   fechas cruzadas validadas contra el registro completo; historial conservado
   al desactivar.
3. Admisión ausente, creación 201, reemplazo 200 y unicidad, incluidos conflictos.
4. Crear/consultar/PATCH períodos y contactos; nulabilidad y orden de fechas;
   PUT completo de compatibilidad y varias escolaridades vigentes.
5. Dos profesionales y dos pacientes del mismo profesional: 401 sin sesión,
   404 para recursos ajenos o de otro padre; ningún cuerpo reasigna identidad.
6. Consultas posteriores recuperan datos confirmados con PostgreSQL real;
   solicitudes inválidas y conflictos no cambian los registros previos.
7. E3 preservó objetivos hasta E4-T01. Ahora se verifican paginación, GET/PATCH,
   estados/cierre, pertenencia y evidencias implementadas en E4-T04.

## Objetivos en E4-T01

La lista de objetivos ahora devuelve el envelope paginado y usa inicio/ID
descendentes, con los mismos límites del perfil. Se agregan GET/PATCH individual
y se conserva PUT completo deprecado. Activo implica cierre null; cumplido y
cerrado requieren cierre no anterior al inicio. PATCH valida el resultado
completo y guarda estado/fecha en una única transacción, sin estados intermedios.
La reapertura exige activo y cierre null. Los consumidores externos deben leer
items y pueden migrar sus ediciones de PUT a PATCH; el backend no edita el cliente.

Los comandos de ejecución y el runner aislado están en [README.md](README.md).

## Sesiones, observaciones y evidencias en E4

- Sesiones: GET/POST en P/sesiones y GET/PATCH individual. La lista ordena
  fecha/ID descendentes; fecha y presente booleano son obligatorios al crear,
  nota_general es opcional. Ausencia y cero observaciones son válidos.
- Observaciones: GET/POST por sesión y GET/PATCH individual. Orden por ID
  ascendente. Al menos uno de contexto/conducta_observable/intervencion/resultado/
  nota_libre debe tener texto. Objetivo opcional y perteneciente al mismo paciente;
  se valida al crear o editar el vínculo. Null desvincula el objetivo.
- Evidencias: GET P/objetivos/{objetivo_id}/observaciones devuelve las observaciones
  y fecha_sesion derivada; ordena fecha de sesión/ID de observación descendentes.
  Filtra objetivo y paciente autorizado, sin copiar filas ni almacenar cronología.
- Las listas usan los mismos límites y envelope paginado. El padre procede de la
  ruta y no se reasigna en cuerpos. PATCH valida contenido y vínculos antes de
  escribir. Recurso inexistente o ajeno: 404; contenido/fecha/tipo inválido: 422.
- No hay PUT ni DELETE para sesiones/observaciones. Los PUT de compatibilidad
  anteriores se conservan solo en objetivos/escolaridades/contactos. El historial
  de seguimiento sigue disponible tras desactivar al paciente.
