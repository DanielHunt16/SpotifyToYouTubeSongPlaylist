import json

client_details = []
client_details = client_details

# client_id = str(input("Enter your client id for your Spotify API"))
# client_secret = str(input("Enter your client secret for your Spotify API"))

client_details = {
    "client_id": "./client_secret_YouTube.json",
    "client_secret": "5ecf069dd16b4e7dba26988a2351e44e",
}

print(client_details)

with open("client_codes_Spotify.json", "w") as f:
    json.dump(client_details, f)
