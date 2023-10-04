import requests
import pandas as pd
import json
import time
from datetime import datetime

# Start timer
startTime = time.time()

# Print timestamp
print(f"--- *** {datetime.now()} *** ---")


########################################################################################################################
# RUN
########################################################################################################################
# Define the API endpoint for seasons
seasons_url = "https://api.motogp.pulselive.com/motogp/v1/results/seasons"
# Request data from the API
seasons_response = requests.get(seasons_url).json()
# Create a dictionary with season years as keys and their IDs as values
seasons_dict = {str(season["year"]): season["id"] for season in seasons_response}

print("")
print("")
print("Seasons collected")


########################################################################################################################
# Find the MotoGP category ID
motogp_id = None
# Define the API endpoint for categories
categories_url = "https://api.motogp.pulselive.com/motogp/v1/results/categories?eventUuid=14bd179e-a4bc-4b0d-bd2e-69a9ed99cb60"
# Request data from the API
categories_response = requests.get(categories_url).json()

# Find MotoGP category ID
for category in categories_response:
    if "MotoGP" in category["name"]:
        motogp_id = category["id"]
        break

print("")
print("")
print("MotoGP category collected")


########################################################################################################################
# Initialize empty lists for event data, race data, and championship rank data
all_events_data = []
all_races_data = []
championship_ranks_data = []

# Iterate through each season and fetch event data
for season_year, season_id in seasons_dict.items():
    # Define the API endpoint for events of a specific season
    events_url = f"https://api.motogp.pulselive.com/motogp/v1/results/events?seasonUuid={season_id}&isFinished=true"
    # Request data from the API
    events_response = requests.get(events_url).json()

    # Create a DataFrame with relevant columns from events_response
    events_data = []
    for event in events_response:
        events_data.append(
            {
                "season_year": season_year,
                "event_name": event["name"],
                "event_id": event["id"],
                "country": event.get("country", {}).get("name"),
                "circuit_name": event.get("circuit", {}).get("name"),
                "toad_api_uuid": event.get("toad_api_uuid"),
            }
        )

    # Append the event data for this season to the overall list
    all_events_data.extend(events_data)

# Create a DataFrame containing information from all seasons
events_df = pd.DataFrame(all_events_data)

# Filter and drop rows where "TEST" is in the "event_name" column
events_df = events_df[~events_df["event_name"].str.contains("TEST")]

events_df = events_df.drop_duplicates()
events_df.reset_index(drop=True, inplace=True)

print("")
print("")
print("Seasons events collected")


########################################################################################################################
# Create empty lists to store latitude and longitude data
circuit_lat_list = []
circuit_long_list = []

# Iterate through events in events_df
for event_uuid in events_df["toad_api_uuid"]:
    # Define the API endpoint for the coordinates of a specific event
    coordinates_request = (
        f"https://api.motogp.pulselive.com/motogp/v1/events/{event_uuid}"
    )

    # Send a request to the API
    coordinates_response = requests.get(coordinates_request).json()

    # Extract latitude and longitude from the response
    circuit_lat = coordinates_response.get("circuit", {}).get("lat")
    circuit_long = coordinates_response.get("circuit", {}).get("lng")

    # Append the data to the respective lists
    circuit_lat_list.append(circuit_lat)
    circuit_long_list.append(circuit_long)

# Create the circuit_coord_df DataFrame with 'toad_api_uuid', 'circuit_lat', and 'circuit_long' columns
circuit_coord_df = pd.DataFrame(
    {
        "toad_api_uuid": events_df["toad_api_uuid"],
        "circuit_lat": circuit_lat_list,
        "circuit_lng": circuit_long_list,
    }
)

print("")
print("")
print("Circuit coordinates collected")

# Merge event_df and circuit_coord_df on 'toad_api_uuid'
events_df = events_df.merge(circuit_coord_df, on="toad_api_uuid", how="left")

events_df = events_df.drop_duplicates()
events_df.reset_index(drop=True, inplace=True)


