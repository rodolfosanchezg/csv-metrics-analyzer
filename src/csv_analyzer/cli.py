# src/csv_analyzer/cli.py
"""Punto de entrada de linea de comandoos para el Analizador de Indicadores CSV."""

import argparse
import sys 
from pathlib import Path

from .loader import load_tickets, filter_tickets
from .metrics import build_summary
from .output import export

def build_parser() -> argparse.ArgumentParser:
    """Define argumentos: --input, --format, --output, --agente, --estado, --desde, --hasta."""

    parser = argparse.ArgumentParser(
        prog = "csv-analyzer",
        description = "Analiza un CSV de tickets y genera un resumen de indicadores operativos."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta del archivo CSV de tickets a analizar.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Formato de sallida del resumen (por defecto: json).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help = "Ruta de archivo donde guardar el resumen. Si se omite, se imprime en pantalla."
    )
    parser.add_argument("--agente", default=None, help="Filtra por agente.")
    parser.add_argument("--estado", default=None, help="Filtra por estado (abierto/cerrado).")
    parser.add_argument("--desde", default=None, help="Filtra desde esta fecha de creacion (YYYY-MM-DD).")
    parser.add_argument("--hasta", default=None, help="Filtra hasta esta fecha de creacion (YYYY-MM-DD).")
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        tickets = load_tickets(Path(args.input))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    
    tickets_filtrados = filter_tickets(
        tickets, 
        agente = args.agente,
        estado = args.estado,
        fecha_desde = args.desde,
        fecha_hasta = args.hasta,
    )

    resumen = build_summary(tickets_filtrados)
    content = export(resumen, fmt=args.format, path=args.output)

    if args.output:
        print(f"Resumen guardado en: {args.output}")
    else:
        print(content)

    return 0

if __name__ == "__main__":
    sys.exit(main())