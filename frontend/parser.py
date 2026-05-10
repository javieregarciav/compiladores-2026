"""
Parser PLY yacc (fase 1) que produce el AST en formato dict que ya
consume el resto del pipeline (visualizador de arbol, get_kids,
node_label, check_semantic, GeneradorTAC).

Mantiene la API:
  build_tree(tokens, errors=None) -> ast (dict)
  get_kids(node), node_label(node)
  check_semantic(ast, tabla, errors)
  RESERVED, TIPOS_DATO
"""

import ply.yacc as yacc
from . import lexer as _lex_mod
from . import errores as _err_mod
from .lexer import tokens, reservadas, encontrar_columna, _NullLogger

# Vocabulario expuesto al resto del pipeline / UI
RESERVED = dict(reservadas)
TIPOS_DATO = {"ENTERO", "DECIMAL", "CADENA_TIPO", "BOOLEANO"}

# Codigo fuente del ultimo analisis (lo necesita PLY para tokenizar)
_ultimo_codigo = [""]


def _set_codigo(codigo: str):
    _ultimo_codigo[0] = codigo


# Helpers de construccion de nodos en formato dict ------------------------

def _tok(tipo, valor, linea, columna):
    return {"tipo": tipo, "valor": valor, "linea": linea, "columna": columna}


def _tok_de_p(p, idx, tipo=None):
    """Construye un token-dict a partir de un slice del parser PLY."""
    valor = p[idx]
    linea = p.lineno(idx) if hasattr(p, "lineno") else 0
    columna = 0
    try:
        if hasattr(p, "lexpos") and p.lexpos(idx):
            columna = p.lexpos(idx) - _ultimo_codigo[0].rfind("\n", 0, p.lexpos(idx))
    except Exception:
        columna = 0
    return {
        "tipo": tipo or str(valor).upper(),
        "valor": str(valor),
        "linea": linea,
        "columna": columna,
    }


# Precedencia ------------------------------------------------------------

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVIDIR', 'MODULO'),
    ('right', 'NOT', 'UMENOS'),
)


# Reglas -----------------------------------------------------------------

def p_programa(p):
    '''programa : PROGRAMA LLAVE_IZQ sentencias LLAVE_DER
                | PROGRAMA LLAVE_IZQ LLAVE_DER
                | sentencias'''
    if len(p) == 5:
        p[0] = {"type": "Program", "children": p[3]}
    elif len(p) == 4:
        p[0] = {"type": "Program", "children": []}
    else:
        p[0] = {"type": "Program", "children": p[1]}


def p_sentencias_lista(p):
    '''sentencias : sentencias sentencia'''
    p[0] = p[1] + ([p[2]] if p[2] else [])


def p_sentencias_uno(p):
    '''sentencias : sentencia'''
    p[0] = [p[1]] if p[1] else []


def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | sentencia_si
                 | sentencia_mientras
                 | sentencia_hacer_mientras
                 | sentencia_para
                 | sentencia_imprimir
                 | sentencia_leer'''
    p[0] = p[1]


# Tipo de dato
def p_tipo(p):
    '''tipo : ENTERO
            | DECIMAL
            | CADENA_TIPO
            | BOOLEANO'''
    p[0] = _tok_de_p(p, 1, tipo=p.slice[1].type)


# Declaracion
def p_declaracion_sin_valor(p):
    '''declaracion : tipo IDENTIFICADOR PUNTO_COMA'''
    p[0] = {
        "type": "Declaration",
        "dataType": p[1],
        "id": _tok_de_p(p, 2, tipo="IDENTIFICADOR"),
        "expr": None,
    }


def p_declaracion_con_valor(p):
    '''declaracion : tipo IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    p[0] = {
        "type": "Declaration",
        "dataType": p[1],
        "id": _tok_de_p(p, 2, tipo="IDENTIFICADOR"),
        "expr": p[4],
    }


# Asignacion
def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    p[0] = {
        "type": "Assignment",
        "id": _tok_de_p(p, 1, tipo="IDENTIFICADOR"),
        "expr": p[3],
    }


def p_asignacion_para(p):
    '''asignacion_para : IDENTIFICADOR ASIGNAR expresion'''
    p[0] = {
        "type": "Assignment",
        "id": _tok_de_p(p, 1, tipo="IDENTIFICADOR"),
        "expr": p[3],
    }


