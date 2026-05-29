from __future__ import annotations

"""
Tabla de simbolos (fase 1) con la API que espera el pipeline:
  - insertar(nombre, tipo, linea, valor=None) -> bool
  - buscar(nombre) -> Simbolo o None
  - todos_los_simbolos() -> list[Simbolo]
  - obtener_errores() -> list[dict]  (errores como dicts estructurados)
  - entrar_ambito() / salir_ambito()
"""

from . import errores as _err_mod


class Simbolo:
    def __init__(
        self,
        nombre: str,
        tipo: str,
        linea: int,
        valor=None,
        kind: str = "variable",
        elem_type: str | None = None,
        size: int | None = None,
        params: list | None = None,
        return_type: str | None = None,
        scope: int = 0,
    ):
        self.nombre = nombre
        self.tipo = tipo
        self.linea = linea
        self.valor = valor
        self.kind = kind
        self.elem_type = elem_type
        self.size = size
        self.params = params or []
        self.return_type = return_type
        self.scope = scope

    def __repr__(self):
        return (
            f"Simbolo(nombre='{self.nombre}', tipo='{self.tipo}', "
            f"linea={self.linea}, valor={self.valor!r}, kind='{self.kind}')"
        )


class TablaSimbolos:

    def __init__(self):
        self._ambitos: list[dict[str, Simbolo]] = [{}]
        self._historico: list[Simbolo] = []
        self._errores: list = []

    def entrar_ambito(self):
        self._ambitos.append({})

    def salir_ambito(self):
        if len(self._ambitos) > 1:
            self._ambitos.pop()

    @property
    def nivel_actual(self) -> int:
        return len(self._ambitos) - 1

    def insertar(
        self,
        nombre,
        tipo,
        linea,
        valor=None,
        columna=0,
        kind="variable",
        elem_type=None,
        size=None,
        params=None,
        return_type=None,
    ):
        ambito = self._ambitos[-1]
        if nombre in ambito:
            _err_mod.agregar_semantico(
                f"Identificador '{nombre}' ya fue declarado en este ambito (linea {ambito[nombre].linea})",
                linea, columna, valor=nombre,
            )
            return False
        sim = Simbolo(
            nombre,
            tipo,
            linea,
            valor,
            kind=kind,
            elem_type=elem_type,
            size=size,
            params=params,
            return_type=return_type,
            scope=self.nivel_actual,
        )
        ambito[nombre] = sim
        self._historico.append(sim)
        return True

    def buscar(self, nombre):
        for ambito in reversed(self._ambitos):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def actualizar_valor(self, nombre, valor):
        s = self.buscar(nombre)
        if s:
            s.valor = valor
            return True
        return False

    def todos_los_simbolos(self):
        # Si check_semantic ya corrio, usamos el historico (sobrevive el
        # cierre de ambitos). Si nadie inserto via AST, caemos al snapshot
        # de los ambitos actuales (compat con consumidores antiguos).
        if self._historico:
            return list(self._historico)
        resultado = []
        for ambito in self._ambitos:
            resultado.extend(ambito.values())
        return resultado

    def obtener_errores(self):
        # Compat: ahora los errores semanticos viven en el modulo errores
        return []

    def limpiar(self):
        self._ambitos = [{}]
        self._historico = []
        self._errores = []

    def __str__(self):
        lineas = [f"{'NOMBRE':<20} {'TIPO':<10} {'LINEA':<8} {'VALOR':<15}"]
        lineas.append("-" * 55)
        for s in self.todos_los_simbolos():
            lineas.append(
                f"{s.nombre:<20} {s.tipo:<10} {s.linea:<8} {str(s.valor):<15}"
            )
        return "\n".join(lineas)
