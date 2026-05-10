# Fase 2 - Resumen general

## Una intro rápida

Un compilador es un programa que toma código escrito por una persona (en
nuestro caso, código en español tipo `programa { entero x = 5; ... }`) y
lo transforma en algo más simple que la máquina pueda usar. Lo hace en
varias etapas, como una fábrica con varias estaciones.

En la **fase 1** ya teníamos las primeras estaciones funcionando: leer el
código, reconocer las palabras y verificar que la gramática esté bien
escrita. En la **fase 2** agregamos las estaciones que faltaban:

- Verificar que el código tenga **sentido** (no solo que esté bien escrito).
- Traducirlo a una forma intermedia más fácil de procesar.
- **Optimizarlo** para que sea más eficiente.
- **Visualizarlo** todo en una interfaz gráfica y en reportes HTML.

---

## Qué venía de antes (fase 1)

El compilador en la fase 1 ya sabía hacer estas cosas:

- **Lexer**: lee el código carácter por carácter y agrupa lo que ve en
  "palabras" del lenguaje (a estas palabras se les dice *tokens*). Por
  ejemplo, en `entero x = 5;` reconoce que `entero` es un tipo, `x` es
  un nombre de variable, `=` es asignación, `5` es un número, `;` es
  un fin de instrucción.

- **Parser**: toma los tokens y verifica que estén en un orden válido
  según las reglas del lenguaje. Si escribís `entero = 5 x;` el parser
  se da cuenta de que el orden está mal.

- **Tabla de símbolos**: lleva un registro de las variables declaradas:
  qué nombre tienen, qué tipo, en qué línea aparecieron.

- **Reportes HTML básicos**: páginas web sencillas que muestran los tokens,
  errores y la tabla de símbolos.

Lo que **no tenía** la fase 1:

- No verificaba si el programa tenía sentido. Por ejemplo, `entero x = "hola";`
  pasaba sin protestar, aunque querés meter texto en una variable entera.
- No generaba código intermedio ni optimizado.
- No tenía interfaz gráfica.

---

## Lo nuevo de la fase 2

### 1. El compilador se partió en dos mitades

Antes todo estaba en un montón de archivos sueltos. Ahora está organizado
en dos carpetas con un nombre claro:

- **`frontend/`** — la parte que entiende **el lenguaje fuente** (el
  código en español que escribís).
- **`backend/`** — la parte que se preocupa por **transformar** ese código
  para que sea más eficiente.

Entre las dos hay un archivo intermedio que les hace de "traductor común":
**`intermedio.py`**. Es como un protocolo: si la mitad de adelante
(frontend) genera algo siguiendo ese protocolo, la mitad de atrás (backend)
sabe cómo leerlo, sin importar el lenguaje original.

¿Por qué importa esto? Porque mañana, si quisiéramos cambiar el lenguaje
fuente (por ejemplo, hacer el compilador en inglés), solo cambiamos el
frontend. Si quisiéramos generar código para otro tipo de máquina, solo
cambiamos el backend. El medio queda igual.

### 2. Análisis semántico: ¿este código tiene sentido?

Una cosa es que el código esté **bien escrito** (eso lo verifica el parser).
Otra cosa es que **tenga sentido**. Por ejemplo:

```
entero x = "hola";       // mal: querés guardar texto en una variable entera
imprimir(z);              // mal: la variable z nunca se declaró
si (5) { ... }            // mal: la condición de un "si" tiene que ser
                          //      verdadero/falso, no un número
entero y = 10 / 0;        // mal: división por cero
```

Eso es lo que hace el **análisis semántico**. En la fase 2 agregamos una
función llamada `check_semantic` que recorre el código y detecta este tipo
de problemas. En total detecta **12 tipos de errores semánticos**, entre
ellos:

- Variables que no fueron declaradas.
- Variables declaradas dos veces.
- Asignar un valor de un tipo a una variable de otro tipo.
- Usar una variable antes de declararla.
- Condiciones que no son verdadero/falso.
- División por cero.
- Operaciones imposibles, como sumar un texto con un número.

Cada error te dice **en qué línea y qué columna está**, para que sepas
dónde mirar.

### 3. Código de Tres Direcciones (TAC)

Acá es donde aparece el "código intermedio". La idea es traducir el
programa original a una forma **más simple y plana**, donde cada
instrucción hace una sola cosa.

