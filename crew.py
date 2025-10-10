from crewai import Crew, Process
from tasks import flight_task, hotel_task, itinerary_task
from agents import flight_agent, hotel_agent, itinerary_agent

crew = Crew(
    agents=[flight_agent, hotel_agent, itinerary_agent],
    tasks=[flight_task, hotel_task, itinerary_task],
    process=Process.sequential,

)

inputs = {
    "source": "Mumbai",
    "destination": "Goa",
    "start_date": "2025-11-01",
    "end_date": "2025-11-05",
    "budget": 50000,
    "interests": "Sightseeing, Food & Dining"
}

result = crew.kickoff(inputs=inputs)
print(result)
