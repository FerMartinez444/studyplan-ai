from datetime import date, timedelta
from copy import deepcopy
from math import isfinite

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

    if any(
        not isinstance(tema, str) or not tema.strip()
        for tema in temas
    ):
        raise ValueError("Hay temas vacios.")

    if any(
        type(d) is not int or d < 1 or d > 5
        for d in dificultades
    ):
        raise ValueError(
            "La dificultad debe estar entre 1 y 5."
        )

    dias = disponibilidad["dias"]

    total_horas = sum(
        float(dia["horas"]) for dia in dias
    )

    if total_horas <= 0:
        raise ValueError("No hay horas disponibles.")

    # Reservamos el 20 % para repaso general.
    horas_repaso = total_horas * 0.20
    horas_contenidos = total_horas - horas_repaso

    suma_dificultades = sum(dificultades)

    # Horas asignadas a cada unidad segun dificultad.
    objetivos = [
        horas_contenidos * dificultad / suma_dificultades
        for dificultad in dificultades
    ]

    pendientes = objetivos.copy()
    cronograma = []
    indice_tema = 0

    for dia in dias:

        horas_restantes = float(dia["horas"])
        actividades = []

        while horas_restantes > 0.000001:

            # Mientras queden contenidos por estudiar.
            while (
                indice_tema < len(temas)
                and pendientes[indice_tema] <= 0.000001
            ):
                indice_tema += 1

            if indice_tema < len(temas):

                bloque = min(
                    1.0,
                    horas_restantes,
                    pendientes[indice_tema],
                )

                actividades.append({
                    "tema": temas[indice_tema],
                    "actividad": "Estudio y ejercicios",
                    "horas": round(bloque, 4),
                })

                pendientes[indice_tema] -= bloque

            else:
                # Las horas sobrantes corresponden al repaso.
                bloque = min(1.0, horas_restantes)

                actividades.append({
                    "tema": "Repaso general",
                    "actividad": "Practica y autoevaluacion",
                    "horas": round(bloque, 4),
                })

            horas_restantes -= bloque

        cronograma.append({
            "fecha": dia["fecha"],
            "actividades": actividades,
        })

    return {
        "cronograma": cronograma,
        "total_horas": round(total_horas, 4),
        "horas_estudio": round(horas_contenidos, 4),
        "horas_repaso": round(horas_repaso, 4),
        "horas_por_tema": {
            temas[i]: round(objetivos[i], 4)
            for i in range(len(temas))
        },
    }



