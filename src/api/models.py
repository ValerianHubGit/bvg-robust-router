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

    @property
    def duration(self) -> int:
        return int((self.end_time-self.start_time).total_seconds() /60)

@dataclass
class Journey:
    start: Stop
    end: Stop
    start_time: datetime
    
    @property
    def connections -> list = field(default_factory=list):
        #To be determined ordered list of Connection-type objects which ultimately connect, efficient or not, self.start and self.end
        pass
    
    @property
    def journey_time -> int:
        #Differenz von Ankunftszeit der letzten Connection und Startzeit der ersten Connection
        if len(self.connections)>0:
            return int((self.connections[-1].end_time - self.connections[0].start_time).total_seconds() /60)
        else:
            #"It's over niiiine thousand!"
            return 9001

