"""
Manejo de errores lexicos, sintacticos y semanticos.

Cada error es un dict con la forma:
    {"tipo": "Lexico"|"Sintactico"|"Semantico",
     "descripcion": str,
     "linea": int,
     "columna": int,
     "valor": str}

El modulo mantiene listas globales que el pipeline reinicia al
empezar cada analisis (Lexer.analizar llama a limpiar()).
"""

errores_lexicos: list[dict] = []
errores_sintacticos: list[dict] = []
errores_semanticos: list[dict] = []


def limpiar():
    """Reinicia el estado de errores. Lo llama Lexer.analizar."""
    errores_lexicos.clear()
    errores_sintacticos.clear()
    errores_semanticos.clear()


def _duplicado(lista, error):
    """True si ya existe un error con misma linea, columna y descripcion."""
    for e in lista:
        if (e["linea"] == error["linea"]
                and e["columna"] == error["columna"]
                and e["descripcion"] == error["descripcion"]):
            return True
    return False


def agregar_lexico(mensaje, linea, columna=0, valor=""):
    e = {
        "tipo": "Lexico",
        "descripcion": mensaje,
        "linea": int(linea or 0),
        "columna": int(columna or 0),
        "valor": str(valor),
    }
    if not _duplicado(errores_lexicos, e):
        errores_lexicos.append(e)


def agregar_sintactico(mensaje, linea, columna=0, valor=""):
    e = {
        "tipo": "Sintactico",
        "descripcion": mensaje,
        "linea": int(linea or 0),
        "columna": int(columna or 0),
        "valor": str(valor),
    }
    if not _duplicado(errores_sintacticos, e):
        errores_sintacticos.append(e)


def agregar_semantico(mensaje, linea, columna=0, valor=""):
    e = {
        "tipo": "Semantico",
        "descripcion": mensaje,
        "linea": int(linea or 0),
        "columna": int(columna or 0),
        "valor": str(valor),
    }
    if not _duplicado(errores_semanticos, e):
        errores_semanticos.append(e)


def todos():
    """Lista combinada ordenada por linea, luego por columna."""
    return sorted(
        errores_lexicos + errores_sintacticos + errores_semanticos,
        key=lambda e: (e["linea"], e["columna"]),
    )


def fmt(e):
    """Formatea un error como string legible (para consola/log)."""
    if not isinstance(e, dict):
        return str(e)
    cat = e.get("tipo", "Error")
    linea = e.get("linea", 0)
    col = e.get("columna", 0)
    msg = e.get("descripcion", "")
    if col and col > 0:
        return f"[{cat}] Linea {linea}, Col {col}: {msg}"
    return f"[{cat}] Linea {linea}: {msg}"


def lista_a_strings(errores):
    return [fmt(e) for e in errores]
