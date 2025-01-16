# resize.py
import io
import base64
from flask import Blueprint, request, jsonify, current_app
from PIL import Image

resize_bp = Blueprint("resize_bp", __name__)

@resize_bp.route("/resize", methods=["POST"])
def resize_images():
    """
    Endpoint to resize multiple images at once.

    Expects:
      - form-data with key "images" for the files (multiple accepted)
      - form-data with key "width" (int)
      - form-data with key "height" (int)

    Returns:
      JSON:
      {
        "images": [
          { "filename": "...", "resized_b64": "..." },
          ...
        ]
      }
      Each item includes base64-encoded resized JPEG data.

    If more than 5 images are provided, returns an error.
    """
    current_app.logger.info("Resize endpoint hit (multi-file)")

    try:
        # 1) Grab width/height
        width_str = request.form.get("width", "0")
        height_str = request.form.get("height", "0")
        width = int(width_str)
        height = int(height_str)
        current_app.logger.info(f"Requested resize to {width} x {height}")

        # 2) Get up to 5 images
        files = request.files.getlist("images")
        if not files or len(files) == 0:
            current_app.logger.warning("No image files provided for resizing")
            return jsonify({"error": "No image files provided"}), 400

        if len(files) > 5:
            current_app.logger.warning(f"Received {len(files)} images, exceeding the limit of 5.")
            return jsonify({"error": "Max 5 images allowed"}), 400

        resized_results = []

        for file in files:
            filename = file.filename or "image.jpg"
            current_app.logger.info(f"Resizing file: {filename}")

            # Load image
            image = Image.open(file.stream)

            # Convert to RGB if needed
            if image.mode not in ["RGB", "L", "1"]:
                current_app.logger.info(f"Converting from {image.mode} to RGB for {filename}")
                image = image.convert("RGB")

            # LANCZOS for high-quality resampling
            resized_image = image.resize((width, height), resample=Image.Resampling.LANCZOS)

            # Save to an in-memory buffer
            output = io.BytesIO()
            resized_image.save(output, format="JPEG")
            output.seek(0)

            # Convert to base64
            b64_data = base64.b64encode(output.read()).decode("utf-8")
            resized_results.append({
                "filename": filename,
                "resized_b64": b64_data
            })

        current_app.logger.info(f"Successfully resized {len(resized_results)} images.")
        return jsonify({"images": resized_results})

    except Exception as e:
        current_app.logger.error(f"Error in /resize: {e}")
        return jsonify({"error": f"Resize error: {str(e)}"}), 500