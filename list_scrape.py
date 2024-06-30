import requests
from bs4 import BeautifulSoup
import pandas as pd

from extract_urls import ALL_URLS

ALL_URLS = set(ALL_URLS)


def scrape_tables_from_url(url):
    """
    Scrapes all tables from the provided URL.

    Parameters:
    - url: The URL to scrape.

    Returns:
    - data_frames: A list of pandas DataFrames containing the extracted data.
    """
    data_frames = []

    try:
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
                df = pd.DataFrame(data, columns=headers[:len(data[0])])
            else:
                df = pd.DataFrame(data)
            if not df.empty:
                data_frames.append(df)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")

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


# Scrape tables from each URL and collect all data
all_data_frames = []
for url in ALL_URLS:
    all_data_frames.extend(scrape_tables_from_url(url))

# Generate insights from the collected data
key_insights = generate_insights(all_data_frames)

# Save the report
report = '\n'.join(key_insights)
with open('list_scrape_report.txt', 'w') as file:
    file.write(report)

print("Report generated and saved as 'tables_report.txt'")
