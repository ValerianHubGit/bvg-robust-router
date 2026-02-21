from itertools import product
from datetime import datetime
from src.api.models import Journey
from src.api.bvg_client import get_journeys, get_stops
from src.graph.robustness import robustness_score


def find_robust_journeys(start_query: str, end_query: str, when: datetime) -> tuple[list[Journey], list[float]]:
    #0. from_ids und to_ids bestimmen aus querys
    start_stops=get_stops(start_query)
    end_stops=get_stops(end_query)                              #eigentlich wollte ich dies. aber wegen API-Anfragen-Limit:
                                                                #start_ids=[x.id for x in start_stops]
                                                                #end_ids=[x.id for x in end_stops]
    start_ids=start_stops[0].id
    end_ids=end_stops[0].id
    # 1. Journeys von API holen
    journeys=get_journeys(start_ids, end_ids, when)
                                                                    #for x in [get_journeys(from_id, to_id) for (from_id, to_id) in product(start_ids, end_ids)]:
                                                                    #   journeys.extend(x)
        # 2. Nach robustness_score sortieren
    journeys_sorted=sorted(journeys, key=lambda x: robustness_score(x))
    # 3. Sortierte Liste zurückgeben
    return (journeys_sorted, [robustness_score(x) for x in journeys_sorted])