def aplicar_pomodoro(cronograma: dict) -> dict:
    """Aplica Pomodoro con parametros fijos al cronograma."""

    MINUTOS_ESTUDIO = 25
    DESCANSO_CORTO = 5
    DESCANSO_LARGO = 20
    CICLOS_DESCANSO_LARGO = 4

    if "cronograma" not in cronograma:
        raise ValueError("El cronograma no tiene actividades.")

    resultado = deepcopy(cronograma)

    total_estudio = 0
    total_descanso = 0
    total_ciclos = 0
    total_descansos_largos = 0

    for dia in resultado["cronograma"]:

        ciclos_del_dia = 0

        for actividad in dia["actividades"]:

            horas = float(actividad["horas"])

            if not isfinite(horas) or horas <= 0:
                raise ValueError(
                    "Una actividad tiene horas invalidas."
                )

            minutos_disponibles = round(horas * 60)

            minutos_restantes = minutos_disponibles

            estudio = 0
            descanso = 0
            ciclos = 0
            descansos_largos = 0
            sesiones = []

            while minutos_restantes > 0:

                # Estudiar hasta 25 minutos.
                bloque_estudio = min(
                    MINUTOS_ESTUDIO,
                    minutos_restantes,
                )

                sesiones.append({
                    "tipo": "estudio",
                    "minutos": bloque_estudio,
                })

                estudio += bloque_estudio
                minutos_restantes -= bloque_estudio

                # Un ciclo completo requiere 25 min de estudio.
                if bloque_estudio < MINUTOS_ESTUDIO:
                    break

                ciclos += 1
                ciclos_del_dia += 1

                # Si no queda tiempo, no agregamos descanso.
                if minutos_restantes == 0:
                    break

                es_descanso_largo = (
                    ciclos_del_dia
                    % CICLOS_DESCANSO_LARGO == 0
                )

                duracion_descanso = (
                    DESCANSO_LARGO
                    if es_descanso_largo
                    else DESCANSO_CORTO
                )

                # Solo programamos el descanso si cabe
                # y queda tiempo para seguir estudiando.
                if minutos_restantes > duracion_descanso:

                    sesiones.append({
                        "tipo": (
                            "descanso_largo"
                            if es_descanso_largo
                            else "descanso_corto"
                        ),
                        "minutos": duracion_descanso,
                    })

                    descanso += duracion_descanso
                    minutos_restantes -= duracion_descanso

                    if es_descanso_largo:
                        descansos_largos += 1

                else:
                    # Aprovechamos los minutos restantes
                    # como una sesion corta de estudio.
                    sesiones.append({
                        "tipo": "estudio",
                        "minutos": minutos_restantes,
                    })

                    estudio += minutos_restantes
                    minutos_restantes = 0

            actividad["metodologia"] = "Pomodoro"
            actividad["actividad"] = "Estudio con tecnica Pomodoro"
            actividad["ciclos"] = ciclos
            actividad["descansos_largos"] = descansos_largos
            actividad["minutos_estudio"] = estudio
            actividad["minutos_descanso"] = descanso
            actividad["sesiones"] = sesiones

            total_estudio += estudio
            total_descanso += descanso
            total_ciclos += ciclos
            total_descansos_largos += descansos_largos

    resultado["metodologia"] = "Pomodoro"

    resultado["configuracion_metodologia"] = {
        "minutos_estudio": MINUTOS_ESTUDIO,
        "descanso_corto": DESCANSO_CORTO,
        "descanso_largo": DESCANSO_LARGO,
        "ciclos_para_descanso_largo": CICLOS_DESCANSO_LARGO,
    }

    resultado["total_minutos_estudio"] = total_estudio
    resultado["total_minutos_descanso"] = total_descanso
    resultado["total_ciclos"] = total_ciclos
    resultado["total_descansos_largos"] = total_descansos_largos

    return resultado


