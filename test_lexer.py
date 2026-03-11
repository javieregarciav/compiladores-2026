from lexer import tokenize


def run_sample():
    data = 'programa ejemplo { entero x = 10; imprimir "hola\\n"; /* comentario */ }'
    tokens, errores = tokenize(data)
    print('Tokens:')
    for tok in tokens:
        print((tok.type, tok.value, tok.lineno, tok.lexpos))
    print('\nErrores léxicos:', errores)


if __name__ == '__main__':
    run_sample()
