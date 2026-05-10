import sys, os, json, subprocess, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = ROOT
BRIDGE = os.path.join(PROJ, "bridge.py")

def run_bridge(code: str = None, no_args: bool = False) -> tuple:
    args = [sys.executable, BRIDGE]
    tmp = None
    if not no_args:
        with tempfile.NamedTemporaryFile("w", suffix=".ml", delete=False, encoding="utf-8") as f:
            f.write(code or "")
            tmp = f.name
        args.append(tmp)
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", timeout=20)
    finally:
        if tmp:
            os.unlink(tmp)
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        data = None
    return r.returncode, data, r.stdout, r.stderr

CASES = [
    ("Sin argumentos", None, True),
    ("Archivo vacío", "", False),
    ("Solo comentarios", "// hola\n// mundo\n", False),
    ("Solo declaración sin valor", "int x;", False),
    ("Solo print", "print(42);", False),
    ("Loop infinito sintáctico (while true)", "while (true) { int x = 1; }", False),
    ("If sin else con expresión booleana", "int n = 5; if (n > 0) { print(n); }", False),
    ("Char ilegal y muy largo", "int x = 5@@@@@@@@@;", False),
    ("Cadena sin cerrar", 'string s = "hola;', False),
    ("División por cero literal (no aborta TAC)", "int a = 5 / 0; print(a);", False),
    ("Llamada a función desconocida", "int r = miFuncion(1, 2, 3); print(r);", False),
    ("Operadores anidados profundos", "int a = ((((1+2)*3)-4)/5)%6; print(a);", False),
    ("Bool con operadores lógicos", "boolean b = (true && false) || !(false); print(b);", False),
    ("For con todo", "for (int i = 0; i < 10; i = i + 1) { print(i); }", False),
    ("Asignación a no declarada (semántico)", "x = 5; print(x);", False),
]

print("=" * 72)
print("QA edge cases")
print("=" * 72)

failures = 0
for name, code, no_args in CASES:
    rc, data, stdout, stderr = run_bridge(code, no_args=no_args)
    if data is None:
        print(f"\n[FAIL] {name}: returncode={rc}, stdout no es JSON")
        print(f"   stdout: {stdout[:200]}")
        print(f"   stderr: {stderr[:200]}")
        failures += 1
        continue
    tk = len(data.get("tokens", []))
    sm = len(data.get("simbolos", []))
    er = len(data.get("errores", []))
    tac = len(data.get("tac", []))
    opt = len(data.get("tac_optimizado", []))
    status = "OK"
    notes = []
    if "tac" not in data: notes.append("falta clave 'tac'")
    if "metricas" not in data: notes.append("falta clave 'metricas'")
    if notes:
        status = "WARN"
        failures += 1
    print(f"\n[{status}] {name}")
    print(f"   tokens={tk} simbolos={sm} errores={er} tac={tac}→{opt}")
    if er and er <= 3:
        for e in data["errores"]:
            print(f"   ! {e}")
    elif er > 3:
        print(f"   ! ({er} errores; primero: {data['errores'][0]})")
    for n in notes:
        print(f"   PROBLEMA: {n}")

print("\n" + "=" * 72)
if failures:
    print(f"{failures} caso(s) con problemas")
    sys.exit(1)
print("Todos los casos edge respondieron con JSON válido y todas las claves")
