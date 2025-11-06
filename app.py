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

@app.route('/synastry')
def synastry():
    """Renders the double chart (synastry) input form."""
    return render_template('synastry.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Handles form submission, calculates the horoscope, and returns the result as JSON."""
    try:
        # --- Get Form Data ---
        year = request.form.get('year')
        month = request.form.get('month')
        day = request.form.get('day')
        hour = request.form.get('hour')
        minute = request.form.get('minute')
        location_name = request.form.get('location_name')

        # Fallbacks: if time is unknown, assume 12:00
        if not hour or str(hour).strip() == '':
            hour = '12'
        if not minute or str(minute).strip() == '':
            minute = '0'

        # Basic validation for required fields
        if not year or not month or not day or not location_name:
            return jsonify({'error': 'Missing required fields: year, month, day, and location_name are required.'}), 400

        data1 = {
            'name': request.form.get('name'),  # optional
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'location_name': location_name,
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

        # --- Optional: Chart 2 ---
        year2 = request.form.get('year2')
        month2 = request.form.get('month2')
        day2 = request.form.get('day2')
        hour2 = request.form.get('hour2')
        minute2 = request.form.get('minute2')
        location_name2 = request.form.get('location_name2')

        data2 = None
        selected_aspects2 = None
        has_chart2_core = year2 and month2 and day2 and location_name2
        if has_chart2_core:
            if not hour2 or str(hour2).strip() == '':
                hour2 = '12'
            if not minute2 or str(minute2).strip() == '':
                minute2 = '0'
            data2 = {
                'name': request.form.get('name2'),  # optional
                'year': year2,
                'month': month2,
                'day': day2,
                'hour': hour2,
                'minute': minute2,
                'location_name': location_name2,
            }
            lat2, lon2 = geocode(data2['location_name'])
            if lat2 is None or lon2 is None:
                return jsonify({'error': f"Could not find location: {data2['location_name']}"}), 400
            data2['lat'] = lat2
            data2['lon'] = lon2

            selected_aspects2 = {
                'Quincunx': request.form.get('Quincunx2') == 'true',
                'Semisextile': request.form.get('Semisextile2') == 'true',
                'Semisquare': request.form.get('Semisquare2') == 'true',
                'Sesquiquadrate': request.form.get('Sesquiquadrate2') == 'true',
                'Quintile': request.form.get('Quintile2') == 'true',
                'Biquintile': request.form.get('Biquintile2') == 'true',
            }

        # --- Generate Markdown ---
        markdown_content = generate_horoscope_markdown(data1, selected_aspects1, data2, selected_aspects2)

        # --- Return Result as JSON ---
        return jsonify({'markdown': markdown_content})

    except Exception as e:
        # A simple error handler
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Note: debug=True is for development. Turn it off for production.
    app.run(debug=True)
