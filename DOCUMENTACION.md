# Compilador 2026 - Fase 2 - Documentación Técnica

## Tabla de contenidos

1. [Visión general](#vision-general)
2. [Instalación](#instalacion)
3. [Cómo usar el compilador](#como-usar)
4. [Arquitectura](#arquitectura)
5. [Sintaxis del lenguaje](#sintaxis)
6. [API de los módulos](#api)
7. [Pipeline de compilación](#pipeline)
8. [Análisis semántico](#semantico)
9. [Código de Tres Direcciones (TAC)](#tac)
10. [Optimización](#optimizacion)
11. [Reportes HTML](#reportes)
12. [Suites de QA](#qa)
13. [Troubleshooting](#troubleshooting)

---

<a id="vision-general"></a>
## 1. Visión general

Compilador para un lenguaje imperativo simple en **español** (`programa{...}`,
`entero`, `si`, `mientras`, `imprimir`, etc.). El frontend está implementado
con **PLY** (`ply.lex` + `ply.yacc`); el backend trabaja sobre un IR de
**código de tres direcciones (TAC)** con un optimizador de seis pasadas que
iteran hasta punto fijo.

### Capacidades

- **Análisis léxico** con PLY: detecta caracteres ilegales y reporta línea/columna.
- **Análisis sintáctico** con PLY yacc: parser LALR(1) con precedencia explícita.
- **Análisis semántico**: tipos, variables no declaradas/duplicadas, condiciones,
  división por cero, operadores incompatibles, uso antes de declaración.
- **Generación de TAC** desde el AST.
- **Optimización**: constant folding, propagation, branch pruning,
  unreachable code elimination, dead-code elimination, jump threading.
- **Reportes HTML** estructurados (especialmente el reporte de errores semánticos).
- **UI dual**: escritorio (Tkinter) y web (PHP+JS).

---

<a id="instalacion"></a>
## 2. Instalación

### Requisitos

- Python 3.10 o superior
- `ply >= 3.11` — `pip install ply`
- Tkinter (incluido con Python en Windows; en Linux: `sudo apt install python3-tk`)
- (Opcional) PHP para la UI web

### Setup

```bash
git clone <repo>
cd compiladores-2026
git checkout fase2-ply
pip install ply
```

---

<a id="como-usar"></a>
## 3. Cómo usar el compilador

### Modo 1: UI Tkinter

```bash
python main.py
```

- **Editor**: pestaña principal con coloreado de tokens en vivo.
- **F5**: ejecuta el análisis. Llena las pestañas Tokens, Árbol,
  Semántico, Código Intermedio y Errores.
- **Botón "EJEMPLOS ▾"** (footer): carga uno de 7 programas precargados.
- **Botón "REPORTES HTML"** (footer): genera los 6 archivos HTML en una
  carpeta a elección y abre el reporte de errores semánticos en el
  navegador.

### Modo 2: UI web

```bash
php -S localhost:8000
# abrir http://localhost:8000/index.php en el navegador
```

Pegar código en el editor, hacer click en *Analizar*. La página llama
internamente a `bridge.py` vía `exec()` y renderiza el JSON.

### Modo 3: CLI

```bash
# Análisis simple, JSON a stdout
python bridge.py mi_programa.programa

# Análisis + reportes HTML en carpeta
python bridge.py mi_programa.programa --reportes ./salida/
```

---

<a id="arquitectura"></a>
## 4. Arquitectura

```
compiladores-2026/
├── frontend/                       # Depende del lenguaje fuente
│   ├── __init__.py                 # Reexporta API pública
│   ├── lexer.py                    # PLY: tokens + tabla de símbolos
│   ├── tabla_simbolos.py           # Simbolo + TablaSimbolos con ámbitos
│   ├── errores.py                  # API agregar_lexico/sintactico/semantico
│   ├── parser.py                   # PLY yacc + check_semantic
│   └── generador_intermedio.py     # AST → TAC
│
├── intermedio.py                   # Contrato compartido (IR)
│                                   # Quad(op, arg1, arg2, dest), formatear_tac()
│
├── backend/                        # Depende de la máquina objetivo
│   ├── __init__.py
│   └── optimizador.py              # 6 pasadas hasta punto fijo
│
├── reportes.py                     # Generadores de HTML
├── bridge.py                       # Pipeline CLI → JSON
├── main.py                         # UI Tkinter
├── index.php / analizar.php        # UI web
└── qa_*.py                         # Suites de QA
```

### Separación frontend / backend

`intermedio.py` (con la dataclass `Quad`) es la **frontera**. No importa de
`frontend` ni de `backend`. Cualquier módulo que respete `Quad` puede leer
o escribir TAC.

---

<a id="sintaxis"></a>
## 5. Sintaxis del lenguaje

### Palabras reservadas

| Categoría | Palabras |
|---|---|
| Estructura | `programa` |
| Tipos | `entero`, `decimal`, `cadena`, `booleano` |
| Control | `si`, `sino`, `mientras`, `hacer_mientras`, `para` |
| I/O | `imprimir`, `leer` |
| Booleanos | `verdadero`, `falso` |
| Operadores | `&&`, `\|\|`, `!` |

### Tipos de dato

| Tipo | Ejemplo | Mapeo Python |
|---|---|---|
| `entero` | `42`, `-7` | `int` |
| `decimal` | `3.14`, `0.0` | `float` |
| `cadena` | `"hola"` | `str` |
| `booleano` | `verdadero`, `falso` | `bool` |

### Operadores

- **Aritméticos**: `+ - * / %`
- **Comparación**: `== != < > <= >=`
- **Lógicos**: `&&` (and), `||` (or), `!` (not)
- **Unarios**: `-` (negación), `!` (negación lógica)
- **Asignación**: `=`

### Estructura general

```
programa {
    // declaraciones
    entero x = 5;
    decimal pi = 3.14;
    cadena nombre = "Ana";
    booleano flag = verdadero;

    // condicionales
    si (x > 0) {
        imprimir(x);
    } sino {
        imprimir("negativo");
    }

    // bucles
    mientras (x > 0) { x = x - 1; }

    hacer_mientras { x = x + 1; } mientras (x < 10);

    para (entero i = 0; i < 5; i = i + 1) {
        imprimir(i);
    }

    // lectura
    leer(x);
}
```

### Comentarios

- `// comentario de línea`
- `/* comentario de bloque (multilínea) */`

---

<a id="api"></a>
## 6. API de los módulos

### `frontend.Lexer`

```python
from frontend import Lexer

lexer = Lexer()
tokens, tabla, errores = lexer.analizar(codigo)
```

- `tokens`: lista de dicts `{tipo, valor, linea, columna, longitud}`
- `tabla`: `TablaSimbolos` poblada con las declaraciones detectadas
- `errores`: lista de dicts `{tipo, descripcion, linea, columna, valor}`

### `frontend.build_tree` / `check_semantic`

```python
from frontend import build_tree, check_semantic

ast = build_tree(tokens, errores)        # parsea, agrega errores sintácticos
check_semantic(ast, tabla, errores)      # agrega errores semánticos
```

El AST es un dict tipo `{"type": "Program", "children": [...]}`. Los hijos
son nodos tipados (`Declaration`, `Assignment`, `If`, `While`, `For`,
`DoWhile`, `Print`, `Read`, `BinaryOp`, `UnaryOp`, `Group`, `Literal`,
`StringLit`, `BoolLit`, `Identifier`).

### `frontend.GeneradorTAC`

```python
from frontend import GeneradorTAC

quads = GeneradorTAC().generar(ast)      # list[Quad]
```

### `backend.optimizar`

```python
from backend import optimizar

quads_opt, traza = optimizar(quads, max_iter=12)
```

`traza` es una lista con la huella de cada pasada que produjo cambios:
`{iter, pasada, antes, despues, delta}`.

### `intermedio.formatear_tac`

```python
from intermedio import formatear_tac

filas = formatear_tac(quads)             # list[dict]
# Cada fila: {n, instruccion, op, arg1, arg2, dest, etiqueta}
```

### `reportes`

```python
import reportes

# Reporte específico de semánticos (criterio 2 de la rúbrica)
reportes.generar_html_errores_semanticos(sem_errores, "out/sem.html")

# Reportes individuales
reportes.generar_html_errores(errores, "out/err.html")
reportes.generar_html_tokens(tokens, "out/tok.html")
reportes.generar_html_tabla_simbolos(tabla, "out/sim.html")
reportes.generar_html_tac(filas, "out/tac.html", titulo="...")

# Genera todos los reportes de una vez
reportes.generar_reportes_completos(
    "carpeta_salida/",
    tokens=tokens, tabla=tabla, errores=errores,
    tac=filas_orig, tac_opt=filas_opt,
)
```

---

<a id="pipeline"></a>
## 7. Pipeline de compilación

```
código fuente (.programa)
     │
     ▼
┌──────────────────┐
│   Lexer (PLY)    │  → tokens + tabla de símbolos + errores léxicos
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Parser (yacc)   │  → AST (dicts) + errores sintácticos
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  check_semantic  │  → errores semánticos (con línea/columna)
└──────────────────┘
     │
     ▼
┌──────────────────┐
│   GeneradorTAC   │  → list[Quad]
└──────────────────┘
     │
     ▼
┌──────────────────┐
│   optimizar()    │  → list[Quad] optimizado + traza
└──────────────────┘
     │
     ▼
┌──────────────────┐
│ formatear_tac()  │  → tabla pretty para UI
└──────────────────┘
     │
     ▼
   UI (Tkinter / web / CLI JSON)
   Reportes HTML
```

---

<a id="semantico"></a>
## 8. Análisis semántico

### Errores que detecta `check_semantic`

| # | Tipo de error | Ejemplo |
|---|---|---|
| 1 | Variable no declarada | `imprimir(x);` con `x` sin declarar |
| 2 | Variable duplicada | `entero x = 1; entero x = 2;` |
| 3 | Asignación tipo incompatible | `entero x = "hola";` |
| 4 | Uso antes de declaración | `imprimir(x); entero x = 5;` |
| 5 | Condición no booleana en `si`/`mientras`/`para` | `si (x) { ... }` con `x` entero |
| 6 | División/módulo por cero literal | `int x = 10 / 0;` |
| 7 | Aritmética entre tipos incompatibles | `booleano + entero` |
| 8 | Comparación entre tipos incompatibles | `entero == cadena` |
| 9 | Operación lógica entre no booleanos | `entero && entero` |
| 10 | Operador unario inválido | `-booleano`, `!entero` |
| 11 | Lectura de variable no declarada | `leer(x);` con `x` sin declarar |
| 12 | Función no definida en `Call` | `f(x)` con `f` desconocida |

### Compatibilidad de tipos (widening)

```python
def _tipo_compatible(declarado, expresion):
    if declarado == expresion:                       return True
    if declarado == "decimal" and expresion == "entero":  return True  # widening
    return False
```

`decimal x = 5;` se acepta (entero → decimal). Lo inverso (`entero x = 3.14;`)
se rechaza.

### Formato de error semántico

```python
{
    "tipo":        "Semantico",
    "descripcion": "Variable 'x' no declarada",
    "linea":       5,
    "columna":     12,
    "valor":       "x"
}
```

---

<a id="tac"></a>
## 9. Código de Tres Direcciones

### Estructura del cuádruplo

```python
@dataclass
class Quad:
    op:   str                       # operación o palabra clave
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    dest: Optional[str] = None
```

### Instrucciones del IR

| Forma | `op` | Significado |
|---|---|---|
| `dest = arg1` | `=` | Asignación |
| `dest = arg1 op arg2` | `+ - * / %`, etc. | Operación binaria |
| `dest = !arg1` | `!` | Negación lógica |
| `L:` | `label` | Etiqueta (`dest = L`) |
| `goto L` | `goto` | Salto incondicional |
| `ifFalse arg1 goto L` | `if_false` | Salto condicional |
| `imprimir arg1` | `print` | Salida |
| `leer dest` | `read` | Entrada |

### Convención de nombres

- **Temporales**: `$t1`, `$t2`, … (prefijo `$` para no chocar con identificadores)
- **Etiquetas**: `$L1`, `$L2`, …

### Ejemplo completo

**Fuente:**
```
programa {
    entero a = 3;
    entero b = 4;
    entero c = (a + b) * 2;
    si (c > 10) { imprimir(c); } sino { imprimir("pequeno"); }
}
```

**TAC generado (12 cuádruplos):**
```
 1: a = 3
 2: b = 4
 3: $t1 = a + b
 4: $t2 = $t1 * 2
 5: c = $t2
 6: $t3 = c > 10
 7: ifFalse $t3 goto $L1
 8: imprimir c
 9: goto $L2
10: $L1:
11: imprimir "pequeno"
12: $L2:
```

**TAC optimizado (7 cuádruplos, reducción 41.7%):**
```
 1: a = 3
 2: b = 4
 3: c = 14
 4: imprimir 14
 5: goto $L2
 6: imprimir "pequeno"
 7: $L2:
```

---

<a id="optimizacion"></a>
## 10. Optimización

### Las 6 pasadas (en orden)

1. **Constant Folding & Algebraic**
   - Si ambos operandos son constantes → evalúa en compilación.
   - Identidades: `x+0`, `x*1` → `x`; `x*0` → `0`.

2. **Constant / Copy Propagation**
   - Mantiene entorno `env` con valores conocidos.
   - Reemplaza usos de variables por su valor literal cuando se conoce.
   - El entorno se invalida en `label` y saltos.

3. **Branch Pruning**
   - `ifFalse verdadero goto L` → elimina (nunca salta).
   - `ifFalse falso goto L` → `goto L` (siempre salta).

4. **Unreachable Code Elimination**
   - Después de un `goto` incondicional, elimina instrucciones hasta el
     siguiente `label`.

5. **Dead-Code Elimination**
   - Elimina cuádruplos cuyo destino es un temporal `$tN` no leído.
   - **No** elimina variables del usuario (pueden tener uso observable).

6. **Jump Threading**
   - `goto L` seguido inmediatamente de `L:` → elimina el `goto`.
   - Labels no referenciados se eliminan.

### Punto fijo

Las pasadas se aplican en orden y el ciclo se repite hasta que ninguna
haga cambios (máximo 12 iteraciones). Esto permite que las pasadas se
**alimenten entre sí**:

1. Folding pliega `$t1 = 3 + 4` → `$t1 = 7`.
2. Propagation reescribe `$t2 = $t1 * 2` → `$t2 = 7 * 2`.
3. Folding (siguiente iter) pliega `$t2 = 14`.
4. Propagation reescribe `c = $t2` → `c = 14`.
5. Dead-code elimina `$t1` y `$t2` muertos.

### Traza

Cada modificación se registra:
```python
{
    "iter":    1,
    "pasada":  "Constant Folding & Algebraic",
    "antes":   10,
    "despues": 8,
    "delta":   -2
}
```

---

<a id="reportes"></a>
## 11. Reportes HTML

### Archivos generados

`reportes.generar_reportes_completos(directorio, ...)` produce:

| Archivo | Contenido |
|---|---|
| `reporte_errores_semanticos.html` | **Solo errores semánticos** con línea/columna/categoría. **Es el reporte clave de la rúbrica (criterio 2).** |
| `reporte_errores.html` | Todos los errores (léxicos + sintácticos + semánticos) combinados |
| `reporte_tokens.html` | Tokens reconocidos con tipo, lexema, línea, columna |
| `reporte_tabla_simbolos.html` | Variables declaradas con nombre, tipo, valor, línea |
| `reporte_tac.html` | Código de tres direcciones original |
| `reporte_tac_optimizado.html` | TAC después del optimizador |

### Estructura del HTML

```
<header>           gradiente azul + título + timestamp
<.summary>         chips estadísticos por categoría
<table>
  <thead>          encabezado en color primario
  <tbody>          filas con alternancia + hover + tags coloreados
.tag.lex           rojo  (errores léxicos)
.tag.sint          ámbar (errores sintácticos)
.tag.sem           morado (errores semánticos)
.code              monospace para identificadores/lexemas
.empty             mensaje verde "sin errores"
```

### Genera desde código

```python
import reportes
from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from backend import optimizar
from intermedio import formatear_tac

codigo = open("mi_programa.programa").read()
lexer = Lexer()
tokens, tabla, errores = lexer.analizar(codigo)
ast = build_tree(tokens, errores)
check_semantic(ast, tabla, errores)

quads = GeneradorTAC().generar(ast)
quads_opt, _ = optimizar(quads)

rutas = reportes.generar_reportes_completos(
    "salida/",
    tokens=tokens,
    tabla=tabla,
    errores=errores,
    tac=formatear_tac(quads),
    tac_opt=formatear_tac(quads_opt),
)
```

---

<a id="qa"></a>
## 12. Suites de QA

| Suite | Casos | Cubre |
|---|---|---|
| `qa_rubrica.py` | 42 | Los 5 criterios técnicos de la rúbrica |
| `qa_completo.py` | 90 | 9 bloques A–I (léxico, sintáctico, semántico, TAC, opt, reportes, pipeline, stress, regresión) |
| `qa_test.py` | 7 | Los 7 ejemplos precargados de `main.py` vía `bridge.py` |

**Total: 139 casos automáticos, 100% PASS.**

### Cómo correr

```bash
python qa_rubrica.py       # ~2 s
python qa_completo.py      # ~10 s
python qa_test.py          # ~15 s (lanza subprocesos)
```

---

<a id="troubleshooting"></a>
## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'ply'`

```bash
pip install ply
```

### `parser.out` y `parsetab.py` aparecen en el repo

PLY genera estos archivos cuando construye las tablas. Están en `.gitignore`,
así que `git status` los ignora. Si los ves localmente: `rm parser.out parsetab.py`.

### Tkinter no se abre en Linux

```bash
sudo apt install python3-tk
```

### La UI web devuelve "Error 500"

- Asegurate que `python` esté en el `PATH` del usuario que corre PHP
  (en Windows es `python`, en Linux/Mac es `python3` — `analizar.php`
  detecta automáticamente).
- Probá `python bridge.py archivo.programa` directamente para descartar
  problemas con `bridge.py`.

### Los errores semánticos no se reportan con línea/columna

Asegurate de llamar `build_tree(tokens, errores)` **antes** de
`check_semantic(ast, tabla, errores)`. El parser ya prepara el contexto
necesario para que `check_semantic` extraiga línea/columna correctamente.

### El TAC se genera aunque haya errores

Por seguridad, `main.py` y `bridge.py` **no generan TAC** cuando hay
errores (para no mostrar código inválido). Si invocás `GeneradorTAC`
directamente sin chequear errores, sí lo genera (puede contener
instrucciones inválidas como `b = not`).

---

## Apéndice: archivos clave

| Archivo | Líneas | Descripción |
|---|---|---|
| `frontend/lexer.py` | ~190 | PLY lexer + clase `Lexer.analizar()` |
| `frontend/parser.py` | ~700 | PLY yacc + AST + `check_semantic` |
| `frontend/generador_intermedio.py` | ~180 | `GeneradorTAC` (visitor) |
| `frontend/tabla_simbolos.py` | ~80 | `Simbolo` + `TablaSimbolos` |
| `frontend/errores.py` | ~85 | Módulo de errores estructurados |
| `intermedio.py` | ~65 | `Quad` + `formatear_tac` |
| `backend/optimizador.py` | ~305 | 6 pasadas + driver con punto fijo |
| `reportes.py` | ~500 | Generadores HTML |
| `main.py` | ~1300 | UI Tkinter completa |
| `bridge.py` | ~150 | CLI / JSON / orquestador |
