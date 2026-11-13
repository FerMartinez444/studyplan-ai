from planning import (
    calcular_disponibilidad_base,
    generar_cronograma_base,
)

disponibilidad = calcular_disponibilidad_base(
    "2026-11-16",
    "2026-11-30",
    [2, 2, 2, 2, 2, 4, 0],
)

plan = generar_cronograma_base(
    disponibilidad,
    ["Induccion", "Inductancia", "Corriente alterna"],
    [5, 3, 2],
)

for dia in plan["cronograma"]:
    print(dia)