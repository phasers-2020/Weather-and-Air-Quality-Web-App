import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

api_key = "APIKeyHere"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

# Cache data to optimize performance
@st.cache_data
def map_creator(latitude, longitude):
    m = folium.Map(location=[latitude, longitude], zoom_start=10)
    folium.Marker([latitude, longitude], popup="Location", tooltip="Location").add_to(m)
    folium_static(m)

@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    return requests.get(countries_url).json()

@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    return requests.get(states_url).json()

@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    return requests.get(cities_url).json()

# Selection categories
category = st.selectbox("Choose Location Method", ["By City, State, and Country", "By Nearest City (IP Address)", "By Latitude and Longitude"])

# Option: By City, State, and Country
if category == "By City, State, and Country":
    countries_dict = generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list = [i["country"] for i in countries_dict["data"]]
        countries_list.insert(0, "")
        country_selected = st.selectbox("Select a country", options=countries_list)

        if country_selected:
            states_dict = generate_list_of_states(country_selected)
            if states_dict["status"] == "success":
                states_list = [i["state"] for i in states_dict["data"]]
                states_list.insert(0, "")
                state_selected = st.selectbox("Select a state", options=states_list)

                if state_selected:
                    cities_dict = generate_list_of_cities(state_selected, country_selected)
                    if cities_dict["status"] == "success":
                        cities_list = [i["city"] for i in cities_dict["data"]]
                        cities_list.insert(0, "")
                        city_selected = st.selectbox("Select a city", options=cities_list)

                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()

                            if aqi_data_dict["status"] == "success":
                                data = aqi_data_dict["data"]["current"]
                                location_data = aqi_data_dict["data"]["location"]["coordinates"]


                                st.write(f"### Weather and Air Quality for {city_selected}, {state_selected}, {country_selected}")
                                st.write(f"Temperature: {data['weather']['tp']}°C")
                                st.write(f"Humidity: {data['weather']['hu']}%")
                                st.write(f"Air Quality Index (AQI): {data['pollution']['aqius']}")

                                map_creator(location_data[1], location_data[0])
                            else:
                                st.warning("No data available for this location.")
                    else:
                        st.warning("No cities available, please select another state.")
            else:
                st.warning("No states available, please select another country.")
    else:
        st.error("Too many requests. Wait for a few minutes before your next API call.")

# Option: Lat and Long
elif category == "By Latitude and Longitude":
    latitude = st.text_input("Enter your latitude")
    longitude = st.text_input("Enter your longitude")

    if latitude and longitude:
        url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
        aqi_data_dict = requests.get(url).json()

        if aqi_data_dict["status"] == "success":
            data = aqi_data_dict["data"]["current"]

            st.write("### Weather and Air Quality for your location")
            st.write(f"Temperature: {data['weather']['tp']}°C")
            st.write(f"Humidity: {data['weather']['hu']}%")
            st.write(f"Air Quality Index (AQI): {data['pollution']['aqius']}")
            map_creator(float(latitude), float(longitude))
        else:
            st.warning("No data available for this location.")

# Option: Nearest City
elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
        # Extract the weather and pollution data
        data = aqi_data_dict["data"]["current"]
        
        # Get the exact coordinates for the nearest city
        location_coords = aqi_data_dict["data"]["location"]["coordinates"]  # Expected to be [longitude, latitude]

        # Display weather and air quality information
        st.write("### Weather and Air Quality for Nearest City")
        st.write(f"Temperature: {data['weather']['tp']}°C")
        st.write(f"Humidity: {data['weather']['hu']}%")
        st.write(f"Air Quality Index (AQI): {data['pollution']['aqius']}")

        # Display the map with correct coordinates
        map_creator(latitude=location_coords[1], longitude=location_coords[0])
    else:
        st.warning("No data available for this location.")
