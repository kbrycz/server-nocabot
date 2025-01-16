# favicon.py
import io
import base64
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

favicon_bp = Blueprint("favicon_bp", __name__)

@favicon_bp.route("/favicon", methods=["POST"])
def generate_favicons():
    """
    Endpoint to create multiple favicons from multiple images.

    Expects:
      - form-data with key "images" (the files, up to 5).
      - We'll resize each to 32x32 and return them as .ico base64.

    Returns:
      JSON:
      {
        "images": [
          { "filename": "...", "favicon_b64": "..." },
          ...
        ]
      }
    """
    current_app.logger.info("Favicon endpoint hit (multi-file)")
    try:
        files = request.files.getlist("images")
        if not files:
            current_app.logger.warning("No images provided for favicon.")
            return jsonify({"error": "No images provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        # We'll pick 32x32
        size = (32, 32)

        fav_results = []

        for file in files:
            filename = file.filename or "image"
            current_app.logger.info(f"Generating favicon for file: {filename}")

            image = Image.open(file.stream).convert("RGBA")
            resized_img = image.resize(size, Image.Resampling.LANCZOS)

            # Save to .ico in memory
            output = io.BytesIO()
            resized_img.save(output, format="ICO")
            output.seek(0)

            b64_data = base64.b64encode(output.read()).decode("utf-8")
            fav_results.append({
                "filename": filename,
                "favicon_b64": b64_data
            })

        current_app.logger.info(f"Successfully generated {len(fav_results)} favicons.")
        return jsonify({"images": fav_results})

    except Exception as e:
        current_app.logger.error(f"Error in /favicon: {e}")
        return jsonify({"error": f"Favicon error: {str(e)}"}), 500