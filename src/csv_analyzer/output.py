# src/csv_analyzer/output.py
from pathlib import Path

def export(summary: dict, fmt: str = "json", path: str | None = None) -> str:
    """Exporta el resumen como JSON o CSV. Si path es None, retorna el string sin escribir a disco."""