# 🧭 AI Trip Planner — Powered by CrewAI, Gemini, and SerpAPI 🌍

An **AI-powered travel planning assistant** that automatically creates your **complete trip itinerary** — including **flights, hotels, and day-by-day activities** — using multiple specialized agents working together.

Built with **CrewAI**, **Gemini LLM**, and **SerpAPI**, and deployed as a beautiful **Streamlit web app**.

---

## 🚀 Features

✅ **AI-Powered Multi-Agent Workflow**
- Uses **CrewAI** to coordinate multiple intelligent agents:
  - ✈️ `Flight Specialist` → Finds the best flight options
  - 🏨 `Hotel Specialist` → Recommends top hotels within budget
  - 📅 `Itinerary Planner` → Builds a realistic day-by-day itinerary

✅ **Real-Time Data via SerpAPI**
- Fetches **live flight and hotel results** using the **Google Flights** and **Google Hotels** SerpAPI engines.

✅ **Gemini LLM Integration**
- Uses Google’s **Gemini 2.0 Flash model** to intelligently reason, summarize, and generate itineraries.

✅ **Beautiful Streamlit Dashboard**
- User-friendly interface with:
  - Trip inputs (source, destination, dates, budgets)
  - Interest selection (sightseeing, food, adventure, etc.)
  - Real-time progress bar
  - Cooldown handling for API limits
  - Downloadable trip plan text file

✅ **Budget Breakdown**
- Separate budget inputs for flights, hotels, and other expenses.
- Clear summary: `X days (Y nights)` duration display.

✅ **Smart Itinerary Generation**
- Includes realistic **departure and return travel days**.
- Avoids unrealistic early-morning arrivals.
- Balanced daily activities with estimated costs.

---

## 🧩 Tech Stack

| Component                  | Technology                                                       |
|----------------------------|------------------------------------------------------------------|
| **Frontend**               | [Streamlit](https://streamlit.io/)                               |
| **AI Engine**              | [CrewAI](https://github.com/joaomdmoura/crewai)                  |
| **Language Model**         | [Gemini 2.0 Flash](https://ai.google.dev/gemini-api/docs/models) |
| **Data Sources**           | [SerpAPI](https://serpapi.com/) (Google Flights + Hotels)        |
| **Environment Management** | `dotenv`                                                         |
| **Language**               | Python 3.10+                                                     |

---

## 🧠 Project Architecture

📦 ai-trip-planner
├── app.py # Streamlit UI
├── agents.py # Agent definitions (Flight, Hotel, Itinerary)
├── tasks.py # CrewAI tasks for each agent
├── tools.py # SerpAPI integration tools
├── crew.py # Crew definition and kickoff logic
├── .env # API keys
└── requirements.txt # Dependencies



### 🔹 Agent Overview
| Agent               | Goal                                | Tool Used            |
|---------------------|-------------------------------------|----------------------|
| `Flight Specialist` | Find best flights within budget     | FlightSearchTool     |
| `Hotel Specialist`  | Recommend best hotels within budget | HotelSearchTool      |
| `Travel Planner`    | Build detailed day-by-day itinerary | AttractionSearchTool |

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Dev-Chitrang/AICTE-AI-CLOUD.git
cd ai-trip-planner

### 2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # for Mac/Linux
venv\Scripts\activate      # for Windows

### 3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure API Keys

Create a .env file in the root directory with:

GOOGLE_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here

🧠 How It Works

User inputs trip details (source, destination, dates, budgets, and interests).
CrewAI sequentially activates:
Flight agent → fetches flights
Hotel agent → fetches hotels
Itinerary agent → generates a realistic itinerary
Streamlit app displays all results neatly:
Flights ✈️
Hotels 🏨
Day-by-Day Itinerary 📅
User can download the complete plan as a .txt file.


🖥️ Running the App
Start the Streamlit app:
streamlit run app.py

Then open in your browser:
http://localhost:8501
