"""
QA exhaustivo FINAL del compilador (fase 2 PLY).

Cubre 80+ casos:
  A. Lexico       (caracteres ilegales, comentarios, escapes, edge cases)
  B. Sintactico   (errores de sintaxis con recuperacion)
  C. Semantico    (todos los casos de la rubrica + edge cases)
  D. TAC          (todas las construcciones del lenguaje)
  E. Optimizacion (5 pasadas, punto fijo, casos especificos)
  F. Reportes     (HTML generados, contenido valido)
  G. Pipeline     (bridge.py JSON, qa_test.py original)
  H. Stress       (programas grandes, anidados, edge cases)
  I. Regresion    (no romper lo que ya andaba)

Estado esperado: TODOS PASS.
"""

import sys, os, json, subprocess, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from frontend import errores as E
from backend import optimizar
from intermedio import formatear_tac
import reportes

resultados = []
TEMP_DIR = "_qa_temp"


def analizar(codigo):
    lex = Lexer()
    toks, tabla, errs = lex.analizar(codigo)
    ast = build_tree(toks, errs)
    check_semantic(ast, tabla, errs)
    return toks, tabla, errs, ast


def es_error_tipo(errores, tipo):
    return any(isinstance(e, dict) and e.get("tipo") == tipo for e in errores)


def hay_subcadena(errores, subcadena):
    return any(
        isinstance(e, dict) and subcadena.lower() in e.get("descripcion", "").lower()
        for e in errores
    )


def registrar(label, fallas):
    estado = "PASS" if not fallas else "FAIL"
    resultados.append({"label": label, "estado": estado, "fallas": fallas})
    print(f"  [{estado}] {label}")
    for f in fallas:
        print(f"         {f}")


def caso(label, codigo, *, tipo=None, subcadena=None, min_errs=None,
         max_errs=None, sin_errores=False, tac_no_vacio=False):
    toks, tabla, errs, ast = analizar(codigo)
    quads = []
    quads_opt = []
    if not errs:
        try:
            quads = GeneradorTAC().generar(ast)
            quads_opt, _ = optimizar(quads)
        except Exception as ex:
            errs.append({"tipo": "Interno", "descripcion": str(ex),
                         "linea": 0, "columna": 0, "valor": ""})

    fallas = []
    if sin_errores and errs:
        fallas.append(f"esperaba 0 errores, hay {len(errs)}: "
                      + str([e.get('descripcion', e) for e in errs[:3]]))
    if tipo and not es_error_tipo(errs, tipo):
        fallas.append(f"esperaba error de tipo {tipo}")
    if subcadena:
        for s in (subcadena if isinstance(subcadena, list) else [subcadena]):
            if not hay_subcadena(errs, s):
                fallas.append(f"esperaba subcadena '{s}'")
    if min_errs is not None and len(errs) < min_errs:
        fallas.append(f"esperaba >= {min_errs} errores, hay {len(errs)}")
    if max_errs is not None and len(errs) > max_errs:
        fallas.append(f"esperaba <= {max_errs} errores, hay {len(errs)}")
    if tac_no_vacio and len(quads) == 0:
        fallas.append("esperaba TAC no vacio")
    # Validar que todos los errores semanticos tienen linea > 0
    for e in errs:
        if isinstance(e, dict) and e.get("tipo") == "Semantico":
            if not e.get("linea") or e.get("linea") <= 0:
                fallas.append(f"error semantico sin linea valida")
                break

    registrar(label, fallas)
    return errs, quads, quads_opt


# ==========================================================================
print("=" * 78)
print("BLOQUE A: ANALISIS LEXICO (caracteres ilegales, comentarios, escapes)")
print("=" * 78)
# ==========================================================================

caso("A.1 Caracter ilegal '@'",
     "programa { entero x = 5@; }",
     tipo="Lexico", subcadena=["@"])

caso("A.2 Caracter ilegal '#'",
     "programa { entero x = 3.14#15; }",
     tipo="Lexico", subcadena=["#"])

caso("A.3 Multiples caracteres ilegales",
     "programa { entero @ # $ x = 5; }",
     min_errs=3)

caso("A.4 Comentario de linea no rompe",
     "programa {\n// comentario\nentero x = 5;\n}",
     sin_errores=True)

