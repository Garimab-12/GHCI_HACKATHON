import os
import requests
import streamlit as st
from diffusers import StableDiffusionPipeline
import torch

# Hardcode the API key for testing (remove this after confirming it works)
API_KEY = "1db5823cbea5194fca875d0dafc6f3a7"  # Replace with your actual API key

# Function to fetch coordinates based on city name
def get_coordinates(api_key, city):
    geocode_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        return lat, lon
    else:
        st.write(f"Error fetching coordinates: {response.status_code} - {response.text}")
        return None, None

# Function to fetch pollution data
def fetch_pollution_data(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        pollution_level = data['list'][0]['components']['co']  # Get CO levels
        return pollution_level
    else:
        st.write(f"Error fetching pollution data: {response.status_code} - {response.text}")
        return None

# Function to generate art based on pollution data
def generate_art(prompt):
    # Ensure 'assets' folder exists
    os.makedirs("assets", exist_ok=True)
    
    # Load the Stable Diffusion model
    pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
    pipe.to("cpu")  # Change to "cpu" for laptops without a GPU

    # Generate the image based on the prompt
    image = pipe(prompt).images[0]
    # Save the generated image
    image_path = "assets/generated_art.png"
    image.save(image_path)
    return image_path  # Return the path of the generated image

# Streamlit app code
if __name__ == "__main__":
    st.title("Pollution Data Art Generator")
    st.write("Welcome to the Pollution Data Art Generator app!")

    # Use the hardcoded API key for testing
    # API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Uncomment if using environment variable
    city_name = st.text_input("Enter a city name:", "Lucknow")  # User input for city name

    if st.button("Get Pollution Data"):
        lat, lon = get_coordinates(API_KEY, city_name)
        st.write(f"Coordinates: {lat}, {lon}")

        if lat is not None and lon is not None:
            pollution = fetch_pollution_data(API_KEY, lat, lon)
            st.write(f"CO levels in {city_name}: {pollution} ppm")

            # Use pollution data to create a prompt for art generation
            if pollution is not None:
                prompt = f"A futuristic city under heavy smog with pollution level {pollution} ppm"
                image_path = generate_art(prompt)
                st.image(image_path, caption="Generated Art")
            else:
                st.write("Could not fetch pollution data.")
        else:
            st.write("Could not get coordinates.")
