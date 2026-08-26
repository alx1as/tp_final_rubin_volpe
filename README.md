# TRABAJO FINAL

## Propuesta de Proyecto

**Integrantes**

Volpe, María Victoria  
Rubin, Alexia

**Tutor**

Sergio Andrés Antonini

**Año**

2026

**Repositorio**

https://github.com/alx1as/tp_final_rubin_volpe

## 1. Nombre provisorio

Nombre de la aplicación a definir

## 2. Problemática y contexto

El proyecto parte de una dificultad frecuente en el seguimiento psicopedagógico de niños y adolescentes: la información de cada paciente o alumno suele quedar distribuida entre anotaciones, documentos, audios, evaluaciones e informes elaborados en distintos momentos y guardados en diferentes lugares. Esto obliga al profesional a reconstruir el proceso cada vez que necesita consultar antecedentes, revisar objetivos o preparar una evolución o un informe.

La definición de esta problemática parte también de la experiencia directa en el ámbito profesional: María Victoria Volpe es psicopedagoga clínica, por lo que su trayectoria permitirá aportar criterios propios del trabajo cotidiano para identificar necesidades, formas de registro y procesos de seguimiento. Además, se realizaron conversaciones informales con otros profesionales (entre ellos integradores y psicólogos) que permitieron contrastar estas necesidades y conocer distintas formas actuales de organizar la información.

El flujo de trabajo que se busca mejorar comienza en el registro de lo ocurrido durante o después de una sesión. Esa información puede quedar en una nota breve, un documento o un audio y luego debe recuperarse y relacionarse con registros anteriores. Cuando el seguimiento se extiende en el tiempo, la dispersión de información aumenta el esfuerzo necesario para encontrar antecedentes, sostener una continuidad y elaborar informes a partir de varios encuentros.

El problema no es solamente que parte del registro se haga de forma manual, sino que la información relevante queda fragmentada y requiere trabajo adicional para ordenarla, relacionarla y volver a utilizarla.

La propuesta busca reducir ese esfuerzo mediante una herramienta que concentre el seguimiento en un único espacio y aproveche los datos registrados.

## 3. Usuarios e interesados

La aplicación estará orientada a profesionales que realizan seguimiento psicopedagógico de niños y adolescentes, principalmente psicopedagogos e integradores.

El sistema podrá ser utilizado por varios profesionales, cada uno con una cuenta individual y acceso a sus propios pacientes y registros. Para el MVP habrá un único rol de usuario: profesional. No se plantea en esta etapa una gestión institucional con distintos niveles de permisos.

El profesional es el usuario directo y necesita poder registrar información con rapidez, recuperar antecedentes y preparar el seguimiento. Los niños y adolescentes acompañados son interesados directos en el proceso, pero no utilizarán la aplicación ni tendrán una cuenta. Las familias, docentes u otros profesionales pueden participar del proceso o recibir información elaborada por el profesional, pero no tendrán acceso directo al sistema (no en esta primera versión).

## 4. Propuesta de solución y valor agregado

Se propone desarrollar una aplicación web que centralice el registro y seguimiento de cada paciente o alumno. Desde un perfil individual, el profesional podrá consultar información general, objetivos de trabajo, sesiones, observaciones, antecedentes e informes, manteniendo una cronología del proceso.

El valor de la solución no está solamente en digitalizar registros. La aplicación busca que la información cargada una vez pueda reutilizarse después: una observación podrá quedar vinculada a una sesión y si corresponde incluso a un objetivo. Los registros podrán recuperarse por orden temporal. Una nota de voz podrá convertirse en texto editable. Y la información acumulada podrá utilizarse para generar un borrador de informe asistido por inteligencia artificial.

La inteligencia artificial funcionará como apoyo para organizar y sintetizar información previamente registrada. No realizará diagnósticos ni tomará decisiones clínicas o pedagógicas. Todo contenido generado será revisable y editable, y la decisión final permanecerá a cargo del profesional.

## 5. Objetivo general

Desarrollar una aplicación web que permita a profesionales del ámbito psicopedagógico registrar, organizar y recuperar la información del seguimiento de niños y adolescentes, reduciendo la dispersión de datos y facilitando el registro de sesiones, la consulta de antecedentes y la elaboración de informes.

## 6. Objetivos específicos

Centralizar en un perfil individual la información relevante de cada paciente o alumno y permitir el seguimiento de objetivos, sesiones y observaciones a lo largo del tiempo.

