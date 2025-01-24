# main.py (or your main Flask entry point)
from flask import Flask
from flask_cors import CORS
import logging

# Existing imports
from compress import compress_bp
from resize import resize_bp
from convert import convert_bp
from favicon import favicon_bp
from app_icon import app_icon_bp
# from remove_bg import remove_bg_bp  # if you had a remove_bg endpoint

app = Flask(__name__)

# FIXED: allow both localhost:3000 and your domain:
cors = CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://www.nocabot.com"]}})

# Register all endpoints
app.register_blueprint(compress_bp)
app.register_blueprint(resize_bp)
app.register_blueprint(convert_bp)
app.register_blueprint(favicon_bp)
app.register_blueprint(app_icon_bp)
# app.register_blueprint(remove_bg_bp)

@app.route("/")
def index():
    app.logger.info("Index endpoint hit")
    return "Hello from server-nocabot!"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, host="0.0.0.0", port=5000)