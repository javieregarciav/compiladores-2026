import argparse
import sys

from frontend.errores import fmt as fmt_error
from runtime import EjecutorTAC, compilar


def main() -> int:
    ap = argparse.ArgumentParser(description="Compila y ejecuta un programa del lenguaje.")
    ap.add_argument("archivo", help="Ruta del archivo fuente .ext")
    ap.add_argument("--sin-banner", action="store_true", help="No imprime resumen de compilacion")
    args = ap.parse_args()

    try:
        with open(args.archivo, "r", encoding="utf-8") as f:
            codigo = f.read()
    except OSError as exc:
        print(f"No se pudo leer {args.archivo}: {exc}", file=sys.stderr)
        return 1

    res = compilar(codigo)
    if res.errores:
        print("El programa no se ejecuto porque tiene errores de compilacion:", file=sys.stderr)
        for err in res.errores:
            print(f"  - {fmt_error(err) if isinstance(err, dict) else err}", file=sys.stderr)
        return 1

    if not args.sin_banner:
        print(f"[OK] Compilado: {len(res.quads)} cuadruplos, {len(res.simbolos)} simbolos")
        print("[RUN] Iniciando programa...")

    try:
        EjecutorTAC(res.quads).ejecutar()
    except Exception as exc:
        print(f"\nError en runtime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