Agilizar el registro posterior a una sesión mediante notas de texto y grabaciones de audio que puedan transcribirse, revisarse y guardarse como parte del seguimiento.

Facilitar la consulta de antecedentes mediante una cronología clara de los registros realizados.

Utilizar inteligencia artificial de forma asistida para generar borradores de informes a partir de información previamente almacenada, manteniendo siempre la revisión profesional.

## 7. Alcance inicial: Producto mínimo viable

La primera versión se concentrará en un flujo completo de trabajo, desde el acceso del profesional hasta el registro de sesiones y la generación de un borrador de informe. Se priorizará que estas funciones estén integradas y sean estables antes de incorporar ampliaciones.

### 7.1 Acceso del profesional

El sistema permitirá registrar una cuenta mediante correo electrónico y contraseña, iniciar sesión y cerrar sesión. Las contraseñas se almacenarán de forma segura mediante hash. Cada profesional podrá acceder únicamente a la información asociada a su cuenta.

### 7.2 Gestión de pacientes o alumnos

El profesional podrá crear, consultar y editar perfiles individuales. Cada perfil concentrará los datos básicos y la información general necesaria para el seguimiento. Desde ese perfil se accederá a los objetivos, sesiones, observaciones, cronología e informes correspondientes. Los campos definitivos se ajustarán al modelo de datos aprobado para la segunda entrega.

### 7.3 Objetivos de trabajo

El sistema permitirá registrar y editar objetivos asociados a un paciente, consultar su estado y mantenerlos como referencia durante el seguimiento. Cuando resulte útil, una observación podrá relacionarse con un objetivo para conservar evidencia de lo trabajado y de los cambios observados.

### 7.4 Sesiones y observaciones

El profesional podrá registrar cada encuentro como una sesión asociada a un paciente, con fecha y una nota general. Dentro de una sesión podrá guardar una o varias observaciones. Las observaciones podrán combinar campos estructurados con una nota libre para registrar, según corresponda, contexto, conducta observable, intervención realizada y resultado. Esta estructura busca ordenar la información sin obligar a describir todos los casos de la misma manera.

### 7.5 Registro por audio y transcripción

El profesional podrá grabar una nota de voz desde la aplicación. El audio será enviado al backend y procesado por un servicio de transcripción. El texto obtenido se mostrará antes de guardarse para que pueda ser corregido, completado o descartado. Una vez confirmado, el texto se incorporará al registro correspondiente. Para el alcance académico del proyecto no se prevé almacenar el archivo de audio de forma permanente.

### 7.6 Cronología

Cada paciente tendrá una cronología que permita consultar los registros del seguimiento en orden temporal. La primera versión priorizará una visualización clara de sesiones y observaciones, con acceso a su contenido. Los filtros o búsquedas avanzadas no forman parte del núcleo obligatorio.

### 7.7 Informes asistidos por inteligencia artificial

El profesional podrá seleccionar un paciente y un período de seguimiento para generar un borrador de informe a partir de los registros almacenados en ese intervalo. El sistema recopilará la información disponible y utilizará un servicio de inteligencia artificial para producir una primera versión. El borrador será editable y podrá guardarse una vez revisado por el profesional. La herramienta se limitará a organizar y sintetizar información existente, no le corresponderá realizar diagnósticos ni tomar decisiones autónomas.

## 8. Fuera de alcance y posibles ampliaciones

La primera versión no incluirá:

- acceso directo para pacientes, familias o docentes
- múltiples roles profesionales
- administración de instituciones o equipos
- almacenamiento permanente de audios
- diagnósticos automáticos
- toma de decisiones clínicas o pedagógicas mediante inteligencia artificial ni sistemas predictivos.

Si el núcleo del sistema queda completo y estable, podrán evaluarse como ampliaciones la adaptación de materiales, lectura fácil, exportación de informes, alertas ante patrones repetidos, visualizaciones gráficas de evolución, recursos sugeridos o herramientas de supervisión entre profesionales. Estas funciones no condicionarán la entrega del MVP.

## 9. Requisitos iniciales

### 9.1 Requisitos funcionales

RF01. El sistema deberá permitir registrar una cuenta profesional e iniciar y cerrar sesión.

RF02. El sistema deberá restringir el acceso de cada profesional a sus propios pacientes y registros.

