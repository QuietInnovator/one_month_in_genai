import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from io import StringIO
import openai

# --- config.py ---

def get_serper_api_key():
    return st.secrets["SERPER_API_KEY"]

def get_openai_api_key():
    return st.secrets["OPENAI_API_KEY"]

def get_openai_model():
    return "gpt-4o-mini"

# --- search.py ---

def make_search_payload(query):
    return {"q": f"best practices {query} schedule"}

def get_search_headers(api_key):
    return {"X-API-KEY": api_key, "Content-Type": "application/json"}

def extract_snippets(results):
    return [item["snippet"] for item in results.get("organic", [])]

def search_best_practices(query, api_key):
    url = "https://google.serper.dev/search"
    headers = get_search_headers(api_key)
    data = make_search_payload(query)
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        st.error("Serper API error. Check your API key and usage.")
        return []
    results = response.json()
    return extract_snippets(results)

# --- gpt_schedule.py ---

def build_weekly_schedule_prompt(snippets, start_time, end_time):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    prompt = (
        "Given the following web search snippets about best practices and sample schedules, "
        "generate a distinct structured daily schedule for each weekday (Monday to Friday) as a JSON object. "
        "Each key should be the day name ('Monday', 'Tuesday', etc), and the value should be a list of schedule items for that day. "
        "Each item should have: 'start_time' (e.g. '09:00'), 'end_time' (e.g. '10:30'), 'activity', and optionally 'notes'.\n\n"
        f"Only schedule activities between {start_time.strftime('%H:%M')} and {end_time.strftime('%H:%M')}.\n"
        "Output ONLY the JSON object, without any additional text or formatting, and do not use markdown formatting. "
        "Example:\n"
        "{\n"
        "  \"Monday\": [\n"
        "    {\"start_time\": \"09:00\", \"end_time\": \"10:00\", \"activity\": \"Breakfast\", \"notes\": \"High-protein meal\"},\n"
        "    ...\n"
        "  ],\n"
        "  \"Tuesday\": [...],\n"
        "  ...\n"
        "  \"Friday\": [...]\n"
        "}\n"
        "Web search snippets:\n"
        + "\n".join(snippets)
    )
    return prompt

def call_gpt(prompt, model, api_key):
    openai.api_key = api_key
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()

def extract_json_from_gpt_output(output):
    import re
    import json
    output = re.sub(r'^```(?:json)?|```$', '', output, flags=re.MULTILINE).strip()
    # Match dictionary (object) style JSON
    json_match = re.search(r'\{\s*".*"\s*:\s*\[.*\}\s*\}', output, re.DOTALL)
    json_str = json_match.group(0) if json_match else output
    try:
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Could not parse GPT output as JSON. Error: {e}")
        st.write("Raw output was:", output)
        return {}

def prompt_gpt_weekly_schedule(snippets, model, api_key, start_time, end_time):
    prompt = build_weekly_schedule_prompt(snippets, start_time, end_time)
    output = call_gpt(prompt, model, api_key)
    return extract_json_from_gpt_output(output)

# --- date_utils.py ---

def is_weekday(date):
    return date.weekday() < 5  # 0-4 = Mon-Fri

def get_weekdays_in_range(start_date, end_date):
    days = []
    current = start_date
    while current <= end_date:
        if is_weekday(current):
            days.append(current)
        current += timedelta(days=1)
    return days

def weekday_name(date):
    return date.strftime("%A")

# --- calendar_utils.py ---

def make_event(item, day):
    from ics import Event, DisplayAlarm
    e = Event()
    e.name = item.get("activity", "")[:40]
    start_dt = datetime.combine(day, datetime.strptime(item["start_time"], "%H:%M").time())
    end_dt = datetime.combine(day, datetime.strptime(item["end_time"], "%H:%M").time())
    e.begin = start_dt
    e.end = end_dt
    # Description as a concise, bulleted list
    description_lines = [
        f"• Activity: {item.get('activity', '')}",
        f"• Time: {item['start_time']}-{item['end_time']}"
    ]
    if item.get("notes"):
        description_lines.append(f"• Notes: {item['notes']}")
    e.description = "\n".join(description_lines)
    # Add reminders (alarms)
    # One day before
    e.alarms.append(DisplayAlarm(trigger=timedelta(days=-1), display_text="Event starts in 1 day!"))
    # One hour before
    e.alarms.append(DisplayAlarm(trigger=timedelta(hours=-1), display_text="Event starts in 1 hour!"))
    return e

def generate_ics_from_gpt_weekly(weekly_schedule, start_date, end_date):
    from ics import Calendar
    weekdays = get_weekdays_in_range(start_date, end_date)
    c = Calendar()
    for day in weekdays:
        wday = weekday_name(day)
        day_schedule = weekly_schedule.get(wday, [])
        for item in day_schedule:
            event = make_event(item, day)
            c.events.add(event)
    return str(c)

