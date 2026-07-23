# tests/test_output.py
"""Pruebas unitarias para la exportacion del resumen."""

import csv
import io
import json

from csv_analyzer.output import export

def _resumen_simple():
    return {
        "total_tickets": 4,
        "porcentaje_resuelto": 50.0,
        "carga_por_agente": {"ana": 2, "luis": 2},
        "top_categorias": [("soporte", 2), ("ventas", 1)],
    }

# --- Caso exitoso ---

def test_export_json_produces_valid_parseable_json(tmp_path):
    resumen = _resumen_simple()
    output_file = tmp_path / "resumen.json"

    export(resumen, fmt="json", path=str(output_file))

    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert data["total_tickets"] == 4
    assert data["carga_por_agente"] == {"ana": 2, "luis": 2}

def test_export_csv_produces_valid_parseable_csv():
    """El CSV generado debe poder leerse de vuelta con el modulo csv estandar."""
    
    resumen = _resumen_simple()

    content = export(resumen, fmt="csv")

    lector = csv.reader(io.StringIO(content))
    filas = list(lector)

    assert filas[0] == ["indicador", "valor"]
    assert filas[1][0] == "total_tickets"
    assert filas[1][1] == "4"

# --- Casos de error ---

def test_export_invalid_format_raises_value_error():
    resumen = _resumen_simple()

    try: 
        export(resumen, fmt="xml")
        assert False, "Se esperaba ValueError para formato no soportado"
    except ValueError as exc:
        assert "xml" in str(exc)

def test_export_without_path_does_not_write_file(tmp_path, monkeypatch):
    """Si no se pasa path, no debe escribirse ningun archivo, solo retornar el string."""

    monkeypatch.chdir(tmp_path)
    resumen = _resumen_simple()

    content = export(resumen, fmt="json", path=None)

    assert isinstance(content, str)
    assert list(tmp_path.iterdir()) == []

def test_export_json_serializes_nested_structures_correctly():
    """Estructuras anidadas (dict, list de tuplas) deben serializarse sin error."""

    resumen = _resumen_simple()

    content = export(resumen, fmt="json")
    data = json.loads(content)

    assert data["top_categorias"] == [["soporte", 2], ["ventas", 1]]