import streamlit as st
from crewai import Crew, Process
from tasks import flight_task, hotel_task, itinerary_task
from agents import flight_agent, hotel_agent, itinerary_agent
from datetime import datetime, timedelta
import json
import time

# Page configuration
st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E3F2FD;
        border-left: 5px solid #1E88E5;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #FFF3E0;
        border-left: 5px solid #FF9800;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F5E9;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .result-section {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #F5F5F5;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565C0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">✈️ AI Travel Planner 🏖️</div>', unsafe_allow_html=True)
st.markdown("### Plan your perfect trip with AI-powered recommendations!")

# Rate limit warning
st.markdown('<div class="warning-box">', unsafe_allow_html=True)
st.write("⚠️ **Important:** This app uses free API tier with limits:")
st.write("- Maximum 10 API requests per minute")
st.write("- **Wait at least 120 seconds between searches**")
st.write("- Select maximum 1-2 interests to reduce API calls")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = None
if 'flight_results' not in st.session_state:
    st.session_state.flight_results = None
if 'hotel_results' not in st.session_state:
    st.session_state.hotel_results = None
if 'itinerary_results' not in st.session_state:
    st.session_state.itinerary_results = None

# Show cooldown timer at the top if needed
if st.session_state.last_request_time:
    elapsed = time.time() - st.session_state.last_request_time
    remaining = max(0, 120 - elapsed)
    if remaining > 0:
        st.warning(f"⏳ Please wait **{int(remaining)} seconds** before next search to avoid rate limits")

st.divider()

# Main input form in center
st.markdown("## 🎯 Enter Your Trip Details")

col1, col2 = st.columns(2)

with col1:
    source = st.text_input(
        "📍 From (Source City)",
        placeholder="e.g., Mumbai",
        value="Mumbai",
        help="Enter the city you're traveling from"
    )

with col2:
    destination = st.text_input(
        "📍 To (Destination City)",
        placeholder="e.g., Goa",
        value="Goa",
        help="Enter your destination city"
    )

# Date inputs
st.markdown("### 🗓️ Travel Dates")
col1, col2 = st.columns(2)

# Calculate safe default dates
today = datetime.now().date()
default_start = today + timedelta(days=30)
default_end = default_start + timedelta(days=3)

with col1:
    start_date = st.date_input(
        "Start Date",
        value=default_start,
        min_value=today,
        max_value=today + timedelta(days=365),
        help="Select your departure date"
    )

with col2:
    # Ensure end_date min is after start_date
    min_end_date = start_date + timedelta(days=1) if start_date else default_end
    end_date = st.date_input(
        "End Date",
        value=max(default_end, min_end_date),
        min_value=min_end_date,
        max_value=today + timedelta(days=365),
        help="Select your return date"
    )

# Budget - SPLIT INTO 3 CATEGORIES
st.markdown("### 💰 Budget Breakdown")
st.caption("Enter separate budgets for each category in Indian Rupees (₹)")

col1, col2, col3 = st.columns(3)

with col1:
    flight_budget = st.number_input(
        "✈️ Flight Budget (₹)",
        min_value=1000,
        max_value=100000,
        value=15000,
        step=1000,
        help="Budget for round-trip flights"
    )
    st.caption(f"**₹{flight_budget:,}**")

with col2:
    hotel_budget = st.number_input(
        "🏨 Hotel Budget (₹)",
        min_value=1000,
        max_value=100000,
        value=20000,
        step=1000,
        help="Total budget for hotel stay"
    )
    st.caption(f"**₹{hotel_budget:,}**")

with col3:
    other_budget = st.number_input(
        "🎭 Other Expenses (₹)",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000,
        help="Food, transport, activities, shopping"
    )
    st.caption(f"**₹{other_budget:,}**")

# Calculate and show total budget
total_budget = flight_budget + hotel_budget + other_budget
st.info(f"💵 **Total Trip Budget: ₹{total_budget:,}**")

# Interests
st.markdown("### 🎨 Travel Interests")
st.caption("⚠️ **Important:** Select maximum 2 interests to avoid rate limits")

col1, col2, col3, col4 = st.columns(4)

with col1:
    interest_sightseeing = st.checkbox("🏛️ Sightseeing", value=True)
    interest_food = st.checkbox("🍽️ Food & Dining", value=False)

with col2:
    interest_adventure = st.checkbox("🏔️ Adventure", value=False)
    interest_shopping = st.checkbox("🛍️ Shopping", value=False)

with col3:
    interest_culture = st.checkbox("🎭 Culture & History", value=False)
    interest_beach = st.checkbox("🏖️ Beach & Water Sports", value=False)