Por ejemplo, una línea como:

```
entero c = (a + b) * 2;
```

Se traduce a tres instrucciones simples:

```
t1 = a + b
t2 = t1 * 2
c = t2
```

A cada una de esas líneas le decimos **"cuádruplo"** porque tiene cuatro
partes: una operación (`+`, `*`, `=`), dos operandos (los valores con los
que opera) y un destino (dónde guarda el resultado). El nombre **"código
de tres direcciones"** viene de que cada instrucción menciona como máximo
tres "direcciones" (lugares donde hay un valor): los dos operandos y el
destino.

Las variables que empiezan con `t` (como `t1`, `t2`) son **temporales**:
las inventa el compilador para guardar resultados intermedios.

¿Por qué hacemos esto? Porque tener el programa en esta forma simple es
**mucho más fácil de analizar y optimizar** que con expresiones anidadas
como las del código original.

Nuestro generador de código intermedio soporta todas las cosas que tiene
el lenguaje: asignaciones, operaciones, `si/sino`, `mientras`,
`hacer_mientras`, `para`, `imprimir`, `leer`, y todos los operadores.

### 4. Optimización

Una vez que tenemos el programa en forma de cuádruplos, el **optimizador**
lo recorre y trata de mejorarlo. "Mejorarlo" significa que el programa
sigue haciendo lo mismo, pero ahora hace menos cuentas o usa menos memoria.

El optimizador hace **seis "pasadas"** (cada pasada busca un tipo
específico de mejora):

1. **Calcular cosas que ya se pueden saber.** Si ve `t1 = 3 + 4`, en vez
   de hacer la suma cuando el programa corra, la hace ya y deja `t1 = 7`.

2. **Reemplazar variables por sus valores conocidos.** Si vio `t1 = 7` y
   más adelante hay `t2 = t1 * 2`, lo reescribe como `t2 = 7 * 2`. Después
   la primera pasada lo va a plegar a `t2 = 14`.

3. **Eliminar saltos inútiles.** Si el programa dice "si verdadero, hacer
   esto, sino hacer lo otro", obviamente siempre va a hacer "esto" — la
   otra rama nunca se ejecuta y se puede borrar.

4. **Borrar código al que nunca se llega.** Si después de un "saltar
   incondicionalmente" hay más instrucciones, esas instrucciones jamás
   se ejecutan, así que se eliminan.

5. **Borrar cuentas inútiles.** Si calcula `t3 = a + b` pero nunca usa
   `t3` después, esa cuenta no sirve para nada y se elimina.

6. **Limpiar saltos redundantes.** Si dice "saltar al lugar X" y
   exactamente abajo está el lugar X, el salto no hace nada y se borra.

Lo interesante: estas pasadas se aplican **una y otra vez** hasta que
ninguna haga cambios. Esto es porque cada pasada puede crear nuevas
oportunidades para que otra mejore más cosas. A esto se le dice "iterar
hasta punto fijo".

**Resultado típico:** programas con 30% a 50% menos instrucciones que el
código original, sin cambiar lo que el programa hace.

### 5. Reportes HTML

Los reportes son páginas web bonitas que muestran el resultado del análisis.
La fase 1 tenía reportes muy básicos. En la fase 2 los rehicimos con
diseño moderno y agregamos uno nuevo y clave:

- **Reporte de errores semánticos** — el más importante para esta entrega.
  Una tabla con cada error: número, tipo, **línea**, **columna**, qué
  variable u operación afecta, y la descripción.
- **Reporte de errores combinado** — todos los errores (léxicos,
  sintácticos y semánticos) juntos.
- **Reporte de tokens** — lista todo lo que el lexer reconoció.
- **Reporte de tabla de símbolos** — las variables del programa.
- **Reporte del código intermedio (TAC)** — los cuádruplos originales.
- **Reporte del código intermedio optimizado** — los cuádruplos después
  del optimizador.

Los HTML tienen diseño con gradientes, hover en las filas, etiquetas de
colores por tipo de error (rojo léxico, amarillo sintáctico, morado
semántico) y son seguros (no se pueden inyectar scripts maliciosos).

### 6. Interfaz gráfica de escritorio (Tkinter)

Una ventana con seis pestañas y un editor en el centro. Lo que hace:

- **Editor**: coloreado de tokens en vivo mientras escribís.
- **Tokens**: tabla con todo lo que reconoció el lexer.
- **Árbol**: el árbol que arma el parser, dibujado como cajitas
  conectadas.
