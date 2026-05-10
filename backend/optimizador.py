
from copy import deepcopy
from intermedio import Quad

_BIN_OPS = {
    "+":  lambda a, b: a + b,
    "-":  lambda a, b: a - b,
    "*":  lambda a, b: a * b,
    "/":  lambda a, b: a / b if isinstance(a, float) or isinstance(b, float) else a // b,
    "%":  lambda a, b: a % b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<":  lambda a, b: a < b,
    ">":  lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
    "&&": lambda a, b: bool(a) and bool(b),
    "||": lambda a, b: bool(a) or bool(b),
}

def _es_numero(s):
    if s is None:
        return False
    try:
        if "." in str(s):
            float(s)
        else:
            int(s)
        return True
    except (ValueError, TypeError):
        return False

def _to_num(s):
    s = str(s)
    return float(s) if "." in s else int(s)

def _es_bool(s):
    return s in ("true", "false", "True", "False")

def _to_bool(s):
    return s in ("true", "True")

def _fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):

        return str(v) if v != int(v) else f"{v:.1f}"
    return str(v)

def _es_temp(nombre):
    if not isinstance(nombre, str) or len(nombre) < 3:
        return False
    return nombre.startswith("$t") and nombre[2:].isdigit()

def _constant_folding(codigo):
    nuevo = []
    cambio = False
    for q in codigo:
        if q.op in _BIN_OPS:
            a1, a2 = q.arg1, q.arg2

            if q.op == "+" and a1 == "0":
                nuevo.append(Quad("=", a2, None, q.dest)); cambio = True; continue
            if q.op == "+" and a2 == "0":
                nuevo.append(Quad("=", a1, None, q.dest)); cambio = True; continue
            if q.op == "-" and a2 == "0":
                nuevo.append(Quad("=", a1, None, q.dest)); cambio = True; continue
            if q.op == "*" and (a1 == "1"):
                nuevo.append(Quad("=", a2, None, q.dest)); cambio = True; continue
            if q.op == "*" and (a2 == "1"):
                nuevo.append(Quad("=", a1, None, q.dest)); cambio = True; continue
            if q.op == "*" and (a1 == "0" or a2 == "0"):
                nuevo.append(Quad("=", "0", None, q.dest)); cambio = True; continue

            if _es_numero(a1) and _es_numero(a2):
                try:
                    r = _BIN_OPS[q.op](_to_num(a1), _to_num(a2))
                    nuevo.append(Quad("=", _fmt(r), None, q.dest))
                    cambio = True
                    continue
                except Exception:
                    pass

            if _es_bool(a1) and _es_bool(a2) and q.op in ("&&", "||", "==", "!="):
                r = _BIN_OPS[q.op](_to_bool(a1), _to_bool(a2))
                nuevo.append(Quad("=", _fmt(r), None, q.dest))
                cambio = True
                continue
        if q.op == "!" and _es_bool(q.arg1):
            nuevo.append(Quad("=", _fmt(not _to_bool(q.arg1)), None, q.dest))
            cambio = True
            continue
        nuevo.append(q)
    return nuevo, cambio

def _propagation(codigo):
    nuevo = []
    env = {}
    cambio = False

    def reemplazar(x):
        if x is None:
            return x
        return env.get(x, x)

    for q in codigo:
        if q.op == "label":

            env = {}
            nuevo.append(q)
            continue
        if q.op in ("goto", "if_false", "if_true"):

            new_q = Quad(q.op, reemplazar(q.arg1), reemplazar(q.arg2), q.dest)
            if new_q.arg1 != q.arg1 or new_q.arg2 != q.arg2:
                cambio = True
            nuevo.append(new_q)
            env = {}
            continue
        if q.op == "=":
            valor = reemplazar(q.arg1)
            if valor != q.arg1:
                cambio = True
            nuevo.append(Quad("=", valor, None, q.dest))

            env[q.dest] = valor

            for k in list(env):
                if env[k] == q.dest and k != q.dest:
                    del env[k]
            continue
        if q.op == "print":
            new_q = Quad("print", reemplazar(q.arg1), None, None)
            if new_q.arg1 != q.arg1:
                cambio = True
            nuevo.append(new_q)
            continue
        if q.op == "param":
            new_q = Quad("param", reemplazar(q.arg1), None, None)
            if new_q.arg1 != q.arg1:
                cambio = True
            nuevo.append(new_q)
            continue
        if q.op == "call":
            nuevo.append(q)
            env[q.dest] = q.dest if q.dest else None
            continue

        a1 = reemplazar(q.arg1)
        a2 = reemplazar(q.arg2)
        if a1 != q.arg1 or a2 != q.arg2:
            cambio = True
        nuevo.append(Quad(q.op, a1, a2, q.dest))
        if q.dest is not None:
            env.pop(q.dest, None)

            for k in list(env):
                if env[k] == q.dest:
                    del env[k]
    return nuevo, cambio

