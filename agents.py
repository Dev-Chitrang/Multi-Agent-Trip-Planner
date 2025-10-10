from crewai import Agent, LLM
from dotenv import load_dotenv
import os
from tools import flight_tool, hotel_tool, attraction_tool

load_dotenv()

# Configure LLM with minimal settings
llm = LLM(
    model="gemini/gemini-2.0-flash-exp",
    temperature=0.1,
    api_key=os.getenv("GOOGLE_API_KEY"),
)

flight_agent = Agent(
    role='Flight Specialist',
    goal='Find the best flight options from {source} to {destination}',
    verbose=True,  # Changed to True for debugging
    memory=False,
    backstory="You are an expert at finding the best flight options. You search for flights and present them clearly.",
    tools=[flight_tool],
    llm=llm,
    allow_delegation=False,
    max_iter=3,  # Increased from 1 to 3
    max_rpm=None,  # Remove rate limiting from agent level
)

hotel_agent = Agent(
    role='Hotel Specialist',
    goal='Find the best hotel options in {destination}',
    verbose=True,  # Changed to True for debugging
    memory=False,
    backstory="You are an expert at finding quality hotels that match the budget. You search for hotels and present them clearly.",
    tools=[hotel_tool],
    llm=llm,
    allow_delegation=False,
    max_iter=3,  # Increased from 1 to 3
    max_rpm=None,  # Remove rate limiting from agent level
)

itinerary_agent = Agent(
    role="Travel Planner",
    goal=(
        "Create a realistic, human-friendly travel itinerary for a trip from {source} to {destination}. "
        "Include travel details like flight departure and arrival on the first and last days. "
        "Ensure the itinerary starts with the traveler leaving {source} and ends with returning home or departing {destination}."
    ),
    verbose=True,
    memory=False,
    backstory=(
        "You are an expert travel planner who creates practical, real-world itineraries. "
        "Always include realistic travel times and transitions between locations. "
        "Start the itinerary with the journey from the source city to the destination, not just activities. "
        "Ensure morning flights are planned realistically (e.g., not 5 AM arrivals unless explicitly possible)."
    ),
    tools=[attraction_tool],
    llm=llm,
    allow_delegation=False,
    max_iter=3,
    max_rpm=None,
)

