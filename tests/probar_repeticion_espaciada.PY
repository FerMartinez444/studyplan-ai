
from planning import (
    calcular_disponibilidad_base,
    generar_cronograma_espaciado,
)

# CASO 1: Sin disponibilidad los fines de semana.

disponibilidad = calcular_disponibilidad_base(
    fecha_inicio="2026-11-27",
    fecha_examen="2026-12-18",
    horas_por_dia=[2, 2, 2, 2, 2, 0, 0],
)

resultado = generar_cronograma_espaciado(
    disponibilidad,
    ["Unidad 1: Cinematica", "Unidad 2: Dinamica"],
    [2, 4],
)

dias_permitidos = {
    dia["fecha"]: dia["horas"]
    for dia in disponibilidad["dias"]
}

for dia in resultado["cronograma"]:
    fecha = dia["fecha"]

    assert fecha in dias_permitidos

    horas_asignadas = sum(
        actividad["horas"]
        for actividad in dia["actividades"]
    )

    assert horas_asignadas <= dias_permitidos[fecha] + 0.001

    # Nunca repetir una misma unidad dos veces
    # como repaso en el mismo dia.
    temas_repasados = [
        actividad["tema"]
        for actividad in dia["actividades"]
        if actividad["actividad"] == "Repaso espaciado"
    ]

    assert len(temas_repasados) == len(set(temas_repasados))

print("CASO 1: Correcto")
print("Repasos programados:", resultado["repasos_programados"])
print("Repasos pendientes:", len(resultado["repasos_pendientes"]))


# CASO 2: Examen cercano.

disponibilidad_corta = calcular_disponibilidad_base(
    fecha_inicio="2026-11-23",
    fecha_examen="2026-11-27",
    horas_por_dia=[2, 2, 2, 2, 2, 2, 2],
)

resultado_corto = generar_cronograma_espaciado(
    disponibilidad_corta,
    ["Unidad 1: Cinematica"],
    [3],
)

assert len(resultado_corto["repasos_pendientes"]) > 0

for dia in resultado_corto["cronograma"]:
    assert dia["fecha"] < "2026-11-27"

print("CASO 2: Correcto")
print("Repasos pendientes:", resultado_corto["repasos_pendientes"])

print("\nTodas las pruebas pasaron.")
