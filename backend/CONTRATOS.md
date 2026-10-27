# Contratos del backend: perfil, seguimiento e informes

Este documento describe los contratos implementados de E3, E4, E5 y la preparación de E6. La comprobación es
por HTTP y PostgreSQL exclusivo de pruebas. Adaptar o conectar el frontend es
responsabilidad externa y no condiciona el cierre de las tareas del backend.

## Contratos actuales y objetivo

La tabla siguiente conserva la transición del perfil en E3; las secciones de
E4 y E5 describen objetivos, sesiones, observaciones, evidencias, cronología e informes.

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

## Cronología en E5-T01

`GET P/cronologia` devuelve `Pagina[EntradaCronologia]`. Cada item es una sesión
(`id`, `paciente_id`, `fecha`, `presente`, `nota_general`) más `observaciones`,
una lista completa de `ObservacionRespuesta` ordenada por ID ascendente.
Las sesiones ordenan fecha/ID descendentes. `desde`/`hasta` son fechas ISO
opcionales inclusivas; fecha inválida o intervalo invertido: 422.

Se pagina por sesión con `offset=0`, `limit=20` (máximo 100). `total` cuenta
sesiones del paciente autorizado con los filtros aplicados, antes de paginar.
Incluye ausencias y sesiones sin observaciones (`[]`); un offset fuera de rango
devuelve items vacío conservando el total. La consulta usa las fuentes actuales
sin crear tablas ni copiar filas. Requiere sesión, cuenta activa y paciente
propio; conserva el historial al desactivar. No agrega métodos de escritura.

El frontend puede reemplazar sus múltiples consultas por este endpoint y agregar
los filtros de fechas; este cambio no modifica automáticamente la interfaz.

## Informes en E5-T02/T03

- `GET P/informes`: página de `InformeRespuesta`, fecha/ID descendentes, con
  los límites y metadatos comunes. `GET P/informes/{informe_id}`: informe propio.
- `POST P/informes`: 201, requiere `titulo`, `periodo_desde`, `periodo_hasta`,
  `contenido`; fecha opcional con valor por defecto de fecha local del servidor.
  Se recortan título/contenido y se rechaza texto vacío o fechas inválidas.
  El período es inclusivo y admite un único día; `hasta < desde`: 422.
- Solo se crea como `borrador`. `asistido_ia` es booleano estricto y por defecto
  false; se admite true al guardar contenido asistido que revisó el profesional,
  conforme al contrato futuro de E6. La marca no invoca servicios externos.
- Respuesta: ID, paciente, título, fecha, período, contenido, estado y marca de
  asistencia. Los IDs de contexto no son editables desde los cuerpos.
- Paciente/propietario ajeno o inexistente: 404; sesión inválida o cuenta
  inactiva: 401. Desactivar conserva el informe. No hay DELETE de dominio.
- `PATCH P/informes/{informe_id}` valida el registro completo combinado con
  los campos recibidos. Ningún campo del informe admite null; campos omitidos
  conservan valor y un cuerpo vacío no cambia datos. El período puede moverse
  enviando ambos extremos en una sola transacción. Una edición inválida no
  modifica ningún campo.
- Finalizar requiere `estado=finalizado` explícito; editar texto conserva el
  estado actual. Un finalizado sigue siendo editable y puede volver a borrador
  mediante PATCH explícito, conforme a los dos estados del SQL. No hay firma ni
  bloqueo irreversible, ni cambios en los registros fuente del seguimiento.

Ejemplo de `POST P/informes` (requiere cookie de sesión):

```json
{
  "titulo": "Seguimiento de enero",
  "fecha": "2026-02-01",
  "periodo_desde": "2026-01-01",
  "periodo_hasta": "2026-01-31",
  "contenido": "Texto ficticio revisado por el profesional."
}
```

El POST devuelve el ID, `estado=borrador` y `asistido_ia=false` además de los
campos enviados. Guardar cambios: `PATCH P/informes/{informe_id}` con los campos
modificados; finalizar después de revisar: `{"estado":"finalizado"}`. El backend
no completa contenido desde sesiones automáticamente en esta etapa. El cliente
debe agregar la sección de informes y consumir estas rutas; no requiere una
migración porque la tabla `informe` ya forma parte del esquema inicial.

## Preparación de transcripción y generación en E6

Los adaptadores se sustituyen mediante `obtener_transcriptor` y
`obtener_generador_informes` de `app.integrations.dependencies`. Ambas dependencias
devuelven None en ejecución normal: no hay proveedor elegido ni simulaciones
registradas. Sin proveedor, las rutas responden 503 con
`{"detail":"Servicio externo no configurado"}`. Una falla o respuesta inválida del
adaptador responde 503 con `{"detail":"Servicio externo no disponible"}`, sin
detalles privados. Elegir y conectar servicios reales corresponde a MVP-T01/T02.

### Audio temporal

`POST /api/transcripciones`, con cookie de sesión y cuenta activa. El cuerpo es
`multipart/form-data` con un archivo en el campo `audio`; responde 200 con
`{"texto":"Texto editable"}`. La ausencia del archivo o un archivo vacío con
proveedor configurado responde 422. Nombre y MIME son solo metadatos; los formatos
y la decodificación concreta dependen del futuro proveedor real.

El stream se presta al transcriptor, se rebobina antes de procesarlo y se cierra
en todos los caminos. El parser puede usar un spool temporal de disco, eliminado
al cerrarlo. No se usa el nombre del cliente como ruta de almacenamiento. Los
adaptadores reales deberán limpiar cualquier recurso propio y fijar timeouts.
El texto y el audio no se guardan automáticamente: el cliente permite corregir
o descartar la transcripción y guarda solo el texto confirmado mediante las
operaciones habituales de sesiones/observaciones.

### Borrador temporal

`POST P/informes/generar`, con JSON `titulo`, `periodo_desde`, `periodo_hasta`.
Texto obligatorio recortado, fechas ISO y período no invertido; entrada inválida:
422. El paciente debe pertenecer al profesional autenticado; inexistente/ajeno:
404, antes de llamar al generador.

El generador recibe datos públicos del paciente, sesiones del período completo
(sin el límite de las listas paginadas), sus observaciones y los objetivos propios
vinculados a esas observaciones. Fechas de sesión inclusivas; orden fecha/ID
descendentes y observaciones por ID ascendente. Ausencias y sesiones sin notas
se conservan. Un período sin sesiones entrega fuentes vacías al adaptador; no
se agregan registros ficticios. El adaptador debe sintetizar solo los datos
recibidos, sin diagnósticos, y explicar la insuficiencia de registros cuando
corresponda. Las fuentes son copias separadas de ORM y no se modifican al generar.

La aplicación controla el título, fecha local del servidor, período,
`estado=borrador` y `asistido_ia=true`; el adaptador devuelve solo contenido.
Respuesta 200 sin `id` ni `paciente_id`, compatible con `InformeCrear`:

```json
{
  "titulo": "Seguimiento de enero",
  "fecha": "2026-02-01",
  "periodo_desde": "2026-01-01",
  "periodo_hasta": "2026-01-31",
  "contenido": "Borrador editable para revisión profesional.",
  "estado": "borrador",
  "asistido_ia": true
}
```

La generación no inserta un informe ni actualiza fuentes. Después de revisar y
editar, el cliente guarda mediante `POST P/informes`; finalizar sigue siendo
una acción explícita separada. Una falla externa no impide el registro manual
ni la consulta de cronología/informes. E6 no acredita transcripción o IA reales
ni el recorrido completo desde el navegador.
