# Frontend de TRAMA

Interfaz de seguimiento psicopedagógico desarrollada con React, TypeScript y Vite.

- `src/modulos/autenticacion`: acceso profesional.
- `src/modulos/pacientes`: ficha, historia, seguimiento, audio, cronología e informes.
- `src/modulos/pacientes/useFichaPaciente.ts`: consultas y operaciones de la ficha.
- `src/hooks`: estado compartido de edición y protección de cambios pendientes.
- `src/servicios`: comunicación HTTP con la API.
- `src/components`: componentes comunes de interfaz.
- `tests`: pruebas unitarias de reglas de navegación, fechas y contratos HTTP.

Desde la raíz del repositorio:

```bash
npm ci --prefix frontend
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run build
npm run dev
```

La API se consume mediante rutas relativas `/api`. El proxy de Vite se utiliza en desarrollo; la publicación utiliza el mismo origen para frontend y backend.

Ver [documentación principal](../README.md) y [validación funcional](../docs/VALIDACION.md).
