"""
tabla_simbolos.py
-----------------
Implementación de la Tabla de Símbolos para el mini-compilador.
Almacena identificadores con su tipo, valor y línea de declaración.
"""


class Simbolo:
    """Representa una entrada individual en la tabla de símbolos."""

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
    """
    Tabla de símbolos con soporte para ámbitos (scopes) anidados.
    Permite insertar, buscar y eliminar símbolos, además de
    gestionar múltiples niveles de alcance (global / local).
    """

    def __init__(self):
        # Pila de ámbitos; cada ámbito es un dict nombre -> Simbolo
        self._ambitos: list[dict[str, Simbolo]] = [{}]
        self._errores: list[str] = []

    # ------------------------------------------------------------------
    # Gestión de ámbitos
    # ------------------------------------------------------------------

    def entrar_ambito(self):
        """Crea un nuevo ámbito (ej: al entrar a un bloque { })."""
        self._ambitos.append({})

    def salir_ambito(self):
        """Destruye el ámbito actual al salir de un bloque."""
        if len(self._ambitos) > 1:
            self._ambitos.pop()

    @property
    def nivel_actual(self) -> int:
        return len(self._ambitos) - 1

    # ------------------------------------------------------------------
    # Operaciones CRUD
    # ------------------------------------------------------------------

    def insertar(self, nombre: str, tipo: str, linea: int, valor=None) -> bool:
        """
        Inserta un símbolo en el ámbito actual.
        Retorna False si ya existe en este mismo ámbito (duplicado).
        """
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
        """
        Busca un símbolo recorriendo los ámbitos de interno a externo.
        Retorna el Simbolo encontrado o None.
        """
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def actualizar_valor(self, nombre: str, valor) -> bool:
        """Actualiza el valor de un símbolo ya declarado."""
        simbolo = self.buscar(nombre)
        if simbolo:
            simbolo.valor = valor
            return True
        return False

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def todos_los_simbolos(self) -> list[Simbolo]:
        """Devuelve todos los símbolos de todos los ámbitos (para la GUI)."""
        resultado = []
        for ambito in self._ambitos:
            resultado.extend(ambito.values())
        return resultado

    def obtener_errores(self) -> list[str]:
        return list(self._errores)

    def limpiar(self):
        """Reinicia la tabla por completo (nueva sesión de análisis)."""
        self._ambitos = [{}]
        self._errores = []

    # ------------------------------------------------------------------
    # Representación
    # ------------------------------------------------------------------

    def __str__(self):
        lineas = [f"{'NOMBRE':<20} {'TIPO':<10} {'LÍNEA':<8} {'VALOR':<15}"]
        lineas.append("-" * 55)
        for s in self.todos_los_simbolos():
            lineas.append(
                f"{s.nombre:<20} {s.tipo:<10} {s.linea:<8} {str(s.valor):<15}"
            )
        return "\n".join(lineas)
