import re
import unicodedata
from datetime import date
import csv
import json
from pathlib import Path
from uuid import uuid4
from langchain.tools import tool
from planning import(
    calcular_disponibilidad_base,
    generar_cronograma_base,
    aplicar_pomodoro,
    generar_cronograma_espaciado,
)

from rag import buscar_conocimiento

BASE = Path(__file__).resolve().parent

@tool
def calcular_disponibilidad(
    fecha_inicio: str,
    fecha_examen: str,
    horas_por_dia: list[float],
) -> str:
    """Calcula los dias y horas disponibles
    Las fechas usan AAAA-MM-DD.
    Las horas van de lunes a domingo.
    """
    try:
        resultado = calcular_disponibilidad_base(
            fecha_inicio,
            fecha_examen,
            horas_por_dia,
        )

        return json.dumps(
            resultado,
            ensure_ascii=False,
        )
    except Exception as error:
        return f"ERROR: {error}"


def crear_tool_conocimiento():

    @tool
    def consultar_conocimiento(
        consulta: str,
        fuente: str = "",
    ) -> str:
        """Recupera reglas de metodologias de estudio
        mediante busqueda semantica en ChromaDB.

        Consulta el corpus metodologico global.
        Devuelve fragmentos, fuentes y paginas.
        """

        try:
            resultados = buscar_conocimiento(
                consulta=consulta,
                categoria="metodologia",
                sesion_id="dominio-global",
                cantidad=4,
                fuente=fuente,
            )

            return json.dumps(
                resultados,
                ensure_ascii=False,
            )

        except Exception as error:
            return json.dumps(
                {
                    "estado": "error",
                    "mensaje": str(error),
                },
                ensure_ascii=False,
            )

    return consultar_conocimiento


def nombre_seguro(texto: str) -> str:
    """Convierte un nombre en una parte segura del archivo."""

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "_", texto)

    return texto.strip("_")[:50] or "Materia"


def guardar_plan_csv(
    cronograma: dict,
    materia: str = "Materia",
) -> str:
    """Exporta el cronograma con columnas legibles."""

    carpeta = BASE / "outputs"
    carpeta.mkdir(parents=True, exist_ok=True)

    metodologia = cronograma.get(
        "metodologia", "General"
    )

    nombre_base = (
        f"Cronograma_{nombre_seguro(materia)}_"
        f"{nombre_seguro(metodologia)}_"
        f"{date.today().isoformat()}"
    )

    nombre = f"{nombre_base}.csv"
    ruta = carpeta / nombre
    numero = 2

    while ruta.exists():
        nombre = f"{nombre_base}_{numero}.csv"
        ruta = carpeta / nombre
        numero += 1

    es_pomodoro = metodologia.lower() == "pomodoro"

    es_espaciada = (
        metodologia.lower() == "repeticion espaciada"
    )

    encabezados = [
        "Fecha",
        "Unidad o tema",
        "Actividad",
        "Duracion (minutos)",
    ]

    if es_pomodoro:
        encabezados += [
            "Ciclos Pomodoro",
            "Estudio (min)",
            "Descanso (min)",
            "Descansos largos",
        ]

    if es_espaciada:
        encabezados += [
            "Repaso programado",
            "Fecha ideal del repaso",
        ]

    with ruta.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as archivo:

        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)

        for dia in cronograma["cronograma"]:
            fecha = date.fromisoformat(
                dia["fecha"]
            ).strftime("%d/%m/%Y")

            for actividad in dia["actividades"]:

                duracion = round(
                    actividad["horas"] * 60
                )

                fila = [
                    fecha,
                    actividad["tema"],
                    actividad["actividad"],
                    duracion,
                ]

                if es_pomodoro:
                    fila += [
                        actividad.get("ciclos", 0),
                        actividad.get("minutos_estudio", 0),
                        actividad.get("minutos_descanso", 0),
                        actividad.get("descansos_largos", 0),
                    ]

                if es_espaciada:
                    intervalo = actividad.get(
                        "intervalo_dias"
                    )

                    fecha_objetivo = actividad.get(
                        "fecha_objetivo"
                    )

                    fila += [
                        (
                            f"+{intervalo} dias"
                            if intervalo is not None
                            else "-"
                        ),
                        (
                            date.fromisoformat(
                                fecha_objetivo
                            ).strftime("%d/%m/%Y")
                            if fecha_objetivo
                            else "-"
                        ),
                    ]

                escritor.writerow(fila)

    return nombre



