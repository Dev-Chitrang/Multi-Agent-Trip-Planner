from crewai.tools import BaseTool
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()
os.environ['SERP_API_KEY'] = os.getenv('SERPAPI_KEY')

# Airport code mapping
AIRPORT_CODES = {
    # Major Indian Cities
    "mumbai": "BOM",
    "delhi": "DEL",
    "bangalore": "BLR",
    "bengaluru": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "ahmedabad": "AMD",
    "goa": "GOI",
    "jaipur": "JAI",
    "lucknow": "LKO",
    "kochi": "COK",
    "cochin": "COK",
    "guwahati": "GAU",
    "chandigarh": "IXC",
    "trivandrum": "TRV",
    "thiruvananthapuram": "TRV",
    "bhubaneswar": "BBI",
    "indore": "IDR",
    "coimbatore": "CJB",
    "nagpur": "NAG",
    "vadodara": "BDQ",
    "visakhapatnam": "VTZ",
    "patna": "PAT",
    "srinagar": "SXR",
    "amritsar": "ATQ",
    "udaipur": "UDR",
    "varanasi": "VNS",
    "bhopal": "BHO",
    "raipur": "RPR",
    "ranchi": "IXR",

    # International Cities (common)
    "dubai": "DXB",
    "singapore": "SIN",
    "bangkok": "BKK",
    "london": "LHR",
    "new york": "JFK",
    "paris": "CDG",
    "hong kong": "HKG",
    "tokyo": "NRT",
    "kuala lumpur": "KUL",
    "istanbul": "IST",
    "doha": "DOH",
}


class FlightSearchTool(BaseTool):
    name: str = "Flight Search Tool"
    description: str = "Search flights between two cities using SerpAPI. Requires source, destination, departure_date, and return_date (all as strings)."

    def _run(self, source: str, destination: str, departure_date: str, return_date: str) -> str:
        """
        Search for flights using SerpAPI Google Flights engine
        """
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            return "SerpAPI key not provided"

        try:
            # Convert city names to airport codes
            source_code = AIRPORT_CODES.get(source.lower(), source.upper()[:3])
            dest_code = AIRPORT_CODES.get(destination.lower(), destination.upper()[:3])

            print(f"Searching flights: {source} ({source_code}) -> {destination} ({dest_code})")

            params = {
                "engine": "google_flights",
                "departure_id": source_code,
                "arrival_id": dest_code,
                "outbound_date": departure_date,
                "return_date": return_date,
                "currency": "INR",
                "hl": "en",
                "api_key": serpapi_key
            }

            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            res = response.json()

            # Check for errors
            if "error" in res:
                return f"API Error: {res['error']}"

            flights = []

            # Try to get best flights first
            if "best_flights" in res and res["best_flights"]:
                for flight in res["best_flights"][:3]:
                    flight_info = self._extract_flight_info(flight)
                    if flight_info:
                        flights.append(flight_info)

            # If no best flights, try other flights
            if not flights and "other_flights" in res and res["other_flights"]:
                for flight in res["other_flights"][:3]:
                    flight_info = self._extract_flight_info(flight)
                    if flight_info:
                        flights.append(flight_info)

            if flights:
                return json.dumps(flights, indent=2)
            else:
                return json.dumps({
                    "message": "No flights found for the specified route and dates",
                    "suggestion": "Try different dates or check if the airport codes are correct",
                    "searched_route": f"{source_code} to {dest_code}"
                })

        except Exception as e:
            return f"Error searching flights: {str(e)}"

    def _extract_flight_info(self, flight):
        """Extract flight information from SerpAPI response"""
        try:
            # Get the first leg of the flight
            flights_data = flight.get("flights", [])
            if not flights_data:
                return None

            first_flight = flights_data[0]

            return {
                "airline": first_flight.get("airline", "Unknown"),
                "flight_number": first_flight.get("flight_number", "N/A"),
                "departure_time": first_flight.get("departure_airport", {}).get("time", "N/A"),
                "arrival_time": first_flight.get("arrival_airport", {}).get("time", "N/A"),
                "departure_airport": first_flight.get("departure_airport", {}).get("name", "N/A"),
                "arrival_airport": first_flight.get("arrival_airport", {}).get("name", "N/A"),
                "price": flight.get("price", "N/A"),
                "duration": flight.get("total_duration", "N/A"),
                "stops": len(flights_data) - 1,
                "type": flight.get("type", "Regular")
            }
        except Exception as e:
            print(f"Error extracting flight info: {e}")
            return None


class HotelSearchTool(BaseTool):
    name: str = "Hotel Search Tool"
    description: str = "Search hotels in destination using SerpAPI"

    def _run(self, destination: str, check_in: str, check_out: str) -> str:
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            return "SerpAPI key not provided"
        try:
            params = {
                "engine": "google_hotels",
                "q": f"hotels in {destination}",
                "check_in_date": check_in,
                "check_out_date": check_out,
                "currency": "INR",
                "api_key": serpapi_key
            }
            res = requests.get("https://serpapi.com/search", params=params, timeout=30).json()

            hotels = []
            for hotel in res.get("properties", [])[:5]:  # Get top 5 hotels
                # Calculate total stay cost
                price_per_night = hotel.get("rate_per_night", {}).get("lowest", "N/A")

                # Try to parse price and calculate total
                total_cost = "N/A"
                if price_per_night != "N/A" and isinstance(price_per_night, str):
                    try:
                        # Remove ₹ symbol and comma, convert to int
                        price_num = int(price_per_night.replace("₹", "").replace(",", ""))
                        # Calculate nights
                        from datetime import datetime
                        check_in_dt = datetime.strptime(check_in, "%Y-%m-%d")
                        check_out_dt = datetime.strptime(check_out, "%Y-%m-%d")
                        nights = (check_out_dt - check_in_dt).days
                        total_cost = f"₹{price_num * nights:,}"
                    except:
                        pass

                hotels.append({
                    "name": hotel.get("name", "Unknown"),
                    "rating": str(hotel.get("overall_rating", "N/A")),
                    "price_per_night": price_per_night,
                    "total_cost": total_cost,
                    "location": hotel.get("location", hotel.get("gps_coordinates", {}).get("latitude", "N/A")),
                    "amenities": ", ".join(hotel.get("amenities", [])[:3]) if hotel.get("amenities") else "N/A"
                })

            return json.dumps(hotels, indent=2) if hotels else "No hotels found"
        except Exception as e:
            return f"Error searching hotels: {str(e)}"


class AttractionSearchTool(BaseTool):
    name: str = "Attraction Search Tool"
    description: str = "Search attractions using SerpAPI"

    def _run(self, destination: str, interests: str) -> str:
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            return "SerpAPI key not provided"
        try:
            params = {
                "engine": "google",
                "q": f"best {interests} places in {destination} attractions",
                "location": destination,
                "api_key": serpapi_key
            }
            res = requests.get("https://serpapi.com/search", params=params, timeout=30).json()
            attractions = []
            for r in res.get("organic_results", [])[:5]:
                attractions.append({
                    "title": r.get("title", "Unknown"),
                    "snippet": r.get("snippet", "No description"),
                    "link": r.get("link", "")
                })
            return json.dumps(attractions, indent=2)
        except Exception as e:
            return f"Error searching attractions: {str(e)}"


# Initialize tool instances
flight_tool = FlightSearchTool()
hotel_tool = HotelSearchTool()
attraction_tool = AttractionSearchTool()
