
import sys
import os
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from frontend import Lexer, build_tree, GeneradorTAC, check_semantic
    from intermedio import formatear_tac
    from backend import optimizar
    import reportes as _reportes_mod
except ImportError as e:
    print(json.dumps({
        "tokens":   [],
        "simbolos": [],
        "errores":  [f"Error de importación: {e}. Verifica que las carpetas frontend/ y backend/ estén junto a bridge.py."],
        "tac": [],
        "tac_optimizado": [],
        "metricas": {},
        "traza_optimizacion": [],
    }, ensure_ascii=False))
    sys.exit(0)

def _contar_temps(quads):
    temps = set()
    for q in quads:
        for x in (q.arg1, q.arg2, q.dest):
            if isinstance(x, str) and x.startswith("$t") and x[2:].isdigit():
                temps.add(x)
    return len(temps)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  ["bridge.py requiere la ruta del archivo fuente como argumento."],
            "tac": [],
            "tac_optimizado": [],
            "metricas": {},
            "traza_optimizacion": [],
        }, ensure_ascii=False))
        sys.exit(1)

    ruta = sys.argv[1]
    # Flag opcional: --reportes <dir>
    dir_reportes = None
    if "--reportes" in sys.argv:
        idx = sys.argv.index("--reportes")
        if idx + 1 < len(sys.argv):
            dir_reportes = sys.argv[idx + 1]

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
    except Exception as e:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  [f"No se pudo leer el archivo temporal: {e}"],
            "tac": [],
            "tac_optimizado": [],
            "metricas": {},
            "traza_optimizacion": [],
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        lexer = Lexer()
        tokens_info, tabla, errores = lexer.analizar(codigo)
    except Exception as e:
        print(json.dumps({
            "tokens":   [],
            "simbolos": [],
            "errores":  [f"Error interno del lexer: {e}"],
            "tac": [],
            "tac_optimizado": [],
            "metricas": {},
            "traza_optimizacion": [],
        }, ensure_ascii=False))
        sys.exit(0)

    tac_filas = []
    tac_opt_filas = []
    metricas = {}
    traza = []
    simbolos_json = []

    try:
        ast = build_tree(tokens_info, errores)
        check_semantic(ast, tabla, errores)
        # La tabla se llena en check_semantic (con scopes correctos),
        # asi que recien aca podemos recolectar los simbolos.
        for sim in tabla.todos_los_simbolos():
            simbolos_json.append({
                "nombre": sim.nombre,
                "tipo":   sim.tipo,
                "linea":  sim.linea,
                "valor":  str(sim.valor) if sim.valor is not None else "—",
            })
        # Si hay errores, no generar TAC para no producir instrucciones invalidas
        quads = []
        quads_opt = []
        traza = []
        if not errores:
            quads = GeneradorTAC().generar(ast)
            quads_opt, traza = optimizar(quads)
        tac_filas = formatear_tac(quads)
        tac_opt_filas = formatear_tac(quads_opt)

        cuad_orig = len(quads)
        cuad_opt = len(quads_opt)
        temps_orig = _contar_temps(quads)
        temps_opt = _contar_temps(quads_opt)
        reduccion_pct = (
            round(100.0 * (cuad_orig - cuad_opt) / cuad_orig, 1)
            if cuad_orig else 0.0
        )

        metricas = {
            "cuad_orig":      cuad_orig,
            "cuad_opt":       cuad_opt,
            "reduccion_pct":  reduccion_pct,
            "temps_orig":     temps_orig,
            "temps_opt":      temps_opt,
        }
    except Exception as e:
        errores = list(errores) + [f"Error generando código intermedio: {e}"]

    # Para la UI web/JSON: errores como strings (retrocompat)
    from frontend.errores import fmt as _fmt_err
    errores_str = [_fmt_err(e) if isinstance(e, dict) else str(e) for e in errores]

    rutas_reportes = {}
    if dir_reportes:
        try:
            rutas_reportes = _reportes_mod.generar_reportes_completos(
                dir_reportes,
                tokens=tokens_info,
                tabla=tabla,
                errores=[e for e in errores if isinstance(e, dict)],
                tac=tac_filas,
                tac_opt=tac_opt_filas,
            )
        except Exception as e:
            errores_str.append(f"[Reportes] No se pudo generar: {e}")

    resultado = {
        "tokens":               tokens_info,
        "simbolos":             simbolos_json,
        "errores":              errores_str,
        "errores_estructurados": [e for e in errores if isinstance(e, dict)],
        "tac":                  tac_filas,
        "tac_optimizado":       tac_opt_filas,
        "metricas":             metricas,
        "traza_optimizacion":   traza,
        "reportes":             rutas_reportes,
    }

    print(json.dumps(resultado, ensure_ascii=False))
    sys.exit(0)

if __name__ == "__main__":
    main()
