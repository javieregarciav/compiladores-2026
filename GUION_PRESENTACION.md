# Guion de la presentación - Fase 2

Este documento es un **guion paso a paso** para presentar el proyecto.
Léelo en orden. Cada bloque dice **qué tipear**, **qué hacer click**,
y **qué vas a ver en pantalla**.

---

## ANTES DE LA PRESENTACIÓN (10 minutos)

### Paso 1: Verificar Python

Abre una terminal en la máquina donde vas a presentar y tipea:

```
python --version
```

**Lo que debes ver:** algo como `Python 3.10.x` o superior.

Si dice `Python 2.x.x` o no existe el comando, probá con `python3 --version`.

### Paso 2: Verificar PLY

Tipea:

```
python -c "import ply; print(ply.__version__)"
```

**Lo que debes ver:** `3.11` (o algo cerca).

**Si dice "No module named 'ply'"** → instalá ahora:

```
pip install ply
```

**Si "pip" no funciona** → probá `python -m pip install ply`.

### Paso 3: Ir a la carpeta del proyecto

```
cd "ruta\donde\esta\compiladores-2026"
```

### Paso 4: Correr el QA — confirmación de que todo funciona

```
python qa_rubrica.py
```

**Lo que debes ver al final:**

```
RESUMEN POR CRITERIO
  Criterio 1. Errores semanticos        20/20 casos PASS  (100%)
  Criterio 2. Reporte HTML              2/2 casos PASS  (100%)
  Criterio 3. TAC                       13/13 casos PASS  (100%)
  Criterio 4. Optimizacion              5/5 casos PASS  (100%)
  Criterio 5. Funcionamiento            2/2 casos PASS  (100%)
  TOTAL: 42/42 casos PASS
```

**Si dice `42/42 PASS`** → todo OK, presentás tranquilo.
**Si dice `FAIL` en algún caso** → algo está mal, avisame qué falla antes
de presentar.

### Paso 5: Abrir la UI por primera vez

```
python main.py
```

**Lo que debes ver:** una ventana con fondo oscuro, editor en el centro,
pestañas arriba (Editor, Tokens, Árbol, Semántico, Código Intermedio,
Errores), barra inferior con botones (ANALIZAR, LIMPIAR, EJEMPLOS,
REPORTES HTML).

**Si abre correctamente** → cerrá la ventana. Listo para presentar.

---

## DURANTE LA PRESENTACIÓN

### Bloque 1 — Introducción (1 minuto)

**Qué decir:**
> "Para esta fase 2 implementamos un compilador completo para un lenguaje
> en español. El frontend usa PLY (lex + yacc), produce un árbol sintáctico,
> hace análisis semántico de tipos, genera código de tres direcciones, y
> el backend optimiza ese código con seis pasadas. Todo se visualiza en
> dos UIs: escritorio con Tkinter y web con PHP."

---

### Bloque 2 — Mostrar la UI (2 minutos)

**Qué tipear en terminal:**

```
python main.py
```

**Qué hacer:**
1. Click en el botón **"EJEMPLOS ▾"** (esquina inferior izquierda).
2. Click en **"01 Variables y Tipos"**.

**Qué decir mientras se carga el código:**
> "El lenguaje está en español: `programa { entero edad = 25; ... }`.
> Tiene los tipos `entero`, `decimal`, `cadena`, `booleano`; control de
> flujo con `si/sino/mientras/para/hacer_mientras`; y entrada/salida con
> `imprimir/leer`."

**Qué hacer:**
3. Presionar **F5**.

**Qué se ve:**
- En la pestaña **Tokens**: lista de tokens detectados.
- En la pestaña **Árbol**: AST gráfico.
- En la pestaña **Semántico**: tabla de símbolos (8 variables).
- En la pestaña **Código Intermedio**: TAC original y optimizado.

**Qué decir:**
> "Al presionar F5 corre el pipeline completo: lexer, parser, análisis
> semántico, generación de TAC, optimización. Todo en menos de un
> segundo."

---

### Bloque 3 — Criterio 1: Errores semánticos (3 minutos)

**Qué hacer:**
1. Click en el editor.
2. Click en **"LIMPIAR"**.
3. Tipear o pegar este programa **a propósito con errores**:

```
programa {
    entero x = "hola";
    si (x) { imprimir(z); }
    decimal r = 10 / 0;
    x = verdadero;
    entero x = 99;
}
```

4. Presionar **F5**.

**Qué se ve en la pestaña Errores:**

