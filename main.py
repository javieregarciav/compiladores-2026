import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font as tkfont
import sys, os, re as _re, webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend import (
    Lexer,
    build_tree, get_kids, node_label, RESERVED, TIPOS_DATO,
    GeneradorTAC,
    check_semantic,
)
from frontend.errores import fmt as fmt_error
from intermedio import formatear_tac
from backend import optimizar
import reportes as _reportes_mod

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
    "PROGRAMA":"#bf5af2",
    "ENTERO":"#5ac8fa","DECIMAL":"#5ac8fa","CADENA_TIPO":"#5ac8fa","BOOLEANO":"#5ac8fa",
    "SI":"#bf5af2","SINO":"#bf5af2","MIENTRAS":"#bf5af2","HACER_MIENTRAS":"#bf5af2","PARA":"#bf5af2",
    "FUNCION":"#bf5af2","PROCEDIMIENTO":"#bf5af2","RETORNAR":"#bf5af2",
    "AND":"#bf5af2","OR":"#bf5af2","NOT":"#bf5af2",
    "VERDADERO":"#ff9f0a","FALSO":"#ff9f0a",
    "IMPRIMIR":"#ff6b6b","LEER":"#ff6b6b",
    "NUMERO_ENTERO":"#ff9f0a","NUMERO_DECIMAL":"#ff9f0a",
    "CADENA_LITERAL":"#30d158","IDENTIFICADOR":"#e0f4ff",
    "MAS":"#0a84ff","MENOS":"#0a84ff","MULTIPLICACION":"#0a84ff",
    "DIVIDIR":"#0a84ff","MODULO":"#0a84ff","IGUAL":"#0a84ff",
    "DIFERENTE":"#0a84ff","MENOR":"#0a84ff","MAYOR":"#0a84ff",
    "MENOR_IGUAL":"#0a84ff","MAYOR_IGUAL":"#0a84ff",
    "ASIGNAR":"#0a84ff",
}

NODE_COLORS = {
    "Program":    ("#3b1a7a","#7b2ff7"),
    "Block":      ("#2a1060","#6b1fe6"),
    "Declaration":("#0a3d6b","#0e7dd6"),
    "Assignment": ("#0a3d2a","#0a7d6b"),
    "If":         ("#4a3000","#c07a00"),
    "While":      ("#3d2800","#a06000"),
    "DoWhile":    ("#3d2800","#a06000"),
    "For":        ("#3a2200","#8b5e00"),
    "Print":      ("#4a0a0a","#cc2222"),
    "Read":       ("#4a0a3a","#cc22aa"),
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
    "Assignment":"<","If":"?","While":"R","DoWhile":"R","For":"@",
    "Print":">","Read":"<","Call":"()","BinaryOp":"+",
    "UnaryOp":"!","Group":"()","Literal":"#",
    "StringLit":'"',"BoolLit":"B","Identifier":"$","Token":"T","Keyword":"K",
}

_TEXTO_INFO_TAC = """\
# CODIGO INTERMEDIO  =  FRONTERA FRONT-END / BACK-END

El codigo intermedio es la frontera entre el FRONT-END y el BACK-END
de un compilador. NO es solo "una etapa mas": es el contrato que
permite separar el lenguaje fuente de la maquina destino.

  FRONT-END  ---->  CODIGO INTERMEDIO  ---->  BACK-END
  (lenguaje                (TAC)              (maquina
   fuente)                                     objetivo)

Si cambia el lenguaje fuente solo se rehace el front-end.
Si cambia la arquitectura objetivo solo se rehace el back-end.
El IR (representacion intermedia) es el unico punto que ambos
lados conocen.

## ESTRUCTURA DE ESTE PROYECTO

  frontend/                  <- depende del lenguaje fuente
     lexer.py                analisis lexico
     tabla_simbolos.py       tabla de simbolos
     parser.py               AST (analisis sintactico)
     generador_intermedio.py emite el TAC

  intermedio.py              <- contrato compartido
     Quad                    cuadruplo (op, arg1, arg2, dest)
     formatear_tac           pretty-printer

  backend/                   <- depende de la maquina objetivo
     optimizador.py          optimiza el TAC
     (futuro) generador_objeto.py  emite ensamblador

## TIPOS DE CODIGO INTERMEDIO

  - Notacion postfija         a b +
  - Three-Address Code (TAC)  t1 = a + b   <-- usamos este
  - Cuadruplos / Triples
  - SSA (Static Single Assignment)
  - DAG (detecta subexpresiones comunes)

## CUAL USA ESTE COMPILADOR

  -> Three-Address Code (TAC) en formato de CUADRUPLOS:
        ( op , arg1 , arg2 , dest )

  Ejemplos:
        a = 5             ->  ( = , 5  , _ , a  )
        $t1 = b + c       ->  ( + , b  , c , $t1 )
        if $t1 goto $L2   ->  ( if_false , $t1 , _ , $L2 )
        goto $L3          ->  ( goto , _ , _ , $L3 )
        $L2:              ->  ( label , _ , _ , $L2 )
        print x           ->  ( print , x , _ , _ )

  Nota: los temporales y etiquetas usan prefijo '$' que el lexer
  no acepta como identificador, asi nunca chocan con variables
  del usuario llamadas t1 o L1.

## OPTIMIZACIONES (BACK-END)

  El optimizador ejecuta varias pasadas hasta punto fijo:

  1. Constant Folding         3 + 4   ->  7
  2. Algebraic Simplification x * 1   ->  x   ;   x + 0  ->  x
  3. Constant Propagation     x = 5; t = x + 1  ->  t = 5 + 1
  4. Copy Propagation         a = b; c = a + 1  ->  c = b + 1
  5. Dead-Code Elimination    elimina temporales nunca leidos
  6. Branch Pruning           ifFalse true   -> elimina el salto
  7. Jump Threading           goto L; L:     -> elimina el goto

## COMO LEER LAS TABLAS

  - Sub-vista "Sin optimizar"  -> TAC tal cual lo emite el front-end.
  - Sub-vista "Optimizado"     -> tras pasar por el back-end.
  - Sub-vista "Comparacion"    -> ambos lados a lado.

  Metricas en la barra:
        cuadruplos antes -> despues   (reduccion %)
        temporales antes -> despues
"""

