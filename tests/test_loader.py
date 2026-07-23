# tests/test_loader.py
"""Pruebas unitarias para la carga, validacion y filtrado de tickets."""

import pytest

from csv_analyzer.loader import(
    validate_columns,
    load_tickets, 
    filter_tickets,
    REQUIRED_COLUMNS,
)

def _write_csv(path, contenido: str) -> None:
    path.write_text(contenido, encoding="utf-8", newline="")

CSV_VALIDO = (
    "agente,categoria,estado,prioridad,fecha_creacion,fecha_cierre\n"
    "ana,soporte,cerrado,2,2026-01-05,2026-01-07\n"
    "luis,ventas,abierto,1,2026-01-10,\n"
)

# --- validate_columns --- 

def test_validate_columns_return_empty_when_all_present():
    """Con todas las columnas requeridas presentes, no debe faltar ninguna."""
    
    faltantes = validate_columns(REQUIRED_COLUMNS)
    assert faltantes == []

def test_validate_columns_detects_missing_columns():
    """Debe detectar exactamente las columnas ausentes, sin lanzar excepcion."""

    columnas_incompletas = ["agente", "categoria", "estado"]
    faltantes = validate_columns(columnas_incompletas)
    assert "prioridad" in faltantes
    assert "fecha_creacion" in faltantes
    assert "fecha_cierre" in faltantes

def test_validate_columns_handles_none_fieldnone():
    """Un CSV vacio (sin encabezado) retorna fieldnames=None; no debe fallar."""

    faltantes = validate_columns(None)
    assert faltantes == REQUIRED_COLUMNS

# --- load_tickets: caso exitoso --- 

def test_load_tickets_parses_valid_csv(tmp_path):
    """Un CSV valido debe cargar el numero correcto de filas con tipos convertidos."""

    csv_path = tmp_path / "tickets.csv"
    _write_csv(csv_path, CSV_VALIDO)

    tickets = load_tickets(csv_path)

    assert len(tickets) == 2
    assert tickets[0]["agente"] == "ana"
    assert tickets[0]["prioridad"] == 2
    assert tickets[1]["fecha_cierre"] is None

# --- load_tickets: casos de error ---

def test_load_tickets_raises_file_not_found(tmp_path):
    """Una ruta inexistente debe lanzar FileNotFoundError, no un error generico."""
    ruta_falsa = tmp_path / "no_existe.csv"

    with pytest.raises(FileNotFoundError):
        load_tickets(ruta_falsa)

def test_load_tickets_raises_value_error_on_missing_columns(tmp_path):
    """Un CSV sin columnas requeridas debe fallar con un mensaje claro, no un KeyError."""

    csv_path = tmp_path / "incomplete.csv"
    _write_csv(csv_path, "agente,categoria\nana, soporte\n")

    with pytest.raises(ValueError, match="prioridad"):
        load_tickets(csv_path)

def test_load_tickets_handles_invalid_priority_without_raising(tmp_path):
    """Una prioridad no numerica no debe detener la carga: la fila queda con prioridad=None."""

    csv_path = tmp_path / "prioridad_invalida.csv"
    _write_csv(
        csv_path,
        "agente,categoria,estado,prioridad,fecha_creacion,fecha_cierre\n"
        "ana,soporte,abierto,alta,226-01-05,\n",
    )

    tickets = load_tickets(csv_path)

    assert len(tickets) == 1
    assert tickets[0]["prioridad"] is None

# --- filtrar_tickets ---

def test_filter_tickets_by_agent_and_status():
    """El filtro combinado de agente + estado debe aplicar ambas condiciones (AND)."""

    tickets = [
        {"agente": "ana", "estado": "abierto", "fecha_creacion": "2026-01-01"},
        {"agente": "ana", "estado": "cerrado", "fecha_creacion": "2026-01-02"},
        {"agente": "luis", "estado": "abierto", "fecha_creacion": "2026-01-03"},
    ]

    resultado = filter_tickets(tickets, agente="ana", estado="abierto")

    assert len(resultado) == 1
    assert resultado[0]["agente"] == "ana"
    assert resultado[0]["estado"] == "abierto"

def test_filter_tickets_with_no_matches_returns_empty_list():
    """Un filtro que no coincide con ningun ticket debe retornar lista vacia, sin excepcion."""

    tickets = [{"agente": "ana", "estado": "abierto", "fecha_creacion": "2026-01-01"}]

    resultado = filter_tickets(tickets, agente="agente_inexistente")

    assert resultado == []