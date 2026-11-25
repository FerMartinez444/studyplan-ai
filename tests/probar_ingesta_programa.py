
import json
from pathlib import Path
from uuid import uuid4

from programas import (
    registrar_programa,
    crear_tool_ingesta,
)


# Cambiar por la ruta real de un PDF de programa
RUTA_PDF = Path(
    r"D:\FACULTAD\FACU\CUARTO\MODELO DE LENGAUJES\studyplan-ai-main\documentos\programas\programa_fisica.pdf"
)

if not RUTA_PDF.is_file():
    raise FileNotFoundError(
        "Coloca programa_fisica.pdf en la carpeta principal "
        "del proyecto para realizar esta prueba."
    )

sesion_id = str(uuid4())

registro = registrar_programa(
    contenido=RUTA_PDF.read_bytes(),
    nombre=RUTA_PDF.name,
    sesion_id=sesion_id,
)

print("=== PROGRAMA REGISTRADO ===")
print(registro)

herramienta = crear_tool_ingesta(sesion_id)

resultado = herramienta.invoke({
    "documento_id": registro["documento_id"]
})

datos = json.loads(resultado)

assert datos["estado"] == "correcto"
assert datos["cantidad_paginas"] > 0
assert datos["paginas"]

print("\n=== RESULTADO DE LA INGESTA ===")
print("Paginas:", datos["cantidad_paginas"])

for pagina in datos["paginas"]:
    print("\nPagina:", pagina["pagina"])
    print(pagina["texto"][:500])

print("\nPrueba correcta.")
