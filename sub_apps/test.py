import streamlit as st
import summarize_meetings as sm
import research_writer as rw
import linkedin_chat as lc
import flight_search as fs

def main():
    fs.flight_search_main()
    # sm.summaryapp()
    # rw.research_writer_redirect()
if __name__ == "__main__":
    main()