- **Semántico**: tabla de símbolos y estadísticas del programa.
- **Código Intermedio**: el TAC, con sub-pestañas para ver el original,
  el optimizado, los dos lado a lado, y una explicación de cada pasada
  del optimizador.
- **Errores**: consola con todos los problemas detectados.

Apretás **F5** y se ejecuta todo el análisis. Tiene un menú de
**ejemplos** con 7 programas precargados para probar (variables, control
de flujo, bucles, expresiones complejas, errores intencionales, etc.).
Tiene un botón **"REPORTES HTML"** que genera los 6 reportes en la
carpeta que elijas y abre el más importante (errores semánticos) en el
navegador.

### 7. Interfaz web (PHP + JavaScript)

La misma idea pero corriendo en el navegador. El usuario escribe código
en una página web, hace click en "Analizar", y la página le muestra los
tokens, símbolos, errores, TAC original y TAC optimizado. Por debajo, la
página llama a nuestro pipeline en Python a través de un archivo PHP.

### 8. Pruebas automáticas

Para garantizar que todo funciona bien, escribimos tres conjuntos de
pruebas que se corren con un comando:

- **`qa_rubrica.py`** (42 pruebas) — una prueba por cada cosa que pide la
  rúbrica de evaluación.
- **`qa_completo.py`** (90 pruebas) — pruebas más detalladas: caracteres
  raros, programas con 50 variables, anidaciones profundas, casos límite.
- **`qa_test.py`** (7 pruebas) — los 7 ejemplos precargados de la UI,
  corridos por línea de comandos.

**Total: 139 pruebas, todas pasan.**

### 9. Documentación

Cuatro documentos para distintos usos:

- **`RESUMEN_FASE2.md`** (este archivo) — qué se hizo, contado fácil.
- **`DOCUMENTACION.md`** — manual técnico con detalles para programadores.
- **`presentacion_fase2.pdf`** — guía técnica de 13 páginas para preparar
  la presentación.
- **`GUION_PRESENTACION.md`** — guion paso a paso de qué hacer y qué
  decir el día de la presentación.

---

## Números de la fase

| Indicador | Valor |
|---|---|
| Líneas de código agregadas o modificadas | ~3500 |
| Módulos nuevos | 4 |
| Pasadas del optimizador | 6 |
| Tipos de errores semánticos detectados | 12 |
| Tipos de instrucción del código intermedio | 8 |
| Reportes HTML que se generan | 6 |
| Pruebas automáticas | 139 (todas pasan) |
| Ejemplos precargados en la UI | 7 |
| Pestañas de la UI de escritorio | 6 |

---

## Cómo está organizado el proyecto

```
compiladores-2026/
│
├── frontend/                      Todo lo que entiende el lenguaje
│   ├── lexer.py                   reconoce palabras
│   ├── parser.py                  verifica gramática + semántica
│   ├── tabla_simbolos.py          variables declaradas
│   ├── errores.py                 maneja los errores
│   └── generador_intermedio.py    traduce a cuádruplos
│
├── intermedio.py                  el "traductor común" entre las dos mitades
│
├── backend/                       Todo lo que optimiza
│   └── optimizador.py             las 6 pasadas
│
├── reportes.py                    genera los HTML
├── bridge.py                      pipeline por línea de comandos
├── main.py                        ventana de escritorio (Tkinter)
├── index.php / analizar.php       página web (PHP + JS)
│
├── qa_rubrica.py                  pruebas según la rúbrica
├── qa_completo.py                 pruebas exhaustivas
├── qa_test.py                     pruebas del pipeline completo
│
└── documentación (4 archivos)
```

---

## Para qué sirve todo esto

Lo más importante de esta fase, más allá de las funcionalidades
puntuales, es la **separación clara** entre las dos mitades del
compilador. Hoy genera código intermedio que se optimiza; mañana, si se
quisiera, ese mismo código intermedio se podría traducir a código real
de máquina (eso sería una eventual fase 3) sin tocar nada del frontend.

Y todo el camino del programa — desde que lo escribís hasta que sale
optimizado — se puede ver con detalle en la interfaz gráfica o en los
reportes HTML, lo que hace al proyecto útil no solo como un compilador
funcional sino también como una herramienta para entender qué hace cada
etapa.
