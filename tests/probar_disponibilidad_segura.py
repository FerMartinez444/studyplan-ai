from planning import calcular_disponibilidad_base

from disponibilidad_segura import (
    registrar_disponibilidad,
    recuperar_disponibilidad,
)

sesion = "prueba-disponibilidad"

datos = calcular_disponibilidad_base(
    "2026-11-26",
    "2026-12-15",
    [2, 2, 2, 2, 2, 4, 0],
)

identificador = registrar_disponibilidad(
    sesion,
    datos,
)

recuperados = recuperar_disponibilidad(
    sesion,
    identificador,
)

assert recuperados == datos
assert recuperados["total_horas"] == 38
assert len(recuperados["dias"]) == 16

# Otra sesion no puede recuperar esos datos.
try:
    recuperar_disponibilidad(
        "otra-sesion",
        identificador,
    )
    raise AssertionError("Fallo el aislamiento.")
except ValueError:
    pass

print("Disponibilidad almacenada correctamente.")
print("Dias:", len(recuperados["dias"]))
print("Horas:", recuperados["total_horas"])
print("Identificador:", identificador)
print("Prueba correcta.")
