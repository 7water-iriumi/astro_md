from flask import Flask, render_template, request, jsonify
import os
import swisseph as swe
from astrology_logic import generate_horoscope_markdown, geocode

app = Flask(__name__)

# --- Swiss Ephemeris Setup ---
# It's crucial to set the path to the ephemeris files.
# These files need to be downloaded separately and placed in the 'ephe' directory.
base_dir = os.path.dirname(os.path.abspath(__file__))
ephe_path = os.path.join(base_dir, 'ephe')
swe.set_ephe_path(ephe_path)

@app.route('/')
def index():
    """Renders the main input form."""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handles form submission, calculates the horoscope, and returns the result as JSON."""
    try:
        # --- Get Form Data ---
        data1 = {
            'name': request.form.get('name'),
            'year': request.form.get('year'),
            'month': request.form.get('month'),
            'day': request.form.get('day'),
            'hour': request.form.get('hour'),
            'minute': request.form.get('minute'),
            'location_name': request.form.get('location_name')
        }

        # --- Geocode Location ---
        lat, lon = geocode(data1['location_name'])
        if lat is None or lon is None:
            return jsonify({'error': f"Could not find location: {data1['location_name']}"}), 400
        
        data1['lat'] = lat
        data1['lon'] = lon

        # --- Get Selected Minor Aspects ---
        selected_aspects1 = {
            'Quincunx': request.form.get('Quincunx') == 'true',
            'Semisextile': request.form.get('Semisextile') == 'true',
            'Semisquare': request.form.get('Semisquare') == 'true',
            'Sesquiquadrate': request.form.get('Sesquiquadrate') == 'true',
            'Quintile': request.form.get('Quintile') == 'true',
            'Biquintile': request.form.get('Biquintile') == 'true',
        }

        # --- Generate Markdown ---
        markdown_content = generate_horoscope_markdown(data1, selected_aspects1)

        # --- Return Result as JSON ---
        return jsonify({'markdown': markdown_content})

    except Exception as e:
        # A simple error handler
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Note: debug=True is for development. Turn it off for production.
    app.run(debug=True)