RF03. El profesional deberá poder crear, consultar y editar pacientes o alumnos.

RF04. El profesional deberá poder registrar y modificar objetivos asociados a un paciente.

RF05. El profesional deberá poder registrar sesiones y una o varias observaciones dentro de cada sesión.

RF06. El sistema deberá permitir vincular una observación con un objetivo cuando corresponda.

RF07. El sistema deberá permitir grabar audio desde el navegador y obtener una transcripción a texto.

RF08. El profesional deberá poder revisar y editar la transcripción antes de guardarla.

RF09. El sistema deberá mostrar los registros de un paciente en una cronología.

RF10. El sistema deberá permitir seleccionar un período y generar un borrador de informe utilizando los registros almacenados.

RF11. El borrador generado mediante inteligencia artificial deberá ser editable y guardable por el profesional.

### 9.2 Requisitos no funcionales

RNF01. La aplicación deberá ser responsive y utilizable desde computadoras y dispositivos móviles.

RNF02. Las contraseñas deberán almacenarse mediante mecanismos de hash y no como texto plano.

RNF03. El backend deberá validar la información recibida antes de almacenarla.

RNF04. Los archivos de audio utilizados para transcripción no se conservarán de forma permanente en el MVP.

RNF05. Para pruebas y demostraciones se utilizarán datos ficticios o anonimizados.

RNF06. La interfaz deberá mantener una navegación simple y consistente entre pacientes, sesiones, observaciones e informes.

## 10. Criterios de éxito del MVP

El MVP se considerará completo cuando pueda demostrarse de punta a punta el flujo principal: un profesional inicia sesión, crea o consulta un paciente, registra objetivos, carga una sesión con observaciones, puede dictar una nota y corregir su transcripción, consulta el seguimiento en orden temporal y genera un borrador de informe a partir de los registros guardados. Las funciones opcionales no serán necesarias para considerar cumplido el objetivo del proyecto.

## 11. Tecnologías propuestas y justificación

### 11.1 Frontend

El frontend se desarrollará con React, TypeScript y Vite. React permite organizar la interfaz en componentes reutilizables, algo conveniente para una aplicación con formularios, vistas de detalle y secciones repetidas. TypeScript aporta tipado y ayuda a detectar errores durante el desarrollo. Vite ofrece una configuración simple y un entorno rápido. Para la navegación se utilizará React Router y, mientras no aparezca una necesidad concreta, las llamadas a la API se realizarán con fetch nativo para evitar sumar dependencias innecesarias.

### 11.2 Backend

El backend se desarrollará en Python con FastAPI. Python resulta adecuado por su ecosistema para integrar servicios de procesamiento de texto, transcripción e inteligencia artificial. FastAPI permite construir una API REST con validación de datos, documentación automática y una estructura simple para el alcance del proyecto. Pydantic y SQLModel se utilizarán para validar información y modelar la persistencia.

### 11.3 Base de datos

Se utilizará PostgreSQL porque la información principal tiene relaciones claras y relativamente estables: profesionales, pacientes, objetivos, sesiones, observaciones e informes. Un modelo relacional permite mantener esas relaciones y asegurar integridad de los datos sin incorporar una tecnología más compleja de lo necesario.

### 11.4 Servicios externos

Se integrará un servicio de transcripción de audio a texto y una API de inteligencia artificial para la generación asistida de borradores de informes. Ambos servicios serán tratados como dependencias externas: si presentan una falla, el resto del registro y consulta de información deberá seguir funcionando.

### 11.5 Control de versiones y despliegue

Git y GitHub se utilizarán para el control de versiones y el trabajo compartido. Todo el proyecto se mantendrá en un único repositorio. Se prevé desplegar el frontend, el backend y la base de datos en servicios cloud compatibles con el stack elegido.

## 12. Viabilidad

### 12.1 Viabilidad técnica

La arquitectura propuesta es: frontend en React, API REST con FastAPI y base de datos PostgreSQL. El proyecto no requiere microservicios, comunicación en tiempo real ni infraestructura compleja. Las partes con mayor curva de aprendizaje o dependencia externa, como SQLModel, la grabación desde el navegador, la transcripción y la generación asistida por IA, se probarán de forma aislada antes de integrarlas al flujo principal para evitar que bloqueen el resto de la aplicación.

### 12.2 Viabilidad operativa

