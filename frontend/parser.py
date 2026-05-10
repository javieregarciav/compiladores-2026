
RESERVED = {
    "int": "INT", "float": "FLOAT", "string": "STRING", "boolean": "BOOLEAN",
    "if": "IF", "else": "ELSE", "while": "WHILE", "for": "FOR", "return": "RETURN",
    "true": "TRUE", "false": "FALSE", "print": "PRINT", "input": "INPUT",
    "and": "AND", "or": "OR", "not": "NOT", "null": "NULL",
}
TIPOS_DATO = {"INT", "FLOAT", "STRING", "BOOLEAN"}

def build_tree(tokens, errors=None):
    if errors is None:
        errors = []
    toks = [t for t in tokens if t["tipo"] not in ("NUEVA_LINEA", "ESPACIO", "COMENTARIO")]
    pos = [0]

    def peek(off=0):
        i = pos[0] + off
        return toks[i] if i < len(toks) else None

    def consume():
        t = toks[pos[0]] if pos[0] < len(toks) else None
        pos[0] += 1
        return t

    def expect(tipo):
        t = peek()
        if t and t["tipo"] == tipo:
            pos[0] += 1
            return t
        if t:
            errors.append(f"[Línea {t['linea']}, Col {t['columna']}] Se esperaba '{tipo}', pero se encontró '{t['tipo']}'")
        else:
            errors.append(f"Fin de archivo inesperado, se esperaba '{tipo}'")
        return None

    def parse_program():
        stmts = []
        while pos[0] < len(toks):
            antes = pos[0]
            s = parse_stmt()
            if s:
                stmts.append(s)
            elif pos[0] == antes:
                t = peek()
                errors.append(f"[Línea {t['linea']}, Col {t['columna']}] Token inesperado: '{t['tipo']}'")
                pos[0] += 1
        return {"type": "Program", "children": stmts}

    def parse_stmt():
        t = peek()
        if not t:
            return None
        if t["tipo"] in TIPOS_DATO:
            return parse_decl()
        if t["tipo"] == "IF":
            return parse_if()
        if t["tipo"] == "WHILE":
            return parse_while()
        if t["tipo"] == "FOR":
            return parse_for()
        if t["tipo"] in ("PRINT", "INPUT"):
            return parse_print()
        if t["tipo"] == "ID":
            n = peek(1)
            if n and n["tipo"] == "ASIGNACION":
                return parse_assign()
        if t["tipo"] == "LLAVE_IZQ":
            return parse_block()
        if t["tipo"] == "PUNTO_COMA":
            consume()
            return None
        # Unknown statement
        tok = consume()
        errors.append(f"[Línea {tok['linea']}, Col {tok['columna']}] Declaración inválida comenzando con '{tok['tipo']}'")
        return {"type": "Unknown", "token": tok}

    def parse_decl():
        dt = consume()
        id_ = expect("ID")
        expr = None
        if peek() and peek()["tipo"] == "ASIGNACION":
            consume()
            expr = parse_expr()
        expect("PUNTO_COMA")
        return {"type": "Declaration", "dataType": dt, "id": id_, "expr": expr}

    def parse_assign():
        id_ = consume()
        expect("ASIGNACION")
        expr = parse_expr()
        expect("PUNTO_COMA")
        return {"type": "Assignment", "id": id_, "expr": expr}

    def parse_if():
        kw = consume()
        expect("PAREN_IZQ")
        cond = parse_expr()
        expect("PAREN_DER")
        body = parse_block()
        else_body = None
        if peek() and peek()["tipo"] == "ELSE":
            consume()
            else_body = parse_block()
        return {"type": "If", "kw": kw, "cond": cond, "body": body, "elseBody": else_body}

    def parse_while():
        kw = consume()
        expect("PAREN_IZQ")
        cond = parse_expr()
        expect("PAREN_DER")
        body = parse_block()
        return {"type": "While", "kw": kw, "cond": cond, "body": body}

    def parse_for():
        kw = consume()
        expect("PAREN_IZQ")
        init = parse_stmt()
        cond = parse_expr()
        expect("PUNTO_COMA")
        upd_id = expect("ID")
        upd_expr = None
        if peek() and peek()["tipo"] == "ASIGNACION":
            consume()
            upd_expr = parse_expr()
        expect("PAREN_DER")
        body = parse_block()
        return {"type": "For", "kw": kw, "init": init, "cond": cond,
                "updId": upd_id, "updExpr": upd_expr, "body": body}

    def parse_print():
        kw = consume()
        expect("PAREN_IZQ")
        args = []
        if peek() and peek()["tipo"] != "PAREN_DER":
            args.append(parse_expr())
            while peek() and peek()["tipo"] == "COMA":
                consume()
                args.append(parse_expr())
        expect("PAREN_DER")
        expect("PUNTO_COMA")
        return {"type": "Print", "kw": kw, "args": args, "arg": args[0] if args else None}

    def parse_block():
        if peek() and peek()["tipo"] == "LLAVE_IZQ":
            consume()
            stmts = []
            while pos[0] < len(toks) and not (peek() and peek()["tipo"] == "LLAVE_DER"):
                s = parse_stmt()
                if s:
                    stmts.append(s)
            expect("LLAVE_DER")
            return {"type": "Block", "stmts": stmts}
        s = parse_stmt()
        return {"type": "Block", "stmts": [s] if s else []}

    def parse_expr():
        return parse_or()

    def parse_or():
        l = parse_and()
        while peek() and peek()["tipo"] in ("O_LOGICO", "OR"):
            op = consume()
            r = parse_and()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_and():
        l = parse_eq()
        while peek() and peek()["tipo"] in ("Y_LOGICO", "AND"):
            op = consume()
            r = parse_eq()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_eq():
        l = parse_rel()
        while peek() and peek()["tipo"] in ("IGUAL", "DIFERENTE"):
            op = consume()
            r = parse_rel()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_rel():
        l = parse_add()
        while peek() and peek()["tipo"] in ("MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL"):
            op = consume()
            r = parse_add()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_add():
        l = parse_mul()
        while peek() and peek()["tipo"] in ("MAS", "MENOS"):
            op = consume()
            r = parse_mul()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_mul():
        l = parse_unary()
        while peek() and peek()["tipo"] in ("MULT", "DIV", "MOD"):
            op = consume()
            r = parse_unary()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_unary():
        if peek() and peek()["tipo"] in ("NO_LOGICO", "NOT", "MENOS", "MAS"):
            op = consume()
            operand = parse_unary()
            return {"type": "UnaryOp", "op": op, "operand": operand}
        return parse_primary()

    def parse_primary():
        t = peek()
        if not t:
            return None
        if t["tipo"] == "PAREN_IZQ":
            consume()
            e = parse_expr()
            expect("PAREN_DER")
            return {"type": "Group", "expr": e}
        if t["tipo"] in ("ENTERO", "DECIMAL"):
            return {"type": "Literal", "token": consume()}
        if t["tipo"] == "CADENA":
            return {"type": "StringLit", "token": consume()}
        if t["tipo"] in ("TRUE", "FALSE"):
            return {"type": "BoolLit", "token": consume()}
        if t["tipo"] == "NULL":
            return {"type": "NullLit", "token": consume()}
        if t["tipo"] == "ID":
            id_ = consume()
            if peek() and peek()["tipo"] == "PAREN_IZQ":
                consume()
                args = []
                while peek() and peek()["tipo"] != "PAREN_DER":
                    args.append(parse_expr())
                    if peek() and peek()["tipo"] == "COMA":
                        consume()
                expect("PAREN_DER")
                return {"type": "Call", "id": id_, "args": args}
            return {"type": "Identifier", "token": id_}
        if t["tipo"] in TIPOS_DATO or t["tipo"] in (
            "IF", "ELSE", "WHILE", "FOR", "RETURN", "PRINT", "INPUT", "AND", "OR", "NOT"
        ):
            return {"type": "Keyword", "token": consume()}
        # Unknown token
        tok = consume()
        errors.append(f"[Línea {tok['linea']}, Col {tok['columna']}] Token desconocido: '{tok['tipo']}'")
        return {"type": "Token", "token": tok}

    ast = parse_program()
    return ast

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
            c.append({**node["elseBody"], "_label": "else"})
        return c
    if t == "While":
        c = []
        if node.get("cond"):
            c.append({**node["cond"], "_label": "cond"})
        if node.get("body"):
            c.append(node["body"])
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
    if t == "Call":
        return [a for a in node.get("args", []) if a]
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
        dt = (node.get("dataType") or {})
        id_ = (node.get("id") or {})
        return ("DECL " + dt.get("valor", "") + " " + id_.get("valor", "")).strip()
    if t == "Assignment":
        id_ = (node.get("id") or {})
        return ("ASIG " + id_.get("valor", "")).strip()
    if t == "If":
        return "IF"
    if t == "While":
        return "WHILE"
    if t == "For":
        return "FOR"
    if t == "Print":
        return "PRINT"
    if t == "Call":
        id_ = (node.get("id") or {})
        return id_.get("valor", "CALL") + "()"
    if t == "BinaryOp":
        op = (node.get("op") or {})
        return "OP  " + op.get("valor", "?")
    if t == "UnaryOp":
        return "UNARIO !"
    if t == "Group":
        return "( expr )"
    if t == "StringLit":
        return '"' + val[:10] + ("..." if len(val) > 10 else "") + '"'
    return val[:14] if val else t