def generar_cronograma_espaciado(
    disponibilidad: dict,
    temas: list[str],
    dificultades: list[int],
) -> dict:
    """Genera estudio y repasos espaciados dentro de la disponibilidad."""

    INTERVALOS = [1, 3, 7, 14]
    MINUTOS_REPASO = 15
    PORCENTAJE_ESTUDIO = 0.80

    if not temas or len(temas) != len(dificultades):
        raise ValueError("Los temas y dificultades no coinciden.")

    if any(not isinstance(t, str) or not t.strip() for t in temas):
        raise ValueError("Hay temas vacios.")

    if any(type(d) is not int or d < 1 or d > 5 for d in dificultades):
        raise ValueError("Las dificultades deben estar entre 1 y 5.")

    dias_originales = disponibilidad["dias"]

    if not dias_originales:
        raise ValueError("No hay dias disponibles.")

    # Cada dia tiene un presupuesto de estudio y repaso.
    dias = []

    for dia in dias_originales:
        minutos = round(float(dia["horas"]) * 60)

        if minutos <= 0:
            raise ValueError("Las horas disponibles deben ser positivas.")

        estudio = round(minutos * PORCENTAJE_ESTUDIO)

        dias.append({
            "fecha": dia["fecha"],
            "fecha_obj": date.fromisoformat(dia["fecha"]),
            "minutos_totales": minutos,
            "estudio_disponible": estudio,
            "repaso_disponible": minutos - estudio,
            "actividades": [],
        })

    if any(
        dias[i]["fecha_obj"] >= dias[i + 1]["fecha_obj"]
        for i in range(len(dias) - 1)
    ):
        raise ValueError("Los dias deben estar ordenados y sin duplicados.")

    # Distribuir el tiempo de estudio segun dificultad.
    total_estudio = sum(d["estudio_disponible"] for d in dias)
    suma_dificultades = sum(dificultades)

    objetivos = []
    acumulado = 0

    for i, dificultad in enumerate(dificultades):
        siguiente = round(
            total_estudio * sum(dificultades[:i + 1])
            / suma_dificultades
        )
        objetivos.append(siguiente - acumulado)
        acumulado = siguiente

    # PASO 1: Programar el estudio inicial.
    indice_tema = 0
    pendientes = objetivos.copy()
    primeras_fechas = {}

    for dia in dias:
        while dia["estudio_disponible"] > 0:

            while (
                indice_tema < len(temas)
                and pendientes[indice_tema] == 0
            ):
                indice_tema += 1

            if indice_tema == len(temas):
                break

            bloque = min(
                60,
                dia["estudio_disponible"],
                pendientes[indice_tema],
            )

            tema = temas[indice_tema]

            if tema not in primeras_fechas:
                primeras_fechas[tema] = dia["fecha_obj"]

            dia["actividades"].append({
                "tema": tema,
                "actividad": "Estudio inicial",
                "horas": round(bloque / 60, 4),
            })

            pendientes[indice_tema] -= bloque
            dia["estudio_disponible"] -= bloque

    # PASO 2: Crear los repasos previstos.
    eventos = []

    for tema in temas:
        fecha_inicial = primeras_fechas[tema]

        for intervalo in INTERVALOS:
            eventos.append({
                "tema": tema,
                "intervalo": intervalo,
                "fecha_objetivo": fecha_inicial
                + timedelta(days=intervalo),
            })

    # Atender primero los repasos con fecha mas temprana.
    eventos.sort(
        key=lambda e: (e["fecha_objetivo"], e["intervalo"])
    )

    pendientes_repaso = []
    repasos_programados = 0
    fechas_repasadas = set()

    for evento in eventos:
        asignado = False

        for dia in dias:
            clave = (evento["tema"], dia["fecha"])

            if dia["fecha_obj"] < evento["fecha_objetivo"]:
                continue

            if dia["repaso_disponible"] < MINUTOS_REPASO:
                continue

            if clave in fechas_repasadas:
                continue

            dia["actividades"].append({
                "tema": evento["tema"],
                "actividad": "Repaso espaciado",
                "horas": MINUTOS_REPASO / 60,
                "intervalo_dias": evento["intervalo"],
                "fecha_objetivo": (
                    evento["fecha_objetivo"].isoformat()
                ),
            })

            dia["repaso_disponible"] -= MINUTOS_REPASO
            fechas_repasadas.add(clave)
            repasos_programados += 1
            asignado = True
            break

        if not asignado:
            pendientes_repaso.append({
                "tema": evento["tema"],
                "intervalo_dias": evento["intervalo"],
                "fecha_objetivo": (
                    evento["fecha_objetivo"].isoformat()
                ),
                "motivo": (
                    "No hay disponibilidad suficiente "
                    "antes del examen."
                ),
            })

    # PASO 3: Construir el resultado.
    cronograma = []

    for dia in dias:
        cronograma.append({
            "fecha": dia["fecha"],
            "actividades": dia["actividades"],
        })

    minutos_repaso = repasos_programados * MINUTOS_REPASO
    minutos_disponibles = sum(
        d["minutos_totales"] for d in dias
    )

    minutos_utilizados = total_estudio + minutos_repaso

    return {
        "cronograma": cronograma,
        "metodologia": "Repeticion espaciada",
        "intervalos_dias": INTERVALOS,
        "total_horas": round(minutos_utilizados / 60, 4),
        "horas_disponibles": round(
            minutos_disponibles / 60, 4
        ),
        "horas_estudio": round(total_estudio / 60, 4),
        "horas_repaso": round(minutos_repaso / 60, 4),
        "horas_libres": round(
            (minutos_disponibles - minutos_utilizados) / 60,
            4,
        ),
        "horas_por_tema": {
            tema: round(objetivos[i] / 60, 4)
            for i, tema in enumerate(temas)
        },
        "repasos_programados": repasos_programados,
        "repasos_pendientes": pendientes_repaso,
    }