EJEMPLOS = [
("01 Variables y Tipos", """// Ejemplo 01 - Variables y Tipos de Dato
programa {
    entero edad = 25;
    decimal salario = 15750.50;
    cadena nombre = "Ana Garcia";
    booleano activo = verdadero;

    entero anioNacimiento = 2025 - edad;
    decimal bono = salario * 0.10;
    decimal salarioTotal = salario + bono;
    entero residuo = edad % 7;

    edad = edad + 1;
    imprimir(nombre);
    imprimir(salarioTotal);
}
"""),
("02 Control de Flujo", """// Ejemplo 02 - Estructuras si / sino
programa {
    entero nota = 78;
    booleano aprobado = falso;
    cadena calificacion = "indefinida";

    si (nota >= 90) {
        calificacion = "Excelente";
        aprobado = verdadero;
    } sino {
        si (nota >= 70) {
            calificacion = "Aprobado";
            aprobado = verdadero;
        } sino {
            calificacion = "Reprobado";
            aprobado = falso;
        }
    }

    booleano conBecas = aprobado && (nota >= 75);
    imprimir(calificacion);
    imprimir(conBecas);
}
"""),
("03 Bucles mientras y para", """// Ejemplo 03 - Bucles mientras y para
programa {
    entero i = 1;
    entero suma = 0;
    mientras (i <= 100) {
        suma = suma + i;
        i = i + 1;
    }
    imprimir(suma);

    entero n = 10;
    entero factorial = 1;
    entero k = n;
    mientras (k > 1) {
        factorial = factorial * k;
        k = k - 1;
    }
    imprimir(factorial);

    entero base = 7;
    para (entero j = 1; j <= 12; j = j + 1) {
        entero resultado = base * j;
        imprimir(resultado);
    }
}
"""),
("04 Expresiones Complejas", """// Ejemplo 04 - Expresiones y Operadores
programa {
    decimal a = 10.5;
    decimal b = 3.2;
    decimal c = 0.0;

    c = a + b * 2.0 - 1.5;
    decimal d = a / b + b % 3.0;

    booleano r1 = (a > 5.0) && (b < 5.0);
    booleano r2 = (a == 10.5) || (b == 0.0);
    booleano r3 = !(a < b) && (c != 0.0);

    entero x = 100;
    entero y = 37;
    entero cociente = x / y;
    entero residuoMod = x % y;

    imprimir(c);
    imprimir(r1);
    imprimir(cociente);
}
"""),
("05 Errores Lexicos", """// Ejemplo 05 - Errores Lexicos Intencionales
programa {
    entero x = 10;
    decimal y = 3.14;
    cadena mensaje = "Hola";

    // ERROR 1: caracter ilegal @
    entero z = 5@2;

    // ERROR 2: caracter ilegal #
    decimal pi = 3.14#15;

    // ERROR 3: variable duplicada
    entero x = 99;

    booleano activo = verdadero;
    entero contador = 0;
    mientras (contador < 5) {
        contador = contador + 1;
    }
    imprimir(x);
}
"""),
("06 Strings y Booleanos", """// Ejemplo 06 - Cadenas y Logica Booleana
programa {
    cadena saludo = "Hola, Mundo!";
    cadena vacia = "";

    booleano flagV = verdadero;
    booleano flagF = falso;

    booleano tt = flagV && flagV;
    booleano tf = flagV && flagF;
    booleano ff = flagF && flagF;
    booleano tt2 = flagV || flagV;

    booleano noV = !flagV;
    booleano noF = !flagF;
    booleano complejo = (tt || tf) && (!ff) && (tt2 != ff);

    imprimir(saludo);
    imprimir(complejo);
}
"""),
("07 Programa Completo", """// Ejemplo 07 - Programa Integrador
programa {
    entero totalAlumnos = 30;
    decimal sumaNotas = 0.0;
    decimal promedio = 0.0;
    entero aprobados = 0;
    entero reprobados = 0;
    booleano cursoActivo = verdadero;
    cadena nombreCurso = "Compiladores";

    decimal nota1 = 85.0;
    decimal nota2 = 72.5;
    decimal nota3 = 91.0;
    decimal nota4 = 60.0;
    decimal nota5 = 55.5;

    sumaNotas = nota1 + nota2 + nota3 + nota4 + nota5;
    entero totalMuestras = 5;
    promedio = sumaNotas / totalMuestras;

    si (nota1 >= 70) { aprobados = aprobados + 1; } sino { reprobados = reprobados + 1; }
    si (nota2 >= 70) { aprobados = aprobados + 1; } sino { reprobados = reprobados + 1; }
    si (nota3 >= 70) { aprobados = aprobados + 1; } sino { reprobados = reprobados + 1; }

    cadena estadoCurso = "indefinido";
    si (promedio >= 90) {
        estadoCurso = "Excelente";
    } sino {
        si (promedio >= 75) {
            estadoCurso = "Bueno";
        } sino {
            estadoCurso = "Regular";
        }
    }

    booleano cursoExitoso = cursoActivo && (aprobados > reprobados);
    entero porcentaje = (aprobados * 100) / totalMuestras;

    imprimir(nombreCurso);
    imprimir(promedio);
    imprimir(estadoCurso);
    imprimir(cursoExitoso);
}
"""),
]

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

        self._cv.create_rectangle(x+2,y+2,x+NW-2,y+NH-2, fill=stroke, outline="", stipple="gray12")

        self._cv.create_rectangle(x,y,x+NW,y+NH, fill=fill, outline=stroke, width=1.5, tags=("node",))

        if get_kids(node):
            dot_fill = stroke if node.get("_id") in self._collapsed else ""
            self._cv.create_oval(cx-4,y+NH-8,cx+4,y+NH-1, fill=dot_fill, outline=stroke, width=1)

        self._cv.create_text(x+12, y+NH//2, text=icon, fill=stroke,
                              font=self._font_n, anchor="center")

        lbl = node_label(node)
        if len(lbl) > 13: lbl = lbl[:12]+"..."
        sub = node.get("_label","")
        lbl_y = y + NH//2 - (4 if sub else 0)
        self._cv.create_text(cx+4, lbl_y, text=lbl, fill="#e0f4ff",
                              font=self._font_n, anchor="center")
        if sub:
            self._cv.create_text(cx+4, y+NH//2+8, text=sub, fill=stroke,
                                  font=self._font_s, anchor="center")

        nid = node.get("_id"); tag = f"nid_{nid}"
        self._cv.create_rectangle(x,y,x+NW,y+NH, fill="", outline="", tags=("node",tag))
        self._cv.tag_bind(tag, "<Button-1>", lambda e,i=nid: self._toggle(i))

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
        self._tema_actual = "oscuro"          # rastrea el tema activo
        self._registered_treeviews = []       # lista de (widget, style_name)
        self._build_menu()
        self._build_banner()
        self._build_header()
        self._build_main()
        self._build_footer()
        self._configure_highlighting()
        self._load_example(0)
        self.bind("<F5>", lambda e: self._analyze())

    def _build_menu(self):
        self._menubar = tk.Menu(self, bg=C["bg2"], fg=C["t1"], activebackground=C["red"],
                     activeforeground="#fff", relief="flat")
        mb = self._menubar
        self.config(menu=mb)
        self._menu_archivo = tk.Menu(mb, tearoff=0, bg=C["bg2"], fg=C["t1"],
                     activebackground=C["red"], activeforeground="#fff")
        mf = self._menu_archivo
        mf.add_command(label="Nuevo   Ctrl+N", command=self._new)
        mf.add_command(label="Abrir...  Ctrl+O", command=self._open)
        mf.add_command(label="Guardar  Ctrl+S", command=self._save)
        mf.add_separator(); mf.add_command(label="Salir", command=self.quit)
        mb.add_cascade(label=" Archivo ", menu=mf)
        self._menu_analizar = tk.Menu(mb, tearoff=0, bg=C["bg2"], fg=C["t1"],
                     activebackground=C["red"], activeforeground="#fff")
        ma = self._menu_analizar
        ma.add_command(label="Analizar  F5", command=self._analyze)
        ma.add_command(label="Limpiar",      command=self._clear_all)
        mb.add_cascade(label=" Analizar ", menu=ma)

        mt = tk.Menu(mb, tearoff=0, bg=C["bg3"], fg=C["t2"], activebackground=C["bg4"],
                     activeforeground=C["cyan"], relief="flat")
        mt.add_command(label="Claro", command=self.configurar_tema_claro)
        mt.add_command(label="Oscuro", command=self.configurar_tema_oscuro)
        self._menu_tema = mt
        mb.add_cascade(label="Tema", menu=mt)

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
        for name in ("editor","tokens","tree","semantic","intermediate","errors"):
            f = tk.Frame(self._left, bg=C["bg1"]); self._tab_frames[name] = f
        self._show_tab("editor")
        self._build_editor_tab()
        self._build_tokens_tab()
        self._build_tree_tab()
        self._build_semantic_tab()
        self._build_intermediate_tab()
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
        self._tab_bar = tk.Frame(self._left, bg=C["bg2"]); self._tab_bar.pack(fill="x")
        bar = self._tab_bar
        tk.Frame(bar, bg=C["bd"], height=1).pack(fill="x", side="bottom")
        self._tab_btns = {}; self._badge_vars = {}
        tabs = [("editor","Editor",None),("tokens","Tokens","tokens"),
                ("tree","Arbol Sint.","tree"),("semantic","Semantico","sem"),
                ("intermediate","Cod. Intermedio","tac"),("errors","Errores","errors")]
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
        es_claro = self._tema_actual == "claro"
        for n, btn in self._tab_btns.items():
            is_active = (n == name)
            btn.configure(
                fg=("#0a84ff" if es_claro else C["cyan"])  if is_active else ("#4a4a4a" if es_claro else C["t3"]),
                bg=("#ffffff" if es_claro else C["bg3"])   if is_active else ("#e9ecef" if es_claro else C["bg2"]))
        self._tab_bar.configure(bg="#e9ecef" if es_claro else C["bg2"])
        for frm in self._tab_bar.winfo_children():
            try: frm.configure(bg="#e9ecef" if es_claro else C["bg2"])
            except: pass
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

    def _build_intermediate_tab(self):
        f = self._tab_frames["intermediate"]
        ph = tk.Frame(f, bg=C["bg2"]); ph.pack(fill="x")
        tk.Frame(ph, bg=C["blue"], width=3).pack(side="left", fill="y")
        tk.Label(ph, text=" CODIGO INTERMEDIO  -  TAC (3 direcciones)",
                 bg=C["bg2"], fg=C["blue"], font=self.fn_disp, pady=7).pack(side="left")
        self._lbl_tac_hdr = tk.Label(ph, text="---", bg=C["bg2"],
                                      fg=C["t3"], font=self.fn_ui)
        self._lbl_tac_hdr.pack(side="right", padx=8)
        tk.Frame(f, bg=C["bd"], height=1).pack(fill="x")

        sub = tk.Frame(f, bg=C["bg2"]); sub.pack(fill="x")
        tk.Frame(sub, bg=C["bd"], height=1).pack(fill="x", side="bottom")
        self._tac_subview = tk.StringVar(value="orig")
        self._tac_sub_btns = {}
        for key, lbl in [("orig","Sin optimizar"),("opt","Optimizado"),
                         ("cmp","Comparacion"),("info","Que es?")]:
            b = tk.Label(sub, text=lbl, bg=C["bg2"], fg=C["t2"], font=self.fn_disp,
                         padx=10, pady=6, cursor="hand2",
                         highlightthickness=1, highlightbackground=C["bd"])
            b.pack(side="left", padx=4, pady=4)
            b.bind("<Button-1>", lambda e, k=key: self._show_tac_sub(k))
            self._tac_sub_btns[key] = b

        self._lbl_tac_metric = tk.Label(sub, text="", bg=C["bg2"], fg=C["t3"],
                                          font=("Consolas",9))
        self._lbl_tac_metric.pack(side="right", padx=10)

        self._tac_body = tk.Frame(f, bg=C["bg1"]); self._tac_body.pack(fill="both", expand=True)
        self._tac_subframes = {}
        for key in ("orig","opt","cmp","info"):
            sf = tk.Frame(self._tac_body, bg=C["bg1"])
            self._tac_subframes[key] = sf

        self._tac_tree_orig = self._make_treeview(self._tac_subframes["orig"],
            ("n","instruccion","op","arg1","arg2","dest"),
            ("#","Instruccion","Op","Arg1","Arg2","Dest"),
            (40, 280, 90, 90, 90, 90))
        self._tac_tree_opt = self._make_treeview(self._tac_subframes["opt"],
            ("n","instruccion","op","arg1","arg2","dest"),
            ("#","Instruccion","Op","Arg1","Arg2","Dest"),
            (40, 280, 90, 90, 90, 90))

        cmp_outer = tk.Frame(self._tac_subframes["cmp"], bg=C["bg1"])
        cmp_outer.pack(fill="both", expand=True)
        cmp_left  = tk.Frame(cmp_outer, bg=C["bg1"]); cmp_left.pack(side="left", fill="both", expand=True)
        tk.Frame(cmp_outer, bg=C["bd"], width=1).pack(side="left", fill="y")
        cmp_right = tk.Frame(cmp_outer, bg=C["bg1"]); cmp_right.pack(side="left", fill="both", expand=True)
        tk.Label(cmp_left,  text="ORIGINAL", bg=C["bg2"], fg=C["amber"],
                 font=self.fn_disp, pady=4).pack(fill="x")
        tk.Label(cmp_right, text="OPTIMIZADO", bg=C["bg2"], fg=C["green"],
                 font=self.fn_disp, pady=4).pack(fill="x")
        self._tac_cmp_orig = tk.Text(cmp_left, bg=C["bg1"], fg=C["t1"],
                                       font=("Consolas",10), relief="flat", bd=0,
                                       padx=10, pady=6, wrap="none", state="disabled")
        self._tac_cmp_opt  = tk.Text(cmp_right, bg=C["bg1"], fg=C["t1"],
                                       font=("Consolas",10), relief="flat", bd=0,
                                       padx=10, pady=6, wrap="none", state="disabled")
        self._tac_cmp_orig.pack(fill="both", expand=True)
        self._tac_cmp_opt.pack(fill="both", expand=True)

        info = tk.Text(self._tac_subframes["info"], bg=C["bg1"], fg=C["t1"],
                        font=("Consolas",10), relief="flat", bd=0,
                        padx=14, pady=10, wrap="word", state="normal")
        info.insert("1.0", _TEXTO_INFO_TAC)
        info.tag_configure("h1", foreground=C["cyan"], font=("Courier New",12,"bold"))
        info.tag_configure("h2", foreground=C["amber"], font=("Courier New",10,"bold"))
        info.tag_configure("code", foreground=C["green"], font=("Consolas",10))
        info.tag_configure("note", foreground=C["t2"])

        for ln_idx, line in enumerate(_TEXTO_INFO_TAC.split("\n"), start=1):
            if line.startswith("# "):
                info.tag_add("h1", f"{ln_idx}.0", f"{ln_idx}.end")
            elif line.startswith("## "):
                info.tag_add("h2", f"{ln_idx}.0", f"{ln_idx}.end")
            elif line.startswith("    "):
                info.tag_add("code", f"{ln_idx}.0", f"{ln_idx}.end")
        info.configure(state="disabled")
        info.pack(fill="both", expand=True)

        self._show_tac_sub("orig")

    def _show_tac_sub(self, key):
        for k, sf in self._tac_subframes.items(): sf.pack_forget()
        self._tac_subframes[key].pack(fill="both", expand=True)
        for k, btn in self._tac_sub_btns.items():
            btn.configure(fg=C["cyan"] if k == key else C["t2"],
                          bg=C["bg3"] if k == key else C["bg2"],
                          highlightbackground=C["cyan"] if k == key else C["bd"])
        self._tac_subview.set(key)

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
        self._btn_run = tk.Label(self._footer, text=" ANALIZAR [F5] ", bg=C["red"], fg="#fff",
                            font=("Courier New",9,"bold"), padx=4, pady=6, cursor="hand2")
        self._btn_run.pack(side="left", padx=8, pady=5)
        self._btn_run.bind("<Button-1>", lambda e: self._analyze())
        self._btn_run.bind("<Enter>",  lambda e: self._btn_run.configure(bg="#ff4070"))
        self._btn_run.bind("<Leave>",  lambda e: self._btn_run.configure(bg=C["red"]))
        self._btn_clr = tk.Label(self._footer, text=" LIMPIAR ", bg=C["bg3"], fg=C["t2"],
                            font=self.fn_disp, padx=4, pady=6,
                            highlightthickness=1, highlightbackground=C["bd"], cursor="hand2")
        self._btn_clr.pack(side="left", padx=4, pady=5)
        self._btn_clr.bind("<Button-1>", lambda e: self._clear_all())
        self._btn_ex = tk.Label(self._footer, text=" EJEMPLOS v ", bg=C["bg3"], fg=C["amber"],
                                 font=self.fn_disp, padx=4, pady=6,
                                 highlightthickness=1, highlightbackground=C["bd"], cursor="hand2")
        self._btn_ex.pack(side="left", padx=4, pady=5)
        self._btn_ex.bind("<Button-1>", self._toggle_example_menu)
        self._btn_ex.bind("<Enter>", lambda e: self._btn_ex.configure(highlightbackground=C["amber"]))
        self._btn_ex.bind("<Leave>", lambda e: self._btn_ex.configure(highlightbackground=C["bd"]))
        self._btn_rep = tk.Label(self._footer, text=" REPORTES HTML ", bg=C["bg3"], fg=C["green"],
                            font=self.fn_disp, padx=4, pady=6,
                            highlightthickness=1, highlightbackground=C["bd"], cursor="hand2")
        self._btn_rep.pack(side="left", padx=4, pady=5)
        self._btn_rep.bind("<Button-1>", lambda e: self._generar_reportes())
        self._btn_rep.bind("<Enter>", lambda e: self._btn_rep.configure(highlightbackground=C["green"]))
        self._btn_rep.bind("<Leave>", lambda e: self._btn_rep.configure(highlightbackground=C["bd"]))
        self._lbl_ft_tok = tk.Label(self._footer, text="Tokens: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_tok.pack(side="right", padx=8)
        self._lbl_ft_err = tk.Label(self._footer, text="Errores: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_err.pack(side="right", padx=8)
        self._lbl_ft_sym = tk.Label(self._footer, text="Simbolos: 0", bg=C["bg2"],
                                     fg=C["t3"], font=("Consolas",9))
        self._lbl_ft_sym.pack(side="right", padx=8)

    def _toggle_example_menu(self, event=None):
        if self._example_menu_open: self._close_example_menu()
        else: self._open_example_menu()

    def _open_example_menu(self):
        self._close_example_menu()
        x = self._btn_ex.winfo_rootx()
        y = self._btn_ex.winfo_rooty()
        item_h = 44
        menu_h = len(EJEMPLOS) * item_h + 30

        # Colores según tema activo
        _claro = getattr(self, "_tema_actual", "oscuro") == "claro"
        _bg_win   = "#dee2e6" if _claro else C["bd"]
        _bg_hdr   = "#e9ecef" if _claro else C["bg4"]
        _fg_hdr   = "#0a84ff" if _claro else C["cyan"]
        _sep_hdr  = "#0a84ff" if _claro else C["cyan"]
        _sep_row  = "#ced4da" if _claro else C["bd"]
        _bg_row   = "#f8f9fa" if _claro else C["bg4"]
        _bg_hover = "#dde3ea" if _claro else C["bg3"]
        _fg_num   = "#6c757d" if _claro else C["t3"]
        _fg_name  = "#1e272e" if _claro else C["t1"]

        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.configure(bg=_bg_win)
        win.geometry(f"310x{menu_h}+{x}+{y-menu_h-2}")
        win.lift(); win.focus_force()
        hdr = tk.Frame(win, bg=_bg_hdr); hdr.pack(fill="x")
        tk.Frame(hdr, bg=_sep_hdr, height=1).pack(fill="x")
        tk.Label(hdr, text="  SELECCIONAR EJEMPLO", bg=_bg_hdr, fg=_fg_hdr,
                 font=("Courier New",7,"bold"), pady=6).pack()
        tk.Frame(hdr, bg=_bg_win, height=1).pack(fill="x")
        for idx,(title,_) in enumerate(EJEMPLOS):
            parts = title.split(" ",1); num = parts[0]; name = parts[1] if len(parts)>1 else title
            row = tk.Frame(win, bg=_bg_row, cursor="hand2"); row.pack(fill="x")
            tk.Frame(row, bg=_sep_row, height=1).pack(fill="x", side="bottom")
            tk.Label(row, text=num, bg=_bg_row, fg=_fg_num,
                     font=("Courier New",10,"bold"), width=4, pady=10).pack(side="left")
            tk.Label(row, text=name, bg=_bg_row, fg=_fg_name,
                     font=("Consolas",10), pady=10, anchor="w").pack(side="left",fill="x",expand=True)
            def on_enter(e, w=row, bh=_bg_hover):
                w.configure(bg=bh)
                for c in w.winfo_children(): c.configure(bg=bh)
            def on_leave(e, w=row, br=_bg_row):
                w.configure(bg=br)
                for c in w.winfo_children(): c.configure(bg=br)
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
            tipo=tok["tipo"]; linea=tok["linea"]; col=tok["columna"]-1
            length=tok.get("longitud", len(tok["valor"]))
            start=f"{linea}.{col}"; end_=f"{linea}.{col+length}"; tag=f"tok_{tipo}"
            if tag in self._editor.tag_names(): self._editor.tag_add(tag,start,end_)
        for m in _re.finditer(r'//[^\n]*', codigo):
            ln=codigo[:m.start()].count("\n")+1; c0=m.start()-codigo[:m.start()].rfind("\n")-1
            self._editor.tag_add("tok_COMENTARIO",f"{ln}.{c0}",f"{ln}.{c0+len(m.group())}")

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

        ast = build_tree(tokens, errores); self._arbol.draw(ast)
        check_semantic(ast, tabla, errores)
        self._lbl_tree_hdr.configure(text="arbol construido")

        # La tabla se llena en check_semantic (scopes reales), recien aca
        # tenemos la lista de simbolos para pintar el panel.
        for row in self._sym_tree.get_children(): self._sym_tree.delete(row)
        simbolos = tabla.todos_los_simbolos()
        for i,sim in enumerate(simbolos):
# --- INCORPORACIÓN REQUERIMIENTOS ROL B (Formateo Extendido) ---
            tipo_visual = sim.tipo
            
            # Buscamos si el símbolo tiene un atributo 'kind' o si el tipo es 'arreglo'/'funcion'
            kind = getattr(sim, 'kind', '').lower()
            tipo_lower = str(sim.tipo).lower()
            
            if 'arreglo' in tipo_lower or kind == 'array':
                # Obtenemos tamaño y tipo base si tu objeto 'sim' los guarda (ej. sim.size y sim.subtipo)
                # Si no los guarda, ponemos valores por defecto o dinámicos
                tamano = getattr(sim, 'size', '—')
                tipo_base = getattr(sim, 'elem_type', getattr(sim, 'subtipo', '—'))
                tipo_visual = f"array [size: {tamano} of {tipo_base}]"
                
            elif 'funcion' in tipo_lower or kind == 'function':
                # Obtenemos los parámetros y tipo de retorno del objeto símbolo
                params = getattr(sim, 'params', [])
                if isinstance(params, list):
                    params = ", ".join(f"{p.get('tipo','?')} {p.get('nombre','?')}" for p in params)
                retorno = getattr(sim, 'return_type', 'void')
                tipo_visual = f"function ({params}) -> {retorno}"
            # ------------------------------

            self._sym_tree.insert("","end",
                values=(sim.nombre,tipo_visual,sim.linea,str(sim.valor) if sim.valor is not None else "---"),
                tags=("par" if i%2==0 else "impar",))
            
        self._lbl_sym_count.configure(text=f"{len(simbolos)} simbolos")
        self._build_semantic_panel(tokens, simbolos, errores)

        quads = []
        quads_opt = []
        if errores:
            self._populate_tac([], [])
        else:
            try:
                quads = GeneradorTAC().generar(ast)
                quads_opt, _traza = optimizar(quads)
                self._populate_tac(quads, quads_opt)
            except Exception as ex:
                self._log("error", f"Error generando codigo intermedio: {ex}")
                self._populate_tac([], [])

        # Guardar para el boton de reportes HTML
        self._last_tokens = tokens
        self._last_tabla = tabla
        self._last_errores = errores
        self._last_quads = quads
        self._last_quads_opt = quads_opt

        self._console.configure(state="normal"); self._console.delete("1.0","end")
        _claro = getattr(self, "_tema_actual", "oscuro") == "claro"
        _col_ok  = "#27ae60" if _claro else C["green"]
        _col_err = "#c0392b" if _claro else C["red"]
        if errores:
            self._log("warn", f"Se encontraron {len(errores)} error(es):")
            for e in errores:
                self._log("error", f"  X  {fmt_error(e) if isinstance(e, dict) else e}")
            self._lbl_err_hdr.configure(text=f"{len(errores)} error(es)", fg=_col_err)
            self._lbl_status.configure(text=f"{len(errores)} error(es)", fg=_col_err)
        else:
            self._log("ok", f"Analisis completado -- {len(tokens)} tokens - {len(simbolos)} simbolos - 0 errores")
            self._lbl_err_hdr.configure(text="sin errores", fg=_col_ok)
            self._lbl_status.configure(text="Analisis OK", fg=_col_ok)
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
            elif k in ("tree","sem","tac"): v.set("OK")
            elif k=="errors": v.set(str(len(errores)) if errores else "")

    def _populate_tac(self, quads, quads_opt):

        for row in self._tac_tree_orig.get_children(): self._tac_tree_orig.delete(row)
        for row in self._tac_tree_opt.get_children():  self._tac_tree_opt.delete(row)

        filas_orig = formatear_tac(quads)
        filas_opt  = formatear_tac(quads_opt)

        for i, fila in enumerate(filas_orig):
            self._tac_tree_orig.insert("","end",
                values=(fila["n"], fila["instruccion"], fila["op"],
                        fila["arg1"], fila["arg2"], fila["dest"]),
                tags=("par" if i%2==0 else "impar",))
        for i, fila in enumerate(filas_opt):
            self._tac_tree_opt.insert("","end",
                values=(fila["n"], fila["instruccion"], fila["op"],
                        fila["arg1"], fila["arg2"], fila["dest"]),
                tags=("par" if i%2==0 else "impar",))

        self._tac_cmp_orig.configure(state="normal")
        self._tac_cmp_orig.delete("1.0","end")
        for fila in filas_orig:
            self._tac_cmp_orig.insert("end", f"{fila['n']:>3}: {fila['instruccion']}\n")
        self._tac_cmp_orig.configure(state="disabled")

        self._tac_cmp_opt.configure(state="normal")
        self._tac_cmp_opt.delete("1.0","end")
        for fila in filas_opt:
            self._tac_cmp_opt.insert("end", f"{fila['n']:>3}: {fila['instruccion']}\n")
        self._tac_cmp_opt.configure(state="disabled")

        n_o = len(quads); n_opt = len(quads_opt)

        def _temps(qs):
            tset = set()
            for q in qs:
                for x in (q.arg1, q.arg2, q.dest):
                    if isinstance(x, str) and x.startswith("$t") and x[2:].isdigit():
                        tset.add(x)
            return len(tset)
        t_o = _temps(quads); t_opt = _temps(quads_opt)
        red = (1 - n_opt/n_o)*100 if n_o else 0
        self._lbl_tac_hdr.configure(text=f"{n_o} cuadruplos -> {n_opt} (-{red:.0f}%)")
        self._lbl_tac_metric.configure(
            text=f"cuadruplos: {n_o} -> {n_opt}    temporales: {t_o} -> {t_opt}")

    def _build_semantic_panel(self, tokens, simbolos, errores):
        for w in self._sem_frame.winfo_children(): w.destroy()
        # Usar colores según el tema activo
        es_claro = self._tema_actual == "claro"
        BG_PANEL  = "#f8f9fa"  if es_claro else C["bg1"]
        BG_CARD   = "#ffffff"  if es_claro else C["bg3"]
        BG_SEP    = "#dee2e6"  if es_claro else C["bd"]
        FG_TITLE  = "#e67e22"  if es_claro else C["amber"]
        FG_TEXT   = "#1e272e"  if es_claro else C["t2"]
        FG_NUM    = "#1e272e"  if es_claro else C["t1"]
        FG_SUB    = "#6c757d"  if es_claro else C["t3"]

        # Parchar el frame contenedor
        self._sem_frame.configure(bg=BG_PANEL)
        self._sem_canvas.configure(bg=BG_PANEL)

        pad = {"padx":14,"pady":4}
        def section(title):
            tk.Frame(self._sem_frame,bg=BG_SEP,height=1).pack(fill="x",padx=0,pady=8)
            tk.Label(self._sem_frame,text=title,bg=BG_PANEL,fg=FG_TITLE,
                     font=("Courier New",8,"bold"),anchor="w").pack(fill="x",**pad)
            tk.Frame(self._sem_frame,bg=BG_SEP,height=1).pack(fill="x")
        def stat_row(icon,label,val,col=None):
            if col is None: col = FG_NUM
            row=tk.Frame(self._sem_frame,bg=BG_PANEL); row.pack(fill="x")
            tk.Frame(row,bg=BG_SEP,height=1).pack(fill="x",side="bottom")
            tk.Label(row,text=icon,bg=BG_PANEL,fg=col,font=("Consolas",11),width=3).pack(side="left",padx=8,pady=5)
            tk.Label(row,text=label,bg=BG_PANEL,fg=FG_TEXT,font=("Consolas",10),anchor="w").pack(side="left",fill="x",expand=True)
            tk.Label(row,text=str(val),bg=BG_PANEL,fg=col,font=("Courier New",10,"bold"),padx=12).pack(side="right")
        TIPOS={"ENTERO","DECIMAL","CADENA_TIPO","BOOLEANO"}
        ifs=sum(1 for t in tokens if t["tipo"]=="SI")
        whiles=sum(1 for t in tokens if t["tipo"]=="MIENTRAS")
        fors=sum(1 for t in tokens if t["tipo"]=="PARA")
        prints=sum(1 for t in tokens if t["tipo"]=="IMPRIMIR")
        decls=sum(1 for t in tokens if t["tipo"] in TIPOS)
        asigs=sum(1 for t in tokens if t["tipo"]=="ASIGNAR")
        section("ESTADISTICAS")
        grid=tk.Frame(self._sem_frame,bg=BG_PANEL); grid.pack(fill="x",padx=10,pady=6)
        colores_cards = [C["cyan"],C["green"],C["amber"],C["purple"]] if not es_claro else \
                        ["#2980b9","#27ae60","#e67e22","#8e44ad"]
        for idx,(k,col,lbl) in enumerate([(len(tokens),colores_cards[0],"Total Tokens"),(len(simbolos),colores_cards[1],"Simbolos"),
                                            (decls,colores_cards[2],"Declaraciones"),(asigs,colores_cards[3],"Asignaciones")]):
            borde = "#dee2e6" if es_claro else C["bd"]
            box=tk.Frame(grid,bg=BG_CARD,padx=8,pady=6,highlightthickness=1,highlightbackground=borde)
            box.grid(row=idx//2,column=idx%2,padx=3,pady=3,sticky="ew"); grid.columnconfigure(idx%2,weight=1)
            tk.Label(box,text=str(k),bg=BG_CARD,fg=col,font=("Courier New",18,"bold")).pack()
            tk.Label(box,text=lbl,bg=BG_CARD,fg=FG_SUB,font=("Courier New",7)).pack()
        section("ESTRUCTURAS DE CONTROL")
        col_ctrl = C["cyan"] if not es_claro else "#2980b9"
        for icon,lbl,val in [("*","Condicionales (si)",ifs),("R","Bucles mientras",whiles),
                               ("@","Bucles para",fors),(">","Llamadas imprimir()",prints)]:
            stat_row(icon,lbl,val,col_ctrl)
        section("DIAGNOSTICO")
        lex_e = [e for e in errores if isinstance(e, dict) and e.get("tipo") == "Lexico"]
        sint_e = [e for e in errores if isinstance(e, dict) and e.get("tipo") == "Sintactico"]
        sem_e = [e for e in errores if isinstance(e, dict) and e.get("tipo") == "Semantico"]
        col_ok  = C["green"] if not es_claro else "#27ae60"
        col_err = C["red"]   if not es_claro else "#c0392b"
        col_wrn = C["amber"] if not es_claro else "#e67e22"
        if not errores: stat_row("V","Sin errores","",col_ok)
        else:
            if lex_e:  stat_row("X", f"{len(lex_e)} error(es) lexico(s)", "", col_err)
            if sint_e: stat_row("X", f"{len(sint_e)} error(es) sintactico(s)", "", col_err)
            if sem_e:  stat_row("X", f"{len(sem_e)} error(es) semantico(s)", "", col_err)
            for e in errores:
                msg = fmt_error(e) if isinstance(e, dict) else str(e)
                tipo = e.get("tipo", "") if isinstance(e, dict) else ""
                col = col_err if tipo in ("Lexico","Semantico") else (col_wrn if tipo=="Sintactico" else FG_TEXT)
                stat_row(".", msg[:55]+"..." if len(msg)>55 else msg, "", col)

    def _generar_reportes(self):
        """Genera todos los reportes HTML del ultimo analisis."""
        if not hasattr(self, "_last_tokens") or self._last_tokens is None:
            self._log("warn", "Primero ejecuta el analisis (F5) antes de generar reportes.")
            return
        salida = filedialog.askdirectory(title="Carpeta destino para los reportes HTML")
        if not salida:
            return
        tac_filas = formatear_tac(self._last_quads) if self._last_quads else []
        tac_opt_filas = formatear_tac(self._last_quads_opt) if self._last_quads_opt else []
        try:
            rutas = _reportes_mod.generar_reportes_completos(
                salida,
                tokens=self._last_tokens,
                tabla=self._last_tabla,
                errores=self._last_errores,
                tac=tac_filas,
                tac_opt=tac_opt_filas,
            )
            self._log("ok", f"{len(rutas)} reporte(s) HTML generado(s) en {salida}")
            for k, r in rutas.items():
                self._log("info", f"  - {k}: {os.path.basename(r)}")
            try:
                webbrowser.open("file://" + os.path.abspath(rutas.get("semanticos") or list(rutas.values())[0]))
            except Exception:
                pass
        except Exception as ex:
            self._log("error", f"No se pudieron generar los reportes: {ex}")

    def _log(self,level,msg):
        self._console.configure(state="normal")
        icon={"ok":"V","error":"X","warn":"!","info":">"}. get(level,">")
        self._console.insert("end",f"  {icon}  {msg}\n",level)
        self._console.see("end"); self._console.configure(state="disabled")

    def _make_treeview(self, parent, cols, headers, widths):
        style_name = f"TV{id(parent)}.Treeview"; style = ttk.Style()
        style.theme_use("clam")
        # Filas con mayor altura para que las celdas respiren
        style.configure(style_name,
                        background=C["bg3"], foreground=C["t1"],
                        fieldbackground=C["bg3"], rowheight=26,
                        font=("Consolas", 10),
                        borderwidth=0, relief="flat")
        # Encabezados con borde inferior visible
        style.configure(f"{style_name}.Heading",
                        background=C["bg2"], foreground=C["cyan"],
                        font=("Courier New", 8, "bold"),
                        relief="groove", borderwidth=1, padding=(6, 5))
        style.map(style_name,
                  background=[("selected", C["red"])],
                  foreground=[("selected", "#ffffff")])
        # Frame exterior: 1px de borde de color actúa como separador de tabla
        frame = tk.Frame(parent, bg=C["bd"], padx=1, pady=1)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1); frame.columnconfigure(0, weight=1)
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style=style_name, selectmode="browse")
        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        for col, hdr, w in zip(cols, headers, widths):
            tree.heading(col, text=hdr)
            tree.column(col, width=w, minwidth=30, anchor="w", stretch=True)
        # Tags alternados: oscuro con dos tonos claramente distintos
        tree.tag_configure("par",   background=C["bg3"], foreground=C["t1"])
        tree.tag_configure("impar", background=C["bg4"], foreground=C["t2"])
        # Registrar para que los cambios de tema lo alcancen
        self._registered_treeviews.append((tree, style_name))
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
        for row in self._tac_tree_orig.get_children(): self._tac_tree_orig.delete(row)
        for row in self._tac_tree_opt.get_children():  self._tac_tree_opt.delete(row)
        for txt in (self._tac_cmp_orig, self._tac_cmp_opt):
            txt.configure(state="normal"); txt.delete("1.0","end"); txt.configure(state="disabled")
        self._lbl_tac_hdr.configure(text="---")
        self._lbl_tac_metric.configure(text="")
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

    def configurar_tema_claro(self):
        """Aplica Modo Claro completo: editor, panel semántico, tablas y todos los widgets"""
        self._tema_actual = "claro"

        # 1. Editor y Consola
        self._editor.configure(bg="#ffffff", fg="#2c3e50", insertbackground="#2c3e50",
                                selectbackground="#0a84ff", selectforeground="#ffffff")
        self._console.configure(bg="#f1f2f6", fg="#1e272e")
        if hasattr(self, '_lnum'):
            self._lnum.configure(bg="#e9ecef"); self._lnum._update()

        # 2. Resaltado de sintaxis (modo claro)
        colores_claro = {
            "tok_PROGRAMA":"#8e44ad","tok_ENTERO":"#2980b9","tok_DECIMAL":"#2980b9",
            "tok_BOOLEANO":"#2980b9","tok_CADENA_TIPO":"#2980b9",
            "tok_SI":"#c0392b","tok_SINO":"#c0392b","tok_MIENTRAS":"#c0392b",
            "tok_PARA":"#c0392b","tok_FUNCION":"#c0392b","tok_RETORNAR":"#c0392b",
            "tok_AND":"#8e44ad","tok_OR":"#8e44ad","tok_NOT":"#8e44ad",
            "tok_VERDADERO":"#d35400","tok_FALSO":"#d35400",
            "tok_IMPRIMIR":"#c0392b","tok_LEER":"#c0392b",
            "tok_NUMERO_ENTERO":"#7f8c8d","tok_NUMERO_DECIMAL":"#7f8c8d",
            "tok_CADENA_LITERAL":"#27ae60","tok_IDENTIFICADOR":"#2c3e50",
            "tok_MAS":"#2980b9","tok_MENOS":"#2980b9","tok_MULTIPLICACION":"#2980b9",
            "tok_DIVIDIR":"#2980b9","tok_MODULO":"#2980b9","tok_ASIGNAR":"#2980b9",
            "tok_IGUAL":"#2980b9","tok_DIFERENTE":"#2980b9",
            "tok_MENOR":"#2980b9","tok_MAYOR":"#2980b9",
            "tok_MENOR_IGUAL":"#2980b9","tok_MAYOR_IGUAL":"#2980b9",
            "tok_COMENTARIO":"#95a5a6",
        }
        for tag, color in colores_claro.items():
            self._editor.tag_configure(tag, foreground=color)
        self._editor.tag_configure("tok_COMENTARIO", foreground="#95a5a6",
                                    font=tkfont.Font(family="Consolas", size=12, slant="italic"))

        # 3. Actualizar los estilos de CADA Treeview registrado (clave del fix)
        estilo = ttk.Style()
        for tree, sname in self._registered_treeviews:
            try:
                estilo.configure(sname,
                    background="#ffffff", foreground="#1e272e",
                    fieldbackground="#ffffff", rowheight=26,
                    font=("Consolas", 10), borderwidth=0, relief="flat")
                estilo.configure(f"{sname}.Heading",
                    background="#dde3ea", foreground="#1a252f",
                    font=("Courier New", 8, "bold"), relief="groove",
                    borderwidth=1, padding=(6, 5))
                estilo.map(sname,
                    background=[("selected", "#0a84ff"), ("!selected", "#ffffff")],
                    foreground=[("selected", "#ffffff"), ("!selected", "#1e272e")])
                # Forzar repintado de tags y de cada fila existente
                tree.configure(background="#ffffff", foreground="#1e272e", fieldbackground="#ffffff")
                tree.tag_configure("par",   background="#ffffff",  foreground="#1e272e")
                tree.tag_configure("impar", background="#f0f4f8", foreground="#2c3e50")
                def _repintar(tv):
                    def _walk(items):
                        for item in items:
                            tags = list(tv.item(item, "tags"))
                            if not tags: tags = ["par"]
                            tv.item(item, tags=("impar",) if "impar" in tags else ("par",))
                            _walk(tv.get_children(item))
                    _walk(tv.get_children())
                _repintar(tree)
                tree.selection_remove(tree.selection())
            except Exception:
                pass

        # 4. Limpiar recursivamente todos los frames, labels y canvas
        def limpiar(w):
            for hijo in w.winfo_children():
                clase = hijo.winfo_class()
                if clase in ("Frame","LabelFrame","TLabelframe","TFrame"):
                    try: hijo.configure(bg="#f8f9fa")
                    except: pass
                elif clase in ("Label","TLabel"):
                    try:
                        txt = hijo.cget("text").lower()
                        fg  = hijo.cget("foreground")
                        if "sin errores" in txt or ("ok" in txt and "analisis" in txt) or fg in (C["green"],"#27ae60"):
                            hijo.configure(bg="#f8f9fa", fg="#27ae60")
                        elif "error" in txt or fg in (C["red"],"#c0392b"):
                            hijo.configure(bg="#f8f9fa", fg="#c0392b")
                        else:
                            hijo.configure(bg="#f8f9fa", fg="#1e272e")
                    except:
                        try: hijo.configure(bg="#f8f9fa", fg="#1e272e")
                        except: pass
                elif clase == "Canvas":
                    try: hijo.configure(bg="#f8f9fa", highlightthickness=0)
                    except: pass
                elif clase == "Text":
                    try: hijo.configure(bg="#f8f9fa", fg="#1e272e")
                    except: pass
                if hijo.winfo_children() and clase != "Treeview":
                    limpiar(hijo)
        limpiar(self)

        # 6. Actualizar menú
        BG_M = "#f0f0f0"; FG_M = "#1e272e"; ABG_M = "#0a84ff"
        for menu in (self._menubar, self._menu_archivo, self._menu_analizar, self._menu_tema):
            try: menu.configure(bg=BG_M, fg=FG_M, activebackground=ABG_M, activeforeground="#ffffff")
            except: pass

        # 7. Barra de pestañas y sus botones
        self._tab_bar.configure(bg="#e9ecef")
        for frm in self._tab_bar.winfo_children():
            try: frm.configure(bg="#e9ecef")
            except: pass
        for n, btn in self._tab_btns.items():
            is_active = (n == self._active_tab)
            btn.configure(
                bg="#ffffff" if is_active else "#e9ecef",
                fg="#0a84ff" if is_active else "#4a4a4a")
        # Badges
        for frm in self._tab_bar.winfo_children():
            for child in frm.winfo_children():
                if child.winfo_class() == "Label" and child not in self._tab_btns.values():
                    try: child.configure(bg="#e74c3c", fg="#ffffff")
                    except: pass

        # 8. Footer
        self._footer.configure(bg="#e9ecef")
        for w in self._footer.winfo_children():
            cls = w.winfo_class()
            if cls == "Frame":
                try: w.configure(bg="#0a84ff" if w.cget("height")==1 else "#e9ecef")
                except: pass
        self._btn_clr.configure(bg="#dee2e6", fg="#2c3e50", highlightbackground="#adb5bd")
        self._btn_ex.configure(bg="#dee2e6",  fg="#e67e22", highlightbackground="#adb5bd")
        self._btn_rep.configure(bg="#dee2e6", fg="#27ae60", highlightbackground="#adb5bd")
        self._lbl_ft_tok.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_ft_sym.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_ft_err.configure(bg="#e9ecef", fg="#6c757d")

        # 9. Header (banner + barra de titulo)
        # _lbl_status y _lbl_err_hdr: respetar estado ok/error tras analisis
        _st_txt = self._lbl_status.cget("text").lower()
        _er_txt = self._lbl_err_hdr.cget("text").lower()
        if "ok" in _st_txt or "analisis" in _st_txt:
            self._lbl_status.configure(bg="#e9ecef", fg="#27ae60")
        elif "error" in _st_txt:
            self._lbl_status.configure(bg="#e9ecef", fg="#c0392b")
        else:
            self._lbl_status.configure(bg="#e9ecef", fg="#2c3e50")
        if "sin errores" in _er_txt:
            self._lbl_err_hdr.configure(bg="#e9ecef", fg="#27ae60")
        elif "error" in _er_txt:
            self._lbl_err_hdr.configure(bg="#e9ecef", fg="#c0392b")
        else:
            self._lbl_err_hdr.configure(bg="#e9ecef", fg="#6c757d")
        self._dot.configure(bg="#e9ecef")
        self._lbl_cursor.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_tok_count.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_tok_hdr.configure(bg="#e9ecef",  fg="#6c757d")
        self._lbl_tree_hdr.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_tac_hdr.configure(bg="#e9ecef",  fg="#6c757d")
        self._lbl_tac_metric.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_sym_count.configure(bg="#e9ecef", fg="#6c757d")
        self._lbl_editor_info.configure(bg="#e9ecef", fg="#6c757d")

        # Sub-botones TAC
        cur = self._tac_subview.get()
        for k, btn in self._tac_sub_btns.items():
            btn.configure(
                bg="#ffffff" if k == cur else "#e9ecef",
                fg="#0a84ff" if k == cur else "#4a4a4a",
                highlightbackground="#0a84ff" if k == cur else "#adb5bd")

        # 10. Sub-vista "Que es?" del TAC: ajustar colores del Text informativo
        info_sf = self._tac_subframes.get("info")
        if info_sf:
            for w in info_sf.winfo_children():
                if w.winfo_class() == "Text":
                    w.configure(bg="#f8f9fa", fg="#1e272e")
                    w.tag_configure("h1",   foreground="#8e44ad")
                    w.tag_configure("h2",   foreground="#c0392b")
                    w.tag_configure("code", foreground="#27ae60")
                    w.tag_configure("note", foreground="#4a4a4a")

        # Sub-vistas "Sin optimizar" / "Optimizado" — comparación de texto
        self._tac_cmp_orig.configure(bg="#f8f9fa", fg="#1e272e")
        self._tac_cmp_opt.configure(bg="#f8f9fa",  fg="#1e272e")

        # 11. Consola de errores: re-colorear tags para fondo claro
        self._console.configure(bg="#f1f2f6", fg="#1e272e")
        self._console.tag_config("ok",    foreground="#27ae60")
        self._console.tag_config("error", foreground="#c0392b")
        self._console.tag_config("warn",  foreground="#d35400")
        self._console.tag_config("info",  foreground="#2980b9")

        if hasattr(self, '_last_tokens') and self._last_tokens is not None:
            self._build_semantic_panel(self._last_tokens,
                                       self._last_tabla.todos_los_simbolos() if self._last_tabla else [],
                                       self._last_errores or [])

        # 6. Forzar redibujado final
        self.update_idletasks()
        self._on_key_editor()
        self._log("info", "Tema cambiado a Modo Claro")

    def configurar_tema_oscuro(self):
        """Revierte al tema oscuro original"""
        self._tema_actual = "oscuro"

        # 1. Editor y Consola
        self._editor.configure(bg=C["bg1"], fg=C["t1"], insertbackground=C["cyan"],
                                selectbackground=C["red"], selectforeground="#fff")
        self._console.configure(bg=C["bg1"], fg=C["green"])
        if hasattr(self, '_lnum'):
            self._lnum.configure(bg=C["bg1"]); self._lnum._update()

        # 2. Resaltado de sintaxis original
        for tipo, color in HL.items():
            self._editor.tag_configure(f"tok_{tipo}", foreground=color)
        self._editor.tag_configure("tok_COMENTARIO", foreground=C["t3"],
                                    font=tkfont.Font(family="Consolas", size=12, slant="italic"))

        # 3. Restaurar estilos de cada Treeview registrado
        estilo = ttk.Style()
        for tree, sname in self._registered_treeviews:
            try:
                estilo.configure(sname,
                    background=C["bg3"], foreground=C["t1"],
                    fieldbackground=C["bg3"], rowheight=22,
                    font=("Consolas", 10))
                estilo.configure(f"{sname}.Heading",
                    background=C["bg2"], foreground=C["cyan"],
                    font=("Courier New", 8, "bold"), relief="flat")
                estilo.map(sname,
                    background=[("selected", C["red"]), ("!selected", C["bg3"])],
                    foreground=[("selected", "#ffffff"), ("!selected", C["t1"])])
                tree.configure(background=C["bg3"], foreground=C["t1"], fieldbackground=C["bg3"])
                tree.tag_configure("par",   background=C["bg3"], foreground=C["t1"])
                tree.tag_configure("impar", background=C["bg4"], foreground=C["t1"])
                def _repintar_osc(tv):
                    def _walk(items):
                        for item in items:
                            tags = list(tv.item(item, "tags"))
                            if not tags: tags = ["par"]
                            tv.item(item, tags=("impar",) if "impar" in tags else ("par",))
                            _walk(tv.get_children(item))
                    _walk(tv.get_children())
                _repintar_osc(tree)
                tree.selection_remove(tree.selection())
            except Exception:
                pass

        # 4. Limpiar recursivamente con colores oscuros
        def limpiar_osc(w):
            for hijo in w.winfo_children():
                clase = hijo.winfo_class()
                if clase in ("Frame","LabelFrame","TLabelframe","TFrame"):
                    try: hijo.configure(bg=C["bg1"])
                    except: pass
                elif clase in ("Label","TLabel"):
                    try: hijo.configure(bg=C["bg1"], fg=C["t2"])
                    except:
                        try: hijo.configure(bg=C["bg1"])
                        except: pass
                elif clase == "Canvas":
                    try: hijo.configure(bg=C["bg1"], highlightthickness=0)
                    except: pass
                elif clase == "Text":
                    try: hijo.configure(bg=C["bg1"], fg=C["t1"])
                    except: pass
                if hijo.winfo_children() and clase != "Treeview":
                    limpiar_osc(hijo)
        limpiar_osc(self)

        # 6. Menú
        for menu in (self._menubar, self._menu_archivo, self._menu_analizar):
            try: menu.configure(bg=C["bg2"], fg=C["t1"], activebackground=C["red"], activeforeground="#fff")
            except: pass
        try: self._menu_tema.configure(bg=C["bg3"], fg=C["t2"], activebackground=C["bg4"], activeforeground=C["cyan"])
        except: pass

        # 7. Barra de pestañas
        self._tab_bar.configure(bg=C["bg2"])
        for frm in self._tab_bar.winfo_children():
            try: frm.configure(bg=C["bg2"])
            except: pass
        for n, btn in self._tab_btns.items():
            is_active = (n == self._active_tab)
            btn.configure(
                bg=C["bg3"] if is_active else C["bg2"],
                fg=C["cyan"] if is_active else C["t3"])

        # 8. Footer
        self._footer.configure(bg=C["bg2"])
        self._btn_clr.configure(bg=C["bg3"], fg=C["t2"], highlightbackground=C["bd"])
        self._btn_ex.configure(bg=C["bg3"],  fg=C["amber"], highlightbackground=C["bd"])
        self._btn_rep.configure(bg=C["bg3"], fg=C["green"], highlightbackground=C["bd"])
        self._lbl_ft_tok.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_ft_sym.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_ft_err.configure(bg=C["bg2"], fg=C["t3"])

        # 9. Header
        self._lbl_status.configure(bg=C["bg2"], fg=C["t2"])
        self._dot.configure(bg=C["bg2"])
        self._lbl_cursor.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_tok_count.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_tok_hdr.configure(bg=C["bg2"],  fg=C["t3"])
        self._lbl_tree_hdr.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_tac_hdr.configure(bg=C["bg2"],  fg=C["t3"])
        self._lbl_tac_metric.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_err_hdr.configure(bg=C["bg2"],  fg=C["t3"])
        self._lbl_sym_count.configure(bg=C["bg2"], fg=C["t3"])
        self._lbl_editor_info.configure(bg=C["bg2"], fg=C["t3"])

        # Sub-botones TAC
        cur = self._tac_subview.get()
        for k, btn in self._tac_sub_btns.items():
            btn.configure(
                bg=C["bg3"] if k == cur else C["bg2"],
                fg=C["cyan"] if k == cur else C["t2"],
                highlightbackground=C["cyan"] if k == cur else C["bd"])

        # 10. Sub-vista "Que es?" — restaurar colores oscuros
        info_sf = self._tac_subframes.get("info")
        if info_sf:
            for w in info_sf.winfo_children():
                if w.winfo_class() == "Text":
                    w.configure(bg=C["bg1"], fg=C["t1"])
                    w.tag_configure("h1",   foreground=C["cyan"])
                    w.tag_configure("h2",   foreground=C["amber"])
                    w.tag_configure("code", foreground=C["green"])
                    w.tag_configure("note", foreground=C["t2"])

        # Sub-vistas comparación de texto
        self._tac_cmp_orig.configure(bg=C["bg1"], fg=C["t1"])
        self._tac_cmp_opt.configure(bg=C["bg1"],  fg=C["t1"])

        # 11. Consola de errores: restaurar tags oscuros
        self._console.configure(bg=C["bg1"], fg=C["t2"])
        self._console.tag_config("ok",    foreground=C["green"])
        self._console.tag_config("error", foreground=C["red"])
        self._console.tag_config("warn",  foreground=C["amber"])
        self._console.tag_config("info",  foreground=C["cyan"])

        if hasattr(self, '_last_tokens') and self._last_tokens is not None:
            self._build_semantic_panel(self._last_tokens,
                                       self._last_tabla.todos_los_simbolos() if self._last_tabla else [],
                                       self._last_errores or [])

        self.update_idletasks()
        self._on_key_editor()
        self._log("info", "Tema cambiado a Modo Oscuro")

if __name__ == "__main__":
    app = MiniIDE()
    app.mainloop()
