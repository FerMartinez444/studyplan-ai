
from planning import (
    calcular_disponibilidad_base,
    generar_cronograma_base,
)

disponibilidad = calcular_disponibilidad_base(
    fecha_inicio="2026-11-23",
    fecha_examen="2026-11-28",
    horas_por_dia=[2, 2, 2, 2, 2, 0, 0],
)

cronograma = generar_cronograma_base(
    disponibilidad=disponibilidad,
    temas=[
        "Unidad 1: Cinematica",
        "Unidad 2: Dinamica",
        "Unidad 3: Energia",
    ],
    dificultades=[1, 2, 3],
)

print("Horas totales:", cronograma["total_horas"])
print("Horas de estudio:", cronograma["horas_estudio"])
print("Horas de repaso:", cronograma["horas_repaso"])

for dia in cronograma["cronograma"]:
    print("\n", dia["fecha"])

    for actividad in dia["actividades"]:
        print(
            actividad["tema"],
            "-",
            actividad["horas"],
            "horas",
        )

assert abs(cronograma["total_horas"] - 10) < 0.001
assert abs(cronograma["horas_estudio"] - 8) < 0.001
assert abs(cronograma["horas_repaso"] - 2) < 0.001

total_asignado = sum(
    actividad["horas"]
    for dia in cronograma["cronograma"]
    for actividad in dia["actividades"]
)

assert abs(total_asignado - 10) < 0.001

print("\nPrueba correcta.")
