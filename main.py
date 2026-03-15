import sys
import os
from lexer import lexer, tokens, lista_errores, encontrar_columna
from reglas_parser import parser
from tabla_simbolos import TablaSimbolos
from reportes import generar_html_tokens, generar_html_errores, generar_html_tabla_simbolos
import errores

if len(sys.argv) < 2:
    print("Uso: python main.py <archivo>")
    sys.exit(1)

ruta = sys.argv[1]

try: 
    with open(ruta, 'r', encoding='utf-8') as f:
        contenido = f.read()
except FileNotFoundError:
    print(f"Error, no se encontró el siguiente archivo: {ruta}")
    sys.exit(1)

print("Fase de análisis léxico:")
lista_errores.clear()
lexer.lineno = 1
lexer.input(contenido)

lista_tokens = []
while True:
    tok = lexer.token()
    if not tok:
        break
    lista_tokens.append({
        'valor': tok.value,
        'tipo': tok.type,
        'linea': tok.lineno,
        'columna': encontrar_columna(contenido, tok)
    })

print(f"Se encontraron {len(lista_tokens)} tokens")

print("\nFase de análisis sintáctico:")
lexer.lineno = 1
resultado = parser.parse(contenido, lexer=lexer)

errores_lexicos = [e for e in lista_errores if e['tipo'] == 'Lexico']
errores_sintacticos = [e for e in lista_errores if e['tipo'] == 'Sintactico']
for e in errores_lexicos:
    errores.agregar_lexico(e['descripcion'], e['linea'], e['columna'])
for e in errores_sintacticos:
    errores.agregar_sintactico(e['descripcion'], e['linea'], e['columna'])


print(f"Se encontraron {len(errores_lexicos)} errores léxicos")
print(f"Se encontraron {len(errores_sintacticos)} errores sintácticos")

print("\nTabla de símbolos:")
tabla = TablaSimbolos()

tipos_validos = {'ENTERO', 'DECIMAL', 'CADENA_TIPO', 'BOOLEANO'}
for i in range(len(lista_tokens) - 1):
    if lista_tokens[i]['tipo'] in tipos_validos and lista_tokens[i + 1]['tipo'] == 'IDENTIFICADOR':
        tabla.agregar(
            nombre=lista_tokens[i + 1]['valor'],
            tipo=lista_tokens[i]['tipo'],
            linea=lista_tokens[i + 1]['linea'],
            columna=lista_tokens[i + 1]['columna']
        )
print(f"Se encontraron {len(tabla.simbolos)} símbolos")

print("\nResumen de analisis:")
print(f"Total de tokens: {len(lista_tokens)}")
print(f"Total de errores: {len(lista_errores)}")

for e in lista_errores:
    print(f"error: {e['tipo']}, línea: {e['linea']}, columna: {e['columna']}, mensaje: {e['descripcion']}")

print(f"Simbolos: {len(tabla.obtener_todos())}")

for s in tabla.obtener_todos():
    print(f"simbolo: {s.nombre}, tipo: {s.tipo}")

generar_html_tokens(lista_tokens, 'reporte_tokens.html')
generar_html_errores(lista_errores, 'reporte_errores.html')
generar_html_tabla_simbolos(tabla, 'reporte_tabla_simbolos.html')