with col4:
    interest_nightlife = st.checkbox("🌙 Nightlife", value=False)

# Collect selected interests
selected_interests = []
if interest_sightseeing:
    selected_interests.append("Sightseeing")
if interest_food:
    selected_interests.append("Food & Dining")
if interest_adventure:
    selected_interests.append("Adventure")
if interest_shopping:
    selected_interests.append("Shopping")
if interest_culture:
    selected_interests.append("Culture & History")
if interest_beach:
    selected_interests.append("Beach & Water Sports")
if interest_nightlife:
    selected_interests.append("Nightlife")

interests_str = ", ".join(selected_interests) if selected_interests else "General tourism"

# Warning if too many interests
if len(selected_interests) > 2:
    st.error(f"❌ You selected {len(selected_interests)} interests. **Maximum 2 recommended** to avoid rate limits!")
elif len(selected_interests) == 0:
    st.warning("⚠️ Please select at least one interest")
else:
    st.success(f"✅ Selected interests: **{interests_str}**")

st.divider()

# Plan Trip Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    plan_button = st.button(
        "🚀 Plan My Trip",
        type="primary",
        disabled=st.session_state.processing,
        use_container_width=True
    )

# Helper function to extract JSON from text
def extract_json_from_text(text):
    """Extract JSON arrays from text"""
    import re
    json_pattern = r'\[?\{[^}]+\}(?:,\s*\{[^}]+\})*\]?'
    matches = re.findall(json_pattern, text, re.DOTALL)
    parsed = []
    for match in matches:
        try:
            # Ensure it's a valid JSON array
            if not match.strip().startswith('['):
                match = '[' + match + ']'
            data = json.loads(match)
            if isinstance(data, list):
                parsed.extend(data)
            else:
                parsed.append(data)
        except:
            continue
    return parsed

# Process the trip planning
if plan_button:
    # Check cooldown period
    if st.session_state.last_request_time:
        elapsed = time.time() - st.session_state.last_request_time
        if elapsed < 120:
            remaining = int(120 - elapsed)
            st.error(f"⏳ Please wait **{remaining} more seconds** to avoid rate limits!")
            st.stop()

    # Validation
    if not source or not destination:
        st.error("❌ Please enter both source and destination cities!")
    elif start_date >= end_date:
        st.error("❌ End date must be after start date!")
    elif not selected_interests:
        st.error("⚠️ Please select at least one interest!")
    elif len(selected_interests) > 2:
        st.error("❌ Too many interests selected! Please select maximum 2 to avoid rate limits.")
    else:
        st.session_state.processing = True
        st.session_state.last_request_time = time.time()

        st.divider()

        # Show info box
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.write("🤖 **AI agents are working on your trip...**")
            st.write(f"- ✈️ Searching flights from **{source}** to **{destination}** (Budget: ₹{flight_budget:,})")
            st.write(f"- 🏨 Finding best hotels in **{destination}** (Budget: ₹{hotel_budget:,})")
            st.write(f"- 📅 Creating itinerary for **{interests_str}** (Budget: ₹{other_budget:,})")
            st.write("⏳ **This will take 60-90 seconds. Please wait...**")
            st.markdown('</div>', unsafe_allow_html=True)

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Prepare inputs with separate budgets
            inputs = {
                "source": source,
                "destination": destination,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "flight_budget": flight_budget,
                "hotel_budget": hotel_budget,
                "other_budget": other_budget,
                "total_budget": total_budget,
                "interests": interests_str
            }

            status_text.text("⏳ Initializing AI agents...")
            progress_bar.progress(10)
            time.sleep(2)

            # Create crew with rate limiting
            crew = Crew(
                agents=[flight_agent, hotel_agent, itinerary_agent],
                tasks=[flight_task, hotel_task, itinerary_task],
                process=Process.sequential,
                max_rpm=3,
                verbose=True,
            )

            status_text.text("✈️ Flight agent searching...")
            progress_bar.progress(30)

            # Execute crew and capture task outputs
            result = crew.kickoff(inputs=inputs)

            # Extract individual task results from crew execution
            # The crew stores task outputs in order of execution
            if hasattr(crew, 'tasks') and crew.tasks:
                for idx, task in enumerate(crew.tasks):
                    if hasattr(task, 'output'):
                        task_output = str(task.output)

                        if idx == 0:  # Flight task
                            st.session_state.flight_results = task_output
                            progress_bar.progress(40)
                        elif idx == 1:  # Hotel task
                            st.session_state.hotel_results = task_output
                            progress_bar.progress(70)
                        elif idx == 2:  # Itinerary task
                            st.session_state.itinerary_results = task_output
                            progress_bar.progress(90)

            progress_bar.progress(100)
            status_text.text("✅ Trip planning complete!")
            time.sleep(1)

            st.session_state.results = {
                'raw': result,
                'inputs': inputs
            }
            st.session_state.processing = False

            progress_bar.empty()
            status_text.empty()

            st.success("🎉 Your trip has been planned successfully!")
            st.balloons()

        except Exception as e:
            st.session_state.processing = False
            progress_bar.empty()
            status_text.empty()

            error_str = str(e)
            if "429" in error_str or "RateLimitError" in error_str or "RESOURCE_EXHAUSTED" in error_str or "rate_limit_error" in error_str.lower():
                st.error("⚠️ **Rate Limit Exceeded**")
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.write("**The API request limit has been exceeded. Here's what to do:**")
                st.write("1. ⏰ **Wait 2-3 minutes** before trying again")
                st.write("2. 📉 **Reduce interests** - Select only 1 interest")
                st.write("3. 🔄 **Refresh the page** and try again")
                st.write("\n**Why this happens:**")
                st.write("- Free tier: 10 requests per minute for Gemini API")
                st.write("- Each agent makes multiple API calls")
                st.write("- More interests = more API calls")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ An error occurred: {error_str}")
                st.write("**Troubleshooting:**")
                st.write("- Check your API keys in .env file")
                st.write("- Ensure you have internet connectivity")
                st.write("- Try again with fewer interests")