caso("A.5 Comentario de bloque no rompe",
     "programa { /* comentario\nmultilinea */ entero x = 5; }",
     sin_errores=True)

caso("A.6 Cadena con escape \\n",
     'programa { cadena s = "linea1\\nlinea2"; }',
     sin_errores=True)

caso("A.7 Cadena con escape \\\"",
     'programa { cadena s = "comilla \\"interna\\""; }',
     sin_errores=True)

caso("A.8 Programa vacio (solo programa{})",
     "programa { }",
     sin_errores=True)

caso("A.9 Solo comentarios",
     "// nada\n/* nada */",
     sin_errores=True)

caso("A.10 Decimal y entero juntos",
     "programa { decimal a = 3.14; entero b = 42; }",
     sin_errores=True)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE B: ANALISIS SINTACTICO")
print("=" * 78)
# ==========================================================================

caso("B.1 Falta punto y coma",
     "programa { entero x = 5 }",
     tipo="Sintactico")

caso("B.2 Falta parentesis cierre",
     "programa { si (x > 0 { imprimir(x); } }",
     tipo="Sintactico")

caso("B.3 Falta llave cierre",
     "programa { entero x = 5;",
     tipo="Sintactico")

caso("B.4 Token inesperado",
     "programa { entero = 5; }",
     tipo="Sintactico")

caso("B.5 Sentencia mientras correcta",
     "programa { entero x = 0; mientras (x < 10) { x = x + 1; } }",
     sin_errores=True, tac_no_vacio=True)

caso("B.6 If sin else correcto",
     "programa { entero x = 5; si (x > 0) { imprimir(x); } }",
     sin_errores=True, tac_no_vacio=True)

caso("B.7 If con else correcto",
     "programa { entero x = 5; si (x > 0) { imprimir(x); } sino { imprimir(0); } }",
     sin_errores=True, tac_no_vacio=True)

caso("B.8 Para correcto",
     "programa { para (entero i = 0; i < 5; i = i + 1) { imprimir(i); } }",
     sin_errores=True, tac_no_vacio=True)

caso("B.9 Hacer-mientras correcto",
     "programa { entero x = 0; hacer_mientras { x = x + 1; } mientras (x < 5); }",
     sin_errores=True, tac_no_vacio=True)

caso("B.10 If anidados",
     """programa {
        entero x = 5;
        si (x > 0) {
            si (x > 10) { imprimir(1); } sino { imprimir(2); }
        }
     }""",
     sin_errores=True, tac_no_vacio=True)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE C: SEMANTICO (rubrica - criterio 1)")
print("=" * 78)
# ==========================================================================

caso("C.1 Variable no declarada en uso",
     "programa { imprimir(noexiste); }",
     subcadena="no declarada", tipo="Semantico")

caso("C.2 Variable no declarada en asignacion",
     "programa { y = 5; }",
     subcadena="no declarada", tipo="Semantico")

caso("C.3 Variable no declarada en condicion",
     "programa { si (z > 0) { imprimir(1); } }",
     subcadena="no declarada", tipo="Semantico")

caso("C.4 Variable duplicada",
     "programa { entero x = 1; entero x = 2; }",
     subcadena="ya fue declarada", tipo="Semantico")

caso("C.5 Tipo incompatible: entero = cadena",
     'programa { entero x = "hola"; }',
     subcadena=["entero", "cadena"], tipo="Semantico")

caso("C.6 Tipo incompatible: entero = decimal",
     "programa { entero x = 3.14; }",
     subcadena=["entero", "decimal"], tipo="Semantico")

caso("C.7 Tipo incompatible: booleano = entero",
     "programa { booleano b = 5; }",
     subcadena=["booleano", "entero"], tipo="Semantico")

caso("C.8 Widening decimal = entero permitido",
     "programa { decimal x = 5; }",
     sin_errores=True, tac_no_vacio=True)

caso("C.9 Widening en aritmetica",
     "programa { decimal x = 5; decimal y = x + 2; }",
     sin_errores=True, tac_no_vacio=True)

caso("C.10 Condicion si con entero",
     "programa { entero x = 5; si (x) { imprimir(x); } }",
     subcadena=["si", "boolean"], tipo="Semantico")

caso("C.11 Condicion mientras con entero",
     "programa { entero x = 5; mientras (x + 1) { x = x - 1; } }",
     subcadena=["mientras", "boolean"], tipo="Semantico")

