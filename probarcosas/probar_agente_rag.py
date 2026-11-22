from agent import agente
from langchain_core.messages import AIMessage, ToolMessage

configuracion = {
    "configurable": {
        "thread_id": "prueba-agente-rag-001"
    }
}

resultado = agente.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Consulta el RAG y decime qué reglas "
                    "establece el documento pomodoro.pdf "
                    "para organizar los tiempos de estudio "
                    "y descanso. No generes un cronograma."
                )
            }
        ]
    },
    config=configuracion,
)

for mensaje in resultado["messages"]:

    if isinstance(mensaje, AIMessage):

        if mensaje.tool_calls:
            print("\nTOOL CALLS:")
            for llamada in mensaje.tool_calls:
                print("Tool:", llamada["name"])
                print("Argumentos:", llamada["args"])

    elif isinstance(mensaje, ToolMessage):
        print("\nRESULTADO DE TOOL:")
        print(mensaje.content)

print("\nRESPUESTA FINAL:")
print(resultado["messages"][-1].content)