# Display results - NOW SHOWING ALL THREE SECTIONS SEPARATELY
if st.session_state.results:
    st.divider()
    st.markdown('<div class="main-header">📋 Your Complete Trip Plan</div>', unsafe_allow_html=True)

    # Trip Summary
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        inputs = st.session_state.results['inputs']

        with col1:
            st.metric("📍 Route", f"{inputs['source']} → {inputs['destination']}")
        with col2:
            start_dt = datetime.strptime(inputs['start_date'], "%Y-%m-%d")
            end_dt = datetime.strptime(inputs['end_date'], "%Y-%m-%d")
            duration_days = (end_dt - start_dt).days + 1  # inclusive
            nights = duration_days - 1
            st.metric("📅 Duration", f"{duration_days} days ({nights} nights)")
        with col3:
            st.metric("💰 Total Budget", f"₹{inputs['total_budget']:,}")
        with col4:
            st.metric("🎨 Interests", len(inputs['interests'].split(',')))

    st.divider()

    # ==================== FLIGHT SECTION ====================
    st.markdown("### ✈️ Flight Options")
    st.markdown('<div class="result-section">', unsafe_allow_html=True)

    if st.session_state.flight_results:
        flight_text = st.session_state.flight_results

        # Try to extract JSON first
        flights_data = extract_json_from_text(flight_text)
        flights = [d for d in flights_data if 'airline' in d or 'flight_number' in d]

        if flights:
            for i, flight in enumerate(flights[:3], 1):
                st.markdown(f"#### Flight Option {i}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Airline:** {flight.get('airline', 'N/A')}")
                    st.write(f"**Flight #:** {flight.get('flight_number', 'N/A')}")
                with col2:
                    st.write(f"**Departure:** {flight.get('departure_time', 'N/A')}")
                    st.write(f"**Arrival:** {flight.get('arrival_time', 'N/A')}")
                with col3:
                    st.write(f"**Price:** {flight.get('price', 'N/A')}")
                    st.write(f"**Duration:** {flight.get('duration', 'N/A')}")

                stops = flight.get('stops', 0)
                stop_text = "Non-stop" if stops == 0 else f"{stops} stop(s)"
                st.caption(f"✈️ {stop_text}")
                st.divider()
        else:
            # Show raw text if JSON parsing fails
            st.markdown(flight_text)
    else:
        st.info("ℹ️ Flight information not available. Try searching directly on airline websites.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== HOTEL SECTION ====================
    st.markdown("### 🏨 Hotel Options")
    st.markdown('<div class="result-section">', unsafe_allow_html=True)

    if st.session_state.hotel_results:
        hotel_text = st.session_state.hotel_results

        # Try to extract JSON first
        hotels_data = extract_json_from_text(hotel_text)
        hotels = [d for d in hotels_data if 'price_per_night' in d or ('name' in d and 'rating' in d)]

        if hotels:
            for i, hotel in enumerate(hotels[:3], 1):
                st.markdown(f"#### Hotel Option {i}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Hotel Name:** {hotel.get('name', 'N/A')}")
                    rating_val = hotel.get('rating', '0')
                    try:
                        rating_stars = '⭐' * int(float(rating_val))
                    except:
                        rating_stars = ''
                    st.write(f"**Rating:** {rating_stars} {rating_val}")
                    st.write(f"**Location:** {hotel.get('location', 'N/A')}")
                with col2:
                    st.write(f"**Price per Night:** {hotel.get('price_per_night', 'N/A')}")
                    st.write(f"**Total Cost:** {hotel.get('total_cost', 'N/A')}")
                    amenities = hotel.get('amenities', 'N/A')
                    if amenities != 'N/A':
                        st.write(f"**Amenities:** {amenities}")
                st.divider()
        else:
            # Show raw text if JSON parsing fails
            st.markdown(hotel_text)
    else:
        st.info("ℹ️ Hotel information not available")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== ITINERARY SECTION ====================
    st.markdown("### 📅 Day-by-Day Itinerary")
    st.markdown('<div class="result-section">', unsafe_allow_html=True)

    if st.session_state.itinerary_results:
        itinerary_text = str(st.session_state.itinerary_results).strip()

        # Clean lines and remove unwanted "undefined"/"null" text
        lines = [
            line.strip()
            for line in itinerary_text.split('\n')
            if line.strip() and line.strip().lower() not in ['undefined', 'none', 'null']
        ]

        displayed_days = set()

        for line in lines:
            if line.startswith("Day") and ":" in line:
                # Extract numeric day (e.g. "Day 1" → 1)
                day_num = ''.join(filter(str.isdigit, line))
                if day_num and day_num in displayed_days:
                    # Skip duplicate day headers
                    continue
                displayed_days.add(day_num)
                st.markdown(f"#### {line.strip()}")
            else:
                st.markdown(line.strip())
    else:
        st.markdown("ℹ️ No itinerary details available.")

    st.markdown('</div>', unsafe_allow_html=True)


    # Budget breakdown display
    st.divider()
    st.markdown("### 💵 Budget Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("✈️ Flights", f"₹{inputs['flight_budget']:,}")
    with col2:
        st.metric("🏨 Hotels", f"₹{inputs['hotel_budget']:,}")
    with col3:
        st.metric("🎭 Other", f"₹{inputs['other_budget']:,}")
    with col4:
        st.metric("💰 Total", f"₹{inputs['total_budget']:,}")

    # Download button
    st.divider()

    # Create formatted download text
    download_sections = []
    download_sections.append("="*60)
    download_sections.append(f"TRIP PLAN: {inputs['source']} to {inputs['destination']}")
    download_sections.append(f"Dates: {inputs['start_date']} to {inputs['end_date']}")
    download_sections.append(f"Duration: {duration_days} days")
    download_sections.append(f"Duration: {nights} nights")
    download_sections.append("="*60)
    download_sections.append("\nBUDGET BREAKDOWN:")
    download_sections.append(f"- Flight Budget: ₹{inputs['flight_budget']:,}")
    download_sections.append(f"- Hotel Budget: ₹{inputs['hotel_budget']:,}")
    download_sections.append(f"- Other Expenses: ₹{inputs['other_budget']:,}")
    download_sections.append(f"- Total Budget: ₹{inputs['total_budget']:,}")
    download_sections.append(f"\nInterests: {inputs['interests']}")
    download_sections.append("\n" + "="*60)

    # Add flights
    download_sections.append("\n✈️ FLIGHT OPTIONS:\n")
    if st.session_state.flight_results:
        download_sections.append(st.session_state.flight_results)
    else:
        download_sections.append("No flight options available\n")

    # Add hotels
    download_sections.append("\n🏨 HOTEL OPTIONS:\n")
    if st.session_state.hotel_results:
        download_sections.append(st.session_state.hotel_results)
    else:
        download_sections.append("No hotel options available\n")

    # Add itinerary
    download_sections.append("\n📅 DAY-BY-DAY ITINERARY:\n")
    if st.session_state.itinerary_results:
        download_sections.append(st.session_state.itinerary_results)
    else:
        download_sections.append("See app for details")

    download_text = '\n'.join(download_sections)

    st.download_button(
        label="📥 Download Trip Plan",
        data=download_text,
        file_name=f"trip_plan_{inputs['source']}_to_{inputs['destination']}.txt",
        mime="text/plain"
    )

    # Action buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Plan Another Trip", use_container_width=True):
            st.session_state.results = None
            st.session_state.flight_results = None
            st.session_state.hotel_results = None
            st.session_state.itinerary_results = None
            st.rerun()

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: #757575; padding: 2rem;'>
        <p>Powered by AI Agents 🤖 | Built with CrewAI & Streamlit</p>
        <p><small>⚠️ Free API tier: Wait 2 minutes between searches. Max 1-2 interests recommended.</small></p>
    </div>
""", unsafe_allow_html=True)
