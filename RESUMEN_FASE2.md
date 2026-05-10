# Fase 2 - Resumen general

## Qué venía de la fase 1

El proyecto en la fase 1 ya tenía un compilador funcional pero limitado a
las dos primeras etapas:

- **Análisis léxico** con PLY (`ply.lex`): tokens, palabras reservadas,
  detección de caracteres ilegales.
- **Análisis sintáctico** con PLY yacc (`ply.yacc`): gramática del lenguaje
  con precedencia, recuperación básica de errores.
- **Tabla de símbolos** sencilla (un solo ámbito).
- **Reportes HTML** mínimos para tokens, errores y tabla de símbolos.
- **CLI** que recibe un archivo y genera los reportes.

No tenía análisis semántico, ni código intermedio, ni optimización, ni UI
de escritorio o web.

---

## Qué se agregó en la fase 2

### 1. Reestructuración: frontend / backend

El código se reorganizó en dos carpetas con un contrato compartido en el
medio:

- **`frontend/`** — todo lo que depende del lenguaje fuente (lexer,
  parser, tabla de símbolos, análisis semántico, generador de TAC).
- **`intermedio.py`** — la frontera. Define la dataclass `Quad` que
  representa un cuádruplo de código de tres direcciones, más el formateador
  para mostrarlo.
- **`backend/`** — todo lo que depende de la máquina destino (en este caso,
  el optimizador).

La idea: si en el futuro cambia el lenguaje fuente, solo se rehace el
frontend; si cambia la máquina destino, solo el backend. El IR es el
único punto que ambos lados conocen.

### 2. Análisis semántico

Se agregó `check_semantic` en `frontend/parser.py`. Recorre el AST y detecta:

- Variables no declaradas (al usarlas, asignarles, leerlas).
- Variables duplicadas en el mismo ámbito.
- Tipos incompatibles en declaraciones y asignaciones.
- Uso de variables antes de su declaración (comparando líneas).
- Condiciones de `si`, `mientras`, `hacer_mientras` y `para` que no son
  booleanas.
- División y módulo por cero literal.
- Operaciones aritméticas, lógicas y comparaciones entre tipos incompatibles.
- Operadores unarios (`-`, `!`) aplicados a tipos erróneos.
- Promoción permitida: `decimal x = 5;` se acepta (widening entero → decimal).

Cada error reporta **línea y columna** y se acumula en un módulo central
de errores (`frontend/errores.py`) con tres categorías: léxicos,
sintácticos y semánticos.

### 3. Generador de Código de Tres Direcciones (TAC)

Nuevo módulo `frontend/generador_intermedio.py`. Toma el AST y emite
cuádruplos de la forma `(op, arg1, arg2, dest)`. Soporta:

- Asignaciones y expresiones binarias.
- Operadores unarios (`-x` se traduce como `0 - x` para que el
  optimizador pueda foldearlo).
- Estructuras de control: `si/sino`, `mientras`, `hacer_mientras`, `para`.
- I/O: `imprimir` (con múltiples argumentos) y `leer`.
- Operadores lógicos (`&&`, `||`, `!`).

Las variables temporales se llaman `$t1`, `$t2`, etc. Las etiquetas son
`$L1`, `$L2`, etc. El prefijo `$` no se permite en identificadores del
usuario, así que nunca chocan.

### 4. Optimizador

Nuevo módulo `backend/optimizador.py` con **seis pasadas** que se aplican
en orden y se repiten hasta que ninguna haga cambios (*punto fijo*):

1. **Constant Folding & Algebraic** — evalúa operaciones con dos
   constantes (`3 + 4` → `7`); aplica identidades (`x + 0` → `x`,
   `x * 1` → `x`, `x * 0` → `0`).
2. **Constant / Copy Propagation** — propaga valores conocidos a usos
   posteriores. Invalida el entorno en saltos y etiquetas.
3. **Branch Pruning** — `ifFalse verdadero goto L` se elimina (nunca
   salta); `ifFalse falso goto L` se convierte en `goto L`.
4. **Unreachable Code Elimination** — después de un `goto`, todo hasta
   el siguiente `label` queda inalcanzable y se borra.
5. **Dead-Code Elimination** — elimina cuádruplos que escriben en un
   temporal que nadie lee. No elimina variables del usuario.
6. **Jump Threading** — borra `goto L` seguido inmediatamente de `L:`;
   borra etiquetas sin referencias.

El optimizador devuelve también una **traza** con cada modificación:
iteración, pasada, cuádruplos antes/después, delta.

### 5. Reportes HTML

Nuevo módulo `reportes.py` con generadores HTML estructurados:

- **`reporte_errores_semanticos.html`** — el reporte clave de la fase.
  Tabla con línea, columna, identificador afectado y descripción de cada
  error semántico. Categorización automática (variable no declarada,
  tipo incompatible, división por cero, etc.).
- **`reporte_errores.html`** — todos los errores (léxicos, sintácticos,
  semánticos) combinados con tags coloreados.
- **`reporte_tokens.html`** — lista de tokens reconocidos.
- **`reporte_tabla_simbolos.html`** — variables declaradas.
- **`reporte_tac.html`** — código intermedio original.
- **`reporte_tac_optimizado.html`** — código intermedio después del
  optimizador.

Todos comparten un CSS moderno (gradientes, alternancia de filas, hover,
tags coloreados por tipo). El HTML escapa correctamente caracteres
especiales (XSS-safe).

### 6. UI de escritorio (Tkinter)

