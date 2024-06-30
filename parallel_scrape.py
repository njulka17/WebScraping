import json
import threading
from queue import Queue
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd

ALL_URLS = set()
URL_QUEUE = Queue()


def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def scrape_tables_from_url(url):
    data_frames = []
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

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


def generate_insights(df):
    insights = {}
    try:
        insights['Party Name'] = df['Party'].unique().tolist()
        insights['Number of Wins'] = df['Won'].astype(int).sum()
        insights['Leading Seats'] = df['Leading'].astype(int).sum()
        insights['Total Contested Seats'] = df['Total'].astype(int).sum()
        insights['Win Percentage'] = (insights['Number of Wins'] / insights['Total Contested Seats']) * 100
        insights['Leading Percentage'] = (insights['Leading Seats'] / insights['Total Contested Seats']) * 100
        insights['Seat Share'] = (insights['Number of Wins'] / df['Total'].astype(int).sum()) * 100

        insights['Party Performance'] = df.loc[df['Won'].astype(int).idxmax(), 'Party']
        sorted_wins = df['Won'].astype(int).sort_values(ascending=False)
        insights['Margin of Victory'] = sorted_wins.iloc[0] - sorted_wins.iloc[1] \
            if len(sorted_wins) > 1 else sorted_wins.iloc[0]
        insights['Election Outcome'] = 'Majority' if insights['Number of Wins'] > df['Total'].astype(int).sum() / 2 \
            else 'No Majority'

        insights['Number of Wins'] = int(insights['Number of Wins'])
        insights['Leading Seats'] = int(insights['Leading Seats'])
        insights['Total Contested Seats'] = int(insights['Total Contested Seats'])
        insights['Win Percentage'] = int(insights['Win Percentage'])
        insights['Leading Percentage'] = int(insights['Leading Percentage'])
        insights['Seat Share'] = int(insights['Seat Share'])
        insights['Margin of Victory'] = int(insights['Margin of Victory'])
    except Exception as e:
        print(f"Failed to generate insights: {e}")

    return insights


def process_url(url):
    if url not in ALL_URLS:
        ALL_URLS.add(url)
        data_frames = scrape_tables_from_url(url)
        for df in data_frames:
            if not df.empty:
                insights = generate_insights(df)
                print(insights)
                with open('parallel_scrape_report.txt', 'a') as file:
                    file.write(json.dumps(insights, indent=4))
                    file.write('\n\n')
                file.close()


def find_urls(url, base_url, visited):
    if url in visited:
        return

    visited.add(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            if full_url not in ALL_URLS:
                URL_QUEUE.put(full_url)
    except requests.RequestException as e:
        print(f"Failed to process URL {url}: {e}")


def worker():
    while True:
        url = URL_QUEUE.get()
        if url is None:
            break
        process_url(url)
        URL_QUEUE.task_done()


def main(root_url):
    base_url = get_base_url(root_url)
    visited = set()

    URL_QUEUE.put(root_url)
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    find_urls(root_url, base_url, visited)
    URL_QUEUE.join()

    for _ in range(10):
        URL_QUEUE.put(None)
    for t in threads:
        t.join()


root_url = 'https://results.eci.gov.in'
print("Collecting URLs and processing...")
main(root_url)
print("Done.")
