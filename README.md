# 📚 StudyPlan AI

** Agente inteligente para la planificacion académica**

Trabajo Integrador - Modelos de Lenguaje
Ingeniería en Sistemas de Información - UTN FRM
Ciclo Electivo 2026

## 1. Descripción del proyecto

StudyPlan AI es una aplicación desarrollada en Python que utiliza inteligencia artificial para generar cronogramas de estudio personalizados.

El agente organiza la preparación de exámenes teniendo en cuenta:

- El programa académico de una materia en PDF.
- La fecha de inicio y la fecha del examen.
- Los días y horas disponibles del estudiante.
- La dificultad de las unidades académicas.
- La metodología de estudio seleccionada.

El resultado final es un cronograma descargable en formato CSV y Excel.

El sistema también permite modificar planificaciones anteriores mediante lenguaje natural, conservando el contexto de la conversacion.

## 2. Caso de uso

### Dominio

Planificación y organización del estudio universitario.

### Usuario objetivo

Estudiantes universitarios que necesitan organizar la preparación de exámenes según sus horarios disponibles y los contenidos académicos de una materia.

### Problema que resuelve

Organizar la preparación de un examen puede resultar complejo cuando existen numerosas unidades académicas, distintos niveles de dificultad y tiempo limitado.

StudyPlan AI automatiza esta organización mediante un agente que coordina herramientas especializadas y genera una planificación estructurada.

### Ejemplo de tarea

Un estudiante carga el programa académico de Fisica 1 y solicita:

> Generá un cronograma desde el 27/11/2026 hasta el examen del 12/12/2026. Tengo 3 horas diarias de lunes a viernes, 5 horas los sábados y no estudio los domingos. Aplicá repetición espaciada y dificultad 3 para todas las unidades.

El agente debe:

1. Recuperar el programa académico.
2. Identificar las unidades.
3. Consultar las reglas de la metodología mediante RAG.
4. Calcular los días y horas disponibles.
5. Generar el cronograma mediante algoritmos Python.
6. Exportar el resultado a CSV y Excel.
7. Informar los resultados al estudiante.

Esta tarea requiere varios pasos y herramientas, por lo que no puede resolverse mediante una única respuesta del modelo.

## 3. Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| Python | Desarrollo de la aplicación |
| LangChain | Agente y herramientas |
| LangGraph | Gestión del estado y memoria |
| Google Gemini | Modelo de lenguaje |
| Streamlit | Interfaz web |
| SQLite | Persistencia |
| ChromaDB | Base de datos vectorial |
| Hugging Face | Embeddings |
| PyPDF | Lectura de documentos PDF |
| OpenPyXL | Exportación a Excel |
| Pytest | Pruebas |

## 4. Arquitectura del sistema

StudyPlan AI utiliza un agente construido mediante `create_agent` de LangChain.

El agente interpreta las solicitudes del estudiante y coordina herramientas implementadas en Python.

### Flujo de ejecución

```text
                 ESTUDIANTE
                     |
                     v
              STREAMLIT
                 app.py
                     |
                     v
            AGENTE LANGCHAIN
               create_agent
                     |
                     v
               GOOGLE GEMINI
                     |
           +---------+---------+
           |                   |
           v                   v
    INGESTAR PROGRAMA    CONSULTAR CONOCIMIENTO
           |                   |
           v                   v
    Programa PDF          RAG / ChromaDB
           |                   |
           +---------+---------+
                     |
                     v
          CALCULAR DISPONIBILIDAD
                     |
                     v
              REGISTRO SQLITE
                     |
                     v
             disponibilidad_id
                     |
                     v
           GENERAR PLAN DE ESTUDIO
                     |
                     v
                planning.py
                     |
              +------+------+
              |             |
              v             v
             CSV           Excel
              |             |
              +------+------+
                     |
                     v
              RESULTADO FINAL
```

Los cálculos académicos se realizan mediante funciones Python, mientras que Gemini interpreta instrucciones y decide cuándo utilizar las herramientas.

## 5. Herramientas del agente

El sistema implementa 4 herramientas principales.