caso("C.12 Condicion para con entero",
     "programa { para (entero i = 0; i; i = i + 1) { imprimir(i); } }",
     subcadena=["para", "boolean"], tipo="Semantico")

caso("C.13 Division por cero entera",
     "programa { entero x = 10 / 0; }",
     subcadena="Division por cero", tipo="Semantico")

caso("C.14 Modulo por cero",
     "programa { entero x = 10 % 0; }",
     subcadena="Division por cero", tipo="Semantico")

caso("C.15 Division por cero decimal",
     "programa { decimal x = 5.0 / 0.0; }",
     subcadena="Division por cero", tipo="Semantico")

caso("C.16 Aritmetica boolean + int",
     "programa { booleano b = verdadero; entero x = b + 1; }",
     subcadena=["aritmetica", "booleano"], tipo="Semantico")

caso("C.17 Comparacion int == string",
     'programa { entero x = 5; booleano b = x == "hi"; }',
     subcadena=["Comparacion"], tipo="Semantico")

caso("C.18 And entre enteros",
     "programa { entero a = 1; entero b = 2; booleano c = a && b; }",
     subcadena=["logica"], tipo="Semantico")

caso("C.19 NOT sobre entero",
     "programa { entero x = 5; booleano b = !x; }",
     subcadena=["!", "entero"], tipo="Semantico")

caso("C.20 MENOS unario sobre booleano",
     "programa { booleano b = verdadero; entero x = -b; }",
     subcadena=["unario", "booleano"], tipo="Semantico")

caso("C.21 Leer variable no declarada",
     "programa { leer(noexiste); }",
     subcadena="no declarada", tipo="Semantico")

caso("C.22 Asignacion en cuerpo del para con var no declarada",
     "programa { para (entero i = 0; i < 5; j = j + 1) { imprimir(i); } }",
     subcadena="no declarada", tipo="Semantico")

caso("C.23 Programa correcto extenso",
     """programa {
        entero a = 5;
        decimal b = 3.14;
        cadena nombre = "test";
        booleano flag = verdadero;
        si (a > 0 && flag) {
            imprimir(nombre);
            mientras (a > 0) { a = a - 1; }
        } sino {
            para (entero i = 0; i < 3; i = i + 1) { imprimir(i); }
        }
     }""",
     sin_errores=True, tac_no_vacio=True)

caso("C.24 Multiples errores semanticos",
     """programa {
        entero x = "a";
        si (5) { imprimir(z); }
        x = verdadero;
        decimal y = 10 / 0;
     }""",
     min_errs=4, tipo="Semantico")

caso("C.25 Variable usada antes de declarar",
     """programa {
        imprimir(x);
        entero x = 5;
     }""",
     subcadena="antes de ser declarada", tipo="Semantico")


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE D: TAC (todas las construcciones)")
print("=" * 78)
# ==========================================================================

def caso_tac(label, codigo, *, ops=None, min_quads=None, exact_quads=None):
    toks, tabla, errs, ast = analizar(codigo)
    if errs:
        registrar(label, [f"errores en analisis: {len(errs)}"])
        return
    quads = GeneradorTAC().generar(ast)
    ops_presentes = {q.op for q in quads}
    fallas = []
    if ops:
        for o in ops:
            if o not in ops_presentes:
                fallas.append(f"falta op '{o}'")
    if min_quads is not None and len(quads) < min_quads:
        fallas.append(f"esperaba >= {min_quads}, hay {len(quads)}")
    if exact_quads is not None and len(quads) != exact_quads:
        fallas.append(f"esperaba {exact_quads}, hay {len(quads)}")
    registrar(f"{label} (q={len(quads)})", fallas)


caso_tac("D.1 Asignacion simple",
         "programa { entero x = 5; }",
         ops=["="], exact_quads=1)

caso_tac("D.2 Operacion binaria + asignacion",
         "programa { entero x = 3 + 4; }",
         ops=["+", "="])

caso_tac("D.3 Operaciones encadenadas",
         "programa { entero x = (1 + 2) * (3 - 4) / 5; }",
         ops=["+", "-", "*", "/"])

caso_tac("D.4 Comparaciones",
         "programa { entero a = 1; entero b = 2; booleano c = a < b; booleano d = a == b; }",
         ops=["<", "=="])