@tool
def generar_plan_estudio(
    disponibilidad_json: str,
    temas: list[str],
    dificultades: list[int],
    metodologia: str,
    materia: str = "Materia",
) -> str:
    """Genera un cronograma de estudio y lo exporta a CSV.

    Utiliza la disponibilidad, los temas y las dificultades.

    Metodologias admitidas:
    - pomodoro: aplica ciclos de estudio y descanso.
    - repeticion_espaciada: programa repasos a 1, 3, 7 y 14 dias.
    - ninguna: genera un cronograma sin metodologia especifica.

    Devuelve un resumen y el nombre del archivo generado.
    """

    try:
        disponibilidad = json.loads(
            disponibilidad_json
        )

        # Normalizar la estructura recibida.
        if isinstance(disponibilidad, list):
            disponibilidad = {
                "dias": disponibilidad,
                "total_horas": sum(
                    float(dia["horas"])
                    for dia in disponibilidad
                ),
            }

        # Validar que tenga el formato esperado.
        if not isinstance(disponibilidad, dict):
            raise ValueError(
                "La disponibilidad debe ser un objeto JSON."
            )

        if "dias" not in disponibilidad:
            raise ValueError(
                "La disponibilidad no contiene la lista de dias."
            )

        if not isinstance(disponibilidad["dias"], list):
            raise ValueError(
                "El campo dias debe ser una lista."
            )

        if not temas:
            raise ValueError(
                "La lista de temas no puede estar vacia."
            )

        if len(temas) != len(dificultades):
            raise ValueError(
                "Cada tema debe tener una dificultad."
            )

        if any(
            type(d) is not int or d < 1 or d > 5
            for d in dificultades
        ):
            raise ValueError(
                "Las dificultades deben ser enteros entre 1 y 5."
            )

        metodo = metodologia.strip().lower()

        if metodo == "pomodoro":

            cronograma = generar_cronograma_base(
                disponibilidad,
                temas,
                dificultades,
            )

            cronograma = aplicar_pomodoro(
                cronograma
            )

        elif metodo == "repeticion_espaciada":

            cronograma = generar_cronograma_espaciado(
                disponibilidad,
                temas,
                dificultades,
            )

        elif metodo == "ninguna":

            cronograma = generar_cronograma_base(
                disponibilidad,
                temas,
                dificultades,
            )

        else:
            raise ValueError(
                "Metodologia no reconocida: "
                + metodologia
            )

        nombre_archivo = guardar_plan_csv(
         cronograma,
         materia=materia,
        )       

        return json.dumps(
            {
                "estado": "correcto",
                "archivo": nombre_archivo,
                "metodologia": metodo,
                "total_horas": cronograma["total_horas"],
                "cantidad_dias": len(
                    cronograma["cronograma"]
                ),
                "horas_por_tema": cronograma.get(
                    "horas_por_tema"
                ),
                "horas_estudio": cronograma.get(
                    "horas_estudio"
                ),
                "horas_repaso": cronograma.get(
                    "horas_repaso"
                ),
                "total_minutos_estudio": cronograma.get(
                    "total_minutos_estudio"
                ),
                "total_minutos_descanso": cronograma.get(
                    "total_minutos_descanso"
                ),
                "total_ciclos": cronograma.get(
                    "total_ciclos"
                ),
                "total_descansos_largos": cronograma.get(
                    "total_descansos_largos"
                ),
                "repasos_programados": cronograma.get(
                    "repasos_programados"
                ),
                "repasos_pendientes": cronograma.get(
                    "repasos_pendientes"
                ),
                "horas_disponibles": cronograma.get(
                    "horas_disponibles"
                ),
                "horas_libres": cronograma.get(
                    "horas_libres"
                ),
            },
            ensure_ascii=False,
        )

    except Exception as error:
        import traceback

        traceback.print_exc()

        return json.dumps(
            {
                "estado": "error",
                "mensaje": str(error),
            },
            ensure_ascii=False,
        )








