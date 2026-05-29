"""
Generadores de reportes HTML.

Funciones disponibles:
  generar_html_errores_semanticos(errores, ruta)   # << el reporte clave (rubrica)
  generar_html_errores(errores, ruta)              # todos los errores
  generar_html_tokens(tokens, ruta)
  generar_html_tabla_simbolos(tabla, ruta)
  generar_html_tac(quads_formateados, ruta, titulo)
  generar_reportes_completos(ruta_dir, ...)        # genera todo de una

Todos los reportes comparten un CSS consistente y muestran:
  - encabezado con titulo, fecha y conteo
  - tabla principal con columnas alineadas
  - mensaje de "sin datos" cuando aplica
"""

import html
import os
from datetime import datetime


# ----------------------------------------------------------------------
#  CSS comun
# ----------------------------------------------------------------------

_CSS = """
:root {
    --bg: #f7f9fc;
    --card-bg: #ffffff;
    --primary: #1e3c78;
    --primary-light: #2a5bb1;
    --border: #d8deea;
    --text: #1a1a2e;
    --text-muted: #6b7280;
    --lex: #c0392b;
    --sint: #d68910;
    --sem: #8e44ad;
    --ok: #229954;
    --hover: #eef2fb;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 28px;
    font-family: -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.5;
}
.container { max-width: 1100px; margin: 0 auto; }
header {
    background: linear-gradient(135deg, var(--primary), var(--primary-light));
    color: white;
    padding: 22px 26px;
    border-radius: 10px 10px 0 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
header h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 0.2px;
}
header .subtitle {
    opacity: 0.85;
    margin-top: 6px;
    font-size: 13px;
}
.card {
    background: var(--card-bg);
    padding: 22px 26px;
    border-radius: 0 0 10px 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 24px;
}
.summary {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.summary .chip {
    background: var(--hover);
    padding: 8px 14px;
    border-radius: 6px;
    border-left: 4px solid var(--primary);
    font-size: 13px;
}
.summary .chip.lex { border-left-color: var(--lex); }
.summary .chip.sint { border-left-color: var(--sint); }
.summary .chip.sem { border-left-color: var(--sem); }
.summary .chip.ok { border-left-color: var(--ok); }
.summary .chip strong { color: var(--primary); }
.summary .chip.lex strong { color: var(--lex); }
.summary .chip.sint strong { color: var(--sint); }
.summary .chip.sem strong { color: var(--sem); }
.summary .chip.ok strong { color: var(--ok); }
table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    font-size: 13px;
}
thead th {
    background: var(--primary);
    color: white;
    padding: 11px 14px;
    text-align: left;
    font-weight: 500;
    letter-spacing: 0.2px;
}
thead th:first-child { border-radius: 6px 0 0 0; }
thead th:last-child { border-radius: 0 6px 0 0; }
tbody td {
    padding: 9px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
tbody tr:nth-child(even) td { background: #fafbfd; }
tbody tr:hover td { background: var(--hover); }
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: white;
}
.tag.lex  { background: var(--lex); }
.tag.sint { background: var(--sint); }
.tag.sem  { background: var(--sem); }
.code {
    font-family: "JetBrains Mono", Consolas, Menlo, monospace;
    font-size: 12.5px;
    background: #f1f3f8;
    padding: 1px 6px;
    border-radius: 3px;
}
.empty {
    text-align: center;
    padding: 40px 20px;
    color: var(--ok);
    font-size: 15px;
    background: #eaf7ee;
    border-radius: 6px;
    border: 1px dashed var(--ok);
}
.numcol { text-align: right; color: var(--text-muted); width: 60px; }
.linecol { width: 70px; text-align: center; }
.colcol { width: 80px; text-align: center; }
footer {
    margin-top: 18px;
    padding: 16px 20px;
    background: var(--card-bg);
    border-radius: 8px;
    font-size: 12px;
    color: var(--text-muted);
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
"""


def _ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _esc(s):
    return html.escape(str(s)) if s is not None else ""


