import requests
from datetime import datetime
from src.api.models import Stop, Connection, Journey

BASE_URL = "https://v6.bvg.transport.rest"

def get_stops(query: str) -> list[Stop]:
    try:                                                    #do we get data?
        response = requests.get(f"{BASE_URL}/locations",
                                params={"query": query, "results": 5},
                                timeout=10)
        response.raise_for_status()       
    except requests.exceptions.ConnectionError:
        print("Keine Verbindung zur BVG-API")
        return []
    except requests.exceptions.Timeout:
        print("BVG-API antwortet nicht")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Fehler: {e}")
        return []

    stops = []
    for item in response.json():
        if item["type"] != "stop":
            continue
        
        transportations = [product for product, active in item["products"].items()  if active]
        
        stop = Stop(name=item["name"],
                    latitude=item["location"]["latitude"],
                    longitude=item["location"]["longitude"],
                    id= item["id"],
                    transportations=transportations
                    )
       
        stops.append(stop)
    
    return stops

def get_journeys(from_id: str, to_id: str ) -> list[Journey]:
    try:                                                    #do we get data?
        response = requests.get(f"{BASE_URL}/journeys",
                                params={"from": from_id, "to": to_id, "results": 5},
                                timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return []
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Fehler: {e}")
        return []
    
    journeys = []
    for journey_data in response.json()["journeys"]:
        connections = []
        for leg in journey_data["legs"]:
            #Wir sortieren direkt jene Legs ohne Zeinangaben aus
            if not leg.get("departure") or not leg.get("arrival"):
                    continue
            #start und end als Stop-Objekte aus leg["origin"] und leg["destination"] bauen  
            transportations_start = [product for product, active in leg["origin"]["products"].items()  if active]
            start_stop=Stop(
                name=leg["origin"]["name"],
                latitude=leg["origin"]["location"]["latitude"],
                longitude=leg["origin"]["location"]["longitude"],
                id=leg["origin"]["id"],
                transportations=transportations_start)
            
            transportations_end = [product for product, active in leg["destination"]["products"].items()  if active]
            end_stop=Stop(
                name=leg["destination"]["name"],
                latitude=leg["destination"]["location"]["latitude"],
                longitude=leg["destination"]["location"]["longitude"],
                id=leg["destination"]["id"],
                transportations=transportations_end)
                        
            #Aus Legs alles auslesen + jene ohne tripID als Fußweg markieren                              
            start_time=datetime.fromisoformat(leg["departure"])
            end_time=datetime.fromisoformat(leg["arrival"])
            planned_departure= datetime.fromisoformat(leg["plannedDeparture"])
            planned_arrival= datetime.fromisoformat(leg["plannedArrival"])
            if not leg.get("tripId"):
                transport_id="walking"
                line_name="Fußweg"
                direction_name=leg["destination"]["name"]    
            else:
                transport_id=leg["tripId"]
                direction_name=leg["direction"]
                line_name=leg["line"]["name"]
            #Connection-Objekt bauen und connections.append() aufrufen
            connection=Connection(
                start= start_stop,
                end= end_stop,
                start_time= start_time,
                end_time= end_time,
                transport_id= transport_id,
                planned_departure= planned_departure,
                planned_arrival= planned_arrival,
                name=line_name,
                direction=direction_name)
            
            connections.append(connection)     

        # Journey-Objekt aus connections bauen und journeys.append() aufrufen
        journey=Journey(
            start=connections[0].start, 
            end=connections[-1].end,
            start_time=connections[0].start_time,
            connections= connections)
        journeys.append(journey)
    return journeys