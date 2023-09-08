########################################################################################################################
import pandas as pd
import requests
import json
from google.cloud import bigquery

########################################################################################################################
# Scrap all MotoGP standings from all seasons
########################################################################################################################
# Scrap all seasons IDs
response = requests.get("https://api.motogp.pulselive.com/motogp/v1/results/seasons")

print()
# Check if the request was successful
if response.status_code == 200:
    data = response.json()  # Parse the JSON response directly

    seasons_df = pd.DataFrame(data)  # Create a DataFrame from the JSON data
    seasons_df = seasons_df[["id", "year"]]
    seasons_ids = seasons_df["id"].tolist()

    print("Seasons successfully processed:")
    print(f"This is the list: {seasons_ids}")
else:
    print("Failed to retrieve the page.")

# Scrap MotoGP category ID
response = requests.get(
    "https://api.motogp.pulselive.com/motogp/v1/results/categories?seasonUuid=db8dc197-c7b2-4c1b-b3a4-7dc723c087ed"
)

print()
# Check if the request was successful
if response.status_code == 200:
    try:
        json_data = response.json()
        print("JSON data retrieved successfully")
        print()

        # Find MotoGP category and extract its ID
        for category in json_data:
            if category["name"] == "MotoGP™":
                motogp_id = category["id"]
                print(f"MotoGP id = {motogp_id}")
                print()
                break
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
        print()
else:
    print("Failed to retrieve the page.")
    print()

########################################################################################################################
# Scrap all MotoGP seasons championships

# Initialize an empty list to hold all data
all_data = []

# Loop through seasons IDs and retrieve MotoGP standings
count = 0
for season_id in seasons_ids:
    count = count + 1
    url = f"https://api.motogp.pulselive.com/motogp/v1/results/standings?seasonUuid={season_id}&categoryUuid={motogp_id}"
    response = requests.get(url)

    print(
        f"Season ID: {season_id}, Status Code: {response.status_code}, Count = {count}"
    )
    print()

    if response.status_code == 200:
        json_data = response.json()

        # Extract relevant information from the JSON response
        data = []
        for entry in json_data.get("classification", []):
            rank = entry.get("position")
            rider_name = entry.get("rider", {}).get("full_name")
            country = entry.get("rider", {}).get("country", {}).get("iso")

            # Check if the "team" object exists before accessing its attributes
            team_info = entry.get("team")
            team_name = team_info.get("name") if team_info else "No Team"

            year = None
            if team_info and "season" in team_info:
                year = entry.get("team", {}).get("season", {}).get("year")

            constructor = entry.get("constructor", {}).get("name")

            data.append([rank, rider_name, country, team_name, constructor, year])

        # Append the data for the current season to the all_data list
        all_data.extend(data)

    else:
        print("Failed to retrieve standings for season", season_id)

# Create a DataFrame from the collected data
columns = ["Rank", "Rider Name", "Country", "Team Name", "Constructor", "Year"]
seasons_rankings_df = pd.DataFrame(all_data, columns=columns)

# Print the global DataFrame or do whatever you need with it
print()
print(seasons_rankings_df)
print()

########################################################################################################################
# Scrap MotoGP race results from all seasons
########################################################################################################################
# Define the API URLs
seasons_url = "https://api.motogp.pulselive.com/motogp/v1/results/seasons"
events_url = "https://api.motogp.pulselive.com/motogp/v1/results/events"
results_url = "https://api.motogp.pulselive.com/motogp/v1/results/session/e38536d9-bf81-4613-b0bf-91ec5ea13de1/classification?test=false"

# Fetch data from the API
seasons_response = requests.get(seasons_url)
seasons_data = seasons_response.json()

# Create an empty list to store data
results_data_list = []

# Loop through each season
for season in seasons_data:
    season_year = season["year"]

    # Fetch events data for the current season
    events_params = {"seasonUuid": season["id"], "isFinished": True}
    events_response = requests.get(events_url, params=events_params)
    events_data = events_response.json()

    # Loop through each event (race) in the current season
    for event in events_data:
        circuit_name = event["circuit"]["name"]

        # Fetch results data for the current event
        results_response = requests.get(results_url)
        results_data = results_response.json()["classification"]

        # Loop through each result in the current event
        for result in results_data:
            rank = result["position"]
            rider_name = result["rider"]["full_name"]
            nationality = result["rider"]["country"]["name"]
            team_name = result["team"]["name"]
            constructor_name = result["constructor"]["name"]

            # Append the data to the list
            results_data_list.append(
                {
                    "Season": season_year,
                    "Circuit": circuit_name,
                    "Rank": rank,
                    "Rider": rider_name,
                    "Nationality": nationality,
                    "Team": team_name,
                    "Constructor": constructor_name,
                }
            )

# Create a DataFrame from the list of data
races_rankings_df = pd.DataFrame(results_data_list)

# Display the resulting DataFrame
print(races_rankings_df)

########################################################################################################################
# Upload to GCP BigQuery
########################################################################################################################
# Construct a BigQuery client object.
client = bigquery.Client()
# Set table_id to the ID of the table to create.
table_id_races = "motogp-project-398408.motogp_dataset.motogp_races_results"
table_id_seasons = "motogp-project-398408.motogp_dataset.motogp_seasons_results"

job_config = bigquery.LoadJobConfig()

# RACES
job_races = client.load_table_from_dataframe(
    races_rankings_df, table_id_races, job_config=job_config
)  # Make an API request.
job_races.result()  # Wait for the job to complete.

table_races = client.get_table(table_id_races)  # Make an API request.
print(
    "Loaded {} rows and {} columns to {}".format(
        table_races.num_rows, len(table_races.schema), table_id_races
    )
)

# SEASONS
job_seasons = client.load_table_from_dataframe(
    seasons_rankings_df, table_id_seasons, job_config=job_config
)  # Make an API request.
job_seasons.result()  # Wait for the job to complete.

table_seasons = client.get_table(table_id_seasons)  # Make an API request.
print(
    "Loaded {} rows and {} columns to {}".format(
        table_seasons.num_rows, len(table_seasons.schema), table_id_races
    )
)
