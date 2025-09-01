from flask import Flask, request, jsonify, render_template_string
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Path to store received callback data
RECEIVED_JSON_PATH = "/app/received.json"

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"ok": True})

@app.route("/callbacks/steps", methods=["POST"])
def receive_callback():
    """Receive callback from API service and save to received.json"""
    try:
        data = request.get_json()
        logger.info(f"Received callback data: {data}")
        
        # Save to received.json
        with open(RECEIVED_JSON_PATH, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Data saved to {RECEIVED_JSON_PATH}")
        return jsonify({"status": "success", "message": "Callback received and saved"})
    
    except Exception as e:
        logger.error(f"Error processing callback: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/guides/<int:guide_id>", methods=["GET"])
def get_guide(guide_id):
    """Load received.json and render HTML page with steps"""
    try:
        # Load received.json
        if not os.path.exists(RECEIVED_JSON_PATH):
            return "No data found. Please process a video first.", 404
        
        with open(RECEIVED_JSON_PATH, "r") as f:
            data = json.load(f)
        
        # Check if guide_id matches
        if data.get("guide_id") != guide_id:
            return f"Guide ID {guide_id} not found. Available guide ID: {data.get('guide_id')}", 404
        
        steps = data.get("steps", [])
        
        # HTML template with clean CSS
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guide {{ guide_id }} - Steps</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .steps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .step-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #fafafa;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .step-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .step-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .step-index {
            background: #3498db;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            margin-right: 10px;
        }
        .step-time {
            background: #e74c3c;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-left: auto;
        }
        .step-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .step-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #ddd;
        }
        .no-steps {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.2em;
            margin-top: 50px;
        }
        .metadata {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .metadata h3 {
            margin-top: 0;
            color: #34495e;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Guide {{ guide_id }} - Video Steps</h1>
        
        <div class="metadata">
            <h3>Guide Information</h3>
            <p><strong>Guide ID:</strong> {{ guide_id }}</p>
            <p><strong>Total Steps:</strong> {{ steps|length }}</p>
        </div>

        {% if steps %}
            <div class="steps-grid">
                {% for step in steps %}
                <div class="step-card">
                    <div class="step-header">
                        <div class="step-index">{{ step.index }}</div>
                        <div class="step-time">{{ step.second }}s</div>
                    </div>
                    <div class="step-title">{{ step.title }}</div>
                    <img src="{{ step.image_url }}" alt="{{ step.title }}" class="step-image" 
                         onerror="this.src='https://via.placeholder.com/400x300/e0e0e0/666666?text=Step+{{ step.index }}'"
                         loading="lazy">
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="no-steps">
                <p>No steps found for this guide.</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        return render_template_string(html_template, guide_id=guide_id, steps=steps)
    
    except Exception as e:
        logger.error(f"Error loading guide {guide_id}: {str(e)}")
        return f"Error loading guide: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
