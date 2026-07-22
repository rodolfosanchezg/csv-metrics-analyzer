# src/csv_analyzer/output.py
"""Exporta el resumen de indicadores como JSON o CSV."""

import csv
import io
import json

from pathlib import Path

def _format_as_json(summary: dict) -> str:
    """Genera una representacion JSON del resumen."""
    
    return json.dumps(summary, indent=2, ensure_ascii=False)

def _format_as_csv(summary: dict) -> str:
    """Genera una representacion CSV del resumen, en formato indicador/valor.
    
    Los valores complejos (dict, list) se serializan como JSON dentro de la celda, 
    para que la fila siga siendo un CSV valido de una sola columna de valor por
    indicador, sin romper la estructura tabular.

    """

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["indicador", "valor"])

    for clave, valor in summary.items():
        if isinstance(valor, (dict,list)):
            valor_serializado = json.dumps(valor, ensure_ascii=False)
        else:
            valor_serializado = valor
        writer.writerow([clave, valor_serializado])

    return buffer.getvalue()

def export(summary: dict, fmt: str = "json", path: str | None = None) -> str:
    """Exporta el resumen como JSON o CSV. 
    
    Si path es None, retorna el string generado sin escribir a disco.
    Si path se proporciona, escribe el archivo y tambien retorna el striing.
    Lanza ValueError si fmt no es json ni csv (error de uso, no de datos).
    
    """

    if fmt not in ("json", "csv"):
        raise ValueError(f"Formato no soportado: {fmt!r}. Usa 'json' o 'csv'.")
    
    content = _format_as_json(summary) if fmt == "json" else _format_as_csv(summary)

    if path is not None:
        output_path = Path(path)
        output_path.write_text(content, encoding="utf-8", newline="")
    
    return content