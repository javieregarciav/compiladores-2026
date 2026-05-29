from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from intermedio import Quad


class RuntimeErrorMini(Exception):
    pass


@dataclass
class ResultadoCompilacion:
    quads: list[Quad]
    errores: list
    simbolos: list


def compilar(codigo: str) -> ResultadoCompilacion:
    lexer = Lexer()
    tokens, tabla, errores = lexer.analizar(codigo)
    ast = build_tree(tokens, errores)
    check_semantic(ast, tabla, errores)
    quads = [] if errores else GeneradorTAC().generar(ast)
    return ResultadoCompilacion(quads=quads, errores=errores, simbolos=tabla.todos_los_simbolos())


class EjecutorTAC:
    def __init__(
        self,
        quads: list[Quad],
        entrada: Callable[[str], str] | None = None,
        salida: Callable[[str], None] | None = None,
    ):
        self.quads = quads
        self.entrada = entrada or input
        self.salida = salida or print
        self.globales: dict[str, object] = {}
        self.arrays_tipo: dict[str, str] = {}
        self.labels: dict[str, int] = {}
        self.funciones: dict[str, tuple[int, int, list[str]]] = {}
        self.param_stack: list[object] = []
        self.frames: list[dict[str, object]] = []
        self._indexar()

    def _indexar(self):
        for i, q in enumerate(self.quads):
            if q.op == "label" and q.dest:
                self.labels[q.dest] = i
            elif q.op == "label_func" and q.dest:
                self.labels[q.dest] = i
                end = self._buscar_exit_func(i + 1, q.dest)
                params = self._leer_params(i + 1)
                self.funciones[q.dest] = (i, end, params)

    def _buscar_exit_func(self, start: int, nombre: str) -> int:
        for i in range(start, len(self.quads)):
            if self.quads[i].op == "exit_func" and self.quads[i].dest == nombre:
                return i
        raise RuntimeErrorMini(f"Funcion '{nombre}' sin exit_func")

    def _leer_params(self, enter_idx: int) -> list[str]:
        if enter_idx >= len(self.quads) or self.quads[enter_idx].op != "enter_func":
            return []
        raw = self.quads[enter_idx].arg2 or ""
        params = []
        for parte in [p.strip() for p in raw.split(",") if p.strip()]:
            params.append(parte.split()[-1])
        return params

    def ejecutar(self):
        self._ejecutar_rango(0, len(self.quads), frame=None)

    def _ejecutar_funcion(self, nombre: str, args: list[object]):
        if nombre not in self.funciones:
            raise RuntimeErrorMini(f"Funcion o procedimiento '{nombre}' no existe en runtime")
        start, end, params = self.funciones[nombre]
        frame = {p: args[i] if i < len(args) else None for i, p in enumerate(params)}
        self.frames.append(frame)
        try:
            returned, valor = self._ejecutar_rango(start + 2, end, frame=frame)
        finally:
            self.frames.pop()
        return valor if returned else None

    def _ejecutar_rango(self, start: int, end: int, frame: dict[str, object] | None):
        pc = start
        while pc < end:
            q = self.quads[pc]
            op = q.op

            if op == "label":
                pc += 1
                continue
            if op == "label_func":
                _, func_end, _ = self.funciones.get(q.dest, (pc, pc, []))
                pc = func_end + 1
                continue
            if op in ("enter_func", "exit_func"):
                pc += 1
                continue
            if op == "goto":
                pc = self._label_pc(q.dest)
                continue
            if op == "if_false":
                pc = self._label_pc(q.dest) if not self._truthy(self._val(q.arg1, frame)) else pc + 1
                continue
            if op == "if_true":
                pc = self._label_pc(q.dest) if self._truthy(self._val(q.arg1, frame)) else pc + 1
                continue
            if op == "array_decl":
                self.arrays_tipo[q.dest] = q.arg1 or "cadena"
                self.globales[q.dest] = [self._default(q.arg1) for _ in range(int(q.arg2 or 0))]
                pc += 1
                continue
            if op == "aload":
                arr = self._array(q.arg1)
                idx = self._indice(q.arg2, frame)
                self._set(q.dest, arr[idx], frame)
                pc += 1
                continue
            if op == "astore":
                arr = self._array(q.arg1)
                idx = self._indice(q.arg2, frame)
                arr[idx] = self._cast(self._val(q.dest, frame), self.arrays_tipo.get(q.arg1, "cadena"))
                pc += 1
                continue
            if op == "read":
                texto = self.entrada("")
                self._set(q.dest, self._cast_para_destino(q.dest, texto, frame), frame)
                pc += 1
                continue
            if op == "print":
                self.salida(self._fmt(self._val(q.arg1, frame)))
                pc += 1
                continue
            if op == "param":
                self.param_stack.append(self._val(q.arg1, frame))
                pc += 1
                continue
            if op == "call":
                n = int(q.arg2 or 0)
                args = self.param_stack[-n:] if n else []
                if n:
                    del self.param_stack[-n:]
                self._set(q.dest, self._ejecutar_funcion(q.arg1, args), frame)
                pc += 1
                continue
            if op == "return":
                return True, self._val(q.arg1, frame) if q.arg1 is not None else None
            if op == "=":
                self._set(q.dest, self._val(q.arg1, frame), frame)
                pc += 1
                continue
            if op == "!":
                self._set(q.dest, not self._truthy(self._val(q.arg1, frame)), frame)
                pc += 1
                continue
            if op in {"+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"}:
                self._set(q.dest, self._bin(op, self._val(q.arg1, frame), self._val(q.arg2, frame)), frame)
                pc += 1
                continue
            raise RuntimeErrorMini(f"Cuadruplo no soportado en runtime: {q}")
        return False, None

    def _label_pc(self, label: str | None) -> int:
        if label not in self.labels:
            raise RuntimeErrorMini(f"Etiqueta '{label}' no existe")
        return self.labels[label] + 1

    def _array(self, nombre: str | None) -> list:
        arr = self.globales.get(nombre or "")
        if not isinstance(arr, list):
            raise RuntimeErrorMini(f"'{nombre}' no es un arreglo en runtime")
        return arr

    def _indice(self, raw, frame) -> int:
        idx = int(self._val(raw, frame))
        return idx

    def _set(self, nombre: str | None, valor, frame: dict[str, object] | None):
        if not nombre:
            return
        if frame is not None and (nombre in frame or nombre not in self.globales):
            frame[nombre] = valor
        else:
            self.globales[nombre] = valor

    def _val(self, raw, frame: dict[str, object] | None):
        if raw is None:
            return None
        if isinstance(raw, (int, float, bool)):
            return raw
        s = str(raw)
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            return bytes(s[1:-1], "utf-8").decode("unicode_escape")
        low = s.lower()
        if low in ("verdadero", "true"):
            return True
        if low in ("falso", "false"):
            return False
        try:
            return float(s) if "." in s else int(s)
        except ValueError:
            pass
        if frame is not None and s in frame:
            return frame[s]
        return self.globales.get(s, "")

    def _cast_para_destino(self, nombre: str | None, texto: str, frame: dict[str, object] | None):
        actual = None
        if nombre:
            if frame is not None and nombre in frame:
                actual = frame[nombre]
            elif nombre in self.globales:
                actual = self.globales[nombre]
        if isinstance(actual, bool):
            return self._cast(texto, "booleano")
        if isinstance(actual, int) and not isinstance(actual, bool):
            return self._cast(texto, "entero")
        if isinstance(actual, float):
            return self._cast(texto, "decimal")
        return texto

    def _cast(self, valor, tipo: str):
        if tipo == "entero":
            return int(float(str(valor).strip()))
        if tipo == "decimal":
            return float(str(valor).strip())
        if tipo == "booleano":
            return str(valor).strip().lower() in ("1", "true", "verdadero", "si", "sí")
        return str(valor)

    def _default(self, tipo: str | None):
        return {"entero": 0, "decimal": 0.0, "booleano": False}.get(tipo or "", "")

    def _truthy(self, v) -> bool:
        return bool(v)

    def _bin(self, op: str, a, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return int(a / b) if isinstance(a, int) and isinstance(b, int) else a / b
        if op == "%":
            return a % b
        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b
        if op == "&&":
            return self._truthy(a) and self._truthy(b)
        if op == "||":
            return self._truthy(a) or self._truthy(b)
        raise RuntimeErrorMini(f"Operador no soportado: {op}")

    def _fmt(self, v) -> str:
        if isinstance(v, bool):
            return "verdadero" if v else "falso"
        if isinstance(v, float) and v.is_integer():
            return f"{v:.1f}"
        return str(v)


def ejecutar_codigo(codigo: str, entradas: Iterable[str] | None = None) -> tuple[ResultadoCompilacion, list[str]]:
    res = compilar(codigo)
    if res.errores:
        return res, []
    cola = list(entradas or [])
    salida: list[str] = []

    def _in(_prompt=""):
        if cola:
            return cola.pop(0)
        return input()

    EjecutorTAC(res.quads, entrada=_in, salida=salida.append).ejecutar()
    return res, salida
