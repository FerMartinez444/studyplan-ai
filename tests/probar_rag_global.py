
from rag import buscar_conocimiento


print("=== BUSQUEDA POMODORO ===")

resultados = buscar_conocimiento(
    consulta="Cuantos minutos se estudia y descansa con Pomodoro",
    categoria="metodologia",
    sesion_id="dominio-global",
    fuente="pomodoro.pdf",
)

assert resultados, "No se recuperaron fragmentos."

for resultado in resultados:
    print("Fuente:", resultado["fuente"])
    print("Pagina:", resultado["pagina"])
    print("Texto:", resultado["texto"])
    print("---------------------")

print("Prueba correcta.")