### 5.1 ingestar_programa

**Objetivo:** recupera el contenido del programa académico proporcionado por el estudiante.

**Entrada:** identificador del documento.

**Salida:** páginas y contenidos del PDF.

**Justificación:** permite trabajar con las unidades reales de lamateria en lugar de depender de contenidos generados por el modelo.

### 5.2 consultar_conocimiento

**Objetivo:** recuperar las reglas metodológicas almacenadas en la base vectorial.

**Entradas:**
- Consulta de búsqueda.
- Documento de origen opcional.

**Salida:** fragmentos relevantes con información de fuente y página.

**Justificación:** aporta conocimiento específico mediante RAG y permite identificar los documentos utilizados.

### 5.3 calcular_disponibilidad

**Objetivo:** determinar los días y horas disponibles para estudiar antes del examen.

**Entradas:**
- Fecha de inicio.
- Fecha del examen.
- Horas disponibles de lunes a domingo.

**Salida:**
- Días disponibles.
- Horas totales.
- Identificador de disponibilidad.

**Justificación:** realiza cálculos determinísticos y evita depender de operaciones aritméticas generadas por el modelo.

### 5.4 generar_plan_estudio

**Objetivo:** construir y exportar el cronograma académico.

**Entradas:**
- Identificador de disponibilidad.
- Lista de unidades académicas.
- Dificultad de cada unidad.
- Metodología.
- Nombre de la materia.

**Salida:**
- Cronograma.
- Estadísticas de planificación.
- Archivo CSV.
- Archivo Excel.

**Justificación:** produce el resultado tangible de la tarea.

### Seguridad entre herramientas

La disponibilidad se almacena en SQLite mediante un identificador asociado a la conversación.

La herramienta `generar_plan_estudio` recupera la disponibilidad registrada utilizando ese identificador.

Esto evita que el modelo modifique libremente los días y horas entre el cálculo de disponibilidad y la generación del cronograma.

Las herramientas incluyen validaciones y manejo de errores.

## 6. Metodologías disponibles

### Planificación general

Distribuye las horas disponiblles entre las unidades académicas según dificultad.

Reserva aproximadamente el 80 % del tiempo para estudio inicial y el 20% para repaso general.

### Pomodoro

Apica:

- 25 minutos de estudio.
- 5 minutos de descanso corto.
- 20 minutos de descanso largo después de cuatro ciclos completos.

Los descansos forman parte del tiempo disponible.

### Repetición espaciada

Programa repasos después del estudio inicial utilizando intervalos de:

- 1 día.
- 3 días.
- 7 días.
- 14 días.

Los repasos se ajustan a los días disponibles y deben realizarse antes del examen.

Cuando no es posible programarlos, el sistema informa los repasos pendientes.

## 7. Conocimiento propio mediante RAG

StudyPlan AI implementa Retrieval-Augmented Generation (RAG) para proporcionar al agente conocimiento sobre metodologías de estudio.

### Corpus documental

Se utilizan tres documentos:

| Documento | Contenido |
|---|---|
| pomodoro.pdf | Técnica Pomodoro |
| repeticion_espaciada.pdf | Reglas de repetición espaciada |
| priorizacion_repaso.pdf | Priorización y distribución de horas |

Los archivos están ubicados en:

```text
conocimiento/metodologias/
```

### Proceso de recuperación

1. Lectura de los PDF.
2. División del contenido en fragmentos (chunking).
3. Generación de embeddings.
4. Almacenamiento en ChromaBD.
5. Búsqueda semántica mediante `consultar_conocimiento`.
6. Recuperación de fragmentos con metadatos de fuente y página.

Se utiliza el modelo de embeddings:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

### Justificación del RAG

El RAG permite consultar documentación metodológica específica sin depender exclusivamente del conocimiento general del modelo.

El agente recupera las reglas cuando las necesita durante la generación del cronograma.

Los cálculos permaneecn implementados en Python.

## 8. Modelo de lenguaje

El sistema utiliza Google Gemini a través de `langchain-google-genai`.

### Justificación

Gemini permite:

