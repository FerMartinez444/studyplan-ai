import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

RUTA_BD = Path(__file__).resolve().parent / "datos" / "memoria.sqlite3"

def crear_checkpointer():
    """
    Crea un chekpointer persistence para el agente.
    Los chekpoints se almacenan en SQLite.
    """

    RUTA_BD.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(
        str(RUTA_BD),
        check_same_thread=False
    )

    return SqliteSaver(conexion)

