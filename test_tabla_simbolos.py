from tabla_simbolos import TablaSimbolos


def test_agregar_y_obtener():
    t = TablaSimbolos()
    t.agregar('x', 'ENTERO', 1, 1, 10)
    assert t.existe('x')
    s = t.obtener('x')
    assert s is not None
    assert s.nombre == 'x'
    assert s.tipo == 'ENTERO'
    assert s.valor == 10


def test_actualizar():
    t = TablaSimbolos()
    t.agregar('y', 'ENTERO', 2, 3, 5)
    t.actualizar('y', valor=20, tipo='DECIMAL')
    s = t.obtener('y')
    assert s.valor == 20
    assert s.tipo == 'DECIMAL'


def test_eliminar():
    t = TablaSimbolos()
    t.agregar('z', 'CADENA', 3, 1, 'hola')
    t.eliminar('z')
    assert not t.existe('z')


if __name__ == '__main__':
    test_agregar_y_obtener()
    test_actualizar()
    test_eliminar()
    print('Todos los tests pasaron')
