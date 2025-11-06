import swisseph as swe
import os
import sys
import requests

# --- Core Calculation and Markdown Generation Logic ---
def format_aspect_string(p1_name, p2_name, aspect_name, orb):
    """Formats the aspect string with special handling for MC/ASC oppositions."""
    # Handle MC/IC
    if aspect_name == 'Opposition' and p2_name == 'MC':
        return f"{p1_name} Conjunction IC (Orb: {orb:.2f}°)"
    if aspect_name == 'Opposition' and p1_name == 'MC':
        return f"{p2_name} Conjunction IC (Orb: {orb:.2f}°)"
    # Handle ASC/DSC
    if aspect_name == 'Opposition' and p2_name == 'ASC':
        return f"{p1_name} Conjunction DSC (Orb: {orb:.2f}°)"
    if aspect_name == 'Opposition' and p1_name == 'ASC':
        return f"{p2_name} Conjunction DSC (Orb: {orb:.2f}°)"
    
    # Default formatting
    return f"{p1_name} {aspect_name} {p2_name} (Orb: {orb:.2f}°)"

def get_house_for_point(point_lon, house_cusps):
    """Determines the house number (1-12) for a given point longitude."""
    for i in range(12):
        cusp_start = house_cusps[i]
        cusp_end = house_cusps[(i + 1) % 12]

        if cusp_start < cusp_end:
            if cusp_start <= point_lon < cusp_end:
                return i + 1
        else:
            if point_lon >= cusp_start or point_lon < cusp_end:
                return i + 1
    return None

def detect_complex_aspects(chart_points, aspects_to_calculate):
    complex_aspects = []
    
    filtered_chart_points = [p for p in chart_points if p['name'] not in ['ASC', 'MC']]
    
    def has_aspect(p1_name, p2_name, target_aspect_name, orb_tolerance=None):
        for i in range(len(chart_points)):
            if chart_points[i]['name'] == p1_name:
                point1 = chart_points[i]
                break
        else:
            return False

        for i in range(len(chart_points)):
            if chart_points[i]['name'] == p2_name:
                point2 = chart_points[i]
                break
        else:
            return False

        angle = abs(point1['lon'] - point2['lon'])
        if angle > 180: angle = 360 - angle

        for aspect_name, (aspect_angle, orb) in aspects_to_calculate.items():
            if aspect_name == target_aspect_name:
                current_orb = orb_tolerance if orb_tolerance is not None else orb
                if abs(angle - aspect_angle) <= current_orb:
                    return True
        return False

    # YOD detection
    for i in range(len(filtered_chart_points)):
        for j in range(i + 1, len(filtered_chart_points)):
            for k in range(j + 1, len(filtered_chart_points)):
                p1 = filtered_chart_points[i]
                p2 = filtered_chart_points[j]
                p3 = filtered_chart_points[k]

                if has_aspect(p1['name'], p2['name'], 'Sextile') and \
                   has_aspect(p3['name'], p1['name'], 'Quincunx') and \
                   has_aspect(p3['name'], p2['name'], 'Quincunx'):
                    complex_aspects.append({
                        'type': 'YOD',
                        'planets': [p1['name'], p2['name'], p3['name']],
                        'apex_planet': p3['name'],
                        'aspects': [
                            f"{p1['name']} Sextile {p2['name']}",
                            f"{p3['name']} Quincunx {p1['name']}",
                            f"{p3['name']} Quincunx {p2['name']}"
                        ]
                    })
                elif has_aspect(p1['name'], p3['name'], 'Sextile') and \
                     has_aspect(p2['name'], p1['name'], 'Quincunx') and \
                     has_aspect(p2['name'], p3['name'], 'Quincunx'):
                    complex_aspects.append({
                        'type': 'YOD',
                        'planets': [p1['name'], p3['name'], p2['name']],
                        'apex_planet': p2['name'],
                        'aspects': [
                            f"{p1['name']} Sextile {p3['name']}",
                            f"{p2['name']} Quincunx {p1['name']}",
                            f"{p2['name']} Quincunx {p3['name']}"
                        ]
                    })
                elif has_aspect(p2['name'], p3['name'], 'Sextile') and \
                     has_aspect(p1['name'], p2['name'], 'Quincunx') and \
                     has_aspect(p1['name'], p3['name'], 'Quincunx'):
                    complex_aspects.append({
                        'type': 'YOD',
                        'planets': [p2['name'], p3['name'], p1['name']],
                        'apex_planet': p1['name'],
                        'aspects': [
                            f"{p2['name']} Sextile {p3['name']}",
                            f"{p1['name']} Quincunx {p2['name']}",
                            f"{p1['name']} Quincunx {p3['name']}"
                        ]
                    })
    
    # Cradle detection
    for i in range(len(filtered_chart_points)):
        for j in range(i + 1, len(filtered_chart_points)):
            for k in range(j + 1, len(filtered_chart_points)):
                for l in range(k + 1, len(filtered_chart_points)):
                    p1 = filtered_chart_points[i]
                    p2 = filtered_chart_points[j]
                    p3 = filtered_chart_points[k]
                    p4 = filtered_chart_points[l]

                    if has_aspect(p1['name'], p2['name'], 'Opposition'):
                        if (has_aspect(p3['name'], p1['name'], 'Trine') and has_aspect(p3['name'], p2['name'], 'Sextile')) or \
                           (has_aspect(p3['name'], p1['name'], 'Sextile') and has_aspect(p3['name'], p2['name'], 'Trine')):
                            if (has_aspect(p4['name'], p2['name'], 'Trine') and has_aspect(p4['name'], p1['name'], 'Sextile')) or \
                               (has_aspect(p4['name'], p2['name'], 'Sextile') and has_aspect(p4['name'], p1['name'], 'Trine')):
                                complex_aspects.append({
                                    'type': 'Cradle',
                                    'planets': [p1['name'], p2['name'], p3['name'], p4['name']],
                                    'aspects': [
                                        f"{p1['name']} Opposition {p2['name']}",
                                        f"{p3['name']} Trine/Sextile to {p1['name']} and {p2['name']}",
                                        f"{p4['name']} Trine/Sextile to {p1['name']} and {p2['name']}"
                                    ]
                                })
    return complex_aspects

