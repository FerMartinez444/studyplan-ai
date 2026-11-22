
import json
import uuid
from pathlib import Path

import streamlit as st
from langchain_core.messages import AIMessage, ToolMessage

from agent import crear_agente
from rag import ingestar_pdf


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

if "metodologias_cargadas" not in st.session_state:
    st.session_state.metodologias_cargadas = []


# CARGA DE DOCUMENTOS

with st.sidebar:

    st.header("Configuracion del estudio")

    st.subheader("Documentos")

    categoria = st.selectbox(
        "Tipo de documento",
        ["programa", "metodologia"],
    )

    archivo = st.file_uploader(
        "Selecciona un PDF",
        type=["pdf"],
    )

    if st.button("Incorporar documento"):

        if archivo is None:
            st.warning("Primero selecciona un archivo.")

        else:
            try:
                with st.spinner("Procesando PDF..."):

                    resultado = ingestar_pdf(
                        contenido=archivo.getvalue(),
                        nombre=archivo.name,
                        categoria=categoria,
                        sesion_id=st.session_state.thread_id,
                    )

                if categoria == "programa":
                    st.session_state.programa_id = (
                        resultado["documento_id"]
                    )
                    st.session_state.programa_nombre = (
                        resultado["archivo"]
                    )

                else:
                    nombre = resultado["archivo"]

                    if nombre not in st.session_state.metodologias_cargadas:
                        st.session_state.metodologias_cargadas.append(
                            nombre
                        )

                st.success(
                    f"Documento incorporado. "
                    f"Fragmentos: {resultado['fragmentos']}"
                )

            except Exception as error:
                st.error(f"Error al procesar el PDF: {error}")

    if st.session_state.programa_nombre:
        st.info(
            "Programa activo: "
            + st.session_state.programa_nombre
        )

    st.subheader("Metodologia")

    metodologia = st.selectbox(
        "Selecciona tu metodologia",
        [
            "Pomodoro",
            "Repeticion espaciada",
        ],
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
        "Pomodoro": "pomodoro.pdf",
        "Repeticion espaciada": "repeticion_espaciada.pdf",
    }

    fuente_elegida = fuentes[metodologia]

    programa_id = st.session_state.programa_id

    consulta_completa = f"""
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
    - Si hay un programa cargado, consulta su contenido completo mediante consultar_programa_completo.
    - Consulta las reglas de la metodologia seleccionada mediante consultar_material.
    - Respeta los horarios indicados por el estudiante.
    - No inventes unidades ni reglas metodologicas.
    - Limita tu respuesta a la planificacion del estudio.
    """

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

st.divider()
st.subheader("Cronogramas exportados")

carpeta_outputs = Path(__file__).resolve().parent / "outputs"

if carpeta_outputs.exists():

    archivos_csv = sorted(
        carpeta_outputs.glob("*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if archivos_csv:
        for ruta in archivos_csv[:5]:
            st.download_button(
                label=f"Descargar {ruta.name}",
                data=ruta.read_bytes(),
                file_name=ruta.name,
                mime="text/csv",
                key=f"descarga_{ruta.name}",
            )
    else:
        st.info("Todavia no hay cronogramas exportados.")

else:
    st.info("Todavia no hay cronogramas exportados.")
