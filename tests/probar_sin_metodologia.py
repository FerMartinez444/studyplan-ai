import json
from tools import generar_plan_estudio

disponibilidad = {
    "dias": [
        {"fecha": "2026-11-17", "horas": 2},
        {"fecha": "2026-11-28", "horas": 4},
        {"fecha": "2026-11-30", "horas": 2},
    ],
    "total_horas": 8,
}

resultado = generar_plan_estudio.invoke({
    "disponibilidad_json": json.dumps(disponibilidad),
    "temas": [
        "Unidad 1: Cinematica",
        "Unidad 2: Dinamica",
    ],
    "dificultades": [3, 4],
    "metodologia": "ninguna",
    "materia": "Fisica I",
})

print(json.dumps(
    json.loads(resultado),
    indent=4,
    ensure_ascii=False,
))