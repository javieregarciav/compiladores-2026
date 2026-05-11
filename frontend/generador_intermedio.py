from intermedio import Quad

_BIN_TIPOS = {
    "MAS": "+", "MENOS": "-",
    "MULT": "*", "MULTIPLICACION": "*",
    "DIV": "/", "DIVIDIR": "/",
    "MOD": "%", "MODULO": "%",
    "IGUAL": "==", "DIFERENTE": "!=",
    "MENOR": "<", "MAYOR": ">",
    "MENOR_IGUAL": "<=", "MAYOR_IGUAL": ">=",
    "Y_LOGICO": "&&", "O_LOGICO": "||",
    "AND": "&&", "OR": "||",
}

class GeneradorTAC:

    def __init__(self):
        self.codigo: list[Quad] = []
        self._t = 0
        self._l = 0

    def _nuevo_temp(self) -> str:
        self._t += 1
        return f"$t{self._t}"

    def _nueva_etiq(self) -> str:
        self._l += 1
        return f"$L{self._l}"

    def emit(self, op, arg1=None, arg2=None, dest=None):
        self.codigo.append(Quad(op, arg1, arg2, dest))

    def generar(self, ast) -> list[Quad]:
        self.codigo = []
        self._t = 0
        self._l = 0
        if ast:
            self._gen(ast)
        return self.codigo

    def _gen(self, node):
        if not node:
            return None
        t = node.get("type", "")
        method = getattr(self, f"_g_{t}", self._g_default)
        return method(node)

    def _g_default(self, node):
        return None

    def _g_Program(self, node):
        for s in node.get("children", []):
            self._gen(s)

    def _g_Block(self, node):
        for s in node.get("stmts", []):
            self._gen(s)

    def _g_Declaration(self, node):
        id_ = node.get("id") or {}
        nombre = id_.get("valor", "?")
        if node.get("expr") is not None:
            valor = self._g_expr(node["expr"])
            self.emit("=", valor, None, nombre)

    def _g_Assignment(self, node):
        id_ = node.get("id") or {}
        nombre = id_.get("valor", "?")
        valor = self._g_expr(node["expr"])
        self.emit("=", valor, None, nombre)

    def _g_If(self, node):
        cond = self._g_expr(node.get("cond"))
        L_else = self._nueva_etiq()
        L_end = self._nueva_etiq() if node.get("elseBody") else L_else

        self.emit("if_false", cond, None, L_else)
        self._gen(node.get("body"))
        if node.get("elseBody"):
            self.emit("goto", None, None, L_end)
            self.emit("label", None, None, L_else)
            self._gen(node["elseBody"])
            self.emit("label", None, None, L_end)
        else:
            self.emit("label", None, None, L_else)

    def _g_While(self, node):
        L_inicio = self._nueva_etiq()
        L_fin = self._nueva_etiq()
        self.emit("label", None, None, L_inicio)
        cond = self._g_expr(node.get("cond"))
        self.emit("if_false", cond, None, L_fin)
        self._gen(node.get("body"))
        self.emit("goto", None, None, L_inicio)
        self.emit("label", None, None, L_fin)

    def _g_For(self, node):
        self._gen(node.get("init"))
        L_inicio = self._nueva_etiq()
        L_fin = self._nueva_etiq()
        self.emit("label", None, None, L_inicio)
        cond = self._g_expr(node.get("cond"))
        self.emit("if_false", cond, None, L_fin)
        self._gen(node.get("body"))

        upd_id = node.get("updId") or {}
        upd_expr = node.get("updExpr")
        if upd_id and upd_expr is not None:
            valor = self._g_expr(upd_expr)
            self.emit("=", valor, None, upd_id.get("valor", "?"))
        self.emit("goto", None, None, L_inicio)
        self.emit("label", None, None, L_fin)

    def _g_DoWhile(self, node):
        L_inicio = self._nueva_etiq()
        L_fin = self._nueva_etiq()
        self.emit("label", None, None, L_inicio)
        self._gen(node.get("body"))
        cond = self._g_expr(node.get("cond"))
        self.emit("if_false", cond, None, L_fin)
        self.emit("goto", None, None, L_inicio)
        self.emit("label", None, None, L_fin)

    def _g_Read(self, node):
        id_ = node.get("id") or {}
        self.emit("read", None, None, id_.get("valor", "?"))

    def _g_Print(self, node):
        args = node.get("args")
        if args:
            for a in args:
                self.emit("print", self._g_expr(a), None, None)
        elif node.get("arg") is not None:
            self.emit("print", self._g_expr(node["arg"]), None, None)

    def _g_Call(self, node):
        ids = []
        for a in node.get("args", []):
            ids.append(self._g_expr(a))
        for a in ids:
            self.emit("param", a, None, None)
        id_ = node.get("id") or {}
        t = self._nuevo_temp()
        self.emit("call", id_.get("valor", "?"), str(len(ids)), t)
        return t

    def _g_short_circuit(self, node, corto_si):
        """Genera TAC con short-circuit para && (corto_si='if_false')
        y || (corto_si='if_true').

        Patron:
            tmp = <izq>
            <corto_si> tmp goto L_short      # salta si ya quedo determinado
            tmp = <der>
            label L_short
        """
        izq = self._g_expr(node["left"])
        tmp = self._nuevo_temp()
        self.emit("=", izq, None, tmp)
        L_short = self._nueva_etiq()
        self.emit(corto_si, tmp, None, L_short)
        der = self._g_expr(node["right"])
        self.emit("=", der, None, tmp)
        self.emit("label", None, None, L_short)
        return tmp

    def _g_expr(self, node):
        if not node:
            return "_"
        t = node.get("type", "")
        if t == "Literal":
            return str(node["token"]["valor"])
        if t == "StringLit":
            v = node["token"]["valor"]
            v = (v.replace("\\", "\\\\")
                  .replace('"',  '\\"')
                  .replace("\n", "\\n")
                  .replace("\t", "\\t")
                  .replace("\r", "\\r"))
            return f"\"{v}\""
        if t == "BoolLit":
            return str(node["token"]["valor"])
        if t == "NullLit":
            return "null"
        if t == "Identifier":
            return node["token"]["valor"]
        if t == "Group":
            return self._g_expr(node["expr"])
        if t == "Call":
            return self._g_Call(node)
        if t == "UnaryOp":
            operand = self._g_expr(node["operand"])
            op_val = node["op"]["valor"]
            if op_val == "+":
                return operand
            tmp = self._nuevo_temp()
            if op_val == "-":
                self.emit("-", "0", operand, tmp)
            elif op_val == "not":
                self.emit("!", operand, None, tmp)
            else:
                self.emit(op_val, operand, None, tmp)
            return tmp
        if t == "BinaryOp":
            op_tipo = node["op"]["tipo"]
            # Short-circuit para && y || : NO evaluar el lado derecho si el
            # resultado ya esta determinado por el izquierdo. Esto es
            # semantica obligatoria: con efectos secundarios (leer / call),
            # evaluar ambos lados cambia el comportamiento del programa.
            if op_tipo in ("AND", "Y_LOGICO"):
                return self._g_short_circuit(node, corto_si="if_false")
            if op_tipo in ("OR", "O_LOGICO"):
                return self._g_short_circuit(node, corto_si="if_true")
            izq = self._g_expr(node["left"])
            der = self._g_expr(node["right"])
            tmp = self._nuevo_temp()
            op = _BIN_TIPOS.get(op_tipo, node["op"]["valor"])
            self.emit(op, izq, der, tmp)
            return tmp
        if node.get("token"):
            return str(node["token"]["valor"])
        return "?"
