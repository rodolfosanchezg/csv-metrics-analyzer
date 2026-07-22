# src/csv_analyzer/loader.py
"""Carga y valida datos de tickets desde un archivo CSV."""

import csv
from pathlib import Path

REQUIRED_COLUMNS = [
    "agente",
    "categoria",
    "estado",
    "prioridad",
    "fecha_creacion", 
    "fecha_cierre",
]

def validate_columns(fieldnames: list[str]) -> list[str]:
    """Retorna la lista de columnas requeridas que faltan en el CSV

    Retorna una lista vacia si todas las columnas requeridas estan presentes.
    No lanza excepcion: el llamador decide que hacer con las columnas faltantes.
    
    """
    if fieldnames is None:
        return list(REQUIRED_COLUMNS)
    return [col for col in REQUIRED_COLUMNS if col not in fieldnames]

def _parse_row(raw_row: dict) -> dict:
    """Convierte una fila cruda (todos los strings) a tipos apropiados.
    
    La prioridad se convierte a entro; fecha_cierre vacia se convierte en None.
    Si prioridad no es un numero valido, se conserva como None en vez de fallar.
    
    """
    prioridad_raw = raw_row.get("prioridad", "").strip()

    try: 
        prioridad = int(prioridad_raw)
    except ValueError:
        prioridad = None

    fecha_cierre = raw_row.get("fecha_cierre", "").strip()

    return {
        "agente": raw_row.get("agente", "").strip(),
        "categoria": raw_row.get("categoria", "").strip(),
        "estado": raw_row.get("estado", "").strip(),
        "prioridad": prioridad,
        "fecha_creacion": raw_row.get("fecha_creacion", "").strip(),
        "fecha_cierre": fecha_cierre if fecha_cierre else None
    }

def load_tickets(csv_path: Path) -> list[dict]:
    """Carga el CSV y retorna una lista de diccionarios, uno por fila valida.
    
    Lanza FileNotFoundError si la ruta no existe (error de uso, no de datos).
    Lanza ValueError si faltan columnas requeridas, con un mensaje claro
    indicando cuales, en vez de fallar mas adelante con un KeyError confuso.
    
    """

    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    
    with open(csv_path, encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        columnas_faltantes = validate_columns(lector.fieldnames)
        if columnas_faltantes:
            raise ValueError(
                f"Columnas requeridas faltantes en el CSV: {', '. join(columnas_faltantes)}"
            )
        return [_parse_row(fila) for fila in lector]

def filter_tickets(
        tickets: list[dict],
        agente: str | None = None,
        estado: str | None = None,
        fecha_desde: str | None = None,
        fecha_hasta: str | None = None,
    ) -> list[dict]:
    """Filtra tickets por agente, estado o rango de fechas. 
    
    Cualquier filtro en None se ignora. Las fechas se comparan como strings
    en formato ISO (YYYY-MM-DD), que ordenan correctamente de forma lexicografica.

    Nota: fecha_desde y fecha_hasta filtran sobre fecha_creacion unicamente.
    No se filtra por fecha_cierre en esta version.
    
    """

    resultado = tickets
    
    if agente is not None:
        resultado = [t for t in resultado if t["agente"] == agente]
    
    if estado is not None:
        resultado = [t for t in resultado if t["estado"] == estado]

    if fecha_desde is not None:
        resultado = [t for t in resultado if t["fecha_creacion"] >= fecha_desde]

    if fecha_hasta is not None:
        resultado = [t for t in resultado if t["fecha_creacion"] <= fecha_hasta]

    return resultado

def load_tickets_as_generator(csv_path: Path):
    """Variante de load_tickets que produce un diccionario por fila, uno a la vez,
    sin cargar el archivo completo en memoria. 
    
    Util para archivos grandes donde solo se necesita un recorrido secuencial.
    No aplica filtros ni valida columnas de forma anticipada: cada fila se
    produce a medida que se solicita.
    
    """
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    
    with open(csv_path, encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        columnas_faltantes = validate_columns(lector.fieldnames)
        if columnas_faltantes:
            raise ValueError(
                f"Columnas requeridas faltantes en el CSV; {', '.join(columnas_faltantes)}"
            )
        for fila in lector:
            yield _parse_row(fila)