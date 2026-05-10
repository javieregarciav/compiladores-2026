
import re
from .tabla_simbolos import TablaSimbolos

RESERVED = {
    "int":     "INT",
    "float":   "FLOAT",
    "string":  "STRING",
    "boolean": "BOOLEAN",
    "if":      "IF",
    "else":    "ELSE",
    "while":   "WHILE",
    "for":     "FOR",
    "return":  "RETURN",
    "true":    "TRUE",
    "false":   "FALSE",
    "print":   "PRINT",
    "input":   "INPUT",
    "and":     "AND",
    "or":      "OR",
    "not":     "NOT",
    "null":    "NULL",
}

RESERVED_INV = {v: k for k, v in RESERVED.items()}

TOKENS = (
    "ENTERO", "DECIMAL", "CADENA", "ID",
    "MAS", "MENOS", "MULT", "DIV", "MOD",
    "IGUAL", "DIFERENTE",
    "MENOR_IGUAL", "MAYOR_IGUAL", "MENOR", "MAYOR",
    "Y_LOGICO", "O_LOGICO", "NO_LOGICO",
    "ASIGNACION",
    "PUNTO_COMA", "COMA",
    "PAREN_IZQ", "PAREN_DER",
    "LLAVE_IZQ", "LLAVE_DER",
) + tuple(RESERVED.values())

SPEC = [
    ("COMENTARIO",  r"//[^\n]*"),
    ("DECIMAL",     r"\d+\.\d+",   float),
    ("ENTERO",      r"\d+",        int),
    ("CADENA",      r'"(?:[^"\\]|\\.)*"'),
    ("ID",          r"[a-zA-Z_][a-zA-Z_0-9]*"),

    ("IGUAL",       r"=="),
    ("DIFERENTE",   r"!="),
    ("MENOR_IGUAL", r"<="),
    ("MAYOR_IGUAL", r">="),
    ("Y_LOGICO",    r"&&"),
    ("O_LOGICO",    r"\|\|"),

    ("MAS",         r"\+"),
    ("MENOS",       r"-"),
    ("MULT",        r"\*"),
    ("DIV",         r"/"),
    ("MOD",         r"%"),
    ("NO_LOGICO",   r"!"),
    ("MENOR",       r"<"),
    ("MAYOR",       r">"),
    ("ASIGNACION",  r"="),

    ("PUNTO_COMA",  r";"),
    ("COMA",        r","),
    ("PAREN_IZQ",   r"\("),
    ("PAREN_DER",   r"\)"),
    ("LLAVE_IZQ",   r"\{"),
    ("LLAVE_DER",   r"\}"),

    ("NUEVA_LINEA", r"\n"),
    ("ESPACIO",     r"[ \t\r]+"),
]

_PATRON = re.compile(
    "|".join("(?P<%s>%s)" % (n, p) for n, p, *_ in SPEC)
)
_CONV = {n: c for n, _, *c in SPEC if c}

_IGNORAR = frozenset({"NUEVA_LINEA", "ESPACIO", "COMENTARIO"})

class Lexer:

    _TIPOS_DATO = frozenset({"INT", "FLOAT", "STRING", "BOOLEAN"})

    def analizar(self, codigo: str):
        tokens_info = []
        errores = []
        tabla = TablaSimbolos()

        linea_actual = 1
        inicio_linea = 0
        ultimo_tipo = None
        proximo_es_id = False

        consumidas = bytearray(len(codigo))

        for m in _PATRON.finditer(codigo):
            tipo = m.lastgroup
            valor = m.group()
            pos = m.start()

            for i in range(m.start(), m.end()):
                consumidas[i] = 1

            if tipo == "NUEVA_LINEA":
                linea_actual += 1
                inicio_linea = m.end()
                continue

            if tipo in _IGNORAR:
                continue

            columna = pos - inicio_linea + 1

            if tipo == "ID":
                tipo = RESERVED.get(valor, "ID")

            if tipo == "CADENA":
                valor_real = (valor[1:-1]
                              .replace('\\"', '"')
                              .replace("\\n", "\n")
                              .replace("\\t", "\t")
                              .replace("\\\\", "\\"))
            elif tipo in _CONV:
                valor_real = _CONV[tipo][0](valor)
            else:
                valor_real = valor

            tokens_info.append({
                "tipo":     tipo,
                "valor":    str(valor_real),
                "linea":    linea_actual,
                "columna":  columna,
                "longitud": m.end() - m.start(),
            })

            if tipo == "CADENA":
                saltos = valor.count("\n")
                if saltos:
                    linea_actual += saltos
                    inicio_linea = m.start() + valor.rfind("\n") + 1

            if tipo in self._TIPOS_DATO:
                ultimo_tipo = RESERVED_INV.get(tipo, tipo.lower())
                proximo_es_id = True
            elif tipo == "ID" and proximo_es_id and ultimo_tipo:
                tabla.insertar(valor, ultimo_tipo, linea_actual)
                proximo_es_id = False
                ultimo_tipo = None
            else:
                proximo_es_id = False

        linea_err = 1
        inicio_err = 0
        for i, ch in enumerate(codigo):
            if ch == "\n":
                linea_err += 1
                inicio_err = i + 1
                continue
            if not consumidas[i] and ch not in (" ", "\t", "\r"):
                col_err = i - inicio_err + 1
                errores.append(
                    f"[Línea {linea_err}, Col {col_err}] "
                    f"Carácter ilegal: '{ch}'"
                )

        errores.extend(tabla.obtener_errores())
        return tokens_info, tabla, errores

if __name__ == "__main__":
    codigo = """\
int x = 10;
float y = 3.14;
string nombre = "Hola Mundo";
boolean activo = true;

// Bucle de ejemplo
while (x != 0) {
    x = x - 1;
}

if (x > 5) {
    print(nombre);
} else {
    print("fin");
}

int z = x + y * 2;
int z = 99;

int a = 5@;
"""
    lexer = Lexer()
    toks, tabla, errores = lexer.analizar(codigo)

    print("=== TOKENS ===")
    for t in toks:
        print(f"  [{t['linea']}:{t['columna']:>3}]  {t['tipo']:<15}  ->  {t['valor']}")

    print("\n=== TABLA DE SIMBOLOS ===")
    print(tabla)

    if errores:
        print("\n=== ERRORES ===")
        for e in errores:
            print(" ", e)
