
import json

from tools import crear_tool_conocimiento


herramienta = crear_tool_conocimiento()

resultado = herramienta.invoke({
    "consulta": (
        "Como priorizar las unidades academicas segun "
        "su dificultad y que porcentaje de tiempo "
        "se reserva para repaso?"
    ),
    "fuente": "Priorización_distribución_del_estudio.pdf",
})

datos = json.loads(resultado)

if isinstance(datos, dict) and "error" in datos:
    raise RuntimeError(datos["mensaje"])

assert datos, "No se recuperaron fragmentos."

print("\n=== CONOCIMIENTO RECUPERADO ===\n")

for fragmento in datos:
    print("Fuente:", fragmento["fuente"])
    print("Pagina:", fragmento["pagina"])
    print("Texto:", fragmento["texto"])
    print("-------------------------")

assert all(
    fragmento["fuente"] == "Priorización_distribución_del_estudio.pdf"
    for fragmento in datos
)

texto = " ".join(
    fragmento["texto"].lower()
    for fragmento in datos
)

assert (
    "dificultad" in texto
    or "20 %" in texto
    or "repaso" in texto
), "No se recuperaron las reglas esperadas."

print("\nPrueba correcta.")
