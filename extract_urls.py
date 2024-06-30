from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ALL_URLS = []


# Function to extract the base URL
def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


# Function to find and print all URLs from a given page
def find_urls(url, base_url, visited):
    # Avoid revisiting the same URL
    if url in visited:
        return

    visited.add(url)
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            # if full_url.startswith(base_url) and full_url not in visited:
            if full_url not in ALL_URLS:
                ALL_URLS.append(full_url)
            lu = len(ALL_URLS)
            if lu % 10 == 0:
                print(lu)
            find_urls(full_url, base_url, visited)
    except requests.RequestException as e:
        pass


def main(root_url):
    base_url = get_base_url(root_url)
    visited = set()
    return find_urls(root_url, base_url, visited)


root_url = 'https://results.eci.gov.in'
print("Collecting URLs...")
main(root_url)
print("Done.", len(ALL_URLS), 'URLs found.')