# Si / sino
def p_sentencia_si(p):
    '''sentencia_si : SI LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER
                    | SI LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER SINO LLAVE_IZQ sentencias LLAVE_DER'''
    kw = _tok_de_p(p, 1, tipo="SI")
    body = {"type": "Block", "stmts": p[6]}
    if len(p) == 8:
        p[0] = {"type": "If", "kw": kw, "cond": p[3], "body": body, "elseBody": None}
    else:
        else_body = {"type": "Block", "stmts": p[10]}
        p[0] = {"type": "If", "kw": kw, "cond": p[3], "body": body, "elseBody": else_body}


# Mientras
def p_sentencia_mientras(p):
    '''sentencia_mientras : MIENTRAS LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER'''
    p[0] = {
        "type": "While",
        "kw": _tok_de_p(p, 1, tipo="MIENTRAS"),
        "cond": p[3],
        "body": {"type": "Block", "stmts": p[6]},
    }


# Hacer-mientras (do-while)
def p_sentencia_hacer_mientras(p):
    '''sentencia_hacer_mientras : HACER_MIENTRAS LLAVE_IZQ sentencias LLAVE_DER MIENTRAS LPAREN expresion RPAREN PUNTO_COMA'''
    p[0] = {
        "type": "DoWhile",
        "kw": _tok_de_p(p, 1, tipo="HACER_MIENTRAS"),
        "body": {"type": "Block", "stmts": p[3]},
        "cond": p[7],
    }


# Para
def p_sentencia_para(p):
    '''sentencia_para : PARA LPAREN para_init expresion PUNTO_COMA asignacion_para RPAREN LLAVE_IZQ sentencias LLAVE_DER'''
    p[0] = {
        "type": "For",
        "kw": _tok_de_p(p, 1, tipo="PARA"),
        "init": p[3],
        "cond": p[4],
        "updId": p[6]["id"],
        "updExpr": p[6]["expr"],
        "body": {"type": "Block", "stmts": p[9]},
    }


def p_para_init_asig(p):
    '''para_init : asignacion_para PUNTO_COMA'''
    p[0] = p[1]


