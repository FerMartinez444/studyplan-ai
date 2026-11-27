import json
import uuid
from pathlib import Path

import streamlit as st
from langchain_core.messages import(
    AIMessage,
    HumanMessage,
    ToolMessage
)

from agent import crear_agente
from programas import registrar_programa
from tools import carpeta_outputs_sesion

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def extraer_texto(mensaje):
    contenido = mensaje.content

    if isinstance(contenido, str):
        return contenido

    if isinstance(contenido, list):
        return "\n".join(
            bloque.get("text", "")
            for bloque in contenido
            if isinstance(bloque, dict)
            and bloque.get("type") == "text"
        )

    return ""

def recuperar_mensajes(agente, thread_id):
    configuracion = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    estado = agente.get_state(configuracion)

    if not estado.values:
        return []

    mensajes = []

    for mensaje in estado.values.get("messages", []):
        if isinstance(mensaje, HumanMessage):
            texto = extraer_texto(mensaje)

            if "SOLICITUD DEL ESTUDIANTE:" in texto:
                texto = texto.split(
                    "SOLICITUD DEL ESTUDIANTE:",
                    1
                )[1].split(
                    "PROGRAMA ACTIVO:",
                    1
                )[0].strip()

            mensajes.append({
                "rol": "user",
                "contenido": texto,
            })

        elif isinstance(mensaje, AIMessage):
            if not mensaje.tool_calls:
                texto = extraer_texto(mensaje)

                if texto.strip():
                    mensajes.append({
                        "rol": "assistant",
                        "contenido": texto,
                    })
    return mensajes

def recuperar_metodologia(agente, thread_id):
    configuracion = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    estado = agente.get_state(configuracion)

    opciones = (
        "Sin metodologia",
        "Pomodoro",
        "Repetición espaciada",
    )

    for mensaje in reversed(
        estado.values.get("messages", [])
    ):
        if not isinstance(mensaje, HumanMessage):
            continue

        texto = extraer_texto(mensaje)

        if "METODOLOGIA ELEGIDA:" not in texto:
            continue

        valor = texto.split(
            "METODOLOGIA ELEGIDA:", 1
        )[1].splitlines()

        for linea in valor:
            seleccion = linea.strip()

            if seleccion in opciones:
                return seleccion

    return "Sin metodologia"

# CONFIGURACION GENERAL

st.set_page_config(
    page_title="StudyPlan AI",
    page_icon="📚",
    layout="wide",
)

st.title("📚 StudyPlan AI")
st.write("Organiza tus horarios de estudio con inteligencia artificial.")


# ESTADO DE LA SESION

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "agente" not in st.session_state:
    st.session_state.agente = crear_agente(
        st.session_state.thread_id
    )

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

if "programa_id" not in st.session_state:
    st.session_state.programa_id = None

if "programa_nombre" not in st.session_state:
    st.session_state.programa_nombre = None

if "registro_ejecucion" not in st.session_state:
    st.session_state.registro_ejecucion = None

# GESTION DE CONVERSACIONES

with st.sidebar:

    st.subheader("Conversaciones")

    st.caption("Identificador de la conversacion actual:")
    st.code(st.session_state.thread_id)

    id_recuperar = st.text_input(
        "Recuperar conversacion por ID",
        placeholder="Pega aqui el identificador anterior",
    )

    if st.button("Recuperar conversacion"):

        try:
            id_validado = str(
                uuid.UUID(id_recuperar.strip())
            )

            agente_recuperado = crear_agente(id_validado)

            mensajes_recuperados = recuperar_mensajes(
                agente_recuperado,
                id_validado,
            )

            if not mensajes_recuperados:
                st.warning(
                    "No se encontro una conversacion "
                    "guardada con ese identificador."
                )

            else:
                st.session_state.thread_id = id_validado
                st.session_state.agente = agente_recuperado
                st.session_state.mensajes = mensajes_recuperados
                st.session_state.metodologia_selector = (
                    recuperar_metodologia(
                        agente_recuperado,
                        id_validado,
                    )
                )

                st.session_state.programa_id = None
                st.session_state.programa_nombre = None

                st.rerun()

        except ValueError:
            st.error(
                "El identificador ingresado no es un UUID valido."
            )

        except Exception as error:
            st.error(
                f"No se pudo recuperar la conversacion: {error}"
            )

    if st.button("Nueva conversacion"):

        nuevo_id = str(uuid.uuid4())

        st.session_state.thread_id = nuevo_id
        st.session_state.agente = crear_agente(nuevo_id)
        st.session_state.mensajes = []

        st.session_state.programa_id = None
        st.session_state.programa_nombre = None

        st.session_state.metodologia_selector = (
            "Sin metodologia"
        )

        st.rerun()