def _doc(titulo: str, subtitulo: str, contenido: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{_esc(titulo)}</title>
<style>{_CSS}</style>
</head>
<body>
<div class="container">
<header>
    <h1>{_esc(titulo)}</h1>
    <div class="subtitle">{_esc(subtitulo)} &middot; Generado: {_ahora()}</div>
</header>
<div class="card">
{contenido}
</div>
<footer>Compilador Fase 2 &middot; Reporte automatico</footer>
</div>
</body>
</html>"""


# ----------------------------------------------------------------------
# 1) REPORTE DE ERRORES SEMANTICOS  (clave para la rubrica - 20 pts)
# ----------------------------------------------------------------------

def generar_html_errores_semanticos(errores_semanticos, ruta_salida):
    """
    Genera un reporte HTML especifico para errores semanticos, con
    linea y columna para cada uno. Es el entregable principal segun
    la rubrica.

    errores_semanticos: lista de dicts {tipo, descripcion, linea, columna, valor}
    """
    total = len(errores_semanticos)

    if total == 0:
        contenido = '<div class="empty">No se detectaron errores semanticos. El analisis paso correctamente.</div>'
    else:
        # Estadistica por tipo de error
        cuenta_por_categoria = {}
        for e in errores_semanticos:
            desc = e.get("descripcion", "")
            categoria = _categorizar(desc)
            cuenta_por_categoria[categoria] = cuenta_por_categoria.get(categoria, 0) + 1

        chips = ['<div class="chip sem">Total: <strong>{}</strong></div>'.format(total)]
        for cat, n in sorted(cuenta_por_categoria.items(), key=lambda x: -x[1]):
            chips.append(f'<div class="chip">{_esc(cat)}: <strong>{n}</strong></div>')

        filas = ""
        errores_ord = sorted(
            errores_semanticos,
            key=lambda e: (e.get("linea", 0), e.get("columna", 0)),
        )
        for i, e in enumerate(errores_ord, 1):
            valor = e.get("valor", "")
            valor_html = f'<span class="code">{_esc(valor)}</span>' if valor else "—"
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="tag sem">Semantico</span></td>
                <td class="linecol">{_esc(e.get('linea', '—'))}</td>
                <td class="colcol">{_esc(e.get('columna', '—'))}</td>
                <td>{valor_html}</td>
                <td>{_esc(e.get('descripcion', ''))}</td>
            </tr>"""

        contenido = f"""
        <div class="summary">{''.join(chips)}</div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Tipo</th>
                    <th class="linecol">Linea</th>
                    <th class="colcol">Columna</th>
                    <th>Identificador / Valor</th>
                    <th>Descripcion</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc(
        "Reporte de Errores Semanticos",
        f"Analisis estatico de tipos, declaraciones y reglas semanticas",
        contenido,
    )
    _escribir(ruta_salida, doc)
    return ruta_salida


def generar_html_errores_lexicos(errores_lexicos, ruta_salida):
    """
    Genera un reporte HTML especifico para errores lexicos (caracteres
    ilegales, lexemas no reconocidos, etc.) con linea y columna.

    errores_lexicos: lista de dicts {tipo, descripcion, linea, columna, valor}
    """
    total = len(errores_lexicos)

    if total == 0:
        contenido = '<div class="empty">No se detectaron errores lexicos. El analisis lexico paso correctamente.</div>'
    else:
        # Estadistica por caracter ofensor
        cuenta_por_valor = {}
        for e in errores_lexicos:
            v = e.get("valor", "?") or "?"
            cuenta_por_valor[v] = cuenta_por_valor.get(v, 0) + 1

        chips = [f'<div class="chip lex">Total: <strong>{total}</strong></div>']
        for v, n in sorted(cuenta_por_valor.items(), key=lambda x: -x[1]):
            chips.append(
                f'<div class="chip">Caracter <span class="code">{_esc(v)}</span>: '
                f'<strong>{n}</strong></div>'
            )

        filas = ""
        errores_ord = sorted(
            errores_lexicos,
            key=lambda e: (e.get("linea", 0), e.get("columna", 0)),
        )
        for i, e in enumerate(errores_ord, 1):
            valor = e.get("valor", "")
            valor_html = f'<span class="code">{_esc(valor)}</span>' if valor else "—"
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="tag lex">Lexico</span></td>
                <td class="linecol">{_esc(e.get('linea', '—'))}</td>
                <td class="colcol">{_esc(e.get('columna', '—'))}</td>
                <td>{valor_html}</td>
                <td>{_esc(e.get('descripcion', ''))}</td>
            </tr>"""

        contenido = f"""
        <div class="summary">{''.join(chips)}</div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Tipo</th>
                    <th class="linecol">Linea</th>
                    <th class="colcol">Columna</th>
                    <th>Caracter / Lexema</th>
                    <th>Descripcion</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc(
        "Reporte de Errores Lexicos",
        "Caracteres y lexemas no reconocidos durante el analisis lexico",
        contenido,
    )
    _escribir(ruta_salida, doc)
    return ruta_salida


def generar_html_errores_sintacticos(errores_sintacticos, ruta_salida):
    """
    Genera un reporte HTML especifico para errores sintacticos (tokens
    inesperados, estructura gramatical invalida) con linea y columna.

    errores_sintacticos: lista de dicts {tipo, descripcion, linea, columna, valor}
    """
    total = len(errores_sintacticos)

    if total == 0:
        contenido = '<div class="empty">No se detectaron errores sintacticos. La gramatica del programa es correcta.</div>'
    else:
        chips = [f'<div class="chip sint">Total: <strong>{total}</strong></div>']

        filas = ""
        errores_ord = sorted(
            errores_sintacticos,
            key=lambda e: (e.get("linea", 0), e.get("columna", 0)),
        )
        for i, e in enumerate(errores_ord, 1):
            valor = e.get("valor", "")
            valor_html = f'<span class="code">{_esc(valor)}</span>' if valor else "—"
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="tag sint">Sintactico</span></td>
                <td class="linecol">{_esc(e.get('linea', '—'))}</td>
                <td class="colcol">{_esc(e.get('columna', '—'))}</td>
                <td>{valor_html}</td>
                <td>{_esc(e.get('descripcion', ''))}</td>
            </tr>"""

        contenido = f"""
        <div class="summary">{''.join(chips)}</div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Tipo</th>
                    <th class="linecol">Linea</th>
                    <th class="colcol">Columna</th>
                    <th>Token / Lexema</th>
                    <th>Descripcion</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc(
        "Reporte de Errores Sintacticos",
        "Tokens inesperados o estructura gramatical invalida",
        contenido,
    )
    _escribir(ruta_salida, doc)
    return ruta_salida


def _categorizar(descripcion: str) -> str:
    """Clasifica un mensaje de error semantico en una categoria amigable."""
    d = descripcion.lower()
    if "no declarada" in d:
        return "Variable no declarada"
    if "ya fue declarada" in d:
        return "Variable duplicada"
    if "asignacion incompatible" in d:
        return "Tipo incompatible"
    if "division por cero" in d:
        return "Division por cero"
    if "condicion" in d and "booleana" in d:
        return "Condicion no booleana"
    if "logica" in d or "logico" in d:
        return "Operacion logica invalida"
    if "aritmetica" in d:
        return "Aritmetica invalida"
    if "comparacion" in d:
        return "Comparacion invalida"
    if "operador" in d:
        return "Operador unario invalido"
    return "Otro"


# ----------------------------------------------------------------------
# 2) REPORTE DE TODOS LOS ERRORES
# ----------------------------------------------------------------------

def generar_html_errores(errores, ruta_salida):
    """Reporte unificado de errores lexicos, sintacticos y semanticos."""
    lex = [e for e in errores if e.get("tipo") == "Lexico"]
    sint = [e for e in errores if e.get("tipo") == "Sintactico"]
    sem = [e for e in errores if e.get("tipo") == "Semantico"]
    total = len(errores)

    if total == 0:
        contenido = '<div class="empty">No se detectaron errores. El analisis paso correctamente.</div>'
    else:
        chips = [
            f'<div class="chip lex">Lexicos: <strong>{len(lex)}</strong></div>',
            f'<div class="chip sint">Sintacticos: <strong>{len(sint)}</strong></div>',
            f'<div class="chip sem">Semanticos: <strong>{len(sem)}</strong></div>',
            f'<div class="chip">Total: <strong>{total}</strong></div>',
        ]

        ordenados = sorted(errores, key=lambda e: (e.get("linea", 0), e.get("columna", 0)))
        filas = ""
        for i, e in enumerate(ordenados, 1):
            tag = e.get("tipo", "").lower()[:3]
            valor = e.get("valor", "")
            valor_html = f'<span class="code">{_esc(valor)}</span>' if valor else "—"
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="tag {tag}">{_esc(e.get('tipo', ''))}</span></td>
                <td class="linecol">{_esc(e.get('linea', '—'))}</td>
                <td class="colcol">{_esc(e.get('columna', '—'))}</td>
                <td>{valor_html}</td>
                <td>{_esc(e.get('descripcion', ''))}</td>
            </tr>"""

        contenido = f"""
        <div class="summary">{''.join(chips)}</div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Tipo</th>
                    <th class="linecol">Linea</th>
                    <th class="colcol">Columna</th>
                    <th>Valor</th>
                    <th>Descripcion</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc(
        "Bitacora de Errores",
        f"Lexicos, sintacticos y semanticos detectados durante el analisis",
        contenido,
    )
    _escribir(ruta_salida, doc)
    return ruta_salida


# ----------------------------------------------------------------------
# 3) REPORTE DE TOKENS
# ----------------------------------------------------------------------

def generar_html_tokens(tokens, ruta_salida):
    total = len(tokens)
    if total == 0:
        contenido = '<div class="empty">No se reconocieron tokens.</div>'
    else:
        filas = ""
        for i, t in enumerate(tokens, 1):
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="code">{_esc(t.get('valor', ''))}</span></td>
                <td>{_esc(t.get('tipo', ''))}</td>
                <td class="linecol">{_esc(t.get('linea', '—'))}</td>
                <td class="colcol">{_esc(t.get('columna', '—'))}</td>
            </tr>"""
        contenido = f"""
        <div class="summary">
            <div class="chip">Total de tokens: <strong>{total}</strong></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Lexema</th>
                    <th>Tipo</th>
                    <th class="linecol">Linea</th>
                    <th class="colcol">Columna</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc("Reporte de Tokens", "Salida del analisis lexico", contenido)
    _escribir(ruta_salida, doc)
    return ruta_salida


# ----------------------------------------------------------------------
# 4) REPORTE DE TABLA DE SIMBOLOS
# ----------------------------------------------------------------------

def generar_html_tabla_simbolos(tabla, ruta_salida):
    simbolos = tabla.todos_los_simbolos() if hasattr(tabla, "todos_los_simbolos") else list(tabla)
    total = len(simbolos)

    if total == 0:
        contenido = '<div class="empty">No se declararon variables.</div>'
    else:
        filas = ""
        for i, s in enumerate(simbolos, 1):
            valor = s.valor if s.valor is not None else "—"
            kind = getattr(s, "kind", "variable")
            tipo = s.tipo
            if kind == "array":
                tipo = f"array [size: {getattr(s, 'size', '—')} of {getattr(s, 'elem_type', '—')}]"
            elif kind == "function":
                params = getattr(s, "params", []) or []
                if isinstance(params, list):
                    params = ", ".join(f"{p.get('tipo', '?')} {p.get('nombre', '?')}" for p in params)
                tipo = f"function ({params}) -> {getattr(s, 'return_type', 'void')}"
            filas += f"""
            <tr>
                <td class="numcol">{i}</td>
                <td><span class="code">{_esc(s.nombre)}</span></td>
                <td>{_esc(tipo)}</td>
                <td>{_esc(valor)}</td>
                <td class="linecol">{_esc(s.linea)}</td>
            </tr>"""
        contenido = f"""
        <div class="summary">
            <div class="chip">Total de simbolos: <strong>{total}</strong></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Nombre</th>
                    <th>Tipo de dato</th>
                    <th>Valor</th>
                    <th class="linecol">Linea</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc("Tabla de Simbolos", "Variables declaradas en el programa", contenido)
    _escribir(ruta_salida, doc)
    return ruta_salida


# ----------------------------------------------------------------------
# 5) REPORTE DE TAC (codigo de tres direcciones)
# ----------------------------------------------------------------------

def generar_html_tac(quads_formateados, ruta_salida, titulo="Codigo de Tres Direcciones"):
    """
    quads_formateados: lista de dicts producida por intermedio.formatear_tac()
        cada uno tiene {n, instruccion, op, arg1, arg2, dest, etiqueta}
    """
    total = len(quads_formateados)
    if total == 0:
        contenido = '<div class="empty">No se genero codigo intermedio.</div>'
    else:
        filas = ""
        for f in quads_formateados:
            filas += f"""
            <tr>
                <td class="numcol">{_esc(f.get('n', ''))}</td>
                <td><span class="code">{_esc(f.get('op', ''))}</span></td>
                <td>{_esc(f.get('arg1', '—'))}</td>
                <td>{_esc(f.get('arg2', '—'))}</td>
                <td>{_esc(f.get('dest', '—'))}</td>
                <td><span class="code">{_esc(f.get('instruccion', ''))}</span></td>
            </tr>"""
        contenido = f"""
        <div class="summary">
            <div class="chip">Cuadruplos: <strong>{total}</strong></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th class="numcol">#</th>
                    <th>Op</th>
                    <th>Arg1</th>
                    <th>Arg2</th>
                    <th>Destino</th>
                    <th>Instruccion</th>
                </tr>
            </thead>
            <tbody>{filas}</tbody>
        </table>"""

    doc = _doc(titulo, "Salida del generador de codigo intermedio", contenido)
    _escribir(ruta_salida, doc)
    return ruta_salida


# ----------------------------------------------------------------------
#   Helpers
# ----------------------------------------------------------------------

def _escribir(ruta, contenido):
    directorio = os.path.dirname(ruta)
    if directorio and not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)