def calculate_chart(birth_data, selected_aspects=None):
    """Calculates all astrological points for a single birth data object."""
    try:
        # Coalesce None to empty string to support optional name
        name = (birth_data.get('name') or '').strip()
        year = int(birth_data['year'])
        month = int(birth_data['month'])
        day = int(birth_data['day'])
        hour = int(birth_data['hour'])
        minute = int(birth_data['minute'])
        lat = float(birth_data['lat'])
        lon = float(birth_data['lon'])
        location_name = birth_data.get('location_name', f"Lat {lat}, Lon {lon}")
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid or missing data for chart '{name}': {e}")

    hour_jst = hour + minute / 60
    hour_ut = hour_jst - 9
    jd = swe.julday(year, month, day, hour_ut)

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
        "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
        "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
    }
    
    chart_points = []
    for planet_name, planet_id in planet_ids.items():
        result = swe.calc_ut(jd, planet_id)
        if result:
            lon_val = result[0][0] if isinstance(result[0], (list, tuple)) else result[0]
            chart_points.append({'name': planet_name, 'lon': lon_val})

    houses, ascmc = swe.houses(jd, lat, lon, b'P')
    chart_points.append({'name': 'ASC', 'lon': ascmc[0]})
    chart_points.append({'name': 'MC', 'lon': ascmc[1]})

    all_aspects_def = {
        'Conjunction': (0, 8), 'Opposition': (180, 8), 'Trine': (120, 7),
        'Square': (90, 7), 'Sextile': (60, 5),
        'Quincunx': (150, 2), 'Semisextile': (30, 2), 'Semisquare': (45, 2),
        'Sesquiquadrate': (135, 2), 'Quintile': (72, 2), 'Biquintile': (144, 2),
    }
    
    aspects_to_calculate = {}
    for aspect_name in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']:
        if aspect_name in all_aspects_def:
            aspects_to_calculate[aspect_name] = all_aspects_def[aspect_name]

    if selected_aspects:
        for aspect_name, is_selected in selected_aspects.items():
            if is_selected and aspect_name not in aspects_to_calculate and aspect_name in all_aspects_def:
                aspects_to_calculate[aspect_name] = all_aspects_def[aspect_name]
    
    found_aspects = []
    sensitive_points = ['ASC', 'MC']
    for i in range(len(chart_points)):
        for j in range(i + 1, len(chart_points)):
            p1, p2 = chart_points[i], chart_points[j]

            if p1['name'] in sensitive_points and p2['name'] in sensitive_points:
                continue

            angle = abs(p1['lon'] - p2['lon'])
            if angle > 180: angle = 360 - angle
            for aspect_name, (aspect_angle, orb) in aspects_to_calculate.items():
                if abs(angle - aspect_angle) <= orb:
                    exact_orb = abs(angle - aspect_angle)
                    aspect_str = format_aspect_string(p1['name'], p2['name'], aspect_name, exact_orb)
                    found_aspects.append(aspect_str)
    if found_aspects:
        found_aspects.sort(key=lambda x: float(x.split('(Orb: ')[1][:-2]))

    complex_aspects = detect_complex_aspects(chart_points, aspects_to_calculate)

    return {
        "name": name,
        "date_str": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d} JST",
        "location_str": f"{location_name} (Lat: {lat:.4f}, Lon: {lon:.4f})",
        "points": chart_points,
        "houses": list(houses),
        "aspects": found_aspects,
        "complex_aspects": complex_aspects
    }

