#!/usr/bin/env python3
"""Quality Gate for JMeter load test results.

Checks whether the total p95 response time and error percentage
exceed predefined performance thresholds:
- p95 <= 100 ms
- Error rate <= 1.0 %
"""

import json
import sys
from pathlib import Path

P95_MAX_MS = 100.0
ERROR_MAX_PCT = 1.0


def evaluate_report(target_path: Path) -> int:
    if target_path.is_dir():
        stats_file = target_path / "statistics.json"
    else:
        stats_file = target_path

    if not stats_file.exists():
        print(f"Error: No se encontro el archivo de estadisticas: {stats_file}", file=sys.stderr)
        return 2

    try:
        with open(stats_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error al leer {stats_file}: {e}", file=sys.stderr)
        return 2

    total = data.get("Total")
    if not total:
        print("Error: El reporte no contiene la clave 'Total'.", file=sys.stderr)
        return 2

    # JMeter statistics.json standard percentile mappings:
    # pct1ResTime = 90th percentile
    # pct2ResTime = 95th percentile
    # pct3ResTime = 99th percentile
    p95 = float(total.get("pct2ResTime", total.get("p95", 0.0)))
    error_pct = float(total.get("errorPct", 0.0))

    passed = True
    print(f"Evaluando reporte: {stats_file}")
    print(f"- p95: {p95:.2f} ms (limite: <= {P95_MAX_MS:.2f} ms)")
    print(f"- Errores: {error_pct:.2f}% (limite: <= {ERROR_MAX_PCT:.2f}%)")

    if p95 > P95_MAX_MS:
        print(f"FALLO: p95 ({p95:.2f} ms) excede el limite de {P95_MAX_MS:.2f} ms", file=sys.stderr)
        passed = False

    if error_pct > ERROR_MAX_PCT:
        print(f"FALLO: Porcentaje de errores ({error_pct:.2f}%) excede el limite de {ERROR_MAX_PCT:.2f}%", file=sys.stderr)
        passed = False

    if passed:
        print("RESULTADO: PASO (exit code 0)")
        return 0
    else:
        print("RESULTADO: REPROBADO (exit code 1)", file=sys.stderr)
        return 1


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <carpeta_del_reporte_o_statistics.json>", file=sys.stderr)
        sys.exit(2)

    target_path = Path(sys.argv[1])
    exit_code = evaluate_report(target_path)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
