
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from frontend import Lexer, TablaSimbolos

def tipos_de(tokens_info: list[dict]) -> list[str]:
    return [t["tipo"] for t in tokens_info]

def valores_de(tokens_info: list[dict]) -> list:
    return [t["valor"] for t in tokens_info]

class TestTokensBasicos(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_entero(self):
        toks, _, _ = self.lexer.analizar("42")
        self.assertEqual(tipos_de(toks), ["ENTERO"])
        self.assertEqual(toks[0]["valor"], "42")

    def test_decimal(self):
        toks, _, _ = self.lexer.analizar("3.14")
        self.assertEqual(tipos_de(toks), ["DECIMAL"])

    def test_cadena(self):
        toks, _, _ = self.lexer.analizar('"hola mundo"')
        self.assertEqual(tipos_de(toks), ["CADENA"])
        self.assertEqual(toks[0]["valor"], "hola mundo")

    def test_identificador(self):
        toks, _, _ = self.lexer.analizar("miVariable")
        self.assertEqual(tipos_de(toks), ["ID"])

    def test_identificador_con_numeros(self):
        toks, _, _ = self.lexer.analizar("var123")
        self.assertEqual(tipos_de(toks), ["ID"])

    def test_operadores_aritmeticos(self):
        toks, _, _ = self.lexer.analizar("+ - * / %")
        self.assertEqual(tipos_de(toks), ["MAS", "MENOS", "MULT", "DIV", "MOD"])

    def test_operadores_relacionales(self):
        toks, _, _ = self.lexer.analizar("== != < > <= >=")
        self.assertEqual(
            tipos_de(toks),
            ["IGUAL", "DIFERENTE", "MENOR", "MAYOR", "MENOR_IGUAL", "MAYOR_IGUAL"],
        )

    def test_delimitadores(self):
        toks, _, _ = self.lexer.analizar("; , ( ) { }")
        self.assertEqual(
            tipos_de(toks),
            ["PUNTO_COMA", "COMA", "PAREN_IZQ", "PAREN_DER", "LLAVE_IZQ", "LLAVE_DER"],
        )

    def test_asignacion(self):
        toks, _, _ = self.lexer.analizar("=")
        self.assertEqual(tipos_de(toks), ["ASIGNACION"])

class TestPalabrasReservadas(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_tipos_dato(self):
        toks, _, _ = self.lexer.analizar("int float string boolean")
        self.assertEqual(tipos_de(toks), ["INT", "FLOAT", "STRING", "BOOLEAN"])

    def test_control_flujo(self):
        toks, _, _ = self.lexer.analizar("if else while for return")
        self.assertEqual(tipos_de(toks), ["IF", "ELSE", "WHILE", "FOR", "RETURN"])

    def test_booleanos(self):
        toks, _, _ = self.lexer.analizar("true false")
        self.assertEqual(tipos_de(toks), ["TRUE", "FALSE"])

    def test_funciones_builtin(self):
        toks, _, _ = self.lexer.analizar("print input")
        self.assertEqual(tipos_de(toks), ["PRINT", "INPUT"])

    def test_null(self):
        toks, _, _ = self.lexer.analizar("null")
        self.assertEqual(tipos_de(toks), ["NULL"])

class TestErroresLexicos(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_caracter_ilegal_arroba(self):
        _, _, errores = self.lexer.analizar("int x@y;")
        self.assertTrue(any("@" in e for e in errores))

    def test_multiples_errores(self):
        _, _, errores = self.lexer.analizar("@ # $")
        self.assertEqual(len(errores), 3)

    def test_codigo_valido_sin_errores(self):
        codigo = "int x = 10;"
        _, _, errores = self.lexer.analizar(codigo)
        self.assertEqual(errores, [])

    def test_caracter_ilegal_no_bloquea_resto(self):
        toks, _, _ = self.lexer.analizar("int @ x")
        tipos = tipos_de(toks)
        self.assertIn("INT", tipos)
        self.assertIn("ID", tipos)

class TestComentarios(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_comentario_linea(self):
        toks, _, _ = self.lexer.analizar("// esto es un comentario\nint x;")
        self.assertNotIn("COMENTARIO", tipos_de(toks))
        self.assertIn("INT", tipos_de(toks))

    def test_comentario_inline(self):
        toks, _, _ = self.lexer.analizar("int x = 5; // valor inicial")
        self.assertNotIn("COMENTARIO", tipos_de(toks))

class TestNumeroDeLinea(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_linea_uno(self):
        toks, _, _ = self.lexer.analizar("int x;")
        self.assertEqual(toks[0]["linea"], 1)

    def test_linea_multilinea(self):
        codigo = "int x;\nfloat y;"
        toks, _, _ = self.lexer.analizar(codigo)

        float_tok = next(t for t in toks if t["tipo"] == "FLOAT")
        self.assertEqual(float_tok["linea"], 2)

class TestTablaSimbolos(unittest.TestCase):

    def setUp(self):
        self.lexer = Lexer()

    def test_declaracion_int(self):
        _, tabla, _ = self.lexer.analizar("int contador = 0;")
        sim = tabla.buscar("contador")
        self.assertIsNotNone(sim)
        self.assertEqual(sim.tipo, "int")

    def test_multiples_declaraciones(self):
        codigo = "int x = 1;\nfloat y = 2.0;\nstring z = \"hola\";"
        _, tabla, _ = self.lexer.analizar(codigo)
        self.assertIsNotNone(tabla.buscar("x"))
        self.assertIsNotNone(tabla.buscar("y"))
        self.assertIsNotNone(tabla.buscar("z"))

    def test_tipo_correcto(self):
        _, tabla, _ = self.lexer.analizar("boolean activo = true;")
        sim = tabla.buscar("activo")
        self.assertEqual(sim.tipo, "boolean")

    def test_duplicado_genera_error(self):
        codigo = "int x = 1;\nint x = 2;"
        _, tabla, errores = self.lexer.analizar(codigo)
        self.assertTrue(any("x" in e for e in errores))

class TestTablaSimbolosDirecta(unittest.TestCase):

    def test_insertar_y_buscar(self):
        t = TablaSimbolos()
        t.insertar("n", "int", 1, 42)
        s = t.buscar("n")
        self.assertIsNotNone(s)
        self.assertEqual(s.valor, 42)

    def test_buscar_inexistente(self):
        t = TablaSimbolos()
        self.assertIsNone(t.buscar("nope"))

    def test_duplicado_mismo_ambito(self):
        t = TablaSimbolos()
        ok1 = t.insertar("x", "int", 1)
        ok2 = t.insertar("x", "float", 2)
        self.assertTrue(ok1)
        self.assertFalse(ok2)

    def test_ambitos_anidados(self):
        t = TablaSimbolos()
        t.insertar("global_var", "int", 1)
        t.entrar_ambito()
        t.insertar("local_var", "float", 5)
        self.assertIsNotNone(t.buscar("global_var"))
        self.assertIsNotNone(t.buscar("local_var"))
        t.salir_ambito()
        self.assertIsNone(t.buscar("local_var"))

    def test_actualizar_valor(self):
        t = TablaSimbolos()
        t.insertar("x", "int", 1, 0)
        t.actualizar_valor("x", 99)
        self.assertEqual(t.buscar("x").valor, 99)

    def test_limpiar(self):
        t = TablaSimbolos()
        t.insertar("a", "int", 1)
        t.limpiar()
        self.assertIsNone(t.buscar("a"))

class TestIntegracion(unittest.TestCase):

    CODIGO = """
int contador = 0;
float promedio = 0.0;
string mensaje = "inicio";
boolean listo = false;

// Bucle principal
while (contador < 10) {
    contador = contador + 1;
}

if (contador == 10) {
    print(mensaje);
}
"""

    def setUp(self):
        self.lexer = Lexer()
        self.toks, self.tabla, self.errores = self.lexer.analizar(self.CODIGO)

    def test_sin_errores(self):
        self.assertEqual(self.errores, [])

    def test_variables_en_tabla(self):
        for nombre in ("contador", "promedio", "mensaje", "listo"):
            with self.subTest(nombre=nombre):
                self.assertIsNotNone(self.tabla.buscar(nombre))

    def test_tipos_en_tabla(self):
        self.assertEqual(self.tabla.buscar("contador").tipo, "int")
        self.assertEqual(self.tabla.buscar("promedio").tipo, "float")
        self.assertEqual(self.tabla.buscar("mensaje").tipo, "string")
        self.assertEqual(self.tabla.buscar("listo").tipo, "boolean")

    def test_hay_tokens_suficientes(self):
        self.assertGreater(len(self.toks), 10)

    def test_palabras_reservadas_presentes(self):
        tipos = tipos_de(self.toks)
        for tipo in ("INT", "FLOAT", "STRING", "BOOLEAN", "WHILE", "IF", "PRINT"):
            with self.subTest(tipo=tipo):
                self.assertIn(tipo, tipos)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    sys.exit(0 if resultado.wasSuccessful() else 1)
