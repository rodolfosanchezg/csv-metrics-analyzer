# Analizador de Indicadores Operativos CSV

Herramienta de línea de comandos que analiza un archivo CSV de tickets de
soporte y genera un resumen de indicadores operativos en formato JSON o CSV.

## Problema

Los equipos de soporte/operaciones suelen tener sus datos de tickets en
archivos CSV exportados, pero calcular manualmente indicadores como carga
por agente, tiempo de resolución o categorías más frecuentes es lento y
propenso a errores. Esta herramienta automatiza ese análisis.

## Instalación

Requiere Python 3.11 o superior.

```bash
git clone https://github.com/rodolfosanchezg/csv-metrics-analyzer.git
cd csv-metrics-analyzer
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

pip install -e ".[dev]"
```

> **Nota (Windows/PowerShell):** si al activar el entorno virtual aparece un
> error de política de ejecución de scripts, ejecuta:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

## Uso

Analizar un CSV e imprimir el resumen en pantalla (JSON por defecto):

```bash
csv-analyzer --input data/sample_tickets.csv
```

Formato CSV:

```bash
csv-analyzer --input data/sample_tickets.csv --format csv
```

Guardar en archivo:

```bash
csv-analyzer --input data/sample_tickets.csv --format json --output resumen.json
```

Con filtros (agente, estado, rango de fechas de creación):

```bash
csv-analyzer --input data/sample_tickets.csv --agente ana --estado cerrado
csv-analyzer --input data/sample_tickets.csv --desde 2026-01-08 --hasta 2026-01-10
```

Ver todas las opciones:

```bash
csv-analyzer --help
```

## Arquitectura
```text
cli.py (argparse)
│
├──> loader.load_tickets() → lee y valida el CSV
├──> loader.filter_tickets() → aplica filtros opcionales
├──> metrics.build_summary() → consolida los 6 indicadores
└──> output.export() → JSON o CSV, a pantalla o archivo
```

- `loader.py`: carga, valida columnas requeridas y filtra tickets.
- `metrics.py`: calcula indicadores (volumen, % resuelto, tiempo promedio,
  carga por agente, top categorías, tickets abiertos más antiguos).
- `output.py`: formatea y exporta el resumen.
- `cli.py`: único punto de entrada; no contiene lógica de cálculo.

### Decisiones técnicas

- **Diccionarios simples en vez de una clase para cada ticket**: cada fila
  del CSV ya tiene una forma fija definida por sus columnas; envolverla en
  una clase no agregaba beneficio claro para este alcance.
- **`calculate_average_resolution_time` retorna `None`, no `0.0`**, cuando
  no hay tickets cerrados con fechas válidas — evita confundir "sin datos"
  con "el promedio es cero días".
- **Duraciones negativas se descartan silenciosamente** (cierre anterior a
  creación) en vez de contaminar el promedio con datos inconsistentes.
- **`Counter` de la librería estándar** para `carga_por_agente` y
  `top_categorias`, reutilizando la misma técnica en ambos casos en vez de
  duplicar lógica de acumulación manual.
- **CSV de salida en formato indicador/valor**, con estructuras anidadas
  (dict, list) serializadas como JSON dentro de la celda — evita imponer
  una forma tabular artificial a datos que no son naturalmente tabulares.
- **El filtro de rango de fechas aplica únicamente sobre `fecha_creacion`**,
  no sobre `fecha_cierre` (ver Limitaciones).

## Pruebas

```bash
pytest -v
```

Más de 20 pruebas unitarias cubren `loader.py`, `metrics.py` y `output.py`,
con casos exitosos y de error/borde: columnas faltantes, prioridad inválida,
fechas inválidas, duraciones negativas, listas vacías, filtros sin
coincidencias, y formatos de exportación no soportados.

## Evidencia y decisiones de diseño (para portafolio)

**Antes/después:** una fila cruda del CSV se ve así:

```csv
ana,soporte,cerrado,2,2026-01-05,2026-01-07
```

Y se convierte en parte de este resumen consolidado:

```json
{
  "total_tickets": 10,
  "resueltos": 6,
  "porcentaje_resuelto": 60.0,
  "carga_por_agente": {"ana": 4, "luis": 3, "carla": 3},
  "top_categorias": [["soporte", 4], ["facturacion", 3], ["ventas", 3]]
}
```

**Decisión de diseño que redujo duplicación:** calcular "carga por agente"
recorriendo la lista una vez por cada agente distinto (comparando nombre
por nombre) tiene complejidad O(n²). En su lugar, se usa `collections.Counter`
para acumular en una sola pasada — O(n) — reutilizando la misma técnica
tanto para `calculate_load_by_agent()` como para `top_categories()`, en vez
de escribir un bucle de acumulación manual distinto para cada uno.

## Reto opcional: variante con generador

`loader.py` incluye `load_tickets_as_generator()`, una variante de
`load_tickets()` que produce un diccionario por fila **uno a la vez**, en
vez de cargar el archivo CSV completo en una lista antes de retornar.

**Diferencia de enfoque:**

| | `load_tickets()` | `load_tickets_as_generator()` |
|---|---|---|
| Memoria | Carga todas las filas antes de retornar | Una fila a la vez, bajo demanda |
| Recorridos | Se puede recorrer múltiples veces | Se agota tras un solo recorrido |
| Uso en este proyecto | Necesario, porque `build_summary()` recorre los tickets varias veces (una por cada métrica) | No se usa en el flujo principal por esa misma razón |

Aunque el dataset de ejemplo es pequeño y no requiere esta optimización, la
variante generador queda documentada como la solución correcta para el caso
de un CSV de varios gigabytes donde cargar todo en memoria no sería viable,
combinada con un procesamiento de una sola pasada (por ejemplo, solo contar
el total de filas, sin calcular las 6 métricas completas).

## Limitaciones conocidas

- El filtro de rango de fechas (`--desde` / `--hasta`) aplica únicamente
  sobre `fecha_creacion`. No es posible filtrar por `fecha_cierre` en esta
  versión.
- En caso de empate en `top_categorias`, el orden entre categorías empatadas
  no está garantizado como determinista por criterio alfabético.
- No valida formatos de fecha distintos a ISO (YYYY-MM-DD).
- `load_tickets_as_generator()` no aplica filtros ni se usa en el flujo
  principal del CLI en esta versión.

## Roadmap

- [ ] Salida coloreada en terminal y bandera `--verbose`.
- [ ] Criterio de desempate explícito en `top_categorias`.
- [ ] Soporte de filtro por `fecha_cierre` como campo alternativo.

## Licencia

Uso educativo — Programa de 24 Semanas Python Developer.