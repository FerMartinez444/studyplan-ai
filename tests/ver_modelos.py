
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

cliente = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

for modelo in cliente.models.list():
    acciones = getattr(
        modelo,
        "supported_actions",
        []
    ) or []

    if "generateContent" in acciones:
        print(modelo.name)
