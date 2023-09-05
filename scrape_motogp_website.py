import json

import pandas as pd
import requests

########################################################################################################################
# Scrap all seasons IDs
########################################################################################################################

response = requests.get("https://api.motogp.pulselive.com/motogp/v1/results/seasons")

# Check if the request was successful
if response.status_code == 200:
    data = response.json()  # Parse the JSON response directly

    seasons_df = pd.DataFrame(data)  # Create a DataFrame from the JSON data
    seasons_df = seasons_df[["id", "year"]]
    seasons_ids = seasons_df["id"].tolist()

    print()
    print("Seasons successfully processed:")
    print(f"This is the list: {seasons_ids}")
else:
    print()
    print("Failed to retrieve the page.")

########################################################################################################################
# Scrap MotoGP ID
########################################################################################################################

response = requests.get(
    "https://api.motogp.pulselive.com/motogp/v1/results/categories?seasonUuid=db8dc197-c7b2-4c1b-b3a4-7dc723c087ed"
)

# Check if the request was successful
if response.status_code == 200:
    try:
        json_data = response.json()
        print()
        print("MotoGP categories retrieved successfully")

        # Find MotoGP category and extract its ID
        for category in json_data:
            if category["name"] == "MotoGP™":
                motogp_id = category["id"]
                print(f"MotoGP id = {motogp_id}")
                break
    except json.JSONDecodeError:
        print()
        print("Failed to parse JSON response.")
else:
    print()
    print("Failed to retrieve the page.")

########################################################################################################################
# Scrap all MotoGP seasons championships
########################################################################################################################
print()
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
global_df = pd.DataFrame(all_data, columns=columns)

# Print the global DataFrame or do whatever you need with it
print()
print(global_df)

global_df.to_parquet("scraper_datas.parquet", index=False)
