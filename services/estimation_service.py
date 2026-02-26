from collections import Counter


class EstimationService:

    # Temporary static pricing (later move to config or DB)
    PRICE_MAP = {
        "valve": 1500,
        "pump": 5000,
    }

    @classmethod
    def calculate(cls, detections):
        labels = [d.label for d in detections]

        counter = Counter(labels)

        material_breakdown = []
        grand_total = 0

        for symbol, count in counter.items():
            unit_cost = cls.PRICE_MAP.get(symbol, 1000)  # default cost
            total_cost = unit_cost * count

            material_breakdown.append({
                "symbol": symbol,
                "count": count,
                "unit_cost": unit_cost,
                "total_cost": total_cost,
            })

            grand_total += total_cost

        return {
            "total_symbols": sum(counter.values()),
            "material_breakdown": material_breakdown,
            "grand_total_cost": grand_total
        }