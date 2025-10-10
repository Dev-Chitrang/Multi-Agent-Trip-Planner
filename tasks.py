from crewai import Task
from tools import flight_tool, hotel_tool, attraction_tool
from agents import flight_agent, hotel_agent, itinerary_agent

flight_task = Task(
    description=(
        "Search for flights from {source} to {destination}. "
        "Departure date: {start_date}, Return date: {end_date}. "
        "Flight budget constraint: {flight_budget} INR (this is ONLY for flights). "
        "Use the Flight Search Tool with ALL required parameters: source, destination, departure_date, and return_date. "
        "IMPORTANT: Always provide return_date as a string, never as None or null."
    ),
    expected_output=(
        "A clear, formatted list of flight options with:\n"
        "For each flight:\n"
        "- Airline name and flight number\n"
        "- Departure time and airport\n"
        "- Arrival time and airport\n"
        "- Price in INR\n"
        "- Flight duration\n"
        "- Number of stops\n\n"
        "Format the output clearly. If no flights are found, provide alternative suggestions or explain why."
    ),
    tools=[flight_tool],
    agent=flight_agent,
)

hotel_task = Task(
    description=(
        "Search for hotels in {destination}. "
        "Check-in: {start_date}, Check-out: {end_date}. "
        "Hotel budget constraint: {hotel_budget} INR (this is ONLY for hotels). "
        "Use the Hotel Search Tool to find available hotel options within this budget. "
        "Calculate the total cost for the entire stay based on number of nights."
    ),
    expected_output=(
        "A clear, formatted list of hotel options with:\n"
        "For each hotel:\n"
        "- Hotel name\n"
        "- Star rating (as number)\n"
        "- Price per night in INR\n"
        "- Total cost for the entire stay\n"
        "- Location/Area\n"
        "- Key amenities (if available)\n\n"
        "Present the information in a structured format that's easy to read. "
        "Highlight which hotels fit within the budget."
    ),
    tools=[hotel_tool],
    agent=hotel_agent
)

itinerary_task = Task(
    description=(
        "Plan a day-by-day itinerary for a trip from {source} to {destination} "
        "between {start_date} and {end_date}. "
        "Use the flight and hotel information found earlier to create a realistic timeline. "
        "Start with the journey from {source} (departure details) and end with the return journey. "
        "Ensure timing and costs are realistic within a total other budget of {other_budget} INR."
    ),
    expected_output=(
        "A well-structured daily itinerary including:\n"
        "- Travel departure and arrival times\n"
        "- Morning, Afternoon, and Evening plans per day\n"
        "- Estimated costs for each activity\n"
        "- Clear labeling of travel days\n"
        "Example:\n"
        "Pre-Trip: Depart from Mumbai (Evening Flight)\n"
        "Day 1: Arrival + Local sightseeing\n"
        "Day 2–3: Activities\n"
        "Day 4: Departure from Goa\n"
        "Total daily cost summary at the end."
    ),
    tools=[attraction_tool],
    agent=itinerary_agent
)

