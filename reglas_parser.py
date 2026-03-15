import ply.yacc as yacc
from lexer import tokens, lista_errores, encontrar_columna

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVIDIR', 'MODULO'),
    ('right', 'NOT', 'UMENOS')
)

def p_programa(p):
    '''programa : PROGRAMA LLAVE_IZQ sentencias LLAVE_DER'''
    p[0] = ('programa', p[3])

def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | sentencia'''
    if len(p) == 3: p[0] = p[1] + [p[2]]
    else: p[0] = [p[1]]

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

def p_tipo(p):
    '''tipo : ENTERO
            | DECIMAL
            | CADENA_TIPO
            | BOOLEANO'''
    p[0] = p[1]

def p_declaracion(p):
    '''declaracion : tipo IDENTIFICADOR PUNTO_COMA
                   | tipo IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    if len(p) == 4: p[0] = ('declaracion', p[1], p[2], None)
    else: p[0] = ('declaracion', p[1], p[2], p[4])

def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNAR expresion PUNTO_COMA'''
    p[0] = ('asignacion', p[1], p[3])

def p_asignacion_para(p):
    '''asignacion_para : IDENTIFICADOR ASIGNAR expresion'''
    p[0] = ('asignacion_para', p[1], p[3])

def p_sentencia_si(p):
    '''sentencia_si : SI LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER
                    | SI LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER SINO LLAVE_IZQ sentencias LLAVE_DER'''
    if len(p) == 8: p[0] = ('si', p[3], p[6], None)
    else: p[0] = ('si', p[3], p[6], p[10])

def p_sentencia_mientras(p):
    '''sentencia_mientras : MIENTRAS LPAREN expresion RPAREN LLAVE_IZQ sentencias LLAVE_DER'''
    p[0] = ('mientras', p[3], p[6])

def p_sentencia_hacer_mientras(p):
    '''sentencia_hacer_mientras : HACER_MIENTRAS LLAVE_IZQ sentencias LLAVE_DER MIENTRAS LPAREN expresion RPAREN PUNTO_COMA'''
    p[0] = ('hacer_mientras', p[3], p[7])

def p_sentencia_para(p):
    '''sentencia_para : PARA LPAREN asignacion_para PUNTO_COMA expresion PUNTO_COMA asignacion_para RPAREN LLAVE_IZQ sentencias LLAVE_DER'''
    p[0] = ('para', p[3], p[5], p[7], p[10])
    

def p_sentencia_imprimir(p):
    '''sentencia_imprimir : IMPRIMIR LPAREN expresion RPAREN PUNTO_COMA'''
    p[0] = ('imprimir', p[3])

def p_sentencia_leer(p):
    '''sentencia_leer : LEER LPAREN IDENTIFICADOR RPAREN PUNTO_COMA'''
    p[0] = ('leer', p[3])

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
    p[0] = (p[2], p[1], p[3])

def p_expresion_not(p):
    '''expresion : NOT expresion'''
    p[0] = ('not', p[2])

def p_expresion_umenos(p):
    '''expresion : MENOS expresion %prec UMENOS'''
    p[0] = ('negativo', p[2])

def p_expresion_paren(p):
    '''expresion : LPAREN expresion RPAREN'''
    p[0] = p[2]

def p_expresion_literal(p):
    '''expresion : NUMERO_ENTERO
                 | NUMERO_DECIMAL
                 | CADENA_LITERAL
                 | VERDADERO
                 | FALSO
                 | IDENTIFICADOR'''
    p[0] = p[1]

def p_error(p):
    if p:
        columna = encontrar_columna(p.lexer.lexdata, p)
        lista_errores.append({
            'tipo': 'Sintactico',
            'descripcion': f"token inesperado: '{p.value}'",
            'linea': p.lineno,
            'columna': columna
        })
        while True:
            tok = parser.token()
            if not tok or tok.type == 'PUNTO_COMA':
                break
        parser.restart()
    else: 
        lista_errores.append({
            'tipo': 'Sintactico',
            'descripcion': f"final de archivo inesperado",
            'linea': 0,
            'columna': 0
        })

parser = yacc.yacc()