# CARGA DE DOCUMENTOS


# CARGA DEL PROGRAMA ACADEMICO

with st.sidebar:

    st.header("Configuracion del estudio")

    st.subheader("Programa de la materia")

    archivo = st.file_uploader(
        "Selecciona el programa academico en PDF",
        type=["pdf"],
    )

    if st.button("Incorporar programa"):

        if archivo is None:
            st.warning("Primero selecciona un PDF.")

        else:
            try:
                resultado = registrar_programa(
                    contenido=archivo.getvalue(),
                    nombre=archivo.name,
                    sesion_id=st.session_state.thread_id,
                )

                st.session_state.programa_id = (
                    resultado["documento_id"]
                )

                st.session_state.programa_nombre = (
                    resultado["archivo"]
                )

                st.success(
                    "Programa registrado correctamente. "
                    "El agente lo procesara cuando sea necesario."
                )

            except Exception as error:
                st.error(
                    f"Error al registrar programa: {error}"
                )

    if st.session_state.programa_nombre:
        st.info(
            "Programa activo: "
            + st.session_state.programa_nombre
        )

    st.subheader("Metodologia")

    metodologia = st.selectbox(
        "Selecciona tu metodologia",
        [
            "Sin metodologia",
            "Pomodoro",
            "Repeticion espaciada",
        ],
        key="metodologia_selector",
    )


for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

consulta = st.chat_input(
    "Escribi tu solicitud de planificacion..."
)

