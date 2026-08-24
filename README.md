# Trabajo Final: Propuesta de Proyecto

## Integrantes

* **Volpe, María Victoria**
* **Rubin, Alexia**

**Tutor:** a definir
**Año:** 2026

---

## Nombre provisorio

**[Nombre de la aplicación a definir]**

---

## Propuesta

El proyecto consiste en desarrollar una aplicación web orientada a generar un **sistema integral de registro y seguimiento psicopedagógico**, destinado a acompañar los procesos de evaluación, diagnóstico, tratamiento, intervención y seguimiento de niños y adolescentes por parte de profesionales como psicopedagogos e integradores.

La idea surge de una necesidad frecuente en este ámbito: gran parte de la información de cada alumno o paciente suele quedar distribuida entre anotaciones, documentos, audios, evaluaciones e informes realizados en distintos momentos y almacenados en diferentes lugares.

La aplicación busca **centralizar y organizar esta información en un único espacio**, facilitando su consulta y permitiendo realizar un seguimiento más ordenado de la evolución a lo largo del tiempo.

El sistema permitirá crear un perfil individual para cada alumno o paciente e incorporar información relevante de su historia inicial, entrevistas, evaluaciones realizadas, técnicas e instrumentos utilizados, objetivos de trabajo, sesiones, intervenciones, observaciones, evolución y registro de actividades.

A partir de esta información, el profesional podrá consultar una cronología del proceso, recuperar antecedentes y utilizar los registros para elaborar informes y realizar el seguimiento de los objetivos planteados.

Una función importante será el **registro mediante audio**. El profesional podrá grabar una observación breve luego de una sesión y el sistema la transcribirá automáticamente, permitiendo revisar, corregir y editar el texto antes de incorporarlo al registro del paciente.

De esta manera, se busca agilizar una tarea que habitualmente requiere tiempo adicional luego de cada encuentro.

También se plantea incorporar asistencia mediante **inteligencia artificial** para organizar información y generar borradores de síntesis, evoluciones o informes a partir de los registros previamente almacenados.

La información generada será siempre editable y funcionará como una herramienta de apoyo al profesional.

> **La inteligencia artificial no realizará diagnósticos ni tomará decisiones clínicas o pedagógicas de manera autónoma. La revisión y decisión final permanecerán siempre a cargo del profesional.**

---

## Alcance inicial: Producto mínimo

La primera versión deberá permitir:

* Registro e inicio de sesión del profesional.
* Alta, edición y consulta de alumnos/pacientes.
* Definición de objetivos de trabajo.
* Registro de sesiones y observaciones.
* Posibilidad de registrar información mediante texto o audio.
* Transcripción del audio a texto editable.
* Cronología de registros por alumno/paciente.
* Registro de conductas observables junto con su contexto.
* Visualización básica de evolución.
* Generación de un borrador de informe utilizando los registros almacenados.

Se priorizará que estas funciones estén completas y sean estables antes de incorporar funcionalidades adicionales.

---

## Posibles ampliaciones

Si el tiempo de desarrollo lo permite, se podrán incorporar funciones como:

* Adaptación de materiales.
* Lectura fácil.
* Alertas ante patrones repetidos.
* Exportación de informes.
* Recursos sugeridos.
* Herramientas de supervisión entre profesionales.

Estas funciones **no forman parte del núcleo obligatorio del proyecto**.

---

# Tecnologías propuestas

## Frontend

### React

Permite construir una interfaz dinámica a partir de componentes reutilizables y facilita la organización de una aplicación con distintas secciones y formularios.

### TypeScript

Agrega tipado a JavaScript, ayudando a detectar errores durante el desarrollo y a mantener el código más claro.

### Vite

Ofrece un entorno de desarrollo rápido y una configuración simple para proyectos con React.

---

## Backend

### Python

Se eligió por su sintaxis clara y por su amplia compatibilidad con herramientas de procesamiento de datos e inteligencia artificial.

### FastAPI

Permite desarrollar una API REST de forma sencilla, con buen rendimiento y validación automática de datos.

### Pydantic / SQLModel

Facilitan la validación de la información recibida por la API y el trabajo con los datos almacenados en la base de datos.

---

## Base de datos

### PostgreSQL

Es una base de datos relacional robusta y adecuada para información estructurada y relacionada, como profesionales, pacientes, sesiones, objetivos e informes.

---

## Servicios externos

### API de transcripción de audio

Permitirá convertir registros de voz de las sesiones en texto para facilitar su posterior consulta y procesamiento.

### API de IA

Se utilizará de manera asistida para generar síntesis, borradores de informes y adaptaciones de material a partir de la información registrada.

---

## Control de versiones

### Git

Permitirá registrar y controlar los cambios realizados durante el desarrollo.

### GitHub

Se utilizará para alojar el repositorio compartido y centralizar el código del proyecto.

---

## Plataforma

Se desarrollará una **aplicación web responsive**, para que pueda utilizarse tanto desde computadoras como desde dispositivos móviles.

El frontend, el backend y la base de datos se desplegarán utilizando servicios cloud compatibles con las tecnologías elegidas y adecuados para el alcance académico del proyecto.

La arquitectura será simple:

```text
Frontend: React + TypeScript + Vite
        ↓
API REST: FastAPI + Python
        ↓
Base de datos: PostgreSQL
```

Se evitará incorporar tecnologías o capas adicionales que no aporten una necesidad concreta al proyecto.

---

# Plan de trabajo

El desarrollo se realizará de forma incremental, completando pequeños flujos funcionales antes de avanzar al siguiente módulo.

## Etapa 1: Definición y estructura inicial

* Terminar de definir los requisitos principales.
* Establecer qué información necesita cada registro.
* Definir el modelo inicial de datos.
* Crear el repositorio de GitHub.
* Crear la estructura base de frontend y backend.
* Preparar las primeras pantallas y modelos.

## Etapa 2: Núcleo del sistema

* Usuarios y acceso.
* Gestión de alumnos/pacientes.
* Objetivos.
* Sesiones y observaciones.
* Cronología.

Al finalizar esta etapa deberá existir un flujo completo desde la creación de un paciente hasta el registro y consulta de una sesión.

## Etapa 3: Audio y evolución

* Grabación de audio desde la aplicación.
* Envío al backend.
* Transcripción.
* Edición y guardado del registro.
* Visualización de evolución y datos básicos.

## Etapa 4: Informes e IA

* Recopilación de registros por período.
* Generación de borradores de informes.
* Asistencia mediante IA.
* Revisión y edición por parte del profesional.

## Etapa 5: Integración y pruebas

* Integración general.
* Corrección de errores.
* Pruebas de los principales flujos.
* Mejoras de usabilidad.
* Deploy.

## Etapa 6: Margen y entrega

Las últimas semanas se reservarán principalmente para solucionar imprevistos, estabilizar la aplicación, completar documentación y preparar la presentación ante el comité.

---

# Organización del equipo

Las funcionalidades se dividirán en módulos para que ambas integrantes puedan avanzar en paralelo y participar tanto del desarrollo como de las decisiones del proyecto.

Algunos puntos, como el modelo de datos inicial, la integración de los módulos y las decisiones que afecten a toda la aplicación, se resolverán en conjunto.

Se realizarán reuniones breves de seguimiento para integrar lo desarrollado, resolver bloqueos y decidir las tareas siguientes.

---

# Repositorio

Todo el proyecto se alojará en un único repositorio de GitHub.

**Repositorio:** [enlace a completar]
