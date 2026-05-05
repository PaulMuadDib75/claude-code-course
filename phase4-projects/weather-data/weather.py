# =============================================================================
# weather.py — Live Weather Data Fetcher
# =============================================================================
# What this script does:
#   1. Asks you to type a city name
#   2. Sends that city name to the Open-Meteo geocoding API to get GPS coordinates
#   3. Sends those coordinates to the Open-Meteo forecast API to get current weather
#   4. Displays the temperature, wind speed, and sky condition in plain English
#
# What is an API?
#   API stands for Application Programming Interface. Think of it like calling
#   dispatch on a two-way radio. You send a request ("What's the weather at
#   this location?"), and the other end sends back a structured answer.
#   Your script doesn't need to know HOW the other end figures it out —
#   it just asks and reads the response.
#
#   Open-Meteo is a free weather API. No account or API key needed.
#   Website: https://open-meteo.com
# =============================================================================

import requests  # The 'requests' library handles sending and receiving data over the internet.
                 # It is not built into Python — install it with: pip install requests
import sys       # Built-in Python library. We use it to exit the script cleanly if something goes wrong.

# Suppress the SSL warning that appears when verify=False is used.
# On corporate networks with HTTPS proxies, this warning would show on every
# API call and clutter the output. We know why it appears, so we silence it.
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =============================================================================
# WEATHER CODE DICTIONARY
# =============================================================================
# Open-Meteo returns a number called a "weathercode" that follows the WMO
# (World Meteorological Organization) standard. Each number means a specific
# sky condition. This dictionary translates those numbers into plain English.
#
# Think of it like a CEC Table — a numbered reference that maps a code to a
# real-world meaning. Code 63 in this table means "Moderate rain," just like
# Rule 12-3000 in the CEC means something specific about outlet spacing.
# =============================================================================
WEATHER_DESCRIPTIONS = {
    0:  "Clear sky",
    1:  "Mainly clear",
    2:  "Partly cloudy",
    3:  "Overcast",
    45: "Foggy",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


# =============================================================================
# FUNCTION: get_coordinates
# =============================================================================
# This function takes a city name (text) and asks the Open-Meteo Geocoding API
# to look up the GPS coordinates (latitude and longitude) for that city.
#
# Think of this like looking up a job site address in a directory. You have the
# name of the location, and you need to find the actual GPS coordinates before
# you can navigate there or call the site to ask about conditions.
#
# Parameters:
#   city_name — the text the user typed (e.g. "Edmonton")
#
# Returns:
#   A tuple of three values: (latitude, longitude, resolved_city_name)
#   A tuple is like a terminal block with three wires — three values held together.
# =============================================================================
def get_coordinates(city_name):

    # This is the Geocoding API URL. The {city_name} part gets filled in with
    # whatever city the user typed. count=1 means "give me only the top result."
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"

    # --- Making the API Call ---
    # requests.get() sends an HTTP GET request to the URL above.
    # It's like pressing the transmit button on your radio and asking a question.
    # The API server at Open-Meteo receives the request and sends back a response.
    #
    # Note on verify=False:
    # Normally, Python checks the website's SSL security certificate to confirm
    # it's talking to the real server (like checking a contractor's license).
    # On some corporate or work networks, a proxy intercepts HTTPS traffic and
    # presents its own certificate, which Python doesn't recognize — causing a
    # verification failure. Setting verify=False skips that check so the script
    # works on those networks. This is acceptable for a learning tool on a
    # trusted network, but production scripts should use proper certificates.
    print(f"\nLooking up coordinates for '{city_name}'...")
    response = requests.get(geocoding_url, verify=False)

    # --- Reading the Response ---
    # The API sends back data in JSON format (JavaScript Object Notation).
    # JSON is structured like a labelled wiring diagram — each value has a name/label.
    # .json() converts that raw text into a Python dictionary we can work with.
    data = response.json()

    # --- Checking the Result ---
    # If the API found no results, the "results" key will be missing or empty.
    # We check for that and exit with a helpful message instead of crashing.
    if "results" not in data or len(data["results"]) == 0:
        print(f"\nError: Could not find a city named '{city_name}'.")
        print("Please check the spelling and try again.")
        sys.exit(1)  # sys.exit(1) stops the script — like opening the main disconnect.

    # Pull the first result out of the list.
    # data["results"] is a list (like a row in a schedule), and [0] picks the first row.
    first_result = data["results"][0]

    # Extract the three values we need from the result.
    # These are like reading three fields off an inspection form.
    latitude  = first_result["latitude"]   # How far north or south (degrees)
    longitude = first_result["longitude"]  # How far east or west (degrees)
    city_full = first_result["name"]       # The official resolved city name

    # Return all three values together as a tuple.
    return latitude, longitude, city_full


# =============================================================================
# FUNCTION: get_weather
# =============================================================================
# This function takes GPS coordinates and calls the Open-Meteo Forecast API
# to get the current weather conditions at that location.
#
# Think of this as calling the job site directly once you have the address.
# You ask "What are current conditions?" and they read you the answer.
#
# Parameters:
#   latitude  — north/south position on Earth (decimal degrees)
#   longitude — east/west position on Earth (decimal degrees)
#
# Returns:
#   A dictionary containing current temperature, wind speed, and weather code.
# =============================================================================
def get_weather(latitude, longitude):

    # This is the Forecast API URL.
    # We pass the coordinates as parameters, and current_weather=true tells
    # the API to include the current (right now) conditions in its response.
    forecast_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&current_weather=true"
    )

    # --- Making the API Call ---
    # Same concept as before: we send a GET request and wait for the answer.
    # This time we're asking about weather conditions, not location lookup.
    # verify=False is used here for the same reason as the geocoding call above.
    print("Fetching current weather data...")
    response = requests.get(forecast_url, verify=False)

    # --- Parsing the Response ---
    # Convert the response text to a Python dictionary using .json()
    data = response.json()

    # The forecast API wraps current conditions inside a key called "current_weather".
    # We pull that sub-dictionary out and return it.
    # It contains: temperature, windspeed, weathercode, and a couple of other fields.
    current_weather = data["current_weather"]

    return current_weather