caso_tac("D.5 Operaciones logicas (short-circuit con saltos)",
         "programa { booleano b = verdadero || (verdadero && verdadero); }",
         ops=["if_false", "if_true", "label"])

caso_tac("D.6 Operacion logica NOT",
         "programa { booleano b = verdadero; booleano c = !b; }",
         ops=["!"])

caso_tac("D.7 Unary minus produce 0 - x",
         "programa { entero x = 5; entero y = -x; }",
         ops=["-"])

caso_tac("D.8 If con saltos",
         "programa { entero x = 5; si (x > 0) { imprimir(x); } }",
         ops=["if_false", "label", "print"])

caso_tac("D.9 If/sino doble salto",
         "programa { entero x = 5; si (x > 0) { imprimir(1); } sino { imprimir(2); } }",
         ops=["if_false", "goto", "label", "print"])

caso_tac("D.10 Mientras: label + goto + if_false",
         "programa { entero i = 0; mientras (i < 10) { i = i + 1; } }",
         ops=["label", "if_false", "goto"])

caso_tac("D.11 Para: label + goto + update",
         "programa { para (entero i = 0; i < 5; i = i + 1) { imprimir(i); } }",
         ops=["label", "if_false", "goto"])

caso_tac("D.12 Hacer-mientras",
         "programa { entero i = 0; hacer_mientras { i = i + 1; } mientras (i < 5); }",
         ops=["label", "if_false", "goto"])

caso_tac("D.13 Imprimir literal",
         'programa { imprimir("hola"); }',
         ops=["print"])

caso_tac("D.14 Imprimir variable",
         "programa { entero x = 5; imprimir(x); }",
         ops=["print", "="])

caso_tac("D.15 Imprimir multiples args",
         'programa { entero x = 5; imprimir(x, "valor"); }',
         ops=["print"])

caso_tac("D.16 Leer variable",
         "programa { entero x; leer(x); }",
         ops=["read"])

caso_tac("D.17 Bucle anidado",
         """programa {
            para (entero i = 0; i < 3; i = i + 1) {
                para (entero j = 0; j < 3; j = j + 1) {
                    imprimir(i);
                }
            }
         }""",
         ops=["label", "goto", "if_false"], min_quads=15)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE E: OPTIMIZACION")
print("=" * 78)
# ==========================================================================

def caso_opt(label, codigo, *, reduccion_min=0, traza_min=0):
    toks, tabla, errs, ast = analizar(codigo)
    if errs:
        registrar(label, [f"errores: {len(errs)}"])
        return
    quads = GeneradorTAC().generar(ast)
    quads_opt, traza = optimizar(quads)
    pct = (100.0 * (len(quads) - len(quads_opt)) / len(quads)) if quads else 0
    fallas = []
    if pct < reduccion_min:
        fallas.append(f"reduccion {pct:.1f}% < {reduccion_min}%")
    if len(traza) < traza_min:
        fallas.append(f"esperaba >= {traza_min} pasos en traza, hay {len(traza)}")
    registrar(f"{label} ({len(quads)}->{len(quads_opt)}, {pct:.1f}%, {len(traza)} pasos)",
              fallas)


caso_opt("E.1 Constant folding (3+4)*2",
         "programa { entero c = (3 + 4) * 2 - 1; imprimir(c); }",
         reduccion_min=30, traza_min=2)

caso_opt("E.2 Identidad x+0",
         "programa { entero a = 5; entero b = a + 0; imprimir(b); }",
         reduccion_min=10)

caso_opt("E.3 Identidad x*1",
         "programa { entero a = 5; entero b = a * 1; imprimir(b); }",
         reduccion_min=10)

caso_opt("E.4 Identidad x*0",
         "programa { entero a = 5; entero b = a * 0; imprimir(b); }",
         reduccion_min=10)

caso_opt("E.5 Branch pruning si(verdadero)",
         "programa { si (verdadero) { imprimir(1); } sino { imprimir(2); } }",
         reduccion_min=10)

caso_opt("E.6 Branch pruning si(falso)",
         "programa { si (falso) { imprimir(1); } sino { imprimir(2); } }",
         reduccion_min=10)

caso_opt("E.7 Constant propagation via temporal",
         "programa { entero x = (5 * 2) + 3; imprimir(x); }",
         reduccion_min=20)

