# Organización asistida de observaciones (extensión opcional)

Esta función usa **el texto ya transcripto o escrito** en Nota libre de una observación. No toca el audio ni cambia los contratos de sesiones/observaciones. Envía el texto al proveedor configurado en `GROQ_API_KEY`, recibe una sugerencia estructurada y la muestra para edición. La IA no crea sesiones ni observaciones.

Recorrido: abrir un paciente → abrir una sesión existente → agregar/editar observación → incorporar transcripción a Nota libre → «Organizar nota libre con IA» → revisar cada sugerencia → aplicar → **Guardar observación**. El registro manual continúa disponible.

El usuario puede conservar el texto original (opción predeterminada) o reemplazarlo por el contenido no clasificado. Si el texto original cambia mientras revisa la sugerencia, el sistema evita sobrescribirlo al optar por reemplazarlo.

Límites: hasta 12.000 caracteres por solicitud. El backend valida la salida del modelo. La sugerencia no vincula automáticamente objetivos ni asigna diagnósticos. Solo están permitidas las categorías de observación existentes. Campos sin respaldo deben quedar vacíos.

Pruebas: `cd backend && .venv/bin/python -m pytest tests/test_organizacion.py` (o `python -m pytest` con el entorno activado). Verificar manualmente con un paciente ficticio, revisar los cambios, guardar la observación y recargarla. No se almacenan audios a través de esta función.
