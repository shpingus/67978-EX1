import requests
from bs4 import BeautifulSoup
import pandas as pd
import re # Import the regular expression module

SCRAPE_ROOT = "https://www.worldometers.info/demographics/"

df_demographics = pd.DataFrame(columns=["Country",
                                        "LifeExpectancy_Both",  # (Both Sexes, in years)
                                        "LifeExpectancy_Female",  # (Females, in years)
                                        "LifeExpectancy_Male",  # (Males, in years)
                                        "UrbanPopulation_Percentage",  # (percentage without commas)
                                        "UrbanPopulation_Absolute",  # (if available)
                                        "PopulationDensity"])

# List to store data before creating DataFrame
data_list = []

try:
    # Fetch the main demographics page
    response = requests.get(SCRAPE_ROOT)
    response.raise_for_status() # Raise an exception for bad status codes
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find links to individual country pages
    # Assuming the links are in a table or list structure. You might need to inspect the page's HTML
    # to find the correct selector for the country links.
    # This is a placeholder selector, you will likely need to adjust it based on the actual HTML structure:
    country_links = soup.select("a[href*='/demographics/country/']")

    print(f"Found {len(country_links)} country links.")

    # Iterate through country links and scrape data
    for link in country_links:
        country_url = SCRAPE_ROOT + link['href'].split('/')[-2] + "/" # Construct the full URL
        country_name = link.text.strip()

        print(f"Scraping data for: {country_name} from {country_url}")

        try:
            country_response = requests.get(country_url)
            country_response.raise_for_status()
            country_soup = BeautifulSoup(country_response.content, 'html.parser')

            # Extract data points for each country
            # These selectors are placeholders and need to be adapted based on the country page HTML
            life_expectancy_both = None
            life_expectancy_female = None
            life_expectancy_male = None
            urban_population_percentage = None
            urban_population_absolute = None
            population_density = None

            # Example: Extracting Life Expectancy (Both Sexes) - You need to find the correct tag and class/id
            # Look for elements containing the text and associated values
            try:
                le_both_element = country_soup.find(text=re.compile("Life Expectancy \(Both Sexes,"))
                if le_both_element:
                    # Assuming the value is in a sibling or parent element, adjust the navigation accordingly
                    le_both_value = le_both_element.find_next('span').text.strip() # Example navigation
                    life_expectancy_both = float(re.search(r'\d+\.?\d*', le_both_value).group()) # Extract number

                le_female_element = country_soup.find(text=re.compile("Life Expectancy \(Females\)"))
                if le_female_element:
                     le_female_value = le_female_element.find_next('span').text.strip()
                     life_expectancy_female = float(re.search(r'\d+\.?\d*', le_female_value).group())

                le_male_element = country_soup.find(text=re.compile("Life Expectancy \(Males\)"))
                if le_male_element:
                    le_male_value = le_male_element.find_next('span').text.strip()
                    life_expectancy_male = float(re.search(r'\d+\.?\d*', le_male_value).group())

                urban_perc_element = country_soup.find(text=re.compile("Urban Population \(percentage"))
                if urban_perc_element:
                    urban_perc_value = urban_perc_element.find_next('span').text.strip()
                    urban_population_percentage = float(re.search(r'\d+\.?\d*', urban_perc_value).group())


                urban_abs_element = country_soup.find(text=re.compile("Urban Population \(if available")) # Check for the exact phrasing or similar
                if urban_abs_element:
                     urban_abs_value = urban_abs_element.find_next('span').text.strip().replace(',', '') # Remove commas
                     urban_population_absolute = int(re.search(r'\d+', urban_abs_value).group())

                pop_density_element = country_soup.find(text=re.compile("Population Density"))
                if pop_density_element:
                     pop_density_value = pop_density_element.find_next('span').text.strip()
                     population_density = float(re.search(r'\d+\.?\d*', pop_density_value).group())


            except Exception as e:
                print(f"Error extracting data for {country_name}: {e}")
                # Set values to None if extraction fails
                life_expectancy_both = None
                life_expectancy_female = None
                life_expectancy_male = None
                urban_population_percentage = None
                urban_population_absolute = None
                population_density = None


            # Append data to the list
            data_list.append({
                "Country": country_name,
                "LifeExpectancy_Both": life_expectancy_both,
                "LifeExpectancy_Female": life_expectancy_female,
                "LifeExpectancy_Male": life_expectancy_male,
                "UrbanPopulation_Percentage": urban_population_percentage,
                "UrbanPopulation_Absolute": urban_population_absolute,
                "PopulationDensity": population_density
            })

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {country_name}: {e}")
            # Append data with None values if fetching fails
            data_list.append({
                "Country": country_name,
                "LifeExpectancy_Both": None,
                "LifeExpectancy_Female": None,
                "LifeExpectancy_Male": None,
                "UrbanPopulation_Percentage": None,
                "UrbanPopulation_Absolute": None,
                "PopulationDensity": None
            })


    # Create DataFrame from the collected data
    df_demographics = pd.DataFrame(data_list)

    # Cast numeric fields to appropriate types
    numeric_cols = ["LifeExpectancy_Both", "LifeExpectancy_Female", "LifeExpectancy_Male",
                    "UrbanPopulation_Percentage", "UrbanPopulation_Absolute", "PopulationDensity"]
    for col in numeric_cols:
        df_demographics[col] = pd.to_numeric(df_demographics[col], errors='coerce') # Use coerce to turn errors into NaN

    # Handle missing UrbanPopulation_Absolute if UrbanPopulation_Percentage is available (optional, based on requirements)
    # If the requirement is to only fill if available on the page, the previous None handling is sufficient.


    print("\nCrawling and data extraction complete.")
    print("DataFrame created with extracted data.")
    print(df_demographics.head()) # Print head for verification

    # You can now proceed to save the DataFrame to CSV as required by the exercise

except requests.exceptions.RequestException as e:
    print(f"Error fetching the main demographics page: {e}")

print(df_demographics)