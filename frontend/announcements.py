"""
ANMDMR Announcements page

Main components:
-> Web scrapping of Romanian National Agency of Medications and Medical Devices (ANMDMR) announcements
-> Processing the announcements using the Anthropic
-> Display the processed announcements
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup     #Used for parsing HTML content
import os                         #Used for accessing environment variables
import anthropic                  #Interacting with Anthropic
from dotenv import load_dotenv


#Load env variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


def scrape_anmdmr_announcements():
    """
    Scrape announcements from the ANMDMR website

    The function sends a GET request for the ANMDMR announcements page, parse the HTML content, and extracts the
    informations for each announcement

    Return:
    list: a list of dictionaries, each containing details of an announcement
          (date, title, link, and other information)
    """
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
    """
    Process the scraped announcements using Anthropic

    The function takes the scraped announcements , formats them into a prompt, and sends this prompt to the Anthropic for
    processing. The API returns a summarized version of the announcements in English.
    """
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
    """
    Main function for displaying the ANMDMR announcements

    Display both the summarized and original announcements
    """
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
