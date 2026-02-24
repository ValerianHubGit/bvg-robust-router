import streamlit as st
from datetime import datetime, timedelta
from src.api.bvg_client import get_stops
from src.graph.router import find_robust_journeys

st.title("🚇 BVG Robust Router")
st.subheader("Nicht die schnellste – die zuverlässigste Verbindung")

start_query = st.text_input("Starthaltestelle")
end_query = st.text_input("Zielhaltestelle")

#Abfahrtszeitpunkt bestimmen - Jetzt oder per Dropdown in Zukunft, biete Option alle 5-Minuten
now = datetime.now()
time_options = {"Jetzt": now}
for i in range(5, 121, 5):
    t = now + timedelta(minutes=i)
    time_options[f"in {i} Min ({t.strftime('%H:%M')})"] = t

#setze den Abfahrtszeitpunkt auf die Auswahl des Menüpunkts
selected_label = st.selectbox("Abfahrtszeit", list(time_options.keys()))
when = time_options[selected_label]


if st.button("Verbindungen suchen"):
    # 1. get_stops(start_query/end_query) aufrufe, beide stops gefunden?
    with st.spinner("Suche läuft..."):        
        start=get_stops(start_query)
        end=get_stops(end_query)
    if start and end:
       with st.spinner("Verbindungen werden bewertet"):
            # 4. find_robust_journeys() aufrufen, erhalte sortiert Verbindungen und Score
            sorted_journey_list, robustness_scores = find_robust_journeys(start_query,end_query, when)
        # 5. st.write() um Ergebnisse anzuzeigen, ausklappbar für Zeiten
            for i, (journey, score) in enumerate(zip(sorted_journey_list, robustness_scores)):
                with st.expander(f"Verbindung {i+1} – Score: {score:.1f} | {journey.journey_time} Min | {journey.num_transfers} Umstiege"):
                    for conn in journey.connections:
                        #Textanpassungen zu Fußwegen
                        if conn.name=="Fußweg":
                            if conn.start.name != conn.end.name:
                                st.write(f"{conn.name}: {conn.start.name} → {conn.end.name}")
                                st.write(f"Start: {conn.start_time.strftime('%H:%M')} | Ankunft: {conn.end_time.strftime('%H:%M')}")
                                st.divider()       
                        else:   
                            st.write(f"🚉 {conn.name} Richtung {conn.direction}: {conn.start.name} → {conn.end.name}")
                            st.write(f"   Abfahrt: {conn.start_time.strftime('%H:%M')} | Ankunft: {conn.end_time.strftime('%H:%M')} | Verspätung: {conn.delay} Min")
                            st.divider()       
    else:
        st.error("Haltestellen nicht gefunden - bitte erneut versuchen.")