```
[Semantico] Linea 2, Col 5: Asignacion incompatible: variable 'x'
    de tipo 'entero' no puede recibir un valor 'cadena'
[Semantico] Linea 3, Col 5: La condicion del 'si' debe ser booleana, no 'entero'
[Semantico] Linea 3, Col 23: Variable 'z' no declarada
[Semantico] Linea 4, Col 17: Division por cero (operador '/')
[Semantico] Linea 5, Col 5: Asignacion incompatible: variable 'x'
    de tipo 'entero' no puede recibir un valor 'booleano'
[Semantico] Linea 6: Variable 'x' ya fue declarada en este ambito (linea 2)
```

**Qué decir mientras señalas los errores:**
> "Detectamos seis tipos de errores en este programa:
> - Línea 2: tipo incompatible al declarar.
> - Línea 3: condición de 'si' que no es booleana.
> - Línea 3 otra vez: variable 'z' usada pero nunca declarada.
> - Línea 4: división por cero detectada en compilación.
> - Línea 5: asignación de un valor de tipo incorrecto.
> - Línea 6: variable duplicada en el mismo ámbito.
>
> Cada error trae **línea y columna**, que es lo que pide la rúbrica."

---

### Bloque 4 — Criterio 2: Reporte HTML semántico (2 minutos)

**Qué hacer:** (después del bloque anterior, sin limpiar)

1. Click en **"REPORTES HTML"** (botón verde en la barra inferior).
2. Aparece un diálogo: **elegir una carpeta** (por ejemplo "Escritorio").
3. Click "Seleccionar carpeta".

**Qué se ve:**
- En la consola de errores aparece: `6 reporte(s) HTML generado(s) en ...`.
- **El navegador se abre automáticamente** mostrando el reporte de errores
  semánticos.

**Qué decir:**
> "El reporte HTML tiene un diseño profesional con CSS moderno. Arriba el
> resumen estadístico — cuántos errores de cada categoría. Abajo la tabla
> con cada error: número, tipo, **línea**, **columna**, el identificador
> afectado y la descripción.
>
> Esto cumple el segundo criterio de la rúbrica: reporte HTML estructurado
> con línea y columna por cada error semántico."

**Si querés mostrar los otros reportes:** abrí el explorador de archivos
en la carpeta elegida. Hay 6 archivos HTML:
- `reporte_errores_semanticos.html` ← el clave
- `reporte_errores.html` (todos los errores combinados)
- `reporte_tokens.html`
- `reporte_tabla_simbolos.html`
- `reporte_tac.html`
- `reporte_tac_optimizado.html`

---

### Bloque 5 — Criterio 3: Código de Tres Direcciones (3 minutos)

**Qué hacer:**
1. Click en **"LIMPIAR"**.
2. Pegar este programa correcto:

```
programa {
    entero a = 3;
    entero b = 4;
    entero c = (a + b) * 2;
    si (c > 10) {
        imprimir(c);
    } sino {
        imprimir("pequeno");
    }
}
```

3. Presionar **F5**.
4. Click en la pestaña **"Código Intermedio"**.

**Qué se ve (TAC original, sub-tab "Original"):**

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

**Qué decir mientras lo lees:**
> "Esto es código de tres direcciones. Cada instrucción tiene la forma
> `destino = arg1 op arg2`. Las variables que empiezan con `$t` son
> temporales que crea el compilador para descomponer expresiones, y
> las que empiezan con `$L` son etiquetas para los saltos.
>
> Ven cómo `(a + b) * 2` se descompone: primero `$t1 = a + b`, después
> `$t2 = $t1 * 2`. El si/sino se traduce a saltos condicionales con
> `ifFalse` y `goto`."

---

### Bloque 6 — Criterio 4: Optimización (2 minutos)

**Qué hacer:** (mismo programa, sin limpiar)

Click en el sub-tab **"Optimizado"** dentro de la pestaña Código
Intermedio.

**Qué se ve (TAC optimizado, 7 cuádruplos):**

```
1: a = 3
2: b = 4
3: c = 14
4: imprimir 14
5: goto $L2
6: imprimir "pequeno"
7: $L2:
```

**Qué decir:**
> "El optimizador hace seis pasadas: constant folding, propagación,
> branch pruning, eliminación de código inalcanzable, dead-code y jump
> threading. Las cinco pasadas se repiten hasta que ninguna haga cambios
> — es lo que se llama *punto fijo*.
>
> Acá podemos ver que `(3+4)*2` se calculó en compilación → `c = 14`.
> Los temporales `$t1`, `$t2`, `$t3` muertos se eliminaron. La condición
> `c > 10` quedó propagada y se sabe que es verdadera, entonces se
> imprimió `14` directamente.
>
> Reducimos de 12 cuádruplos a 7 — un 41.7% de reducción."

**Qué hacer (opcional):**

