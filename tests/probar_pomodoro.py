
from planning import aplicar_pomodoro

cronograma = {
    "cronograma": [
        {
            "fecha": "2026-11-25",
            "actividades": [
                {
                    "tema": "Unidad 1: Cinematica",
                    "actividad": "Estudio y ejercicios",
                    "horas": 3,
                }
            ],
        }
    ],
    "total_horas": 3,
}

resultado = aplicar_pomodoro(cronograma)

actividad = resultado["cronograma"][0]["actividades"][0]

print("\n=== SESIONES POMODORO ===")

for sesion in actividad["sesiones"]:
    print(
        sesion["tipo"],
        "-",
        sesion["minutos"],
        "minutos",
    )

print("\nCiclos completos:", resultado["total_ciclos"])
print("Descansos largos:", resultado["total_descansos_largos"])
print("Minutos de estudio:", resultado["total_minutos_estudio"])
print("Minutos de descanso:", resultado["total_minutos_descanso"])

assert resultado["total_descansos_largos"] >= 1

assert (
    resultado["total_minutos_estudio"]
    + resultado["total_minutos_descanso"]
    == 180
)

assert actividad["minutos_estudio"] > 0
assert actividad["minutos_descanso"] > 0

print("\nPrueba correcta.")

