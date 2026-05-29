from dataclasses import dataclass
from typing import Optional

@dataclass
class Quad:
    op: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    dest: Optional[str] = None

    def as_tuple(self):
        return (self.op,
                self.arg1 if self.arg1 is not None else "_",
                self.arg2 if self.arg2 is not None else "_",
                self.dest if self.dest is not None else "_")

def formatear_tac(quads):
    filas = []
    n = 0
    for q in quads:
        op, a1, a2, d = q.op, q.arg1, q.arg2, q.dest
        if op == "label":
            instr = f"{d}:"
            etiqueta = d
        elif op == "goto":
            instr = f"goto {d}"
            etiqueta = ""
        elif op == "if_false":
            instr = f"ifFalse {a1} goto {d}"
            etiqueta = ""
        elif op == "if_true":
            instr = f"if {a1} goto {d}"
            etiqueta = ""
        elif op == "=":
            instr = f"{d} = {a1}"
            etiqueta = ""
        elif op == "print":
            instr = f"imprimir {a1}"
            etiqueta = ""
        elif op == "read":
            instr = f"leer {d}"
            etiqueta = ""
        elif op == "array_decl":
            instr = f"arreglo {a1} {d}[{a2}]"
            etiqueta = ""
        elif op == "aload":
            instr = f"{d} = {a1}[{a2}]"
            etiqueta = ""
        elif op == "astore":
            instr = f"{a1}[{a2}] = {d}"
            etiqueta = ""
        elif op == "param":
            instr = f"param {a1}"
            etiqueta = ""
        elif op == "call":
            instr = f"{d} = call {a1}, {a2}"
            etiqueta = ""
        elif op == "label_func":
            instr = f"func {d}:"
            etiqueta = d
        elif op == "enter_func":
            firma = f"{a1} {d}({a2 if a2 != '_' else ''})"
            instr = f"enter_func {firma}"
            etiqueta = ""
        elif op == "return":
            instr = f"return {a1}" if a1 is not None else "return"
            etiqueta = ""
        elif op == "exit_func":
            instr = f"exit_func {d}"
            etiqueta = ""
        elif op == "!":
            instr = f"{d} = !{a1}"
            etiqueta = ""
        else:
            instr = f"{d} = {a1} {op} {a2}"
            etiqueta = ""
        n += 1
        filas.append({
            "n": n,
            "etiqueta": etiqueta,
            "instruccion": instr,
            "op": op,
            "arg1": a1 if a1 is not None else "—",
            "arg2": a2 if a2 is not None else "—",
            "dest": d if d is not None else "—",
        })
    return filas
