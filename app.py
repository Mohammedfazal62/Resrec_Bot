from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# --- CONFIGURATION ---
USERNAME = "mohammedfazal62"
DATABASE_PATH = f"/home/{USERNAME}/restaurants.json"

# --- HELPER: Load Database ---
def load_restaurants():
    try:
        with open(DATABASE_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

# Load data once at startup
restaurants = load_restaurants()

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        req = request.get_json(silent=True)
        params = req.get("queryResult", {}).get("parameters", {})

        # --- SAFETY: Handle lists, strings, and clean input ---
        def get_clean_value(key):
            val = params.get(key, "")
            # If Dialogflow sends a list (even if "IS LIST" is off, it happens), take the first item
            if isinstance(val, list):
                val = val[0] if len(val) > 0 else ""
            # Clean: convert to string, lowercase, and remove spaces
            return str(val).lower().strip()

        # 1. Capture exact names from your Dialogflow parameters
        cuisine = get_clean_value("Cuisine_type")
        dietary = get_clean_value("dietary_pref")
        atmosphere = get_clean_value("Restaurant-Atmosphere")
        seating = get_clean_value("Indoor_or_Outdoor")

        # Safe integer conversion for guests
        try:
            # FIXED: Corrected spelling from "Guest_numbe" to "Guest_number"
            num_guests = int(params.get("Guest_number", 0))
        except:
            num_guests = 0

        recommended = None

        # 2. Strict If-Else Filtering Logic
        for res in restaurants:
            # Cuisine Check (Strict)
            if cuisine and res.get("cuisine", "").lower() != cuisine:
                continue

            # Dietary Check (Flexible: checks if user preference is IN the restaurant's list)
            if dietary:
                res_dietary = [d.lower() for d in res.get("dietary", [])]
                if not any(dietary in d for d in res_dietary):
                    continue

            # Atmosphere Check (Strict: checks if user preference is IN the restaurant's list)
            if atmosphere:
                res_atmospheres = [a.lower() for a in res.get("atmosphere", [])]
                if atmosphere not in res_atmospheres:
                    continue

            # Seating Check (Strict: checks if user preference is IN the restaurant's list)
            if seating:
                res_seating = [s.lower() for s in res.get("seating", [])]
                if seating not in res_seating:
                    continue

            # Guest Capacity Check
            if num_guests > res.get("max_guests", 0):
                continue

            # If all checks pass, we found our match!
            recommended = res
            break

        # 3. Build the Response
        if recommended:
            # FIXED: 'atmosphere' is a list, so we join it into a string like "romantic, quite"
            # instead of crashing with .lower() on a list.
            atm_str = ", ".join(recommended['atmosphere'])

            response_text = (
                f"I've found the perfect spot! I recommend {recommended['name']} "
                f"in {recommended['location']}. It perfectly fits your requirements "
                f"and has that {atm_str} vibe you're looking for."
            )
        else:
            response_text = (
                "Ach! Even for Berlin, that's a very specific craving! 🍻 "
                "I couldn't find a match that fits every single one of those requirements. "
                "Maybe try changing the cuisine or atmosphere slightly?"
            )

        return jsonify({"fulfillmentText": response_text})

    except Exception as e:
        return jsonify({"fulfillmentText": f"Cloud Logic Error: {str(e)}"})

if __name__ == "__main__":
    app.run(port=5000)