import json

client_details = []
client_details = client_details

client_id = str(input("Enter your client id for your Spotify API"))
client_secret = str(input("Enter your client secret for your Spotify API"))

client_details = {"client_id" : client_id,
                  "client_secret":  client_secret }

print(client_details)

with open("client_codes_Spotify.json", "w") as f:
    json.dump(client_details, f)

