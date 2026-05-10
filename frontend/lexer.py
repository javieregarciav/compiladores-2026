"""
Lexer PLY (fase 1) adaptado al pipeline de la fase 2.

Mantiene la API que espera el pipeline: una clase `Lexer` con metodo
`analizar(codigo) -> (tokens_info, tabla, errores)` donde:
  - tokens_info: lista de dicts {tipo, valor, linea, columna, longitud}
  - tabla: TablaSimbolos con los simbolos descubiertos por declaracion
  - errores: lista de strings con errores lexicos y semanticos basicos
"""

import ply.lex as lex
from .tabla_simbolos import TablaSimbolos
from . import errores as _errores_mod

# Palabras reservadas en espanol
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

tokens = [
    'MAS', 'MENOS', 'MULTIPLICACION', 'DIVIDIR', 'MODULO',
    'IGUAL', 'DIFERENTE',
    'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL',
    'AND', 'OR', 'NOT',
    'ASIGNAR',
    'LPAREN', 'RPAREN', 'LLAVE_IZQ', 'LLAVE_DER',
    'PUNTO_COMA', 'COMA',
    'NUMERO_ENTERO', 'NUMERO_DECIMAL', 'CADENA_LITERAL',
    'IDENTIFICADOR',
] + list(reservadas.values())

# Tokens simples
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

t_ignore = ' \t'


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
    _errores_mod.agregar_lexico(
        f"Caracter ilegal '{t.value[0]}'",
        t.lineno, columna, valor=t.value[0],
    )
    t.lexer.skip(1)


def encontrar_columna(texto, token):
    ultima_linea = texto.rfind('\n', 0, token.lexpos)
    if ultima_linea < 0:
        ultima_linea = -1
    return token.lexpos - ultima_linea


class _NullLogger:
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def info(self, *a, **k): pass
    def debug(self, *a, **k): pass
    def critical(self, *a, **k): pass


_lexer_global = lex.lex(errorlog=_NullLogger())


# Tipos de dato (en token) que disparan registro en tabla de simbolos
_TIPOS_DATO_TOKEN = frozenset({"ENTERO", "DECIMAL", "CADENA_TIPO", "BOOLEANO"})
# Nombre user-friendly del tipo (para la tabla de simbolos)
_TIPO_AMIGABLE = {
    "ENTERO": "entero",
    "DECIMAL": "decimal",
    "CADENA_TIPO": "cadena",
    "BOOLEANO": "booleano",
}


class Lexer:
    """API que espera el pipeline (main.py, bridge.py)."""

    def analizar(self, codigo: str):
        # Limpiar estado global de errores (modulo errores)
        _errores_mod.limpiar()
        _lexer_global.lineno = 1
        _lexer_global.input(codigo)
        # Guardar codigo para que el parser PLY pueda re-tokenizar
        from . import parser as _parser_mod
        _parser_mod._set_codigo(codigo)

        tabla = TablaSimbolos()
        tokens_info = []

        ultimo_tipo = None
        proximo_es_id = False

        while True:
            t = _lexer_global.token()
            if not t:
                break
            columna = encontrar_columna(codigo, t)
            valor_str = str(t.value)
            longitud = len(valor_str) if t.type != 'CADENA_LITERAL' else len(valor_str) + 2
            tokens_info.append({
                'tipo': t.type,
                'valor': valor_str,
                'linea': t.lineno,
                'columna': columna,
                'longitud': longitud,
            })
            # State machine para declaraciones: tipo seguido de identificador
            if t.type in _TIPOS_DATO_TOKEN:
                ultimo_tipo = _TIPO_AMIGABLE[t.type]
                proximo_es_id = True
            elif t.type == 'IDENTIFICADOR' and proximo_es_id and ultimo_tipo:
                tabla.insertar(t.value, ultimo_tipo, t.lineno)
                proximo_es_id = False
                ultimo_tipo = None
            else:
                proximo_es_id = False

        # Devolver lista combinada de errores (lexicos + semanticos de tabla)
        errores = _errores_mod.todos()
        return tokens_info, tabla, errores


# Helpers exportados para el parser
def get_ply_lexer():
    return _lexer_global


def limpiar_errores_lexicos():
    lista_errores.clear()