# =============================================================================
# FUNCTION: display_weather
# =============================================================================
# This function takes the city name and the weather data dictionary, then
# prints a clean, readable summary to the screen.
#
# Think of this as writing up the job site report after you've gathered all
# the information — organized, easy to read, no raw numbers without labels.
#
# Parameters:
#   city_name    — the resolved city name to display
#   weather_data — the dictionary returned by get_weather()
# =============================================================================
def display_weather(city_name, weather_data):

    # Pull each value out of the weather dictionary.
    # Dictionary keys are like wire labels — they identify what each value carries.
    temperature  = weather_data["temperature"]  # In degrees Celsius
    wind_speed   = weather_data["windspeed"]    # In km/h
    weather_code = weather_data["weathercode"]  # WMO numeric code

    # Look up the weather code in our dictionary to get the plain-English description.
    # .get() is a safe way to look up a key — if the code isn't in our dictionary,
    # it returns "Unknown conditions" instead of crashing.
    description = WEATHER_DESCRIPTIONS.get(weather_code, "Unknown conditions")

    # Print the formatted weather report.
    # The :<13 part in the f-string left-aligns the label text in a 13-character
    # wide column, so everything lines up neatly — like columns in a panel schedule.
    print("\n" + "=" * 32)
    print(f"  Weather for: {city_name}")
    print("=" * 32)
    print(f"  {'Condition':<13}: {description}")
    print(f"  {'Temperature':<13}: {temperature} °C")
    print(f"  {'Wind Speed':<13}: {wind_speed} km/h")
    print("=" * 32)


# =============================================================================
# FUNCTION: main
# =============================================================================
# This is the main function — it controls the overall flow of the script.
# It's like the main panel in a building: everything else branches off from here.
#
# Flow:
#   1. Ask user for a city name
#   2. Get coordinates for that city (geocoding API)
#   3. Get current weather for those coordinates (forecast API)
#   4. Display the results
# =============================================================================
def main():

    print("=" * 32)
    print("  Live Weather Checker")
    print("  Powered by Open-Meteo")
    print("=" * 32)

    # Ask the user to type a city name.
    # .strip() removes any accidental leading or trailing spaces the user may have typed.
    city_input = input("\nEnter a city name: ").strip()

    # Check that the user didn't just press Enter without typing anything.
    if not city_input:
        print("Error: No city name entered. Please run the script again.")
        sys.exit(1)

    # --- Wrap everything in a try/except block ---
    # This is like having a main breaker — if anything trips (an error occurs),
    # we catch it here and show a friendly message instead of a confusing Python crash.
    try:

        # Step 1: Convert city name to GPS coordinates.
        latitude, longitude, resolved_city = get_coordinates(city_input)

        # Step 2: Fetch current weather using those coordinates.
        weather_data = get_weather(latitude, longitude)

        # Step 3: Display the results in a readable format.
        display_weather(resolved_city, weather_data)

    except requests.exceptions.ConnectionError:
        # This error happens when the script can't reach the internet.
        # Like trying to call dispatch but your radio has no signal.
        print("\nError: Could not connect to the internet.")
        print("Please check your network connection and try again.")
        sys.exit(1)


# =============================================================================
# ENTRY POINT
# =============================================================================
# This is a standard Python pattern. When you run this file directly
# (python weather.py), Python sets __name__ to "__main__" and runs main().
# If this file were imported by another script, main() would NOT run automatically.
# It's like a main disconnect — it only activates when this script is in charge.
# =============================================================================
if __name__ == "__main__":
    main()
