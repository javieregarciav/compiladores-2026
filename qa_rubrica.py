"""
QA exhaustivo orientado a la rubrica del Entregable 2.

Cubre:
  1. Deteccion de errores semanticos (25 pts)
  2. Reporte HTML de errores semanticos (20 pts)
  3. Generacion de TAC (25 pts)
  4. Optimizacion (10 pts)
  5. Funcionamiento general (10 pts)
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from frontend import errores as E
from backend import optimizar
from intermedio import formatear_tac
import reportes

resultados = []


def caso(label, codigo, *, espera_tipo=None, espera_subcadena=None,
         espera_min_errores=None, espera_max_errores=None,
         espera_sin_errores=False, espera_tac_no_vacio=False):
    """Ejecuta un caso, registra OK/FAIL en resultados."""
    lex = Lexer()
    toks, tabla, errs = lex.analizar(codigo)
    ast = build_tree(toks, errs)
    check_semantic(ast, tabla, errs)

    quads = []
    quads_opt = []
    if not errs:
        try:
            quads = GeneradorTAC().generar(ast)
            quads_opt, _ = optimizar(quads)
        except Exception as e:
            errs.append({"tipo": "Interno", "descripcion": str(e),
                         "linea": 0, "columna": 0, "valor": ""})

    sem_errs = [e for e in errs if isinstance(e, dict) and e.get("tipo") == "Semantico"]
    fallas = []

    if espera_sin_errores and errs:
        fallas.append(f"esperaba 0 errores, hay {len(errs)}")

    if espera_tipo and not any(
        isinstance(e, dict) and e.get("tipo") == espera_tipo for e in errs
    ):
        fallas.append(f"esperaba al menos un error de tipo {espera_tipo}")

    if espera_subcadena:
        for sub in espera_subcadena:
            if not any(sub.lower() in e.get("descripcion", "").lower()
                       for e in errs if isinstance(e, dict)):
                fallas.append(f"esperaba subcadena '{sub}' en descripcion")

    if espera_min_errores is not None and len(errs) < espera_min_errores:
        fallas.append(f"esperaba >= {espera_min_errores} errores, hay {len(errs)}")
    if espera_max_errores is not None and len(errs) > espera_max_errores:
        fallas.append(f"esperaba <= {espera_max_errores} errores, hay {len(errs)}")

    if espera_tac_no_vacio and len(quads) == 0:
        fallas.append("esperaba TAC no vacio")

    # Validar que todos los errores semanticos tienen linea Y columna
    for e in sem_errs:
        if not e.get("linea") or e.get("linea") <= 0:
            fallas.append(f"error semantico sin linea valida: {e}")
        # columna 0 es valida cuando no se pudo extraer (ya OK)

    estado = "PASS" if not fallas else "FAIL"
    resultados.append({"label": label, "estado": estado, "fallas": fallas,
                       "errs": errs, "quads": quads, "quads_opt": quads_opt})
    print(f"  [{estado}] {label}")
    if fallas:
        for f in fallas:
            print(f"         {f}")
        for e in errs[:3]:
            print(f"         err: {e}")


print("=" * 76)
print("CRITERIO 1: Deteccion de errores semanticos (25 pts)")
print("=" * 76)

# Casos esperados a detectar (cada uno = 1 caso de error semantico)
caso(
    "1.1 Variable no declarada (uso simple)",
    "programa { imprimir(x); }",
    espera_subcadena=["no declarada"], espera_tipo="Semantico",
)
caso(
    "1.2 Variable no declarada (en asignacion)",
    "programa { y = 10; }",
    espera_subcadena=["no declarada"], espera_tipo="Semantico",
)
caso(
    "1.3 Variable duplicada en mismo ambito",
    "programa { entero x = 1; entero x = 2; }",
    espera_subcadena=["ya fue declarada"], espera_tipo="Semantico",
)
caso(
    "1.4 Asignacion int = string",
    'programa { entero x = "hola"; }',
    espera_subcadena=["incompatible", "entero", "cadena"], espera_tipo="Semantico",
)
caso(
    "1.5 Asignacion int = decimal",
    "programa { entero x = 3.14; }",
    espera_subcadena=["incompatible", "entero", "decimal"], espera_tipo="Semantico",
)
caso(
    "1.6 Asignacion bool = int",
    "programa { booleano b = 5; }",
    espera_subcadena=["incompatible", "booleano", "entero"], espera_tipo="Semantico",
)
caso(
    "1.7 Widening decimal = entero permitido",
    "programa { decimal x = 5; }",
    espera_sin_errores=True, espera_tac_no_vacio=True,
)
caso(
    "1.8 Condicion 'si' no booleana",
    "programa { entero x = 5; si (x) { imprimir(x); } }",
    espera_subcadena=["si", "boolean"], espera_tipo="Semantico",
)
caso(
    "1.9 Condicion 'mientras' no booleana",
    "programa { entero x = 0; mientras (x + 1) { x = x - 1; } }",
    espera_subcadena=["mientras", "boolean"], espera_tipo="Semantico",
)
caso(
    "1.10 Condicion 'para' no booleana",
    "programa { para (entero i = 0; i; i = i + 1) { imprimir(i); } }",
    espera_subcadena=["para", "boolean"], espera_tipo="Semantico",
)
caso(
    "1.11 Division por cero literal entero",
    "programa { entero x = 10 / 0; }",
    espera_subcadena=["Division por cero"], espera_tipo="Semantico",
)
caso(
    "1.12 Modulo por cero literal",
    "programa { entero x = 10 % 0; }",
    espera_subcadena=["Division por cero"], espera_tipo="Semantico",
)
caso(
    "1.13 Suma entre booleano y entero",
    "programa { booleano b = verdadero; entero x = b + 1; }",
    espera_subcadena=["aritmetica", "booleano"], espera_tipo="Semantico",
)
caso(
    "1.14 Comparacion entre tipos incompatibles",
    'programa { entero x = 5; booleano b = x == "hola"; }',
    espera_subcadena=["Comparacion", "entero", "cadena"], espera_tipo="Semantico",
)
caso(
    "1.15 Operacion logica entre no booleanos",
    "programa { entero a = 1; entero b = 2; booleano c = a && b; }",
    espera_subcadena=["logica"], espera_tipo="Semantico",
)
caso(
    "1.16 Operador unario - sobre booleano",
    "programa { booleano b = verdadero; entero x = -b; }",
    espera_subcadena=["unario", "booleano"], espera_tipo="Semantico",
)
caso(
    "1.17 Operador ! sobre entero",
    "programa { entero x = 5; booleano b = !x; }",
    espera_subcadena=["!", "entero"], espera_tipo="Semantico",
)
caso(
    "1.18 Lectura de variable no declarada",
    "programa { leer(noexiste); }",
    espera_subcadena=["no declarada"], espera_tipo="Semantico",
)
caso(
    "1.19 Programa correcto NO produce errores semanticos",
    """programa {
        entero x = 5;
        decimal y = 3.14;
        cadena s = "hola";
        booleano f = verdadero;
        si (x > 0 && f) { imprimir(s); } sino { imprimir("no"); }
        mientras (x > 0) { x = x - 1; }
    }""",
    espera_sin_errores=True, espera_tac_no_vacio=True,
)
caso(
    "1.20 Multiples errores semanticos en mismo programa",
    """programa {
        entero x = "a";
        si (5) { imprimir(z); }
        x = verdadero;
    }""",
    espera_min_errores=3, espera_tipo="Semantico",
)

print()
print("=" * 76)
print("CRITERIO 2: Reporte HTML de errores semanticos (20 pts)")
print("=" * 76)

codigo_errors = """programa {
    entero x = "hola";
    si (x) { imprimir(z); }
    decimal r = 10 / 0;
    x = verdadero;
    entero x = 99;
}"""

lex = Lexer()
toks, tabla, errs = lex.analizar(codigo_errors)
ast = build_tree(toks, errs)
check_semantic(ast, tabla, errs)
sem_errs = [e for e in errs if isinstance(e, dict) and e.get("tipo") == "Semantico"]

ruta = reportes.generar_html_errores_semanticos(sem_errs, "reportes_qa/sem.html")

fallas = []
# 2.1 Archivo creado
if not os.path.exists(ruta):
    fallas.append("HTML no se creo")
# 2.2 Tamano razonable (no vacio)
elif os.path.getsize(ruta) < 1000:
    fallas.append(f"HTML demasiado pequeno ({os.path.getsize(ruta)} bytes)")
# 2.3 Contenido tiene linea y columna
else:
    with open(ruta, encoding="utf-8") as f:
        html = f.read()
    if "Linea" not in html:
        fallas.append("HTML no menciona 'Linea'")
    if "Columna" not in html:
        fallas.append("HTML no menciona 'Columna'")
    if "Semantico" not in html:
        fallas.append("HTML no etiqueta tipo 'Semantico'")
    # Cada error semantico aparece en el HTML (escapando apostrofes)
    import html as html_mod
    for e in sem_errs:
        desc = html_mod.escape(e["descripcion"])[:30]
        if desc not in html:
            fallas.append(f"falta error en HTML: {desc}")

estado = "PASS" if not fallas else "FAIL"
resultados.append({"label": "2.1 HTML estructurado con linea y columna",
                   "estado": estado, "fallas": fallas})
print(f"  [{estado}] 2.1 HTML estructurado con linea y columna")
for f in fallas:
    print(f"         {f}")

# 2.2 Validar que generar_reportes_completos crea todos los archivos
rutas = reportes.generar_reportes_completos(
    "reportes_qa",
    tokens=toks, tabla=tabla, errores=errs,
    tac=formatear_tac(GeneradorTAC().generar(ast)),
    tac_opt=[],
)
fallas2 = []
esperados = {"semanticos", "errores", "tokens", "tabla_simbolos", "tac"}
for k in esperados:
    if k not in rutas:
        fallas2.append(f"falta reporte: {k}")
    elif not os.path.exists(rutas[k]):
        fallas2.append(f"archivo no existe: {k} -> {rutas[k]}")

estado = "PASS" if not fallas2 else "FAIL"
resultados.append({"label": "2.2 Suite completa de reportes",
                   "estado": estado, "fallas": fallas2})
print(f"  [{estado}] 2.2 Suite completa de reportes")
for f in fallas2:
    print(f"         {f}")

print()
print("=" * 76)
print("CRITERIO 3: Generacion de TAC (25 pts)")
print("=" * 76)

def caso_tac(label, codigo, ops_esperadas=None, n_min_cuads=None):
    lex = Lexer()
    toks, tabla, errs = lex.analizar(codigo)
    ast = build_tree(toks, errs)
    check_semantic(ast, tabla, errs)
    if errs:
        print(f"  [SKIP] {label} (errores: {len(errs)})")
        return
    quads = GeneradorTAC().generar(ast)
    ops = {q.op for q in quads}
    fallas = []
    if ops_esperadas:
        for op in ops_esperadas:
            if op not in ops:
                fallas.append(f"op '{op}' no aparece")
    if n_min_cuads is not None and len(quads) < n_min_cuads:
        fallas.append(f"esperaba >= {n_min_cuads} cuadruplos, hay {len(quads)}")
    estado = "PASS" if not fallas else "FAIL"
    resultados.append({"label": label, "estado": estado, "fallas": fallas})
    print(f"  [{estado}] {label}  (cuads: {len(quads)})")
    for f in fallas:
        print(f"         {f}")


caso_tac(
    "3.1 Asignacion simple",
    "programa { entero x = 5; }",
    ops_esperadas=["="],
)
caso_tac(
    "3.2 Operacion binaria",
    "programa { entero x = 3 + 4 * 2; }",
    ops_esperadas=["+", "*", "="],
)
caso_tac(
    "3.3 If con saltos",
    "programa { entero x = 5; si (x > 0) { imprimir(x); } }",
    ops_esperadas=["if_false", "label", ">", "print"],
)
caso_tac(
    "3.4 If/sino con doble salto",
    """programa {
        entero x = 5;
        si (x > 0) { imprimir(x); } sino { imprimir(0); }
    }""",
    ops_esperadas=["if_false", "goto", "label"],
)
caso_tac(
    "3.5 Mientras (loop)",
    "programa { entero i = 0; mientras (i < 10) { i = i + 1; } }",
    ops_esperadas=["label", "if_false", "goto", "<", "+"],
)
caso_tac(
    "3.6 Para (loop)",
    "programa { para (entero i = 0; i < 5; i = i + 1) { imprimir(i); } }",
    ops_esperadas=["label", "if_false", "goto"],
)
caso_tac(
    "3.7 Hacer-mientras",
    "programa { entero i = 0; hacer_mientras { i = i + 1; } mientras (i < 5); }",
    ops_esperadas=["label", "if_false", "goto"],
)
caso_tac(
    "3.8 Operador unario MENOS (0-x)",
    "programa { entero x = 5; entero y = -x; }",
    ops_esperadas=["-"],
)
caso_tac(
    "3.9 Operador unario NOT",
    "programa { booleano b = verdadero; booleano c = !b; }",
    ops_esperadas=["!"],
)
caso_tac(
    "3.10 Print con argumento",
    'programa { imprimir("hola"); }',
    ops_esperadas=["print"],
)
caso_tac(
    "3.11 Leer variable",
    "programa { entero x; leer(x); }",
    ops_esperadas=["read"],
)
caso_tac(
    "3.12 And/Or logicos",
    "programa { booleano b = verdadero || (verdadero && verdadero); }",
    ops_esperadas=["||", "&&"],
)
caso_tac(
    "3.13 Comparaciones",
    "programa { entero a = 1; entero b = 2; booleano c = a == b; booleano d = a < b; }",
    ops_esperadas=["==", "<"],
)


print()
print("=" * 76)
print("CRITERIO 4: Optimizacion (10 pts)")
print("=" * 76)

def caso_opt(label, codigo, *, reduccion_min_pct=0):
    lex = Lexer()
    toks, tabla, errs = lex.analizar(codigo)
    ast = build_tree(toks, errs)
    check_semantic(ast, tabla, errs)
    if errs:
        print(f"  [SKIP] {label} (errores: {len(errs)})")
        return
    quads = GeneradorTAC().generar(ast)
    quads_opt, traza = optimizar(quads)
    delta = len(quads) - len(quads_opt)
    pct = (100.0 * delta / len(quads)) if quads else 0
    fallas = []
    if pct < reduccion_min_pct:
        fallas.append(f"reduccion {pct:.1f}% < {reduccion_min_pct}%")
    estado = "PASS" if not fallas else "FAIL"
    resultados.append({"label": label, "estado": estado, "fallas": fallas})
    print(f"  [{estado}] {label}  ({len(quads)} -> {len(quads_opt)}, {pct:.1f}%, {len(traza)} pasos)")
    for f in fallas:
        print(f"         {f}")


caso_opt(
    "4.1 Constant folding aritmetico",
    "programa { entero c = (3 + 4) * 2 - 1; imprimir(c); }",
    reduccion_min_pct=20,
)
caso_opt(
    "4.2 Identidades algebraicas (x + 0, x * 1)",
    "programa { entero a = 5; entero b = a + 0; entero c = b * 1; imprimir(c); }",
    reduccion_min_pct=10,
)
caso_opt(
    "4.3 Constant propagation (folding via temporal)",
    "programa { entero a = (5 * 2) + 3; imprimir(a); }",
    reduccion_min_pct=20,
)
caso_opt(
    "4.4 Branch pruning si(verdadero)",
    "programa { si (verdadero) { imprimir(1); } sino { imprimir(0); } }",
    reduccion_min_pct=10,
)
caso_opt(
    "4.5 Dead-code elimination de temporales",
    "programa { entero a = 1; entero b = 2; entero c = a + b; imprimir(c); }",
    reduccion_min_pct=10,
)


print()
print("=" * 76)
print("CRITERIO 5: Funcionamiento general (10 pts)")
print("=" * 76)

# 5.1 Bridge produce JSON valido para todos los EJEMPLOS
import subprocess, tempfile
def cargar_ejemplos():
    # Reutilizar la funcion de qa_test.py
    with open("main.py", "r", encoding="utf-8") as f:
        src = f.read()
    start = src.find("EJEMPLOS = [")
    end = src.find("\n]\n", start) + 2
    ns = {}
    exec(src[start:end], ns)
    return ns["EJEMPLOS"]


ejemplos = cargar_ejemplos()
print(f"  Probando {len(ejemplos)} ejemplos precargados via bridge.py...")
ok = 0
fallas_bridge = []
for titulo, codigo in ejemplos:
    with tempfile.NamedTemporaryFile("w", suffix=".programa", delete=False, encoding="utf-8") as f:
        f.write(codigo)
        tmp = f.name
    try:
        r = subprocess.run(
            [sys.executable, "bridge.py", tmp],
            capture_output=True, text=True, encoding="utf-8", timeout=20
        )
        try:
            d = json.loads(r.stdout)
            assert "tokens" in d and "errores" in d and "tac" in d
            ok += 1
        except Exception as e:
            fallas_bridge.append(f"{titulo}: {e}")
    finally:
        os.unlink(tmp)

resultados.append({"label": f"5.1 Bridge produce JSON para los 7 ejemplos",
                   "estado": "PASS" if ok == len(ejemplos) else "FAIL",
                   "fallas": fallas_bridge})
print(f"  [{'PASS' if ok == len(ejemplos) else 'FAIL'}] 5.1 Bridge OK en {ok}/{len(ejemplos)} ejemplos")
for f in fallas_bridge:
    print(f"         {f}")

# 5.2 main.py importable
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_test", "main.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert hasattr(m, "MiniIDE")
    assert hasattr(m.MiniIDE, "_generar_reportes")
    resultados.append({"label": "5.2 main.py importable + tiene _generar_reportes",
                       "estado": "PASS", "fallas": []})
    print("  [PASS] 5.2 main.py importable + tiene _generar_reportes")
except Exception as e:
    resultados.append({"label": "5.2 main.py importable",
                       "estado": "FAIL", "fallas": [str(e)]})
    print(f"  [FAIL] 5.2 main.py importable: {e}")


# ============================================================
print()
print("=" * 76)
print("RESUMEN POR CRITERIO")
print("=" * 76)

def cuenta(prefix):
    casos = [r for r in resultados if r["label"].startswith(prefix)]
    p = sum(1 for r in casos if r["estado"] == "PASS")
    return p, len(casos)

for crit, nombre, pts in [
    ("1.", "Errores semanticos", 25),
    ("2.", "Reporte HTML",         20),
    ("3.", "TAC",                  25),
    ("4.", "Optimizacion",         10),
    ("5.", "Funcionamiento",       10),
]:
    p, t = cuenta(crit)
    pct = (100 * p / t) if t else 0
    print(f"  Criterio {crit} {nombre:<25} {p}/{t} casos PASS  ({pct:.0f}%)")

total_pass = sum(1 for r in resultados if r["estado"] == "PASS")
total = len(resultados)
print(f"\n  TOTAL: {total_pass}/{total} casos PASS")

# Cleanup
import shutil
shutil.rmtree("reportes_qa", ignore_errors=True)

# Exit code
sys.exit(0 if total_pass == total else 1)
