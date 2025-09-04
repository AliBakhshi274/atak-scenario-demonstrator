from itertools import chain

class SimulationManager:
    def __init__(self):
        self.fire_incidents = []
        self.fire_trucks = []

    def add_fire_incident(self, lat: float, lon: float):
        uid = f"fire-incident-{len(self.fire_incidents) + 1}"
        new_fire = FireIncident(uid=uid, lat=lat, lon=lon)
        self.fire_incidents.append(new_fire)
        return new_fire

    def add_fire_truck(self, lat: float, lon: float):
        uid = f"fire-truck-{len(self.fire_trucks) + 1}"
        new_truck = FireTruck(uid=uid, lat=lat, lon=lon)
        self.fire_trucks.append(new_truck)
        return new_truck
        
    def update_positions(self):
        pass

    def all_markers(self):
        return chain(self.fire_incidents, self.fire_trucks)




class Marker:
    def __init__(self, uid: str, marker_type: str, lat: float, lon: float):
        self.uid = uid
        self.type = marker_type
        self.lat = lat
        self.lon = lon

class FireIncident(Marker):
    def __init__(self, uid, lat, lon):
        super().__init__(uid, "a-h-A-M-A", lat, lon)

class FireTruck(Marker):
    def __init__(self, uid, lat, lon):
        super().__init__(uid, "a-.-G-E-V", lat, lon)

