
import json
import csv
from pathlib import Path

from planning import calcular_disponibilidad_base
from tools import generar_plan_estudio

disponibilidad = calcular_disponibilidad_base(
    fecha_inicio="2026-11-23",
    fecha_examen="2026-12-13",
    horas_por_dia=[2, 2, 2, 2, 2, 2, 2],
)

for metodo in ["pomodoro", "repeticion_espaciada"]:

    resultado = generar_plan_estudio.invoke({
        "disponibilidad_json": json.dumps(disponibilidad),
        "temas": [
            "Unidad 1: Cinematica",
            "Unidad 2: Dinamica",
        ],
        "dificultades": [2, 4],
        "metodologia": metodo,
    })

    datos = json.loads(resultado)

    print("\nMetodologia:", metodo)
    print(json.dumps(datos, indent=2, ensure_ascii=False))

    assert datos["estado"] == "correcto", datos

    ruta = Path("outputs") / datos["archivo"]
    assert ruta.exists()

    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    assert filas, "El CSV no contiene actividades."

    if metodo == "pomodoro":
        assert datos["total_ciclos"] > 0
        assert datos["total_minutos_estudio"] > 0
        assert any(
            int(fila["Ciclos Pomodoro"]) > 0
            for fila in filas
        )

    else:
        assert datos["repasos_programados"] > 0
        assert any(
            fila["Actividad"] == "Repaso espaciado"
            for fila in filas
        )
        assert any(
            fila["Fecha ideal del repaso"]
            for fila in filas
        )

    print("Archivo generado:", ruta)
    print("Prueba correcta.")

print("\nAMBAS METODOLOGIAS FUNCIONAN.")
