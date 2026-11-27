
import json

from tools import crear_tools_planificacion

calcular, generar = crear_tools_planificacion(
    "prueba-integracion-segura"
)

resultado = json.loads(calcular.invoke({
    "fecha_inicio": "2026-11-26",
    "fecha_examen": "2026-12-15",
    "horas_por_dia": [2, 2, 2, 2, 2, 4, 0],
}))

assert resultado["estado"] == "correcto"
assert resultado["cantidad_dias"] == 16
assert resultado["total_horas"] == 38

print("Disponibilidad calculada:")
print(json.dumps(resultado, indent=2))

plan = json.loads(generar.invoke({
    "disponibilidad_id": resultado["disponibilidad_id"],
    "temas": [
        "Unidad 1: Cinematica",
        "Unidad 2: Dinamica",
    ],
    "dificultades": [3, 4],
    "metodologia": "ninguna",
    "materia": "Fisica I",
}))

assert plan["estado"] == "correcto", plan
assert plan["total_horas"] == 38
assert plan["cantidad_dias"] == 16
assert plan["archivo"].endswith(".csv")
assert plan["archivo_excel"].endswith(".xlsx")

print("\nPlan generado:")
print(json.dumps(plan, indent=2, ensure_ascii=False))
# Probar aislamiento entre conversaciones.
_, generar_otra_sesion = crear_tools_planificacion(
    "otra-conversacion"
)

resultado_invalido = json.loads(
    generar_otra_sesion.invoke({
        "disponibilidad_id": resultado["disponibilidad_id"],
        "temas": ["Unidad 1"],
        "dificultades": [3],
        "metodologia": "ninguna",
        "materia": "Prueba",
    })
)

assert resultado_invalido["estado"] == "error"

print("Aislamiento entre conversaciones: CORRECTO")
print("\nPRUEBA CORRECTA")
