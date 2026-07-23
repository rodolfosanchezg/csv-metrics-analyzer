# src/csv_analyzer/metrics.py
"""Calcula indicadores operativos a partir de una lista de tickets."""

from datetime import date
from collections import Counter

def count_total(tickets: list[dict]) -> int: 
    """Cuenta el numero total de tickets."""
    return len(tickets)

def count_resolved(tickets: list[dict]) -> int:
    """Cuenta cuantos tickets estan en estado 'cerrado'."""
    return sum(1 for t in tickets if t["estado"] == "cerrado")

def calculate_resolved_percentage(tickets: list[dict]) -> float:
    """Calcula el porcentaje de tickets resueltos. Retorna 0.0 si no hay tickets."""
    total = count_total(tickets)
    if total == 0:
        return 0.0
    return count_resolved(tickets) / total * 100

def _parse_iso_date(fecha_str: str) -> date | None:
    """Convierte un string ISO (YYYY-MM-DD) a date. Retorna None si el formato  es invalido."""
    try:
        return date.fromisoformat(fecha_str)
    except (ValueError, TypeError):
        return None

def calculate_average_resolution_time(tickets: list[dict]) -> float | None:
    """Calcula el tiempo promedio de resolucion en dias, sobre tickets cerrados
    con fechas validas. 
    
    Retorna None si no hay tickets cerrados con fechas validas para calcular,
    en vez de lanzar una excepcion o retornar un valor engañoso como 0. 
    
    """
    duraciones: list[int] = []

    for t in tickets:
        if t["estado"] != "cerrado":
            continue

        fecha_creacion = _parse_iso_date(t["fecha_creacion"])
        fecha_cierre = _parse_iso_date(t["fecha_cierre"])

        if fecha_creacion is None or fecha_cierre is None:
            continue

        dias = (fecha_cierre - fecha_creacion).days
        if dias < 0:
            continue                # descarta datos inconsistentes (cierra antes que creacion)

        duraciones.append(dias)

    if not duraciones:
        return None
        
    return sum(duraciones) / len(duraciones)

def calculate_load_by_agent(tickets: list[dict]) -> dict[str, int]:
    """Calcula cuantos tickets tiene asignado cada agente.
    
    Reutiliza Counter en vez de un bucle manual con .get(), evitandoo duplicar
    la misma logica de acumulacion.

    """
    return dict(Counter(t["agente"] for t in tickets))

def top_categories(tickets: list[dict], n: int = 5) -> list[tuple[str, int]]:
    """Retorna las n categorias con mas tickets, ordenadas de mayor a menor.
    
    Si hay menos de n categorias distintas, retorna todas las disponibles
    sin lanzar error. 

    """
    conteo = Counter(t["categoria"] for t in tickets)

    return conteo.most_common(n)

def oldest_open_tickets(tickets:list[dict], n: int = 5) -> list[dict]:
    """Retorna los n tickets abiertos mas antiguos, ordenados por fecha de 
    creacion ascendente (el mas antiguo primero).
    
    Los tickets con fecha_creacion invalida o vacia se excluyen del resultado, 
    en vez de romper el ordenamiento o aparecer en una posicion arbitraria.

    """

    abiertos = [
        t for t in tickets
        if t["estado"] == "abierto" and _parse_iso_date(t["fecha_creacion"]) is not None
    ]
    ordenados = sorted(abiertos, key=lambda t: t["fecha_creacion"])

    return ordenados[:n]

def build_summary(tickets: list[dict]) -> dict:
    """Consolida todos los indicadores anteriores en un unico diccionario 
    de resumen, listo para ser exportado por output.py
    
    No aplica filtros: recibe la lista de tickets ya filtrada (si aplica) desde
    cli.py, manteniendo la separacion entre filtrado y calculo.
    
    """

    return {
        "total_tickets": count_total(tickets),
        "resueltos": count_resolved(tickets),
        "porcentaje_resuelto": calculate_resolved_percentage(tickets),
        "tiempo_promedio_resolucion_dias": calculate_average_resolution_time(tickets),
        "carga_por_agente": calculate_load_by_agent(tickets),
        "top_categorias": top_categories(tickets, n=5),
        "tickets_abiertos_mas_antiguos": [
            {"agente": t["agente"], "categoria": t["categoria"], "fecha_creacion": t["fecha_creacion"]}
            for t in oldest_open_tickets(tickets, n=5)
        ],
    }