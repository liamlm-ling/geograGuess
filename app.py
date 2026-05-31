import os
import math
from flask import Flask, render_template, request, jsonify
from haversine import haversine, Unit
# vAIzaSyCQnMLula2xcJLhy2AlxcYzWmFLgQt4yu8


# Initialize the Flask application
app = Flask(__name__)

START_LOC = (43.6426, -79.3871)

# def begin_game():
#     # get random location available from 
#     game = gameInstance()

# Define the route for the home page
@app.route('/')
def home():
    # Render and return the HTML file
    return render_template('index.html')

@app.route('/load-game-page')
def load_game_page():
    # This is the function name used in url_for()
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    error_message = None
    if not api_key or not api_key.startswith("AIza"):
        error_message = (
            "Google Maps API key is missing or invalid. "
            "Set GOOGLE_MAPS_API_KEY in your environment to a valid key starting with 'AIza'."
        )
        api_key = None

    return render_template('gamewindow.html', api_key=api_key, error_message=error_message)

@app.route('/load-home-page')
def load_home_page():
    # This is the function name used in url_for()
    return render_template('index.html') 

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'missing json'}), 400
    lat = data.get('lat')
    lng = data.get('lng')
    if lat is None or lng is None:
        return jsonify({'error': 'missing coordinates'}), 400
    try:
        lat = float(lat)
        lng = float(lng)
    except (TypeError, ValueError):
        return jsonify({'error': 'invalid coordinates'}), 400
    print(f"Received location: {lat}, {lng}")
    dist_km = round(haversine((lat, lng), START_LOC), 2)
    if dist_km <= 0.025:
        score = 5000
    else:
        score = round(5000 * math.exp(-dist_km / 500), 0)
    print("Guess submitted!")
    print(f"Distance from location: {dist_km} km")
    print(f"Score: {score}")
    return jsonify({'status': 'ok', 'lat': lat, 'lng': lng})

# def get_distance():
#     # Placeholder: compute distance between two (lat, lng) pairs if needed.
#     # Implement using haversine or other method when required.
#     return None

# @app.route('/submit_guess')
# def submit_guess():
#     # Placeholder endpoint for submitting a guess. Implement game logic here.
#     return jsonify({'status': 'not-implemented'}), 200

# Run the app locally in debug mode
if __name__ == '__main__':
    app.run(debug=True, port=5002)