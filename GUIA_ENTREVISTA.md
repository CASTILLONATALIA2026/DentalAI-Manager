# Guía breve para defender DentalAI Manager

## Explicación de 30 segundos

“DentalAI Manager es una aplicación de escritorio desarrollada en Python para gestionar pacientes de una clínica dental. Utiliza SQLite para guardar la información, genera informes PDF y Excel e incorpora un copiloto clínico orientativo basado en reglas. Cada análisis queda registrado y puede ser validado o rechazado por un profesional, por lo que existe trazabilidad y supervisión humana.”

## Explicación de 2 minutos

“El proyecto nace de mi experiencia como higienista bucodental. Quería crear una aplicación que resolviera tareas reales de una clínica y que, al mismo tiempo, me permitiera practicar programación, bases de datos e inteligencia artificial.

La interfaz está desarrollada con Tkinter. Los pacientes se guardan en SQLite y se pueden añadir, modificar, eliminar y buscar. También se pueden importar desde JSON, exportar a Excel y generar informes PDF.

La parte más diferenciadora es DentalAI Copilot. El usuario introduce síntomas, duración, dolor, antecedentes, fiebre e inflamación. Una lógica de reglas devuelve una valoración orientativa, prioridad, pruebas sugeridas y señales de alarma. No se presenta como diagnóstico. El análisis se guarda en la base de datos y después un profesional puede marcarlo como pendiente, validado o rechazado.

Separé el proyecto en módulos: interfaz, base de datos, lógica del Copilot y generación de PDF. Utilicé herramientas de IA como apoyo para depuración y revisión, pero yo definí el problema, adapté la lógica al ámbito dental, probé el recorrido completo y fui tomando las decisiones funcionales.”

## Qué hace cada archivo

- `app.py`: crea las ventanas y conecta botones con las funciones.
- `database.py`: contiene las consultas SQL y centraliza el acceso a SQLite.
- `copilot_logic.py`: analiza los datos mediante reglas y devuelve un resultado estructurado.
- `pdf_utils.py`: crea informes clínicos y análisis en PDF.

## Preguntas técnicas probables

### ¿Por qué SQLite?

Porque es una base de datos ligera, local y no necesita servidor. Para un prototipo de escritorio es suficiente y permite conservar los datos entre ejecuciones.

### ¿Qué es CRUD?

Crear, leer, actualizar y eliminar datos. En el proyecto se aplica a los pacientes y parcialmente a los análisis.

### ¿Es realmente inteligencia artificial?

Es un sistema orientativo basado en reglas, no un modelo generativo. Se diseñó así para que el razonamiento sea transparente, trazable y fácil de validar. Como mejora futura podría conectarse a un modelo de lenguaje con respuestas estructuradas y fuentes clínicas.

### ¿Por qué existe el estado Pendiente, Validado o Rechazado?

Para aplicar supervisión humana. El sistema propone una orientación, pero un profesional conserva la decisión final.

### ¿Cómo evitas errores en SQL?

Uso consultas parametrizadas con `?`, separando la sentencia de los valores. Esto reduce errores y evita concatenar directamente datos introducidos por el usuario.

### ¿Qué mejorarías para producción?

Autenticación, roles, cifrado, cumplimiento de protección de datos, auditoría, pruebas automatizadas, copias de seguridad y una arquitectura cliente-servidor.

### ¿Usaste IA para programarlo?

“Sí, utilicé IA como herramienta de apoyo para planificación, depuración y revisión. Yo definí el proyecto, probé cada función, adapté el código y entiendo el flujo principal. No presento como mío algo que no pueda explicar.”

## Demostración recomendada

1. Mostrar la pantalla principal.
2. Añadir un paciente ficticio.
3. Seleccionarlo y abrir el Copilot.
4. Analizar un caso sencillo.
5. Guardar el análisis.
6. Abrir el historial.
7. Validar el análisis.
8. Exportarlo a PDF.

Duración ideal: entre 2 y 3 minutos.

## Limitaciones que debes reconocer

- No utiliza datos reales.
- No diagnostica.
- El motor actual se basa en reglas.
- La interfaz es de escritorio y puede mejorar visualmente.
- No incluye usuarios ni permisos.
- No está preparada para un entorno sanitario real.

Reconocer limitaciones demuestra criterio técnico, no debilidad.