########################################################################################################################
# Iterate through each event and fetch race data
for event_id in events_df["event_id"]:
    # Define the API endpoint for race sessions of a specific event
    events_types_url = f"https://api.motogp.pulselive.com/motogp/v1/results/sessions?eventUuid={event_id}&categoryUuid={motogp_id}"

    # Request data from the API
    events_types_response = requests.get(events_types_url).json()

    # Filter and extract data for races (type == "RAC")
    races_data = []
    for session in events_types_response:
        if session["type"] == "RAC":
            races_data.append(
                {
                    "event_id": event_id,
                    "circuit_name": session["circuit"],
                    "race_id": session["id"],
                }
            )

    # Append the race data for this event to the overall list
    all_races_data.extend(races_data)

# Create a DataFrame containing race information from all events
events_types_df = pd.DataFrame(all_races_data)

# Merge event_df and events_types_df on 'event_id'
races_df = events_df.merge(events_types_df, on="event_id", how="left")

# Rename columns and drop duplicates
races_df = races_df.drop(["circuit_name_y"], axis=1)
races_df = races_df.rename(columns={"circuit_name_x": "circuit_name"})
races_df = races_df.drop_duplicates()
races_df.reset_index(drop=True, inplace=True)

print("")
print("")
print("Races collected")


########################################################################################################################
# Define the base URL for fetching championship ranks
base_url = "https://api.motogp.pulselive.com/motogp/v1/results/session"

# Iterate through each race_id in races_df
for race_id in races_df["race_id"]:
    # Define the API endpoint for fetching championship ranks
    ranks_url = f"{base_url}/{race_id}/classification?test=false"

    try:
        # Request data from the API
        ranks_response = requests.get(ranks_url)
        ranks_response.raise_for_status()  # Raise an error for non-OK responses

        # Parse the JSON response
        ranks_data = ranks_response.json()

        # Iterate through the ranks in the response and extract relevant information
        for rank in ranks_data.get("classification", []):
            rider_info = rank.get("rider", {})
            country_info = rider_info.get("country", {})
            team_info = rank.get("team", {})
            constructor_info = rank.get("constructor", {})

            championship_ranks_data.append(
                {
                    "season_year": races_df.loc[
                        races_df["race_id"] == race_id, "season_year"
                    ].values[0],
                    "event_name": races_df.loc[
                        races_df["race_id"] == race_id, "event_name"
                    ].values[0],
                    "event_id": races_df.loc[
                        races_df["race_id"] == race_id, "event_id"
                    ].values[0],
                    "circuit_country": races_df.loc[
                        races_df["race_id"] == race_id, "country"
                    ].values[0],
                    "circuit_name": races_df.loc[
                        races_df["race_id"] == race_id, "circuit_name"
                    ].values[0],
                    "circuit_lat": races_df.loc[
                        races_df["race_id"] == race_id, "circuit_lat"
                    ].values[0],
                    "circuit_lng": races_df.loc[
                        races_df["race_id"] == race_id, "circuit_lng"
                    ].values[0],
                    "race_id": race_id,
                    "rider_name": rider_info.get("full_name", ""),
                    "rider_country": country_info.get("name", ""),
                    "team_name": team_info.get("name", ""),
                    "constructor_name": constructor_info.get("name", ""),
                    "position": rank.get("position", ""),
                }
            )
    except requests.exceptions.HTTPError as e:
        # Handle HTTP error, such as 404 Not Found or 500 Internal Server Error
        print(f"HTTP Error: {e}")
    except json.JSONDecodeError as e:
        # Handle JSON decode error (invalid JSON response)
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {e}")

print("")
print("")
print("Races results collected")


# Create the championship_ranks_df DataFrame, drop duplicates, and reset the index
championship_ranks_df = pd.DataFrame(championship_ranks_data)
championship_ranks_df = championship_ranks_df.drop_duplicates()
championship_ranks_df.reset_index(drop=True, inplace=True)

# Export data to CSV
championship_ranks_df.to_csv("collect_motogp_datas.csv", index=False)


########################################################################################################################
# TIMER
########################################################################################################################
endTime = time.time()
executionTime = endTime - startTime
print("")
print("")
print(
    f"--- *** Total execution time in seconds: {executionTime}, in minutes: {executionTime/60} and in hours: {executionTime/60/60} *** ---"
)
print("")
print("")
