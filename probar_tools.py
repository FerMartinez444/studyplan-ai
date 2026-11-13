
import json

from tools import (
    consultar_estrategia,
    calcular_disponibilidad,
    generar_cronograma,
    exportar_cronograma,
)


print("=== PRUEBA 1: CONOCIMIENTO PROPIO ===")

estrategia = consultar_estrategia.invoke({
    "estrategia": "priorizacion"
})

print(estrategia)


print("\n=== PRUEBA 2: DISPONIBILIDAD ===")

disponibilidad = calcular_disponibilidad.invoke({
    "fecha_inicio": "2026-11-16",
    "fecha_examen": "2026-11-30",
    "horas_por_dia": [2, 2, 2, 2, 2, 4, 0]
})

datos = json.loads(disponibilidad)

assert datos["total_horas"] == 28, (
    "ERROR: el total de horas es incorrecto"
)

print("Horas disponibles:", datos["total_horas"])


print("\n=== PRUEBA 3: CRONOGRAMA ===")

cronograma = generar_cronograma.invoke({
    "disponibilidad_json": disponibilidad,
    "temas": [
        "Induccion",
        "Inductancia",
        "Corriente alterna"
    ],
    "dificultades": [5, 3, 2]
})

plan = json.loads(cronograma)

assert plan["total_horas"] == 28, (
    "ERROR: el cronograma tiene horas incorrectas"
)

print("Cronograma generado correctamente")

for dia in plan["cronograma"]:
    print(dia)


print("\n=== PRUEBA 4: EXPORTACION ===")

exportacion = exportar_cronograma.invoke({
    "cronograma_json": cronograma
})

print(exportacion)

resultado = json.loads(exportacion)

assert resultado["estado"] == "exportado"

print("\nTODAS LAS PRUEBAS FINALIZARON CORRECTAMENTE")
