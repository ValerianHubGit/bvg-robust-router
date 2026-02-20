import streamlit as st
from src.api.bvg_client import get_stops
from src.graph.router import find_robust_journeys
from src.graph.robustness import robustness_score

st.title("🚇 BVG Robust Router")
st.subheader("Nicht die schnellste – die zuverlässigste Verbindung")

start_query = st.text_input("Starthaltestellte")
end_query = st.text_input("Zielhaltestelle")

if st.button("Verbindungen suchen"):
    # 1. get_stops(start_query/end_query) aufrufe, beide stops gefunden?
    with st.spinner("Suche läuft..."):        
        start=get_stops(start_query)
        end=get_stops(end_query)
    if start and end:
       with st.spinner("Verbindungen werden bewertet"):
            # 4. find_robust_journeys() aufrufen
            sorted_journey_list, robustness_scores = find_robust_journeys(start_query,end_query)
        # 5. st.write() um Ergebnisse anzuzeigen
            for i, (journey, score) in enumerate(zip(sorted_journey_list, robustness_scores)):
                with st.expander(f"Verbindung {i+1} – Score: {score:.1f} | {journey.journey_time} Min | {journey.num_transfers} Umstiege"):
                    for conn in journey.connections:
                        st.write(f"🚉 {conn.name} Richtung {conn.direction}: {conn.start.name} → {conn.end.name}")
                        st.write(f"   Abfahrt: {conn.start_time.strftime('%H:%M')} | Ankunft: {conn.end_time.strftime('%H:%M')} | Verspätung: {conn.delay} Min")
                        st.divider()       
    else:
        st.error("Haltestellen nicht gefunden - bitte erneut versuchen.")