caso_opt("E.8 Dead-code elimination",
         "programa { entero a = 1; entero b = 2; entero c = a + b; imprimir(c); }",
         reduccion_min=10)

caso_opt("E.9 Optimizacion compleja: punto fijo",
         """programa {
            entero a = 3;
            entero b = 4;
            entero c = (a + b) * 2;
            entero d = c - 0;
            entero e = d * 1;
            imprimir(e);
         }""",
         reduccion_min=40, traza_min=3)

caso_opt("E.10 Si optimizable a goto",
         "programa { entero x = 0; si (falso) { x = 1; } imprimir(x); }",
         reduccion_min=10)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE F: REPORTES HTML")
print("=" * 78)
# ==========================================================================

os.makedirs(TEMP_DIR, exist_ok=True)

codigo_test = """programa {
    entero x = "hola";
    si (x) { imprimir(z); }
    decimal r = 10 / 0;
    entero x = 99;
    booleano b = 5;
}"""

toks, tabla, errs, ast = analizar(codigo_test)
sem_errs = [e for e in errs if isinstance(e, dict) and e.get("tipo") == "Semantico"]

# F.1 Reporte semantico generado y contenido valido
ruta = reportes.generar_html_errores_semanticos(
    sem_errs, os.path.join(TEMP_DIR, "sem.html"))
fallas = []
if not os.path.exists(ruta):
    fallas.append("HTML no creado")
elif os.path.getsize(ruta) < 2000:
    fallas.append(f"HTML demasiado pequeno ({os.path.getsize(ruta)} bytes)")
else:
    with open(ruta, encoding="utf-8") as f:
        html_txt = f.read()
    for marca in ["<!DOCTYPE html>", "<table>", "Linea", "Columna",
                  "Semantico", "</html>"]:
        if marca not in html_txt:
            fallas.append(f"HTML no contiene: {marca}")
registrar("F.1 Reporte semantico estructurado", fallas)

# F.2 Reporte combinado de errores
ruta2 = reportes.generar_html_errores(
    errs, os.path.join(TEMP_DIR, "err.html"))
fallas = [] if os.path.exists(ruta2) and os.path.getsize(ruta2) > 1000 else \
         ["HTML errores no creado o muy chico"]
registrar("F.2 Reporte combinado de errores", fallas)

# F.3 Reporte de tokens
ruta3 = reportes.generar_html_tokens(toks, os.path.join(TEMP_DIR, "tok.html"))
fallas = [] if os.path.exists(ruta3) and os.path.getsize(ruta3) > 1000 else \
         ["HTML tokens no creado"]
registrar("F.3 Reporte de tokens", fallas)

# F.4 Reporte tabla de simbolos
ruta4 = reportes.generar_html_tabla_simbolos(
    tabla, os.path.join(TEMP_DIR, "sim.html"))
fallas = [] if os.path.exists(ruta4) and os.path.getsize(ruta4) > 1000 else \
         ["HTML tabla no creado"]
registrar("F.4 Reporte tabla de simbolos", fallas)

# F.5 Reporte TAC
codigo_ok = "programa { entero a = 3; entero b = a + 2; imprimir(b); }"
toks2, tabla2, errs2, ast2 = analizar(codigo_ok)
quads = GeneradorTAC().generar(ast2)
ruta5 = reportes.generar_html_tac(formatear_tac(quads),
                                   os.path.join(TEMP_DIR, "tac.html"))
fallas = [] if os.path.exists(ruta5) and os.path.getsize(ruta5) > 1000 else \
         ["HTML TAC no creado"]
registrar("F.5 Reporte TAC", fallas)

# F.6 Suite completa
rutas = reportes.generar_reportes_completos(
    TEMP_DIR + "_full",
    tokens=toks, tabla=tabla, errores=errs,
    tac=formatear_tac(GeneradorTAC().generar(ast)),
    tac_opt=[],
)
esperados = {"semanticos", "errores", "tokens", "tabla_simbolos", "tac"}
faltantes = [k for k in esperados if k not in rutas or not os.path.exists(rutas[k])]
registrar("F.6 Suite completa de reportes",
          [f"falta: {k}" for k in faltantes])

