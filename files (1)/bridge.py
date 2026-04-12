#!/usr/bin/env python3
"""
bridge.py
---------
Script puente entre analizar.php y el motor léxico Python.

Uso (llamado por PHP):
    python3 bridge.py <ruta_archivo_temporal>

Lee el código fuente del archivo recibido como argumento,
ejecuta el lexer y la tabla de símbolos, y escribe el resultado
como JSON en stdout para que PHP lo capture con exec().
"""

import sys
import os
import json

# Añadir el directorio del script al path para importar lexer y tabla_simbolos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from lexer import Lexer
except ImportError as e:
    print(json.dumps({
        "tokens":   [],
        "simbolos": [],
        "errores":  [f"Error de importación: {e}. Verifica que lexer.py esté en la misma carpeta."],
    }, ensure_ascii=False))
    sys.exit(0)


def main():
    # ── Verificar argumento ────────────────────────────────────────
    if len(sys.argv) < 2:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  ["bridge.py requiere la ruta del archivo fuente como argumento."],
        }, ensure_ascii=False))
        sys.exit(1)

    ruta = sys.argv[1]

    # ── Leer el código fuente ──────────────────────────────────────
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except Exception as e:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  [f"No se pudo leer el archivo temporal: {e}"],
        }, ensure_ascii=False))
        sys.exit(1)

    # ── Ejecutar el lexer ──────────────────────────────────────────
    try:
        lexer = Lexer()
        tokens_info, tabla, errores = lexer.analizar(codigo)
    except Exception as e:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  [f"Error interno del lexer: {e}"],
        }, ensure_ascii=False))
        sys.exit(0)

    # ── Serializar tabla de símbolos ───────────────────────────────
    simbolos_json = []
    for sim in tabla.todos_los_simbolos():
        simbolos_json.append({
            "nombre": sim.nombre,
            "tipo":   sim.tipo,
            "linea":  sim.linea,
            "valor":  str(sim.valor) if sim.valor is not None else "—",
        })

    # ── Salida JSON ────────────────────────────────────────────────
    resultado = {
        "tokens":   tokens_info,   # lista de {tipo, valor, linea, columna}
        "simbolos": simbolos_json, # lista de {nombre, tipo, linea, valor}
        "errores":  errores,       # lista de strings
    }

    print(json.dumps(resultado, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
