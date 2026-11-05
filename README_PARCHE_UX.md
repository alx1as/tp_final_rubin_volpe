# Parche UX/UI integral — Sistema de Seguimiento Psicopedagógico

## Objetivo

Rediseñar la experiencia del frontend sin alterar el backend, sus endpoints, los datos almacenados ni la integración con Groq. Se parte de la versión incluida en `tp_final_rubin_volpe-main (8).zip` (4/11/2026). El parche no modifica el alcance del MVP.

## Qué cambia

- **Ficha del paciente:** presentación compacta con edad calculada, escolaridad vigente (si consta), estado, inicio y accesos rápidos a Sesiones, Objetivos e Informes.
- **Inicio:** prioridad para la última sesión, objetivos activos, motivo de consulta y contexto escolar; estadísticas secundarias.
- **Historia y contexto:** cuatro categorías explorables (Datos personales, Admisión, Escolaridad y Profesionales). Los formularios originales se conservan, pero se consultan en vistas separadas. Antecedentes y detalles escolares se expanden a demanda.
- **Seguimiento:** Sesiones y Objetivos dejan de competir por la misma pantalla. Se añade filtro mensual de sesiones y filtro de estado de objetivos. Las observaciones aparecen justo debajo de su sesión. Los objetivos abren su evidencia de forma contextual.
- **Navegación entre registros:** una evidencia puede abrir su sesión original, desde la que se puede regresar al objetivo.
- **Cronología:** selector mensual discreto, vista de actividad consultada mediante `GET /api/pacientes/{paciente_id}/cronologia?desde=...&hasta=...`, detalle por sesión y observaciones expandibles. Utiliza el endpoint y la paginación ya existentes. En móvil se accede a un panel con selector de mes.
- **Informes:** filtros por estado (todos, borradores, finalizados), conservar editor/IA/vista previa y avisos de cambios pendientes.
- **Estética:** paleta verde petróleo/blanco cálido y nuevas escalas de lectura y espacios, incluyendo acceso profesional, barra lateral y grabadora.
- **Carga:** las pantallas secundarias de la ficha se montan solamente cuando se seleccionan, evitando consultas tempranas de módulos y descartando formularios al confirmar que se sale de ellos.

## Archivos modificados

- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/components/sidebar/sideBar.css`
- `frontend/src/modulos/autenticacion/AccesoProfesional.css`
- `frontend/src/modulos/pacientes/AdmisionPaciente.tsx`
- `frontend/src/modulos/pacientes/CronologiaPaciente.tsx`
- `frontend/src/modulos/pacientes/EscolaridadPaciente.tsx`
- `frontend/src/modulos/pacientes/EvidenciasObjetivo.tsx`
- `frontend/src/modulos/pacientes/FichaPaciente.tsx`
- `frontend/src/modulos/pacientes/GrabadoraNota.css`
- `frontend/src/modulos/pacientes/InformesPaciente.tsx`
- `frontend/src/modulos/pacientes/ObjetivosPaciente.tsx`
- `frontend/src/modulos/pacientes/Pacientes.tsx`
- `frontend/src/modulos/pacientes/ProfesionalesIntervinientes.tsx`
- `frontend/src/modulos/pacientes/SesionesPaciente.tsx`
- `frontend/src/servicios/api-seguimiento.ts`
- Nuevo: `frontend/src/modulos/pacientes/Redisenio.css`

No se modificó ningún archivo de `backend/`, ni los contratos de API existentes.

## Cómo aplicar el archivo .patch (desde la raíz del repositorio local)

Antes de empezar, guardá cualquier cambio que tengas sin commitear. Este parche fue generado contra el contenido exacto del ZIP de referencia y podría no aplicarse si el repositorio actual tiene cambios en esos archivos.

```bash
git status -sb
git switch -c ux/redisenio-integral
git apply --check /RUTA/AL/ARCHIVO/redisenio_ux_integral.patch
git apply /RUTA/AL/ARCHIVO/redisenio_ux_integral.patch
```

El archivo ZIP alternativo contiene un árbol completo del proyecto actualizado, útil para comparar sin aplicar directamente el `.patch`. **No reemplaces con él el repositorio local sin revisar los cambios de tus compañeras.**

## Compilar y probar en tu Linux Mint

Desde la raíz del proyecto, con Node y npm configurados:

```bash
cd frontend
npm ci
npm run build
npm run lint
cd ..
npm run dev
```

El último comando se ejecuta **desde la raíz**, como en el proyecto original. La base PostgreSQL y el archivo `.env` deben estar configurados como antes.

## Pruebas manuales prioritarias

1. Iniciar sesión y abrir un paciente activo.
2. Verificar nombre, edad, estado, contexto escolar y motivo de consulta.
3. Entrar en Historia y contexto; consultar y editar los cuatro tipos de registro. Comprobar persistencia al actualizar.
4. Crear una sesión, grabar/transcribir si corresponde, guardar y verificar que aparezca en Inicio y Cronología.
5. Abrir una sesión, crear/editar una observación y vincularla a un objetivo.
6. Desde Objetivos → Evidencias, abrir la sesión de origen y regresar al objetivo.
7. Seleccionar un mes, desplegar observaciones y cambiar de período. Probar también en móvil.
8. Filtrar objetivos e informes. Crear un informe con IA, revisar/editar/guardar y volver a abrirlo.
9. Abrir un formulario, escribir un cambio y navegar fuera: confirmar que advierte antes de descartar.
10. Comprobar teclado (tabulador, flechas de las pestañas, Escape en cronología), zoom 200 %, escritorio y móvil.

## Validación realizada en este entorno

- Revisión sintáctica automatizada de todos los TS/TSX: **sin errores de parseo**.
- Comprobación de tipos con *declaraciones de compatibilidad* para dependencias faltantes: **sin diagnósticos**. **No equivale** a `npm run build`.
- Revisión de que no se editaron modelos/endpoints del backend.
- La ejecución de `npm ci` no se pudo completar: el entorno no dispuso de todos los paquetes de npm (entre ellos `zwitch@2.0.4`). Por ese motivo, **no se ejecutaron `npm run build`, `npm run lint` ni una prueba integral en navegador contra PostgreSQL**. Es necesario hacer las pruebas anteriores antes de integrar a `main`.

No se hicieron commits ni merges de tu repositorio.
