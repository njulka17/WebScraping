import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define the URL of the website to scrape
url = 'https://results.eci.gov.in/PcResultGenJune2024/index.htm'

# Make a request to fetch the page content
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the page content with BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extract relevant data
# Note: Update these selectors based on the actual structure of the website
data = []
for row in soup.select('table tr'):
    columns = row.find_all('td')
    if columns:
        data.append([col.get_text(strip=True) for col in columns])

# Convert data to a DataFrame for processing
columns = ['Party', 'Won', 'Leading', 'Total']
df = pd.DataFrame(data, columns=columns)

# Convert numerical columns to integers
df[['Won', 'Leading', 'Total']] = df[['Won', 'Leading', 'Total']].apply(pd.to_numeric)
print(df)
# Generate 10 key insights from the data
insights = []

# Example insights
total_parties = df['Party'].nunique()
insights.append(f"Total number of parties: {total_parties}")

total_won = df['Won'].sum()
insights.append(f"Total seats won: {total_won}")

leading_party = df.loc[df['Leading'].idxmax()]
insights.append(f"Party leading in most constituencies: {leading_party['Party']} with {leading_party['Leading']} leads")

highest_total_seats = df.loc[df['Total'].idxmax()]
insights.append(f"Party with highest total seats (Won + Leading): {highest_total_seats['Party']} with "
                f"{highest_total_seats['Total']} seats")

average_won = df['Won'].mean()
insights.append(f"Average number of seats won per party: {average_won:.2f}")

party_with_most_wins = df.loc[df['Won'].idxmax()]
insights.append(f"Party with most seats won: {party_with_most_wins['Party']} with {party_with_most_wins['Won']} seats")

parties_with_no_wins = df[df['Won'] == 0]['Party'].tolist()
insights.append(f"Parties with no seats won: {', '.join(parties_with_no_wins)}")

total_leading = df['Leading'].sum()
insights.append(f"Total number of leading seats: {total_leading}")

party_with_least_total = df.loc[df['Total'].idxmin()]
insights.append(f"Party with least total seats (Won + Leading): {party_with_least_total['Party']} with "
                f"{party_with_least_total['Total']} seats")

top_5_parties_total = df.nlargest(5, 'Total')[['Party', 'Total']].values.tolist()
insights.append(f"Top 5 parties by total seats (Won + Leading):\n\t" +
                '\n\t'.join([f'{party[0]} ({party[1]})' for party in top_5_parties_total]))

# Save the report
report = '\n'.join(insights)
with open('election_report.txt', 'w') as file:
    file.write(report)

print("Report generated and saved as 'election_report.txt'")
