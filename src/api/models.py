from dataclasses import dataclass, field
from datetime import datetime
@dataclass
class Stop:
    #Jeder Stop erhält Floats für latitude und longitude sowie eine Liste der Verkehrsmittel die dort halten
    name: str
    latitude: float 
    longitude: float
    transportations: list = field(default_factory=list)

@dataclass 
class Connection:
    #Jede Connection zwischen zwei Stops erhält Start und Ziel, Abfahrts- und Ankunftszeit und das verbindene Transportmittel
    start: Stop
    end: Stop
    start_time: datetime
    end_time: datetime
    transport_id: str 
    planned_departure: datetime
    planned_arrival: datetime

    @property
    def duration(self) -> int:
        return int((self.end_time-self.start_time).total_seconds() /60)

    @property
    def delay(self) -> int:
        #Verspätung in Minuten
        return int((self.start_time-self.planned_departure).total_seconds()/60)

@dataclass
class Journey:
    start: Stop
    end: Stop
    start_time: datetime
    connections: list = field(default_factory=list)
        
    @property
    def journey_time(self) -> int:
        #Differenz von Ankunftszeit der letzten Connection und Startzeit der ersten Connection
        if len(self.connections)>0:
            return int((self.connections[-1].end_time - self.connections[0].start_time).total_seconds() /60)
        else:
            #"It's over niiiine thousand!"
            return 9001

    @property
    def num_transfers(self) -> int:
        #Anzahl Connections minus one
        return max(len(self.connections)-1,0)
    
    @property
    def end_time(self) -> datetime:
        if len(self.connections)>0:
            return self.connections[-1].end_time
        return self.start_time