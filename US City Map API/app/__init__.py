from flask import Flask, request, jsonify
import psycopg2
import math
from datetime import datetime
import pytz

import os
from dotenv import load_dotenv

api = Flask(__name__)

# Load environment variables from .env file (.env file is to be created manually in root folder)
load_dotenv()

# Access the environment variables
user = os.getenv('PG_USER')
password = os.getenv('PG_PASSWORD')
uri = f"postgres://{user}:{password}@SG-SharedPostgres-3990-pgsql-master.servers.mongodirector.com/74123fa8739c7c37b6f4619d66db551c"

# Create a connection to the PostgreSQL database
conn = psycopg2.connect(uri)
cur = conn.cursor()

@api.route("/")
def welcome():
    return "Welcome to SkillReactor"


################################################################################
# Task UCM1: API to get city data
################################################################################
"""
Create API to get list of cities.
type City = {
 id: number;
 name: string;
} 

The response is City[] For pagination, the accepted params are page_size and page_num 
page_num is the number of page and page_size is the number of records to return 
For example, if this route is called: /city?page_num=1&page_size=10 this call 
should return the first ten cities sorted by ID like
[ 
   { id: 1, city: "ABC" }, 
   { id: 2, city: "DEF" },
    ... 
   { id: 1, city: "ABC" }
] 

ID is another search param. if this route is called: /city?id=2 this call should return 
the city with ID 2 like [ { id: 2, city: "DEF" } ] 

state_id is another search param. if this route is called: /city?state_id=AK this call 
should return the cities with state AK like
[ { id: 2, city: "DEF" }, { id: 5, city: "JKL" } ] 
"""
# Endpoint to get cities
@api.route('/city', methods=['GET'])
def get_cities():
    page_num = request.args.get('page_num', type=int)
    page_size = request.args.get('page_size', type=int)
    city_id = request.args.get('id')
    state_id = request.args.get('state_id')

    if city_id:
        cur.execute("SELECT id, city FROM uscitymapapi_us_cities_j_akbar WHERE id = %s", (city_id,))
        city = cur.fetchone()

        if city:
            city_data = {'id':city[0], 'city':city[1]}
            return jsonify([city_data])
        else:
            return jsonify({'message': 'City not found'})

    else:
        if page_num and page_size:
            cur.execute("SELECT id, city FROM uscitymapapi_us_cities_j_akbar ORDER BY city LIMIT %s OFFSET %s", (page_size, (page_num - 1) * page_size) )
        else:
            if state_id:
                cur.execute("SELECT id, city FROM uscitymapapi_us_cities_j_akbar WHERE state_id = %s ORDER BY city", (state_id,))
            else:
                cur.execute("SELECT id, city FROM uscitymapapi_us_cities_j_akbar ORDER BY city")
    
    cities = cur.fetchall()

    city_list = []
    for city in cities:
        city_list.append({'id': city[0], 'city': city[1]})

    return jsonify(city_list)

################################################################################


################################################################################
# Task UCM2: API to get state data
################################################################################
"""
Create an API to get a list of states. The structure of a state is defined as follows:
type State = {
  id: number;
  state: string;
}

The response format is an array of State objects:
State[]

For pagination, the accepted parameters are page_size and page_num:
page_num is the number of the page.
page_size is the number of records to return.
For example, if this route is called: /state?page_num=1&page_size=10, it should return 
the first ten states sorted by ID like:
[
  { "id": 1, "state": "ABC" },
  { "id": 2, "state": "DEF" },
  ...
  { "id": 10, "state": "XYZ" }
]

Additionally, ID is another search parameter. If this route is called: /state?id=2, it 
should return the state with ID 2, like:
[
  { "id": 2, "state": "DEF" }
]
"""
@api.route('/state', methods=['GET'])
def get_states():
    page_num = request.args.get('page_num', type=int)
    page_size = request.args.get('page_size', type=int)
    state_id = request.args.get('id')

    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'uscitymapapi_us_cities_j_akbar';")
    columns = cur.fetchall()
    print(columns)

    if state_id:
        cur.execute("SELECT distinct state_id, state_name FROM uscitymapapi_us_cities_j_akbar WHERE state_id = %s", (state_id,))
        state = cur.fetchone()
        if state:
            state_data = {'id':state[0], 'state':state[1]}
            return jsonify([state_data])
        else:
            return jsonify({'message': 'State not found'})
    else:
        if page_num and page_size:
            cur.execute("SELECT distinct state_id, state_name FROM uscitymapapi_us_cities_j_akbar ORDER BY state_id LIMIT %s OFFSET %s", (page_size, (page_num - 1) * page_size) )
        else:
            cur.execute("SELECT distinct state_id, state_name FROM uscitymapapi_us_cities_j_akbar ORDER BY state_id;")
    
    states = cur.fetchall()

    state_list = []
    for state in states:
        state_list.append({'id': state[0], 'state': state[1]})

    return jsonify(state_list)
################################################################################