La solución se plantea como una herramienta de apoyo para un flujo que ya existe: registrar sesiones, ordenar observaciones, revisar antecedentes y elaborar informes. No busca reemplazar el criterio profesional ni modificar el proceso de evaluación o intervención. La interfaz se diseñará para que el registro pueda realizarse con texto o audio y para que toda información generada automáticamente pueda revisarse antes de ser incorporada.

### 12.3 Viabilidad temporal

El alcance se limita a un único rol, una arquitectura web simple y un flujo principal definido. Las ampliaciones quedarán condicionadas a que el MVP esté integrado y estable. El desarrollo se realizará de forma incremental, con pequeñas funcionalidades completas que puedan probarse antes de avanzar al siguiente bloque.

## 13. Riesgos iniciales y mitigación

Los principales riesgos técnicos están relacionados con la integración de servicios externos de transcripción e inteligencia artificial, la coordinación entre frontend y backend y el despliegue final.

Para reducirlos, las integraciones externas se probarán de forma aislada antes de incorporarlas al flujo principal, el frontend podrá avanzar con datos mock cuando el backend todavía no esté disponible y se priorizarán contratos de datos simples y acordados entre ambas integrantes.

El principal riesgo temporal es ampliar el alcance durante el desarrollo. Para evitarlo, cualquier función nueva quedará fuera del MVP salvo que el flujo obligatorio ya esté completo y estable.

## 14. Plan de trabajo

### Etapa 1 - Semanas 1 y 2 | Definición y estructura inicial

Se cerrarán los requisitos principales y el modelo inicial de datos, se organizará el repositorio y se prepararán las estructuras base de frontend y backend. El frontend podrá avanzar con datos mock mientras se termina el modelado. Al cerrar esta etapa deberán estar acordados los nombres de los datos principales y una primera conexión entre frontend y API.

### Etapa 2 - Semanas 3 a 5 | Núcleo del seguimiento

Se desarrollarán la gestión de pacientes, objetivos, sesiones y observaciones. El objetivo es completar un flujo funcional desde la creación de un paciente hasta el registro y consulta de una sesión con sus observaciones.

### Etapa 3 - Semanas 6 y 7 | Audio y transcripción

Se incorporará la grabación desde el navegador, el envío del archivo al backend, la integración con el servicio de transcripción y la edición del texto antes de guardarlo en el seguimiento.

### Etapa 4 - Semanas 8 y 9 | Cronología e informes con IA

Se integrará la cronología del paciente y la generación de borradores de informes por período a partir de registros reales. Se probará que el contenido generado pueda revisarse, editarse y guardarse sin afectar los datos originales.

### Etapa 5 - Semanas 10 a 11 | Integración, pruebas y deploy

Se probarán los recorridos principales, se corregirán errores de navegación y formularios, se prepararán datos ficticios para la demostración y se realizará el despliegue. También se completará la documentación mínima del repositorio y la preparación para la presentación.

### Etapa 6 - Semanas 12 a 14 | Margen y entrega

El tiempo restante se reservará para resolver imprevistos, estabilizar la aplicación, completar documentación y preparar la defensa. Solo se incorporarán ampliaciones si no existen pendientes importantes del MVP.

## 15. Organización del equipo

Las funcionalidades se dividirán en módulos para que ambas integrantes puedan avanzar en paralelo.

La experiencia de María Victoria en la psicopedagogía clínica será de gran ayuda para definir la información requerida para el sistema, cómo organizarla y qué aspectos tienen sentido dentro del seguimiento psicopedagógico.

Las decisiones que afecten a toda la aplicación (como el modelo de datos, los contratos entre frontend y backend y la integración final) se resolverán en conjunto. Se utilizarán ramas cortas por funcionalidad y se mantendrá la rama principal en estado funcional.

## 16. Plataforma y arquitectura

El producto será una aplicación web responsive. La arquitectura estará compuesta por un frontend desarrollado con React y TypeScript, una API REST con FastAPI y una base de datos PostgreSQL. Se evitarán capas o tecnologías adicionales que no respondan a una necesidad concreta del proyecto. Se prevé desplegar los tres componentes mediante servicios cloud compatibles con el alcance académico.

## 17. Repositorio

Todo el proyecto se alojará en un único repositorio de GitHub, incluyendo código fuente, documentación y los archivos necesarios para la entrega.

Repositorio: https://github.com/alx1as/tp_final_rubin_volpe
