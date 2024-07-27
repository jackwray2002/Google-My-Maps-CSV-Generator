#####################################################################################
#GOOGLE MYMAPS CSV GENERATOR
#   Author: Jack Ray
#   Date: 7/25/24
#
#CONTEXT:
#   A module which writes a csv file that can be imported into google my maps, it 
#   lists nearby locations that match a specified keyword and shows their hours.
#

from sys import modules
from types import ModuleType
from googlemaps import Client
from csv import writer
from time import sleep
from os import listdir, getcwd, remove
from os.path import join

class _Write_Location_CSV(ModuleType):
    def __call__(self, latitude: float, longitude: float, radius: int,
    keyword: str, file_name: str, api_key: str) -> None:
        COORDS = (latitude, longitude) # Coordinate pair created from arguments
        RADIUS = radius * 5280 * 0.3048 # Miles converted to meters
        KEYWORD = keyword # Argument for search keyword
        FILE_NAME = file_name # Argument for .csv file name

        client = Client(key = api_key) # Google maps client instance initialization
        token = None # Token initialized as None
        place_list = [] # List stores values to be written to .csv file

        while True:
            sleep(2) # Cooldown to not overwhelm servers

            # Initialization condition, places_nearby initialized from arguments
            if(token == None):
                places = client.places_nearby(
                location = COORDS,
                radius = RADIUS,
                keyword = KEYWORD)
            
            # Condition to continue search if next_page_token given last iteration
            else: 
                try: places = client.places_nearby(page_token = token)
                except: break
            
            # Push each entry from places_nearby search 
            for place in places['results']:

                # Anticipate failure(s) to read hours
                try:
                    # Create search query instance
                    hours_list = client.place(place_id = place["place_id"]
                    )["result"]["opening_hours"]["weekday_text"]

                    # Iterate through entries and format them accordingly
                    for i in range(7):
                        hours_list[i] = str(hours_list[i].encode("ASCII",
                        errors="replace")).replace("?", " ")[2:-1]

                        hours_list[i] = hours_list[i][hours_list[i].find(":") + 2:]
                
                # Handle error by writing "N/A" for entries instead
                except Exception:
                    hours_list = []
                    for i in range(7): hours_list.insert(i, "N/A")

                # Update place_list with values to insert into each column
                place_list.append([str(place["name"]), place["vicinity"],
                str(round(place["geometry"]["location"]["lat"], 6)), 
                str(round(place["geometry"]["location"]["lng"], 6)),
                hours_list[6], hours_list[0], hours_list[1], hours_list[2], 
                hours_list[3], hours_list[4], hours_list[5]])

            # Pass token to subsequent search, break loop if no token recieved
            if "next_page_token" in places: token = places["next_page_token"]
            else: break

        # Remove .csv file of same name if it already exists in working directory
        if FILE_NAME in listdir(getcwd()): remove(join(getcwd(), FILE_NAME))

        # Initialize csv file
        csv_file = open(FILE_NAME, "a", newline='')
        csv_writer = writer(csv_file)
        csv_writer.writerow(["Name", "Address", "Latitude", "Longitude",
        "Sunday Hours", "Monday Hours", "Tuesday Hours", "Wednesday Hours",
        "Thursday Hours", "Friday hours", "Saturday Hours"])

        # Write data to csv file
        csv_writer.writerows(place_list)

modules[__name__].__class__ = _Write_Location_CSV