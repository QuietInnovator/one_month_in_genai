import streamlit as st
import summarize_meetings as sm
import research_writer as rw

def main():
    sm.summaryapp()
    rw.research_writer_redirect()
if __name__ == "__main__":
    main()