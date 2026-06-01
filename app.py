import os
import json
import math
import random
from flask import Flask, render_template, request, jsonify, session
from haversine import haversine, Unit

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-prod")

# def begin_game():
#     # get random location available from 
#     game = gameInstance()

# Define the route for the home page
@app.route('/')
def home():
    # Render and return the HTML file
    return render_template('index.html')

def _load_pool():
    try:
        with open("locations.json") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

_location_pool = _load_pool()

@app.route('/load-game-page')
def load_game_page():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key or not api_key.startswith("AIza"):
        return render_template('gamewindow.html', api_key=None, coords={},
            error_message="Google Maps API key is missing or invalid. "
                          "Set GOOGLE_MAPS_API_KEY in your environment to a valid key starting with 'AIza'.")

    if not _location_pool:
        return render_template('gamewindow.html', api_key=api_key, coords={},
            error_message="Location pool is empty. Run generate_pool.py first.")

    loc = random.choice(_location_pool)
    session['start_loc'] = (loc['lat'], loc['lng'])
    return render_template('gamewindow.html', api_key=api_key, error_message=None, coords=loc)

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
    start_loc = session.get('start_loc')
    if not start_loc:
        return jsonify({'error': 'no active game'}), 400

    dist_km = round(haversine((lat, lng), start_loc), 2)
    if dist_km <= 0.025:
        score = 5000
    else:
        score = round(5000 * math.exp(-dist_km / 500), 0)

    print("Guess submitted!")
    print(f"Distance from location: {dist_km} km")
    print(f"Score: {score}")
    return jsonify({
        'status': 'ok',
        'lat': lat,
        'lng': lng,
        'distance_km': dist_km,
        'score': score,
    })

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
    app.run(debug=True, port=5003)