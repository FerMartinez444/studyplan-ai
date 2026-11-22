
from planning import aplicar_pomodoro


cronograma_original = {
    "cronograma": [
        {
            "fecha": "2026-11-23",
            "actividades": [
                {
                    "tema": "Unidad 1: Mediciones y errores",
                    "actividad": "Estudio y ejercicios",
                    "horas": 1,
                },
                {
                    "tema": "Unidad 2: Optica geometrica",
                    "actividad": "Estudio y ejercicios",
                    "horas": 1,
                },
            ],
        }
    ],
    "total_horas": 2,
}


resultado = aplicar_pomodoro(
    cronograma=cronograma_original,
    minutos_estudio=25,
    minutos_descanso=5,
)


print("=== CRONOGRAMA POMODORO ===")

for dia in resultado["cronograma"]:
    print("\nFecha:", dia["fecha"])

    for actividad in dia["actividades"]:
        print("\nTema:", actividad["tema"])
        print("Ciclos:", actividad["ciclos"])
        print("Estudio:", actividad["minutos_estudio"], "min")
        print("Descanso:", actividad["minutos_descanso"], "min")


print("\n=== TOTALES ===")
print("Estudio:", resultado["total_minutos_estudio"])
print("Descanso:", resultado["total_minutos_descanso"])


assert resultado["total_minutos_estudio"] == 100
assert resultado["total_minutos_descanso"] == 20

assert (
    resultado["total_minutos_estudio"]
    + resultado["total_minutos_descanso"]
) == 120

print("\nPrueba correcta.")
