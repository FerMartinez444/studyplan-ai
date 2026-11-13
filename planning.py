from datetime import date, timedelta

def calcular_disponibilidad_base(
        fecha_inicio: str,
        fecha_examen: str,
        horas_por_dia: list[float]
) -> dict:
    inicio = date.fromisoformat(fecha_inicio)
    examen = date.fromisoformat(fecha_examen)

    if inicio >= examen:
        raise ValueError(
            "La fecha de inicio debe ser anterior al examen."
        )

    if len(horas_por_dia) != 7:
        raise ValueError(
            "Debes indicar las horas de los siete dias."
        )

    if any(h < 0 or h > 24 for h in horas_por_dia):
        raise ValueError(
            "Las horas deben estar entre 0 y 24."
        )

    dias = []
    fecha_actual = inicio

    while fecha_actual < examen:
        indice_dia = fecha_actual.weekday()
        horas = horas_por_dia[indice_dia]

        if horas > 0:
            dias.append({
                "fecha": fecha_actual.isoformat(),
                "horas": horas,
            })

        fecha_actual += timedelta(days=1)

    total_horas = sum(
        dia["horas"] for dia in dias
    )

    return {
        "dias": dias,
        "total_horas": total_horas,
    }

def generar_cronograma_base(
        disponibilidad: dict,
        temas: list[str],
        dificultades: list[int],
) -> dict:

    if not temas or len(temas) != len(dificultades):
        raise ValueError(
            "Los temas y dificultades no coinciden."
        )

    if any(not tema.strip() for tema in temas):
        raise ValueError("Hay temas vacios.")

    if any(d < 1 or d > 5 for d in dificultades):
        raise ValueError(
            "La dificultad debe estar entre 1 y 5."
        )

    dias = disponibilidad["dias"]
    total_horas = disponibilidad["total_horas"]

    if total_horas <= 0:
        raise ValueError("No hay horas disponibles.")

    horas_repaso = round(total_horas * 0.20, 2)
    horas_contenidos = total_horas - horas_repaso

    suma_dificultades = sum(dificultades)

    objetivos = [
        horas_contenidos * d / suma_dificultades
        for d in dificultades
    ]

    asignadas = [0.0] * len(temas)
    cronograma = []
    repaso_restante = horas_repaso

    for dia in dias:
        horas_restantes = dia["horas"]
        actividades = []

        while horas_restantes > 0.000001:
            bloque = min(1.0, horas_restantes)

            deficits = [
                objetivos[i] - asignadas[i]
                for i in range(len(temas))
            ]

            if max(deficits) <= 0.000001:
                tema = "Repaso general"
                actividad = "Practica y autoevaluacion"
                repaso_restante -= bloque

            else:
                indice = max(
                    range(len(temas)),
                    key=lambda i: deficits[i]
                )

                tema = temas[indice]
                actividad = "Estudio y ejercicios"
                asignadas[indice] += bloque

            actividades.append({
                "tema": tema,
                "actividad": actividad,
                "horas": round(bloque,2)
            })

            horas_restantes -= bloque

        cronograma.append({
            "fecha": dia["fecha"],
            "actividades": actividades,
        })

    return {
        "cronograma": cronograma,
        "total_horas": total_horas,
        "horas_por_tema": {
            temas[i]: round(asignadas[i], 2)
            for i in range(len(temas))
        },
    }