- Interpretar solicitudes en lenguaje natural.
- Realizar llamadas a herramientas (tool calling).
- Utiliza el contexto de la conversación.
- Generar respuestas estructuradas para el estudiante.

El agente se construye con `create_agent` de LangChain, sin utilizar Deep Agents.

### Limitaciones del proveedor

La API puede presentar límites de solicitudes, latencia o errores temporales.

El sistema requiere una clave API válida y conexión a Internet.

## 9. Memoria de corto plazo

La memoria conversacional se implementa mediante un checkpointer de LangGrapgh con persistencia en SQLite.

Cada conversación tiene un identificador único (`thread_id`).

Esto permite:

- Mantener el historial de mensajes.
- Recuperar conversaciones anteriores.
- Conservar información entre turnos.
- Continuar después de reiniciar Streamlit.
- Replanificar sin repetir todos los datos.

### Ejemplo

**Primer turno:**

> Generá un cronograma para Física 1 con repetición espaciada y 5 horas disponibles los sábados.

**Segundo turno:**

> Conservá todo lo anterior, pero cambiá los sábados a 2 horas.

El agente recupera la información del turno anterior y genera una nueva planificación.

## 10. Interfaz y visibilidad del flujo

La interfaz está desarrollada con Streamlit.

Permite:

- Conversar con el agente.
- Cargar programas PDF.
- Seleccionar metodologías.
- Visualizar respuestas en Markdown.
- Consultar las llamadas a herramientas.
- Inspeccionar argumentos y resultados.
- Descargar cronogramas.
- Crear y recuperar conversaciones.

La ejecución del agente utiliza streaming de actualizaciones.

### Visibilidad de herramientas

Se muestra información sobre:

- Nombre de la herramienta invocada.
- Argumentos utilizados.
- Resultado obtenido.

### Razonamiento del modelo

La implementación actual con Gemini no expone bloques de razonamiento interno para presentarlos en la interfaz.

Por ese motivo, se muestra el flujo observable de herramientas, sus argumentos y resultados.

No se presentan razonamientos internos que el proveedor no haya proporcionado.

## 11. Middleware

No se utiliza middleware adicional de LangChain para implementar las reglas principales.

Las validaciones, el manejo de disponibilidad y la planificación se implementan mediante código Python propio.

Esta decicion reduce la complejidad y permite controlar directamente las restricciones del dominio.

## 12. Estructura del proyecto

```text
studyplan-ai/
|
|-- app.py
|-- agent.py
|-- tools.py
|-- planning.py
|-- rag.py
|-- programas.py
|-- persistencia.py
|-- disponibilidad_segura.py
|-- ingestar_metodologias.py
|
|-- conocimiento/
|   |-- metodologias/
|       |-- pomodoro.pdf
|       |-- repeticion_espaciada.pdf
|       |-- priorizacion_repaso.pdf
|
|-- tests/
|   |-- probar_disponibilidad_segura.py
|   |-- probar_integracion_disponibilidad.py
|
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
```

## 13. Instalación y configuración

### Requisitos previos

- Python instalado.
- pip disponible.
- Conexión a Internet.
- Clave API de Google Gemini.

### Paso 1. Clonar el repositorio

```bash
git clone https://github.com/FerMartinez444/studyplan-ai.git
cd studyplan-ai
```

### Paso 2. Crear el entorno virtual

En Windows, utilizando PowerShell:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Paso 3. Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### Paso 4. Configurar las credenciales

Crear un archivo `.env` en la raíz del proyecto, tomando como referencia `.env.example`.

Contenido:

```env
GOOGLE_API_KEY=tu_clave_api
```

La clave puede obtenerse desde Google Ai Studio.

### Paso 5. Preparar la base de conocimiento

Verificar que estén presentes los tres documentos metodológicos en:

```text
conocimiento/metodologias/
```

Ejecutar:
```powershell
python ingestar_metodologias.py
```

Este script procesa los documentos y construye la base vectorial utilizada por el sistema.

La carpeta `chroma_bd/` se genera localmente y está excluida del repositorio mediante `.gitignore`.

### Paso 6. Ejecutar Streamlit