Nuevo archivo `main.py`: una clase `MiniIDE(tk.Tk)` con seis pestañas:

- **Editor** con coloreado de tokens en vivo y atajo F5 para analizar.
- **Tokens** con tipo, valor, línea y columna.
- **Árbol** (AST) renderizado en un canvas con nodos coloreados por tipo.
- **Semántico** con tabla de símbolos y diagnóstico.
- **Código Intermedio** con sub-tabs para TAC original, optimizado,
  comparación lado a lado e información de cada pasada.
- **Errores** con consola dedicada.

En la barra inferior:
- **Botón "ANALIZAR"** (F5).
- **Botón "EJEMPLOS"** con 7 programas precargados.
- **Botón "REPORTES HTML"** que genera los 6 reportes en una carpeta y
  abre automáticamente el reporte de errores semánticos en el navegador.

### 7. UI web (PHP + JavaScript)

- `analizar.php` actúa de endpoint: recibe el código, lo guarda en un
  archivo temporal y llama a `bridge.py` vía `exec()` para obtener el
  resultado en JSON.
- `index.php` muestra el editor y las pestañas en el navegador. Renderiza
  las tablas de tokens, símbolos, errores, TAC original, TAC optimizado,
  con métricas de reducción y traza del optimizador.

### 8. Pipeline CLI (`bridge.py`)

Mejorado con:
- Llamadas a `check_semantic` antes de generar TAC (si hay errores, no
  emite código intermedio).
- Salida JSON con campos extra: `errores_estructurados` (dicts en lugar
  de strings) y `reportes` (rutas a los HTMLs generados).
- Flag `--reportes <dir>` que genera los seis reportes en una carpeta de
  una sola corrida.

### 9. Suites de QA

Tres scripts de pruebas automáticas:

- **`qa_rubrica.py`** (42 casos) — un caso por cada item de la rúbrica de
  evaluación. Cubre los cinco criterios técnicos.
- **`qa_completo.py`** (90 casos) — pruebas exhaustivas organizadas en
  nueve bloques: léxico, sintáctico, semántico, TAC, optimización,
  reportes, pipeline, stress (programas grandes, anidaciones profundas),
  regresión.
- **`qa_test.py`** (7 casos) — corre los siete ejemplos precargados de
  `main.py` a través de `bridge.py` para validar el pipeline completo.

**Total: 139 casos automáticos, 100% PASS.**

### 10. Documentación

- **`DOCUMENTACION.md`** — manual técnico con instalación, uso, API,
  arquitectura, troubleshooting.
- **`guia_pruebas_fase2.tex`** / `.pdf` — guía de pruebas con casos
  concretos por criterio de la rúbrica.
- **`presentacion_fase2.tex`** / `.pdf` — guía técnica de 13 páginas
  para la presentación.
- **`GUION_PRESENTACION.md`** — guion paso a paso para presentar.

---

## Cambios al lenguaje

La fase 1 ya tenía la sintaxis en español con `programa { ... }` como
envoltorio. En la fase 2 se mantiene esa sintaxis. Lo que sí se extendió
internamente es:

- El AST ahora son **diccionarios** (no tuplas) para que `check_semantic`
  y `GeneradorTAC` puedan recorrerlo más fácilmente.
- Cada token, cada nodo, cada error trae **línea y columna**.
- Los errores se manejan en un módulo central que distingue las tres
  categorías y permite obtenerlas ordenadas por línea.

---

## Métricas

| Indicador | Valor |
|---|---|
| Líneas de código Python agregadas/modificadas | ~3500 |
| Módulos nuevos | 4 (errores, generador_intermedio, optimizador, reportes) |
| Pasadas de optimización | 6 |
| Tipos de errores semánticos detectados | 12 |
| Cuádruplos del IR distintos | 8 (asignación, binario, unario, label, goto, if_false, print, read) |
| Reportes HTML generados | 6 |
| Tests automáticos | 139 (100% PASS) |
| Ejemplos precargados en la UI | 7 |

---

## Estructura final del proyecto

```
compiladores-2026/
├── frontend/
│   ├── lexer.py                    PLY lex
│   ├── parser.py                   PLY yacc + check_semantic
│   ├── tabla_simbolos.py           tabla con ámbitos
│   ├── errores.py                  módulo central de errores
│   └── generador_intermedio.py     AST → TAC
│
├── intermedio.py                   Quad + formatear_tac (frontera)
│
├── backend/
│   └── optimizador.py              6 pasadas + punto fijo
│
├── reportes.py                     generadores HTML
├── bridge.py                       CLI / JSON
├── main.py                         UI Tkinter
├── index.php / analizar.php        UI web
│
├── qa_rubrica.py                   42 casos rúbrica
├── qa_completo.py                  90 casos exhaustivos
├── qa_test.py                      7 ejemplos vía bridge
│
├── DOCUMENTACION.md
├── GUION_PRESENTACION.md
├── presentacion_fase2.tex/.pdf
└── guia_pruebas_fase2.tex/.pdf
```

---

## Lo que esta fase deja listo para la siguiente

El proyecto ahora tiene un IR bien definido (`Quad`) que es el punto de
partida natural para una eventual fase 3 que genere código de máquina
real: el frontend no se tocaría, y el backend solo necesitaría una etapa
adicional de "traducción de TAC a ensamblador" después del optimizador.

La separación frontend / backend y el contrato `Quad` son la pieza más
importante de esta fase desde el punto de vista arquitectónico — todo
lo demás se construye sobre eso.
