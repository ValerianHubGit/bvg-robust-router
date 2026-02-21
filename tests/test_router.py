import pytest
from datetime import datetime, timezone, timedelta
from src.api.models import Stop, Connection, Journey
from src.graph.robustness import robustness_score, W1, W2, W3

# ── Hilfsfunktionen ────────────────────────────────────────────────────────────

def make_stop(name: str, id: str = "900000001") -> Stop:
    return Stop(name=name, latitude=52.5, longitude=13.4, id=id)

def make_connection(start: Stop, end: Stop, departure: datetime,
                    duration_minutes: int, transport_id: str = "S1",
                    name: str = "S1", direction: str = "Testrichtung") -> Connection:
    arrival = departure + timedelta(minutes=duration_minutes)
    return Connection(
        start=start,
        end=end,
        start_time=departure,
        end_time=arrival,
        transport_id=transport_id,
        planned_departure=departure,
        planned_arrival=arrival,
        name=name,
        direction=direction,
    )

BASE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

# ── Tests: robustness_score ────────────────────────────────────────────────────

def test_single_connection_no_transfer():
    """Eine Connection, kein Umstieg → Score = W1 * Dauer"""
    stop_a = make_stop("A", "900000001")
    stop_b = make_stop("B", "900000002")
    conn = make_connection(stop_a, stop_b, BASE_TIME, duration_minutes=6)
    journey = Journey(start=stop_a, end=stop_b,
                      start_time=BASE_TIME, connections=[conn])

    expected = W1 * 6
    assert robustness_score(journey) == pytest.approx(expected)


def test_two_connections_same_transport_no_transfer():
    """Zwei Connections mit gleicher transport_id = kein echter Umstieg"""
    stop_a = make_stop("A", "900000001")
    stop_b = make_stop("B", "900000002")
    stop_c = make_stop("C", "900000003")
    conn1 = make_connection(stop_a, stop_b, BASE_TIME, 5, transport_id="S1")
    conn2 = make_connection(stop_b, stop_c, BASE_TIME + timedelta(minutes=5), 5, transport_id="S1")
    journey = Journey(start=stop_a, end=stop_c,
                      start_time=BASE_TIME, connections=[conn1, conn2])

    expected = W1 * 10  # Kein Umstieg, kein W2/W3 Term
    assert robustness_score(journey) == pytest.approx(expected)


def test_two_connections_real_transfer():
    """Echter Umstieg mit 5 Minuten Puffer"""
    stop_a = make_stop("A", "900000001")
    stop_b = make_stop("B", "900000002")
    stop_c = make_stop("C", "900000003")
    conn1 = make_connection(stop_a, stop_b, BASE_TIME, 5, transport_id="S1", name="S1")
    # 5 Minuten Puffer zwischen Ankunft conn1 und Abfahrt conn2
    conn2 = make_connection(stop_b, stop_c, BASE_TIME + timedelta(minutes=10), 5,
                            transport_id="U8", name="U8")
    journey = Journey(start=stop_a, end=stop_c,
                      start_time=BASE_TIME, connections=[conn1, conn2])

    expected = W1 * 15 + W2 * (1 / max(5, 1)) + W3 * 1
    assert robustness_score(journey) == pytest.approx(expected)


def test_walking_leg_ignored_in_transfer_risk():
    """Fußweg zwischen zwei Verbindungen zählt nicht als Umstieg"""
    stop_a = make_stop("A", "900000001")
    stop_b = make_stop("B", "900000002")
    stop_c = make_stop("C", "900000003")
    conn1 = make_connection(stop_a, stop_b, BASE_TIME, 5, transport_id="S1", name="S1")
    walk  = make_connection(stop_b, stop_c, BASE_TIME + timedelta(minutes=5), 3,
                            transport_id="walking", name="Fußweg")
    journey = Journey(start=stop_a, end=stop_c,
                      start_time=BASE_TIME, connections=[conn1, walk])

    # Fußweg → kein Umstieg, nur Dauer zählt
    expected = W1 * 8
    assert robustness_score(journey) == pytest.approx(expected)


def test_empty_journey_returns_9001():
    """Journey ohne Connections → journey_time = 9001"""
    stop_a = make_stop("A")
    stop_b = make_stop("B")
    journey = Journey(start=stop_a, end=stop_b, start_time=BASE_TIME)
    assert journey.journey_time == 9001


def test_higher_transfer_risk_with_tight_connection():
    """Knappes Umstiegsfenster (1 Min) muss schlechter sein als großzügiges (10 Min)"""
    stop_a = make_stop("A", "900000001")
    stop_b = make_stop("B", "900000002")
    stop_c = make_stop("C", "900000003")

    def make_journey(buffer_minutes: int) -> Journey:
        conn1 = make_connection(stop_a, stop_b, BASE_TIME, 5,
                                transport_id="S1", name="S1")
        conn2 = make_connection(stop_b, stop_c,
                                BASE_TIME + timedelta(minutes=5 + buffer_minutes), 5,
                                transport_id="U8", name="U8")
        return Journey(start=stop_a, end=stop_c,
                       start_time=BASE_TIME, connections=[conn1, conn2])

    tight   = make_journey(1)
    relaxed = make_journey(10)
    assert robustness_score(tight) > robustness_score(relaxed)