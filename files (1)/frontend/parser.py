
RESERVED = {
    "int": "INT", "float": "FLOAT", "string": "STRING", "boolean": "BOOLEAN",
    "if": "IF", "else": "ELSE", "while": "WHILE", "for": "FOR", "return": "RETURN",
    "true": "TRUE", "false": "FALSE", "print": "PRINT", "input": "INPUT",
    "and": "AND", "or": "OR", "not": "NOT", "null": "NULL",
}
TIPOS_DATO = {"INT", "FLOAT", "STRING", "BOOLEAN"}

def build_tree(tokens):
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
        return None

    def parse_program():
        stmts = []
        while pos[0] < len(toks):
            s = parse_stmt()
            if s:
                stmts.append(s)
            else:
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
        tok = consume()
        return {"type": "Unknown", "token": tok}

    def parse_decl():
        dt = consume()
        id_ = consume() if peek() and peek()["tipo"] == "ID" else None
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
        upd_id = consume() if peek() and peek()["tipo"] == "ID" else None
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
        arg = parse_expr()
        expect("PAREN_DER")
        expect("PUNTO_COMA")
        return {"type": "Print", "kw": kw, "arg": arg}

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
        while peek() and peek()["tipo"] == "O_LOGICO":
            op = consume()
            r = parse_and()
            l = {"type": "BinaryOp", "op": op, "left": l, "right": r}
        return l

    def parse_and():
        l = parse_eq()
        while peek() and peek()["tipo"] == "Y_LOGICO":
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
        if peek() and peek()["tipo"] == "NO_LOGICO":
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
        if t["tipo"] in ("TRUE", "FALSE", "NULL"):
            return {"type": "BoolLit", "token": consume()}
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
        return {"type": "Token", "token": consume()}

    return parse_program()

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
