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
                 | declaracion_arreglo
                 | declaracion_funcion
                 | asignacion
                 | asignacion_arreglo
                 | sentencia_si
                 | sentencia_mientras
                 | sentencia_hacer_mientras
                 | sentencia_para
                 | sentencia_imprimir
                 | sentencia_leer
                 | sentencia_retornar
                 | sentencia_llamada'''
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


def p_declaracion_arreglo(p):
    '''declaracion_arreglo : ARREGLO tipo IDENTIFICADOR LCORCHETE NUMERO_ENTERO RCORCHETE PUNTO_COMA'''
    p[0] = {
        "type": "ArrayDeclaration",
        "dataType": p[2],
        "id": _tok_de_p(p, 3, tipo="IDENTIFICADOR"),
        "size": _tok_de_p(p, 5, tipo="NUMERO_ENTERO"),
    }


def p_declaracion_funcion(p):
    '''declaracion_funcion : FUNCION tipo IDENTIFICADOR LPAREN parametros_opt RPAREN LLAVE_IZQ sentencias LLAVE_DER
                           | PROCEDIMIENTO IDENTIFICADOR LPAREN parametros_opt RPAREN LLAVE_IZQ sentencias LLAVE_DER'''
    if p.slice[1].type == "FUNCION":
        p[0] = {
            "type": "FunctionDecl",
            "kind": "function",
            "kw": _tok_de_p(p, 1, tipo="FUNCION"),
            "returnType": p[2],
            "id": _tok_de_p(p, 3, tipo="IDENTIFICADOR"),
            "params": p[5],
            "body": {"type": "Block", "stmts": p[8]},
        }
    else:
        p[0] = {
            "type": "FunctionDecl",
            "kind": "procedure",
            "kw": _tok_de_p(p, 1, tipo="PROCEDIMIENTO"),
            "returnType": None,
            "id": _tok_de_p(p, 2, tipo="IDENTIFICADOR"),
            "params": p[4],
            "body": {"type": "Block", "stmts": p[7]},
        }


def p_parametros_opt(p):
    '''parametros_opt : parametros
                      | empty'''
    p[0] = p[1] or []


def p_parametros_lista(p):
    '''parametros : parametros COMA parametro'''
    p[0] = p[1] + [p[3]]


def p_parametros_uno(p):
    '''parametros : parametro'''
    p[0] = [p[1]]


def p_parametro_scalar(p):
    '''parametro : tipo IDENTIFICADOR'''
    p[0] = {
        "type": "Param",
        "dataType": p[1],
        "id": _tok_de_p(p, 2, tipo="IDENTIFICADOR"),
        "isArray": False,
    }


def p_parametro_arreglo(p):
    '''parametro : ARREGLO tipo IDENTIFICADOR'''
    p[0] = {
        "type": "Param",
        "dataType": p[2],
        "id": _tok_de_p(p, 3, tipo="IDENTIFICADOR"),
        "isArray": True,
    }


# Asignacion
def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    p[0] = {
        "type": "Assignment",
        "id": _tok_de_p(p, 1, tipo="IDENTIFICADOR"),
        "expr": p[3],
    }


def p_asignacion_arreglo(p):
    '''asignacion_arreglo : acceso_arreglo ASIGNAR expresion PUNTO_COMA'''
    p[0] = {
        "type": "ArrayAssignment",
        "target": p[1],
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
    '''sentencia_leer : LEER LPAREN destino_lectura RPAREN PUNTO_COMA'''
    p[0] = {
        "type": "Read",
        "kw": _tok_de_p(p, 1, tipo="LEER"),
        "id": p[3] if p[3].get("type") != "ArrayAccess" else None,
        "target": p[3],
    }


def p_destino_lectura_id(p):
    '''destino_lectura : IDENTIFICADOR'''
    p[0] = {"type": "Identifier", "token": _tok_de_p(p, 1, tipo="IDENTIFICADOR")}


def p_destino_lectura_arreglo(p):
    '''destino_lectura : acceso_arreglo'''
    p[0] = p[1]


def p_sentencia_retornar(p):
    '''sentencia_retornar : RETORNAR expresion PUNTO_COMA
                          | RETORNAR PUNTO_COMA'''
    p[0] = {
        "type": "Return",
        "kw": _tok_de_p(p, 1, tipo="RETORNAR"),
        "expr": p[2] if len(p) == 4 else None,
    }


def p_sentencia_llamada(p):
    '''sentencia_llamada : llamada_funcion PUNTO_COMA'''
    p[0] = p[1]


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


def p_expresion_arreglo(p):
    '''expresion : acceso_arreglo'''
    p[0] = p[1]


def p_acceso_arreglo(p):
    '''acceso_arreglo : IDENTIFICADOR LCORCHETE expresion RCORCHETE'''
    p[0] = {
        "type": "ArrayAccess",
        "id": _tok_de_p(p, 1, tipo="IDENTIFICADOR"),
        "index": p[3],
    }


def p_expresion_llamada(p):
    '''expresion : llamada_funcion'''
    p[0] = p[1]


def p_llamada_funcion(p):
    '''llamada_funcion : IDENTIFICADOR LPAREN argumentos_llamada_opt RPAREN'''
    p[0] = {
        "type": "Call",
        "id": _tok_de_p(p, 1, tipo="IDENTIFICADOR"),
        "args": p[3],
    }


def p_argumentos_llamada_opt(p):
    '''argumentos_llamada_opt : argumentos_llamada
                              | empty'''
    p[0] = p[1] or []


def p_argumentos_llamada_lista(p):
    '''argumentos_llamada : argumentos_llamada COMA expresion'''
    p[0] = p[1] + [p[3]]


def p_argumentos_llamada_uno(p):
    '''argumentos_llamada : expresion'''
    p[0] = [p[1]]


def p_empty(p):
    '''empty :'''
    p[0] = None


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
    if not codigo or not codigo.strip():
        ast_vacio = {"type": "Program", "children": []}
        if errors is not None:
            del errors[:]
            errors.extend(_err_mod.todos())
        return ast_vacio

    # Si la lista de tokens (sin comentarios) es vacia, programa vacio valido
    toks_efectivos = [t for t in (tokens or [])
                       if t.get("tipo") not in ("NUEVA_LINEA", "ESPACIO", "COMENTARIO")]
    if not toks_efectivos:
        if errors is not None:
            del errors[:]
            errors.extend(_err_mod.todos())
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
    if t == "ArrayDeclaration":
        c = []
        if node.get("dataType"):
            c.append({"type": "Token", "token": node["dataType"], "_label": "Tipo"})
        if node.get("id"):
            c.append({"type": "Token", "token": node["id"], "_label": "ID"})
        if node.get("size"):
            c.append({"type": "Literal", "token": node["size"], "_label": "tam"})
        return c
    if t == "FunctionDecl":
        c = []
        if node.get("returnType"):
            c.append({"type": "Token", "token": node["returnType"], "_label": "ret"})
        if node.get("id"):
            c.append({"type": "Token", "token": node["id"], "_label": "ID"})
        for i, param in enumerate(node.get("params", [])):
            c.append({**param, "_label": f"param{i+1}"})
        if node.get("body"):
            c.append({**node["body"], "_label": "body"})
        return c
    if t == "Param":
        c = []
        if node.get("dataType"):
            c.append({"type": "Token", "token": node["dataType"], "_label": "Tipo"})
        if node.get("id"):
            c.append({"type": "Token", "token": node["id"], "_label": "ID"})
        return c
    if t == "Assignment":
        c = []
        if node.get("id"):
            c.append({"type": "Identifier", "token": node["id"], "_label": "var"})
        if node.get("expr"):
            c.append({**node["expr"], "_label": "expr"})
        return c
    if t == "ArrayAssignment":
        c = []
        if node.get("target"):
            c.append({**node["target"], "_label": "dest"})
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
        if node.get("target"):
            return [{**node["target"], "_label": "var"}]
        return [{"type": "Identifier", "token": node["id"], "_label": "var"}] if node.get("id") else []
    if t == "Return":
        return [{**node["expr"], "_label": "valor"}] if node.get("expr") else []
    if t == "Call":
        return [{**a, "_label": f"arg{i+1}"} for i, a in enumerate(node.get("args", [])) if a]
    if t == "ArrayAccess":
        return [{**node["index"], "_label": "idx"}] if node.get("index") else []
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
    if t == "ArrayDeclaration":
        dt = node.get("dataType") or {}
        id_ = node.get("id") or {}
        sz = node.get("size") or {}
        return (f"ARREGLO {dt.get('valor', '')} {id_.get('valor', '')}[{sz.get('valor', '')}]").strip()
    if t == "FunctionDecl":
        id_ = node.get("id") or {}
        return ("FUNC " if node.get("kind") == "function" else "PROC ") + id_.get("valor", "")
    if t == "Param":
        id_ = node.get("id") or {}
        dt = node.get("dataType") or {}
        pref = "arr " if node.get("isArray") else ""
        return ("PARAM " + pref + dt.get("valor", "") + " " + id_.get("valor", "")).strip()
    if t == "Assignment":
        id_ = node.get("id") or {}
        return ("ASIG " + id_.get("valor", "")).strip()
    if t == "ArrayAssignment":
        id_ = (node.get("target") or {}).get("id") or {}
        return ("ASIG " + id_.get("valor", "") + "[]").strip()
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
    if t == "Return":
        return "RETORNAR"
    if t == "Call":
        id_ = node.get("id") or {}
        return ("CALL " + id_.get("valor", "")).strip()
    if t == "ArrayAccess":
        id_ = node.get("id") or {}
        return (id_.get("valor", "") + "[]").strip()
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


def _tipo_desde_token(tok):
    return _TIPO_VAR_DE_TOKEN.get(tok.get("tipo"), tok.get("valor"))


def _firma_parametro(param):
    tipo = _tipo_desde_token(param.get("dataType") or {})
    return {
        "nombre": (param.get("id") or {}).get("valor", ""),
        "tipo": tipo,
        "kind": "array" if param.get("isArray") else "variable",
        "elem_type": tipo if param.get("isArray") else None,
    }


def check_semantic(ast, tabla, errors=None):
    """Recorre el AST y agrega errores semanticos al modulo errores.

    Si el caller pasa `errors`, lo actualiza in-place al final con
    todos los errores acumulados (lex + sint + sem) ordenados.

    La tabla de simbolos se llena AQUI (desde el AST), abriendo y
    cerrando ambitos en cada bloque (si/sino/mientras/para/bloque).
    Esto reemplaza la pre-carga ingenua que hacia el lexer a nivel de
    tokens, la cual no entendia scopes.
    """
    # Reinicio: cada ambito anidado se trackea correctamente.
    tabla.limpiar()
    # Track de identificadores ya usados para evitar errores repetidos
    _no_decl_reportadas = set()

    # Pre-scan: linea minima de declaracion por nombre (ignora scopes).
    # Sirve unicamente para distinguir "usada antes de declarar" de
    # "no declarada". No se usa para resolucion de simbolos (eso lo hace
    # la tabla con scopes reales).
    _decl_lineas: dict[str, int] = {}

    def _prescan(node):
        if not node:
            return
        t = node.get("type", "")
        if t in ("Declaration", "ArrayDeclaration", "FunctionDecl"):
            id_tok = node.get("id") or {}
            nombre = id_tok.get("valor", "")
            linea = id_tok.get("linea", node.get("dataType", {}).get("linea", 0))
            if nombre and (nombre not in _decl_lineas or linea < _decl_lineas[nombre]):
                _decl_lineas[nombre] = linea
        for v in node.values():
            if isinstance(v, dict):
                _prescan(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        _prescan(it)

    _prescan(ast)

    def _sem(msg, linea, col=0, valor=""):
        _err_mod.agregar_semantico(msg, linea, col, valor=valor)

    _funcion_actual = []

    def _registrar_funciones_globales(node):
        if not node:
            return
        if node.get("type") == "FunctionDecl":
            id_tok = node.get("id") or {}
            nombre = id_tok.get("valor", "")
            if nombre:
                ret = _tipo_desde_token(node["returnType"]) if node.get("returnType") else "void"
                params = [_firma_parametro(p) for p in node.get("params", [])]
                tipo = "funcion" if node.get("kind") == "function" else "procedimiento"
                tabla.insertar(
                    nombre,
                    tipo,
                    id_tok.get("linea", node.get("kw", {}).get("linea", 0)),
                    columna=id_tok.get("columna", 0),
                    kind="function",
                    params=params,
                    return_type=ret,
                )
            return
        for v in node.values():
            if isinstance(v, dict):
                _registrar_funciones_globales(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        _registrar_funciones_globales(it)

    _registrar_funciones_globales(ast)

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
                # Distinguir "declarada mas adelante" de "no declarada del todo".
                decl_linea = _decl_lineas.get(tok["valor"])
                key = (tok["valor"], tok["linea"], tok["columna"])
                if key not in _no_decl_reportadas:
                    _no_decl_reportadas.add(key)
                    if decl_linea is not None and decl_linea > tok["linea"]:
                        _sem(
                            f"Variable '{tok['valor']}' usada antes de ser declarada "
                            f"(declarada en linea {decl_linea})",
                            tok["linea"], tok["columna"], valor=tok["valor"],
                        )
                    else:
                        _sem(f"Variable '{tok['valor']}' no declarada",
                             tok["linea"], tok["columna"], valor=tok["valor"])
                return None
            if getattr(sym, "kind", "variable") == "function":
                _sem(f"Funcion o procedimiento '{tok['valor']}' usado sin llamada",
                     tok["linea"], tok["columna"], valor=tok["valor"])
                return None
            if getattr(sym, "kind", "variable") == "array":
                return f"arreglo:{sym.elem_type}"
            return sym.tipo
        if t == "ArrayAccess":
            id_tok = node["id"]
            sym = tabla.buscar(id_tok["valor"])
            if not sym:
                _sem(f"Arreglo '{id_tok['valor']}' no declarado",
                     id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                get_type(node.get("index"))
                return None
            if getattr(sym, "kind", "variable") != "array":
                _sem(f"Identificador '{id_tok['valor']}' no es un arreglo",
                     id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                get_type(node.get("index"))
                return None
            it = get_type(node.get("index"))
            if it and it != "entero":
                _sem(f"Indice de arreglo '{id_tok['valor']}' debe ser entero, no '{it}'",
                     id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
            idx = node.get("index")
            if idx and idx.get("type") == "Literal":
                try:
                    n = int(idx["token"]["valor"])
                    if n < 0 or (sym.size is not None and n >= sym.size):
                        _sem(f"Indice {n} fuera de rango para arreglo '{id_tok['valor']}' de tamano {sym.size}",
                             id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                except (TypeError, ValueError):
                    pass
            return sym.elem_type or sym.tipo
        if t == "Call":
            id_tok = node["id"]
            sym = tabla.buscar(id_tok["valor"])
            if not sym or getattr(sym, "kind", "variable") != "function":
                _sem(f"Funcion o procedimiento '{id_tok['valor']}' no declarado",
                     id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                for arg in node.get("args", []):
                    get_type(arg)
                return None
            params = getattr(sym, "params", []) or []
            args = node.get("args", [])
            if len(args) != len(params):
                _sem(
                    f"Llamada a '{id_tok['valor']}' espera {len(params)} argumento(s), recibio {len(args)}",
                    id_tok["linea"], id_tok["columna"], valor=id_tok["valor"],
                )
            for i, arg in enumerate(args):
                at = get_type(arg)
                if i >= len(params) or at is None:
                    continue
                esperado = params[i]
                if esperado.get("kind") == "array":
                    if not (isinstance(at, str) and at.startswith("arreglo:")):
                        _sem(f"Argumento {i + 1} de '{id_tok['valor']}' debe ser arreglo",
                             id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                    elif at.split(":", 1)[1] != esperado.get("elem_type"):
                        _sem(f"Argumento {i + 1} de '{id_tok['valor']}' espera arreglo de '{esperado.get('elem_type')}', recibio '{at.split(':', 1)[1]}'",
                             id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                elif isinstance(at, str) and at.startswith("arreglo:"):
                    _sem(f"Argumento {i + 1} de '{id_tok['valor']}' no debe ser arreglo",
                         id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
                elif not _tipo_compatible(esperado.get("tipo"), at):
                    _sem(f"Argumento {i + 1} de '{id_tok['valor']}' espera '{esperado.get('tipo')}', recibio '{at}'",
                         id_tok["linea"], id_tok["columna"], valor=id_tok["valor"])
            if getattr(sym, "return_type", None) == "void":
                return None
            return sym.return_type
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
            vt = _tipo_desde_token(dt)
            # Registrar en la tabla ANTES de chequear el tipo de la expresion
            # (asi `entero x = x + 1;` reporta correctamente uso de x).
            nombre = id_tok.get("valor", "")
            if nombre:
                tabla.insertar(
                    nombre, vt,
                    id_tok.get("linea", dt["linea"]),
                    columna=id_tok.get("columna", 0),
                )
            if node.get("expr"):
                et = get_type(node["expr"])
                if et and not _tipo_compatible(vt, et):
                    _sem(
                        f"Asignacion incompatible: variable '{id_tok.get('valor','?')}' "
                        f"de tipo '{vt}' no puede recibir un valor '{et}'",
                        dt["linea"], dt.get("columna", 0),
                        valor=id_tok.get("valor", ""),
                    )
        elif t == "ArrayDeclaration":
            dt = node["dataType"]
            id_tok = node.get("id") or {}
            size_tok = node.get("size") or {}
            vt = _tipo_desde_token(dt)
            try:
                size = int(size_tok.get("valor", 0))
            except (TypeError, ValueError):
                size = 0
            if size <= 0:
                _sem(f"El arreglo '{id_tok.get('valor','?')}' debe tener tamano mayor que cero",
                     size_tok.get("linea", dt["linea"]), size_tok.get("columna", 0),
                     valor=id_tok.get("valor", ""))
            nombre = id_tok.get("valor", "")
            if nombre:
                tabla.insertar(
                    nombre,
                    f"arreglo {vt}",
                    id_tok.get("linea", dt["linea"]),
                    columna=id_tok.get("columna", 0),
                    kind="array",
                    elem_type=vt,
                    size=size,
                    valor=f"[{size}]",
                )
        elif t == "FunctionDecl":
            ret = _tipo_desde_token(node["returnType"]) if node.get("returnType") else "void"
            id_tok = node.get("id") or {}
            tabla.entrar_ambito()
            _funcion_actual.append({"nombre": id_tok.get("valor", ""), "ret": ret, "tiene_return": False})
            for param in node.get("params", []):
                p_id = param.get("id") or {}
                p_tipo = _tipo_desde_token(param.get("dataType") or {})
                tabla.insertar(
                    p_id.get("valor", ""),
                    f"arreglo {p_tipo}" if param.get("isArray") else p_tipo,
                    p_id.get("linea", id_tok.get("linea", 0)),
                    columna=p_id.get("columna", 0),
                    kind="array" if param.get("isArray") else "variable",
                    elem_type=p_tipo if param.get("isArray") else None,
                    size=None,
                )
            check_node(node.get("body"))
            info = _funcion_actual.pop()
            if ret != "void" and not info["tiene_return"]:
                _sem(f"Funcion '{info['nombre']}' debe retornar un valor de tipo '{ret}'",
                     id_tok.get("linea", 0), id_tok.get("columna", 0), valor=info["nombre"])
            tabla.salir_ambito()
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
        elif t == "ArrayAssignment":
            target = node.get("target") or {}
            id_tok = target.get("id") or {}
            sym = tabla.buscar(id_tok.get("valor", ""))
            if not sym:
                _sem(f"Arreglo '{id_tok.get('valor','?')}' no declarado",
                     id_tok.get("linea", 0), id_tok.get("columna", 0),
                     valor=id_tok.get("valor", ""))
                get_type(target.get("index"))
                get_type(node.get("expr"))
            elif getattr(sym, "kind", "variable") != "array":
                _sem(f"Identificador '{id_tok.get('valor','?')}' no es un arreglo",
                     id_tok.get("linea", 0), id_tok.get("columna", 0),
                     valor=id_tok.get("valor", ""))
                get_type(target.get("index"))
                get_type(node.get("expr"))
            else:
                get_type(target)
                et = get_type(node.get("expr"))
                if et and not _tipo_compatible(sym.elem_type, et):
                    _sem(
                        f"Asignacion incompatible: arreglo '{id_tok.get('valor','?')}' "
                        f"de elementos '{sym.elem_type}' no puede recibir '{et}'",
                        id_tok.get("linea", 0), id_tok.get("columna", 0),
                        valor=id_tok.get("valor", ""),
                    )
        elif t == "Print":
            for a in node.get("args", []):
                get_type(a)
        elif t == "Read":
            target = node.get("target")
            if target and target.get("type") == "ArrayAccess":
                get_type(target)
            else:
                id_tok = node.get("id") or (target or {}).get("token", {})
                if id_tok and id_tok.get("type") == "Identifier":
                    id_tok = id_tok.get("token", {})
                if id_tok and not tabla.buscar(id_tok["valor"]):
                    _sem(f"Variable '{id_tok['valor']}' no declarada",
                         id_tok["linea"], id_tok["columna"],
                         valor=id_tok["valor"])
        elif t == "Return":
            if not _funcion_actual:
                kw = node.get("kw", {})
                _sem("'retornar' solo puede usarse dentro de una funcion o procedimiento",
                     kw.get("linea", 0), kw.get("columna", 0), valor="retornar")
            else:
                actual = _funcion_actual[-1]
                actual["tiene_return"] = True
                et = get_type(node.get("expr")) if node.get("expr") else None
                if actual["ret"] == "void":
                    if node.get("expr"):
                        kw = node.get("kw", {})
                        _sem(f"Procedimiento '{actual['nombre']}' no debe retornar valor",
                             kw.get("linea", 0), kw.get("columna", 0), valor=actual["nombre"])
                elif not node.get("expr"):
                    kw = node.get("kw", {})
                    _sem(f"Funcion '{actual['nombre']}' debe retornar '{actual['ret']}'",
                         kw.get("linea", 0), kw.get("columna", 0), valor=actual["nombre"])
                elif et and not _tipo_compatible(actual["ret"], et):
                    kw = node.get("kw", {})
                    _sem(f"Funcion '{actual['nombre']}' debe retornar '{actual['ret']}', no '{et}'",
                         kw.get("linea", 0), kw.get("columna", 0), valor=actual["nombre"])
        elif t == "Call":
            get_type(node)
        elif t == "If":
            ct = get_type(node["cond"])
            if ct and ct != "booleano":
                _sem(f"La condicion del 'si' debe ser booleana, no '{ct}'",
                     node["kw"]["linea"], node["kw"].get("columna", 0))
            # El scope lo abre el Block que envuelve al body.
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
            # El 'para' define un scope propio para que el 'init' (ej:
            # `entero i = 0;`) viva durante init/cond/upd/body, pero NO
            # filtre al scope exterior. El body (Block) abrira otro scope
            # anidado encima de este.
            tabla.entrar_ambito()
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
            tabla.salir_ambito()
        elif t == "Block":
            # Bloques sueltos { ... } abren scope. Los cuerpos de
            # if/while/for ya estan envueltos por sus respectivas reglas,
            # asi que esto solo aporta scope extra para bloques anidados
            # standalone (poco comunes pero validos).
            tabla.entrar_ambito()
            for s in node.get("stmts", []):
                check_node(s)
            tabla.salir_ambito()
        elif t == "Program":
            for c in node.get("children", []):
                check_node(c)

    check_node(ast)

    if errors is not None:
        del errors[:]
        errors.extend(_err_mod.todos())
