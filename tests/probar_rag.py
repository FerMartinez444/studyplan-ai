
from pathlib import Path

from rag import (
    ingestar_pdf,
    buscar_conocimiento,
    obtener_programa_completo,
)

BASE = Path(__file__).resolve().parent
SESION = "prueba-rag-001"

archivos = [
    (
        BASE / "documentos/programas/programa_fisica.pdf",
        "programa",
    ),
    (
        BASE / "documentos/metodologias/pomodoro.pdf",
        "metodologia",
    ),
    (
        BASE / "documentos/metodologias/repeticion_espaciada.pdf",
        "metodologia",
    ),
]


print("=== INGESTA ===")

programa_id = None

for ruta, categoria in archivos:

    resultado = ingestar_pdf(
        contenido=ruta.read_bytes(),
        nombre=ruta.name,
        categoria=categoria,
        sesion_id=SESION,
    )

    print(resultado)

    if categoria == "programa":
        programa_id = resultado["documento_id"]


print("\n=== BUSQUEDA SEMANTICA ===")

resultados = buscar_conocimiento(
    consulta="Como se organizan los intervalos Pomodoro",
    categoria="metodologia",
    sesion_id=SESION,
)

for resultado in resultados:
    print("\nDocumento:", resultado["fuente"])
    print("Pagina:", resultado["pagina"])
    print("Texto:", resultado["texto"][:450])


print("\n=== PROGRAMA COMPLETO ===")

programa = obtener_programa_completo(
    sesion_id=SESION,
    documento_id=programa_id,
)

print("Fuente:", programa["fuente"])
print("Paginas:", len(programa["paginas"]))

for pagina in programa["paginas"]:
    print(
        "Pagina",
        pagina["pagina"],
        ":",
        pagina["texto"][:150],
    )
