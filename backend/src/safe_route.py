import requests, os
from dotenv import load_dotenv
from src.utils.exception import customException
from src.database.supabase_config import Supabase

supa_client=Supabase()
HIGH_RISK_ZONES=[]
load_dotenv()

class OpenRouteService:
    def __init__(self):
        self.api_key = os.getenv("ORS_API_KEY")

    # Helper function to calculate the safest route
    def get_safest_route(self, start_coords, end_coords):
        """
        Calculate route from start to end while avoiding high-risk areas.
        """
        try:
            url = f"https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {"Authorization": self.api_key}
            params = {
                "start": f"{start_coords[1]},{start_coords[0]}",  # lon, lat
                "end": f"{end_coords[1]},{end_coords[0]}",
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            route = response.json()

            # Analyze and remove high-risk waypoints from the route
            safe_route = self.filter_safe_route(route["features"][0]["geometry"]["coordinates"])

            return safe_route

        except requests.exceptions.RequestException as e:
            raise customException(e)

    def filter_safe_route(self, coordinates):
        """
        Filters out route coordinates that fall within high-risk zones.
        """
        safe_coords = []
        self.get_high_risk_zones()
        for coord in coordinates:
            if not self.is_in_high_risk_zone(coord):
                safe_coords.append(coord)
        return safe_coords

    def is_in_high_risk_zone(self,coord):
        """
        Check if a coordinate falls within any high-risk zone.
        """
        for zone in HIGH_RISK_ZONES:
            if (abs(zone["lon"] - coord[0]) < 0.01) and (abs(zone["lat"] - coord[1]) < 0.01):
                return True
        return False
    
    def get_high_risk_zones(self):
        """
        Converts a list of high-risk area data into the required HIGH_RISK_ZONES format.
        """
        data=supa_client.get_geofence()
        for item in data:
            HIGH_RISK_ZONES.append({
                "lon": item['center_long'],
                "lat": item['center_lat']
            })

if __name__=="__main__":
    ors=OpenRouteService()
    a = (12.8150, 80.1600)
    b = (12.9400, 80.1300)
    res=ors.get_safest_route(a,b)
    print(res)
