import csv
import json
from pathlib import Path
from uuid import uuid4
from langchain.tools import tool
from planning import(
    calcular_disponibilidad_base,
    generar_cronograma_base,
    aplicar_pomodoro,
)

from rag import(
    buscar_conocimiento,
    obtener_programa_completo,
)

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

@tool
def generar_cronograma(
    disponibilidad_json: str,
    temas: list[str],
    dificultades: list[int],
    metodologia: str = "ninguna",
    minutos_estudio: int = 25,
    minutos_descanso: int = 5,

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

        if metodologia.lower() == "pomodoro":
            cronograma = aplicar_pomodoro(
                cronograma,
                minutos_estudio,
                minutos_descanso,
            )
        elif metodologia.lower() != "ninguna":
            raise ValueError(
                "Metodologia tovadia no implementada."
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

def crear_tools_rag(sesion_id:str):

    @tool
    def consultar_material(
        consulta:str,
        categoria:str,
        fuente: str = "",
    ) -> str:
        """Consulta documentos del RAG
        por categoria y fuente.
        """

        try:
            resultados = buscar_conocimiento(
                consulta=consulta,
                categoria=categoria,
                sesion_id=sesion_id,
                fuente=fuente,
            )

            return json.dumps(
                resultados,
                ensure_ascii=False,
            )

        except Exception as error:
            return f"ERROR RAG: {error}"

    @tool
    def consultar_programa_completo(
        documento_id: str,
    ) -> str:
        """Recupera todas las paginas de un programa
        previamente cargado. Utilizar cuando sea
        necesario identificar todas sus unidades.
        """

        try:
            programa = obtener_programa_completo(
                sesion_id=sesion_id,
                documento_id=documento_id,
            )

            contenido = json.dumps(
                programa,
                ensure_ascii=False,
            )

            if len(contenido) > 20000:
                return(
                    "ERROR: programa demasiado extenso "
                    "para esta consulta completa. "
                    "Debe procesarse por partes."
                )

            return contenido

        except Exception as error:
            return f"ERROR PROGRAMA: {error}"

    return consultar_material, consultar_programa_completo
