# diccionario de palabras reservadas
reservadas = {
    'programa': 'PROGRAMA',
    'entero': 'ENTERO',
    'decimal': 'DECIMAL',
    'cadena': 'CADENA_TIPO',
    'booleano': 'BOOLEANO',
    'si': 'SI',
    'sino': 'SINO',
    'mientras': 'MIENTRAS',
    'hacer_mientras': 'HACER_MIENTRAS',
    'para': 'PARA',
    'funcion': 'FUNCION',
    'procedimiento': 'PROCEDIMIENTO',
    'retornar': 'RETORNAR',
    'verdadero': 'VERDADERO',
    'falso': 'FALSO',
    'imprimir': 'IMPRIMIR',
    'leer': 'LEER',
}

# lista de tokens
tokens = [
    'MAS',
    'MENOS',
    'MULTIPLICACION',
    'DIVIDIR',
    'MODULO',
    'IGUAL',
    'DIFERENTE',
    'MENOR',
    'MAYOR',
    'MENOR_IGUAL',
    'MAYOR_IGUAL',
    'AND',
    'OR',
    'NOT',
    'ASIGNAR',
    'LPAREN',
    'RPAREN',
    'LLAVE_IZQ',
    'LLAVE_DER',
    'PUNTO_COMA',
    'COMA',
    'NUMERO_ENTERO',
    'NUMERO_DECIMAL',
    'CADENA_LITERAL',
    'IDENTIFICADOR',
] + list(reservadas.values())

# Tokens simples (regex directa)
t_MAS = r'\+'
t_MENOS = r'-'
t_MULTIPLICACION = r'\*'
t_DIVIDIR = r'/'
t_MODULO = r'%'

t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MENOR_IGUAL = r'<='
t_MAYOR_IGUAL = r'>='
t_MENOR = r'<'
t_MAYOR = r'>'

t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

t_ASIGNAR = r'='

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_PUNTO_COMA = r';'
t_COMA = r','

# Ignorar espacios y tabs
t_ignore = ' \t'

# lista para acumular errores léxicos
lista_errores = []


# --- tokens complejos como funciones (orden importante: decimal antes que entero) ---
def t_NUMERO_DECIMAL(t):
    r'\d+\.\d+'
    try:
        t.value = float(t.value)
    except ValueError:
        t.value = 0.0
    return t


def t_NUMERO_ENTERO(t):
    r'\d+'
    try:
        t.value = int(t.value)
    except ValueError:
        t.value = 0
    return t


def t_CADENA_LITERAL(t):
    r'"([^\\"]|\\.)*"'
    # eliminar comillas y procesar escapes básicos
    raw = t.value[1:-1]
    try:
        t.value = bytes(raw, 'utf-8').decode('unicode_escape')
    except Exception:
        t.value = raw
    return t


def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reservadas.get(t.value, 'IDENTIFICADOR')
    return t


def t_COMENTARIO_LINEA(t):
    r'//.*'
    pass


def t_COMENTARIO_BLOQUE(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    columna = encontrar_columna(t.lexer.lexdata, t)
    lista_errores.append({
        'tipo': 'Lexico',
        'descripcion': f"Caracter ilegal '{t.value[0]}'",
        'linea': t.lineno,
        'columna': columna,
    })
    t.lexer.skip(1)


def encontrar_columna(texto, token):
    # devuelve número de columna (1-indexed)
    ultima_linea = texto.rfind('\n', 0, token.lexpos)
    if ultima_linea < 0:
        ultima_linea = -1
    return token.lexpos - ultima_linea


# Construir el lexer
import ply.lex as lex

lexer = lex.lex()


def tokenize(text):
    """Tokeniza el texto dado y devuelve (tokens, errores).

    tokens: lista de objetos tipo ply.lex.LexToken
    errores: lista con diccionarios de errores léxicos
    """
    # limpiar estado previo
    lista_errores.clear()
    lexer.lineno = 1
    lexer.input(text)
    toks = []
    for t in lexer:
        toks.append(t)
    return toks, list(lista_errores)