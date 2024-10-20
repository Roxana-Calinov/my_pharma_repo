import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
import anthropic
from dotenv import load_dotenv


load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def scrape_anmdmr_announcements():
    url = "https://www.anm.ro/medicamente-de-uz-uman/anunturi-importante-medicamente-de-uz-uman/"
    response = requests.get(url)

    if response.status_code != 200:
        st.error("Failed to retrieve the website.")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    announcements = []

    for item in soup.select('li.listing-item'):
        title_element = item.select_one('a.title')
        link = title_element['href'] if title_element else '#'
        title = title_element.text.strip() if title_element else 'No Title'
        date_element = item.select_one('.content strong')
        date = date_element.text.strip() if date_element else 'No Date'

        additional_texts = []
        for br in item.select('.content br'):
            additional_text = br.find_next_sibling(text=True)
            if additional_text:
                additional_texts.append(additional_text.strip())

        additional_info = " ".join(additional_texts) if additional_texts else "No additional information"

        announcements.append({
            'date': date,
            'title': title,
            'link': link,
            'additional_info': additional_info
        })

    return announcements[:5]   #First 5 page announcements


def process_with_anthropic(announcements):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    announcements_text = "\n".join([
        f"{a['date']} - {a['title']}: {a['additional_info']}" for a in announcements
    ])

    prompt = f"""Summarize these ANMDMR announcements in English, highlighting key points for each:{announcements_text}
                 Provide a concise summary for each announcement, highlight the important information. 
                 Do NOT provide ANY additional information or description.
            """

    #Send prompt to API Anthropic for processing
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    text_content = ''.join([block.text for block in response.content])
    return text_content



def main_announcements():
    st.title("ANMDMR Announcements and Medication Stock Levels")

    #Scrape and display announcements
    announcements = scrape_anmdmr_announcements()
    if announcements:
        summary = process_with_anthropic(announcements)

        st.subheader("Summary of ANMDMR Announcements:")
        st.write(summary)

        st.subheader("Original Announcements:")
        for a in announcements:
            st.write(f"**Date:** {a['date']} - **Title:** {a['title']}")
            st.write(f"**Additional Information:** {a['additional_info']}")
            st.write(f"[Link]({a['link']})")
    else:
        st.write("No announcements found on the ANMDMR website.")


if __name__ == "__main__":
    main_announcements()