def make_csv_rows_weekly(weekly_schedule, weekdays):
    rows = []
    for day in weekdays:
        wday = weekday_name(day)
        for item in weekly_schedule.get(wday, []):
            row = item.copy()
            row['date'] = day.strftime('%Y-%m-%d')
            row['weekday'] = wday
            rows.append(row)
    return rows

def display_snippet_cards(snippets):
    st.markdown("### 🔎 Best Practices & Research Results")
    for idx, snippet in enumerate(snippets):
        with st.container():
            st.markdown(
                f"""
                <div style="
                    padding:0.5em 1em 0.5em 1em;
                    border-left: 5px solid #0077FF;
                    margin-bottom:0.7em;
                ">
                    <span style="color:#0077FF; font-weight:600; font-size:1.08em;">Tip {idx+1}</span><br>
                    <span style="color:#256029; font-size:1.1em;">{snippet}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

# --- UI Helper for Cards ---

def display_snippet_cards(snippets):
    st.markdown("### 🔎 Best Practices & Research Results")
    for idx, snippet in enumerate(snippets):
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#F7F7F9;padding:1em 1em 0.5em 1em;border-radius:16px;margin-bottom:0.5em;box-shadow:0 1px 6px #0001;">
                    <b>Tip {idx+1}</b><br>
                    {snippet}
                </div>
                """,
                unsafe_allow_html=True,
            )

# --- Main App ---

def main():
    st.title("AI Weekly Rotating Schedule Generator (GPT-4o Mini Structured Output)")
    st.markdown("""
    - Enter your **topic or activity** (e.g., "marathon training", "study for exams").
    - The app finds best-practice schedules and structures a unique schedule for each weekday (Mon–Fri) with OpenAI GPT-4o Mini.
    - Download as **Excel (CSV)** or **ICS calendar**.
    - Schedules will rotate: Monday schedule repeats every Monday, Tuesday schedule every Tuesday, etc.
    - **Reminders**: Each event will have notifications 1 day and 1 hour before!
    """)

    query = st.text_input(
        "What do you want to schedule?",
        help="e.g., 'study for exams', 'workout routine', 'marathon training'"
    )
    today = datetime.now().date()
    default_end = today + timedelta(days=6)
    default_start_time = datetime.strptime("09:00", "%H:%M").time()
    default_end_time = datetime.strptime("17:00", "%H:%M").time()

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Schedule start date", value=today)
        start_time = st.time_input("Start time", value=default_start_time, key="start_time")
    with col2:
        end_date = st.date_input("Schedule end date", value=default_end, min_value=date)
        end_time = st.time_input("End time", value=default_end_time, key="end_time")

    serper_api_key = get_serper_api_key()
    openai_api_key = get_openai_api_key()
    openai_model = get_openai_model()

    if st.button("Generate Weekly Rotating Schedule"):
        if not query:
            st.warning("Please enter your topic or activity.")
        elif end_date < date:
            st.warning("End date must be after start date.")
        elif end_time <= start_time:
            st.warning("End time must be after start time.")
        else:
            with st.spinner("Searching and generating schedule..."):
                snippets = search_best_practices(query, serper_api_key)
                if not snippets:
                    st.error("No results found. Try a different query.")
                else:
                    # Show best practices research as cards BEFORE the schedule
                    display_snippet_cards(snippets)
                    weekly_schedule = prompt_gpt_weekly_schedule(
                        snippets, openai_model, openai_api_key, start_time, end_time
                    )
                    if not weekly_schedule or not isinstance(weekly_schedule, dict):
                        st.error("Could not generate structured schedule. Try again or use a different query.")
                    else:
                        st.success("Weekly rotating schedule generated using GPT-4o Mini!")
                        st.write(
                            f"Below are the **five weekday schedules** (Monday–Friday). Each will repeat on its weekday over the span from {date} to {end_date}, "
                            f"between {start_time.strftime('%H:%M')} and {end_time.strftime('%H:%M')}:"
                        )
                        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                        for wday in weekday_order:
                            if wday in weekly_schedule:
                                st.markdown(f"#### {wday}")
                                df = pd.DataFrame(weekly_schedule[wday])
                                if not df.empty:
                                    st.dataframe(df)
                                else:
                                    st.info(f"No activities for {wday}.")
                            else:
                                st.info(f"No schedule for {wday}.")

                        # Download as CSV and ICS
                        csv_data = generate_csv_from_gpt_weekly(weekly_schedule, date, end_date)
                        ics_data = generate_ics_from_gpt_weekly(weekly_schedule, date, end_date)

                        st.download_button("Download as Excel (CSV)", csv_data, "weekly_schedule.csv", "text/csv")
                        st.download_button("Download as iCal (ICS)", ics_data, "weekly_schedule.ics", "text/calendar")

    st.markdown("---")
    st.caption("Weekly rotating schedule powered by Serper API + OpenAI GPT-4o Mini + Streamlit.")

if __name__ == "__main__":
    main()
