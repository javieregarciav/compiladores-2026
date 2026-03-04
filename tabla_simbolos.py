"""Módulo simple de tabla de símbolos.

Clases:
  Simbolo: representa un símbolo con nombre, tipo, posición y valor opcional.
  TablaSimbolos: tabla que permite agregar, actualizar, eliminar y consultar símbolos.
"""

from typing import Any, Dict, List, Optional


class Simbolo:
    def __init__(self, nombre: str, tipo: str, linea: int, columna: int, valor: Any = None):
        self.nombre = nombre
        self.tipo = tipo
        self.linea = linea
        self.columna = columna
        self.valor = valor

    def __repr__(self) -> str:
        return f"Simbolo(nombre={self.nombre!r}, tipo={self.tipo!r}, linea={self.linea}, columna={self.columna}, valor={self.valor!r})"


class TablaSimbolos:
    """Tabla de símbolos sencilla (un único ámbito plano).

    Notas:
      - `agregar` por defecto no sobrescribe un símbolo existente.
      - `actualizar` lanza KeyError si el símbolo no existe.
    """

    def __init__(self) -> None:
        self.simbolos: Dict[str, Simbolo] = {}

    def agregar(self, nombre: str, tipo: str, linea: int, columna: int, valor: Any = None, *, sobrescribir: bool = False) -> None:
        """Agrega un símbolo. Si ya existe y `sobrescribir` es False, no hace nada.

        Args:
            nombre: nombre del símbolo.
            tipo: tipo del símbolo (ej. 'ENTERO').
            linea: línea donde se declara.
            columna: columna donde se declara.
            valor: valor opcional.
            sobrescribir: si True, reemplaza el símbolo existente.
        """
        if nombre in self.simbolos and not sobrescribir:
            return
        self.simbolos[nombre] = Simbolo(nombre, tipo, linea, columna, valor)

    def existe(self, nombre: str) -> bool:
        return nombre in self.simbolos

    def obtener(self, nombre: str) -> Optional[Simbolo]:
        return self.simbolos.get(nombre)

    def actualizar(self, nombre: str, *, tipo: Optional[str] = None, valor: Any = None, linea: Optional[int] = None, columna: Optional[int] = None) -> None:
        """Actualiza campos de un símbolo existente. Lanza KeyError si no existe."""
        if nombre not in self.simbolos:
            raise KeyError(f"El símbolo '{nombre}' no existe")
        s = self.simbolos[nombre]
        if tipo is not None:
            s.tipo = tipo
        if valor is not None:
            s.valor = valor
        if linea is not None:
            s.linea = linea
        if columna is not None:
            s.columna = columna

    def eliminar(self, nombre: str) -> None:
        """Elimina un símbolo; lanza KeyError si no existe."""
        if nombre not in self.simbolos:
            raise KeyError(f"El símbolo '{nombre}' no existe")
        del self.simbolos[nombre]

    def obtener_todos(self) -> List[Simbolo]:
        return list(self.simbolos.values())

    def nombres(self) -> List[str]:
        return list(self.simbolos.keys())

    def __repr__(self) -> str:
        return f"TablaSimbolos({self.simbolos!r})"