import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("GENAI_API_KEY", "AIzaSyC3uz0BOff6r50e7BSsoAGeWasv1-fvxGk")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

ROOM_TYPES = ['bedroom', 'kitchen', 'living room', 'bathroom']
STYLES = ['modern', 'aesthetic', 'minimalist', 'rustic', 'traditional']

def is_valid_room_type(room_type: str) -> bool:
    return room_type.lower() in ROOM_TYPES

def is_valid_style(style: str) -> bool:
    return style.lower() in STYLES

def generate_design_advice(room_type, bed_type, room_size, color, doors_windows, style):
    """Generates room design advice with (x, y, z) positions for each furniture item."""
    bed_type_text = f" with a {bed_type} bed," if room_type == "bedroom" and bed_type else ""
    
    prompt = (
        f"Design a {style} {room_type}{bed_type_text} with a size of {room_size} (in feet) and a color scheme of '{color}', "
        f"with doors/windows positioned at {doors_windows}. List each furniture item required in the room, "
        f"along with its precise (x, y, z) coordinates based on the room's dimensions. Ensure the coordinates are aligned with three.js box geometry, "
        f"where x represents width, y represents height, and z represents depth. Also, provide the overall room coordinates in the same format. "
        f"I want only dimensions and position and furniture name like dimx:' ', dimy: ,dimz: and position in posx:, posy, posz "
        f"and also give {style} name before furniture name e.g. ({style}- furniture name) and also give which side case for three.js "
        f"(left, right, front, back), for {room_type} bedroom only generate for bed, almirah, desk, lamp, plant, rug "
        f"for {room_type}=living room generate sofa, t.v, floor lamp, table"
    )

    try:
        logger.info(f"Generating design for prompt: {prompt}")
        response = model.generate_content(prompt)
        return response.text.strip() if response else 'No response from AI model.'
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return 'An error occurred while generating content.'

def parse_design_response_to_json(design_text):
    """Parses the AI model's response text into a structured JSON format."""
    furniture_items = []

    pattern = re.compile(r'(\w+)\s+is\s+(?:placed|at)\s+\((\d+),\s*(\d+),\s*(\d+)\)', re.IGNORECASE)
    matches = pattern.findall(design_text)
    
    for match in matches:
        furniture, x, y, z = match
        furniture_items.append({
            "furniture_name": furniture,
            "dimensions": {
                "dimx": int(x),
                "dimy": int(y),
                "dimz": int(z)
            },
            "position": {
                "posx": int(x),
                "posy": int(y),
                "posz": int(z),
            },
            "side": "side"  # Replace with actual side value if available.
        })
    
    return furniture_items

@app.route('/design', methods=['POST'])
def design():
    try:
        data = request.json
        room_type = data.get('room_type', '').strip().lower()
        bed_type = data.get('bed_type', '').strip().lower()
        room_size = data.get('room_size', 'N/A')
        color = data.get('color', 'white').strip().lower()
        doors_windows = data.get('doors_windows', {})
        style = data.get('style', '').strip().lower()

        logger.info(f"Received design request for room type: {room_type} with style: {style}")

        if not is_valid_room_type(room_type):
            return jsonify({"error": f"Invalid room type '{room_type}'. Supported types: {', '.join(ROOM_TYPES)}"}), 400
        if not is_valid_style(style):
            return jsonify({"error": f"Invalid style '{style}'. Supported styles: {', '.join(STYLES)}"}), 400

        design_advice = generate_design_advice(room_type, bed_type, room_size, color, doors_windows, style)
        logger.info(f"Generated design advice: {design_advice}")

        return jsonify({"design_advice": design_advice})

    except Exception as e:
        logger.error(f"Error processing design request: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