def generate_horoscope_markdown(data1, selected_aspects1, data2=None, selected_aspects2=None):
    """Calculates horoscope for one or two charts and returns a Markdown formatted string."""
    try:
        # In a web context, ephe path should be set once at startup.
        # base = os.path.dirname(os.path.abspath(__file__))
        # swe.set_ephe_path(os.path.join(base, "ephe"))

        chart1 = calculate_chart(data1, selected_aspects1)
        chart2 = calculate_chart(data2, selected_aspects2) if data2 else None

        signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        
        def format_lon(plon, signs_list):
            sign = signs_list[int(plon // 30)]
            deg = int(plon % 30)
            minute = int((plon % 1) * 60)
            return f"{sign} {deg}°{minute:02d}'"

        name1 = chart1['name'] or "Chart 1"
        title = f"# Horoscope for {name1}"
        if chart2:
            name2 = chart2['name'] or "Chart 2"
            title = f"# Synastry Chart: {name1} and {name2}"
        
        markdown_lines = [title]

        charts_to_process = [chart1]
        if chart2: charts_to_process.append(chart2)

        for i, chart_data in enumerate(charts_to_process):
            chart_name = chart_data['name'] or f"Chart {i+1}"
            if len(charts_to_process) > 1:
                 markdown_lines.append("\n---\n")
                 markdown_lines.append(f"## {chart_name}")

            markdown_lines.append(f"- **Date:** {chart_data['date_str']}")
            markdown_lines.append(f"- **Location:** {chart_data['location_str']}")
            markdown_lines.append("\n### Planets and Points")
            markdown_lines.append("| Name      | Position           |")
            markdown_lines.append("| :-------- | :----------------- |")
            for point in chart_data['points']:
                house_num = get_house_for_point(point['lon'], chart_data['houses'])
                markdown_lines.append(f"| {point['name']:<10}| {format_lon(point['lon'], signs):<18} | {house_num:<5} |")
            
            markdown_lines.append("\n### House Cusps")
            markdown_lines.append("| House     | Position           |")
            markdown_lines.append("| :-------- | :----------------- |")
            for i_house, cusp in enumerate(chart_data['houses']):
                markdown_lines.append(f"| {i_house+1:<10}| {format_lon(cusp, signs):<18} |")

            markdown_lines.append("\n### Aspects (Natal)")
            if chart_data['aspects']:
                for aspect_str in chart_data['aspects']:
                    markdown_lines.append(f"- {aspect_str}")
            else:
                markdown_lines.append("- No major aspects found.")

            markdown_lines.append("\n### Complex Aspects")
            if chart_data['complex_aspects']:
                for complex_asp in chart_data['complex_aspects']:
                    markdown_lines.append(f"- **{complex_asp['type']}**: {' '.join(complex_asp['planets'])}")
                    if complex_asp['type'] == 'YOD':
                        markdown_lines.append(f"  - Apex Planet: {complex_asp['apex_planet']}")
                    for asp_detail in complex_asp['aspects']:
                        markdown_lines.append(f"  - {asp_detail}")
            else:
                markdown_lines.append("- No complex aspects found.")

        if chart2:
            all_aspects_def = {
                'Conjunction': (0, 8), 'Opposition': (180, 8), 'Trine': (120, 7),
                'Square': (90, 7), 'Sextile': (60, 5),
                'Quincunx': (150, 2), 'Semisextile': (30, 2), 'Semisquare': (45, 2),
                'Sesquiquadrate': (135, 2), 'Quintile': (72, 2), 'Biquintile': (144, 2),
            }
            
            synastry_aspects_to_calculate = {}
            for aspect_name in ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile']:
                if aspect_name in all_aspects_def:
                    synastry_aspects_to_calculate[aspect_name] = all_aspects_def[aspect_name]

            if selected_aspects1:
                for aspect_name, is_selected in selected_aspects1.items():
                    if is_selected and aspect_name not in synastry_aspects_to_calculate and aspect_name in all_aspects_def:
                        synastry_aspects_to_calculate[aspect_name] = all_aspects_def[aspect_name]

            name2 = chart2['name'] or "Chart 2"
            synastry_aspects = []
            sensitive_points = ['ASC', 'MC']
            for p1 in chart1['points']:
                for p2 in chart2['points']:
                    if p1['name'] in sensitive_points and p2['name'] in sensitive_points:
                        continue

                    angle = abs(p1['lon'] - p2['lon'])
                    if angle > 180: angle = 360 - angle
                    for aspect_name, (aspect_angle, orb) in synastry_aspects_to_calculate.items():
                        if abs(angle - aspect_angle) <= orb:
                            exact_orb = abs(angle - aspect_angle)
                            aspect_str = format_aspect_string(f"{name1}'s {p1['name']}", f"{name2}'s {p2['name']}", aspect_name, exact_orb)
                            synastry_aspects.append(aspect_str)
            if synastry_aspects:
                synastry_aspects.sort(key=lambda x: float(x.split('(Orb: ')[1][:-2]))

            house_overlays = []
            house_cusps1 = chart1['houses']
            for p2 in chart2['points']:
                planet_lon = p2['lon']
                for i in range(12):
                    cusp_start = house_cusps1[i]
                    cusp_end = house_cusps1[(i + 1) % 12]
                    if cusp_start < cusp_end:
                        if cusp_start <= planet_lon < cusp_end:
                            house_overlays.append(f"{name2}'s {p2['name']} in {name1}'s House {i+1}")
                            break
                    else:
                        if cusp_start <= planet_lon < 360 or 0 <= planet_lon < cusp_end:
                            house_overlays.append(f"{name2}'s {p2['name']} in {name1}'s House {i+1}")
                            break
            
            markdown_lines.append("\n---\n")
            markdown_lines.append(f"## Synastry Aspects ({name1} & {name2})")
            if synastry_aspects:
                for aspect_str in synastry_aspects:
                    markdown_lines.append(f"- {aspect_str}")
            else:
                markdown_lines.append("- No major synastry aspects found.")

            markdown_lines.append("\n---\n")
            markdown_lines.append(f"## House Overlays ({name2} in {name1}'s Houses)")
            if house_overlays:
                for overlay_str in house_overlays:
                    markdown_lines.append(f"- {overlay_str}")
            else:
                markdown_lines.append("- No house overlays found.")

        return "\n".join(markdown_lines)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"An error occurred: {e}"

def geocode(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
    headers = {'User-Agent': 'AstroMD/1.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        return None, None
    except requests.exceptions.RequestException as e:
        # In a web app, you'd want to log this error properly
        print(f"Geocoding Error: {e}")
        return None, None
