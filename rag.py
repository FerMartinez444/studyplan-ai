import hashlib
import json
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

BASE = Path(__file__).resolve().parent

RUTA_BD = BASE / "chroma_bd"
RUTA_PROGRAMAS = BASE / "programas_extraidos"

CATEGORIAS = {"programa", "metodologia"}

# Modelo para generar embeddings
embeddings = HuggingFaceEmbeddings(
    model_name=(
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )
)

# Base de datos vectorial
base_vectorial = Chroma(
    collection_name = "studyplan_conocimiento",
    embedding_function = embeddings,
    persist_directory=str(RUTA_BD),
)

# Configuracion del chuking
fragmentador = RecursiveCharacterTextSplitter(
    chunk_size=900,
    chunk_overlap=150,
)

def extraer_texto_pdf(contenido: bytes) -> list[dict]:
    """Extrae el texto del PDF, conservando las paginas."""

    lector = PdfReader(BytesIO(contenido))

    paginas = []

    for numero, pagina in enumerate(lector.pages, start=1):
        texto = " ".join(
            (pagina.extract_text() or "").split()
        )

        if texto.strip():
            paginas.append({
                "pagina": numero,
                "texto": texto,
            })

    if not paginas:
        raise ValueError(
            "No se pudo extraer el texto. "
            "El PDF puede ser escaneado."
        )

    return paginas

def ingestar_pdf(
        contenido: bytes,
        nombre: str,
        categoria: str,
        sesion_id: str,
) -> dict:
    """Extrae, fragmenta, vectoriza y almacena un PDF."""

    if categoria not in CATEGORIAS:
        raise ValueError("Categoria no permitida.")

    if not sesion_id:
        raise ValueError("La sesion es obligatoria.")

    if not contenido.startswith(b"%PDF-"):
        raise ValueError("El archivo no es un PDF valido.")

    if len(contenido) > 15 * 1024 * 1024:
        raise ValueError("El PDF supera los 15 MB.")

    paginas = extraer_texto_pdf(contenido)

    nombre_seguro = Path(nombre).name

    documento_id = hashlib.sha256(
        contenido + categoria.encode() + sesion_id.encode()
    ).hexdigest()

    documentos = []

    for pagina in paginas:
        documentos.append(
            Document(
                page_content=pagina["texto"],
                metadata={
                    "fuente": nombre_seguro,
                    "pagina": pagina["pagina"],
                    "categoria": categoria,
                    "sesion": sesion_id,
                    "documento_id": documento_id,
                },
            )
        )
    chunks = fragmentador.split_documents(documentos)

    ids = [
        f"{documento_id}-{i}"
        for i in range(len(chunks))
    ]

    base_vectorial.add_documents(
        documents=chunks,
        ids=ids,
    )

    if categoria == "programa":
        carpeta = RUTA_PROGRAMAS / sesion_id
        carpeta.mkdir(parents=True, exist_ok=True)

        ruta = carpeta / f"{documento_id}.json"

        ruta.write_text(
            json.dumps(
                {
                    "fuente": nombre_seguro,
                    "paginas": paginas,
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    return{
        "documento_id": documento_id,
        "archivo": nombre_seguro,
        "categoria": categoria,
        "paginas": len(paginas),
        "fragmentos": len(chunks),
    }

def buscar_conocimiento(
        consulta: str,
        categoria: str,
        sesion_id: str,
        cantidad: int = 4,
        fuente: str = "",
) -> list[dict]:
    """Busca fragmentos relevantes en Chroma."""

    if categoria not in CATEGORIAS:
        raise ValueError("Categoria no permitida")

    if not consulta.strip():
        raise ValueError("La consulta no puede estar vacia.")

    if not sesion_id:
        raise ValueError("La sesion es obligatoria.")

    cantidad = max(1, min(cantidad,6))

    filtros = [
        {"categoria": categoria},
        {"sesion": sesion_id},
    ]

    if fuente:
        filtros.append({"fuente": fuente})

    documentos = base_vectorial.similarity_search(
        query=consulta,
        k=cantidad,
        filter={"$and": filtros},
    )

    resultados = []

    for documento in documentos:
        resultados.append({
            "texto":documento.page_content,
            "fuente":documento.metadata["fuente"],
            "pagina":documento.metadata["pagina"],
            "categoria":documento.metadata["categoria"],
        })
    return resultados

def obtener_programa_completo(
        sesion_id: str,
        documento_id: str,
) -> dict:
    """Lee todas las paginas de un programa ta integrido."""

    if not sesion_id or not documento_id:
        raise ValueError("Faltan identificadores.")

    ruta = (
        RUTA_PROGRAMAS
        / sesion_id
        / f"{documento_id}.json"
    )

    if not ruta.is_file():
        raise FileNotFoundError(
            "No se encontro el programa solicitado."
        )

    return json.loads(ruta.read_text(encoding="utf-8"))

