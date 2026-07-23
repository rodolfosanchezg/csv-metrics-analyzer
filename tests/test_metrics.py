# tests/test_metrics.py
"""Pruebas unitarias para el calculo de indicadores operativos."""

from csv_analyzer.metrics import (
    count_total,
    count_resolved,
    calculate_resolved_percentage,
    calculate_average_resolution_time,
    calculate_load_by_agent,
    top_categories,
    oldest_open_tickets,
    build_summary,
)

def _ticket(agente="ana", categoria="soporte", estado="abierto", prioridad=1, fecha_creacion="2026-01-01", fecha_cierre=None):
    return {
        "agente": agente,
        "categoria": categoria,
        "estado": estado,
        "prioridad": prioridad, 
        "fecha_creacion": fecha_creacion,
        "fecha_cierre": fecha_cierre,
    }

# --- Casos exitosos ---

def test_calculate_resolved_percentage_with_mixed_tickets():
    """El porcentaje resuelto debe calcularse correctamente sobre datos mixtos."""

    tickets = [
        _ticket(estado="cerrado"),
        _ticket(estado="cerrado"),
        _ticket(estado="abierto"),
        _ticket(estado="abierto"),
    ]

    assert count_total(tickets) == 4
    assert count_resolved(tickets) == 2
    assert calculate_resolved_percentage(tickets) == 50.0

def test_calculate_average_resolution_time_with_valid_closed_ticket():
    """El tiempo promedio debe calcularse correctamente sobre tickets cerrados validos."""

    tickets = [
        _ticket(estado="cerrado", fecha_creacion="2026-01-01", fecha_cierre="2026-01-03"),
        _ticket(estado="cerrado", fecha_creacion="2026-01-01", fecha_cierre="2026-01-05"),
    ]

    resultado = calculate_average_resolution_time(tickets)

    assert resultado == 3.0

def test_calculate_load_by_agent_counts_correctly():
    tickets = [_ticket(agente="ana"), _ticket(agente="ana"), _ticket(agente="luis")]

    resultado = calculate_load_by_agent(tickets)

    assert resultado == {"ana": 2, "luis": 1}

def test_top_categories_returns_sorted_by_frequency():
    tickets = [
        _ticket(categoria="soporte"),
        _ticket(categoria="soporte"),
        _ticket(categoria="ventas"),
    ]

    resultado = top_categories(tickets, n=2)

    assert resultado[0] == ("soporte", 2)
    assert resultado[1] == ("ventas", 1)

    # --- Casos de error / borde ---

    def test_calculate_resolved_percentage_with_empty_list_returns_zero():
        """Una lista vacia no debe lanzar ZeroDivisionError; debe retornar 0.0."""

        assert calculate_resolved_percentage([]) == 0.0

    def test_calculate_average_resolution_time_ignores_invalid_dates():
        """Fechas con formato invalido no deben lanzar excepcion; se excluyen del calculo."""

        tickets = [
            _ticket(estado="cerrado", fecha_creacion="fecha_invalida", fecha_cierre="2026-01.05"),
            _ticket(estado="cerrado", fecha_creacion="2026-01-01", fecha_cierre="2026-01-03"),
        ]

        resultado = calculate_average_resolution_time(tickets)

        assert resultado == 2.0

    def test_calculate_average_resolution_time_ignores_negative_durations():
        """Un cierre anterior a la creacion (dato inconsistente) se descarta, no rompe el promedio."""

        tickets = [
            _ticket(estado="cerrado", fecha_creacion="2026-01-10", fecha_cierre="2026-01-05"),
            _ticket(estado="cerrado", fecha_creacion="2026-01-01", fecha_cierre="2026-01-03"),
        ]

        resultado = calculate_average_resolution_time(tickets)

        assert resultado == 2.0

    def test_oldest_open_tickets_excludes_closed_and_invalid_dates():
        tickets = [
            _ticket(estado="cerrado", fecha_creacion="2026-01-01"),
            _ticket(estado="abierto", fecha_creacion="fecha_invalida"),
            _ticket(estado="abierto", fecha_creacion="2026-01-05"),
        ]

        resultado = oldest_open_tickets(tickets, n=5)

        assert len(resultado) == 1
        assert resultado[0]["fecha_creacion"] == "2026-01-05"

    def test_top_categories_with_n_greater_than_available_does_not_raise():
        """Pedir mas categorias de las que existen no debe lanzar error."""

        tickets = [_ticket(categoria="soporte")]

        resultado = top_categories(tickets, n=100)

        assert resultado == [("soporte", 1)]

    def test_build_summary_on_empty_list_does_not_raise():
        """build_summary sobre una lista vacia no debe lanzar excepcion en ninguna metrica."""

        resumen = build_summary([])

        assert resumen["total_tickets"] == 0
        assert resumen["porcentaje_resuelto"] == 0.0
        assert resumen["tiempo_promedio_resolucion_dias"] is None
        assert resumen["carga_por_agente"] == {}
        assert resumen["top_categorias"] == []
        assert resumen["tickets_abiertos_mas_antiguos"] == []