# F.7 HTML escapa caracteres especiales (XSS prevention)
codigo_xss = 'programa { cadena s = "<script>alert(1)</script>"; }'
toks3, tabla3, errs3, ast3 = analizar(codigo_xss)
ruta7 = reportes.generar_html_tokens(toks3, os.path.join(TEMP_DIR, "xss.html"))
with open(ruta7, encoding="utf-8") as f:
    html_xss = f.read()
fallas = []
if "<script>" in html_xss:
    fallas.append("HTML no escapa <script>")
registrar("F.7 HTML escapa XSS", fallas)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE G: PIPELINE (bridge.py + qa_test.py)")
print("=" * 78)
# ==========================================================================

# G.1: Cargar EJEMPLOS de main.py
def cargar_ejemplos():
    with open("main.py", "r", encoding="utf-8") as f:
        src = f.read()
    start = src.find("EJEMPLOS = [")
    end = src.find("\n]\n", start) + 2
    ns = {}
    exec(src[start:end], ns)
    return ns["EJEMPLOS"]


ejemplos = cargar_ejemplos()
print(f"  Probando {len(ejemplos)} ejemplos via bridge.py...")
ok, fallas_b = 0, []
for titulo, codigo in ejemplos:
    with tempfile.NamedTemporaryFile("w", suffix=".programa", delete=False,
                                       encoding="utf-8") as f:
        f.write(codigo); tmp = f.name
    try:
        r = subprocess.run([sys.executable, "bridge.py", tmp],
                            capture_output=True, text=True,
                            encoding="utf-8", timeout=20)
        d = json.loads(r.stdout)
        # Validar claves
        for k in ("tokens", "simbolos", "errores", "tac", "tac_optimizado",
                  "metricas", "traza_optimizacion", "errores_estructurados"):
            if k not in d:
                fallas_b.append(f"{titulo}: falta clave {k}")
                break
        else:
            ok += 1
    except Exception as e:
        fallas_b.append(f"{titulo}: {e}")
    finally:
        os.unlink(tmp)
registrar(f"G.1 Bridge JSON valido en {ok}/{len(ejemplos)} ejemplos", fallas_b)

# G.2 Bridge con --reportes
with tempfile.NamedTemporaryFile("w", suffix=".programa", delete=False,
                                   encoding="utf-8") as f:
    f.write(ejemplos[0][1]); tmp = f.name
try:
    dir_rep = TEMP_DIR + "_bridge_reportes"
    r = subprocess.run([sys.executable, "bridge.py", tmp, "--reportes", dir_rep],
                        capture_output=True, text=True,
                        encoding="utf-8", timeout=20)
    d = json.loads(r.stdout)
    fallas = []
    if "reportes" not in d or len(d["reportes"]) < 4:
        fallas.append(f"reportes no generados via flag")
    if not os.path.exists(dir_rep):
        fallas.append(f"directorio reportes no existe")
    registrar("G.2 Bridge --reportes funciona", fallas)
finally:
    os.unlink(tmp)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE H: STRESS Y EDGE CASES")
print("=" * 78)
# ==========================================================================

# H.1: Programa grande con muchas declaraciones
codigo_grande = "programa {\n"
for i in range(50):
    codigo_grande += f"    entero v{i} = {i};\n"
codigo_grande += "}\n"
toks, tabla, errs, ast = analizar(codigo_grande)
quads = GeneradorTAC().generar(ast) if not errs else []
fallas = []
if errs:
    fallas.append(f"errores inesperados: {len(errs)}")
if len(tabla.todos_los_simbolos()) != 50:
    fallas.append(f"esperaba 50 simbolos, hay {len(tabla.todos_los_simbolos())}")
if len(quads) != 50:
    fallas.append(f"esperaba 50 quads, hay {len(quads)}")
registrar("H.1 Programa con 50 declaraciones", fallas)

# H.2 Expresion profundamente anidada
codigo_anidado = "programa { entero x = ((((((1 + 2) * 3) - 4) / 5) % 6) + 7); }"
toks, tabla, errs, ast = analizar(codigo_anidado)
fallas = [] if not errs else [f"errores: {[e['descripcion'] for e in errs[:3]]}"]
registrar("H.2 Expresion profundamente anidada", fallas)

# H.3 Ifs anidados (4 niveles)
codigo_ifs = """programa {
    entero x = 5;
    si (x > 0) {
        si (x > 1) {
            si (x > 2) {
                si (x > 3) { imprimir(1); }
            }
        }
    }
}"""
toks, tabla, errs, ast = analizar(codigo_ifs)
quads = GeneradorTAC().generar(ast) if not errs else []
fallas = [] if not errs and len(quads) > 10 else \
         [f"errs={len(errs)}, quads={len(quads)}"]
