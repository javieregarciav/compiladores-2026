"""QA script — runs bridge.py against all 7 sample programs from main.py
and validates the JSON output."""
import sys, os, json, subprocess, tempfile, importlib.util

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.join(ROOT, "files (1)")
BRIDGE = os.path.join(PROJ, "bridge.py")

# Load EJEMPLOS list from main.py without executing tk init
sys.path.insert(0, PROJ)

def load_examples():
    """Read main.py and execute only up through the EJEMPLOS list."""
    main_path = os.path.join(PROJ, "main.py")
    with open(main_path, "r", encoding="utf-8") as f:
        src = f.read()
    # Find the EJEMPLOS = [ ... ] block and execute just the list literal
    start = src.find("EJEMPLOS = [")
    end = src.find("\n]\n", start) + 2
    snippet = src[start:end]
    ns = {}
    exec(snippet, ns)
    return ns["EJEMPLOS"]


def run_bridge(code: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".ml", delete=False, encoding="utf-8") as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [sys.executable, BRIDGE, tmp],
            capture_output=True, text=True, encoding="utf-8", timeout=20
        )
    finally:
        os.unlink(tmp)
    if r.returncode != 0:
        print(f"  STDERR: {r.stderr}")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        print(f"  Invalid JSON: {e}")
        print(f"  stdout: {r.stdout[:500]}")
        return None


def validate_response(data: dict, label: str) -> list:
    issues = []
    if data is None:
        return [f"[{label}] No JSON returned"]

    required = ["tokens", "simbolos", "errores", "tac", "tac_optimizado", "metricas", "traza_optimizacion"]
    for k in required:
        if k not in data:
            issues.append(f"[{label}] Missing key: {k}")

    if "tac" in data and data["tac"]:
        sample = data["tac"][0]
        for k in ("n", "etiqueta", "instruccion", "op", "arg1", "arg2", "dest"):
            if k not in sample:
                issues.append(f"[{label}] tac row missing key: {k}")

    if "metricas" in data and data["metricas"]:
        for k in ("cuad_orig", "cuad_opt", "reduccion_pct", "temps_orig", "temps_opt"):
            if k not in data["metricas"]:
                issues.append(f"[{label}] metricas missing key: {k}")

    return issues


def main():
    print("=" * 72)
    print("QA: Running all 7 sample programs through bridge.py")
    print("=" * 72)

    examples = load_examples()
    all_issues = []
    for i, (titulo, codigo) in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] {titulo}")
        data = run_bridge(codigo)
        issues = validate_response(data, titulo)
        if data:
            tk = len(data.get("tokens", []))
            sm = len(data.get("simbolos", []))
            er = len(data.get("errores", []))
            tac = len(data.get("tac", []))
            opt = len(data.get("tac_optimizado", []))
            m = data.get("metricas", {})
            red = m.get("reduccion_pct", "?")
            print(f"   tokens={tk}  simbolos={sm}  errores={er}  tac={tac}→{opt}  red={red}%")
            if er:
                for e in data["errores"]:
                    print(f"   ! {e}")
        if issues:
            print(f"   PROBLEMAS:")
            for it in issues:
                print(f"     - {it}")
        all_issues.extend(issues)

    print("\n" + "=" * 72)
    if all_issues:
        print(f"FAILED: {len(all_issues)} issue(s) found")
        for i in all_issues:
            print(f"  - {i}")
        sys.exit(1)
    else:
        print("PASSED: all 7 examples produced valid JSON with all required keys")


if __name__ == "__main__":
    main()
