import io
import base64
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

app_icon_bp = Blueprint("app_icon_bp", __name__)

@app_icon_bp.route("/app-icon", methods=["POST"])
def generate_app_icons():
    """
    Turns each uploaded image into a 1024x1024 "app icon" at fixed compression level=5.
    Expects:
      - form-data with key "images" (multiple allowed, up to 5)
    Returns JSON:
      {
        "images": [
          { "filename": "...", "icon_b64": "..." },
          ...
        ]
      }
    Where 'icon_b64' is the base64-encoded JPEG at 1024x1024, quality ~ 50
    """

    current_app.logger.info("App Icon endpoint hit (multi-file)")
    try:
        files = request.files.getlist("images")
        if not files:
            current_app.logger.warning("No images provided for app icon creation.")
            return jsonify({"error": "No images provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        # We'll fix the size to 1024x1024
        target_size = (1024, 1024)

        # We'll treat compression level=5 => ~ quality=50
        jpeg_quality = 50

        results = []
        for file in files:
            filename = file.filename or "image.jpg"
            current_app.logger.info(f"Processing for App Icon: {filename}")

            image = Image.open(file.stream)
            # Convert to RGB if needed
            if image.mode not in ["RGB", "L", "1"]:
                image = image.convert("RGB")

            # Resize to 1024x1024
            resized = image.resize(target_size, Image.Resampling.LANCZOS)

            # Save to an in-memory buffer as JPEG with quality=50
            output = io.BytesIO()
            resized.save(output, format="JPEG", quality=jpeg_quality)
            output.seek(0)

            b64_data = base64.b64encode(output.read()).decode("utf-8")
            results.append({
                "filename": filename,
                "icon_b64": b64_data
            })

        current_app.logger.info(f"Successfully generated {len(results)} app icon(s).")
        return jsonify({"images": results})

    except Exception as e:
        current_app.logger.error(f"Error in /app-icon: {e}")
        return jsonify({"error": f"App Icon error: {str(e)}"}), 500