registrar("H.3 Ifs anidados 4 niveles", fallas)

# H.4 Bucles anidados
codigo_loops = """programa {
    para (entero i = 0; i < 3; i = i + 1) {
        para (entero j = 0; j < 3; j = j + 1) {
            mientras (j > 0) {
                imprimir(i);
            }
        }
    }
}"""
toks, tabla, errs, ast = analizar(codigo_loops)
fallas = [] if not errs else [f"errores: {len(errs)}"]
registrar("H.4 Loops triplemente anidados", fallas)

# H.5 Programa minimo
caso("H.5 Programa minimo: solo declaracion",
     "programa { entero x = 1; }",
     sin_errores=True, tac_no_vacio=True)

# H.6 Solo asignacion (sin programa{})
caso("H.6 Sin envoltorio programa{}",
     "entero x = 5;",
     sin_errores=True, tac_no_vacio=True)

# H.7 Cadena vacia
caso("H.7 Cadena vacia",
     'programa { cadena s = ""; }',
     sin_errores=True)


# ==========================================================================
print()
print("=" * 78)
print("BLOQUE I: REGRESION (compatibilidad)")
print("=" * 78)
# ==========================================================================

# I.1: qa_test.py original sigue pasando
print("  Corriendo qa_test.py original...")
r = subprocess.run([sys.executable, "qa_test.py"],
                    capture_output=True, text=True, encoding="utf-8", timeout=60)
fallas = []
if "PASSED" not in r.stdout:
    fallas.append(f"qa_test.py no paso: {r.stdout[-200:]}")
registrar("I.1 qa_test.py original sigue pasando", fallas)

# I.2: test_lexer.py NO se puede ejecutar (es de la version re-pura)
# Lo saltamos a proposito porque la sintaxis cambio
print("  test_lexer.py: SKIP (era para version re-pura, no PLY)")

# I.3: API publica de frontend no cambio
from frontend import (Lexer, TablaSimbolos, Simbolo, build_tree,
                      get_kids, node_label, TIPOS_DATO, RESERVED,
                      GeneradorTAC, check_semantic)
api = [Lexer, TablaSimbolos, Simbolo, build_tree, get_kids, node_label,
       TIPOS_DATO, RESERVED, GeneradorTAC, check_semantic]
fallas = [f"falta {n}" for o, n in zip(api, [
    "Lexer", "TablaSimbolos", "Simbolo", "build_tree", "get_kids",
    "node_label", "TIPOS_DATO", "RESERVED", "GeneradorTAC", "check_semantic"
]) if o is None]
registrar("I.2 API publica de frontend intacta", fallas)


# ============================================================
# RESUMEN
# ============================================================
print()
print("=" * 78)
print("RESUMEN GENERAL")
print("=" * 78)

bloques = [("A.", "Lexico"), ("B.", "Sintactico"), ("C.", "Semantico"),
           ("D.", "TAC"), ("E.", "Optimizacion"), ("F.", "Reportes"),
           ("G.", "Pipeline"), ("H.", "Stress"), ("I.", "Regresion")]

total_pass = 0
total_tests = 0
for prefix, nombre in bloques:
    bloque = [r for r in resultados if r["label"].startswith(prefix)]
    p = sum(1 for r in bloque if r["estado"] == "PASS")
    total_pass += p
    total_tests += len(bloque)
    pct = (100 * p / len(bloque)) if bloque else 0
    icono = "OK" if p == len(bloque) else "!!"
    print(f"  [{icono}] Bloque {prefix} {nombre:<14} {p}/{len(bloque)} PASS  ({pct:.0f}%)")

print()
print(f"  TOTAL: {total_pass}/{total_tests} casos PASS  "
      f"({100*total_pass/total_tests:.1f}%)")

# Cleanup
shutil.rmtree(TEMP_DIR, ignore_errors=True)
shutil.rmtree(TEMP_DIR + "_full", ignore_errors=True)
shutil.rmtree(TEMP_DIR + "_bridge_reportes", ignore_errors=True)

sys.exit(0 if total_pass == total_tests else 1)