if consulta:

    st.session_state.mensajes.append({
        "rol": "user",
        "contenido": consulta,
    })

    with st.chat_message("user"):
        st.markdown(consulta)

    fuentes = {
        "Sin metodologia": None,
        "Pomodoro": "pomodoro.pdf",
        "Repeticion espaciada": "repeticion_espaciada.pdf",
    }

    fuente_elegida = fuentes[metodologia]

    programa_id = st.session_state.programa_id

    hoy = datetime.now(
        ZoneInfo("America/Argentina/Mendoza")
    ).date()

    maniana = hoy + timedelta(days=1)
    
    consulta_completa = f"""
    CONTEXTO TEMPORAL:
    Fecha actual: {hoy.isoformat()}
    Fecha de mañana: {maniana.isoformat()}
    Zona horaria: America/Argentina/Mendoza.

    - Interpreta "hoy" y "mañana" utilizando estas fechas.
    - No utilices fechas de años anteriores.
    -Si el usuario indica 12/12 sin año, utiliza el
    proximo 12 de diciembre que no haya pasado.
    - Antes de calcular disponibilidad, verifica que
    las fechas correspondan a la solicitud.

    SOLICITUD DEL ESTUDIANTE:
    {consulta}

    PROGRAMA ACTIVO:
    Nombre: {st.session_state.programa_nombre}
    Identificador: {programa_id or "No cargado"}

    METODOLOGIA ELEGIDA:
    {metodologia}

    DOCUMENTO METODOLOGICO:
    {fuente_elegida}

    INSTRUCCIONES:
    - Si hay un programa cargado, utiliza ingestar_programa
    para recuperar su contenido.

    - Identifica todas las unidades academicas respetando
    sus nombres y el orden original.
    
    - Respeta exclusivamente la metodologia seleccionada
    por el estudiante en Streamlit.

    - Si se selecciono Pomodoro:
    Consulta las reglas de pomodoro.pdf en el RAG.
    Utiliza "pomodoro" en generar_plan_estudio.

    - Si se selecciono Repeticion espaciada:
    Consulta las reglas de repeticion_espaciada.pdf
    en el RAG.
    Utiliza "repeticion_espaciada" en generar_plan_estudio.

    - Si se selecciono Sin metodologia:
    No apliques Pomodoro ni repeticion espaciada.
    Utiliza "ninguna" en generar_plan_estudio.

    - Para las tres opciones, consulta los criterios
    generales de priorizacion y distribucion del
    estudio desde priorizacion_repaso.pdf.

    - Calcula la disponibilidad real del estudiante
    mediante calcular_disponibilidad.

    - Genera el cronograma mediante generar_plan_estudio.

    - Respeta las fechas y los horarios indicados
    por el estudiante.

    - No inventes unidades ni reglas metodologicas.

    - Limita tu respuesta a la planificacion del estudio.
    """

    st.session_state.registro_ejecucion = []

    with st.chat_message("assistant"):

        respuesta_final = ""

        try:
            configuracion = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            with st.status(
                "Ejecutando agente...",
                expanded=True,
            ) as estado:
                

                eventos = st.session_state.agente.stream(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": consulta_completa,
                            }
                        ]
                    },
                    config=configuracion,
                    stream_mode="updates",
                )

                for evento in eventos:

                    for nodo, actualizacion in evento.items():

                        if not isinstance(actualizacion, dict):
                            continue

                        for mensaje in actualizacion.get("messages", []):

                            if isinstance(mensaje, AIMessage):

                                for llamada in mensaje.tool_calls:

                                    st.session_state.registro_ejecucion.append({
                                        "tipo": "llamada",
                                        "herramienta": llamada["name"],
                                        "contenido": llamada["args"],
                                    })

                                    st.write(
                                        "Herramienta:",
                                        llamada["name"],
                                    )

                                    st.json(llamada["args"])

                                if not mensaje.tool_calls and mensaje.content:

                                    if isinstance(mensaje.content, str):
                                        respuesta_final = mensaje.content

                                    elif isinstance(mensaje.content, list):
                                        respuesta_final = "\n".join(
                                            bloque.get("text", "")
                                            for bloque in mensaje.content
                                            if isinstance(bloque, dict)
                                            and bloque.get("type") == "text"
                                        )

                            elif isinstance(mensaje, ToolMessage):

                                st.session_state.registro_ejecucion.append({
                                    "tipo": "resultado",
                                    "herramienta": mensaje.name or "Tool",
                                    "contenido": str(mensaje.content),
                                })

                                st.write(
                                    "📄 Resultado de herramienta:",
                                    mensaje.name or "Tool",
                                )

                                st.code(
                                    str(mensaje.content)[:2500]
                                )

                estado.update(
                    label="Ejecucion finalizada",
                    state="complete",
                )

            if respuesta_final:
                st.markdown(respuesta_final)
            else:
                respuesta_final = (
                    "El agente no devolvio una respuesta final."
                )
                st.warning(respuesta_final)

        except Exception as error:
            respuesta_final = f"Error del agente: {error}"
            st.error(respuesta_final)

        st.session_state.mensajes.append({
            "rol": "assistant",
            "contenido": respuesta_final,
        })

if st.session_state.get("registro_ejecucion"):
    with st.expander(
        "Ver detalle de la ultima ejecucion",
        expanded=False,
    ):

        for evento in st.session_state.registro_ejecucion:

            st.write(
                evento["tipo"].upper(),
                evento["herramienta"],
            )

            if isinstance(evento["contenido"], dict):
                st.json(evento["contenido"])
            else:
                st.code(evento["contenido"])

st.divider()
st.subheader("Cronogramas exportados")

carpeta_outputs = carpeta_outputs_sesion(
    st.session_state.thread_id
)

if carpeta_outputs.exists():

    archivos = sorted(
        [
            archivo
            for archivo in carpeta_outputs.iterdir()
            if archivo.is_file()
            and archivo.suffix.lower() in (".csv", ".xlsx")
        ],
        key=lambda archivo: archivo.stat().st_mtime,
        reverse=True,
    )[:10]

    if archivos:

        st.write(
            f"Archivos disponibles: {len(archivos)}"
        )

        for archivo in archivos:

            if archivo.suffix.lower() == ".csv":
                tipo = "text/csv"
            else:
                tipo = (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                )

            st.download_button(
                label=f"Descargar {archivo.name}",
                data=archivo.read_bytes(),
                file_name=archivo.name,
                mime=tipo,
                key=(
                    f"descarga_{st.session_state.thread_id}_"
                    f"{archivo.name}"
                ),
            )

    else:
        st.info(
            "Esta conversacion todavia no tiene "
            "cronogramas exportados."
        )

else:
    st.info(
        "Esta conversacion todavia no tiene "
        "cronogramas exportados."
    )