def _dead_code(codigo):

    leidos = set()
    for q in codigo:
        for a in (q.arg1, q.arg2):
            if a is not None:
                leidos.add(a)

        if q.op in ("goto", "if_false", "if_true") and q.dest:
            leidos.add(q.dest)

    nuevo = []
    cambio = False
    for q in codigo:
        if q.op in ("=",) or q.op in _BIN_OPS or q.op == "!":
            if q.dest and _es_temp(q.dest) and q.dest not in leidos:
                cambio = True
                continue
        if q.op == "call":

            pass
        nuevo.append(q)
    return nuevo, cambio

def _jump_threading(codigo):
    nuevo = []
    cambio = False
    i = 0
    while i < len(codigo):
        q = codigo[i]
        if (q.op == "goto"
                and i + 1 < len(codigo)
                and codigo[i + 1].op == "label"
                and codigo[i + 1].dest == q.dest):
            cambio = True
            i += 1
            continue
        nuevo.append(q)
        i += 1

    referenciadas = set()
    for q in nuevo:
        if q.op in ("goto", "if_false", "if_true") and q.dest:
            referenciadas.add(q.dest)
    final = []
    for q in nuevo:
        if q.op == "label" and q.dest not in referenciadas:
            cambio = True
            continue
        final.append(q)
    return final, cambio

def _branch_pruning(codigo):
    nuevo = []
    cambio = False
    for q in codigo:
        if q.op == "if_false":
            if q.arg1 in ("true", "True", "1"):

                cambio = True
                continue
            if q.arg1 in ("false", "False", "0"):

                nuevo.append(Quad("goto", None, None, q.dest))
                cambio = True
                continue
        if q.op == "if_true":
            if q.arg1 in ("false", "False", "0"):
                cambio = True
                continue
            if q.arg1 in ("true", "True", "1"):
                nuevo.append(Quad("goto", None, None, q.dest))
                cambio = True
                continue
        nuevo.append(q)
    return nuevo, cambio

def optimizar(codigo, max_iter: int = 12):
    actual = deepcopy(codigo)
    traza = []
    pasadas = [
        ("Constant Folding & Algebraic", _constant_folding),
        ("Constant / Copy Propagation",  _propagation),
        ("Branch Pruning",               _branch_pruning),
        ("Dead-Code Elimination",        _dead_code),
        ("Jump Threading",               _jump_threading),
    ]

    for it in range(max_iter):
        cambio_global = False
        for nombre, fn in pasadas:
            antes = len(actual)
            actual, cambio = fn(actual)
            despues = len(actual)
            if cambio:
                traza.append({
                    "iter": it + 1,
                    "pasada": nombre,
                    "antes": antes,
                    "despues": despues,
                    "delta": despues - antes,
                })
                cambio_global = True
        if not cambio_global:
            break
    return actual, traza

if __name__ == "__main__":
    from .lexer import Lexer
    from .parser import build_tree
    from .codigo_intermedio import GeneradorTAC, formatear_tac

    codigo = """\
int a = 3;
int b = 4;
int c = a + b;
int d = c * 2;
int e = d - 0;
int f = e * 1;
print(f);
"""
    lex = Lexer()
    toks, _, _ = lex.analizar(codigo)
    ast = build_tree(toks)
    quads = GeneradorTAC().generar(ast)
    print("=== ORIGINAL ===")
    for f in formatear_tac(quads):
        print(f"{f['n']:>3}: {f['instruccion']}")
    opt, traza = optimizar(quads)
    print("\n=== OPTIMIZADO ===")
    for f in formatear_tac(opt):
        print(f"{f['n']:>3}: {f['instruccion']}")
    print(f"\nReducción: {len(quads)} -> {len(opt)} cuádruplos")
    for t in traza:
        print(f"  iter {t['iter']}  {t['pasada']}: {t['antes']} -> {t['despues']}")