Click en el sub-tab **"Comparación"** para verlos lado a lado, o
**"Info"** para leer la explicación de cada pasada.

---

### Bloque 7 — Criterio 5: Funcionamiento (2 minutos)

**Qué hacer:** abrir una terminal nueva (sin cerrar Tkinter).

```
python qa_rubrica.py
```

**Qué se ve al final:**

```
RESUMEN POR CRITERIO
  Criterio 1. Errores semanticos        20/20 PASS  (100%)
  Criterio 2. Reporte HTML              2/2 PASS  (100%)
  Criterio 3. TAC                       13/13 PASS  (100%)
  Criterio 4. Optimizacion              5/5 PASS  (100%)
  Criterio 5. Funcionamiento            2/2 PASS  (100%)
  TOTAL: 42/42 casos PASS
```

**Qué decir:**
> "Tenemos una suite de QA con 42 casos automáticos, uno por cada item
> de la rúbrica. Todos pasan. Plus tenemos `qa_completo.py` con 90 casos
> más exhaustivos (caracteres ilegales, programas con 50 declaraciones,
> bucles anidados profundo, edge cases). 90 de 90 PASS también."

**Si querés mostrar también el extenso:**

```
python qa_completo.py
```

**Qué se ve:**

```
  [OK] Bloque A. Lexico         10/10 PASS  (100%)
  [OK] Bloque B. Sintactico     10/10 PASS  (100%)
  [OK] Bloque C. Semantico      25/25 PASS  (100%)
  [OK] Bloque D. TAC            17/17 PASS  (100%)
  [OK] Bloque E. Optimizacion   10/10 PASS  (100%)
  [OK] Bloque F. Reportes       7/7 PASS  (100%)
  [OK] Bloque G. Pipeline       2/2 PASS  (100%)
  [OK] Bloque H. Stress         7/7 PASS  (100%)
  [OK] Bloque I. Regresion      2/2 PASS  (100%)
  TOTAL: 90/90 casos PASS (100.0%)
```

---

### Bloque 8 — Cierre (1 minuto)

**Qué decir:**
> "Para cerrar: separamos frontend y backend con un contrato común
> (`Quad`); el TAC es la representación intermedia que elegimos por sobre
> postfija porque permite expresar saltos y asignaciones; el optimizador
> de seis pasadas itera hasta punto fijo; los errores semánticos se
> reportan con línea y columna en HTML estructurado; y todo está
> respaldado por 139 tests automáticos.
>
> Gracias."

---

## QUÉ HACER SI ALGO FALLA

### Si `python main.py` no abre la ventana

```
python -c "import tkinter; print(tkinter.TkVersion)"
```

Si falla, en Linux: `sudo apt install python3-tk`.

### Si dice "No module named 'ply'"

```
pip install ply
```

### Si el botón "REPORTES HTML" no abre el navegador

Los archivos HTML **igual se generan** en la carpeta que elegiste.
Abrí el explorador de archivos, andá a la carpeta, doble click en
`reporte_errores_semanticos.html`. Se abre con el navegador
predeterminado.

### Si una pestaña aparece vacía

Presioná **F5** otra vez. A veces hay que ejecutar el análisis después
de cambiar de pestaña.

### Plan B: solo con la terminal

Si la UI gráfica falla por algún motivo, podés mostrar todo desde
terminal:

```
python qa_rubrica.py            # mostrar 42/42 PASS
python qa_completo.py           # mostrar 90/90 PASS
python bridge.py programa.txt   # JSON del análisis
```

Y abrir los HTML directamente:

```
python -c "
from frontend import Lexer, build_tree, check_semantic, GeneradorTAC
from backend import optimizar
from intermedio import formatear_tac
import reportes

codigo = open('mi_archivo.txt').read()
lex = Lexer()
toks, tabla, errs = lex.analizar(codigo)
ast = build_tree(toks, errs)
check_semantic(ast, tabla, errs)
quads = GeneradorTAC().generar(ast)
quads_opt, _ = optimizar(quads)
reportes.generar_reportes_completos('out', tokens=toks, tabla=tabla,
    errores=errs, tac=formatear_tac(quads), tac_opt=formatear_tac(quads_opt))
print('Reportes en ./out/')
"
```

---

## CHECKLIST FINAL (5 minutos antes de entrar)

- [ ] Terminal abierta en la carpeta del proyecto.
- [ ] `python qa_rubrica.py` corre y da 42/42 PASS.
- [ ] `python main.py` abre la ventana correctamente.
- [ ] El editor responde, los botones funcionan.
- [ ] La carpeta donde vas a guardar los reportes existe (escritorio o similar).
- [ ] Este guion lo tenés a mano (impreso o en otro tab).

Listo. Suerte.