def _tipo_compatible(declarado, expresion):
    if declarado == expresion:
        return True
    if declarado == "float" and expresion == "int":
        return True
    if declarado in ("string",) and expresion == "null":
        return True
    return False

def check_semantic(ast, tabla, errors):
    RESERVED_INV = {v: k for k, v in RESERVED.items()}
    def get_type(node):
        if not node:
            return None
        t = node.get("type", "")
        if t == "Literal":
            tok = node["token"]
            if tok["tipo"] == "ENTERO":
                return "int"
            elif tok["tipo"] == "DECIMAL":
                return "float"
            elif tok["tipo"] == "CADENA":
                return "string"
            elif tok["tipo"] in ("TRUE", "FALSE"):
                return "boolean"
        elif t == "StringLit":
            return "string"
        elif t == "BoolLit":
            return "boolean"
        elif t == "NullLit":
            return "null"
        elif t == "Identifier":
            tok = node["token"]
            sym = tabla.buscar(tok["valor"])
            if not sym:
                errors.append(f"[Línea {tok['linea']}, Col {tok['columna']}] Variable '{tok['valor']}' no declarada")
                return None
            return sym.tipo
        elif t == "BinaryOp":
            left_type = get_type(node["left"])
            right_type = get_type(node["right"])
            op = node["op"]["tipo"]
            if op in ("DIV", "MOD"):
                rnode = node["right"]
                if rnode.get("type") == "Literal":
                    rval = rnode["token"]["valor"]
                    try:
                        if float(rval) == 0:
                            errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] División por cero")
                    except (ValueError, TypeError):
                        pass
            if op in ("MAS", "MENOS", "MULT", "DIV", "MOD"):
                if left_type == "int" and right_type == "int":
                    return "int"
                elif (left_type in ("int", "float")) and (right_type in ("int", "float")):
                    return "float"
                else:
                    errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] Operación aritmética incompatible entre '{left_type}' y '{right_type}'")
                    return None
            elif op in ("IGUAL", "DIFERENTE", "MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL"):
                if (left_type in ("int", "float")) and (right_type in ("int", "float")):
                    return "boolean"
                elif left_type == "string" and right_type == "string" and op in ("IGUAL", "DIFERENTE"):
                    return "boolean"
                elif left_type == "boolean" and right_type == "boolean" and op in ("IGUAL", "DIFERENTE"):
                    return "boolean"
                else:
                    errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] Comparación incompatible entre '{left_type}' y '{right_type}'")
                    return None
            elif op in ("Y_LOGICO", "O_LOGICO", "AND", "OR"):
                if left_type == "boolean" and right_type == "boolean":
                    return "boolean"
                else:
                    errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] Operación lógica incompatible entre '{left_type}' y '{right_type}'")
                    return None
        elif t == "UnaryOp":
            operand_type = get_type(node["operand"])
            op = node["op"]["tipo"]
            if op in ("MENOS", "MAS"):
                if operand_type in ("int", "float"):
                    return operand_type
                else:
                    errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] Operador unario '{node['op']['valor']}' incompatible con '{operand_type}'")
                    return None
            elif op in ("NO_LOGICO", "NOT"):
                if operand_type == "boolean":
                    return "boolean"
                else:
                    errors.append(f"[Línea {node['op']['linea']}, Col {node['op']['columna']}] Operador '{node['op']['valor']}' incompatible con '{operand_type}'")
                    return None
        elif t == "Group":
            return get_type(node["expr"])
        elif t == "Call":
            id_tok = node["id"]
            for arg in node.get("args", []):
                get_type(arg)
            if id_tok["valor"] in ("print", "input"):
                return None
            else:
                errors.append(f"[Línea {id_tok['linea']}, Col {id_tok['columna']}] Función '{id_tok['valor']}' no definida")
                return None
        return None

    def check_node(node):
        if not node:
            return
        t = node.get("type", "")
        if t == "Declaration":
            dt_tok = node["dataType"]
            expr = node["expr"]
            if expr:
                expr_type = get_type(expr)
                var_type = RESERVED_INV.get(dt_tok["tipo"], dt_tok["tipo"].lower())
                if expr_type and not _tipo_compatible(var_type, expr_type):
                    errors.append(f"[Línea {dt_tok['linea']}, Col {dt_tok['columna']}] Asignación incompatible: '{var_type}' no puede asignar '{expr_type}'")
        elif t == "Assignment":
            id_tok = node["id"]
            expr = node["expr"]
            sym = tabla.buscar(id_tok["valor"])
            if not sym:
                errors.append(f"[Línea {id_tok['linea']}, Col {id_tok['columna']}] Variable '{id_tok['valor']}' no declarada")
                get_type(expr)
            else:
                expr_type = get_type(expr)
                if expr_type and not _tipo_compatible(sym.tipo, expr_type):
                    errors.append(f"[Línea {id_tok['linea']}, Col {id_tok['columna']}] Asignación incompatible: '{sym.tipo}' no puede asignar '{expr_type}'")
        elif t == "Print":
            for a in node.get("args", []):
                get_type(a)
        elif t == "If":
            cond = node["cond"]
            cond_type = get_type(cond)
            if cond_type and cond_type != "boolean":
                errors.append(f"[Línea {node['kw']['linea']}, Col {node['kw']['columna']}] Condición 'if' debe ser booleana, no '{cond_type}'")
            check_node(node["body"])
            if node.get("elseBody"):
                check_node(node["elseBody"])
        elif t == "While":
            cond = node["cond"]
            cond_type = get_type(cond)
            if cond_type and cond_type != "boolean":
                errors.append(f"[Línea {node['kw']['linea']}, Col {node['kw']['columna']}] Condición 'while' debe ser booleana, no '{cond_type}'")
            check_node(node["body"])
        elif t == "For":
            check_node(node.get("init"))
            cond = node.get("cond")
            if cond:
                cond_type = get_type(cond)
                if cond_type and cond_type != "boolean":
                    errors.append(f"[Línea {node['kw']['linea']}, Col {node['kw']['columna']}] Condición 'for' debe ser booleana, no '{cond_type}'")
            upd_id = node.get("updId")
            upd_expr = node.get("updExpr")
            if upd_id and upd_expr is not None:
                sym = tabla.buscar(upd_id["valor"])
                if not sym:
                    errors.append(f"[Línea {upd_id['linea']}, Col {upd_id['columna']}] Variable '{upd_id['valor']}' no declarada")
                    get_type(upd_expr)
                else:
                    upd_type = get_type(upd_expr)
                    if upd_type and not _tipo_compatible(sym.tipo, upd_type):
                        errors.append(f"[Línea {upd_id['linea']}, Col {upd_id['columna']}] Asignación incompatible: '{sym.tipo}' no puede asignar '{upd_type}'")
            check_node(node["body"])
        elif t == "Block":
            for s in node.get("stmts", []):
                check_node(s)
        elif t == "Program":
            for c in node.get("children", []):
                check_node(c)

    check_node(ast)
