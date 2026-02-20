from src.api.models import Journey
from src.api.bvg_client import get_journeys
from src.graph.robustness import robustness_score

def find_robust_journeys(from_id: str, to_id: str) -> list[Journey]:
    # 1. Journeys von API holen
    journeys=get_journeys(from_id, to_id)
    # 2. Nach robustness_score sortieren
    journeys_sorted=sorted(journeys, key=lambda x: robustness_score(x))
    # 3. Sortierte Liste zurückgeben
    return journeys_sorted