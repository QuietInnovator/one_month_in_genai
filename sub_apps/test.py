import streamlit as st
import summarize_meetings as sm
import research_writer as rw
import linkedin_chat as lc
import flight_search as fs
import email_composer as ec
import tagline_generator as tg
import doc_editor as de
import regex_generator as rg

def main():
    rg.main()
    # de.main()
    # fs.main()
    # ec.email_composer_ui()
    # tg.main()
    # sm.summaryapp()
    # rw.research_writer_redirect()
if __name__ == "__main__":
    main()