################################################################################
# Task UCM3: API for finding nearest city
################################################################################
"""
It should take lat (latitude) and long (longitude) as search parameters. Then, it 
will provide the nearest city to the provided latitude and longitude coordinates, 
along with the distance to that city as calculated by Euclidean distance formula.

The structure of a city is defined as follows:
type City = {
  id: number;
  name: string;
}

If the route being called is /city/find?lat=123&lng=456, the output should be in 
the following format:
{
  "city": City,
  "distance": number
}

Output format: {  "city": City,  "distance": number} where field city should be 
of type City, and distance is a floating point number representing the Euclidean 
distance from the given city.
"""
@api.route('/city/find', methods=['GET'])
def get_nearest_city():
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)

    cur.execute("SELECT id, city, lat, lng FROM uscitymapapi_us_cities_j_akbar ORDER BY city")
    cities = cur.fetchall()

    # Calculate the Euclidean distance to each city
    distances = []
    for city in cities:
        distance = math.sqrt((float(city[2]) - lat)**2 + (float(city[3]) - lng)**2)
        distances.append({ "city": city, "distance": distance })

    # Find the nearest city
    nearest_city = min(distances, key=lambda x: x["distance"])

    # Convert to the output format
    nearest_city_data = {
        'city':{'id':nearest_city['city'][0],'name':nearest_city['city'][1]}, 
        'distance': nearest_city['distance']
        }

    return jsonify(nearest_city_data)
################################################################################


################################################################################
# Task UCM4: API to get population distribution
################################################################################
""" 
The /city/population API route should provide a distribution of cities based on 
population ranges. The key function of this route is to process all available 
city data to calculate the distribution of city populations.

The output is structured in a JSON object, where each key represents a distinct 
population range, and the corresponding value is an array of city objects that 
fall within that range.

City Object Structure: The city data is represented as objects of type City, 
defined in TypeScript as follows:
type City = {
  id: number;
  city: string;
}

Response Format: The API response is a JSON object. Each key in this object 
is a string that represents a population range, and its value is an array of City 
objects. The format of the response is:
{
  "[population range in format 'min - max']": City[]
}

Population Ranges:

Each range spans 1,000,000 in population.
Ranges start from the minimum population found in the dataset and extend up to 
the maximum population.
The range is inclusive of its starting point but exclusive of its endpoint. 
For example, a range "10000000 - 20000000" includes cities with populations of 10,000,000 
up to but not including 20,000,000.

Example Response: An example of the API response would be:
{ 
  "10000000 - 20000000": [ { "id": 1, "city": "ABC" } ], 
  "20000000 - 30000000": [ { "id": 5, "city": "DEF" } ]  
}
"""
@api.route('/city/population', methods=['GET'])
def get_population_distribution():

    cur.execute("SELECT id, city, population FROM uscitymapapi_us_cities_j_akbar ORDER BY city")
    cities = cur.fetchall()

    min_population = cities[0][2]
    max_population = cities[0][2]

    # Loop through the cities list using a for loop
    for city in cities:
        print(city)
        if(min_population > city[2]):
            min_population = city[2]
        if(max_population < city[2]):
            max_population = city[2]

    print(min_population)
    print(max_population)
    gap = 1000000

    response = {}

    # Loop through the range with a gap of 1000000
    for start in range(0, max_population + gap, gap):
        end = min(start + gap, max_population + gap)
        if start > max_population:
            break
        print(f"{start} - {end}")
        response[f"{start} - {end}"] = []
        for city in cities:
            if city[2] >= start and city[2] < end:
                response[f"{start} - {end}"].append({"id":city[0], "city":city[1]})

    return response
################################################################################
    

################################################################################
# Task UCM5: API to get timezones
################################################################################
"""
Returns a list of distinct time zones along with the current time 
in each of these zones. The response is structured as an array of 
TimeDef objects, where each object includes the time zone's name 
and the corresponding current time.

The TimeDef type is defined as follows:
type TimeDef = {
    name: string;  // The name of the time zone
    time: string;  // The current time in that time zone in the ISO format 'YYYY-MM-DDTHH:mm:ss.SSSZ'
}
Example Response:
[ 
   {
      "name": "America/New_York",
       "time": "2023-11-25T17:06:02.324Z"
    },
   {
      "name": "America/Los_Angeles",
      "time": "2023-11-25T17:06:02.324Z"
   }
   …
   {
      "name": "America/Chicago",
      "time": "2023-11-25T17:06:02.324Z"
   } 
] 
"""
@api.route('/time', methods=['GET'])
def get_time():

    time_defs = []  # Create an empty list to store TimeDef objects

    cur.execute("SELECT distinct timezone FROM uscitymapapi_us_cities_j_akbar;")
    time_zones = cur.fetchall()

    # Iterate over each time zone and get the current time
    for zone in time_zones:
        timezone = pytz.timezone(zone[0])
        current_time = datetime.now(timezone).strftime('%Y-%m-%dT%H:%M:%S.%fZ') #current time in time zone in the ISO format 'YYYY-MM-DDTHH:mm:ss.SSSZ'
        time_defs.append({ "name": zone[0], "time": current_time })

    return time_defs
################################################################################


    