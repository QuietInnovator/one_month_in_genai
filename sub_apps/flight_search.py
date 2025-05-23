import streamlit as st
import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI

def main_form():
    # Main form
    col1, col2 = st.columns(2)

    with col1:
        origin = st.text_input("Origin City (e.g., New York, JFK)", "New York")
        
    with col2:
        destination = st.text_input("Destination City (e.g., Los Angeles, LAX)", "Los Angeles")

    # Date selection (default to tomorrow)
    tomorrow = datetime.now() + timedelta(days=1)
    travel_date = st.date_input("Travel Date", tomorrow)

    return origin, destination, travel_date

def search_flights(origin, destination, date, serper_key):
    """Search flights using Serper API"""
    
    # Format date for search
    formatted_date = date.strftime("%Y-%m-%d")
    
    # Construct search query - make it more specific
    query = f"one way flight from {origin} to {destination} on {formatted_date} flight price"
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "us",  # Set region to US for better flight results
        "num": 20    # Request more results
    })
    
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Check if we got valid results
        result_json = response.json()
        
        # If no organic results found, try an alternative search query
        if 'organic' not in result_json or len(result_json.get('organic', [])) < 2:
            # Try alternative search query
            alt_query = f"book flights {origin} to {destination} {formatted_date}"
            
            alt_payload = json.dumps({
                "q": alt_query,
                "gl": "us",
                "num": 20
            })
            
            alt_response = requests.post(url, headers=headers, data=alt_payload)
            alt_response.raise_for_status()
            return alt_response.json()
        
        return result_json
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching flights: {e}")
        return None

# Process search results with OpenAI
def analyze_flights(search_results, openai_key):
    """Analyze flight search results using OpenAI API"""
    
    client = OpenAI(api_key=openai_key)
    
    # Convert search results to string
    search_text = json.dumps(search_results)
    
    # Send to OpenAI for analysis
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """
                You are an expert flight finder assistant. Your task is to analyze search results and extract flight information.
                
                INSTRUCTIONS:
                1. Look for flight details including: airline names, prices, departure times, arrival times, and flight durations
                2. For each flight found, extract:
                   - airline: The airline name
                   - price: The ticket price (with currency)
                   - departure: Departure time with date
                   - arrival: Arrival time with date
                   - duration: Flight duration if available
                3. Compare options and select the best flight based on:
                   - Lower price
                   - Convenient departure time (not too early/late)
                   - Reputable airline
                   - Shorter duration
                
                YOUR RESPONSE MUST BE VALID JSON with this structure:
                {
                  "all_flights": [
                    {"airline": "Airline Name", "price": "$199", "departure": "9:00 AM", "arrival": "11:30 AM", "duration": "2h 30m"},
                    ...more flights...
                  ],
                  "best_flight": {"airline": "Best Airline", "price": "$249", "departure": "10:15 AM", "arrival": "12:45 PM", "duration": "2h 30m"},
                  "recommendation_reason": "This flight offers the best balance of price and convenient timing"
                }
                
                If no flight information can be found, return:
                {"all_flights": [], "best_flight": {}, "recommendation_reason": "No flight information could be extracted from the search results"}
                """},
                {"role": "user", "content": f"Here are the search results for flights. Extract all flight options and recommend the best one:\n\n{search_text}"}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}  # Force JSON response format
        )
        
        # Parse the response - should be JSON with response_format parameter
        content = response.choices[0].message.content
        
        try:
            flight_data = json.loads(content)
            
            # Validate the response structure
            if "all_flights" not in flight_data or "best_flight" not in flight_data:
                # Create a basic structure if missing
                if "all_flights" not in flight_data:
                    flight_data["all_flights"] = []
                if "best_flight" not in flight_data:
                    flight_data["best_flight"] = {}
                if "recommendation_reason" not in flight_data:
                    flight_data["recommendation_reason"] = "No clear recommendation available"
                    
            return flight_data
            
        except json.JSONDecodeError:
            # This shouldn't happen with response_format=json_object, but just in case
            return {
                "error": "Could not parse flight data", 
                "raw_response": content,
                "all_flights": [],
                "best_flight": {},
                "recommendation_reason": "Error processing flight data"
            }
            
    except Exception as e:
        st.error(f"Error analyzing flights: {str(e)}")
        return {
            "error": str(e),
            "all_flights": [],
            "best_flight": {},
            "recommendation_reason": "An error occurred while processing flight data"
        }

def flight_search_main():
    st.title("Flight Search")
    origin, destination, travel_date = main_form()
    serper_key = st.secrets["SERPER_API_KEY"]
    openai_key = st.secrets["OPENAI_API_KEY"]

    if st.button("Search Flights", type="primary"):
        with st.spinner("Searching for flights..."):
            search_results = search_flights(origin, destination, travel_date, serper_key)
            if search_results:
                with st.expander("View raw search data"):
                    st.json(search_results)
            
                # Analyze with OpenAI
                with st.spinner("Analyzing flight options..."):
                    flight_analysis = analyze_flights(search_results, openai_key)
                    
                    # Always have these keys now due to improved error handling
                    all_flights = flight_analysis.get("all_flights", [])
                    best_flight = flight_analysis.get("best_flight", {})
                    
                    if "error" in flight_analysis:
                        # Show error but continue with any data we have
                        st.error(f"Warning: {flight_analysis['error']}")
                        if "raw_response" in flight_analysis:
                            with st.expander("View error details"):
                                st.text(flight_analysis["raw_response"])
                    
                    # Display results based on what we have
                    if best_flight and all_flights:
                        st.success("Flight search complete!")
                    elif not all_flights:
                        st.warning("No flight details could be extracted from the search results.")
                        st.info("Try modifying your search terms or search date to get better results.")
                        st.stop()  # Stop execution if no flights found
                    
                    # Best flight recommendation (if we have one)
                    if best_flight:
                        st.header("✨ Recommended Flight")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader(f"{best_flight.get('airline', 'Airline')}")
                            st.metric("Price", best_flight.get('price', 'N/A'))
                        with col2:
                            st.subheader("Flight Details")
                            st.write(f"🛫 Departs: {best_flight.get('departure', 'N/A')}")
                            st.write(f"🛬 Arrives: {best_flight.get('arrival', 'N/A')}")
                            if 'duration' in best_flight:
                                st.write(f"⏱️ Duration: {best_flight.get('duration', 'N/A')}")
                        
                        st.info(f"**Why this flight?** {flight_analysis.get('recommendation_reason', 'Best option based on price and schedule')}")
                    
                    # All flight options
                    if all_flights:
                        st.header(f"All Available Flights ({len(all_flights)})")
                        
                        # Convert to DataFrame for display
                        df = pd.DataFrame(all_flights)
                        st.dataframe(df, use_container_width=True)
                        
                        # Add CSV download option
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download flight data as CSV",
                            csv,
                            f"flights_{origin}_to_{destination}_{travel_date}.csv",
                            "text/csv",
                            key='download-csv'
                        )
            else:
                st.error("No search results found. Please try different search terms.")