def generar_reportes_completos(directorio, *, tokens=None, tabla=None,
                                errores=None, tac=None, tac_opt=None):
    """
    Genera TODOS los reportes en el directorio indicado.
    Retorna un dict con las rutas absolutas de los reportes generados.
    """
    if not os.path.exists(directorio):
        os.makedirs(directorio, exist_ok=True)

    rutas = {}

    # Errores separados por categoria + combinado
    if errores is not None:
        lexicos = [e for e in errores if e.get("tipo") == "Lexico"]
        sintacticos = [e for e in errores if e.get("tipo") == "Sintactico"]
        semanticos = [e for e in errores if e.get("tipo") == "Semantico"]
        rutas["lexicos"] = generar_html_errores_lexicos(
            lexicos, os.path.join(directorio, "reporte_errores_lexicos.html")
        )
        rutas["sintacticos"] = generar_html_errores_sintacticos(
            sintacticos, os.path.join(directorio, "reporte_errores_sintacticos.html")
        )
        rutas["semanticos"] = generar_html_errores_semanticos(
            semanticos, os.path.join(directorio, "reporte_errores_semanticos.html")
        )
        rutas["errores"] = generar_html_errores(
            errores, os.path.join(directorio, "reporte_errores.html")
        )

    if tokens is not None:
        rutas["tokens"] = generar_html_tokens(
            tokens, os.path.join(directorio, "reporte_tokens.html")
        )

    if tabla is not None:
        rutas["tabla_simbolos"] = generar_html_tabla_simbolos(
            tabla, os.path.join(directorio, "reporte_tabla_simbolos.html")
        )

    if tac is not None:
        rutas["tac"] = generar_html_tac(
            tac, os.path.join(directorio, "reporte_tac.html"),
            titulo="Codigo de Tres Direcciones (Original)",
        )

    if tac_opt is not None:
        rutas["tac_opt"] = generar_html_tac(
            tac_opt, os.path.join(directorio, "reporte_tac_optimizado.html"),
            titulo="Codigo de Tres Direcciones (Optimizado)",
        )

    return rutas
