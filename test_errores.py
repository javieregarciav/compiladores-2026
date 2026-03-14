# test_errores.py — Pruebas de errores.py

import errores

# Limpiar antes de probar
errores.errores_lexicos.clear()
errores.errores_sintacticos.clear()

# --- Prueba 1: agregar error léxico ---
errores.agregar_lexico("Carácter no reconocido", linea=3, valor="@")
assert len(errores.errores_lexicos) == 1, "Debería haber 1 error léxico"
print("✔ Error léxico agregado correctamente")

# --- Prueba 2: agregar error sintáctico ---
errores.agregar_sintactico("Se esperaba 'entonces'", linea=7, valor="si")
assert len(errores.errores_sintacticos) == 1, "Debería haber 1 error sintáctico"
print("✔ Error sintáctico agregado correctamente")

# --- Prueba 3: todos() devuelve ambos ---
assert len(errores.todos()) == 2, "Debería haber 2 errores en total"
print("✔ todos() funciona correctamente")

# --- Prueba 4: ordenados por línea ---
errores.agregar_lexico("Otro error", linea=1, valor="$")
lineas = [e["linea"] for e in errores.todos()]
assert lineas == sorted(lineas), "Deben estar ordenados por línea"
print("✔ Ordenamiento por línea correcto")

# --- Prueba 5: generar HTML ---
html = errores.generar_html()
assert "<!DOCTYPE html>" in html, "Debe generar HTML válido"
assert "Léxico" in html, "HTML debe contener errores léxicos"
assert "Sintáctico" in html, "HTML debe contener errores sintácticos"
print("✔ HTML generado correctamente")

# --- Prueba 6: sin errores ---
errores.errores_lexicos.clear()
errores.errores_sintacticos.clear()
html_vacio = errores.generar_html()
assert "Sin errores" in html_vacio, "Debe indicar que no hay errores"
print("✔ HTML sin errores correcto")

print("\n✔ Todas las pruebas pasaron correctamente")
