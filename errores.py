# errores.py — Manejo de errores léxicos y sintácticos

errores_lexicos = []
errores_sintacticos = []

def agregar_lexico(mensaje, linea, valor=""):
    errores_lexicos.append({
        "tipo": "Léxico",
        "mensaje": mensaje,
        "linea": linea,
        "valor": valor
    })

def agregar_sintactico(mensaje, linea, valor=""):
    errores_sintacticos.append({
        "tipo": "Sintáctico",
        "mensaje": mensaje,
        "linea": linea,
        "valor": valor
    })

def todos():
    return sorted(errores_lexicos + errores_sintacticos, key=lambda e: e["linea"])

def generar_html():
    filas = ""
    for i, e in enumerate(todos(), 1):
        color = "#e74c3c" if e["tipo"] == "Léxico" else "#e67e22"
        filas += f"""
        <tr>
            <td>{i}</td>
            <td style="color:{color};font-weight:bold">{e["tipo"]}</td>
            <td>{e["linea"]}</td>
            <td>{e["valor"]}</td>
            <td>{e["mensaje"]}</td>
        </tr>"""

    if not filas:
        filas = '<tr><td colspan="5" style="color:green">Sin errores</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Bitácora de Errores</title>
    <style>
        body  {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1    {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th    {{ background: #333; color: white; padding: 10px; }}
        td    {{ padding: 8px; border-bottom: 1px solid #ddd; }}
        tr:hover td {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Bitácora de Errores</h1>
    <p>Total: {len(todos())} | Léxicos: {len(errores_lexicos)} | Sintácticos: {len(errores_sintacticos)}</p>
    <table>
        <thead>
            <tr><th>#</th><th>Tipo</th><th>Línea</th><th>Valor</th><th>Mensaje</th></tr>
        </thead>
        <tbody>{filas}</tbody>
    </table>
</body>
</html>"""

def para_reportes():
    """Convierte los errores al formato que espera reportes.py"""
    lista = []
    for e in todos():
        lista.append({
            "tipo": e["tipo"],
            "descripcion": e["mensaje"],
            "linea": e["linea"],
            "columna": 0,
        })
    return lista
