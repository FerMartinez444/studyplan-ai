
from agent import agente
from langchain_core.messages import AIMessage, ToolMessage

configuracion = {
    "configurable": {
        "thread_id": "prueba-completa-001"
    }
}

consulta = """
Necesito preparar un examen de Física II.

Fecha de inicio: 2026-11-16
Fecha del examen: 2026-11-30

Disponibilidad:
- Lunes a viernes: 2 horas
- Sábados: 4 horas
- Domingos: 0 horas

Temas y dificultades:
- Inducción: 5
- Inductancia: 3
- Corriente alterna: 2

Consultá las estrategias necesarias,
calculá mi disponibilidad,
generá el cronograma y exportalo a CSV.
"""

try:
    resultado = agente.invoke(
        {
            "messages": [
                {"role": "user", "content": consulta}
            ]
        },
        config=configuracion,
    )

    for mensaje in resultado["messages"]:

        if isinstance(mensaje, AIMessage):

            for llamada in mensaje.tool_calls:
                print("\nHERRAMIENTA SOLICITADA:")
                print("Nombre:", llamada["name"])
                print("Argumentos:", llamada["args"])

            if mensaje.content:
                print("\nRESPUESTA DEL AGENTE:")
                print(mensaje.content)

        elif isinstance(mensaje, ToolMessage):
            print("\nRESULTADO DE TOOL:")
            print("Herramienta:", mensaje.name)
            print(str(mensaje.content)[:1000])

except Exception as error:
    print("\nERROR DURANTE LA EJECUCIÓN:")
    print(error)
