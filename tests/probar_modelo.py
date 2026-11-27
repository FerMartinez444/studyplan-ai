
from agent import modelo
from tools import consultar_estrategia

# Asociamos una herramienta al modelo
modelo_con_tools = modelo.bind_tools([
    consultar_estrategia
])

respuesta = modelo_con_tools.invoke(
    "Necesito las reglas de priorizacion "
    "de StudyPlan AI. Consulta la herramienta "
    "consultar_estrategia con la estrategia "
    "'priorizacion'."
)

print("Contenido:", respuesta.content)
print("Herramientas solicitadas:", respuesta.tool_calls)
