import requests
from bs4 import BeautifulSoup
import pandas as pd
import re  # Import the regular expression module
from tqdm import tqdm

output_path = "../output/"

SCRAPE_SOURCE = "https://www.worldometers.info/demographics/"
SCRAPE_ROOT = "https://www.worldometers.info"
response = requests.get(SCRAPE_SOURCE)
response.raise_for_status()  # Raise an exception for bad status codes
soup = BeautifulSoup(response.content, 'html.parser')

# Initialize a list to collect demographic data
demographics_data = []

df_demographics = pd.DataFrame(columns=["Country",
                                        "LifeExpectancy_Both",  # (Both Sexes, in years)
                                        "LifeExpectancy_Female",  # (Females, in years)
                                        "LifeExpectancy_Male",  # (Males, in years)
                                        "UrbanPopulation_Percentage",  # (percentage without commas)
                                        "UrbanPopulation_Absolute",  # (if available)
                                        "PopulationDensity"])
progress_bar = tqdm(soup.find_all(attrs={'data-country': True}))
for country_link in progress_bar:
    progress_bar.set_description(f"Scraping data for {country_link.text.strip()}")

    country_url = SCRAPE_ROOT + soup.find_all(attrs={'data-country': True})[0]['href']
    country_url = SCRAPE_ROOT + country_link['href']  # Fixed to use current country_link

    response = requests.get(country_url)
    country_soup = BeautifulSoup(response.content, 'html.parser')

    # Get life expectancies
    expectancies = map( lambda x: float(x.text.strip()), country_soup.find_all(attrs={'class': 'grid grid-col-1 lg:grid-cols-3 gap-4'})[0].find_all(
                          attrs={'class': 'text-2xl font-bold mb-1.5'}))

    expectancies = list(expectancies)  # Convert map object to list

    # Get urban population data
    populations= re.findall('\d+\.?\d+',
                        country_soup.find(lambda tag: tag.name == 'p' and 'Currently' in tag.text).text.replace(',', ''))[0:2]
    # Dealing with lack of absolute number
    if len(populations) == 1:
        populations.append('None')

    # Get population density
    density = re.findall('\d+\.?\d+',
                        country_soup.find(lambda tag: tag.name == 'p' and 'population density in ' in tag.text).text.replace(',', ''))[0:2]
    populations.append(density[1])
    # Populations = [percentage urban, total population, population density per sqkm]

    # Append data as a list to demographics_data
    demographics_data.append([
        country_link.text.strip(),  # Country name
        *expectancies,              # Life expectancy (Both, Female, Male)
        *populations               # Urban population percentage, absolute, and density
    ])


# Create DataFrame from collected data
df_demographics = pd.DataFrame(
    demographics_data,
    columns=["Country", "LifeExpectancy_Both", "LifeExpectancy_Female", "LifeExpectancy_Male",
             "UrbanPopulation_Percentage", "UrbanPopulation_Absolute", "PopulationDensity"]
).apply(pd.to_numeric, errors='ignore')

# df_demographics.to_csv(output_path + 'demographics_data.csv', index=False)
# head = df_demographics.head(10)
# head.to_csv(output_path + 'demographics_before_sort.csv', index=False)
# head.sort_values('Country', inplace=False).to_csv(output_path + 'demographics_after_sort.csv', index=False)