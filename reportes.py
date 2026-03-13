def generar_html_tokens(listaTokens, rutaSalida):
    html = """<!DOCTYPE html><html><body>
<h1>Tokens</h1>
<table border="1">
<tr><th>#</th><th>Lexema</th><th>Tipo de Token</th><th>Linea</th><th>Columna</th></tr>"""
    for i, token in enumerate(listaTokens, 1):
        html += f"<tr><td>{i}</td><td>{token['valor']}</td><td>{token['tipo']}</td><td>{token['linea']}</td><td>{token['columna']}</td></tr>"
    html += "</table></body></html>"
    with open(rutaSalida, 'w', encoding='utf-8') as f:
        f.write(html)


def generar_html_errores(listaErrores, rutaSalida):
    html = """<!DOCTYPE html><html><body><h1>Reporte de Errores</h1>"""
    if not listaErrores:
        html += "<p>No se encontraron errores</p>"
    else:
        html += """<table border="1">
<tr><th>#</th><th>Tipo de Error</th><th>Descripcion</th><th>Linea</th><th>Columna</th></tr>"""
        for i, error in enumerate(listaErrores, 1):
            html += f"<tr><td>{i}</td><td>{error['tipo']}</td><td>{error['descripcion']}</td><td>{error['linea']}</td><td>{error['columna']}</td></tr>"
        html += "</table>"
        lexicos = sum(1 for e in listaErrores if e['tipo'] == 'Lexico')
        sintacticos = sum(1 for e in listaErrores if e['tipo'] == 'Sintactico')
        html += f"<p>Total errores lexicos: {lexicos}, sintacticos: {sintacticos}</p>"
    html += "</body></html>"
    with open(rutaSalida, 'w', encoding='utf-8') as f:
        f.write(html)


def generar_html_tabla_simbolos(tabla, rutaSalida):
    simbolos = tabla.obtener_todos()
    html = """<!DOCTYPE html><html><body><h1>Tabla de Simbolos</h1>"""
    if not simbolos:
        html += "<p>No se encontraron declaraciones de variables</p>"
    else:
        html += """<table border="1">
<tr><th>#</th><th>Nombre</th><th>Tipo de Dato</th><th>Valor</th><th>Linea</th><th>Columna</th></tr>"""
        for i, sim in enumerate(simbolos, 1):
            valor = sim.valor if sim.valor is not None else '-'
            html += f"<tr><td>{i}</td><td>{sim.nombre}</td><td>{sim.tipo}</td><td>{valor}</td><td>{sim.linea}</td><td>{sim.columna}</td></tr>"
        html += "</table>"
        html += f"<p>Total de simbolos: {len(simbolos)}</p>"
    html += "</body></html>"
    with open(rutaSalida, 'w', encoding='utf-8') as f:
        f.write(html)
