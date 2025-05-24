import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI

#---------------------- UI COMPONENTS ------------------------

def show_description():
    st.subheader("Description")
    st.write("""
        My fifth project solves a pain that I had when I was traveling.
        I was spending too much time searching for flights and defining the best prices.
        So this project provides a way to search for flights automatically and instantaneously.
    """)

def get_city_input(label, default_value):
    return st.text_input(label, default_value)

def get_date_input(label, default_date):
    return st.date_input(label, default_date)

def show_loading_spinner(text):
    return st.spinner(text)

def show_error(msg):
    st.error(msg)

def show_success(msg):
    st.success(msg)

def show_warning(msg):
    st.warning(msg)

def show_info(msg):
    st.info(msg)

def show_json(data, expander_label="View raw data"):
    with st.expander(expander_label):
        st.json(data)

def show_text(text, expander_label="Details"):
    with st.expander(expander_label):
        st.text(text)

def show_flight_table(flights, origin, destination, travel_date):
    if flights:
        df = pd.DataFrame(flights)
        # Fill missing fields with "N/A" for user clarity
        for col in ['departure', 'arrival', 'duration']:
            if col in df.columns:
                df[col] = df[col].replace("", "N/A").fillna("N/A")
        # "Link" column has been removed
        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download flight data as CSV",
            csv,
            f"flights_{origin}_to_{destination}_{travel_date}.csv",
            "text/csv",
            key='download-csv'
        )

def show_best_flight(flight, reason):
    st.header("✨ Recommended Flight")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{flight.get('airline', 'Airline')}")
        st.metric("Price", flight.get('price', 'N/A'))
        url = flight.get('url', '')
        if url:
            st.markdown(f"[Book or view this flight]({url})", unsafe_allow_html=True)
    with col2:
        st.subheader("Flight Details")
        st.write(f"🛫 Departs: {flight.get('departure', 'N/A')}")
        st.write(f"🛬 Arrives: {flight.get('arrival', 'N/A')}")
        st.write(f"⏱️ Duration: {flight.get('duration', 'N/A')}")
    st.info(f"**Why this flight?** {reason}")

#---------------------- API HANDLERS -------------------------

def build_search_query(origin, destination, date):
    formatted_date = date.strftime("%Y-%m-%d")
    return f"one way flight from {origin} to {destination} on {formatted_date} flight price"

def build_alt_search_query(origin, destination, date):
    formatted_date = date.strftime("%Y-%m-%d")
    return f"book flights {origin} to {destination} {formatted_date}"

def search_with_serper(query, serper_key, num_results=20):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "us",
        "num": num_results
    })
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def search_flights(origin, destination, date, serper_key):
    query = build_search_query(origin, destination, date)
    results = search_with_serper(query, serper_key)
    if 'error' in results:
        return results
    if 'organic' not in results or len(results.get('organic', [])) < 2:
        alt_query = build_alt_search_query(origin, destination, date)
        results = search_with_serper(alt_query, serper_key)
    return results

def openai_analyze_flights(search_results, openai_key):
    client = OpenAI(api_key=openai_key)
    search_text = json.dumps(search_results)
    # ---- Improved Prompt! ----
    system_prompt = """
You are an expert flight finder assistant. Your task is to analyze search results and extract flight information.

INSTRUCTIONS:
1. Look for flight details including: airline names, prices, departure times, arrival times, flight durations, and any URL or booking link associated with the flight.
2. For each flight found, extract:
   - airline: The airline name
   - price: The ticket price (with currency)
   - departure: The departure time with date, if available (extract any phrase that looks like a time or datetime, e.g., "2024-06-30 09:30", "9:00 AM", etc.)
   - arrival: The arrival time with date, if available (same rule)
   - duration: The flight duration if available (e.g., "2h 30m", or phrases like "5 hours")
   - url: The URL to view or book the flight if available (else leave empty string)
   - If times or durations are missing but can be inferred from text, extract the approximate info.
3. Include values even if they're approximate or incomplete (e.g., only "Morning" or "Overnight").
4. Compare options and select the best flight based on:
   - Lower price
   - Convenient departure time (not too early/late)
   - Reputable airline
   - Shorter duration

YOUR RESPONSE MUST BE VALID JSON with this structure:
{
  "all_flights": [
    {"airline": "Airline Name", "price": "$199", "departure": "2024-06-30 09:30", "arrival": "2024-06-30 12:00", "duration": "2h 30m", "url": "https://www.example.com"},
    ...more flights...
  ],
  "best_flight": {"airline": "Best Airline", "price": "$249", "departure": "2024-06-30 10:15", "arrival": "2024-06-30 12:45", "duration": "2h 30m", "url": "https://www.example.com"},
  "recommendation_reason": "This flight offers the best balance of price and convenient timing"
}

If no flight information can be found, return:
{"all_flights": [], "best_flight": {}, "recommendation_reason": "No flight information could be extracted from the search results"}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here are the search results for flights. Extract all flight options and recommend the best one:\n\n{search_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "all_flights": [],
            "best_flight": {},
            "recommendation_reason": "An error occurred while processing flight data"
        })

def parse_flight_analysis_response(content):
    try:
        data = json.loads(content)
        if "all_flights" not in data:
            data["all_flights"] = []
        if "best_flight" not in data:
            data["best_flight"] = {}
        if "recommendation_reason" not in data:
            data["recommendation_reason"] = "No clear recommendation available"
        return data
    except json.JSONDecodeError:
        return {
            "error": "Could not parse flight data",
            "raw_response": content,
            "all_flights": [],
            "best_flight": {},
            "recommendation_reason": "Error processing flight data"
        }

#---------------------- MAIN LOGIC ---------------------------

def get_form_inputs():
    col1, col2 = st.columns(2)
    with col1:
        origin = get_city_input("Origin City (e.g., New York, JFK)", "New York")
    with col2:
        destination = get_city_input("Destination City (e.g., Los Angeles, LAX)", "Los Angeles")
    tomorrow = datetime.now() + timedelta(days=1)
    travel_date = get_date_input("Travel Date", tomorrow)
    return origin, destination, travel_date

def handle_flight_search(origin, destination, travel_date, serper_key, openai_key):
    with show_loading_spinner("Searching for flights..."):
        results = search_flights(origin, destination, travel_date, serper_key)
    if 'error' in results:
        show_error(f"Error searching flights: {results['error']}")
        return
    show_json(results)
    with show_loading_spinner("Analyzing flight options..."):
        analysis_content = openai_analyze_flights(results, openai_key)
    flight_data = parse_flight_analysis_response(analysis_content)
    if "error" in flight_data:
        show_error(f"Warning: {flight_data['error']}")
        if "raw_response" in flight_data:
            show_text(flight_data["raw_response"], "View error details")
    all_flights = flight_data.get("all_flights", [])
    best_flight = flight_data.get("best_flight", {})
    reason = flight_data.get("recommendation_reason", "")
    if not all_flights:
        show_warning("No flight details could be extracted from the search results.")
        show_info("Try modifying your search terms or search date to get better results.")
        return
    if best_flight:
        show_best_flight(best_flight, reason)
    show_flight_table(all_flights, origin, destination, travel_date)

def main():
    st.title("Flight Search")
    show_description()
    origin, destination, travel_date = get_form_inputs()
    serper_key = st.secrets["SERPER_API_KEY"]
    openai_key = st.secrets["OPENAI_API_KEY"]
    if st.button("Search Flights", type="primary"):
        handle_flight_search(origin, destination, travel_date, serper_key, openai_key)

if __name__ == "__main__":
    main()
