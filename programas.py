
import hashlib
import json
import re
from io import BytesIO
from pathlib import Path
from uuid import UUID

from langchain_core.tools import tool
from pypdf import PdfReader


BASE = Path(__file__).resolve().parent

RUTA_PROGRAMAS = BASE / "programas_usuario"

MAX_BYTES = 15 * 1024 * 1024
MAX_CARACTERES = 30000


def registrar_programa(
    contenido: bytes,
    nombre: str,
    sesion_id: str,
) -> dict:
    """
    Registra un programa subido desde Streamlit.

    No extrae texto ni genera embeddings.
    Solamente guarda el PDF para que el agente
    pueda procesarlo posteriormente.
    """

    UUID(sesion_id)

    if not contenido.startswith(b"%PDF-"):
        raise ValueError("El archivo no es un PDF valido.")

    if len(contenido) > MAX_BYTES:
        raise ValueError("El PDF supera los 15 MB.")

    documento_id = hashlib.sha256(contenido).hexdigest()

    carpeta = RUTA_PROGRAMAS / sesion_id
    carpeta.mkdir(parents=True, exist_ok=True)

    ruta = carpeta / f"{documento_id}.pdf"
    ruta.write_bytes(contenido)

    nombre_seguro = Path(nombre.replace("\\", "/")).name

    return {
        "documento_id": documento_id,
        "archivo": nombre_seguro,
    }


def crear_tool_ingesta(sesion_id: str):
    """
    Crea una herramienta limitada a los documentos
    pertenecientes a una sesion concreta.
    """

    UUID(sesion_id)

    @tool
    def ingestar_programa(documento_id: str) -> str:
        """
        Extrae el texto completo de un programa PDF
        previamente subido por el estudiante.

        Devuelve las paginas para que el agente
        identifique las unidades del programa.

        No almacena el documento en ChromaDB.
        """

        try:
            if not re.fullmatch(
                r"[0-9a-f]{64}",
                documento_id,
            ):
                raise ValueError(
                    "Identificador de documento invalido."
                )

            ruta = (
                RUTA_PROGRAMAS
                / sesion_id
                / f"{documento_id}.pdf"
            )

            if not ruta.is_file():
                raise FileNotFoundError(
                    "No existe un programa con ese identificador "
                    "en la sesion actual."
                )

            contenido = ruta.read_bytes()

            lector = PdfReader(BytesIO(contenido))

            paginas = []

            for numero, pagina in enumerate(
                lector.pages,
                start=1,
            ):
                texto = " ".join(
                    (pagina.extract_text() or "").split()
                )

                if texto:
                    paginas.append({
                        "pagina": numero,
                        "texto": texto,
                    })

            if not paginas:
                raise ValueError(
                    "No se pudo extraer texto del programa."
                )

            total_caracteres = sum(
                len(pagina["texto"])
                for pagina in paginas
            )

            if total_caracteres > MAX_CARACTERES:
                raise ValueError(
                    "El programa supera el limite de texto "
                    "admitido por esta version."
                )

            return json.dumps(
                {
                    "estado": "correcto",
                    "documento_id": documento_id,
                    "cantidad_paginas": len(lector.pages),
                    "paginas": paginas,
                },
                ensure_ascii=False,
            )

        except Exception as error:
            return json.dumps(
                {
                    "estado": "error",
                    "mensaje": str(error),
                },
                ensure_ascii=False,
            )

    return ingestar_programa
