from pprint import pprint

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def scrape_website(url, base_domain, visited_urls=None):
    """
    Scrapes data from the provided URL and recursively follows links within the same domain.

    Parameters:
    - url: The URL to scrape.
    - base_domain: The base domain to restrict scraping.
    - visited_urls: A set of visited URLs to avoid infinite loops.

    Returns:
    - data_frames: A list of pandas DataFrames containing the extracted data.
    """
    if visited_urls is None:
        visited_urls = set()

    data_frames = []
    if url in visited_urls:
        return data_frames

    visited_urls.add(url)
    print(url)

    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract table data
    tables = soup.find_all('table')
    for table in tables:
        data = []
        headers = [header.get_text(strip=True) for header in table.find_all('th')]
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all('td')
            if columns:
                data.append([col.get_text(strip=True) for col in columns])
        if headers and data:
            pprint(data)
            pprint(headers)
            df = pd.DataFrame(data, columns=headers[:len(data[0])])
        else:
            df = pd.DataFrame(data)
        if not df.empty:
            data_frames.append(df)

    # Find and follow links within the same domain
    links = soup.find_all('a', href=True)
    for link in links:
        href = link['href']
        if href.__contains__(base_domain) or re.match(r'^/', href):
            new_url = href if href.startswith(base_domain) else base_domain + href
            data_frames.extend(scrape_website(new_url, base_domain, visited_urls))

    return data_frames


def generate_insights(data_frames):
    """
    Generates 10 key insights from a list of DataFrames.

    Parameters:
    - data_frames: A list of pandas DataFrames.

    Returns:
    - insights: A list of insights.
    """
    insights = []
    for df in data_frames:
        if not df.empty:
            insights.append(f"DataFrame columns: {', '.join(df.columns)}")
            insights.append(f"Total rows: {len(df)}")
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    insights.append(f"Mean of {col}: {df[col].astype(float).mean()}")
                    insights.append(f"Max of {col}: {df[col].astype(float).max()}")
                    insights.append(f"Min of {col}: {df[col].astype(float).min()}")
                else:
                    insights.append(f"Most common value in {col}: {df[col].mode().iloc[0]}")
            insights.append(f"Number of unique values in columns: {df.nunique().to_dict()}")
            insights.append(f"Summary statistics:\n{df.describe(include='all').to_string()}")
            insights.append(f"First few rows:\n{df.head().to_string()}")
    return insights


# Define the base URL and domain
BASE_URL = 'https://results.eci.gov.in'
BASE_DOMAIN = 'results.eci.gov.in'

# Scrape the website and collect all data
all_data_frames = scrape_website(BASE_URL, BASE_DOMAIN)

# Generate insights from the collected data
key_insights = generate_insights(all_data_frames)

# Save the report
report = '\n'.join(key_insights)
with open('election_report.txt', 'w') as file:
    file.write(report)

print("Report generated and saved as 'election_report.txt'")
