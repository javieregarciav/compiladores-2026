
class Simbolo:

    def __init__(self, nombre: str, tipo: str, linea: int, valor=None):
        self.nombre = nombre
        self.tipo = tipo
        self.linea = linea
        self.valor = valor

    def __repr__(self):
        return (
            f"Simbolo(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"linea={self.linea}, valor={self.valor!r})"
        )

class TablaSimbolos:

    def __init__(self):

        self._ambitos: list[dict[str, Simbolo]] = [{}]
        self._errores: list[str] = []

    def entrar_ambito(self):
        self._ambitos.append({})

    def salir_ambito(self):
        if len(self._ambitos) > 1:
            self._ambitos.pop()

    @property
    def nivel_actual(self) -> int:
        return len(self._ambitos) - 1

    def insertar(self, nombre: str, tipo: str, linea: int, valor=None) -> bool:
        ambito_actual = self._ambitos[-1]
        if nombre in ambito_actual:
            self._errores.append(
                f"[Línea {linea}] Error semántico: '{nombre}' ya fue declarado "
                f"en este ámbito (línea {ambito_actual[nombre].linea})."
            )
            return False
        ambito_actual[nombre] = Simbolo(nombre, tipo, linea, valor)
        return True

    def buscar(self, nombre: str) -> Simbolo | None:
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def actualizar_valor(self, nombre: str, valor) -> bool:
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.valor = valor
            return True
        return False

    def todos_los_simbolos(self) -> list[Simbolo]:
        resultado = []
        for ambito in self._ambitos:
            resultado.extend(ambito.values())
        return resultado

    def obtener_errores(self) -> list[str]:
        return list(self._errores)

    def limpiar(self):
        self._ambitos = [{}]
        self._errores = []

    def __str__(self):
        lineas = [f"{'NOMBRE':<20} {'TIPO':<10} {'LÍNEA':<8} {'VALOR':<15}"]
        lineas.append("-" * 55)
        for s in self.todos_los_simbolos():
            lineas.append(
                f"{s.nombre:<20} {s.tipo:<10} {s.linea:<8} {str(s.valor):<15}"
            )
        return "\n".join(lineas)
