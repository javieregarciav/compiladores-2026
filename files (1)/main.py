"""
main.py  —  Mini-Compilador v2.0
================================
IDE de escritorio (Tkinter) que replica la interfaz web neón:
  - Banner académico con los 4 integrantes
  - Header con logo
  - Pestañas: Editor / Tokens / Árbol Sint. / Semántico / Errores
  - Editor con syntax highlighting y numeración de líneas
  - Árbol sintáctico visual en Canvas (nodos coloreados + bezier)
  - Tabla de símbolos lateral permanente
  - Panel de estadísticas con cajas numéricas
  - Menú desplegable de 7 ejemplos (Toplevel flotante funcional)
  - Tema oscuro neón idéntico al HTML
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
import sys, os, re as _re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lexer import Lexer

# ══════════════════════════════════════════════════════════════════
#  PALETA DE COLORES (idéntica al CSS del navegador)
# ══════════════════════════════════════════════════════════════════
C = {
    "bg0": "#020408", "bg1": "#040810", "bg2": "#060d18",
    "bg3": "#0a1628", "bg4": "#0d1e35",
    "cyan":   "#00f5ff", "green":  "#00ff88",
    "amber":  "#ffb700", "red":    "#ff2d55",
    "purple": "#bf5af2", "blue":   "#0a84ff",
    "t1": "#e0f4ff", "t2": "#7ab3cc", "t3": "#2a4a60",
    "bd": "#0d2a3d",
}

HL = {
    "INT":"#5ac8fa","FLOAT":"#5ac8fa","STRING":"#5ac8fa","BOOLEAN":"#5ac8fa",
    "IF":"#bf5af2","ELSE":"#bf5af2","WHILE":"#bf5af2","FOR":"#bf5af2",
    "RETURN":"#bf5af2","AND":"#bf5af2","OR":"#bf5af2","NOT":"#bf5af2",
    "TRUE":"#ff9f0a","FALSE":"#ff9f0a","NULL":"#ff9f0a",
    "PRINT":"#ff6b6b","INPUT":"#ff6b6b",
    "ENTERO":"#ff9f0a","DECIMAL":"#ff9f0a",
    "CADENA":"#30d158","ID":"#e0f4ff",
    "MAS":"#0a84ff","MENOS":"#0a84ff","MULT":"#0a84ff",
    "DIV":"#0a84ff","MOD":"#0a84ff","IGUAL":"#0a84ff",
    "DIFERENTE":"#0a84ff","MENOR":"#0a84ff","MAYOR":"#0a84ff",
    "MENOR_IGUAL":"#0a84ff","MAYOR_IGUAL":"#0a84ff",
    "ASIGNACION":"#0a84ff","Y_LOGICO":"#0a84ff",
    "O_LOGICO":"#0a84ff","NO_LOGICO":"#0a84ff",
}

NODE_COLORS = {
    "Program":    ("#3b1a7a","#7b2ff7"),
    "Block":      ("#2a1060","#6b1fe6"),
    "Declaration":("#0a3d6b","#0e7dd6"),
    "Assignment": ("#0a3d2a","#0a7d6b"),
    "If":         ("#4a3000","#c07a00"),
    "While":      ("#3d2800","#a06000"),
    "For":        ("#3a2200","#8b5e00"),
    "Print":      ("#4a0a0a","#cc2222"),
    "Call":       ("#4a0a0a","#cc2222"),
    "BinaryOp":   ("#0a2a0a","#1a7a1a"),
    "UnaryOp":    ("#0a2a14","#1a7a3a"),
    "Group":      ("#0a2a3a","#1a6a8a"),
    "Literal":    ("#1a1a3a","#4a4aaa"),
    "StringLit":  ("#0a1a0a","#2a6a2a"),
    "BoolLit":    ("#1a1a3a","#6a4aaa"),
    "Identifier": ("#1a2a2a","#3a6a6a"),
    "Token":      ("#1a1a2a","#3a3a6a"),
    "Keyword":    ("#2a1a0a","#6a4a1a"),
}
NODE_ICONS = {
    "Program":"O","Block":"{}","Declaration":"=",
    "Assignment":"<","If":"?","While":"R","For":"@",
    "Print":">","Call":"()","BinaryOp":"+",
    "UnaryOp":"!","Group":"()","Literal":"#",
    "StringLit":'"',"BoolLit":"B","Identifier":"$","Token":"T","Keyword":"K",
}

# ══════════════════════════════════════════════════════════════════
#  EJEMPLOS
# ══════════════════════════════════════════════════════════════════
EJEMPLOS = [
("01 Variables y Tipos", """// Ejemplo 01 - Variables y Tipos de Dato
int edad = 25;
float salario = 15750.50;
string nombre = "Ana Garcia";
boolean activo = true;

int anioNacimiento = 2025 - edad;
float bono = salario * 0.10;
float salarioTotal = salario + bono;
int residuo = edad % 7;

edad = edad + 1;
print(nombre);
print(salarioTotal);
"""),
("02 Control de Flujo", """// Ejemplo 02 - Estructuras if / else
int nota = 78;
boolean aprobado = false;
string calificacion = "indefinida";

if (nota >= 90) {
    calificacion = "Excelente";
    aprobado = true;
} else {
    if (nota >= 70) {
        calificacion = "Aprobado";
        aprobado = true;
    } else {
        calificacion = "Reprobado";
        aprobado = false;
    }
}

boolean conBecas = aprobado && (nota >= 75);
print(calificacion);
print(conBecas);
"""),
("03 Bucles while y for", """// Ejemplo 03 - Bucles while y for
int i = 1;
int suma = 0;
while (i <= 100) {
    suma = suma + i;
    i = i + 1;
}
print(suma);

int n = 10;
int factorial = 1;
int k = n;
while (k > 1) {
    factorial = factorial * k;
    k = k - 1;
}
print(factorial);

int base = 7;
for (int j = 1; j <= 12; j = j + 1) {
    int resultado = base * j;
    print(resultado);
}
"""),
("04 Expresiones Complejas", """// Ejemplo 04 - Expresiones y Operadores
float a = 10.5;
float b = 3.2;
float c = 0.0;

c = a + b * 2.0 - 1.5;
float d = a / b + b % 3.0;

boolean r1 = (a > 5.0) && (b < 5.0);
boolean r2 = (a == 10.5) || (b == 0.0);
boolean r3 = !(a < b) && (c != 0.0);

int x = 100;
int y = 37;
int cociente = x / y;
int residuoMod = x % y;

print(c);
print(r1);
print(cociente);
"""),
("05 Errores Lexicos", """// Ejemplo 05 - Errores Lexicos Intencionales
int x = 10;
float y = 3.14;
string mensaje = "Hola";

// ERROR 1: caracter ilegal @
int z = 5@2;

// ERROR 2: caracter ilegal #
float pi = 3.14#15;

// ERROR 3: variable duplicada
int x = 99;

boolean activo = true;
int contador = 0;
while (contador < 5) {
    contador = contador + 1;
}
print(x);
"""),
("06 Strings y Booleanos", """// Ejemplo 06 - Cadenas y Logica Booleana
string saludo = "Hola, Mundo!";
string vacia = "";

boolean verdadero = true;
boolean falso = false;
boolean nulo = null;

boolean tt = verdadero && verdadero;
boolean tf = verdadero && falso;
boolean ff = falso && falso;
boolean tt2 = verdadero || verdadero;

boolean noV = !verdadero;
boolean noF = !falso;
boolean complejo = (tt || tf) && (!ff) && (tt2 != ff);

print(saludo);
print(complejo);
"""),
("07 Programa Completo", """// Ejemplo 07 - Programa Integrador
// Compiladores 120262294035A

int totalAlumnos = 30;
float sumaNotas = 0.0;
float promedio = 0.0;
int aprobados = 0;
int reprobados = 0;
boolean cursoActivo = true;
string nombreCurso = "Compiladores 120262294035A";

