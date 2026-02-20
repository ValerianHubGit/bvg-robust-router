from src.api.models import Journey

W1 = 0.5   # Gewicht Gesamtdauer
W2 = 3.0   # Gewicht Umstiegsrisiko
W3 = 5.0   # Gewicht Anzahl Umstiege

def robustness_score(journey: Journey) -> float:
    # T: Gesamtdauer
    # Summe 1/max(p_i, 1) über alle Umstiegsfenster
    # n: Anzahl Umstiege
    T = journey.journey_time
    n = journey.num_transfers
    windows = journey.transfer_windows
    transfer_risk = sum([1/max(1,x) for x in windows])
    return W1*T + W2*transfer_risk + W3*n
    