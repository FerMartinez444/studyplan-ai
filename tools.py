import csv
import json
from pathlib import Path
from uuid import uuid4
from langchain.tools import tool
from planning import(
    calcular_disponibilidad_base,
    generar_cronograma_base,
)

BASE = Path(__file__).resolve().parent

@tool
def consultar_estrategia(estrategia: str) -> str:
    """Consulta las reglas de planificacion academica.
    Valores admitidos: priorizacion, distribucion y replanificacion.
    """
    try:
        estrategias = {
            "priorizacion",
            "distribucion",
            "replanificacion",
        }

        if estrategia not in estrategias:
            return "ERROR: estrategia no reconocida."

        ruta = BASE / "skills" / f"{estrategia}.md"

        contenido = ruta.read_text(
            encoding="utf-8"
        )

        return f"Fuente: {ruta.name}\n{contenido}"

    except Exception as error:
        return f"ERROR al consultar la skill: {error}"

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

@tool
def generar_cronograma(
    disponibilidad_json: str,
    temas: list[str],
    dificultades: list[int],
) -> str:
    """Genera un cronograma validado.
    Recibe la disponibilidad obtenida de la herramienta calcular_disponibilidad.
    Cada dificultad debe esatr entre 1 y 5.
    """
    try:
        disponibilidad = json.loads(
            disponibilidad_json
        )

        resultado = generar_cronograma_base(
            disponibilidad,
            temas,
            dificultades,
        )

        return json.dumps(
            resultado,
            ensure_ascii=False,
        )
    except Exception as error:
        return f"ERROR: {error}"

@tool
def exportar_cronograma(
    cronograma_json: str,
) -> str:
    """Exporta un cronograma valido a CSV.
    Devuelve el nombre del archivo generado.
    """
    try:
        datos = json.loads(cronograma_json)

        if not isinstance(datos.get("cronograma"), list):
            return "ERROR: cronograma invalido."

        carpeta = BASE / "outputs"
        carpeta.mkdir(exist_ok=True)

        nombre = f"plan_{uuid4().hex[:10]}.csv"
        ruta = carpeta / nombre

        with ruta.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as archivo:
            escritor = csv.writer(archivo)

            escritor.writerow([
                "Fecha",
                "Tema",
                "Actividad",
                "Horas",
            ])

            for dia in datos["cronograma"]:
                for actividad in dia["actividades"]:
                    escritor.writerow([
                        dia["fecha"],
                        actividad["tema"],
                        actividad["actividad"],
                        actividad["horas"],
                    ])
        return json.dumps({
            "archivo": nombre,
            "estado": "exportado",
        })
    except Exception as error:
        return f"ERROR: {error}"