float nota1 = 85.0;
float nota2 = 72.5;
float nota3 = 91.0;
float nota4 = 60.0;
float nota5 = 55.5;

sumaNotas = nota1 + nota2 + nota3 + nota4 + nota5;
int totalMuestras = 5;
promedio = sumaNotas / totalMuestras;

if (nota1 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota2 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }
if (nota3 >= 70) { aprobados = aprobados + 1; } else { reprobados = reprobados + 1; }

string estadoCurso = "indefinido";
if (promedio >= 90) {
    estadoCurso = "Excelente";
} else {
    if (promedio >= 75) {
        estadoCurso = "Bueno";
    } else {
        estadoCurso = "Regular";
    }
}

boolean cursoExitoso = cursoActivo && (aprobados > reprobados);
int porcentaje = (aprobados * 100) / totalMuestras;

print(nombreCurso);
print(promedio);
print(estadoCurso);
print(cursoExitoso);
"""),
]

RESERVED = {
    "int":"INT","float":"FLOAT","string":"STRING","boolean":"BOOLEAN",
    "if":"IF","else":"ELSE","while":"WHILE","for":"FOR","return":"RETURN",
    "true":"TRUE","false":"FALSE","print":"PRINT","input":"INPUT",
    "and":"AND","or":"OR","not":"NOT","null":"NULL",
}
TIPOS_DATO = {"INT","FLOAT","STRING","BOOLEAN"}


def build_tree(tokens):
    toks = [t for t in tokens if t["tipo"] not in ("NUEVA_LINEA","ESPACIO","COMENTARIO")]
    pos = [0]

    def peek(off=0):
        i = pos[0]+off
        return toks[i] if i < len(toks) else None
    def consume():
        t = toks[pos[0]] if pos[0] < len(toks) else None
        pos[0] += 1; return t
    def expect(tipo):
        t = peek()
        if t and t["tipo"] == tipo: pos[0] += 1; return t
        return None

    def parse_program():
        stmts = []
        while pos[0] < len(toks):
            s = parse_stmt()
            if s: stmts.append(s)
            else: pos[0] += 1
        return {"type":"Program","children":stmts}

    def parse_stmt():
        t = peek()
        if not t: return None
        if t["tipo"] in TIPOS_DATO: return parse_decl()
        if t["tipo"] == "IF":       return parse_if()
        if t["tipo"] == "WHILE":    return parse_while()
        if t["tipo"] == "FOR":      return parse_for()
        if t["tipo"] in ("PRINT","INPUT"): return parse_print()
        if t["tipo"] == "ID":
            n = peek(1)
            if n and n["tipo"] == "ASIGNACION": return parse_assign()
        if t["tipo"] == "LLAVE_IZQ": return parse_block()
        if t["tipo"] == "PUNTO_COMA": consume(); return None
        tok = consume(); return {"type":"Unknown","token":tok}

    def parse_decl():
        dt = consume()
        id_ = consume() if peek() and peek()["tipo"]=="ID" else None
        expr = None
        if peek() and peek()["tipo"]=="ASIGNACION": consume(); expr = parse_expr()
        expect("PUNTO_COMA")
        return {"type":"Declaration","dataType":dt,"id":id_,"expr":expr}

    def parse_assign():
        id_ = consume(); expect("ASIGNACION")
        expr = parse_expr(); expect("PUNTO_COMA")
        return {"type":"Assignment","id":id_,"expr":expr}

    def parse_if():
        kw = consume(); expect("PAREN_IZQ")
        cond = parse_expr(); expect("PAREN_DER")
        body = parse_block(); else_body = None
        if peek() and peek()["tipo"]=="ELSE": consume(); else_body = parse_block()
        return {"type":"If","kw":kw,"cond":cond,"body":body,"elseBody":else_body}

    def parse_while():
        kw = consume(); expect("PAREN_IZQ")
        cond = parse_expr(); expect("PAREN_DER")
        body = parse_block()
        return {"type":"While","kw":kw,"cond":cond,"body":body}

    def parse_for():
        kw = consume(); expect("PAREN_IZQ")
        init = parse_stmt(); cond = parse_expr(); expect("PUNTO_COMA")
        upd_id = consume() if peek() and peek()["tipo"]=="ID" else None
        upd_expr = None
        if peek() and peek()["tipo"]=="ASIGNACION": consume(); upd_expr = parse_expr()
        expect("PAREN_DER"); body = parse_block()
        return {"type":"For","kw":kw,"init":init,"cond":cond,"updId":upd_id,"body":body}

    def parse_print():
        kw = consume(); expect("PAREN_IZQ")
        arg = parse_expr(); expect("PAREN_DER"); expect("PUNTO_COMA")
        return {"type":"Print","kw":kw,"arg":arg}

    def parse_block():
        if peek() and peek()["tipo"]=="LLAVE_IZQ":
            consume(); stmts = []
            while pos[0]<len(toks) and not(peek() and peek()["tipo"]=="LLAVE_DER"):
                s = parse_stmt()
                if s: stmts.append(s)
            expect("LLAVE_DER"); return {"type":"Block","stmts":stmts}
        s = parse_stmt()
        return {"type":"Block","stmts":[s] if s else []}

    def parse_expr():  return parse_or()
    def parse_or():
        l = parse_and()
        while peek() and peek()["tipo"]=="O_LOGICO":
            op=consume(); r=parse_and(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_and():
        l = parse_eq()
        while peek() and peek()["tipo"]=="Y_LOGICO":
            op=consume(); r=parse_eq(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_eq():
        l = parse_rel()
        while peek() and peek()["tipo"] in ("IGUAL","DIFERENTE"):
            op=consume(); r=parse_rel(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_rel():
        l = parse_add()
        while peek() and peek()["tipo"] in ("MENOR","MAYOR","MENOR_IGUAL","MAYOR_IGUAL"):
            op=consume(); r=parse_add(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_add():
        l = parse_mul()
        while peek() and peek()["tipo"] in ("MAS","MENOS"):
            op=consume(); r=parse_mul(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_mul():
        l = parse_unary()
        while peek() and peek()["tipo"] in ("MULT","DIV","MOD"):
            op=consume(); r=parse_unary(); l={"type":"BinaryOp","op":op,"left":l,"right":r}
        return l
    def parse_unary():
        if peek() and peek()["tipo"]=="NO_LOGICO":
            op=consume(); operand=parse_unary()
            return {"type":"UnaryOp","op":op,"operand":operand}
        return parse_primary()
    def parse_primary():
        t = peek()
        if not t: return None
        if t["tipo"]=="PAREN_IZQ":
            consume(); e=parse_expr(); expect("PAREN_DER")
            return {"type":"Group","expr":e}
        if t["tipo"] in ("ENTERO","DECIMAL"): return {"type":"Literal","token":consume()}
        if t["tipo"]=="CADENA": return {"type":"StringLit","token":consume()}
        if t["tipo"] in ("TRUE","FALSE","NULL"): return {"type":"BoolLit","token":consume()}
        if t["tipo"]=="ID":
            id_=consume()
            if peek() and peek()["tipo"]=="PAREN_IZQ":
                consume(); args=[]
                while peek() and peek()["tipo"]!="PAREN_DER":
                    args.append(parse_expr())
                    if peek() and peek()["tipo"]=="COMA": consume()
                expect("PAREN_DER")
                return {"type":"Call","id":id_,"args":args}
            return {"type":"Identifier","token":id_}
        if t["tipo"] in TIPOS_DATO or t["tipo"] in ("IF","ELSE","WHILE","FOR","RETURN","PRINT","INPUT","AND","OR","NOT"):
            return {"type":"Keyword","token":consume()}
        return {"type":"Token","token":consume()}

    return parse_program()


def get_kids(node):
    if not node: return []
    t = node.get("type","")
    if t == "Program":     return [c for c in node.get("children",[]) if c]
    if t == "Block":       return [c for c in node.get("stmts",[]) if c]
    if t == "Declaration":
        c = []
        if node.get("dataType"): c.append({"type":"Token","token":node["dataType"],"_label":"Tipo"})
        if node.get("id"):       c.append({"type":"Token","token":node["id"],"_label":"ID"})
        if node.get("expr"):     c.append({**node["expr"],"_label":"valor"})
        return c
    if t == "Assignment":
        c = []
        if node.get("id"):   c.append({"type":"Identifier","token":node["id"],"_label":"var"})
        if node.get("expr"): c.append({**node["expr"],"_label":"expr"})
        return c
    if t == "If":
        c = []
        if node.get("cond"):     c.append({**node["cond"],"_label":"cond"})
        if node.get("body"):     c.append({**node["body"],"_label":"then"})
        if node.get("elseBody"): c.append({**node["elseBody"],"_label":"else"})
        return c
    if t == "While":
        c = []
        if node.get("cond"): c.append({**node["cond"],"_label":"cond"})
        if node.get("body"): c.append(node["body"])
        return c
    if t == "For":
        c = []
        if node.get("init"):  c.append({**node["init"],"_label":"init"})
        if node.get("cond"):  c.append({**node["cond"],"_label":"cond"})
        if node.get("updId"): c.append({"type":"Identifier","token":node["updId"],"_label":"upd"})
        if node.get("body"):  c.append(node["body"])
        return c
    if t == "Print":    return [{**node["arg"],"_label":"arg"}] if node.get("arg") else []
    if t == "Call":     return [a for a in node.get("args",[]) if a]
    if t == "BinaryOp":
        c = []
        if node.get("left"):  c.append({**node["left"],"_label":"izq"})
        if node.get("right"): c.append({**node["right"],"_label":"der"})
        return c
    if t == "UnaryOp":  return [node["operand"]] if node.get("operand") else []
    if t == "Group":    return [node["expr"]] if node.get("expr") else []
    return []


def node_label(node):
    t = node.get("type","")
    tok = node.get("token") or node.get("kw")
    val = tok["valor"] if tok else ""
    if t=="Program":      return "PROGRAMA"
    if t=="Block":        return "BLOQUE"
    if t=="Declaration":
        dt = (node.get("dataType") or {}); id_ = (node.get("id") or {})
        return ("DECL " + dt.get("valor","") + " " + id_.get("valor","")).strip()
    if t=="Assignment":
        id_ = (node.get("id") or {}); return ("ASIG " + id_.get("valor","")).strip()
    if t=="If":           return "IF"
    if t=="While":        return "WHILE"
    if t=="For":          return "FOR"
    if t=="Print":        return "PRINT"
    if t=="Call":
        id_ = (node.get("id") or {}); return id_.get("valor","CALL") + "()"
    if t=="BinaryOp":
        op = (node.get("op") or {}); return "OP  " + op.get("valor","?")
    if t=="UnaryOp":      return "UNARIO !"
    if t=="Group":        return "( expr )"
    if t=="StringLit":    return '"' + val[:10] + ("..." if len(val)>10 else "") + '"'
    return val[:14] if val else t


# ══════════════════════════════════════════════════════════════════
#  NUMERADOR DE LINEAS
# ══════════════════════════════════════════════════════════════════
class NumeradorLineas(tk.Canvas):
    def __init__(self, master, editor, **kw):
        super().__init__(master, width=46, bg=C["bg1"], highlightthickness=0, **kw)
        self._ed = editor
        self._font = tkfont.Font(family="Consolas", size=11)
        for ev in ("<<Change>>","<Configure>","<KeyRelease>","<MouseWheel>","<Button-4>","<Button-5>"):
            editor.bind(ev, self._update)

    def _update(self, _=None):
        self.delete("all")
        i = self._ed.index("@0,0")
        while True:
            dl = self._ed.dlineinfo(i)
            if dl is None: break
            self.create_text(42, dl[1]+1, anchor="ne", text=i.split(".")[0],
                             fill=C["t3"], font=self._font)
            i = self._ed.index(f"{i}+1line")
            if self._ed.compare(i,">=","end"): break


# ══════════════════════════════════════════════════════════════════
#  ARBOL CANVAS
# ══════════════════════════════════════════════════════════════════
NW, NH, HGAP, VGAP = 132, 40, 24, 56

class ArbolCanvas(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=C["bg1"], **kw)
        self._collapsed = set()
        self._root_node = None
        self._id_counter = 0
        self._font_n = tkfont.Font(family="Consolas", size=9)
        self._font_s = tkfont.Font(family="Consolas", size=8)

        vsb = tk.Scrollbar(self, bg=C["bg2"], troughcolor=C["bg1"])
        hsb = tk.Scrollbar(self, orient="horizontal", bg=C["bg2"], troughcolor=C["bg1"])
        self._cv = tk.Canvas(self, bg=C["bg1"], highlightthickness=0,
                              yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self._cv.yview); hsb.config(command=self._cv.xview)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self._cv.pack(fill="both", expand=True)
        self._cv.bind("<MouseWheel>", lambda e: self._cv.yview_scroll(int(-1*(e.delta/120)),"units"))
        self._cv.bind("<Button-4>",   lambda e: self._cv.yview_scroll(-1,"units"))
        self._cv.bind("<Button-5>",   lambda e: self._cv.yview_scroll(1,"units"))

    def clear(self):
        self._cv.delete("all"); self._root_node = None

    def draw(self, ast_root):
        self._root_node = ast_root
        self._collapsed.clear()
        self._id_counter = 0
        self._assign_ids(ast_root)
        self._redraw()

    def _assign_ids(self, node):
        if not node: return
        self._id_counter += 1
        node["_id"] = self._id_counter
        for k in get_kids(node): self._assign_ids(k)

    def _redraw(self):
        self._cv.delete("all")
        if not self._root_node: return
        layout = self._layout(self._root_node, 0)
        all_lays = []; self._collect(layout, all_lays)
        if not all_lays: return
        min_x = min(l["x"] for l in all_lays)
        shift = 20 - min_x
        self._shift_all(layout, shift)
        self._draw(layout)
        max_x = max(l["x"] for l in all_lays) + NW + 24
        max_y = max(l["y"] for l in all_lays) + NH + 24
        self._cv.config(scrollregion=(0, 0, max_x+shift, max_y))

    def _collect(self, l, lst):
        lst.append(l)
        for c in l["children"]: self._collect(c, lst)

    def _shift_all(self, l, dx):
        l["x"] += dx
        for c in l["children"]: self._shift_all(c, dx)

    def _bounds(self, l):
        lm = rm = l["x"]
        for c in l["children"]:
            cl, cr = self._bounds(c)
            lm = min(lm, cl); rm = max(rm, cr)
        return lm, rm

    def _layout(self, node, depth):
        collapsed = node.get("_id") in self._collapsed
        kids = [] if collapsed else get_kids(node)
        for k in kids: self._assign_ids(k)
        y = depth * (NH + VGAP)
        if not kids:
            return {"node":node,"x":0,"y":y,"children":[],"collapsed":collapsed}
        child_lays = [self._layout(k, depth+1) for k in kids]
        cx = 0
        for cl in child_lays:
            lm, rm = self._bounds(cl)
            w = rm - lm + NW
            dx = cx - lm
            self._shift_all(cl, dx)
            cx += w + HGAP
        first_x = child_lays[0]["x"]; last_x = child_lays[-1]["x"]
        px = (first_x + last_x) / 2
        return {"node":node,"x":px,"y":y,"children":child_lays,"collapsed":collapsed}

    def _draw(self, lay):
        node = lay["node"]; x, y = lay["x"], lay["y"]
        cx = x + NW/2
        ntype = node.get("type","")
        fill, stroke = NODE_COLORS.get(ntype, ("#1a1a2a","#3a3a6a"))
        icon = NODE_ICONS.get(ntype,".")

        # bezier edges
        for child in lay["children"]:
            ccx = child["x"] + NW/2; ccy = child["y"]
            mid_y = y + NH + VGAP/2
            pts = []
            for i in range(13):
                t = i/12
                bx = (1-t)**3*cx + 3*(1-t)**2*t*cx + 3*(1-t)*t**2*ccx + t**3*ccx
                by = (1-t)**3*(y+NH) + 3*(1-t)**2*t*mid_y + 3*(1-t)*t**2*mid_y + t**3*ccy
                pts.extend([bx, by])
            self._cv.create_line(*pts, fill=stroke, width=1.5, smooth=False)

        # glow
        self._cv.create_rectangle(x+2,y+2,x+NW-2,y+NH-2, fill=stroke, outline="", stipple="gray12")
        # box
        self._cv.create_rectangle(x,y,x+NW,y+NH, fill=fill, outline=stroke, width=1.5, tags=("node",))
        # collapse dot
        if get_kids(node):
            dot_fill = stroke if node.get("_id") in self._collapsed else ""
            self._cv.create_oval(cx-4,y+NH-8,cx+4,y+NH-1, fill=dot_fill, outline=stroke, width=1)
        # icon (left)
        self._cv.create_text(x+12, y+NH//2, text=icon, fill=stroke,
                              font=self._font_n, anchor="center")
        # label
        lbl = node_label(node)
        if len(lbl) > 13: lbl = lbl[:12]+"..."
        sub = node.get("_label","")
        lbl_y = y + NH//2 - (4 if sub else 0)
        self._cv.create_text(cx+4, lbl_y, text=lbl, fill="#e0f4ff",
                              font=self._font_n, anchor="center")
        if sub:
            self._cv.create_text(cx+4, y+NH//2+8, text=sub, fill=stroke,
                                  font=self._font_s, anchor="center")
        # click area
        nid = node.get("_id"); tag = f"nid_{nid}"
        self._cv.create_rectangle(x,y,x+NW,y+NH, fill="", outline="", tags=("node",tag))
        self._cv.tag_bind(tag, "<Button-1>", lambda e,i=nid: self._toggle(i))
        # recurse
        for child in lay["children"]: self._draw(child)

    def _toggle(self, nid):
        if nid in self._collapsed: self._collapsed.discard(nid)
        else: self._collapsed.add(nid)
        self._redraw()

    def expand_all(self):
        self._collapsed.clear(); self._redraw()

    def collapse_all(self):
        def collect(node):
            if not node: return
            nid = node.get("_id")
            if nid: self._collapsed.add(nid)
            for k in get_kids(node): collect(k)
        if self._root_node:
            for k in get_kids(self._root_node): collect(k)
        self._redraw()


# ══════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════
class MiniIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniCompiler v2.0  -  Proyecto Final Compiladores")
        self.geometry("1340x860")
        self.minsize(1000, 680)
        self.configure(bg=C["bg0"])
        self._lexer = Lexer()
        self._archivo = None
        self.fn_mono = tkfont.Font(family="Consolas", size=12)
        self.fn_ui   = tkfont.Font(family="Segoe UI",  size=9)
        self.fn_bold = tkfont.Font(family="Segoe UI",  size=9, weight="bold")
        self.fn_disp = tkfont.Font(family="Courier New", size=8, weight="bold")
        self._example_menu_win = None
        self._example_menu_open = False
        self._build_menu()
        self._build_banner()
        self._build_header()
        self._build_main()
        self._build_footer()
        self._configure_highlighting()
        self._load_example(0)
        self.bind("<F5>", lambda e: self._analyze())

    def _build_menu(self):
        mb = tk.Menu(self, bg=C["bg2"], fg=C["t1"], activebackground=C["red"],
                     activeforeground="#fff", relief="flat")
        self.config(menu=mb)
        mf = tk.Menu(mb, tearoff=0, bg=C["bg2"], fg=C["t1"],
                     activebackground=C["red"], activeforeground="#fff")
        mf.add_command(label="Nuevo   Ctrl+N", command=self._new)
        mf.add_command(label="Abrir...  Ctrl+O", command=self._open)
        mf.add_command(label="Guardar  Ctrl+S", command=self._save)
        mf.add_separator(); mf.add_command(label="Salir", command=self.quit)
        mb.add_cascade(label=" Archivo ", menu=mf)
        ma = tk.Menu(mb, tearoff=0, bg=C["bg2"], fg=C["t1"],
                     activebackground=C["red"], activeforeground="#fff")
        ma.add_command(label="Analizar  F5", command=self._analyze)
        ma.add_command(label="Limpiar",      command=self._clear_all)
        mb.add_cascade(label=" Analizar ", menu=ma)
        self.bind("<Control-n>", lambda e: self._new())
        self.bind("<Control-o>", lambda e: self._open())
        self.bind("<Control-s>", lambda e: self._save())

    def _build_banner(self):
        f = tk.Frame(self, bg=C["bg2"], height=50); f.pack(fill="x"); f.pack_propagate(False)
        tk.Frame(f, bg=C["cyan"], height=1).pack(fill="x", side="bottom")
        left = tk.Frame(f, bg=C["bg2"]); left.pack(side="left", padx=14, pady=5)
        tk.Label(left, text="PROYECTO FINAL", bg=C["bg2"], fg=C["t3"],
                 font=("Courier New",7,"bold")).pack(anchor="w")
        tk.Label(left, text="COMPILADORES", bg=C["bg2"], fg=C["cyan"],
                 font=("Courier New",13,"bold")).pack(anchor="w")
        ctr = tk.Frame(f, bg=C["bg2"]); ctr.pack(side="left", expand=True)
        row1 = tk.Frame(ctr, bg=C["bg2"]); row1.pack()
        row2 = tk.Frame(ctr, bg=C["bg2"]); row2.pack()
        authors = ["Javier Emanuel Garcia Vasquez","Jose Luis Curup Aquino",
                   "Deyvis Abisai Silva Enriquez","Erica Patricia Hidalgo Castro"]
        for i,a in enumerate(authors):
            row = row1 if i < 2 else row2
            tk.Label(row, text=f"> {a}", bg=C["bg2"], fg=C["green"],
                     font=("Consolas",9)).pack(side="left", padx=8)
        right = tk.Frame(f, bg=C["bg2"]); right.pack(side="right", padx=14, pady=4)
        tk.Label(right, text="Facultad de Ingenieria en Sistemas",
                 bg=C["bg2"], fg=C["amber"], font=("Consolas",8)).pack(anchor="e")
        tk.Label(right, text="Universidad Mariano Galvez - Jocotenango",
                 bg=C["bg2"], fg=C["amber"], font=("Consolas",8)).pack(anchor="e")
        tk.Label(right, text="Compiladores 120262294035A",
                 bg=C["bg2"], fg=C["t2"], font=("Courier New",7)).pack(anchor="e")
        tk.Label(right, text="Ing. Manuel Alberto Herrera Estrada",
                 bg=C["bg2"], fg=C["purple"], font=("Consolas",8)).pack(anchor="e")

    def _build_header(self):
        f = tk.Frame(self, bg=C["bg2"], height=46); f.pack(fill="x"); f.pack_propagate(False)
        tk.Frame(f, bg=C["cyan"], height=1).pack(fill="x", side="bottom")
        logo = tk.Frame(f, bg=C["bg2"]); logo.pack(side="left", padx=14, pady=7)
        icon_f = tk.Frame(logo, bg=C["bg2"], width=28, height=28,
                          highlightthickness=1, highlightbackground=C["cyan"])
        icon_f.pack(side="left"); icon_f.pack_propagate(False)
        tk.Label(icon_f, text="O", bg=C["bg2"], fg=C["cyan"],
                 font=("Consolas",14)).place(relx=.5,rely=.5,anchor="center")
        txt = tk.Frame(logo, bg=C["bg2"]); txt.pack(side="left", padx=8)
        tk.Label(txt, text="MiniCompiler", bg=C["bg2"], fg=C["cyan"],
                 font=("Courier New",12,"bold")).pack(anchor="w")
        tk.Label(txt, text="Lexer - Parser - Semantic Analyzer v2.0",
                 bg=C["bg2"], fg=C["t2"], font=("Consolas",8)).pack(anchor="w")
        for lbl,col in [("Lexico",C["cyan"]),("Sintactico",C["green"]),("Semantico",C["purple"])]:
            tf = tk.Frame(f, bg=C["bg2"], highlightthickness=1, highlightbackground=col)
            tf.pack(side="left", padx=4, pady=10)
            tk.Label(tf, text=lbl, bg=C["bg2"], fg=col,
                     font=("Courier New",7,"bold"), padx=6, pady=2).pack()
        self._lbl_status = tk.Label(f, text="Sistema listo", bg=C["bg2"],
                                     fg=C["t2"], font=self.fn_ui)
        self._lbl_status.pack(side="right", padx=14)
        self._dot = tk.Canvas(f, width=8, height=8, bg=C["bg2"], highlightthickness=0)
        self._dot.pack(side="right", pady=19)
        self._dot.create_oval(1,1,7,7, fill=C["green"], outline=C["green"])

    def _build_main(self):
        self._main = tk.Frame(self, bg=C["bg0"]); self._main.pack(fill="both", expand=True)
        self._left = tk.Frame(self._main, bg=C["bg0"]); self._left.pack(side="left", fill="both", expand=True)
        self._build_right()
        self._build_tabs()
        self._tab_frames = {}
        for name in ("editor","tokens","tree","semantic","errors"):
            f = tk.Frame(self._left, bg=C["bg1"]); self._tab_frames[name] = f
        self._show_tab("editor")
        self._build_editor_tab()
        self._build_tokens_tab()
        self._build_tree_tab()
        self._build_semantic_tab()
        self._build_errors_tab()

    def _build_right(self):
        right = tk.Frame(self._main, bg=C["bg2"], width=295)
        right.pack(side="right", fill="y"); right.pack_propagate(False)
        tk.Frame(right, bg=C["bd"], width=1).pack(side="left", fill="y")
        inner = tk.Frame(right, bg=C["bg2"]); inner.pack(fill="both", expand=True)
        ph = tk.Frame(inner, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["green"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" TABLA DE SIMBOLOS", bg=C["bg2"], fg=C["green"],
                 font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_sym_count = tk.Label(ph, text="0 simbolos", bg=C["bg2"],
                                        fg=C["t3"], font=self.fn_ui)
        self._lbl_sym_count.pack(side="right", padx=8)
        tk.Frame(inner, bg=C["bd"], height=1).pack(fill="x")
        sym_frame = tk.Frame(inner, bg=C["bg1"]); sym_frame.pack(fill="both", expand=True)
        self._sym_tree = self._make_treeview(sym_frame,
            ("nombre","tipo","linea","valor"),("Nombre","Tipo","Ln","Valor"),(88,58,32,68))
        tk.Frame(inner, bg=C["bd"], height=1).pack(fill="x")
        stats = tk.Frame(inner, bg=C["bg2"]); stats.pack(fill="x", padx=10, pady=8)
        tk.Label(stats, text="RESUMEN", bg=C["bg2"], fg=C["t3"],
                 font=("Courier New",7,"bold")).pack(anchor="w")
        grid = tk.Frame(stats, bg=C["bg2"]); grid.pack(fill="x", pady=4)
        self._stat_vars = {}
        for idx,(key,col,lbl) in enumerate([("tokens",C["cyan"],"Tokens"),("syms",C["green"],"Simbolos"),
                                              ("lines",C["amber"],"Lineas"),("errs",C["red"],"Errores")]):
            box = tk.Frame(grid, bg=C["bg3"], padx=8, pady=6,
                           highlightthickness=1, highlightbackground=C["bd"])
            box.grid(row=idx//2, column=idx%2, padx=3, pady=3, sticky="ew")
            grid.columnconfigure(idx%2, weight=1)
            v = tk.StringVar(value="0"); self._stat_vars[key] = v
            tk.Label(box, textvariable=v, bg=C["bg3"], fg=col,
                     font=("Courier New",18,"bold")).pack()
            tk.Label(box, text=lbl, bg=C["bg3"], fg=C["t3"],
                     font=("Courier New",7)).pack()

    def _build_tabs(self):
        bar = tk.Frame(self._left, bg=C["bg2"]); bar.pack(fill="x")
        tk.Frame(bar, bg=C["bd"], height=1).pack(fill="x", side="bottom")
        self._tab_btns = {}; self._badge_vars = {}
        tabs = [("editor","Editor",None),("tokens","Tokens","tokens"),
                ("tree","Arbol Sint.","tree"),("semantic","Semantico","sem"),("errors","Errores","errors")]
        for name,label,bkey in tabs:
            frm = tk.Frame(bar, bg=C["bg2"]); frm.pack(side="left")
            btn = tk.Label(frm, text=label, bg=C["bg2"], fg=C["t3"],
                           font=self.fn_disp, padx=12, pady=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda e,n=name: self._show_tab(n))
            self._tab_btns[name] = btn
            if bkey:
                bv = tk.StringVar(value=""); self._badge_vars[name] = bv
                badge = tk.Label(frm, textvariable=bv, bg=C["red"], fg="#fff",
                                  font=("Consolas",8), padx=4, pady=0)
                badge.pack(side="left", pady=7)
                badge.bind("<Button-1>", lambda e,n=name: self._show_tab(n))
        self._active_tab = None

    def _show_tab(self, name):
        for n,f in self._tab_frames.items(): f.pack_forget()
        self._tab_frames[name].pack(fill="both", expand=True)
        for n,btn in self._tab_btns.items():
            btn.configure(fg=C["cyan"] if n==name else C["t3"],
                          bg=C["bg3"] if n==name else C["bg2"])
        self._active_tab = name

    def _build_editor_tab(self):
        f = self._tab_frames["editor"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["cyan"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" CODIGO FUENTE", bg=C["bg2"], fg=C["cyan"],
                 font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_editor_info = tk.Label(ph, text="0 lineas - 0 chars",
                                          bg=C["bg2"], fg=C["t3"], font=self.fn_ui)
        self._lbl_editor_info.pack(side="right", padx=8)
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")
        wrap = tk.Frame(f, bg=C["bg1"]); wrap.pack(fill="both", expand=True)
        self._editor = tk.Text(wrap, bg=C["bg1"], fg=C["t1"], insertbackground=C["cyan"],
                                selectbackground=C["red"], selectforeground="#fff",
                                font=self.fn_mono, undo=True, wrap="none",
                                relief="flat", bd=0, padx=10, pady=8, tabs=("4c",))
        self._lnum = NumeradorLineas(wrap, self._editor)
        vsb = tk.Scrollbar(wrap, bg=C["bg2"], troughcolor=C["bg1"], command=self._editor.yview)
        hsb = tk.Scrollbar(wrap, orient="horizontal", bg=C["bg2"], troughcolor=C["bg1"],
                            command=self._editor.xview)
        self._editor.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self._lnum.grid(row=0,column=0,sticky="ns")
        self._editor.grid(row=0,column=1,sticky="nsew")
        vsb.grid(row=0,column=2,sticky="ns"); hsb.grid(row=1,column=0,columnspan=3,sticky="ew")
        wrap.rowconfigure(0,weight=1); wrap.columnconfigure(1,weight=1)
        sb = tk.Frame(f, bg=C["bg2"]); sb.pack(fill="x")
        tk.Frame(sb, bg=C["bd"], height=1).pack(fill="x")
        inner = tk.Frame(sb, bg=C["bg2"]); inner.pack(fill="x")
        self._lbl_cursor = tk.Label(inner, text="Linea 1, Col 1", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_cursor.pack(side="left", padx=10, pady=3)
        self._lbl_tok_count = tk.Label(inner, text="", bg=C["bg2"],
                                        fg=C["t3"], font=("Consolas",9))
        self._lbl_tok_count.pack(side="right", padx=10)
        self._editor.bind("<KeyRelease>", self._on_key_editor)
        self._editor.bind("<ButtonRelease>", self._on_key_editor)

    def _build_tokens_tab(self):
        f = self._tab_frames["tokens"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["cyan"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" TABLA DE TOKENS", bg=C["bg2"], fg=C["cyan"],
                 font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_tok_hdr = tk.Label(ph, text="0 tokens", bg=C["bg2"],
                                      fg=C["t3"], font=self.fn_ui)
        self._lbl_tok_hdr.pack(side="right", padx=8)
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")
        inner = tk.Frame(f, bg=C["bg1"]); inner.pack(fill="both", expand=True)
        self._tok_tree = self._make_treeview(inner,
            ("tipo","valor","linea","columna"),("Tipo","Valor","Ln","Col"),(140,160,50,50))

    def _build_tree_tab(self):
        f = self._tab_frames["tree"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["purple"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" ARBOL SINTACTICO VISUAL", bg=C["bg2"], fg=C["purple"],
                 font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_tree_hdr = tk.Label(ph, text="---", bg=C["bg2"],
                                       fg=C["t3"], font=self.fn_ui)
        self._lbl_tree_hdr.pack(side="right", padx=8)
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")
        tb = tk.Frame(f, bg=C["bg2"]); tb.pack(fill="x")
        tk.Frame(tb, bg=C["bd"], height=1).pack(fill="x", side="bottom")
        for lbl,cmd in [("Expandir todo",lambda:self._arbol.expand_all()),
                         ("Colapsar todo",lambda:self._arbol.collapse_all())]:
            b = tk.Label(tb, text=lbl, bg=C["bg2"], fg=C["t2"], font=self.fn_disp,
                          padx=10, pady=5, cursor="hand2",
                          highlightthickness=1, highlightbackground=C["bd"])
            b.pack(side="left", padx=5, pady=4)
            b.bind("<Button-1>", lambda e,c=cmd: c())
            b.bind("<Enter>",  lambda e,w=b: w.configure(fg=C["purple"],highlightbackground=C["purple"]))
            b.bind("<Leave>",  lambda e,w=b: w.configure(fg=C["t2"],highlightbackground=C["bd"]))
        tk.Label(tb, text="Clic en nodo para expandir/colapsar",
                 bg=C["bg2"], fg=C["t3"], font=("Consolas",8)).pack(side="right",padx=10)
        self._arbol = ArbolCanvas(f); self._arbol.pack(fill="both", expand=True)
        leg = tk.Frame(f, bg=C["bg2"]); leg.pack(fill="x")
        tk.Frame(leg, bg=C["bd"], height=1).pack(fill="x")
        inner = tk.Frame(leg, bg=C["bg2"]); inner.pack(fill="x", padx=10, pady=5)
        for col,lbl in [("#7b2ff7","Programa/Bloque"),("#0e7dd6","Declaracion"),
                         ("#0a7d6b","Asignacion"),("#c07a00","Control"),
                         ("#cc2222","Funcion"),("#1a7a1a","Expresion"),("#4a4aaa","Literal/ID")]:
            dot = tk.Canvas(inner, width=10, height=10, bg=C["bg2"], highlightthickness=0)
            dot.pack(side="left", padx=2)
            dot.create_rectangle(1,1,9,9, fill=col, outline=col)
            tk.Label(inner, text=lbl, bg=C["bg2"], fg=C["t2"],
                     font=("Consolas",8)).pack(side="left", padx=(0,8))

    def _build_semantic_tab(self):
        f = self._tab_frames["semantic"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["amber"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" ANALISIS SEMANTICO", bg=C["bg2"], fg=C["amber"],
                 font=self.fn_disp, pady=7).pack(side="left")
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")
        outer = tk.Frame(f, bg=C["bg1"]); outer.pack(fill="both", expand=True)
        vsb = tk.Scrollbar(outer, bg=C["bg2"], troughcolor=C["bg1"]); vsb.pack(side="right",fill="y")
        self._sem_canvas = tk.Canvas(outer, bg=C["bg1"], highlightthickness=0, yscrollcommand=vsb.set)
        vsb.config(command=self._sem_canvas.yview)
        self._sem_canvas.pack(fill="both", expand=True)
        self._sem_frame = tk.Frame(self._sem_canvas, bg=C["bg1"])
        self._sem_frame_id = self._sem_canvas.create_window((0,0), window=self._sem_frame, anchor="nw")
        self._sem_frame.bind("<Configure>",
            lambda e: self._sem_canvas.configure(scrollregion=self._sem_canvas.bbox("all")))
        self._sem_canvas.bind("<Configure>",
            lambda e: self._sem_canvas.itemconfig(self._sem_frame_id, width=e.width))

    def _build_errors_tab(self):
        f = self._tab_frames["errors"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["red"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" CONSOLA DE ERRORES", bg=C["bg2"], fg=C["red"],
                 font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_err_hdr = tk.Label(ph, text="---", bg=C["bg2"],
                                      fg=C["t3"], font=self.fn_ui)
        self._lbl_err_hdr.pack(side="right", padx=8)
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")
        self._console = tk.Text(f, bg=C["bg1"], fg=C["t2"], font=("Consolas",11),
                                 state="disabled", relief="flat", bd=0, padx=10, pady=8, wrap="word")
        vsb = tk.Scrollbar(f, bg=C["bg2"], troughcolor=C["bg1"], command=self._console.yview)
        self._console.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y"); self._console.pack(fill="both", expand=True)
        self._console.tag_config("ok", foreground=C["green"])
        self._console.tag_config("error", foreground=C["red"])
        self._console.tag_config("warn", foreground=C["amber"])
        self._console.tag_config("info", foreground=C["cyan"])

    def _build_footer(self):
        self._footer = tk.Frame(self, bg=C["bg2"], height=44)
        self._footer.pack(fill="x", side="bottom"); self._footer.pack_propagate(False)
        tk.Frame(self._footer, bg=C["cyan"], height=1).pack(fill="x", side="top")
        btn_run = tk.Label(self._footer, text=" ANALIZAR [F5] ", bg=C["red"], fg="#fff",
                            font=("Courier New",9,"bold"), padx=4, pady=6, cursor="hand2")
        btn_run.pack(side="left", padx=8, pady=5)
        btn_run.bind("<Button-1>", lambda e: self._analyze())
        btn_run.bind("<Enter>",  lambda e: btn_run.configure(bg="#ff4070"))
        btn_run.bind("<Leave>",  lambda e: btn_run.configure(bg=C["red"]))
        btn_clr = tk.Label(self._footer, text=" LIMPIAR ", bg=C["bg3"], fg=C["t2"],
                            font=self.fn_disp, padx=4, pady=6,
                            highlightthickness=1, highlightbackground=C["bd"], cursor="hand2")
        btn_clr.pack(side="left", padx=4, pady=5)
        btn_clr.bind("<Button-1>", lambda e: self._clear_all())
        self._btn_ex = tk.Label(self._footer, text=" EJEMPLOS v ", bg=C["bg3"], fg=C["amber"],
                                 font=self.fn_disp, padx=4, pady=6,
                                 highlightthickness=1, highlightbackground=C["bd"], cursor="hand2")
        self._btn_ex.pack(side="left", padx=4, pady=5)
        self._btn_ex.bind("<Button-1>", self._toggle_example_menu)
        self._btn_ex.bind("<Enter>", lambda e: self._btn_ex.configure(highlightbackground=C["amber"]))
        self._btn_ex.bind("<Leave>", lambda e: self._btn_ex.configure(highlightbackground=C["bd"]))
        self._lbl_ft_tok = tk.Label(self._footer, text="Tokens: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_tok.pack(side="right", padx=8)
        self._lbl_ft_err = tk.Label(self._footer, text="Errores: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_err.pack(side="right", padx=8)
        self._lbl_ft_sym = tk.Label(self._footer, text="Simbolos: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_sym.pack(side="right", padx=8)

    # ── EXAMPLE DROPDOWN ──────────────────────────────────────────
    def _toggle_example_menu(self, event=None):
        if self._example_menu_open: self._close_example_menu()
        else: self._open_example_menu()

    def _open_example_menu(self):
        self._close_example_menu()
        x = self._btn_ex.winfo_rootx()
        y = self._btn_ex.winfo_rooty()
        item_h = 44
        menu_h = len(EJEMPLOS) * item_h + 30
        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.configure(bg=C["bd"])
        win.geometry(f"310x{menu_h}+{x}+{y-menu_h-2}")
        win.lift(); win.focus_force()
        hdr = tk.Frame(win, bg=C["bg4"]); hdr.pack(fill="x")
        tk.Frame(hdr, bg=C["cyan"], height=1).pack(fill="x")
        tk.Label(hdr, text="  SELECCIONAR EJEMPLO", bg=C["bg4"], fg=C["cyan"],
                 font=("Courier New",7,"bold"), pady=6).pack()
        tk.Frame(hdr, bg=C["bd"], height=1).pack(fill="x")
        for idx,(title,_) in enumerate(EJEMPLOS):
            parts = title.split(" ",1); num = parts[0]; name = parts[1] if len(parts)>1 else title
            row = tk.Frame(win, bg=C["bg4"], cursor="hand2"); row.pack(fill="x")
            tk.Frame(row, bg=C["bd"], height=1).pack(fill="x", side="bottom")
            tk.Label(row, text=num, bg=C["bg4"], fg=C["t3"],
                     font=("Courier New",10,"bold"), width=4, pady=10).pack(side="left")
            tk.Label(row, text=name, bg=C["bg4"], fg=C["t1"],
                     font=("Consolas",10), pady=10, anchor="w").pack(side="left",fill="x",expand=True)
            def on_enter(e, w=row):
                w.configure(bg=C["bg3"])
                for c in w.winfo_children(): c.configure(bg=C["bg3"])
            def on_leave(e, w=row):
                w.configure(bg=C["bg4"])
                for c in w.winfo_children(): c.configure(bg=C["bg4"])
            def on_click(e, i=idx):
                self._load_example(i); self._close_example_menu()
            row.bind("<Enter>", on_enter); row.bind("<Leave>", on_leave); row.bind("<Button-1>", on_click)
            for child in row.winfo_children():
                child.bind("<Enter>", on_enter); child.bind("<Leave>", on_leave); child.bind("<Button-1>", on_click)
        self._example_menu_win = win; self._example_menu_open = True
        win.bind("<Escape>", lambda e: self._close_example_menu())
        win.bind("<FocusOut>", lambda e: self.after(100, self._check_focus))

    def _check_focus(self):
        try:
            focused = self.focus_get()
            if self._example_menu_win and focused:
                widget_window = str(focused).split(".")[0] if "." in str(focused) else str(focused)
                if self._example_menu_win and not str(focused).startswith(str(self._example_menu_win)):
                    self._close_example_menu()
        except Exception:
            pass

    def _close_example_menu(self):
        if self._example_menu_win:
            try: self._example_menu_win.destroy()
            except Exception: pass
        self._example_menu_win = None; self._example_menu_open = False

    # ── HIGHLIGHTING ──────────────────────────────────────────────
    def _configure_highlighting(self):
        for tipo, color in HL.items():
            self._editor.tag_configure(f"tok_{tipo}", foreground=color)
        self._editor.tag_configure("tok_COMENTARIO", foreground=C["t3"],
                                    font=tkfont.Font(family="Consolas",size=12,slant="italic"))

    def _apply_highlighting(self, tokens_info):
        for tag in self._editor.tag_names():
            if tag.startswith("tok_"): self._editor.tag_remove(tag,"1.0","end")
        codigo = self._editor.get("1.0","end-1c")
        for tok in tokens_info:
            tipo=tok["tipo"]; linea=tok["linea"]; col=tok["columna"]-1; val=tok["valor"]
            start=f"{linea}.{col}"; end_=f"{linea}.{col+len(val)}"; tag=f"tok_{tipo}"
            if tag in self._editor.tag_names(): self._editor.tag_add(tag,start,end_)
        for m in _re.finditer(r'//[^\n]*', codigo):
            ln=codigo[:m.start()].count("\n")+1; c0=m.start()-codigo[:m.start()].rfind("\n")-1
            self._editor.tag_add("tok_COMENTARIO",f"{ln}.{c0}",f"{ln}.{c0+len(m.group())}")

    # ── ANALYSIS ──────────────────────────────────────────────────
    def _analyze(self):
        codigo = self._editor.get("1.0","end-1c")
        if not codigo.strip(): self._log("warn","No hay codigo para analizar."); return
        self._lbl_status.configure(text="Analizando...", fg=C["amber"]); self.update()
        try: tokens, tabla, errores = self._lexer.analizar(codigo)
        except Exception as ex: self._log("error", f"Error interno: {ex}"); return

        for row in self._tok_tree.get_children(): self._tok_tree.delete(row)
        for i,tok in enumerate(tokens):
            self._tok_tree.insert("","end",
                values=(tok["tipo"],tok["valor"],tok["linea"],tok["columna"]),
                tags=("par" if i%2==0 else "impar",))
        self._lbl_tok_hdr.configure(text=f"{len(tokens)} tokens")

        for row in self._sym_tree.get_children(): self._sym_tree.delete(row)
        simbolos = tabla.todos_los_simbolos()
        for i,sim in enumerate(simbolos):
            self._sym_tree.insert("","end",
                values=(sim.nombre,sim.tipo,sim.linea,str(sim.valor) if sim.valor is not None else "---"),
                tags=("par" if i%2==0 else "impar",))
        self._lbl_sym_count.configure(text=f"{len(simbolos)} simbolos")

        ast = build_tree(tokens); self._arbol.draw(ast)
        self._lbl_tree_hdr.configure(text="arbol construido")
        self._build_semantic_panel(tokens, simbolos, errores)

        self._console.configure(state="normal"); self._console.delete("1.0","end")
        if errores:
            self._log("warn", f"Se encontraron {len(errores)} error(es):")
            for e in errores: self._log("error", f"  X  {e}")
            self._lbl_err_hdr.configure(text=f"{len(errores)} error(es)", fg=C["red"])
            self._lbl_status.configure(text=f"{len(errores)} error(es)", fg=C["red"])
        else:
            self._log("ok", f"Analisis completado -- {len(tokens)} tokens - {len(simbolos)} simbolos - 0 errores")
            self._lbl_err_hdr.configure(text="sin errores", fg=C["green"])
            self._lbl_status.configure(text="Analisis OK", fg=C["green"])
        self._console.configure(state="disabled")
        self._apply_highlighting(tokens)

        lines = codigo.count("\n") + 1
        self._stat_vars["tokens"].set(str(len(tokens)))
        self._stat_vars["syms"].set(str(len(simbolos)))
        self._stat_vars["lines"].set(str(lines))
        self._stat_vars["errs"].set(str(len(errores)))
        self._lbl_ft_tok.configure(text=f"Tokens: {len(tokens)}")
        self._lbl_ft_sym.configure(text=f"Simbolos: {len(simbolos)}")
        self._lbl_ft_err.configure(text=f"Errores: {len(errores)}")
        self._lbl_tok_count.configure(text=f"T:{len(tokens)}  S:{len(simbolos)}  E:{len(errores)}")
        for k,v in self._badge_vars.items():
            if k=="tokens": v.set(str(len(tokens)))
            elif k in ("tree","sem"): v.set("OK")
            elif k=="errors": v.set(str(len(errores)) if errores else "")

    def _build_semantic_panel(self, tokens, simbolos, errores):
        for w in self._sem_frame.winfo_children(): w.destroy()
        pad = {"padx":14,"pady":4}
        def section(title):
            tk.Frame(self._sem_frame,bg=C["bd"],height=1).pack(fill="x",padx=0,pady=8)
            tk.Label(self._sem_frame,text=title,bg=C["bg1"],fg=C["amber"],
                     font=("Courier New",8,"bold"),anchor="w").pack(fill="x",**pad)
            tk.Frame(self._sem_frame,bg=C["bd"],height=1).pack(fill="x")
        def stat_row(icon,label,val,col=C["t1"]):
            row=tk.Frame(self._sem_frame,bg=C["bg1"]); row.pack(fill="x")
            tk.Frame(row,bg=C["bd"],height=1).pack(fill="x",side="bottom")
            tk.Label(row,text=icon,bg=C["bg1"],fg=col,font=("Consolas",11),width=3).pack(side="left",padx=8,pady=5)
            tk.Label(row,text=label,bg=C["bg1"],fg=C["t2"],font=("Consolas",10),anchor="w").pack(side="left",fill="x",expand=True)
            tk.Label(row,text=str(val),bg=C["bg1"],fg=col,font=("Courier New",10,"bold"),padx=12).pack(side="right")
        TIPOS={"INT","FLOAT","STRING","BOOLEAN"}
        ifs=sum(1 for t in tokens if t["tipo"]=="IF")
        whiles=sum(1 for t in tokens if t["tipo"]=="WHILE")
        fors=sum(1 for t in tokens if t["tipo"]=="FOR")
        prints=sum(1 for t in tokens if t["tipo"]=="PRINT")
        decls=sum(1 for t in tokens if t["tipo"] in TIPOS)
        asigs=sum(1 for t in tokens if t["tipo"]=="ASIGNACION")
        section("ESTADISTICAS")
        grid=tk.Frame(self._sem_frame,bg=C["bg1"]); grid.pack(fill="x",padx=10,pady=6)
        for idx,(k,col,lbl) in enumerate([(len(tokens),C["cyan"],"Total Tokens"),(len(simbolos),C["green"],"Simbolos"),
                                            (decls,C["amber"],"Declaraciones"),(asigs,C["purple"],"Asignaciones")]):
            box=tk.Frame(grid,bg=C["bg3"],padx=8,pady=6,highlightthickness=1,highlightbackground=C["bd"])
            box.grid(row=idx//2,column=idx%2,padx=3,pady=3,sticky="ew"); grid.columnconfigure(idx%2,weight=1)
            tk.Label(box,text=str(k),bg=C["bg3"],fg=col,font=("Courier New",18,"bold")).pack()
            tk.Label(box,text=lbl,bg=C["bg3"],fg=C["t3"],font=("Courier New",7)).pack()
        section("ESTRUCTURAS DE CONTROL")
        for icon,lbl,val in [("*","Condicionales (if)",ifs),("R","Bucles while",whiles),
                               ("@","Bucles for",fors),(">","Llamadas print()",prints)]:
            stat_row(icon,lbl,val,C["cyan"])
        section("DIAGNOSTICO")
        lex_e=[e for e in errores if "ilegal" in e.lower()]
        sem_e=[e for e in errores if "semantico" in e.lower()]
        if not errores: stat_row("V","Sin errores lexicos ni semanticos","",C["green"])
        else:
            if lex_e: stat_row("X",f"{len(lex_e)} error(es) lexico(s)","caracteres ilegales",C["red"])
            if sem_e: stat_row("X",f"{len(sem_e)} error(es) semantico(s)","variables duplicadas",C["red"])
            for e in errores:
                col=C["red"] if "ilegal" in e.lower() or "semantico" in e.lower() else C["amber"]
                stat_row(".",e[:55]+"..." if len(e)>55 else e,"",col)

    def _log(self,level,msg):
        self._console.configure(state="normal")
        icon={"ok":"V","error":"X","warn":"!","info":">"}. get(level,">")
        self._console.insert("end",f"  {icon}  {msg}\n",level)
        self._console.see("end"); self._console.configure(state="disabled")

    def _make_treeview(self, parent, cols, headers, widths):
        style_name = f"TV{id(parent)}.Treeview"; style = ttk.Style()
        style.theme_use("clam")
        style.configure(style_name, background=C["bg3"], foreground=C["t1"],
                        fieldbackground=C["bg3"], rowheight=22, font=("Consolas",10))
        style.configure(f"{style_name}.Heading", background=C["bg2"], foreground=C["cyan"],
                        font=("Courier New",8,"bold"), relief="flat")
        style.map(style_name, background=[("selected",C["red"])])
        frame=tk.Frame(parent,bg=C["bd"]); frame.pack(fill="both",expand=True)
        frame.rowconfigure(0,weight=1); frame.columnconfigure(0,weight=1)
        tree=ttk.Treeview(frame,columns=cols,show="headings",style=style_name,selectmode="browse")
        vsb=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
        hsb=ttk.Scrollbar(frame,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=vsb.set,xscrollcommand=hsb.set)
        tree.grid(row=0,column=0,sticky="nsew"); vsb.grid(row=0,column=1,sticky="ns")
        hsb.grid(row=1,column=0,sticky="ew")
        for col,hdr,w in zip(cols,headers,widths):
            tree.heading(col,text=hdr); tree.column(col,width=w,minwidth=30,anchor="w")
        tree.tag_configure("par",background=C["bg3"]); tree.tag_configure("impar",background=C["bg4"])
        return tree

    def _on_key_editor(self, _=None):
        pos=self._editor.index("insert"); ln,col=pos.split(".")
        self._lbl_cursor.configure(text=f"Linea {ln}, Col {int(col)+1}")
        txt=self._editor.get("1.0","end-1c"); lines=txt.count("\n")+1; chars=len(txt)
        self._lbl_editor_info.configure(text=f"{lines} lineas - {chars} chars")

    def _load_example(self, idx):
        _,codigo = EJEMPLOS[idx]
        self._editor.delete("1.0","end"); self._editor.insert("1.0",codigo)
        self._show_tab("editor")
        self._console.configure(state="normal"); self._console.delete("1.0","end")
        self._log("info", f"Ejemplo cargado: {EJEMPLOS[idx][0]} -- presiona F5 para analizar.")
        self._console.configure(state="disabled"); self._on_key_editor()

    def _new(self):
        if messagebox.askyesno("Nuevo","Descartar el contenido actual?"):
            self._editor.delete("1.0","end"); self._archivo = None
    def _open(self):
        path=filedialog.askopenfilename(filetypes=[("MiniLang","*.ml *.txt"),("Todos","*.*")])
        if path:
            with open(path,"r",encoding="utf-8") as fh:
                self._editor.delete("1.0","end"); self._editor.insert("1.0",fh.read())
            self._archivo=path
    def _save(self):
        path=self._archivo or filedialog.asksaveasfilename(defaultextension=".ml",
            filetypes=[("MiniLang","*.ml"),("Texto","*.txt"),("Todos","*.*")])
        if path:
            with open(path,"w",encoding="utf-8") as fh: fh.write(self._editor.get("1.0","end-1c"))
            self._archivo=path

    def _clear_all(self):
        self._editor.delete("1.0","end")
        for row in self._tok_tree.get_children(): self._tok_tree.delete(row)
        for row in self._sym_tree.get_children(): self._sym_tree.delete(row)
        self._arbol.clear()
        for w in self._sem_frame.winfo_children(): w.destroy()
        self._console.configure(state="normal"); self._console.delete("1.0","end")
        self._console.configure(state="disabled")
        for k in self._stat_vars: self._stat_vars[k].set("0")
        for lbl in (self._lbl_tok_hdr,self._lbl_tree_hdr,self._lbl_err_hdr,self._lbl_sym_count):
            lbl.configure(text="---")
        self._lbl_status.configure(text="Sistema listo",fg=C["t2"])
        self._lbl_ft_tok.configure(text="Tokens: 0")
        self._lbl_ft_sym.configure(text="Simbolos: 0")
        self._lbl_ft_err.configure(text="Errores: 0")
        self._on_key_editor()


if __name__ == "__main__":
    app = MiniIDE()
    app.mainloop()
