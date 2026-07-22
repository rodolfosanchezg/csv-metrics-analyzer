# src/csv_analyzer/metrics.py

def count_total(tickets: list[dict]) -> int: 
    """Cuenta el numero total de tickets."""

def calculate_resolved_percentage(tickets: list[dict]) -> float:
    """Calcula el porcentaje de tickets en estado 'cerrado'."""

def calculate_average_resolution_time(tickets: list[dict]) -> float | None:
    """Calcula el tiempo promedio de resolucion en dias. None si no hay tickets cerrados. """

def calculate_load_by_agent(tickets: list[dict]) -> dict[str, int]:
    """Calcula cuantos tickets tiene asignado cada agente."""

def top_categories(tickets: list[dict], n: int = 5) -> list[tuple[str, int]]:
    """Retorna las n categorias con mas tickets, ordenadas de mayor a menor."""

def oldest_open_tickets(tickets:list[dict], n: int = 5) -> list[dict]:
    """Retorna los n tickets abiertos mas antiguos, ordenados por fecha de creacion."""

def build_summary(tickets: list[dict]) -> dict:
    """Consolida todos los indicadores anteriores en un unico diccionario de resumen."""