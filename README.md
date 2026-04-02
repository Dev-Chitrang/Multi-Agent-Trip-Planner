# AI Multi-Agent Trip Planner

## Overview
This system is an automated travel planning pipeline that uses multiple AI agents to search for flights, hotels, and generate a daily itinerary. It is a multi-agent AI system built to handle real-time data retrieval and structured plan generation based on user constraints like budget, dates, and interests.

## Architecture
The system follows a multi-agent orchestration pattern using the crewAI framework.

- **Components**:
  - **Agents**: Specialized agents for flights, hotels, and itinerary planning.
  - **Tools**: Custom Python tools that interface with SerpAPI (Google Flights, Google Hotels, and Google Search).
  - **LLM**: Google Gemini 2.0 Flash-Exp for reasoning and natural language generation.
  - **UI**: Streamlit-based web interface for user input and result visualization.
- **Data Flow**:
  1. User inputs (source, destination, dates, budget, interests) are captured via Streamlit.
  2. The `Flight Specialist` agent uses the `FlightSearchTool` to retrieve real-time flight options.
  3. The `Hotel Specialist` agent uses the `HotelSearchTool` to find accommodation within the specified budget.
  4. The `Travel Planner` agent consumes the output of the previous two agents and uses the `AttractionSearchTool` to build a day-by-day itinerary.
  5. The final plan is presented to the user.

## Key Engineering Decisions
- **Sequential Task Execution**: Tasks are executed in a fixed sequence (Flight -> Hotel -> Itinerary) to ensure downstream agents have the necessary context (e.g., arrival/departure times) to build a realistic timeline.
- **Real-time Data Retrieval**: The system uses SerpAPI to fetch live travel data instead of relying on static training data, ensuring accuracy for pricing and availability.
- **Static Airport Code Mapping**: A dictionary-based mapping for major cities to IATA codes was implemented in `tools.py` to improve the reliability of the Google Flights engine searches.
- **Agent Backstory and Constraints**: Agents are configured with specific "backstories" and constraints (e.g., `max_iter=3`) to prevent infinite loops while ensuring they find relevant data.

## Features
- **Real-time Flight Search**: Retrieves airline, flight number, departure/arrival times, and pricing in INR.
- **Budget-Filtered Hotel Search**: Filters hotels based on a per-night cost derived from the total hotel budget and trip duration.
- **Automated Itinerary Generation**: Creates a day-by-day timeline including travel days, morning/afternoon/evening activities, and estimated costs.
- **Rate Limit Management**: Includes a cooldown mechanism to handle SerpAPI's free tier limitations.

## Tech Stack
- **Backend**: Python 3.10+
- **Agent Framework**: crewAI
- **LLM**: Google Gemini 2.0 Flash-Exp
- **Data APIs**: SerpAPI (Google Flights, Google Hotels, Google Search)
- **UI**: Streamlit

## Workflow / API
The system operates internally as a directed acyclic graph (DAG) of tasks:
1. `flight_task`: Executes a search via `FlightSearchTool` using `source`, `destination`, `start_date`, and `end_date`.
2. `hotel_task`: Executes a search via `HotelSearchTool` using `destination`, `start_date`, and `end_date`.
3. `itinerary_task`: Aggregates the results of the first two tasks and performs a search for points of interest via `AttractionSearchTool`.

## Challenges & Solutions
- **API Rate Limiting**: SerpAPI's free tier has strict limits. This was addressed by implementing a 120-second cooldown in the Streamlit UI and reducing the number of concurrent tool calls.
- **Geographic Ambiguity**: Searching for flights by city name can be unreliable. The solution was to implement an `AIRPORT_CODES` mapping in `tools.py` to ensure the API receives valid IATA codes.
- **Itinerary Realism**: Initial versions generated activities without considering travel time. The `itinerary_agent` backstory was updated to explicitly prioritize travel logistics (departure/arrival) on travel days.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in a `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   SERPAPI_KEY=your_serpapi_key
   ```
3. Launch the application:
   ```bash
   streamlit run app.py
   ```