def p_para_init_decl(p):
    '''para_init : tipo IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    p[0] = {
        "type": "Declaration",
        "dataType": p[1],
        "id": _tok_de_p(p, 2, tipo="IDENTIFICADOR"),
        "expr": p[4],
    }


# Imprimir
def p_sentencia_imprimir(p):
    '''sentencia_imprimir : IMPRIMIR LPAREN argumentos_imprimir RPAREN PUNTO_COMA
                          | IMPRIMIR LPAREN RPAREN PUNTO_COMA'''
    kw = _tok_de_p(p, 1, tipo="IMPRIMIR")
    args = p[3] if len(p) == 6 else []
    p[0] = {"type": "Print", "kw": kw, "args": args, "arg": args[0] if args else None}


def p_argumentos_imprimir_lista(p):
    '''argumentos_imprimir : argumentos_imprimir COMA expresion'''
    p[0] = p[1] + [p[3]]


def p_argumentos_imprimir_uno(p):
    '''argumentos_imprimir : expresion'''
    p[0] = [p[1]]


# Leer
def p_sentencia_leer(p):
    '''sentencia_leer : LEER LPAREN IDENTIFICADOR RPAREN PUNTO_COMA'''
    p[0] = {
        "type": "Read",
        "kw": _tok_de_p(p, 1, tipo="LEER"),
        "id": _tok_de_p(p, 3, tipo="IDENTIFICADOR"),
    }


# Expresiones binarias / unarias / agrupacion
_OP_TIPOS = {
    'MAS': '+', 'MENOS': '-', 'MULTIPLICACION': '*', 'DIVIDIR': '/',
    'MODULO': '%', 'IGUAL': '==', 'DIFERENTE': '!=',
    'MENOR': '<', 'MAYOR': '>', 'MENOR_IGUAL': '<=', 'MAYOR_IGUAL': '>=',
    'AND': '&&', 'OR': '||',
}


def p_expresion_binaria(p):
    '''expresion : expresion MAS expresion
                 | expresion MENOS expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVIDIR expresion
                 | expresion MODULO expresion
                 | expresion MENOR expresion
                 | expresion MAYOR expresion
                 | expresion MENOR_IGUAL expresion
                 | expresion IGUAL expresion
                 | expresion MAYOR_IGUAL expresion
                 | expresion DIFERENTE expresion
                 | expresion AND expresion
                 | expresion OR expresion'''
    op_tipo = p.slice[2].type
    lp = p.lexpos(2)
    col = lp - _ultimo_codigo[0].rfind("\n", 0, lp) if lp else 0
    op_tok = {
        "tipo": op_tipo,
        "valor": _OP_TIPOS.get(op_tipo, str(p[2])),
        "linea": p.lineno(2),
        "columna": col,
    }
    p[0] = {"type": "BinaryOp", "op": op_tok, "left": p[1], "right": p[3]}


def p_expresion_not(p):
    '''expresion : NOT expresion'''
    op_tok = {"tipo": "NOT", "valor": "!", "linea": p.lineno(1), "columna": 0}
    p[0] = {"type": "UnaryOp", "op": op_tok, "operand": p[2]}


def p_expresion_umenos(p):
    '''expresion : MENOS expresion %prec UMENOS'''
    op_tok = {"tipo": "MENOS", "valor": "-", "linea": p.lineno(1), "columna": 0}
    p[0] = {"type": "UnaryOp", "op": op_tok, "operand": p[2]}


def p_expresion_paren(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = {"type": "Group", "expr": p[2]}


def p_expresion_entero(p):
    '''expresion : NUMERO_ENTERO'''
    tok = _tok_de_p(p, 1, tipo="NUMERO_ENTERO")
    p[0] = {"type": "Literal", "token": tok}


def p_expresion_decimal(p):
    '''expresion : NUMERO_DECIMAL'''
    tok = _tok_de_p(p, 1, tipo="NUMERO_DECIMAL")
    p[0] = {"type": "Literal", "token": tok}


def p_expresion_cadena(p):
    '''expresion : CADENA_LITERAL'''
    tok = _tok_de_p(p, 1, tipo="CADENA_LITERAL")
    p[0] = {"type": "StringLit", "token": tok}


def p_expresion_verdadero(p):
    '''expresion : VERDADERO'''
    tok = _tok_de_p(p, 1, tipo="VERDADERO")
    p[0] = {"type": "BoolLit", "token": tok}


def p_expresion_falso(p):
    '''expresion : FALSO'''
    tok = _tok_de_p(p, 1, tipo="FALSO")
    p[0] = {"type": "BoolLit", "token": tok}


def p_expresion_id(p):
    '''expresion : IDENTIFICADOR'''
    tok = _tok_de_p(p, 1, tipo="IDENTIFICADOR")
    p[0] = {"type": "Identifier", "token": tok}


def p_error(p):
    if p:
        col = encontrar_columna(_ultimo_codigo[0], p)
        _err_mod.agregar_sintactico(
            f"Token inesperado '{p.value}'", p.lineno, col, valor=str(p.value),
        )
    else:
        _err_mod.agregar_sintactico("Fin de archivo inesperado", 0, 0)


# Construir el parser una sola vez (no escribir tablas a disco)
_parser_global = yacc.yacc(write_tables=False, debug=False, errorlog=_NullLogger())


def build_tree(tokens, errors=None):
    """Parsea el codigo fuente que el lexer dejo cargado y devuelve un AST.

    Los errores sintacticos se acumulan en el modulo `errores`. Si el
    caller pasa `errors`, se actualiza in-place al final con todos
    los errores acumulados hasta el momento.
    """
    codigo = _ultimo_codigo[0]
    if not codigo:
        return {"type": "Program", "children": []}

    lex_obj = _lex_mod.get_ply_lexer()
    lex_obj.lineno = 1
    try:
        ast = _parser_global.parse(codigo, lexer=lex_obj)
    except Exception as e:
        _err_mod.agregar_sintactico(f"Error interno del parser: {e}", 0, 0)
        ast = {"type": "Program", "children": []}

    if errors is not None:
        del errors[:]
        errors.extend(_err_mod.todos())
    return ast if ast else {"type": "Program", "children": []}


# Get_kids y node_label: identicos a la version anterior, ya que el AST
# mantiene el mismo formato de dicts.

def get_kids(node):
    if not node:
        return []
    t = node.get("type", "")
    if t == "Program":
        return [c for c in node.get("children", []) if c]
    if t == "Block":
        return [c for c in node.get("stmts", []) if c]
    if t == "Declaration":
        c = []
        if node.get("dataType"):
            c.append({"type": "Token", "token": node["dataType"], "_label": "Tipo"})
        if node.get("id"):
            c.append({"type": "Token", "token": node["id"], "_label": "ID"})
        if node.get("expr"):
            c.append({**node["expr"], "_label": "valor"})
        return c
    if t == "Assignment":
        c = []
        if node.get("id"):
            c.append({"type": "Identifier", "token": node["id"], "_label": "var"})
        if node.get("expr"):
            c.append({**node["expr"], "_label": "expr"})
        return c
    if t == "If":
        c = []
        if node.get("cond"):
            c.append({**node["cond"], "_label": "cond"})
        if node.get("body"):
            c.append({**node["body"], "_label": "then"})
        if node.get("elseBody"):
            c.append({**node["elseBody"], "_label": "sino"})
        return c
    if t == "While":
        c = []
        if node.get("cond"):
            c.append({**node["cond"], "_label": "cond"})
        if node.get("body"):
            c.append(node["body"])
        return c
    if t == "DoWhile":
        c = []
        if node.get("body"):
            c.append({**node["body"], "_label": "cuerpo"})
        if node.get("cond"):
            c.append({**node["cond"], "_label": "cond"})
        return c
    if t == "For":
        c = []
        if node.get("init"):
            c.append({**node["init"], "_label": "init"})
        if node.get("cond"):
            c.append({**node["cond"], "_label": "cond"})
        if node.get("updId"):
            c.append({"type": "Identifier", "token": node["updId"], "_label": "upd"})
        if node.get("body"):
            c.append(node["body"])
        return c
    if t == "Print":
        args = node.get("args")
        if args:
            return [{**a, "_label": f"arg{i+1}"} for i, a in enumerate(args) if a]
        return [{**node["arg"], "_label": "arg"}] if node.get("arg") else []
    if t == "Read":
        return [{"type": "Identifier", "token": node["id"], "_label": "var"}] if node.get("id") else []
    if t == "BinaryOp":
        c = []
        if node.get("left"):
            c.append({**node["left"], "_label": "izq"})
        if node.get("right"):
            c.append({**node["right"], "_label": "der"})
        return c
    if t == "UnaryOp":
        return [node["operand"]] if node.get("operand") else []
    if t == "Group":
        return [node["expr"]] if node.get("expr") else []
    return []


def node_label(node):
    t = node.get("type", "")
    tok = node.get("token") or node.get("kw")
    val = tok["valor"] if tok else ""
    if t == "Program":
        return "PROGRAMA"
    if t == "Block":
        return "BLOQUE"
    if t == "Declaration":
        dt = node.get("dataType") or {}
        id_ = node.get("id") or {}
        return ("DECL " + dt.get("valor", "") + " " + id_.get("valor", "")).strip()
    if t == "Assignment":
        id_ = node.get("id") or {}
        return ("ASIG " + id_.get("valor", "")).strip()
    if t == "If":
        return "SI"
    if t == "While":
        return "MIENTRAS"
    if t == "DoWhile":
        return "HACER-MIENTRAS"
    if t == "For":
        return "PARA"
    if t == "Print":
        return "IMPRIMIR"
    if t == "Read":
        return "LEER"
    if t == "BinaryOp":
        op = node.get("op") or {}
        return "OP  " + op.get("valor", "?")
    if t == "UnaryOp":
        op = node.get("op") or {}
        return "UNARIO " + op.get("valor", "?")
    if t == "Group":
        return "( expr )"
    if t == "StringLit":
        return '"' + val[:10] + ("..." if len(val) > 10 else "") + '"'
    return val[:14] if val else t


# ----------------------------- Analisis semantico ------------------------

_TIPO_VAR_DE_TOKEN = {
    "ENTERO": "entero",
    "DECIMAL": "decimal",
    "CADENA_TIPO": "cadena",
    "BOOLEANO": "booleano",
}


def _tipo_literal(tok):
    tt = tok["tipo"]
    if tt == "NUMERO_ENTERO":
        return "entero"
    if tt == "NUMERO_DECIMAL":
        return "decimal"
    if tt == "CADENA_LITERAL":
        return "cadena"
    if tt in ("VERDADERO", "FALSO"):
        return "booleano"
    return None


def _tipo_compatible(declarado, expresion):
    if declarado == expresion:
        return True
    if declarado == "decimal" and expresion == "entero":
        return True   # widening
    return False


def check_semantic(ast, tabla, errors=None):
    """Recorre el AST y agrega errores semanticos al modulo errores.

    Si el caller pasa `errors`, lo actualiza in-place al final con
    todos los errores acumulados (lex + sint + sem) ordenados.
    """
    # Track de identificadores ya usados para evitar errores repetidos
    _no_decl_reportadas = set()

    def _sem(msg, linea, col=0, valor=""):
        _err_mod.agregar_semantico(msg, linea, col, valor=valor)

    def get_type(node):
        if not node:
            return None
        t = node.get("type", "")
        if t == "Literal":
            return _tipo_literal(node["token"])
        if t == "StringLit":
            return "cadena"
        if t == "BoolLit":
            return "booleano"
        if t == "Identifier":
            tok = node["token"]
            sym = tabla.buscar(tok["valor"])
            if not sym:
                key = (tok["valor"], tok["linea"], tok["columna"])
                if key not in _no_decl_reportadas:
                    _no_decl_reportadas.add(key)
                    _sem(f"Variable '{tok['valor']}' no declarada",
                         tok["linea"], tok["columna"], valor=tok["valor"])
                return None
            return sym.tipo
        if t == "BinaryOp":
            lt = get_type(node["left"])
            rt = get_type(node["right"])
            op = node["op"]["tipo"]
            op_lin = node["op"]["linea"]
            op_col = node["op"].get("columna", 0)
            op_val = node["op"]["valor"]
            if op in ("DIVIDIR", "MODULO"):
                rnode = node["right"]
                if rnode and rnode.get("type") == "Literal":
                    try:
                        if float(rnode["token"]["valor"]) == 0:
                            _sem(f"Division por cero (operador '{op_val}')",
                                 op_lin, op_col, valor=op_val)
                    except (ValueError, TypeError):
                        pass
            if op in ("MAS", "MENOS", "MULTIPLICACION", "DIVIDIR", "MODULO"):
                if lt is None or rt is None:
                    return None
                if lt == "entero" and rt == "entero":
                    return "entero"
                if lt in ("entero", "decimal") and rt in ("entero", "decimal"):
                    return "decimal"
                _sem(f"Operacion aritmetica '{op_val}' incompatible entre '{lt}' y '{rt}'",
                     op_lin, op_col, valor=op_val)
                return None
            if op in ("IGUAL", "DIFERENTE", "MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL"):
                if lt is None or rt is None:
                    return None
                if lt in ("entero", "decimal") and rt in ("entero", "decimal"):
                    return "booleano"
                if lt == "cadena" and rt == "cadena" and op in ("IGUAL", "DIFERENTE"):
                    return "booleano"
                if lt == "booleano" and rt == "booleano" and op in ("IGUAL", "DIFERENTE"):
                    return "booleano"
                _sem(f"Comparacion '{op_val}' incompatible entre '{lt}' y '{rt}'",
                     op_lin, op_col, valor=op_val)
                return None
            if op in ("AND", "OR"):
                if lt is None or rt is None:
                    return None
                if lt == "booleano" and rt == "booleano":
                    return "booleano"
                _sem(f"Operacion logica '{op_val}' incompatible entre '{lt}' y '{rt}'",
                     op_lin, op_col, valor=op_val)
                return None
        if t == "UnaryOp":
            ot = get_type(node["operand"])
            op = node["op"]["tipo"]
            op_lin = node["op"]["linea"]
            op_col = node["op"].get("columna", 0)
            op_val = node["op"]["valor"]
            if op in ("MENOS", "MAS"):
                if ot is None:
                    return None
                if ot in ("entero", "decimal"):
                    return ot
                _sem(f"Operador unario '{op_val}' incompatible con '{ot}'",
                     op_lin, op_col, valor=op_val)
                return None
            if op == "NOT":
                if ot is None:
                    return None
                if ot == "booleano":
                    return "booleano"
                _sem(f"Operador '!' incompatible con '{ot}'",
                     op_lin, op_col, valor=op_val)
                return None
        if t == "Group":
            return get_type(node["expr"])
        return None

    def check_node(node):
        if not node:
            return
        t = node.get("type", "")
        if t == "Declaration":
            dt = node["dataType"]
            id_tok = node.get("id") or {}
            if node.get("expr"):
                et = get_type(node["expr"])
                vt = _TIPO_VAR_DE_TOKEN.get(dt["tipo"], dt["valor"])
                if et and not _tipo_compatible(vt, et):
                    _sem(
                        f"Asignacion incompatible: variable '{id_tok.get('valor','?')}' "
                        f"de tipo '{vt}' no puede recibir un valor '{et}'",
                        dt["linea"], dt.get("columna", 0),
                        valor=id_tok.get("valor", ""),
                    )
        elif t == "Assignment":
            id_tok = node["id"]
            sym = tabla.buscar(id_tok["valor"])
            if not sym:
                _sem(f"Variable '{id_tok['valor']}' no declarada",
                     id_tok["linea"], id_tok["columna"],
                     valor=id_tok["valor"])
                get_type(node["expr"])
            else:
                et = get_type(node["expr"])
                if et and not _tipo_compatible(sym.tipo, et):
                    _sem(
                        f"Asignacion incompatible: variable '{id_tok['valor']}' "
                        f"de tipo '{sym.tipo}' no puede recibir un valor '{et}'",
                        id_tok["linea"], id_tok["columna"],
                        valor=id_tok["valor"],
                    )
        elif t == "Print":
            for a in node.get("args", []):
                get_type(a)
        elif t == "Read":
            id_tok = node["id"]
            if not tabla.buscar(id_tok["valor"]):
                _sem(f"Variable '{id_tok['valor']}' no declarada",
                     id_tok["linea"], id_tok["columna"],
                     valor=id_tok["valor"])
        elif t == "If":
            ct = get_type(node["cond"])
            if ct and ct != "booleano":
                _sem(f"La condicion del 'si' debe ser booleana, no '{ct}'",
                     node["kw"]["linea"], node["kw"].get("columna", 0))
            check_node(node["body"])
            if node.get("elseBody"):
                check_node(node["elseBody"])
        elif t == "While":
            ct = get_type(node["cond"])
            if ct and ct != "booleano":
                _sem(f"La condicion del 'mientras' debe ser booleana, no '{ct}'",
                     node["kw"]["linea"], node["kw"].get("columna", 0))
            check_node(node["body"])
        elif t == "DoWhile":
            check_node(node["body"])
            ct = get_type(node["cond"])
            if ct and ct != "booleano":
                _sem(f"La condicion del 'hacer_mientras' debe ser booleana, no '{ct}'",
                     node["kw"]["linea"], node["kw"].get("columna", 0))
        elif t == "For":
            check_node(node.get("init"))
            ct = get_type(node.get("cond"))
            if ct and ct != "booleano":
                _sem(f"La condicion del 'para' debe ser booleana, no '{ct}'",
                     node["kw"]["linea"], node["kw"].get("columna", 0))
            upd_id = node.get("updId")
            upd_expr = node.get("updExpr")
            if upd_id and upd_expr is not None:
                sym = tabla.buscar(upd_id["valor"])
                if not sym:
                    _sem(f"Variable '{upd_id['valor']}' no declarada (paso del 'para')",
                         upd_id["linea"], upd_id["columna"],
                         valor=upd_id["valor"])
                    get_type(upd_expr)
                else:
                    ut = get_type(upd_expr)
                    if ut and not _tipo_compatible(sym.tipo, ut):
                        _sem(
                            f"Asignacion incompatible en 'para': '{sym.tipo}' "
                            f"no puede recibir '{ut}'",
                            upd_id["linea"], upd_id["columna"],
                            valor=upd_id["valor"],
                        )
            check_node(node["body"])
        elif t == "Block":
            for s in node.get("stmts", []):
                check_node(s)
        elif t == "Program":
            for c in node.get("children", []):
                check_node(c)

    check_node(ast)

    if errors is not None:
        del errors[:]
        errors.extend(_err_mod.todos())
