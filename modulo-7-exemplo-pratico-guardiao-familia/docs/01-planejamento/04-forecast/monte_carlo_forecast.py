import csv
import json
import random
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUT_CSV = BASE / "pert_inputs.csv"
OUTPUT_JSON = BASE / "monte_carlo_resultados.json"

RANDOM_SEED = 42
RUNS = 10000


def pert_mean(o: float, m: float, p: float) -> float:
    return (o + 4 * m + p) / 6


def sample_triangular(o: float, m: float, p: float) -> float:
    return random.triangular(o, p, m)


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * pct))
    return ordered[idx]


def load_inputs() -> list[dict]:
    with INPUT_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    parsed = []
    for row in rows:
        parsed.append(
            {
                "epic": row["epic"],
                "descricao": row["descricao"],
                "o": float(row["o_dias"]),
                "m": float(row["m_dias"]),
                "p": float(row["p_dias"]),
                "motivo_estimativa": row["motivo_estimativa"],
            }
        )
    return parsed


def main() -> None:
    random.seed(RANDOM_SEED)
    items = load_inputs()
    totals = []
    for _ in range(RUNS):
        total = 0.0
        for item in items:
            total += sample_triangular(item["o"], item["m"], item["p"])
        totals.append(total)

    pert_totals = sum(pert_mean(item["o"], item["m"], item["p"]) for item in items)
    result = {
        "assumptions": {
            "runs": RUNS,
            "random_seed": RANDOM_SEED,
            "timebox_days": 180,
            "method": "triangular sampling per epic with PERT reference",
        },
        "epics": items,
        "summary": {
            "pert_total_days": round(pert_totals, 2),
            "p50_days": round(percentile(totals, 0.50), 2),
            "p80_days": round(percentile(totals, 0.80), 2),
            "p95_days": round(percentile(totals, 0.95), 2),
            "min_days": round(min(totals), 2),
            "max_days": round(max(totals), 2),
        },
    }
    result["summary"]["fits_6_months_at_p80"] = result["summary"]["p80_days"] <= 180
    OUTPUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"written={OUTPUT_JSON}")


if __name__ == "__main__":
    main()
