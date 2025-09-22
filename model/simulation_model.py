from itertools import chain
from geographiclib.geodesic import Geodesic

geod = Geodesic.WGS84

class SimulationManager:
    def __init__(self):
        self.fire_incidents = []
        self.fire_trucks = []

    def add_fire_incident(self, lat: float, lon: float):
        uid = f"fire-incident-{len(self.fire_incidents) + 1}"
        new_fire = FireIncident(uid=uid, lat=lat, lon=lon)
        self.fire_incidents.append(new_fire)
        # print(new_fire.uid)
        return new_fire

    def add_fire_truck(self, lat: float, lon: float):
        uid = f"fire-truck-{len(self.fire_trucks) + 1}"
        new_truck = FireTruck(uid=uid, lat=lat, lon=lon)
        self.fire_trucks.append(new_truck)
        # print(new_truck.uid)
        return new_truck
        
    def update_positions(self):
        """ update the positions of all movable markers """
        for truck in self.fire_trucks:
            truck.update_position()
            

    def all_markers(self):
        return chain(self.fire_incidents, self.fire_trucks)

    def get_marker_by_uid(self, uid: str):
        for marker in self.all_markers():
            if marker.uid == uid:
                return marker
        return None



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
        self.route = [] # list of (lat, lon)
        self.current_step = 0
        self.speed_m_per_s = 100 # speed in meters per second

    def set_route(self, route: list):
        self.route = route
        self.current_step = 0

    def update_position(self):
        """ Move fire_truck one step along its route """
        if not self.route or self.current_step >= len(self.route) - 1:
            return # no route OR reached the end
        
        start_lat, start_lon = self.lat, self.lon # start point
        target_lat, target_lon = self.route[self.current_step + 1] # next step

        # Calculate distance and azimuth to the next point
        result = geod.Inverse(start_lat, start_lon, target_lat, target_lon)
        distance_to_target = result['s12'] # in meters
        azimuth_to_target = result['azi1'] # in degrees

        if distance_to_target <= self.speed_m_per_s:
            # If within one step, move directly to the target point
            self.lat, self.lon = target_lat, target_lon
            self.current_step += 1
        else:
            # Move towards the target point by speed_m_per_s
            new_position = geod.Direct(start_lat, start_lon, azimuth_to_target, self.speed_m_per_s)
            self.lat, self.lon = new_position['lat2'], new_position['lon2']

    