```powershell
streamlit run app.py
```

Abrir en el navegador:

```text
http://localhost:8501
```

## 14. Uso de la aplicación

1. Iniciar Streamlit.
2. Crear una conversación.
3. Cargar el programa académico en PDF.
4. Seleccionar la metodología.
5. Indicar fechas y horas disponibles.
6. Asignar dificultades entre 1 y 5.
7. Solicitar el cronograma.
8. Revisar las herramientas ejecutadas.
9. Descargar los archivos generados.

### Ejemplo de solicitud

> > Generá un cronograma para Física I desde el 27/11/2026 hasta el examen del 12/12/2026. Tengo 3 horas diarias de lunes a viernes, 5 horas los sábados y 0 horas los domingos. Aplicá repetición espaciada y dificultad 3 para todas las unidades.

### Replanificación

El estudiante puede modificar la planificación sin repetir todos los datos.

Ejemplo:

> Conservá el cronograma anterior, pero cambiá la disponibilidad de los sábados a 2 horas.

## 15. Exportación de resultados

Los cronogramas se generan automáticamente en:

- CSV: para trabajar con hojas de cálculo y procesadores de datos.
- Excel (.xslx): con una hoja de resumen y una hoja de cronograma.

Los archivos se almacenan en carpetas separadas por conversación dentro de `outputs/`.

Los resultados generados no se incluyen en Github.

## 16. Pruebas realizadas

Se realizaron pruebas funcionales de:

- Generación con planificación general.
- Generación mediante Pomodoro.
- Generación mediante repetición espaciada.
- Consulta del corpus mediante RAG.
- Exportación a CSV y Excel.
- Cálculo y almacenamiento seguro de disponibilidad.
- Replanificación utilizando memoria.
- Recuperación de conversaciones después de reiniciar Streamlit.
- Rechazo de solicitudes con fechas incorrectas.
- Rechazo de disponibilidad nula.
- Rechazo de dificultades fuera del rango permitido.
- Separación de archivos entre conversaciones.

### Ejecución de pruebas

Desde la raíz del proyecto:

```powershell
python -m tests.probar_disponibilidad_segura
```

```powershell
python -m tests.probar_integracion_disponibilidad
```

## 17. Validaciones

El sistema contempla situaciones como:

- Fechas de planificación inválidas.
- Falta de días disponibles.
- Dificultades fuera del rango de 1 a 5.
- Identificadores de disponibilidad incorrectos.
- Datos induficientes para generar un cronograma.
- Intentos de reutilizar disponibilidad de otra conversación.
- Repasos que no pueden completarse antes del examen.

## 18. Limitaciones conocidas

- La calidad del cronograma depende de los datos ingresados.
- El sistema no evalúa automáticamente los conocimientos del estudiante.
- Las dificultades son estimaciones proporcionadas por el usuario.
- La distribución de horas no garantiza el aprendizaje completo de los contenidos.
- Algunos repasos pueden quedar pendientes.
- Se requiere una API Key válida de Gemini.
- El modelo de embeddings requiere recursos de memoria.
- La aplicación no realiza seguimiento automático del progreso del estudiante.
- La disponibilidad del servicio depende de los limites y condiciones de la API.

## 19. Posibles mejoras

Como trabajo futuro se propone.

- Incorporar seguimiento de actividades completadas.
- Permitir replanificación según el progreso real.
- Incorporar estadísticas visuales del estudio.
- Mejorar el manejo de límites de solicitudes de la API.
- Optimizar la carga del modelo de embeddings.
- Ampliar las pruebas automatizadas.
- Agregar notificaciones de sesiones y repasos.

## 20. Conclusión

StudyPlan AI integra un agente implementado con LangChain, herramientas propias, RAG, memoria persistente y una interfaz web desarrollada con Streamlit.

El sistema resuelve una tarea académica de múltiples pasos, coordina herramientas especializadas y produce un resultado tangible mediante archivos CSV y Excel.

El proyecto permite aplicar conceptos de agentes inteligentes, tool calling, recuperación de conocimiento, persistencia y automatización de procesos.