
from pathlib import Path

from rag import ingestar_pdf


BASE = Path(__file__).resolve().parent

RUTA_METODOLOGIAS = (
    BASE / "conocimiento" / "metodologias"
)

SESION_CONOCIMIENTO = "dominio-global"


def preparar_conocimiento():

    archivos = sorted(
        RUTA_METODOLOGIAS.glob("*.pdf")
    )

    if not archivos:
        raise FileNotFoundError(
            "No se encontraron documentos metodologicos."
        )

    print("=== INGESTA DE CONOCIMIENTO ===")

    for archivo in archivos:

        resultado = ingestar_pdf(
            contenido=archivo.read_bytes(),
            nombre=archivo.name,
            categoria="metodologia",
            sesion_id=SESION_CONOCIMIENTO,
        )

        print(
            f"Documento: {resultado['archivo']}"
        )
        print(
            f"Paginas: {resultado['paginas']}"
        )
        print(
            f"Fragmentos: {resultado['fragmentos']}"
        )
        print("-------------------------")

    print("Ingesta finalizada correctamente.")


if __name__ == "__main__":
    preparar_conocimiento()
