import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from runtime import ejecutar_codigo


def analizar(codigo):
    lexer = Lexer()
    tokens, tabla, errores = lexer.analizar(codigo)
    ast = build_tree(tokens, errores)
    check_semantic(ast, tabla, errores)
    quads = [] if errores else GeneradorTAC().generar(ast)
    return tokens, tabla, errores, quads


class TestFase3(unittest.TestCase):
    def test_arreglos_end_to_end(self):
        codigo = """
programa {
    arreglo entero notas[3];
    notas[0] = 90;
    entero x = notas[0];
    imprimir(x);
}
"""
        _, tabla, errores, quads = analizar(codigo)
        self.assertEqual(errores, [])
        notas = tabla.buscar("notas")
        self.assertIsNotNone(notas)
        self.assertEqual(notas.kind, "array")
        self.assertEqual(notas.elem_type, "entero")
        self.assertEqual(notas.size, 3)
        self.assertIn("array_decl", [q.op for q in quads])
        self.assertIn("astore", [q.op for q in quads])
        self.assertIn("aload", [q.op for q in quads])

    def test_funciones_end_to_end(self):
        codigo = """
programa {
    funcion decimal promedio(entero a, entero b) {
        retornar (a + b) / 2;
    }
    decimal p = promedio(90, 80);
    imprimir(p);
}
"""
        _, tabla, errores, quads = analizar(codigo)
        self.assertEqual(errores, [])
        promedio = tabla.buscar("promedio")
        self.assertIsNotNone(promedio)
        self.assertEqual(promedio.kind, "function")
        self.assertEqual(promedio.return_type, "decimal")
        ops = [q.op for q in quads]
        for op in ("label_func", "enter_func", "return", "param", "call", "exit_func"):
            self.assertIn(op, ops)

    def test_programa_final_compila(self):
        ruta = os.path.join(os.path.dirname(__file__), "programa_final.ext")
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
        _, tabla, errores, quads = analizar(codigo)
        self.assertEqual(errores, [])
        self.assertGreaterEqual(len(tabla.todos_los_simbolos()), 30)
        self.assertGreater(len(quads), 100)

    def test_programa_final_ejecuta_menu(self):
        ruta = os.path.join(os.path.dirname(__file__), "programa_final.ext")
        with open(ruta, "r", encoding="utf-8") as f:
            codigo = f.read()
        entradas = [
            "1", "Ana Garcia", "2026001", "7", "Compiladores", "2026",
            "Sabado", "Proyecto1", "95", "88", "91",
            "2", "3", "4", "0", "5", "6",
        ]
        res, salida = ejecutar_codigo(codigo, entradas)
        self.assertEqual(res.errores, [])
        texto = "\n".join(salida)
        self.assertIn("===== SISTEMA DE REGISTRO DE NOTAS =====", texto)
        self.assertIn("Ana Garcia", texto)
        self.assertIn("Promedio general:", texto)
        self.assertIn("Aprobados:", texto)
        self.assertIn("Estudiantes con mejores notas:", texto)


if __name__ == "__main__":
    unittest.main()
