import json
import sqlite3
import uuid
from pathlib import Path
from math import isfinite

BASE = Path(__file__).resolve().parent
RUTA_BD = BASE / "datos" / "disponibilidad.sqlite3"

def conectar():
    RUTA_BD.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(
        str(RUTA_BD),
        timeout=10,
    )

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS disponibilidades (
            sesion_id TEXT PRIMARY KEY,
            disponibilidad_id TEXT NOT NULL,
            contenido TEXT NOT NULL
        )
    """)

    return conexion

def registrar_disponibilidad(sesion_id: str, datos: dict) -> str:
    """Guarda la disponibilidad calculada por Python."""

    if not sesion_id:
        raise ValueError("La sesion es obligatoria")

    if not isinstance(datos, dict):
        raise ValueError("Disponibilidad invalida.")

    dias = datos.get("dias")
    total = datos.get("total_horas")

    if not isinstance(dias, list) or not dias:
        raise ValueError("No hay dias disponibles.")

    fechas = []

    for dia in dias:
        if not isinstance(dia, dict):
            raise ValueError("Dia invalido.")

        fechas.append(dia["fecha"])
        horas = dia["horas"]

        if(
            not isinstance(horas, (int, float))
            or not isfinite(horas)
            or horas <= 0
            or horas > 24
        ):
            raise ValueError("Horas invalidas.")

        if fechas != sorted(set(fechas)):
            raise ValueError("Fechas duplicadas o desordenadas.")

        horas_calculadas = sum(d["horas"] for d in dias)

        if abs(horas_calculadas - total) > 0.0001:
            raise ValueError("El total de horas no conicide.")

        identificador = str(uuid.uuid4())

        with conectar() as conexion:
            conexion.execute("""
            INSERT OR REPLACE INTO disponibilidades
            (sesion_id, disponibilidad_id, contenido)
            VALUES (?, ?, ?)
            """,(
                sesion_id,
                identificador,
                json.dumps(datos, ensure_ascii=False),
            ))

        return identificador

def recuperar_disponibilidad(
        sesion_id: str,
        disponibilidad_id: str,
) -> dict:
    """Recupera la disponibilidad autorizada en la sesion."""

    with conectar() as conexion:
        fila = conexion.execute("""
            SELECT contenido
            FROM disponibilidades
            WHERE sesion_id = ?
                AND disponibilidad_id = ?
        """, (sesion_id, disponibilidad_id)).fetchone()

    if fila is None:
        raise ValueError(
            "No existe una disponibilidad calculada "
            "para esta sesion e identificador."
        )

    return json.loads(fila[0])

